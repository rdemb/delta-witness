# DeltaWitness

[![CI](https://github.com/rdemb/delta-witness/actions/workflows/ci.yml/badge.svg)](https://github.com/rdemb/delta-witness/actions/workflows/ci.yml)

**Counterfactual verification and exact patch influence for AI-generated code changes.**

DeltaWitness is an open research prototype for checking whether a software patch produced the behavioral change claimed by its tests, and for measuring how each changed code path influences that declared witness. It does not trust a green final-state run or an agent's narrative by itself.

**Current status:** pre-alpha research software (`v0.0.3`). It is not a formal proof system, a security certification product, a code-review replacement, or a sandbox for untrusted code.

## The problem

A coding agent can modify production code, modify tests, run the resulting suite, and report success. That workflow can become self-confirming. A final test run does not establish that:

- the candidate test would have detected the original defect;
- the implementation change caused the observed improvement;
- the original suite still passes against the candidate implementation;
- the agent did not weaken, skip, or replace the relevant oracle;
- a nonzero test-runner exit came from an assertion rather than collection, import, setup, or infrastructure failure;
- every implementation file changed by the patch contributed to the declared result;
- two changes are alternatives, jointly necessary, redundant, or mutually compensating.

DeltaWitness moves the first layers of this decision out of the agent's narrative and into deterministic Git replay, typed execution evidence, and bounded interventional analysis.

## Layer 1: four-state change witness

Given a base commit and a descendant candidate commit, DeltaWitness separates changed test paths from the remaining candidate tree and constructs four exact Git states:

| | Base tests | Candidate tests |
|---|---:|---:|
| **Base implementation-side tree** | `base_base` | `base_candidate` |
| **Candidate implementation-side tree** | `candidate_base` | `candidate_candidate` |

For a conventional regression fix, the expected pattern is usually:

```text
base_base            pass
base_candidate       fail
candidate_base       pass
candidate_candidate  pass
```

This pattern is consistent with the candidate witness exposing the old behavior, the candidate implementation satisfying that witness, and the original suite remaining valid against the candidate implementation. The interpretation is only as strong as the declared command and its outcome classification.

DeltaWitness calls the resulting artifact a **change witness**. It is bounded evidence about declared commits, paths, commands, and observations. It is not proof of full correctness, security, completeness, minimality, or causal necessity.

## Layer 2: typed outcome semantics

### Exit-code observer

`exit-code-v1` is the backward-compatible default. Exit code `0` is classified as `pass`, exit code `1` as `fail`, and every other result as an execution error unless the claim declares different disjoint code sets.

A raw exit code cannot establish why the runner failed. This mode is appropriate only when the command has documented, unambiguous exit semantics or when the limitation is acceptable.

### Typed outcome receipt

`outcome-receipt-v1` requires a cooperating test adapter to write a strict, bounded JSON receipt bound to the exact claim, command, specification, matrix state, tree, and commit.

Only two dual-channel combinations become normal matrix observations:

```text
receipt passed       + configured pass exit code -> pass
receipt test_failure + configured fail exit code -> fail
```

Import errors, discovery failures, no tests, all-skipped execution, unexpected successes, malformed or missing receipts, binding mismatches, and receipt/exit contradictions become `error`, making the report incomplete rather than creating a false regression witness.

The first built-in producer supports Python's standard-library `unittest`:

```bash
deltawitness-unittest --start-directory tests
```

Read the complete protocol and its non-claims in [Outcome Receipt Protocol v1](docs/OUTCOME_RECEIPT_V1.md).

## Layer 3: exact patch influence

A valid full patch can still contain collateral or interacting changes. For patches with at most eight changed code paths, `deltawitness influence` enumerates every coalition exactly.

For each subset of changed code paths, DeltaWitness:

1. starts from the immutable base implementation-side tree;
2. holds candidate documentation changes constant;
3. overlays only the selected candidate code paths;
4. evaluates the implementation under base tests;
5. evaluates the same implementation under candidate tests;
6. records exact trees, commits, observer evidence, and a coalition status.

A coalition is:

- `supported` when every declared claim produces a valid pass under both test worlds;
- `unsupported` when execution is complete and at least one valid failure is observed;
- `indeterminate` when any timeout, malformed observation, import/setup/infrastructure error, or other incomplete result occurs.

No exact influence metric is emitted unless the entire coalition table is complete and endpoint anchors remain consistent with the canonical four-state witness.

For a complete table, DeltaWitness reports:

- every inclusion-minimal witness-sufficient coalition;
- paths present in every supported coalition;
- paths absent from every minimal supported coalition;
- full-context leave-one-out necessity;
- standalone sufficiency;
- positive and negative marginal swing counts;
- exact rational Shapley allocation of the endpoint witness change;
- exact normalized Banzhaf influence;
- exact pairwise Banzhaf interaction;
- whether the witness predicate is monotone over the observed path interventions.

Example interpretation:

```text
src/access.py
  Shapley: 1
  globally necessary: true

src/banner.py
  Shapley: 0
  appears in no minimal coalition
```

This says that `src/access.py` controls the declared witness across the exact file-level intervention table, while `src/banner.py` does not. It does **not** prove that either file is semantically correct, production-safe, or universally causal.

Read [Exact Patch Influence v1](docs/PATCH_INFLUENCE_V1.md) and [Research Note 002](docs/RESEARCH_NOTE_002_EXACT_PATCH_INFLUENCE.md).

## What is technically recorded

A four-state report records:

- immutable base and candidate commit IDs;
- exact tree IDs for all four states;
- deterministic synthetic commit IDs for the two hybrid states;
- the specification digest and explicit path classification;
- every expected and observed state result;
- exit codes, timeout status, durations, and output digests;
- observer identifier and deterministic invocation binding;
- typed receipt outcome, producer, aggregate counts, digest, and stable observer error code when enabled;
- a stable witness digest over the semantic outcome;
- a report digest over the complete JSON document.

An influence report additionally records:

- deterministic path order and bit encoding;
- every selected path coalition;
- exact implementation and candidate-test trees and commits for every coalition;
- endpoint anchor checks;
- complete coalition-level claim observations;
- exact rational attribution metrics when available;
- a semantic influence digest and a complete report digest.

Hybrid and intervention states are represented as synthetic commits rather than dirty worktrees. Commands that inspect `HEAD` therefore see a recorded commit identity. Git subprocesses use a reduced environment that rejects process-level repository redirection and replacement-object overrides. Changed submodule and changed symbolic-link entries are rejected before hybrid-state materialization. Repository-local attributes and filters remain a documented limitation.

Raw command output is excluded by default. Local absolute repository and specification paths are not written to reports. Command arrays, claim descriptions, environment-variable names, output digests, selected repository paths, and receipt metadata are recorded; every exported report remains review-required before publication.

## Quick start

Requirements:

- Python 3.11 or later;
- Git;
- a clean repository;
- a base commit that is an ancestor of the candidate commit.

Install from a local checkout:

```bash
python -m pip install --no-deps -e .
deltawitness doctor
```

Run the self-contained demonstration:

```bash
./scripts/demo.sh
```

The demonstration executes typed four-state verification, exact two-path influence analysis, and integrity verification for both reports.

Verify another repository:

```bash
deltawitness verify \
  --repo /path/to/repository \
  --base origin/main \
  --head HEAD \
  --spec deltawitness.toml
```

Analyze exact patch influence:

```bash
deltawitness influence \
  --repo /path/to/repository \
  --base origin/main \
  --head HEAD \
  --spec deltawitness.toml
```

The influence command currently requires:

- the canonical `pass / fail / pass / pass` expectation pattern;
- a complete, supported four-state witness;
- no more than eight changed code paths;
- exact exhaustive execution of all `2^n` coalitions;
- complete endpoint consistency before metrics are released.

By default, reports are written inside the repository's private Git metadata directory:

```bash
git rev-parse --git-path deltawitness/report.json
git rev-parse --git-path deltawitness/influence.json
```

Verify either report:

```bash
deltawitness verify-report "$(git rev-parse --git-path deltawitness/report.json)"
deltawitness verify-report "$(git rev-parse --git-path deltawitness/influence.json)"
```

Use `--output /reviewed/path/report.json` only when a report must be exported deliberately.

## Specification

A receipt-aware `unittest` claim:

```toml
[paths]
code = ["src/**", "pyproject.toml"]
tests = ["tests/**"]
documentation = ["README.md", "docs/**"]

# Host environment variables are not inherited unless named here.
[execution]
pass_env = []

[[claim]]
id = "security-regression"
description = "The candidate witness must expose the defect before the patch and pass after it."
observer = "outcome-receipt-v1"
command = ["deltawitness-unittest", "--start-directory", "tests"]
timeout_seconds = 300

# The receipt and process exit must agree.
pass_exit_codes = [0]
fail_exit_codes = [1]

[claim.expect]
base_base = "pass"
base_candidate = "fail"
candidate_base = "pass"
candidate_candidate = "pass"
```

Every changed path must match exactly one declared category. Every matrix expectation must be explicit. Pass and fail exit-code sets must be disjoint. Timeouts, unclassified return codes, invalid receipts, and inconclusive receipt outcomes produce `INCOMPLETE`, even when an expectation is `any`. Ambiguous configuration fails closed.

Dependency manifests, build scripts, generated-code inputs, and configuration that can influence execution should be classified as `code`, not `documentation`. The influence endpoint anchors are designed to detect some misclassification, but they cannot prove that every hidden dependency has been categorized correctly.

Projects that do not use a receipt adapter may omit `observer`; `exit-code-v1` remains the default. A project-specific adapter should derive results from a structured framework API rather than terminal text and must follow the protocol's privacy and consistency rules.

CLI exit codes:

- `0`: the requested supported witness or exact attribution is available;
- `1`: four-state execution completed, but the declared witness was unsupported;
- `2`: configuration, Git, execution, observer, endpoint, incomplete-attribution, or report error.

## Computational boundary

Exact patch influence is intentionally exponential:

```text
n changed code paths -> 2^n coalitions -> 2 test worlds per coalition
```

At the current hard cap of eight paths, one claim requires up to 512 coalition command executions in addition to the canonical four-state matrix. The exact mode is designed for small, high-value patches where complete interaction structure matters more than throughput.

DeltaWitness does not silently approximate larger patches. Future work may add explicitly labeled sampling and confidence intervals, but approximate results must remain distinguishable from exact enumeration.

## Safety model

DeltaWitness executes commands from the specification without a shell, with a sanitized environment and isolated temporary home and cache directories. It still runs with the current user's filesystem permissions and does not isolate the network.

Use it only with code and commands you trust. Never place secrets directly in a command array. Values passed through `execution.pass_env` are not written to the report, but a command can still print or otherwise expose them. Output digests can fingerprint low-entropy sensitive values and are not a safe substitute for review.

A receipt binding prevents accidental cross-state reuse; it does not authenticate the producer. A malicious command can read its binding and forge a syntactically valid receipt. Producer signing, environment provenance, and containment remain separate future layers.

Exact coalition enumeration multiplies command execution. Run influence analysis only in a disposable, resource-bounded environment when the repository or command is not fully trusted.

For untrusted repositories, use a disposable virtual machine or a separately secured container without production credentials. Read [THREAT_MODEL.md](THREAT_MODEL.md) before use.

## Research boundary

Fail-to-pass validation, delta debugging, patch minimization, automated patch assessment, program slicing, mutation testing, cooperative-game attribution, and test-code co-evolution are established areas. DeltaWitness does not currently claim scientific novelty.

The provisional contribution under evaluation is narrower: a Git-native four-state replay, exact hybrid-state identities, typed and invocation-bound outcomes, exhaustive dual-test-world path interventions, endpoint consistency checks, exact non-monotonic attribution, and portable integrity-verifiable reports.

The project must still demonstrate through literature review, falsifiable benchmarks, held-out evaluation, external reproduction, and technical review that this combination adds useful evidence beyond existing methods.

See:

- [Research Note 000](docs/RESEARCH_NOTE_000.md)
- [Research Note 001](docs/RESEARCH_NOTE_001_TYPED_FAILURES.md)
- [Research Note 002](docs/RESEARCH_NOTE_002_EXACT_PATCH_INFLUENCE.md)
- [DW-001 protocol](research/DW-001/PROTOCOL.md)

## Current limitations

The prototype intentionally supports a narrow case:

- test changes must be separable by repository path;
- candidate test changes are required;
- changed submodule and changed symbolic-link entries are rejected;
- dependency, toolchain, generated-file, unchanged-submodule, unchanged-symbolic-link, and cross-repository state are not yet fully modeled or cryptographically bound;
- repository-local Git attributes, filters, checkout transformations, and the shared object database can still affect materialized worktrees;
- commands can still access the host filesystem and network;
- nondeterministic tests are observed only once;
- `exit-code-v1` can still confuse assertion failure with collection, import, setup, teardown, or infrastructure failure;
- `outcome-receipt-v1` requires a cooperating producer and does not authenticate it;
- the built-in typed producer currently supports only standard-library `unittest` discovery;
- typed outcomes do not establish oracle relevance or strength;
- exact influence uses whole changed paths as intervention units, so results depend on path grouping;
- documentation changes are held at candidate state and must pass endpoint consistency checks;
- any indeterminate coalition withholds all exact attribution metrics;
- exact influence is capped at eight changed code paths;
- Shapley and Banzhaf values describe the declared Boolean witness game, not universal semantic importance;
- weak assertions, excessive mocking, semantic overfitting, environment drift, and production behavior remain outside the current proof boundary;
- synthetic commits are local Git objects and are not pushed automatically;
- a matching matrix and stable influence map can still support a misleading or incomplete claim.

## Project principles

1. Deterministic checks precede model judgment.
2. Ambiguous trust boundaries fail closed.
3. Public claims remain narrower than the evidence.
4. Incomplete execution is not negative evidence.
5. Negative results and failed hypotheses are publishable outcomes.
6. Exact and approximate results must never be conflated.
7. Reproduction matters more than branding.
8. Material AI assistance is disclosed, while responsibility remains human.

## Public research boundary

The repository may contain safe synthetic fixtures, protocols, source code, released results, and reproducible evidence. Unpatched vulnerabilities, credentials, private infrastructure details, customer data, access configuration, and operational exploit material remain private or under coordinated disclosure. See [PUBLICATION_POLICY.md](docs/PUBLICATION_POLICY.md).

## Development

```bash
python -m unittest discover -s tests -v
./scripts/demo.sh
python scripts/validate_public_tree.py
```

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [AI_USAGE.md](AI_USAGE.md).

## Author and license

DeltaWitness is an independent open research project created by **Rafal Dembski**. It is licensed under Apache License 2.0.
