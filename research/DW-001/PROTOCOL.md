# DW-001 Protocol

**Status:** DRAFT — DEVELOPMENT PILOT ONLY — NOT FROZEN — NO HOLDOUT EXECUTION AUTHORIZED.

**Study identifier:** `DW-001`.

**Implementation anchor for this draft:** `c8dbb48b70f6d79484f886590433fce922a1b8cd` plus the reviewed commits on `research/dw-001-projection-v1`.

This document is a protocol candidate, not a preregistration. It may be revised during design review and development-pilot work. No held-out scenario may be executed until the freeze checklist in Section 14 is complete and the frozen protocol, generator, manifests, metrics, exclusions, and commitment digest are recorded in an immutable commit.

## 1. Primary research question

Does a Git-native four-state witness detect materially important false-assurance cases that are missed by stronger nested baselines, at an acceptable execution and review cost?

The primary incremental question is narrower:

> Does adding the independently checked `base implementation + base tests` endpoint and full matrix consistency produce useful evidence beyond a three-state comparator that already checks candidate-test discrimination and original-test preservation?

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

## 7. Decision semantics

Every method produces exactly one primary decision:

- `accept`: every required observation is complete and every required predicate is satisfied;
- `reject`: every required observation is complete and at least one required predicate is contradicted;
- `indeterminate`: at least one applicable required observation is `error` or `timeout`;
- `not_applicable`: independently frozen scenario ground truth declares at least one required state semantically invalid.

Decision precedence is:

```text
not_applicable
    before indeterminate
    before reject
    before accept
```

`not_applicable` is never inferred from command output. It requires an independently defined scenario annotation and a non-empty reason.

Within an applicable method, `indeterminate` takes precedence over `reject`. Incomplete evidence cannot be converted into a negative semantic finding merely because another required state contradicts the predicate.

## 8. Hidden-state isolation

For each method, the serialized method payload contains only:

- its declared required state names;
- observations for those states;
- claims projected from those states;
- method-specific applicability reasons.

Changing an outcome in a state not declared by `M0`, `M1`, or `M2` must not alter that method's payload. The complete source report digest may change, but the nested method decision and evidence slice must not.

Truth-table and hidden-state isolation tests are normative implementation checks.

## 9. Projection artifact

The deterministic projection schema is:

```text
research/DW-001/schema/projection.schema.json
```

The implementation is:

```text
src/deltawitness/dw001.py
```

A projection records:

- schema and study identifiers;
- scenario identifier;
- exact source report and witness digests;
- exact base, candidate, and specification identities;
- observer arm;
- independently declared state applicability;
- all four nested method decisions;
- only each method's allowed state observations;
- `projection_sha256` over the complete projection with that field replaced by `null`.

The projection has no timestamp. Re-projecting the same source report, scenario identifier, and applicability declaration must produce identical bytes under canonical serialization.

The digest is unkeyed. It detects modification only when compared with a separately trusted value and does not authenticate the producer.

## 10. Decision-equivalence execution

For the primary detection comparison:

1. execute the complete four-state matrix once for one observer arm;
2. integrity-verify the source report;
3. project `M0` through `M3` from the same immutable observations;
4. prevent every method payload from including undeclared states;
5. retain the source report and projection digests.

This controls run-to-run drift across nested state-set methods.

Observer-arm comparisons require separately configured homogeneous source reports unless a later frozen protocol defines and validates a common dual-channel observation artifact. The current matrix report does not record enough exit-class configuration to reconstruct every `O0` decision faithfully from an `O1` report after the fact.

## 11. Cost execution

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

## 12. Development pilot boundary

Before freeze, a development corpus may be used only to:

- test scenario construction;
- test projector and schema correctness;
- estimate applicability and invalid-hybrid frequency;
- estimate runtime and scenario-generation cost;
- choose a precision target without inspecting holdout results;
- identify operationally impossible baseline artifacts;
- refine exclusion and deviation procedures.

Development-pilot scenarios and outcomes must be labeled `development`. They cannot be moved into the holdout or reported as confirmatory evidence.

No claim of effectiveness, superiority, prevalence, or generalization may be made from the development pilot.

## 13. Required scenario and result controls

Before freeze, every scenario must have an independently reviewed manifest containing at least:

- stable scenario ID and family;
- development or holdout partition;
- source, license, ownership, or authorization basis;
- immutable base and candidate Git identities;
- declared code, test, and documentation paths;
- command, observer, timeout, and environment requirements;
- expected semantic outcome for every state;
- method applicability and non-applicability reasons;
- expected decision for every controlled method;
- false-assurance mechanism;
- known environmental assumptions;
- reviewer identity and rationale.

Every result must retain the four-way decision, exact denominator membership, source identities, observer arm, report digest, projection digest, cost fields, exclusions, and deviations.

Ground truth must be defined without inspecting DeltaWitness outputs. A post-freeze ambiguity becomes an exclusion, deviation, or reported dispute under a frozen rule; it is not silently relabeled.

## 14. Freeze checklist

No held-out execution is authorized until all items are complete in an immutable protocol commit:

- [ ] scenario taxonomy and generator specification;
- [ ] canonical scenario-manifest schema;
- [ ] canonical result and aggregation schemas;
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

A completed checklist authorizes execution under the frozen protocol. It does not itself establish a positive result.

## 15. Holdout commitment

Before any held-out command runs:

1. serialize the canonical holdout manifest and expected-label material permitted by the publication policy;
2. compute a digest over canonical bytes;
3. record the digest, canonicalization procedure, protocol commit, generator commit, and baseline versions in an immutable public commit or recognized preregistration service;
4. retain sensitive material privately when required;
5. preserve every post-commit deviation without rewriting the original commitment.

A Git commit containing only the protocol does not credibly bind undisclosed holdout membership or labels.

## 16. Primary measurements under consideration

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

No single aggregate accuracy score may replace the paired contingency tables and four-way outcome flow.

The exact interval method, multiplicity handling, precision target, and primary endpoint remain unfrozen.

## 17. Falsification and narrowing criteria

The four-state layer should be narrowed, redesigned, or abandoned for the tested population if the frozen study shows that:

- `M3` does not reduce unsafe acceptance relative to `M2`;
- the incremental `BB` endpoint mostly reproduces information already available from a simpler method;
- invalid or non-applicable hybrids dominate realistic scenarios;
- indeterminate or over-refusal rates make the method operationally unusable;
- observed gains disappear under fair observer and runner controls;
- cost exceeds the incremental evidence value;
- results are unstable under harmless scenario-preserving transformations;
- independent operators cannot reproduce the states, projections, or arithmetic.

A negative result is a valid outcome and must not trigger post-hoc benchmark repair.

## 18. Independent reproduction

Issue #4 remains open. Work by the maintainer and the same agent workflow does not satisfy its independence criterion.

DW-001 design, implementation QA, and a development pilot may proceed, but:

- Gate 0 remains incomplete;
- no result may be labeled independently reproduced;
- the corresponding roadmap checkbox remains unchecked;
- external reproduction requires exact commit or release identities, not a moving default branch.

## 19. Safety and publication

Only synthetic, owned, licensed, or explicitly authorized targets may be used. External baseline artifacts must be reviewed before execution.

The current runner is not a sandbox. Any development or held-out execution must occur in a disposable, non-sensitive environment without credentials or unrelated data. Environment capture is provenance evidence, not a containment claim.

Raw output, paths, dependency details, and scenario material require privacy and boundary review before publication.

## 20. Deviation policy

Every deviation after freeze must record:

- timestamp and operator;
- affected scenario or method;
- original rule;
- observed problem;
- replacement action;
- whether labels or results were visible;
- impact on confirmatory and exploratory analyses;
- approval and publication decision.

The frozen protocol and commitment digest must never be rewritten to conceal a deviation.

## 21. Current status

### Implemented

- deterministic nested projection for `M0` through `M3`;
- homogeneous observer-arm enforcement;
- fail-closed source-report validation and integrity verification;
- explicit `accept`, `reject`, `indeterminate`, and `not_applicable` decisions;
- method-specific hidden-state isolation;
- deterministic projection digest;
- machine-readable projection schema;
- truth-table, confound, applicability, integrity, and tamper tests.

### Not implemented or frozen

- scenario generator and canonical scenario manifest;
- development corpus;
- holdout corpus or commitment;
- direct ecological baseline runners;
- aggregation and statistical analysis;
- precision target;
- environmental containment;
- independent reproduction;
- confirmatory result.

## 22. Public wording rule

Permitted:

> DeltaWitness is preparing a preregistered study of nested final-state, fail-to-pass, regression-preservation, and four-state evidence under controlled observer semantics.

Not permitted from this draft:

> DW-001 proves that four-state verification is superior.

> DeltaWitness has validated the method on held-out coding-agent patches.

> The protocol is frozen or independently reproduced.

The next protocol revision must remain narrower than the evidence available at that revision.
