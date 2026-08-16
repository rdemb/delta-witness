# DW-001 Protocol

**Status:** DRAFT — NOT FROZEN — OWNED-SYNTHETIC DEVELOPMENT MECHANISM PILOT EXECUTED AND RETAINED — CLAIM-SCOPED MUTATION DESIGN FROZEN AND ONE BOUNDED TYPED RESULT EXECUTED — NO ECOLOGICAL OR HOLDOUT EXECUTION AUTHORIZED.

**Study identifier:** `DW-001`.

**Implementation lineage for this revision:** stable `main` at `687c71bcd1a6edd1cd0831accb74735e82c2f796` plus the claim-scoped mutation-result implementation under review in PR #40. Exact future broader calibration, ecological protocol, implementation, generator, schema, baseline, environment, sampling, and analysis commits remain unpinned until their respective freeze gates.

This document is a protocol candidate, not a preregistration. The sealed five-family owned-synthetic development mechanism pilot has been executed and retained. The later weak-proxy challenge has been executed as development-only negative-control evidence. The claim-scoped mutation plan and catalog froze their source, target, operators, profiles, reference checks, identities, and result taxonomy before execution; one bounded typed development result now executes those exact inputs. None of these steps freezes the broader protocol, authorizes external repository execution, creates a holdout, permits ecological inference, or establishes mutation adequacy.

No held-out command may execute until the complete protocol, target population, sampling frame, instance authorization, containment environment, ground-truth process, metrics, exclusions, versions, and commitment digest are immutably recorded before unblinding.

## 1. Research questions

### 1.1 Primary state-set question

Does a Git-native four-state witness detect materially important false-assurance cases missed by stronger nested baselines at an acceptable execution and review cost?

The primary incremental contrast is:

> Does adding the independently checked `base implementation + base tests` endpoint and complete-matrix consistency provide useful evidence beyond a three-state comparator that already checks candidate-test discrimination and original-test preservation?

### 1.2 Controlled observer question

> When Git states and source/test mechanism are held fixed, does preserving assertion failure versus generic test error change nested patch-evidence decisions relative to configured process exit codes?

### 1.3 Oracle-relevance limitation question

> When a suite contains a genuine assertion failure caused only by collateral behavior while a claim-facing assertion is non-discriminating, do typed outcomes and all nested state-set methods still accept the witness, and can exact selector localization expose the mismatch?

### 1.4 Oracle-strength limitation question

> When the exact predeclared claim selector is itself a genuine typed fail-to-pass witness, can one fixed claim-violating mutant still pass that selector while failing a separately fixed development claim check?

### 1.5 Mutation-design question

> Can the first mutation calibration freeze one outcome-blind generic operator set, one exact source/AST target, one deterministic mutant catalog, and paired strong/weak selector profiles before any mutation-test outcome, while retaining duplicate, invalid, and not-applicable generation records and separating the known weak-proxy mutant from generic operator evidence?

### 1.6 Mutation-result integrity question

> Can the exact frozen catalog be executed through invocation-bound typed selectors while retaining complete preregistration-concordant or preregistration-divergent observations, recomputing all profile/reference/summary/analysis semantics, and refusing to replace the complete table with a scalar score or policy decision?

The oracle-relevance and oracle-strength questions are negative controls. The mutation-design question concerns pre-execution methodological integrity. The mutation-result question concerns bounded execution and evidence retention. Positive results do not establish a complete relevance or strength method, a valid mutation score, operator representativeness, or ecological effectiveness.

## 2. Claims not under test

DW-001 does not establish:

- complete patch correctness, security, or semantic intent;
- test-oracle relevance, adequacy, completeness, or general mutation strength;
- representativeness of the three generic mutants or the historical control;
- mutation adequacy, mutation-score validity, or complete equivalent-mutant classification;
- vulnerability removal or absence of untested regressions;
- production safety or universal causality;
- complete environment reproducibility;
- producer, reviewer, agent, model, or organization authenticity;
- authorization to merge, deploy, publish, execute an external repository, block a merge, or inspect a holdout;
- scientific novelty or general superiority.

Exact path-level influence is outside the primary state-set acceptance rule and may appear only as exploratory secondary evidence where its own prerequisites hold.

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

All primary methods are projected from one immutable source report for one homogeneous observer arm.

| Method | Required states | Acceptance predicate |
|---|---|---|
| `M0_FINAL` | `CC` | `CC == pass` |
| `M1_F2P` | `BC`, `CC` | `BC == fail` and `CC == pass` |
| `M2_F2P_P2P` | `BC`, `CB`, `CC` | `BC == fail`, `CB == pass`, and `CC == pass` |
| `M3_FOUR_STATE` | `BB`, `BC`, `CB`, `CC` | canonical four-state pattern |

Controlled evidence increments:

```text
M1 - M0 = candidate-test discrimination
M2 - M1 = original-test preservation
M3 - M2 = base-endpoint validity and complete-matrix consistency
```

These labels describe nested evidence increments. They are not universal causal effects and do not establish which assertion failed, whether it is relevant, or whether it is strong enough.

## 5. Observation arms

| Observer ID | DeltaWitness observer | Recorded meaning |
|---|---|---|
| `O0_EXIT_CODE` | `exit-code-v1` | configured disjoint process exit classes |
| `O1_TYPED_RECEIPT` | `outcome-receipt-v1` | invocation-bound typed receipt plus process-exit agreement |

A projected comparison contains exactly one observer arm. Mixed-observer reports are invalid because they confound state-set and observation-semantics effects.

Receipt v1 distinguishes assertion failure from generic test error and other aggregate outcomes. It does not:

- identify every error subtype;
- identify which assertion caused a suite failure;
- determine whether a selector is semantically relevant;
- determine whether an assertion is strong enough to reject plausible incorrect implementations;
- authenticate its producer.

An exact synthetic fixture may therefore have predeclared `import_error` ground truth while the runtime receipt honestly records only generic `test_error`.

Combined method/observer identifiers remain explicit, for example:

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

Source-report bytes and projection remain separately mandatory. A projection records source digests but cannot reconstruct omitted source fields.

## 7. Four-way decision semantics

Each method returns one decision:

- `accept`: all applicable required observations are complete and satisfy the predicate;
- `reject`: all applicable required observations are complete and at least one contradicts the predicate;
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

Each projected method contains only its declared state names, observations, claim slices, and method-specific applicability information.

Changing an outcome outside `M0`, `M1`, or `M2` may alter the complete source digest but must not alter that weaker method's payload or decision. Hidden-state isolation tests are normative.

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

Development research may use the project-owned deterministic generator only for explicitly supported families:

```text
research/DW-001/SCENARIO_TAXONOMY.md
research/DW-001/FIXTURE_GENERATOR.md
research/DW-001/schema/fixture-descriptor.schema.json
research/DW-001/schema/fixture-identity.schema.json
src/deltawitness/_dw001_scenarios.py
src/deltawitness/_dw001_wrong_reason.py
src/deltawitness/_dw001_weak_proxy.py
src/deltawitness/dw001_scenarios.py
```

The descriptor fixes family, control role, generator/template versions, observer arm, command, timeout, paths, state outcomes, failure causes, and nested-method expectations. Expected method labels are recomputed from states.

The generator writes fixed owned-synthetic bytes into an absent or empty non-symlink destination and emits exact base/candidate commit and tree IDs plus specification identity. Equivalent descriptors must reproduce the same identity in clean supported environments.

Fixture-identity verification recomputes descriptor-derived specification bytes and rejects a substituted SHA-256 even when `identity_sha256` is recomputed.

Generator v1 currently implements six families:

- `valid-discriminating-regression`;
- `non-discriminating-candidate-test`;
- `candidate-regression-against-base-tests`;
- `wrong-reason-base-import-failure`;
- `wrong-reason-unrelated-assertion`;
- `weak-proxy-oracle`.

The committed ten-arm development mechanism pilot remains fixed to the five families in its sealed plan. The later weak-proxy family is a separate development-only Gate 1 control and does not rewrite that archive.

The schemas remain pre-freeze. Adding a family expands v1 enums while preserving existing artifact validity and digest meaning. Older verifiers may reject newer-family artifacts; every result must retain exact schema and implementation commits.

## 11. Paired import-error observer contrast

The import family uses fixed source and tests. Candidate tests import a candidate-introduced symbol before intended assertions. The same scenario identity and source/test bytes are used under both observer arms.

Expected contrast:

```text
O0: BB/BC/CB/CC = pass/fail/pass/pass
    BC cause     = test_failure_untyped
    M0/M1/M2/M3 = accept/accept/accept/accept

O1: BB/BC/CB/CC = pass/error/pass/pass
    fixture cause = import_error
    receipt class = test_error
    M0/M1/M2/M3 = accept/indeterminate/indeterminate/indeterminate
```

For O1, `import_error` is fixed fixture ground truth and `test_error` is the runtime receipt class. Those layers must not be conflated.

Falsify or redesign the contrast if source/test bytes or scenario identity differ between arms, the import is itself the intended oracle, or the typed arm does not preserve incomplete generic-error evidence.

## 12. Unrelated-assertion oracle-relevance negative control

The unrelated-assertion family uses fixed bytes:

- base `is_admin` is buggy and candidate `is_admin` repairs viewer authorization;
- base `version_label()` returns `v1`, candidate returns `v2`;
- the claim-facing viewer test asserts only that `is_admin(viewer)` returns a Boolean and passes on both implementations;
- a separate collateral assertion requires `version_label() == "v2"`;
- that assertion is the sole source of `BC = fail`;
- removing it makes `BC` pass.

Expected under both observers:

```text
BB/BC/CB/CC = pass/fail/pass/pass
M0/M1/M2/M3 = accept/accept/accept/accept
```

The typed arm records a real assertion failure. Exact selector localization later classifies the claim-facing selector as non-discriminating.

The expected result is a limitation:

```text
real assertion failure
    + typed outcome
    + canonical four-state witness
    != claim-oracle relevance
```

Direct controls must demonstrate that the claim-facing assertion is non-discriminating and the collateral assertion is the sole `BC` failure source.

Falsify or redesign the family if the claim-facing assertion fails on base, the collateral assertion is not the sole failure, either observer returns error/timeout, any nested method does not accept, or collateral behavior is materially part of the declared claim.

## 13. Declared witness-test localization

A separate versioned declaration can bind one claim to exact standard-library unittest logical-test selectors before selector execution.

```text
research/DW-001/schema/claim-witness-declaration.schema.json
research/DW-001/schema/claim-witness-localization.schema.json
src/deltawitness/claim_witness.py
```

The declaration fixes:

- source specification digest and claim ID;
- adapter and adapter version;
- ordered unique selectors;
- adapter-derived commands;
- one aggregate rule;
- declaration digest.

The runner reconstructs exact `BC` and `CC` Git states from the verified report, executes each selector through typed receipts, and emits:

- `discriminating` for typed assertion failure in `BC` and pass in `CC`;
- `non_discriminating` for pass in both states;
- `candidate_invalid` when `CC` does not pass;
- `indeterminate` for error, timeout, missing selector, malformed/contradictory receipt, or unsupported semantics.

Per-selector evidence remains visible. Incomplete evidence is never converted into non-discrimination.

A valid localization proves only that exact predeclared test identities exhibited recorded transitions under exact Git states. It does not prove that the operator selected the semantically correct tests or that those tests are strong enough.

## 14. Weak-proxy-oracle strength negative control

The fixed task asks for administrator-only authorization and a viewer-denial regression test.

Base:

```python
def is_admin(user):
    return user.get("role")
```

Candidate:

```python
def is_admin(user):
    return user.get("role") == "admin"
```

Declared selector:

```text
test_access.AccessTests.test_viewer_result_is_boolean
```

Declared assertion:

```python
self.assertIsInstance(is_admin({"role": "viewer"}), bool)
```

The selector genuinely fails on base and passes on candidate. Under both observers:

```text
BB/BC/CB/CC = pass/fail/pass/pass
M0/M1/M2/M3 = accept/accept/accept/accept
localization = supported / discriminating
```

Fixed mutant:

```python
def is_admin(user):
    return bool(user.get("role"))
```

The mutant passes the declared selector while authorizing a viewer. A separately fixed hidden development claim check passes on candidate and fails on mutant.

Exactly five typed controls are fixed before execution:

```text
base      + declared selector = fail
candidate + declared selector = pass
mutant    + declared selector = pass
candidate + hidden claim      = pass
mutant    + hidden claim      = fail
```

The resulting challenge binds verified descriptor, identity, matrix, projection, declaration, localization, fixed task, candidate, mutant, tests, controls, finding, and limitations.

```text
research/DW-001/WEAK_ORACLE_CHALLENGE.md
research/DW-001/schema/weak-oracle-challenge.schema.json
src/deltawitness/dw001_oracle_challenge.py
```

The expected result is a limitation:

```text
typed assertion failure
    + canonical four-state witness
    + exact declared-selector fail-to-pass localization
    != sufficient oracle strength
```

Falsify or redesign the challenge if the selector is not genuinely fail-to-pass, current localization does not support it, the mutant fails the selector, the hidden check passes on mutant, candidate or mutant contains confounding changes, or repeated clean execution changes stable challenge semantics.

The hidden check is fixed development evidence, not a general oracle. One mutant does not define mutation adequacy or a mutation score.

## 15. Fixture-manifest binding

Scenario-manifest v1 predates fixture identity and has no fixture-identity digest field. Its existing fields and digest semantics are not silently repurposed.

```text
research/DW-001/schema/fixture-manifest-binding.schema.json
src/deltawitness/dw001_fixture_binding.py
research/DW-001/FIXTURE_MANIFEST_BINDING.md
```

The builder accepts one independently verified descriptor, identity, and manifest and derives every relation value.

Binding v1 checks study/scenario identity, descriptor-to-identity relations, owned-synthetic provenance, exact commits, path categories, observer, command, timeout, state and method semantics, false-assurance family, and specification path/digest relations.

`relation_scope` separates verified relations, manifest-owned governance fields, and fixture-only values absent from manifest v1.

The verifier re-verifies all sources, validates strict structure, recomputes `binding_sha256`, derives the canonical binding again, and requires exact equality.

A valid binding cannot authorize execution, create denominator eligibility, authenticate a producer, prove creation time, establish oracle relevance or strength, or establish tree-to-commit correspondence without the separately verified repository.

## 16. Scenario-manifest contract

```text
research/DW-001/schema/scenario-manifest.schema.json
src/deltawitness/dw001_contracts.py
```

A manifest fixes study/scenario/partition identity, partition lock, public-safe provenance, exact Git endpoints, disjoint paths, execution and observer requirements, state and method ground truth, mechanism and environment assumptions, reviewer records, and `manifest_sha256`.

Stored method labels and denominator eligibility are recomputed. Development manifests are never primary-denominator eligible.

A holdout manifest requires `holdout_committed`, a 64-character commitment digest, and scope `dw001-holdout-index-v1`. An internal digest does not establish that commitment predates execution.

## 17. Result-record contract

```text
research/DW-001/schema/result-record.schema.json
src/deltawitness/dw001_contracts.py
```

A result records the exact manifest and partition; protocol, implementation, generator, and baseline identities; source report, witness, and projection digests; observer arm; exclusions; deviations; expected and observed decisions; concordance; denominator membership; costs or explicit missingness; and `result_sha256`.

Excluded results remain recorded and ineligible. Applied deviations require approval. Exploratory-only, excluded, or results-visible deviations cannot silently preserve confirmatory eligibility.

Measured costs require finite nonnegative values. Missing costs are explicit and never encoded as zero.

## 18. Result cross-artifact verification

`verify_result_against_sources` independently verifies manifest, projection, and result semantics and digests, then checks scenario, partition, Git endpoints, observer, applicability, source digests, decisions, concordance, and denominator membership.

Malformed sources return typed invalid diagnostics before relational dereference. The source report remains separately required because the result verifier does not possess its bytes.

Complete details:

```text
research/DW-001/STUDY_CONTRACTS.md
```

## 19. Development execution

For one generated development scenario and observer arm:

1. validate and retain the descriptor;
2. materialize into a disposable literal destination;
3. verify identity against the repository;
4. construct and review the manifest;
5. derive and verify the fixture-manifest binding;
6. execute one complete four-state matrix;
7. write, strict-decode, and verify the report;
8. project `M0` through `M3`;
9. verify the projection;
10. optionally execute a predeclared selector localization;
11. optionally execute a fixed negative-control challenge;
12. construct and verify the result against sources;
13. retain the complete chain and separately trusted expected digests.

This controls decision drift and exposes specific limitations. It does not make synthetic probes representative.

Paired observer probes must fix one scenario and identical mechanism bytes while allowing only declared observer-derived fields to differ.

Oracle-relevance controls must directly establish which assertion is the sole suite-level failure source.

Weak-oracle controls must freeze task, selector, candidate, mutant, hidden check, and outcomes before execution.

Claim-scoped mutation execution must verify the exact plan and catalog, execute no free-form record, retain expected and observed outcomes separately, preserve complete unexpected evidence, and keep every result development-only.

## 20. Cost execution

Native method cost must be measured separately from decision-equivalence projection. A cost run executes only states required by that method.

The claim-scoped mutation result records 25 typed selector commands across five implementation identities. These timings describe only the fixed owned-synthetic workload and are not native cost estimates for broader mutation engines or ecological repositories.

The frozen ecological protocol must define method order, cache policy, timing boundaries, state and command counts, wall-clock and CPU measurement, peak resources where supported, repetition, and partial-run accounting.

A projected full-matrix run must not be presented as native runtime for `M0`, `M1`, or `M2`. Fixed synthetic challenge or mutation-result counts must not be extrapolated to ecological repositories.

## 21. Development boundary and completed mechanism evidence

Development material may be used to:

- test construction, schemas, and cross-artifact contracts;
- estimate mechanism-level feasibility and costs;
- test baseline feasibility;
- design a precision target without holdout inspection;
- refine exclusions, deviations, review procedures, and containment requirements;
- demonstrate known method limitations through explicit negative controls;
- freeze experimental inputs before development calibration;
- execute bounded owned-synthetic calibration while retaining complete positive or negative results.

Development artifacts remain labeled `development`, outside the primary denominator, and permanently separate from holdout material.

The sealed ten-arm five-family development mechanism pilot has been executed and retained:

```text
research/DW-001/development-pilot-plan.v1.json
research/DW-001/development-pilot-archive.v1.json
research/DW-001/DEVELOPMENT_PILOT_V1.md
```

It executed 40 matrix states, 12 selector states, and five controlled contrasts. It emitted no headline score and prohibited ecological inference.

That pilot establishes fixed-pipeline behavior only. The later weak-proxy family is a separate inspected development challenge and is not silently added to the historical pilot population.

The claim-scoped mutation plan and catalog are separate pre-execution development artifacts. The typed mutation result executes only those exact inputs and retains the complete table. None of these artifacts enters the primary denominator or becomes a holdout.

No effectiveness, superiority, prevalence, model-quality, mutation-adequacy, or generalization claim may be made from these development fixtures, plans, or results.

## 22. Ground-truth, selector, mutation, and result controls

Ground truth must be fixed without inspecting DeltaWitness outcomes.

Every scenario requires state outcomes and causes, applicability, expected method decisions, a false-assurance mechanism, environment assumptions, reviewed rationale, and reviewer independence disclosure.

Generated expectations must verify before execution. Generator determinism does not create reviewer independence.

Failure and mutation evidence have separate layers:

- runtime typed class, such as `test_error` or `test_failure`;
- independently fixed mechanism label, such as `import_error`;
- predeclared selector identity and exact outcome transition;
- frozen mutation source, target, operator, and mutant identity;
- observed selector result under one exact mutant;
- separately fixed reference development checks;
- derived profile/reference/record concordance.

A mechanism subtype must not be inferred post hoc from a generic runtime result.

A genuine assertion failure does not establish claim relevance. A discriminating selector does not establish oracle strength. A killed or surviving single mutant does not establish mutation adequacy. A compiled mutant catalog does not establish outcomes. One complete synthetic result table does not establish population performance.

The claim-scoped mutation design froze before outcome inspection:

- one exact source and AST target;
- three ordered generic operators;
- duplicate, invalid, and not-applicable generation controls;
- mutant identity and deduplication rules;
- paired strong and weak selector profiles;
- reference development claim checks;
- killed/survived/invalid/equivalent-review-required/indeterminate taxonomy;
- prohibitions on scores, thresholds, blockers, holdout selection, and denominator eligibility.

The mutation-result contract additionally fixes:

- five implementation identities and 25 selector commands;
- source, test, command, invocation-binding, and typed-receipt relations;
- separate frozen expectations and observed evidence;
- error/timeout precedence over killed/survived;
- non-execution of duplicate, invalid, and not-applicable records;
- complete unexpected-result retention;
- summary and analysis recomputation;
- semantic versus complete-report digests;
- policy and denominator refusal.

A complete observation that disagrees with preregistration remains a negative result. It must not be suppressed as a harness error. Malformed or contradictory evidence remains invalid and must not be relabeled as unexpected.

Any future mutation or coverage study must additionally freeze before outcome inspection:

- broader execution environment and command semantics;
- mutant result aggregation and precedence;
- equivalent-mutant review procedure;
- coverage targets and collection semantics;
- positive and negative control population;
- thresholds, exclusions, and missingness;
- calibration and policy boundary.

Real-corpus relevance and strength require separate reviewed procedures, disagreement handling, and uncertainty. Where evidence is insufficient, labels remain unknown rather than inferred.

A post-freeze ambiguity becomes an exclusion, deviation, or documented dispute. It is never silently relabeled.

## 23. Ecological source-universe boundary

The design-only source universe currently records SWE-bench and TDD-Bench Verified as candidate source classes with exact reviewed implementation-repository revisions, repository-level license metadata, known biases, and unresolved blockers.

```text
research/DW-001/ecological-source-universe.v1.json
research/DW-001/ECOLOGICAL_SOURCE_UNIVERSE.md
src/deltawitness/dw001_ecological.py
```

It keeps:

```text
execution_authorized  = false
containment_status    = unaccepted
sampling_frame_status = unfrozen
holdout_selected      = false
holdout_inspected     = false
```

Repository-level license metadata does not establish dataset-release, underlying-project, patch, test, environment, execution, redistribution, or publication authorization.

A valid source-universe artifact does not authorize dataset download, instance admission, environment construction, repository execution, or ecological inference.

## 24. Claim-scoped mutation plan and mutant catalog

Canonical pre-execution artifacts:

```text
research/DW-001/claim-scoped-mutation-plan.v1.json
research/DW-001/claim-scoped-mutant-catalog.v1.json
research/DW-001/schema/claim-scoped-mutation-plan.schema.json
research/DW-001/schema/claim-scoped-mutant-catalog.schema.json
research/DW-001/MUTATION_CALIBRATION_PLAN.md
src/deltawitness/dw001_mutation_plan.py
```

Exact identities:

```text
plan_id         = DW-001-CLAIM-SCOPED-MUTATION-PLAN-V1
operator_set_id = python-boolean-predicate-minimal-v1
adapter_id      = python-stdlib-ast-return-v1
plan_sha256     = 0ebf64e1de76849050c86d8a4d53d72d8067561ab48b4bd5a4083495dc99fe37
catalog_sha256  = 7b3e405bd3893f532c0ccfa16e9cc208422bbdd20dfe82a002c99342a04201c0
```

The fixed source is the project-owned candidate authorization predicate used by the weak-proxy challenge. Public artifacts retain source SHA-256 and a versioned semantic-AST digest but do not publish source or mutant bodies.

Target rules require exactly one top-level function named `is_admin` with one return-expression target. Target identity binds source digest, path, symbol, node kind, cardinality, and exact source positions.

The semantic-AST compatibility rule records node kinds and non-empty declared fields while excluding source locations and empty optional fields. It is validated only for the fixed source and Python 3.11–3.14; it is not a universal AST canonicalization claim.

The frozen generic operator order is:

```text
return-constant-false-v1
return-constant-true-v1
comparison-eq-to-ne-v1
```

Separate generation controls require one duplicate, one not-applicable, and one compile-invalid record. The complete catalog retains:

```text
3 generated
1 duplicate
1 not_applicable
1 invalid
```

The known `nonempty-role-boolean-v1` weak-proxy mutant remains a historical challenge control and is explicitly excluded from generic operator evidence and generalization claims.

The paired profiles use the same source and generic mutants:

```text
strong-authorization-oracle-v1
weak-boolean-proxy-v1
```

The plan itself authorizes no external execution, holdout, score, threshold, blocker, or denominator eligibility. Its identities remain immutable inputs to the separate result runner.

Plan and catalog verifiers reconstruct complete canonical artifacts from fixed source and constants. Recomputed unkeyed digests cannot hide source, target, operator, profile, generation-status, duplicate, invalid, summary, authorization, holdout, score, threshold, or denominator drift.

## 25. Claim-scoped mutation result

Canonical result artifacts:

```text
research/DW-001/schema/claim-scoped-mutation-result.schema.json
research/DW-001/MUTATION_RESULT_V1.md
src/deltawitness/dw001_mutation_results.py
scripts/smoke_dw001_mutation_results.py
```

The runner first verifies the exact plan and catalog. It then executes:

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

Duplicate, invalid, and not-applicable records remain ordered in the result with zero commands and explicit non-execution reasons.

Every selector stores:

```text
expected_observed
observed
concordant
```

Every profile and reference group stores:

```text
expected_outcome
outcome
concordant
```

Record concordance, summary counts, and top-level analysis are recomputed. A complete typed observation that diverges from preregistration remains valid evidence and produces `analysis.status = unexpected`. This is a negative result, not a harness failure.

The expected current owned-synthetic contrast is:

```text
all 3 generic mutants:
    strong profile -> killed
    weak profile   -> survived
    reference      -> claim_violation_observed
```

The historical control is executed but excluded from generic evidence. Agreement with this table validates the bounded mechanism only.

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

`semantic_sha256` excludes timestamps, runtime metadata, output digests, and timing while retaining expected/observed outcomes, receipt identities, concordance, summary, analysis, and policy. `report_sha256` binds the complete document.

Malformed structure, source/selector/command/binding substitution, receipt contradiction, impossible stored aggregates, non-finite costs, or digest tampering fail closed. An `unexpected` label cannot rescue invalid evidence.

A valid result does not establish mutation adequacy, equivalent-mutant completeness, real-agent prevalence, ecological effectiveness, or merge-policy validity.

## 26. Freeze checklist

No held-out command may execute until the complete protocol is frozen in one immutable commit. Required items include:

- [ ] accepted scenario taxonomy and generator specification;
- [ ] accepted descriptor, identity, binding, manifest, result, declaration, and localization contracts;
- [x] frozen development-only claim-scoped mutation source, operator set, profiles, target identity, and deterministic generation catalog;
- [x] implemented development-only typed mutation-result contract with complete expected/unexpected evidence retention;
- [ ] accepted mutation-result population, equivalent-mutant review, coverage-evidence, and policy contracts for confirmatory analysis;
- [ ] direct-baseline implementations or exact semantic contracts;
- [ ] immutable dataset releases and exact instance manifest;
- [ ] per-instance license, authorization, environment, and publication review;
- [ ] accepted target population, unit of analysis, sampling frame, and duplicate/cluster handling;
- [ ] accepted containment environment;
- [ ] development/holdout split procedure;
- [ ] independent ground-truth, failure-subtype, selector-relevance, equivalent-mutant, and oracle-strength review procedures;
- [ ] primary and secondary contrasts;
- [ ] exact denominators;
- [ ] frozen metrics, interval method, multiplicity handling, and precision target;
- [ ] stochastic repetition and aggregation policy;
- [ ] frozen exclusions and deviations;
- [ ] privacy, boundary, and publication review;
- [ ] canonical holdout manifest and expected-label commitment procedure;
- [ ] public commitment recorded before unblinding;
- [ ] exact protocol, implementation, generator, schema, baseline, image, and dependency versions pinned.

The checked mutation items apply only to the committed owned-synthetic development plan/catalog/result. They do not freeze a confirmatory mutation method or broader protocol. Passing tests or matching the preregistered table does not freeze the study.

## 27. Holdout commitment

Before any held-out command:

1. serialize the canonical holdout index and permitted expected-label material;
2. hash canonical bytes;
3. record digest, canonicalization, protocol commit, generator commit, artifact schemas, baselines, environment image, and dependency identities immutably;
4. retain sensitive material privately where required;
5. preserve later deviations without rewriting the commitment.

A commit containing only individual manifests, identities, source metadata, mutation plans, catalogs, development results, or challenge artifacts does not bind undisclosed holdout membership.

## 28. Measurements under consideration

The frozen ecological protocol is expected to report explicit all-scenario and applicable-scenario denominators for:

- unsafe acceptance on false-assurance cases;
- valid-patch acceptance and over-refusal;
- indeterminate, not-applicable, and invalid-hybrid rates;
- paired increments `M1-M0`, `M2-M1`, and `M3-M2`;
- assertion-failure versus generic-error classification by observer arm;
- declared-selector localization outcomes;
- failure-subtype accuracy only where independently labeled;
- oracle-relevance and mutation-warning performance only after reviewed procedures exist;
- expected versus observed mutation outcomes and concordance;
- per-mutant killed, survived, invalid, equivalent-review-required, indeterminate, and non-executed outcomes;
- duplicate and not-applicable generation records;
- surviving claim-violating mutants and invalid/equivalent mutant handling;
- executed-state and command multipliers;
- wall-clock, CPU, resource, and review costs;
- reviewer disagreement and adjudication.

No aggregate accuracy or mutation score may replace paired tables, four-way outcome flow, per-selector evidence, and the complete retained per-mutant table. Interval method, multiplicity handling, precision target, sampling frame, and primary endpoint remain unfrozen.

## 29. Falsification and narrowing

Narrow, redesign, or abandon the four-state layer for the tested population if:

- `M3` does not reduce unsafe acceptance relative to `M2`;
- `BB` mostly duplicates simpler evidence;
- invalid or non-applicable hybrids dominate;
- indeterminate or over-refusal rates are operationally unacceptable;
- gains disappear under fair observer and runner controls;
- cost exceeds evidence value;
- results are unstable under harmless transformations;
- independent operators cannot reproduce states, fixtures, relations, or arithmetic.

Narrow or redesign typed observation if it does not improve cause separation beyond exit-code baselines or creates unacceptable false indeterminacy.

Narrow or redesign selector localization if unstable framework identities, changed discovery semantics, or over-refusal exceed its provenance value.

Narrow or redesign the frozen mutation design if:

- Python 3.11–3.14 do not reproduce exact source, AST, target, mutant, and catalog identities;
- AST round-tripping changes semantics outside the target;
- duplicate, invalid, or not-applicable records cannot be retained deterministically;
- generic operators merely restate the known PR #34 control;
- operator choice dominates later outcomes;
- established mutation tooling or a simpler fixed-mutant baseline offers the same evidence with lower complexity.

Narrow or redesign the mutation-result layer if:

- complete unexpected observations are suppressed as harness errors;
- malformed or contradictory evidence is accepted as an unexpected result;
- error or timeout is counted as killed;
- generation-only records leak into execution denominators;
- summaries or analysis drift from the complete table;
- repeated clean runs change stable semantic outcomes;
- source, selector, command, binding, receipt, or policy substitution survives semantic verification;
- the complete table cannot be published without exposing prohibited source or raw output.

Narrow or redesign any broader mutation/oracle-integrity layer if it:

- cannot expose the weak-proxy negative control without materially rejecting valid controls;
- cannot preserve the unrelated-assertion distinction;
- selects operators, mutants, thresholds, or exclusions after results are visible;
- hides surviving claim-violating mutants behind one scalar score;
- treats compile-invalid or execution-error mutants as killed;
- treats an LLM explanation as an unverified decision authority;
- becomes more complex than a stronger direct baseline without incremental evidence.

Negative and unexpected results are valid and must not trigger post-hoc operator, selector, expected-label, or benchmark repair without a recorded deviation.

## 30. Independent reproduction

Issue #4 remains open. The maintainer's second run, another machine controlled by the same workflow, or another run by the same agent process is not independent.

Until qualifying external reproduction is accepted:

- Gate 0 remains incomplete;
- no result is independently reproduced;
- the roadmap gate remains unchecked;
- reproduction must cite an exact commit or release.

## 31. Safety and publication

Only synthetic, owned, licensed, or explicitly authorized targets may be used.

The runner and generator are not sandboxes. Execution requires a separately secured disposable, non-sensitive environment without credentials or unrelated data. Environment capture is provenance, not containment.

Current weak-oracle controls and the claim-scoped mutation result execute only fixed project-owned Python bytes in temporary directories. The mutation-plan adapter parses, transforms, unparses, reparses, and compiles the same fixed project-owned source. None authorizes external repository execution.

Artifacts may expose prompts, paths, commands, selectors, mutant IDs, AST/source/test digests, invocation bindings, receipt metadata, Git IDs, family labels, observer metadata, reviewer records, authorization references, deviations, exclusions, timings, and costs. Every export requires privacy and claim-boundary review.

Raw tracebacks and command output remain excluded by default. Source, mutant, and test bodies are excluded from public mutation plan/catalog/result artifacts. Output digests can still reveal equality or support guessing of low-entropy values.

## 32. Deviation policy

Every post-freeze deviation records stable IDs, affected scenario or method, problem, action, result visibility, confirmatory impact, and approval when applied.

A results-visible applied deviation cannot retain impact `none`. Frozen protocol, sampling frame, partition lock, commitment, mutation source, operator set, profiles, target identities, mutant catalog, reference checks, expected outcomes, or original artifacts must never be rewritten to conceal a deviation.

Complete unexpected observations remain in the original result. A later design change must cite them and create a new version rather than rewriting the earlier record.

## 33. Current status

### Implemented and synthetically tested

- four-state matrix and typed outcome semantics;
- nested `M0`–`M3` projection with hidden-state isolation;
- strict report, projection, manifest, result, fixture, and binding verification;
- exclusions, deviations, denominator, and cost-missingness controls;
- six fixed owned-synthetic families;
- paired exit-code/typed import-error observer contrast;
- unrelated-assertion oracle-relevance negative control and direct collateral ablation;
- exact declared unittest-selector localization under reconstructed `BC`/`CC` states;
- weak-proxy oracle-strength negative control with one fixed surviving claim-violating mutant;
- deterministic integrity-bound weak-oracle challenge artifact;
- sealed and retained five-family development mechanism pilot;
- design-only ecological source universe with execution authorization false;
- frozen outcome-blind minimal stdlib-AST mutation operator set;
- exact source, semantic-AST, target, generated-mutant, duplicate, invalid, and not-applicable identities;
- paired strong/weak selector profiles over identical source and generic mutant catalog;
- known weak-proxy control excluded from generic operator evidence;
- committed mutation plan and deterministic catalog;
- typed execution of candidate, three generic mutants, and one historical control through 25 frozen selectors;
- complete per-selector, profile, reference, record, summary, analysis, and cost evidence;
- complete unexpected-result retention without weakening malformed-evidence rejection;
- generation-only records retained with zero execution;
- stable mutation-result semantic digest and complete-report digest;
- descriptor-derived specification verification;
- malformed-object and recomputed-digest regressions;
- editable and installed-wheel full-chain smoke validation on Python 3.11–3.14.

### Not implemented, authorized, accepted, or frozen

- broader mutation population beyond one source and three generic operators;
- independent equivalent-mutant adjudication;
- calibrated false-warning, missed-warning, applicability, or mutation-score estimates;
- assertion-delta weakening analysis;
- claim-boundary coverage analysis;
- over-mocking analysis;
- broader setup/dependency, invalid-hybrid, no-op, and stochastic families;
- validated claim-to-oracle relevance or strength analyzer;
- immutable ecological dataset releases and per-instance admission records;
- accepted sampling frame, reviewer protocol, or containment environment;
- ecological baseline runners or authorized external execution;
- holdout corpus and public commitment;
- aggregation and statistical analysis;
- precision target and stochastic repetition policy;
- authenticated producers or signed attestations;
- independent reproduction;
- confirmatory result.

## 34. Public wording rule

Permitted:

> DeltaWitness is preparing a preregistered comparison of nested patch-evidence methods, observer semantics, and test-integrity signals using deterministic development controls and explicitly bound artifacts.

> One controlled synthetic pair shows that generic typed error evidence can prevent an exit-code-only import failure from being accepted as semantic fail-to-pass evidence.

> A separate negative case shows that typed suite failure and a canonical four-state pattern do not establish that the failing assertion is relevant to the declared claim.

> A further development-only challenge shows one exact declared fail-to-pass selector that a fixed claim-violating mutant survives.

> A pre-execution development plan freezes one minimal generic AST operator set, exact mutant identities, and paired strong/weak selector profiles before mutation-test outcomes.

> One bounded owned-synthetic result executes that exact catalog through 25 typed selectors, retains the complete table, and separates preregistered expectations from observed outcomes and concordance.

> In the current bounded table, the three generic mutants are killed by the strong profile and survive the weak Boolean-proxy profile; this is development mechanism evidence only.

Not permitted from this draft:

> Typed receipts are generally superior or diagnose all failures.

> Selector localization proves semantic relevance.

> The weak-proxy challenge or bounded result validates mutation testing or complete oracle strength.

> The frozen catalog or one result table establishes mutation adequacy, representative operator quality, or a valid mutation score.

> Four-state replay proves patch correctness.

> DW-001 proves DeltaWitness is superior.

> DeltaWitness has validated the method on held-out coding-agent patches.

> The protocol is frozen, independently reproduced, production-ready, or scientifically novel.

Public claims must remain narrower than evidence at the cited immutable revision.
