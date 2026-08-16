# DW-001 Protocol

**Status:** DRAFT — DEVELOPMENT-PILOT PREPARATION ONLY — NOT FROZEN — NO PILOT OR HOLDOUT EXECUTION AUTHORIZED.

**Study identifier:** `DW-001`.

**Implementation lineage for this revision:** `e30be96b387c5580cc85fff831f08beda69ad600` plus the fixture-manifest binding changes under review. The exact protocol, implementation, generator, baseline, and artifact-schema commits remain unpinned until freeze.

This is a protocol candidate, not a preregistration. It may change during design review and development-pilot preparation. No development pilot or held-out scenario may execute until its explicit authorization gate is complete. No held-out scenario may execute until the complete frozen protocol, generator, manifests, metrics, exclusions, versions, and commitment digest are immutably recorded before unblinding.

## 1. Primary research question

Does a Git-native four-state witness detect materially important false-assurance cases that are missed by stronger nested baselines, at an acceptable execution and review cost?

The primary incremental question is narrower:

> Does adding the independently checked `base implementation + base tests` endpoint and full matrix consistency provide useful evidence beyond a three-state comparator that already checks candidate-test discrimination and original-test preservation?

A separate controlled question asks whether invocation-bound typed outcome receipts provide incremental evidence beyond configured process exit codes when the matrix state set is held constant.

## 2. Claims not under test

DW-001 does not test or establish:

- complete patch correctness;
- semantic intent;
- test-oracle adequacy;
- vulnerability removal;
- production safety;
- universal causality;
- environment reproducibility;
- producer authenticity;
- authorization to merge or deploy;
- scientific novelty or superiority.

Exact path-level influence is outside the primary acceptance rule.

## 3. Canonical state model

| State | Implementation side | Test side |
|---|---|---|
| `base_base` (`BB`) | base | base |
| `base_candidate` (`BC`) | base | candidate |
| `candidate_base` (`CB`) | candidate | base |
| `candidate_candidate` (`CC`) | candidate | candidate |

Canonical discriminating-regression expectation:

```text
BB = pass
BC = fail
CB = pass
CC = pass
```

`error` and `timeout` are incomplete observations. They are never converted into semantic `fail`.

## 4. Controlled state-set methods

All primary methods are projected from one complete immutable source report for one homogeneous observer arm.

| Method | Required states | Acceptance predicate |
|---|---|---|
| `M0_FINAL` | `CC` | `CC == pass` |
| `M1_F2P` | `BC`, `CC` | `BC == fail` and `CC == pass` |
| `M2_F2P_P2P` | `BC`, `CB`, `CC` | `BC == fail`, `CB == pass`, and `CC == pass` |
| `M3_FOUR_STATE` | `BB`, `BC`, `CB`, `CC` | canonical four-state pattern |

Paired evidence increments:

```text
M1 - M0 = candidate-test discrimination
M2 - M1 = original-test preservation
M3 - M2 = base-endpoint validity and complete-matrix consistency
```

These labels describe controlled evidence increments, not universal causal effects.

## 5. Observation arms

| Observer ID | DeltaWitness observer | Meaning |
|---|---|---|
| `O0_EXIT_CODE` | `exit-code-v1` | configured disjoint process exit classes |
| `O1_TYPED_RECEIPT` | `outcome-receipt-v1` | invocation-bound typed receipt plus process-exit agreement |

A projected comparison may contain exactly one observer arm. Mixed-observer reports are invalid because they confound state-set and observation-semantics effects.

Combined identifiers remain explicit, for example:

```text
M2_F2P_P2P__O0_EXIT_CODE
M2_F2P_P2P__O1_TYPED_RECEIPT
```

## 6. Source-report requirements

The v1 projector accepts only a matrix report that:

- uses report schema `0.3`;
- was decoded as strict UTF-8 JSON with recursive duplicate-key rejection;
- passes semantic and complete-report integrity verification;
- contains exactly four ordered observations for every claim;
- uses canonical DW-001 expectations;
- has consistent state, Git-object, observer, match, completeness, claim, and overall fields;
- contains at least one claim;
- uses one homogeneous observer arm.

The complete source report is validated before any projected decision is exposed. Validation of a hidden state is not permission for a weaker method to consume that state's outcome.

The retained source-report bytes and projection are separately mandatory. A projection records source digests but cannot reconstruct omitted source fields.

## 7. Four-way decision semantics

Each method returns one decision:

- `accept`: all required observations are complete and satisfy the predicate;
- `reject`: all required observations are complete and at least one contradicts the predicate;
- `indeterminate`: at least one applicable required state is `error` or `timeout`;
- `not_applicable`: independently fixed pre-execution ground truth makes at least one required state semantically invalid.

Precedence:

```text
not_applicable
    before indeterminate
    before reject
    before accept
```

`not_applicable` is never inferred from runtime output. Within an applicable method, incomplete evidence takes precedence over a complete contradiction.

## 8. Hidden-state isolation

Each projected method contains only its declared state names, state observations, claim slices, and method-specific applicability information.

Changing an outcome outside `M0`, `M1`, or `M2` may change the full source-report digest but must not alter that weaker method's payload or decision. Hidden-state isolation tests are normative.

## 9. Projection artifact

```text
research/DW-001/schema/projection.schema.json
src/deltawitness/_dw001_projection.py
src/deltawitness/dw001.py
research/DW-001/PROJECTION_INTEGRITY.md
```

The verifier recomputes applicability, ordered slices, claim decisions, method decisions, reason codes, shared-state equality, and `projection_sha256`.

The digest is unkeyed. Semantic recomputation is mandatory.

## 10. Synthetic fixture descriptor and identity

Development preparation may use the project-owned deterministic generator only for the explicitly supported taxonomy subset:

```text
research/DW-001/SCENARIO_TAXONOMY.md
research/DW-001/FIXTURE_GENERATOR.md
research/DW-001/schema/fixture-descriptor.schema.json
research/DW-001/schema/fixture-identity.schema.json
src/deltawitness/_dw001_scenarios.py
src/deltawitness/dw001_scenarios.py
```

The descriptor fixes family, control role, generator/template versions, observer arm, command, timeout, paths, state outcomes, failure causes, and nested-method expectations. Expected method labels are recomputed from expected states.

The generator writes fixed owned-synthetic bytes into an absent or empty non-symlink destination and emits deterministic base/candidate commit and tree IDs plus specification identity. Equivalent descriptors must reproduce the same identity in clean supported environments.

Fixture-identity verification recomputes the specification bytes implied by the descriptor and rejects a substituted SHA-256 even when `identity_sha256` is recomputed.

Generator v1 implements only:

- `valid-discriminating-regression`;
- `non-discriminating-candidate-test`;
- `candidate-regression-against-base-tests`.

Assertion weakening, wrong-reason failures, collection/import/setup errors, invalid hybrids, and no-op/already-resolved controls remain required but unsupported. Unsupported mechanisms must not be relabeled as implemented templates.

## 11. Fixture-manifest binding

Scenario-manifest v1 predates the fixture identity and has no fixture-identity digest field. Its schema and digest semantics must not be mutated in place.

The separate relation contract is:

```text
research/DW-001/schema/fixture-manifest-binding.schema.json
src/deltawitness/dw001_fixture_binding.py
research/DW-001/FIXTURE_MANIFEST_BINDING.md
```

The binding builder accepts only one independently verified descriptor, identity, and manifest. Every binding value is derived from those sources.

Binding v1 checks the common relation for:

- study and scenario identity;
- descriptor-to-identity family, generator, template, observer, path, state, and method agreement;
- owned-synthetic manifest provenance;
- exact base and candidate commits;
- path categories;
- observer arm, command, and timeout;
- state applicability, outcomes, and failure causes;
- nested-method decisions and reasons;
- false-assurance family;
- specification path membership and descriptor-derived specification digest.

`relation_scope` separately lists verified relations, manifest-owned governance fields, and fixture-only values absent from manifest v1. In particular, partition, review, authorization, and denominator eligibility remain manifest-owned; tree IDs and specification SHA remain fixture-only.

The verifier re-verifies all sources, validates strict structure, recomputes `binding_sha256`, derives the canonical binding again, and requires exact canonical equality. A recomputed digest cannot hide a source mismatch.

A valid binding cannot authorize execution, make a development scenario denominator-eligible, authenticate a producer, prove creation time, or establish tree-to-commit correspondence without the separately verified materialized repository.

## 12. Scenario-manifest contract

```text
research/DW-001/schema/scenario-manifest.schema.json
src/deltawitness/dw001_contracts.py
```

A manifest fixes:

- study, scenario, and partition identifiers;
- development or committed-holdout partition lock;
- public-safe ownership, license, and authorization provenance;
- exact base and candidate commits;
- disjoint prefix-free path categories;
- execution and observer requirements;
- state applicability, expected observations, and failure causes;
- nested-method expected decisions;
- false-assurance mechanism and environment assumptions;
- reviewer identity, independence disclosure, decision, and rationale;
- `manifest_sha256`.

Stored method labels and denominator eligibility are recomputed. Development manifests are never primary-denominator eligible.

A holdout manifest requires `holdout_committed`, a 64-character commitment digest, and scope `dw001-holdout-index-v1`. An internal digest does not establish that commitment predates execution.

## 13. Result-record contract

```text
research/DW-001/schema/result-record.schema.json
src/deltawitness/dw001_contracts.py
```

A result records the exact manifest and partition; protocol, implementation, generator, and baseline identities; source report, witness, and projection digests; observer arm; exclusions; deviations; expected and observed method decisions; concordance; denominator membership; costs or explicit missingness; and `result_sha256`.

Excluded results remain recorded and ineligible. Applied deviations require approval. Exploratory-only or excluded deviations cannot retain confirmatory eligibility. A results-visible applied deviation cannot retain confirmatory impact `none`.

Measured costs require finite nonnegative values. Missing costs are explicit, never silently encoded as zero.

## 14. Result cross-artifact verification

`verify_result_against_sources` independently verifies manifest, projection, and result semantics and digests, then checks scenario, partition, Git endpoints, observer arm, applicability, source digests, expected and observed decisions, concordance, and denominator membership.

Malformed source objects return typed invalid diagnostics before relational dereference.

The source report must still be strict-decoded and verified separately because the result verifier does not possess its bytes.

Complete contract detail:

```text
research/DW-001/STUDY_CONTRACTS.md
```

## 15. Decision-equivalence execution

For a generated development scenario:

1. validate and retain the fixture descriptor;
2. materialize into a disposable literal destination;
3. verify the fixture identity against the repository;
4. construct and review the scenario manifest;
5. derive and verify the fixture-manifest binding;
6. execute one complete four-state matrix for one observer arm;
7. write, strict-decode, and verify the source report;
8. project `M0` through `M3` from the same observations;
9. verify the projection;
10. construct and verify the result record against its sources;
11. retain the complete artifact chain and separately trusted expected digests.

This controls decision drift across nested methods. It does not make synthetic mechanism probes representative.

Observer-arm comparisons require separately configured homogeneous source reports unless a later frozen protocol defines a validated common dual-channel artifact.

## 16. Cost execution

Native method cost must be measured separately from decision-equivalence projection. A cost run executes only the states required by that method.

The frozen protocol must define order randomization or counterbalancing, cache policy, timing boundaries, state and command counts, wall-clock and CPU measurements, peak resources where supported, repetition policy, and partial-run accounting.

A projected full-matrix run must not be presented as the native runtime of `M0`, `M1`, or `M2`.

## 17. Development-pilot boundary

Before freeze, development material may be used only to test construction and contracts, estimate applicability and invalid-hybrid frequency, estimate cost, select a precision target without holdout inspection, test baseline feasibility, and refine exclusions or deviations.

Development artifacts must remain labeled `development`, outside the primary denominator, and permanently separate from the holdout.

The three implemented families are mechanism probes, not a representative corpus. No effectiveness, superiority, prevalence, or generalization claim may be made from them.

## 18. Ground-truth controls

Ground truth must be fixed without inspecting DeltaWitness outputs.

Every scenario requires state outcomes and causes, applicability, expected method decisions for each observer arm, a false-assurance mechanism, environment assumptions, reviewed rationale, and reviewer independence disclosure.

Generated descriptor expectations must verify before execution. Generator determinism does not create reviewer independence.

A post-freeze ambiguity becomes an exclusion, deviation, or documented dispute. It is never silently relabeled.

## 19. Freeze checklist

No held-out command may execute until the complete protocol is frozen in one immutable commit. Required items include:

- [ ] accepted scenario taxonomy and generator specification;
- [ ] accepted fixture descriptor, identity, and fixture-manifest binding contracts;
- [ ] accepted scenario-manifest and result-record contracts;
- [ ] direct-baseline implementation or exact semantic contract;
- [ ] artifact feasibility, license, language, and safety review;
- [ ] development/holdout split procedure;
- [ ] independent ground-truth review procedure;
- [ ] primary and secondary contrasts;
- [ ] exact denominators;
- [ ] frozen metrics and interval method;
- [ ] pilot-informed precision or sample-size target;
- [ ] stochastic repetition and aggregation policy;
- [ ] frozen exclusions and deviation handling;
- [ ] environment capture and disposable execution requirements;
- [ ] privacy, boundary, and publication review;
- [ ] canonical holdout manifest and expected-label commitment procedure;
- [ ] public commitment recorded before unblinding;
- [ ] exact protocol, implementation, generator, schema, and baseline versions pinned.

An implemented component is not frozen merely because its tests pass. All boxes remain open until the complete protocol is accepted and frozen together.

## 20. Holdout commitment

Before any held-out command:

1. serialize the canonical holdout index and permitted expected-label material;
2. hash canonical bytes;
3. record the digest, canonicalization, protocol commit, generator commit, artifact schemas, and baselines in an immutable public commit or recognized preregistration service;
4. retain sensitive material privately where required;
5. preserve all later deviations without rewriting the original commitment.

A commit containing only individual manifests, fixture identities, or bindings does not bind undisclosed holdout membership.

## 21. Measurements under consideration

The frozen protocol is expected to report explicit all-scenario and applicable-scenario denominators for:

- unsafe acceptance on false-assurance cases;
- valid-patch acceptance and over-refusal;
- indeterminate, not-applicable, and invalid-hybrid rates;
- paired increments `M1-M0`, `M2-M1`, and `M3-M2`;
- failure-cause classification accuracy by observer arm;
- executed-state and command multipliers;
- wall-clock, CPU, and review cost;
- reviewer disagreement and adjudication.

No aggregate accuracy score may replace paired contingency tables and four-way outcome flow. Interval method, multiplicity handling, precision target, and primary endpoint remain unfrozen.

## 22. Falsification and narrowing

Narrow, redesign, or abandon the four-state layer for the tested population if:

- `M3` does not reduce unsafe acceptance relative to `M2`;
- `BB` mostly duplicates simpler evidence;
- invalid or non-applicable hybrids dominate;
- indeterminate or over-refusal rates are operationally unacceptable;
- gains disappear under fair observer and runner controls;
- cost exceeds evidence value;
- results are unstable under harmless transformations;
- independent operators cannot reproduce states, fixtures, bindings, projections, or arithmetic.

Narrow or redesign the generator/binding layer if equivalent descriptors do not reproduce identities, family/control boundaries cannot be maintained, relation records add no detection beyond direct comparison, or toolchain effects dominate fixture identity.

Negative results are valid and must not trigger post-hoc benchmark repair.

## 23. Independent reproduction

Issue #4 remains open. The maintainer's second run or the same agent workflow is not independent.

Until qualifying external reproduction is accepted:

- Gate 0 remains incomplete;
- no result is independently reproduced;
- the roadmap gate remains unchecked;
- reproduction must cite an exact commit or release, not a moving branch.

## 24. Safety and publication

Only synthetic, owned, licensed, or explicitly authorized targets may be used.

The runner and generator are not sandboxes. All execution requires a disposable, non-sensitive environment without credentials or unrelated data. Environment capture is provenance evidence, not containment.

The generator rejects a symbolic-link final destination but does not establish trust in ancestor paths, mounts, namespaces, the Git executable, Python runtime, kernel, or filesystem.

Fixture descriptors, identities, bindings, manifests, reports, projections, and results may expose paths, commands, Git IDs, digests, family labels, observer metadata, reviewer records, authorization references, deviations, exclusions, and cost data. Every export requires privacy and claim-boundary review.

## 25. Deviation policy

Every post-freeze deviation records stable IDs, affected scenario or method, problem, action, result visibility, confirmatory impact, and approval when applied.

A results-visible applied deviation cannot retain impact `none`. The frozen protocol, partition lock, commitment, or original artifacts must never be rewritten to conceal a deviation.

## 26. Current status

### Implemented and synthetically tested

- four-state matrix and typed outcome semantics;
- nested `M0`–`M3` projection with hidden-state isolation;
- strict report, projection, manifest, and result verification;
- exclusions, deviations, denominator, and cost-missingness controls;
- versioned three-family taxonomy and deterministic owned-synthetic generator;
- fixture descriptor and identity contracts;
- descriptor-derived specification-digest verification;
- versioned fixture-manifest binding with strict relation scope;
- malformed-object and recomputed-digest adversarial regressions;
- editable and installed-wheel smoke validation.

### Not implemented, authorized, accepted, or frozen

- five remaining required scenario families;
- reviewed development corpus and pilot authorization;
- direct ecological baseline runners;
- holdout corpus and public commitment;
- aggregation and statistical analysis;
- precision target;
- stochastic repetition policy;
- environmental containment;
- authenticated producers or signed attestations;
- independent reproduction;
- confirmatory result.

## 27. Public wording rule

Permitted:

> DeltaWitness is preparing a preregistered study of nested final-state, fail-to-pass, regression-preservation, and four-state evidence using controlled observer semantics, deterministic owned-synthetic mechanism probes, and explicitly bound study artifacts.

Not permitted from this draft:

> DW-001 proves that four-state verification is superior.

> DeltaWitness has validated the method on held-out coding-agent patches.

> The protocol is frozen, independently reproduced, or production-ready.

Public claims must remain narrower than the evidence available at the cited immutable revision.
