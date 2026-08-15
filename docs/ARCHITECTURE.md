# Architecture

## Layered assurance model

DeltaWitness separates questions that are often collapsed into one green check:

```text
state identity
    -> process execution
    -> outcome semantics
    -> executable change witness
    -> bounded intervention influence
    -> oracle relevance
    -> oracle strength
    -> broader patch causality
    -> environment provenance
    -> producer authenticity
    -> policy decision
```

Version `0.0.3` advances through **bounded intervention influence**. It does not claim to solve oracle relevance, full patch causality, environment reproducibility, producer authentication, or authorization.

The core deliberately excludes an LLM judge. Models may help design claims, generate candidate tests, or review reports outside the trust path, but verification decisions are currently derived from explicit configuration, immutable Git objects, process observations, strict receipt semantics, exact coalition enumeration, and deterministic arithmetic.

## Canonical four-state trust path

DeltaWitness receives a repository, a base ref, a candidate ref, and a TOML specification.

1. Resolve both refs to immutable commits.
2. Require the base to be an ancestor of the candidate.
3. Require a clean repository.
4. Enumerate changed paths using NUL-delimited Git output with rename heuristics disabled.
5. Require every changed path to match exactly one declared category.
6. Reject changed Git submodule and symbolic-link entries.
7. Create four detached worktrees.
8. Overlay candidate tests onto the base tree and base tests onto the candidate tree.
9. Write exact Git trees for all states.
10. Create deterministic synthetic commits for hybrid states.
11. Restore each state before each claim to prevent cross-claim contamination.
12. Derive an invocation binding from the exact claim, command, specification, observer, state, tree, and commit.
13. Execute the command without a shell and with a sanitized environment.
14. Observe the process through explicit exit-code classes or a typed outcome receipt.
15. Require receipt semantics and process exit codes to agree when a receipt observer is enabled.
16. Mark timeouts, unknown exits, missing receipts, inconclusive receipt outcomes, and contradictions as incomplete execution.
17. Record exact state identities, observer evidence, output digests, and integrity digests.

## Canonical state semantics

`base_base` and `candidate_candidate` are the original commits. `base_candidate` and `candidate_base` are deterministic local synthetic commits whose parent is the base commit.

Files classified as tests are crossed between versions. Code and documentation remain on the implementation side of the canonical matrix. Dependency manifests, build scripts, generated-code inputs, and configuration that influence execution should normally be classified as code.

| State | Narrow observation |
|---|---|
| `base_base` | Does the declared baseline behave as expected under its own tests? |
| `base_candidate` | Do candidate tests expose behavior in the base implementation-side tree? |
| `candidate_base` | Does the candidate implementation-side tree preserve declared base-test behavior? |
| `candidate_candidate` | Does the final candidate state satisfy candidate tests? |

A matching matrix is evidence within the declared scope. It does not establish oracle strength, implementation minimality, absence of untested regressions, or production safety.

## Observer architecture

### `exit-code-v1`

The default observer classifies a process result through each claim's disjoint `pass_exit_codes` and `fail_exit_codes`. The defaults are `[0]` and `[1]`. A timeout or every other exit code makes the report incomplete.

This mode cannot distinguish multiple failure causes reported through the same exit code. It is suitable only when the command has documented, unambiguous exit semantics or when that limitation is explicitly accepted.

### `outcome-receipt-v1`

A receipt-aware claim receives:

```text
DELTAWITNESS_RECEIPT_PATH
DELTAWITNESS_RECEIPT_BINDING
```

The binding is SHA-256 over canonical JSON containing:

- invocation protocol version;
- claim identifier;
- exact matrix or intervention state;
- exact tree and commit IDs;
- observer identifier;
- declared command array;
- specification digest.

A cooperating producer writes one strict JSON receipt. DeltaWitness accepts only:

```text
receipt passed       + configured pass exit code -> pass
receipt test_failure + configured fail exit code -> fail
```

Every other receipt outcome and every receipt/exit contradiction becomes `error`, making the observation incomplete.

Receipt validation includes:

- exact schema and field sets;
- strict UTF-8 JSON with duplicate-key rejection;
- bounded file size;
- regular-file and symbolic-link checks;
- exact invocation-binding match;
- producer-token validation;
- nonnegative bounded integer counts;
- a count-total invariant;
- semantic consistency between aggregate counts and declared outcome.

The built-in `unittest` producer retains each logical test object through aggregation and records one conservative final category per object. Multiple failing subtests therefore remain one logical failed test.

The binding is visible to the child process. It prevents accidental cross-state reuse and detects stale or mismatched evidence; it does not authenticate a malicious producer.

See [Outcome Receipt Protocol v1](OUTCOME_RECEIPT_V1.md).

## Exact patch-influence trust path

`deltawitness influence` begins by running the canonical matrix. It proceeds only when every claim uses the canonical regression pattern and the matrix is both complete and supported:

```text
base_base            pass
base_candidate       fail
candidate_base       pass
candidate_candidate  pass
```

Let the sorted changed-code path order be:

```text
N = [p0, p1, ..., p(n-1)]
```

The current exact protocol requires `1 <= n <= 8` and evaluates all `2^n` path coalitions.

For each coalition `S`:

1. Restore the immutable base commit.
2. Overlay candidate documentation paths and hold them constant for every coalition.
3. Overlay candidate versions of only the code paths in `S`.
4. Write the exact implementation tree and deterministic commit.
5. Execute every claim under base tests.
6. Overlay candidate tests onto the same intervened implementation.
7. Write the exact candidate-test tree and deterministic commit.
8. Execute every claim under candidate tests.
9. Classify the coalition as `supported`, `unsupported`, or `indeterminate`.

A coalition is supported only when every claim produces a valid `pass` under both test worlds. A complete valid failure makes it unsupported. Any timeout, observer error, import/setup/infrastructure failure, missing receipt, or unknown exit makes it indeterminate.

`indeterminate` is never converted to `unsupported`. Incomplete execution is not negative evidence.

## Endpoint anchors

Candidate documentation is held constant so the full coalition can reproduce the final candidate tree. A path labeled documentation can still affect execution, so four endpoint anchors are mandatory:

| Influence endpoint | Canonical state |
|---|---|
| Empty coalition under base tests | `base_base` |
| Empty coalition under candidate tests | `base_candidate` |
| Full coalition under base tests | `candidate_base` |
| Full coalition under candidate tests | `candidate_candidate` |

Anchor comparison uses semantic process/observer signatures. The two full-coalition trees must also equal their canonical candidate-side trees. Empty tree equality is required when there are no candidate documentation changes; otherwise semantic equality remains mandatory.

Any anchor inconsistency withholds all exact attribution metrics.

## Exact witness game

When all coalitions are complete, anchors are consistent, the empty coalition is unsupported, and the full coalition is supported, DeltaWitness defines:

```text
f(S) = 1 when coalition S is supported
f(S) = 0 when coalition S is unsupported
```

No monotonicity assumption is made. The exact table supports:

- all inclusion-minimal supported coalitions;
- global and full-context necessity;
- standalone sufficiency;
- positive and negative marginal swings;
- exact rational Shapley allocation;
- exact normalized Banzhaf influence;
- exact pairwise Banzhaf interaction;
- monotonicity diagnostics.

The arithmetic is performed with rational numbers. Decimal renderings are convenience fields; numerators and denominators are authoritative.

These metrics describe the declared Boolean witness game over whole changed paths. They do not establish semantic correctness, desirability, legal responsibility, or universal causal importance.

See [Exact Patch Influence v1](PATCH_INFLUENCE_V1.md).

## State and object lifecycle

Canonical hybrid states and intervention states are represented as local Git objects without creating refs. The worktree is reset and cleaned before each claim execution. Synthetic commit messages bind the state label, base commit, and candidate commit, and deterministic metadata makes identical state construction reproducible within the same Git object model.

Synthetic objects may remain reachable through Git's recent-object retention until garbage collection. DeltaWitness does not currently maintain permanent refs for them or push them automatically.

## Environment handling

The command runner does not inherit the full host environment. It preserves a small set of platform variables, creates isolated temporary home, cache, configuration, and temporary directories, and passes additional variables only when listed in `[execution].pass_env`.

Git subprocesses use a reduced environment. External `GIT_DIR`, work-tree, index, object-directory, replacement-object, global-config, and credential-prompt overrides are not inherited. System and global Git configuration are disabled, replacement objects are disabled, literal pathspec handling is required, and Git LFS smudging is skipped.

Repository-local configuration, attributes, filters, checkout transformations, unchanged symbolic links, and the shared object database remain within the residual trust boundary.

This is not a filesystem, network, process, or resource sandbox. Exact influence multiplies command execution and therefore multiplies the impact of unsafe code.

The current environment record does not bind the operating-system image, executable binaries, dependency trees, kernel, locale database, hardware, or network responses. Reproducible containment remains a later layer.

## Report schemas

### Canonical matrix report

Schema `0.3` records typed observer evidence for every claim and state:

- observer protocol;
- invocation binding;
- receipt digest;
- typed outcome;
- producer name and version;
- aggregate counts;
- stable observation-error code.

Earlier schema `0.2` reports remain integrity-verifiable because their witness payload is reconstructed without fields that did not exist at issuance.

### Exact influence report

Schema `deltawitness.patch-influence.v1` records:

- deterministic path order and bit encoding;
- path classification;
- canonical matrix reference and witness digest;
- all endpoint anchors;
- every coalition's selected paths;
- exact implementation and candidate-test trees and commits;
- complete claim observations for both test worlds;
- coalition status;
- exact metrics when their release conditions are satisfied.

No source code or raw receipt narrative is recorded. Raw process output remains excluded unless explicitly requested.

## Integrity model

Canonical reports carry:

- `witness_sha256` over stable semantic inputs and outcomes;
- `report_sha256` over the complete JSON document.

Influence reports carry:

- `influence_sha256` over exact intervention semantics, Git identities, observer evidence, anchors, statuses, and metrics;
- `report_sha256` over the complete JSON document.

`deltawitness verify-report` recalculates the applicable semantic digest and the full-report digest.

All digests are unkeyed. An attacker who can replace a report can recompute them. They detect modification only when compared with a separately trusted value and do not authenticate the producer. Signing and standard attestations remain future work.

Output digests can fingerprint low-entropy sensitive values. They are evidence fields, not a redaction mechanism.

Reports default to private Git metadata resolved through `git rev-parse --git-path`, preserving working-tree cleanliness. Exporting into a public path requires an explicit operator decision.

## Remaining separation of concerns

DeltaWitness intentionally refuses to let one signal substitute silently for another:

- typed outcomes do not prove oracle relevance;
- an exact coalition table does not prove tests cover the intended behavior;
- a Shapley value does not prove semantic causality;
- a report digest does not authenticate the producer;
- a matching witness does not authorize deployment;
- a supported patch does not establish production safety.

Future layers may add oracle analysis, mutation testing, coverage, hunk-level interventions, negative controls, repeated stochastic execution, reproducible containment, signed provenance, external policy evaluation, and independent reproduction. Each must retain its own claim boundary.
