# DeltaWitness

[![CI](https://github.com/rdemb/delta-witness/actions/workflows/ci.yml/badge.svg)](https://github.com/rdemb/delta-witness/actions/workflows/ci.yml)

**Counterfactual verification and exact patch influence for AI-generated code changes.**

DeltaWitness is an open research prototype for checking whether a software patch produced the behavioral change claimed by its tests, for localizing exact declared witness-test transitions, for retaining complete typed mutation evidence under frozen development controls, and for measuring how each changed code path influences the declared witness. It does not trust a green final-state run, a raw nonzero exit, a test-suite aggregate, a compiled mutation catalog, a preregistration-concordant result, or an agent's narrative by itself.

**Current status:** pre-alpha research software (`v0.0.3` plus unreleased DW-001 research infrastructure). It is not a formal proof system, a security certification product, a code-review replacement, a complete oracle analyzer, a validated mutation system, or a sandbox for untrusted code.

## The problem

A coding agent can modify production code, modify tests, run the resulting suite, and report success. That workflow can become self-confirming. A final test run does not establish that:

- the candidate test would have detected the original defect;
- the implementation change caused the observed improvement;
- the original suite still passes against the candidate implementation;
- the agent did not weaken, skip, replace, or misdirect the relevant oracle;
- a nonzero test-runner exit came from an assertion rather than collection, import, setup, or infrastructure failure;
- the assertion that caused suite failure belongs to the test declared for the claim;
- an exact declared fail-to-pass test is strong enough to reject plausible incorrect implementations;
- a mutation operator set or score was fixed before its outcomes were observed;
- duplicate, invalid, not-applicable, equivalent, or incomplete mutants were retained honestly;
- a complete outcome that contradicted the preregistered expectation was retained rather than suppressed as a harness error;
- summary counts and policy fields were recomputed from the complete result table;
- every implementation file changed by the patch contributed to the declared result;
- two changes are alternatives, jointly necessary, redundant, or mutually compensating.

DeltaWitness moves the first layers of this decision out of the agent's narrative and into deterministic Git replay, typed execution evidence, exact selector provenance, bounded negative controls, frozen experimental inputs, complete expected-or-unexpected result tables, and exhaustive path-level intervention analysis.

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

DeltaWitness calls the resulting artifact a **change witness**. It is bounded evidence about declared commits, paths, commands, and observations. It is not proof of full correctness, security, completeness, minimality, oracle adequacy, or causal necessity.

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

The built-in producer supports Python's standard-library `unittest` discovery and exact repeated logical-test selection:

```bash
deltawitness-unittest --start-directory tests
deltawitness-unittest --start-directory tests \
  --test-name test_access.AccessTests.test_viewer_is_denied
```

Read the complete protocol and its non-claims in [Outcome Receipt Protocol v1](docs/OUTCOME_RECEIPT_V1.md).

## Layer 3: declared witness-test provenance

DW-001 research infrastructure can bind one claim to exact predeclared standard-library unittest selector identities and replay those selectors under the exact `base_candidate` and `candidate_candidate` states reconstructed from a verified matrix report.

A selector is classified as:

- `discriminating`: typed assertion failure in `BC`, pass in `CC`;
- `non_discriminating`: pass in both states;
- `candidate_invalid`: `CC` does not pass;
- `indeterminate`: error, timeout, missing selector, malformed or contradictory receipt, or unsupported selection semantics.

The declaration binds claim, specification, adapter, selectors, and adapter-derived commands. The localization artifact binds exact Git states, invocation-bound receipts, per-selector outcomes, aggregate status, semantic digest, and complete-report digest.

This layer addresses **which declared logical test produced the transition**. It does not establish that the selected test expresses the intended behavior or rejects plausible incorrect implementations.

## Development negative controls for oracle interpretation

### Unrelated suite assertion

A fixed owned-synthetic control produces a canonical four-state witness and genuine typed assertion failure, but the suite fails only because of a collateral assertion. The claim-facing selector passes on base and candidate. Exact selector localization exposes that mismatch.

This demonstrates:

```text
typed suite failure
    + canonical four-state witness
    != claim-oracle relevance
```

### Weak but genuinely discriminating selector

A second fixed control goes further. Its exact declared selector genuinely fails on base, passes on candidate, and localizes as `discriminating`. The selector asserts only that `is_admin(viewer)` returns a Boolean.

A fixed mutant:

```python
def is_admin(user):
    return bool(user.get("role"))
```

also passes that selector while authorizing a viewer. A separately fixed development claim check passes on the candidate and rejects the mutant.

This demonstrates one controlled limitation:

```text
typed assertion failure
    + canonical four-state witness
    + exact declared-selector fail-to-pass
    != sufficient oracle strength
```

The integrity-bound challenge executes five fixed typed controls and reconstructs its complete semantics from verified matrix, projection, declaration, and localization sources. It is an owned-synthetic agent-workflow surrogate, not an evaluation of any named model, a mutation score, or a complete test-integrity method.

Read [DW-001 Weak-Proxy-Oracle Challenge v1](research/DW-001/WEAK_ORACLE_CHALLENGE.md).

## Claim-scoped mutation design and typed result

The current Gate 1 experiment is deliberately split into three stages:

```text
freeze source/operator/profile identities
    -> execute one bounded typed result table
    -> broader calibration and direct baselines
```

The first two stages are implemented for one owned-synthetic source. Broader calibration is not.

Canonical design artifacts:

```text
research/DW-001/claim-scoped-mutation-plan.v1.json
research/DW-001/claim-scoped-mutant-catalog.v1.json
research/DW-001/MUTATION_CALIBRATION_PLAN.md
```

The plan fixes one project-owned candidate predicate, one exact standard-library AST return-expression target, and this outcome-blind generic operator order:

```text
return-constant-false-v1
return-constant-true-v1
comparison-eq-to-ne-v1
```

The deterministic catalog retains:

```text
3 generated
1 duplicate
1 not_applicable
1 invalid
```

The duplicate, not-applicable, and compile-invalid records are generation controls. They cannot be silently dropped or counted as generic mutation evidence.

The known `nonempty-role-boolean-v1` mutant from the weak-proxy challenge remains separate:

```text
included_in_generic_operator_set      = false
counts_toward_operator_generalization = false
```

Two selector profiles are frozen over the same candidate source and generic mutant identities:

```text
strong-authorization-oracle-v1
weak-boolean-proxy-v1
```

The adapter uses only the standard-library `ast` module. It parses, transforms, unparses, reparses, and compiles fixed project-owned bytes. Exact plan, AST-target, mutant, and catalog identities are reconstructed from editable and installed-wheel packages on Python 3.11–3.14.

Read [DW-001 Claim-Scoped Mutation Calibration Plan v1](research/DW-001/MUTATION_CALIBRATION_PLAN.md).

### Typed bounded result

The result runner verifies the exact plan and catalog and then executes only:

```text
candidate baseline
3 frozen generic generated mutants
1 separately labeled historical control
```

Each implementation runs:

```text
2 strong selectors
1 weak selector
2 reference selectors
```

Total fixed workload:

```text
5 implementations × 5 selectors = 25 typed commands
```

Generation-only duplicate, invalid, and not-applicable records remain in the complete table with zero commands and explicit non-execution reasons.

Every selector stores:

```text
expected_observed
observed
concordant
```

Profiles and reference checks store expected outcome, observed outcome, and concordance. Record-level concordance, summary counts, and top-level analysis are recomputed.

A complete invocation-bound observation that contradicts preregistration remains a valid negative result:

```text
complete unexpected observation
    != malformed evidence
    != harness failure
```

Malformed structure, source or selector substitution, wrong commands or bindings, receipt contradiction, impossible aggregates, non-finite costs, or digest tampering still fail closed.

For the current exact owned-synthetic table, the preregistered contrast is:

```text
all 3 generic mutants:
    strong profile -> killed
    weak profile   -> survived
    reference      -> claim_violation_observed
```

Agreement with this table validates only the bounded mechanism. The historical control is excluded from generic evidence.

The result fixes:

```text
mutation_score                           = null
headline_score                           = null
universal_threshold                      = null
merge_blocker_authorized                 = false
ecological_inference_allowed             = false
holdout_selected                         = false
primary_denominator_eligible             = false
generic_operator_generalization_allowed  = false
```

```text
complete typed mutation result
    != mutation adequacy
    != ecological effectiveness
    != merge policy
```

Read [DW-001 Claim-Scoped Mutation Result v1](research/DW-001/MUTATION_RESULT_V1.md).

## Layer 4: exact patch influence

A valid full patch can still contain collateral or interacting changes. For patches with at most eight changed code paths, `deltawitness influence` enumerates every coalition exactly.

For each subset of changed code paths, DeltaWitness:

1. starts from the immutable base implementation-side tree;
2. holds candidate documentation changes constant;
3. overlays only the selected candidate code paths;
4. evaluates the implementation under base tests;
5. evaluates the same implementation under candidate tests;
6. records exact trees, commits, observer evidence, and coalition status.

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
- whether the witness predicate is monotone over observed path interventions.

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
- specification digest and explicit path classification;
- every expected and observed state result;
- exit codes, timeout status, durations, and output digests;
- observer identifier and deterministic invocation binding;
- typed receipt outcome, producer, aggregate counts, digest, and stable observer error code when enabled;
- stable witness digest over semantic outcome;
- report digest over the complete JSON document.

A selector-localization artifact additionally records:

- one predeclared claim and ordered selector set;
- adapter-derived selector commands;
- exact `BC` and `CC` tree and commit identities;
- per-selector typed receipts and classifications;
- aggregate localization status;
- semantic and complete-report digests.

The weak-oracle challenge additionally records:

- fixed task, declared selector, candidate, mutant, and hidden development check identities;
- exact source and test digests;
- five ordered typed control executions;
- current matrix/projection/localization evidence bindings;
- one development-only limitation finding;
- semantic and complete-report digests.

The mutation plan and catalog additionally record:

- fixed source-byte and semantic-AST identities;
- exact path, symbol, target cardinality, source positions, and target digest;
- ordered generic operator and generation-control identities;
- exact generated mutant and duplicate relations;
- invalid and not-applicable generation records;
- paired selector-profile identities;
- future outcome taxonomy and explicit non-authorization fields;
- plan and catalog digests.

The mutation result additionally records:

- exact candidate and mutant identities;
- 25 selector commands with source/test digests and invocation bindings;
- typed receipts and process outcomes;
- expected and observed selector outcomes;
- expected and observed profile/reference outcomes;
- selector, profile, reference, and record concordance;
- generation-only non-execution records;
- observed summary, unexpected-result analysis, policy, and costs;
- stable semantic and complete-report digests.

An influence report additionally records:

- deterministic path order and bit encoding;
- every selected path coalition;
- exact implementation and candidate-test trees and commits for every coalition;
- endpoint anchor checks;
- complete coalition-level claim observations;
- exact rational attribution metrics when available;
- semantic influence digest and complete report digest.

Hybrid and intervention states are represented as synthetic commits rather than dirty worktrees. Commands that inspect `HEAD` therefore see a recorded commit identity. Git subprocesses use a reduced environment that rejects process-level repository redirection and replacement-object overrides. Changed submodule and changed symbolic-link entries are rejected before hybrid-state materialization. Repository-local attributes and filters remain a documented limitation.

Raw command output is excluded by default. Local absolute repository and specification paths are not written to reports. Command arrays, claim descriptions, selectors, public-safe fixed prompts, environment-variable names, output digests, repository paths, mutant IDs, AST/source/test digests, invocation bindings, and receipt metadata can be recorded; every exported artifact remains review-required before publication.

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

- canonical `pass / fail / pass / pass` expectations;
- a complete supported four-state witness;
- no more than eight changed code paths;
- exhaustive execution of all `2^n` coalitions;
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

The selector-localization, weak-oracle, mutation-plan, and mutation-result APIs are development research contracts, not general CLI policy or authorization to execute external repositories.

## Specification

A receipt-aware `unittest` claim:

```toml
[paths]
code = ["src/**", "pyproject.toml"]
tests = ["tests/**"]
documentation = ["README.md", "docs/**"]

[execution]
pass_env = []

[[claim]]
id = "security-regression"
description = "The candidate witness must expose the defect before the patch and pass after it."
observer = "outcome-receipt-v1"
command = ["deltawitness-unittest", "--start-directory", "tests"]
timeout_seconds = 300
pass_exit_codes = [0]
fail_exit_codes = [1]

[claim.expect]
base_base = "pass"
base_candidate = "fail"
candidate_base = "pass"
candidate_candidate = "pass"
```

Every changed path must match exactly one declared category. Every expectation must be explicit. Pass and fail exit-code sets must be disjoint. Timeouts, unclassified return codes, invalid receipts, and inconclusive receipt outcomes produce `INCOMPLETE`, even when an expectation is `any`. Ambiguous configuration fails closed.

Dependency manifests, build scripts, generated-code inputs, and execution-sensitive configuration should be classified as `code`, not `documentation`. Endpoint anchors detect some misclassification but cannot prove every hidden dependency has been categorized correctly.

Projects that do not use a receipt adapter may omit `observer`; `exit-code-v1` remains the default. A project-specific adapter should derive results from a structured framework API rather than terminal text and must follow protocol privacy and consistency rules.

CLI exit codes:

- `0`: the requested supported witness or exact attribution is available;
- `1`: four-state execution completed, but the declared witness was unsupported;
- `2`: configuration, Git, execution, observer, endpoint, incomplete-attribution, or report error.

## Computational boundary

Exact patch influence is intentionally exponential:

```text
n changed code paths -> 2^n coalitions -> 2 test worlds per coalition
```

At the hard cap of eight paths, one claim requires up to 512 coalition command executions in addition to the canonical matrix. Exact mode is designed for small, high-value patches where complete interaction structure matters more than throughput.

DeltaWitness does not silently approximate larger patches. Future work may add explicitly labeled sampling and confidence intervals, but approximate results must remain distinguishable from exact enumeration.

Selector localization and the weak-oracle challenge are separate development APIs rather than implicit additions to the core CLI policy. The weak-oracle challenge uses exactly five fixed controls and does not define a general mutation workload.

The mutation plan performs three generic AST transformations and three generation controls over one fixed source. The bounded mutation result executes 25 typed selector commands across five fixed implementation identities. Neither cost profile can be extrapolated to ecological repositories or general mutation engines.

## Safety model

DeltaWitness executes declared commands without a shell, with a sanitized environment and isolated temporary home and cache directories. It still runs with the current user's filesystem permissions and does not isolate the network.

Use it only with code and commands you trust. Never place secrets directly in a command array. Values passed through `execution.pass_env` are not written to reports, but a command can still print or otherwise expose them. Output digests can fingerprint low-entropy sensitive values and are not a substitute for review.

A receipt binding prevents accidental cross-state reuse; it does not authenticate the producer. A malicious command can read its binding and forge a syntactically valid receipt. Producer signing, environment provenance, and containment remain separate future layers.

Exact coalition enumeration multiplies command execution. Run influence analysis only in a separately secured, disposable, resource-bounded environment when the repository or command is not fully trusted.

The weak-oracle challenge and mutation-result runner execute only fixed project-owned bytes in temporary directories. The mutation-plan adapter parses and compiles the same fixed bytes. None makes DeltaWitness safe for external or untrusted patches. No VPS or credential-bearing environment should be used as an ad hoc sandbox.

Read [THREAT_MODEL.md](THREAT_MODEL.md) before use.

## Research boundary

Fail-to-pass validation, selector execution, delta debugging, patch minimization, automated patch assessment, program slicing, mutation testing, selective mutation, equivalent-mutant analysis, cooperative-game attribution, test-code co-evolution, weak or partial oracles, hidden tests, coverage, and assertion-quality analysis are established areas. DeltaWitness does not currently claim scientific novelty.

The provisional contribution under evaluation is narrower: a Git-native four-state replay, exact hybrid-state identities, typed invocation-bound outcomes, exact declared-selector provenance, integrity-bound negative controls for oracle interpretation, a pre-execution outcome-blind mutation design with exact identities, a complete expected-or-unexpected typed mutation result table, exhaustive dual-test-world path interventions, endpoint consistency, exact non-monotonic attribution, and portable verifiable artifacts.

The project must still demonstrate through systematic literature review, fair direct tooling baselines, broader frozen calibration, equivalent-mutant review, calibrated error rates, authorized ecological data, held-out evaluation, external reproduction, and technical review that this combination adds useful evidence beyond existing methods.

See:

- [Research Note 000](docs/RESEARCH_NOTE_000.md)
- [Research Note 001](docs/RESEARCH_NOTE_001_TYPED_FAILURES.md)
- [Research Note 002](docs/RESEARCH_NOTE_002_EXACT_PATCH_INFLUENCE.md)
- [DW-001 protocol](research/DW-001/PROTOCOL.md)
- [DW-001 Weak-Proxy-Oracle Challenge](research/DW-001/WEAK_ORACLE_CHALLENGE.md)
- [DW-001 Claim-Scoped Mutation Calibration Plan](research/DW-001/MUTATION_CALIBRATION_PLAN.md)
- [DW-001 Claim-Scoped Mutation Result](research/DW-001/MUTATION_RESULT_V1.md)

## Current limitations

The prototype intentionally supports a narrow case:

- test changes must be separable by repository path;
- candidate test changes are required;
- changed submodule and changed symbolic-link entries are rejected;
- dependency, toolchain, generated-file, unchanged-submodule, unchanged-symbolic-link, and cross-repository state are not yet fully modeled or cryptographically bound;
- repository-local Git attributes, filters, checkout transformations, and the shared object database can still affect worktrees;
- commands can access the host filesystem and network;
- nondeterministic tests are observed only once;
- `exit-code-v1` can confuse assertion failure with collection, import, setup, teardown, or infrastructure failure;
- `outcome-receipt-v1` requires a cooperating producer and does not authenticate it;
- built-in typed selection currently supports only standard-library `unittest`;
- typed outcomes do not establish oracle relevance or strength;
- selector localization proves exact declared transition, not semantic intent;
- the weak-oracle challenge uses one fixed mutant and hidden check, not a calibrated mutation set or score;
- the minimal AST operator set covers one fixed Boolean predicate and is not a complete Python mutation model;
- the typed mutation result covers only three generic mutants and one historical control under two owned-synthetic profiles;
- equivalent-mutant adjudication, coverage, false-warning rates, missed-warning rates, and population uncertainty remain unresolved;
- the semantic-AST compatibility rule is validated only for one fixed source across Python 3.11–3.14;
- exact influence uses whole changed paths as intervention units, so results depend on path grouping;
- documentation changes are held at candidate state and must pass endpoint consistency checks;
- any indeterminate coalition withholds all exact attribution metrics;
- exact influence is capped at eight changed code paths;
- Shapley and Banzhaf values describe the declared Boolean witness game, not universal semantic importance;
- weak assertions, excessive mocking, semantic overfitting, environment drift, and production behavior remain outside the current validated boundary;
- synthetic commits are local Git objects and are not pushed automatically;
- a matching matrix, discriminating selector, compiled mutant catalog, matching mutation result, and stable influence map can still support a misleading or incomplete claim;
- the fixed synthetic development pilot, mutation plan/result, and challenges are not ecological agent evidence;
- independent reproduction remains incomplete.

## Project principles

1. Deterministic checks precede model judgment.
2. Ambiguous trust boundaries fail closed.
3. Public claims remain narrower than the evidence.
4. Incomplete execution is not negative evidence.
5. Negative and preregistration-divergent results are publishable outcomes.
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

## Unreleased DW-001 Coverage.py direct-baseline result

Issue #43 adds one optional, development-only direct comparison against Coverage.py `7.15.2`. Coverage.py is not a base runtime dependency. The base package keeps `dependencies = []`; the exact package is available only through the `research` extra and a hash-locked offline-reproduction path.

Reviewed distribution identity:

```text
artifact = coverage-7.15.2-py3-none-any.whl
sha256   = eb6bcae8d1a9d305351ecb108232441d11c5cfe9de840a04388ba5d2db8d735c
source   = coveragepy/coveragepy@50d865908dfeb21a0bf1e6f05db578c11662f8dd
license  = Apache-2.0
```

For the exact frozen owned-synthetic source, target, and selectors:

```text
strong Coverage.py statement union/intersection = [2] / [2]
weak Coverage.py statement union/intersection   = [2] / [2]

strong Coverage.py arc union/intersection = [[-1, 2], [2, -1]] / same
weak Coverage.py arc union/intersection   = [[-1, 2], [2, -1]] / same

stdlib statement distinguishes profiles   = false
Coverage.py statement distinguishes       = false
Coverage.py branch/arc distinguishes      = false
frozen generic mutation table distinguishes = true
```

Every selector had one exact static measurement context, complete typed outcome evidence, complete Coverage.py evidence, and a valid uncontaminated context partition. The result matched the preregistration and is frozen as:

```text
semantic_sha256 = ec0c2fdd5ac24ba53eb895d9014aab623d2631125b8512ba0e0cbf5105f21ee8
report_sha256   = 8b248757374ebff4195bad181ad02bc5b0bfc61fa2e21ebf45549686c33d2c41
```

This establishes only that, in one exact straight-line project-owned synthetic case, the two frozen selector profiles produced identical target statement and target-related arc sets while the already frozen generic-mutation table differed. It does not establish that coverage is generally insufficient, Coverage.py is weak, mutation testing is generally better or sufficient, oracle strength is complete, a merge blocker is justified, external execution is safe, Gate 0 or Gate 1 is complete, or the project is production-ready or scientifically novel.

The fixed source contains no conditional branch point. Broader conditional-control-flow cases, calibration populations, equivalent-mutant review, error-rate estimation, authorized ecological data, holdout evaluation, external reproduction, and independent technical review remain open.

See:

- [Coverage.py dependency and provenance review](research/DW-001/COVERAGEPY_DEPENDENCY_PROVENANCE_V1.md)
- [Coverage.py bounded result](research/DW-001/COVERAGEPY_BASELINE_RESULT_V1.md)
- [Coverage.py threat boundary](research/DW-001/COVERAGEPY_THREAT_BOUNDARY_V1.md)
- [Coverage.py direct-baseline architecture](docs/ARCHITECTURE.md#coveragepy-direct-baseline-architecture)
- [Frozen public-safe result](research/DW-001/coveragepy-baseline-result.v1.json)

## DW-001 selector-context interaction-lattice result

Issue #47 executes one exact preregistered, project-owned two-condition authorization control only after the design artifacts were merged. A separate execution protocol leaves the merged preregistration's `execution_authorized = false` and `execution_status = not_implemented` fields unchanged while authorizing exactly:

```text
4 candidate selectors with typed and Coverage.py evidence
5 generated mutants × 4 typed selectors
24 exact selector commands total
```

The complete result matched the frozen hypotheses:

```text
statement_aggregate_discriminates_profiles     = false
arc_aggregate_discriminates_profiles           = false
anonymous_path_multiset_discriminates_profiles = true

equal_cardinality_path_multisets_distinct     = true
mfa_independence_agrees_with_drop_mfa          = true
role_independence_agrees_with_drop_role        = true
any_independence_agrees_with_or_gates          = true
analysis.status                                = expected
```

Every candidate selector passed with one unique static context and complete typed and Coverage.py evidence. The five profiles had identical statement and arc union/intersection signatures, while their order-independent multisets of exact per-selector statement-and-arc path shapes were distinct. The fixed truth-table condition-independence relations agreed with the separately frozen five-mutant incidence table.

Stable result identity:

```text
semantic_sha256 = bc2ab879595da61815a17dcc33a09c6334b93dea3fd464f2fe4a5437944ebb77
checkpoint_sha256 = 40cf297679c83809368e53f35796d817761c25746302530f29fa4dda603277fc
```

The dependency-free public checkpoint is the default publication artifact. The full result retains exact commands, contexts, bindings, receipts, runtime identity, output digests, and costs only as reviewed diagnostic evidence.

This result is one bounded owned-synthetic observation. It does not establish general statement, branch, path, condition, MC/DC, combinatorial, checked-coverage, mutation, or oracle adequacy; method superiority; coding-agent or ecological effectiveness; a score, threshold, or merge blocker; containment or authentication; Gate completion; production readiness; scientific novelty; or award-level significance. The authorization boundary is explicit: external repository execution remains unauthorized.

See:

- [Interaction-lattice preregistration result note](research/DW-001/INTERACTION_WITNESS_LATTICE_RESULT_V1.md)
- [Interaction-lattice execution threat boundary](research/DW-001/INTERACTION_WITNESS_LATTICE_RESULT_THREAT_BOUNDARY_V1.md)
- [Dependency-free public checkpoint](research/DW-001/interaction-witness-lattice-result-checkpoint.v1.json)
- [Result architecture](docs/ARCHITECTURE.md#selector-context-interaction-lattice-result-architecture)
