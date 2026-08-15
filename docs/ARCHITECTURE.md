# Architecture

## Trust path

DeltaWitness receives a repository, a base ref, a candidate ref, and a TOML specification. The current trust path is intentionally small and deterministic:

1. resolve both refs to immutable commits;
2. require the base to be an ancestor of the candidate;
3. enumerate changed paths using NUL-delimited Git output with rename heuristics disabled;
4. require every changed path to match exactly one declared category;
5. reject changed Git submodule and symbolic-link entries;
6. create four detached worktrees;
7. overlay candidate tests onto the base tree and base tests onto the candidate tree;
8. write exact Git trees for all states;
9. create deterministic synthetic commits for hybrid states;
10. restore each state before each claim to prevent cross-claim contamination;
11. derive an invocation binding from the exact claim, command, specification, state, tree, and commit;
12. execute the command without a shell and with a sanitized environment;
13. observe the process through either explicit exit-code classes or a typed outcome receipt;
14. require receipt semantics and process exit codes to agree when a receipt observer is enabled;
15. mark timeouts, unclassified results, missing receipts, inconclusive receipt outcomes, and contradictions as incomplete execution;
16. record observations, observer evidence, output digests, state identities, and report digests.

The core deliberately excludes an LLM judge. Models may help design claims or review reports outside this trust path, but the verification decision is currently derived from explicit configuration, Git objects, process outcomes, and strict receipt semantics.

## State semantics

`base_base` and `candidate_candidate` are the original commits. `base_candidate` and `candidate_base` are synthetic local commits whose parent is the base commit.

The synthetic commits are deterministic for a given base, candidate, state name, and tree. They are stored as local Git objects without creating refs. DeltaWitness records their IDs in the report.

Files classified as tests are crossed between versions. Code and documentation remain on the implementation side of the matrix. Dependency manifests and build configuration should normally be classified as code because they influence execution.

The four states answer separate questions:

| State | Narrow observation |
|---|---|
| `base_base` | Does the declared baseline behave as expected under its own tests? |
| `base_candidate` | Do the candidate tests expose the behavior of the base implementation-side tree? |
| `candidate_base` | Does the candidate implementation-side tree preserve the declared behavior of the base tests? |
| `candidate_candidate` | Does the final candidate state satisfy the candidate tests? |

A matching matrix is evidence within the declared scope. It does not establish that a test oracle is relevant or strong, that the implementation delta is minimal, or that no untested behavior regressed.

## Observer architecture

### `exit-code-v1`

The default observer classifies a process result through each claim's disjoint `pass_exit_codes` and `fail_exit_codes`. The defaults are `[0]` and `[1]`. A timeout or any other exit code makes the report incomplete instead of being silently interpreted as a test failure.

This mode cannot distinguish multiple failure causes that a test runner reports with the same code. It remains useful for commands whose exit semantics are already explicit, but it is not a strong basis for high-assurance claims when assertion, collection, setup, and infrastructure failures share one status.

### `outcome-receipt-v1`

A receipt-aware claim receives two additional environment variables:

```text
DELTAWITNESS_RECEIPT_PATH
DELTAWITNESS_RECEIPT_BINDING
```

The binding is SHA-256 over canonical JSON containing:

- invocation protocol version;
- claim identifier;
- matrix state;
- exact tree and commit IDs;
- observer identifier;
- declared command array;
- specification digest.

A cooperating producer writes one strict JSON receipt to the private path. DeltaWitness accepts only:

```text
receipt passed       + configured pass exit code -> pass
receipt test_failure + configured fail exit code -> fail
```

All other receipt outcomes and every receipt/exit contradiction become `error`, making the report incomplete.

Receipt validation includes:

- exact schema and field sets;
- strict UTF-8 JSON with duplicate-key rejection;
- bounded file size;
- regular-file and symbolic-link checks;
- exact invocation-binding match;
- producer token validation;
- nonnegative bounded integer counts;
- one count-total invariant;
- semantic consistency between aggregate counts and the declared outcome.

The built-in `unittest` producer records one conservative final category per logical test object. This prevents multiple failing subtests from being misrepresented as more logical tests than were run.

The binding is not a secret. A malicious child process can read it and forge a matching receipt. This architecture protects against accidental cross-state reuse, malformed evidence, ambiguous runner outcomes, and contradictory dual-channel results. It does not authenticate the producer.

See [Outcome Receipt Protocol v1](OUTCOME_RECEIPT_V1.md).

## Environment handling

The command runner does not inherit the full host environment. It preserves a small set of platform variables, creates isolated temporary home, cache, configuration, and temporary directories, and passes additional variables only when listed in `[execution].pass_env`.

DeltaWitness Git subprocesses also use a reduced environment. External `GIT_DIR`, work-tree, index, object-directory, replacement-object, global-config, and credential-prompt overrides are not inherited. System and global Git configuration are disabled for the harness, replacement objects are disabled, literal pathspec handling is required, and Git LFS smudging is skipped. Repository-local configuration and repository attributes can still affect checkout behavior and remain part of the residual trust boundary.

This reduces accidental credential exposure but does not create a filesystem or network sandbox. The child process still has the current user's operating-system permissions. Command arguments are recorded in the report and therefore must not contain secrets.

The current environment record is deliberately incomplete. It does not hash the operating-system image, executables found through `PATH`, dependency trees, kernel, locale database, or network responses. Reproducible containment and toolchain binding are roadmap items rather than properties of `v0.0.2`.

## Report schema

Schema `0.3` adds observer evidence to every claim and state:

- observer protocol;
- invocation binding;
- receipt digest;
- typed receipt outcome;
- producer name and version;
- aggregate counts;
- stable observation error code.

Older schema `0.2` reports remain integrity-verifiable because their witness payload is reconstructed without fields that did not exist when they were produced.

No raw receipt narrative is recorded. The receipt protocol carries aggregate counts only. The normal report still records command arrays and output digests, so publication review remains mandatory.

## Integrity model

The report carries two digests:

- `witness_sha256` covers stable semantic inputs, state identities, observed outcomes, and typed observer evidence while excluding volatile durations, timestamps, and raw-output digests;
- `report_sha256` covers the complete JSON document with its own field normalized to `null` during hashing.

`deltawitness verify-report` recalculates both values. Detection is meaningful only when a digest is compared with a separately trusted value. An attacker who can replace the document can recompute its unkeyed hashes. The digests do not authenticate who produced the report. Signing and standard attestations are future work.

Output digests are included in the exact report, but they can fingerprint low-entropy sensitive values. They are evidence fields, not a redaction mechanism.

The default report path is resolved with `git rev-parse --git-path` and stored under private Git metadata. Exporting a report into the working tree requires an explicit `--output` path.

## Separation of future layers

DeltaWitness intentionally separates questions that are often collapsed into one green check:

```text
state identity
    -> execution outcome
    -> outcome semantics
    -> oracle relevance
    -> oracle strength
    -> patch causality
    -> environment provenance
    -> producer authenticity
    -> policy decision
```

Version `0.0.2` advances only through **outcome semantics**. Oracle analysis, mutation testing, hunk ablation, containment, signed attestations, and authorization policy remain independent future layers so that one weak signal cannot silently substitute for another.
