# DW-001 Protocol

**Status:** DRAFT — DEVELOPMENT PILOT ONLY — NOT FROZEN — NO HOLDOUT EXECUTION AUTHORIZED.

**Study identifier:** `DW-001`.

**Implementation base for this revision:** `d96046eaf222d30d371d59f0a935764b1385c76c`. The study-contract implementation, schemas, tests, and this protocol revision on `research/dw-001-study-contracts-v1` remain unfrozen until review and merge.

This document is a protocol candidate, not a preregistration. It may be revised during design review and development-pilot preparation. No held-out scenario may be executed until the freeze checklist is complete and the frozen protocol, generator, manifests, metrics, exclusions, and commitment digest are recorded immutably before unblinding.

## 1. Primary research question

Does a Git-native four-state witness detect materially important false-assurance cases that are missed by stronger nested baselines, at an acceptable execution and review cost?

The primary incremental question is narrower:

> Does adding the independently checked `base implementation + base tests` endpoint and full matrix consistency provide useful evidence beyond a three-state comparator that already checks candidate-test discrimination and original-test preservation?

A separate factorial question asks whether invocation-bound typed outcome receipts provide incremental evidence beyond configured process exit codes when the matrix state set is held constant.

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

Exact patch-path influence is outside the primary acceptance rule for this study.

## 3. Canonical state model

| State | Implementation side | Test side |
|---|---|---|
| `base_base` (`BB`) | base | base |
| `base_candidate` (`BC`) | base | candidate |
| `candidate_base` (`CB`) | candidate | base |
| `candidate_candidate` (`CC`) | candidate | candidate |

The canonical discriminating-regression expectation is:

```text
BB = pass
BC = fail
CB = pass
CC = pass
```

`error` and `timeout` are incomplete observations. They are never converted into semantic `fail`.

## 4. Controlled state-set methods

The primary methods are nested and consume observations from one complete source matrix report for a fixed observer arm.

| Method | Required states | Acceptance predicate |
|---|---|---|
| `M0_FINAL` | `CC` | `CC == pass` |
| `M1_F2P` | `BC`, `CC` | `BC == fail` and `CC == pass` |
| `M2_F2P_P2P` | `BC`, `CB`, `CC` | `BC == fail`, `CB == pass`, and `CC == pass` |
| `M3_FOUR_STATE` | `BB`, `BC`, `CB`, `CC` | canonical four-state pattern |

Primary paired contrasts:

```text
M1 - M0 = candidate-test discrimination
M2 - M1 = original-test preservation
M3 - M2 = base-endpoint validity and complete-matrix consistency
```

These labels describe evidence increments. They are not claims of universal causal effects.

## 5. Observation arms

Each homogeneous source report belongs to exactly one observer arm:

| Observer ID | DeltaWitness observer | Meaning |
|---|---|---|
| `O0_EXIT_CODE` | `exit-code-v1` | configured disjoint process exit classes |
| `O1_TYPED_RECEIPT` | `outcome-receipt-v1` | invocation-bound typed receipt plus process-exit agreement |

A source report containing mixed observer protocols is invalid for projection. The study must not credit the state-set method for a detection caused only by changing the observer.

Combined identifiers are explicit, for example:

```text
M2_F2P_P2P__O0_EXIT_CODE
M2_F2P_P2P__O1_TYPED_RECEIPT
```

## 6. Source-report requirements

The v1 projector accepts only a DeltaWitness matrix report that:

- uses report schema `0.3`;
- passes semantic and complete-report integrity verification;
- was decoded as strict UTF-8 JSON with recursive duplicate-key rejection;
- contains exactly four ordered observations for every claim;
- uses canonical DW-001 expectations;
- has internally consistent state IDs, Git object IDs, observer IDs, `matched`, claim support, completeness, and overall support fields;
- contains at least one claim;
- uses one homogeneous observer arm across all claims.

The projector validates the complete source report before exposing any method decision. Validation of hidden-state integrity is not permission for a method predicate to consume the hidden state's outcome.

The study pipeline must retain the strict-decoded source report. A standalone projection records the source report and witness digests, but it does not contain the source report bytes and cannot independently establish correspondence to them. Source-report verification and projection verification are separate mandatory checks.

## 7. Four-way decision semantics

Every method produces exactly one primary decision:

- `accept`: every required observation is complete and every required predicate is satisfied;
- `reject`: every required observation is complete and at least one required predicate is contradicted;
- `indeterminate`: at least one applicable required observation is `error` or `timeout`;
- `not_applicable`: independently defined pre-execution ground truth declares at least one required state semantically invalid.

Decision precedence is:

```text
not_applicable
    before indeterminate
    before reject
    before accept
```

`not_applicable` is never inferred from command output. It requires a pre-execution scenario annotation and a non-empty reason.

Within an applicable method, `indeterminate` takes precedence over `reject`. Incomplete evidence cannot be converted into a negative semantic finding merely because another required state contradicts the predicate.

## 8. Hidden-state isolation

For each method, the serialized projection contains only:

- its declared required state names;
- observations for those states;
- claims projected from those states;
- method-specific applicability reasons.

Changing an outcome in a state not declared by `M0`, `M1`, or `M2` must not alter that method's payload. The complete source report digest may change, but the nested method decision and evidence slice must not.

Truth-table and hidden-state isolation tests are normative implementation checks.

## 9. Projection artifact

Projection schema:

```text
research/DW-001/schema/projection.schema.json
```

Projection producer and source-report validator:

```text
src/deltawitness/_dw001_projection.py
```

Public API and independent fail-closed semantic verifier:

```text
src/deltawitness/dw001.py
```

Trust-boundary note:

```text
research/DW-001/PROJECTION_INTEGRITY.md
```

The verifier independently recomputes applicability, ordered state slices, claim decisions, method decisions, reason codes, shared-state equality, and `projection_sha256`.

The digest is unkeyed. A caller can recompute it after modifying an artifact, so digest verification never substitutes for semantic recomputation.

## 10. Scenario-manifest contract

The pre-execution artifact is defined by:

```text
research/DW-001/schema/scenario-manifest.schema.json
src/deltawitness/dw001_contracts.py
```

A scenario manifest records:

- stable study, scenario, and partition identifiers;
- a development or committed-holdout partition lock;
- public-safe ownership, license, or authorization provenance;
- immutable base and candidate Git identities;
- disjoint and prefix-free path categories;
- execution and observer requirements;
- applicability, expected observation, and expected failure-cause class for every matrix state;
- expected decisions for all nested methods;
- false-assurance mechanism and environment assumptions;
- reviewer identity, independence disclosure, decision, and rationale;
- `manifest_sha256`.

Stored method labels are not trusted. The manifest verifier recomputes each expected decision from the ordered state ground truth and recomputes denominator eligibility from partition, independent review, and applicability.

A development manifest is never primary-denominator eligible. A holdout manifest requires an external `dw001-holdout-index-v1` commitment digest. The manifest digest binds the recorded commitment but does not prove that it predates execution.

## 11. Result-record contract

The post-execution artifact is defined by:

```text
research/DW-001/schema/result-record.schema.json
src/deltawitness/dw001_contracts.py
```

A result record contains:

- exact scenario-manifest digest and partition;
- protocol, implementation, optional generator, and baseline identities;
- source matrix-report, witness, and projection digests;
- one homogeneous observer arm;
- exclusions and decision references;
- protocol deviations and confirmatory impact;
- expected and observed four-way method decisions;
- concordance;
- primary-denominator membership and deterministic reason;
- method-specific cost fields or explicit missingness;
- `result_sha256`.

An excluded result remains in the record but cannot remain denominator eligible. An applied deviation requires an approval reference. A deviation marked `exploratory_only` or `excluded` cannot silently preserve confirmatory eligibility.

A measured cost requires finite nonnegative wall-clock, CPU, state-count, command-count, and review fields. `not_run` and `unavailable` require `null` quantitative fields and an explicit missing reason. Missing values are not encoded as zero.

## 12. Cross-artifact verification

`verify_result_against_sources` separately verifies:

1. manifest semantics and digest;
2. result semantics and digest;
3. projection semantics and digest;
4. scenario and partition identity;
5. manifest digest recorded by the result;
6. base, candidate, observer, applicability, and non-applicability agreement between manifest and projection;
7. matrix-report, witness, projection, and observer identities recorded by the result;
8. expected decisions from the manifest;
9. observed decisions and reason codes from the projection;
10. concordance and denominator membership across all supplied artifacts.

The verifier does not possess source matrix-report bytes. The source report must still be strict-decoded and verified separately, and its trusted digest must be compared with the projection and result.

Complete contract details are maintained in:

```text
research/DW-001/STUDY_CONTRACTS.md
```

## 13. Decision-equivalence execution

For the primary detection comparison:

1. select a pre-execution manifest whose semantics and digest verify;
2. execute the complete four-state matrix once for one observer arm;
3. strict-decode and integrity-verify the source report;
4. project `M0` through `M3` from the same immutable observations;
5. independently verify projection semantics and digest;
6. construct the result record linked to the supplied manifest and projection;
7. independently verify result semantics, digest, and cross-artifact bindings;
8. retain the complete artifact chain and separately trusted expected digests.

This controls run-to-run drift across nested state-set methods.

Observer-arm comparisons require separately configured homogeneous source reports unless a later frozen protocol defines and validates a common dual-channel observation artifact. The current matrix report does not record enough exit-class configuration to reconstruct every `O0` decision faithfully from an `O1` report after the fact.

## 14. Cost execution

Method-specific operational cost must be measured separately from decision-equivalence projection.

A cost run executes only the states required by that method. The frozen protocol must define:

- randomized or counterbalanced method order;
- cold-cache and warm-cache policy;
- setup, checkout, command, verification, and review timing boundaries;
- state and command counts;
- wall-clock and CPU measurements;
- peak resource measurement where supported;
- retry and stochastic-repetition policy;
- failure and partial-run accounting.

A projected full-matrix run must not be presented as the native runtime of `M0`, `M1`, or `M2`.

## 15. Development-pilot boundary

Before freeze, a development corpus may be used only to:

- test scenario construction;
- test manifest, projection, result, and schema correctness;
- estimate applicability and invalid-hybrid frequency;
- estimate runtime and scenario-generation cost;
- choose a precision target without inspecting holdout results;
- identify operationally impossible baseline artifacts;
- refine exclusion and deviation procedures.

Development-pilot scenarios and outcomes must be labeled `development`. Their method records must remain outside the primary denominator. They cannot be moved into the holdout or reported as confirmatory evidence.

No claim of effectiveness, superiority, prevalence, or generalization may be made from the development pilot.

## 16. Ground-truth controls

Ground truth must be defined without inspecting DeltaWitness outputs.

Every scenario requires:

- expected state outcome and failure-cause class;
- state applicability and reason;
- expected decision for every controlled method and observer arm;
- a false-assurance mechanism;
- explicit environmental assumptions;
- at least one reviewed rationale;
- an independence disclosure for each reviewer.

An `approved` manifest requires an approving reviewer independent of both the scenario author and the implementation. A rejection takes precedence over approval. A post-freeze ambiguity becomes an exclusion, deviation, or documented dispute; it is never silently relabeled.

## 17. Freeze checklist

No held-out execution is authorized until all items are complete in an immutable protocol commit:

- [ ] scenario taxonomy and generator specification;
- [ ] canonical scenario-manifest schema and semantic verifier accepted;
- [ ] canonical result-record schema and semantic verifier accepted;
- [ ] direct-baseline implementation or exact semantic contract;
- [ ] artifact feasibility, license, language, and safety review;
- [ ] development/holdout split procedure;
- [ ] independent ground-truth review procedure;
- [ ] primary contrast and secondary contrasts;
- [ ] exact decision denominators;
- [ ] frozen metrics and interval method;
- [ ] pilot-informed precision or sample-size target;
- [ ] stochastic repetition and aggregation policy;
- [ ] frozen exclusions and deviation handling;
- [ ] environment capture and disposable execution requirements;
- [ ] privacy, boundary, and publication review;
- [ ] canonical holdout manifest and expected-label commitment procedure;
- [ ] public commitment digest recorded before unblinding;
- [ ] exact implementation, generator, and baseline versions pinned.

Implementation of a checklist item does not mark it frozen. The checkboxes remain open until the complete protocol is frozen in one immutable commit.

## 18. Holdout commitment

Before any held-out command runs:

1. serialize the canonical holdout index and permitted expected-label material;
2. compute a digest over canonical bytes;
3. record the digest, canonicalization procedure, protocol commit, generator commit, and baseline versions in an immutable public commit or recognized preregistration service;
4. retain sensitive material privately when required;
5. preserve every post-commit deviation without rewriting the original commitment.

A Git commit containing only the protocol or individual manifests does not credibly bind undisclosed holdout membership or labels.

## 19. Primary measurements under consideration

The frozen protocol is expected to include, with explicit all-scenario and applicable-scenario denominators:

- unsafe-acceptance rate on false-assurance scenarios;
- valid-patch acceptance rate;
- over-refusal rate;
- indeterminate rate;
- not-applicable and invalid-hybrid rate;
- incremental paired detections for `M1-M0`, `M2-M1`, and `M3-M2`;
- failure-cause classification accuracy for observer arms;
- executed-state and command multipliers;
- wall-clock, CPU, and review cost;
- reviewer disagreement and adjudication counts.

No single aggregate accuracy score may replace paired contingency tables and the four-way outcome flow.

The exact interval method, multiplicity handling, precision target, and primary endpoint remain unfrozen.

## 20. Falsification and narrowing criteria

The four-state layer should be narrowed, redesigned, or abandoned for the tested population if the frozen study shows that:

- `M3` does not reduce unsafe acceptance relative to `M2`;
- the incremental `BB` endpoint mostly reproduces information already available from a simpler method;
- invalid or non-applicable hybrids dominate realistic scenarios;
- indeterminate or over-refusal rates make the method operationally unusable;
- observed gains disappear under fair observer and runner controls;
- cost exceeds the incremental evidence value;
- results are unstable under harmless scenario-preserving transformations;
- independent operators cannot reproduce the states, projections, contracts, or arithmetic.

A negative result is a valid outcome and must not trigger post-hoc benchmark repair.

## 21. Independent reproduction

Issue #4 remains open. Work by the maintainer and the same agent workflow does not satisfy its independence criterion.

DW-001 design, implementation QA, and development-pilot preparation may proceed, but:

- Gate 0 remains incomplete;
- no result may be labeled independently reproduced;
- the corresponding roadmap checkbox remains unchecked;
- external reproduction requires exact commit or release identities, not a moving default branch.

## 22. Safety and publication

Only synthetic, owned, licensed, or explicitly authorized targets may be used. External baseline artifacts must be reviewed before execution.

The current runner is not a sandbox. Any development or held-out execution must occur in a disposable, non-sensitive environment without credentials or unrelated data. Environment capture is provenance evidence, not a containment claim.

Manifests and results can expose repository IDs, paths, commands, environment-variable names, reviewer identifiers, authorization references, exclusions, deviations, and cost data. Every exported artifact requires privacy and publication-boundary review.

## 23. Deviation policy

Every deviation after freeze must record:

- stable deviation and rule identifiers;
- affected scenario or method;
- observed problem and action;
- whether results were visible;
- confirmatory impact;
- approval reference when applied.

The frozen protocol, partition lock, and commitment digest must never be rewritten to conceal a deviation.

## 24. Current status

### Implemented and synthetically tested

- deterministic nested projection for `M0` through `M3`;
- homogeneous observer-arm enforcement;
- fail-closed source-report validation;
- explicit four-way decisions;
- hidden-state isolation;
- independent projection semantic verification;
- versioned scenario-manifest and result-record structural schemas;
- fail-closed manifest and result semantic verification;
- ground-truth method recomputation;
- partition-lock and reviewer-independence checks;
- exclusion, deviation, denominator, and cost-missingness checks;
- cross-artifact manifest–projection–result verification;
- deterministic unkeyed integrity digests;
- red-first adversarial fixtures.

### Not implemented or frozen

- scenario taxonomy and generator;
- development corpus;
- direct ecological baseline runners;
- holdout corpus or public commitment;
- aggregation and statistical analysis;
- precision target;
- stochastic repetition policy;
- environmental containment;
- independent reproduction;
- confirmatory result.

## 25. Public wording rule

Permitted:

> DeltaWitness is preparing a preregistered study of nested final-state, fail-to-pass, regression-preservation, and four-state evidence under controlled observer semantics and integrity-bound study contracts.

Not permitted from this draft:

> DW-001 proves that four-state verification is superior.

> DeltaWitness has validated the method on held-out coding-agent patches.

> The protocol is frozen or independently reproduced.

The next protocol revision must remain narrower than the evidence available at that revision.
