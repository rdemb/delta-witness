# DW-001 Scenario Taxonomy v1

**Status:** development-pilot design contract; not frozen; no pilot or held-out execution authorized.

This taxonomy defines mechanism and control labels for deterministic owned-synthetic DW-001 fixtures. A family identifier is not a narrative tag: expected four-state observations, failure-cause declarations, and nested-method decisions are recomputed by the fixture verifier.

The current generator implements four controlled families. Remaining issue #2 mechanisms stay explicit rather than being silently treated as covered. The schema is still pre-freeze; every result must pin the exact implementation commit because older v1 verifiers do not understand families added later during development.

## Taxonomy invariants

Every family must define:

- one falsifiable false-assurance mechanism or control purpose;
- valid-patch or false-assurance role;
- state applicability before execution;
- expected `BB`, `BC`, `CB`, and `CC` observations;
- expected `M0_FINAL`, `M1_F2P`, `M2_F2P_P2P`, and `M3_FOUR_STATE` decisions;
- observer requirements and failure-cause boundary;
- a contrast or counterexample that would invalidate the label;
- fixed owned-synthetic bytes or another auditable generation rule.

Stored method decisions are not authoritative. They are derived from state semantics using the DW-001 predicate contract.

## Implemented deterministic subset

| Family ID | Role | Observer | Expected states `BB / BC / CB / CC` | Expected methods `M0 / M1 / M2 / M3` | Isolated contrast |
|---|---|---|---|---|---|
| `valid-discriminating-regression` | valid-patch control | `O0` or `O1` | `pass / fail / pass / pass` | `accept / accept / accept / accept` | positive control for a valid discriminating repair |
| `non-discriminating-candidate-test` | false-assurance case | `O0` or `O1` | `pass / pass / pass / pass` | `accept / reject / reject / reject` | incremental value of `BC` beyond final-state execution |
| `candidate-regression-against-base-tests` | false-assurance case | `O0` or `O1` | `pass / fail / fail / pass` | `accept / accept / reject / reject` | incremental value of `CB` beyond fail-to-pass validation |
| `wrong-reason-base-import-failure` | false-assurance case | `O0` | `pass / fail / pass / pass` | `accept / accept / accept / accept` | exit-code-only false assurance from a pre-assertion import error |
| `wrong-reason-base-import-failure` | false-assurance case | `O1` | `pass / error / pass / pass` | `accept / indeterminate / indeterminate / indeterminate` | typed preservation of error rather than semantic failure |

### `valid-discriminating-regression`

Mechanism:

- the base implementation accepts any non-empty role;
- the candidate accepts only `admin`;
- candidate tests add a viewer-denial assertion;
- original tests remain satisfied.

Falsification boundary:

- `BC` is not an assertion failure;
- `CB` does not pass;
- any required state is indeterminate;
- a weaker method changes because it consumed a hidden state.

This is a positive control, not evidence that real valid patches generally have this shape.

### `non-discriminating-candidate-test`

Mechanism:

- the candidate repairs the role check;
- the added test repeats an administrator example already passing on the base;
- final-state execution remains green without candidate-test discrimination.

Falsification boundary:

- candidate tests fail on the base;
- the family depends on execution error rather than semantic pass;
- `M0` rejects or `M1` accepts.

The family tests only the missing `BC` signal. It does not claim the patch itself is incorrect.

### `candidate-regression-against-base-tests`

Mechanism:

- candidate tests check administrator and viewer behavior;
- the candidate satisfies them;
- the original missing-role denial test is absent from the candidate test world;
- the candidate regresses that original behavior.

Falsification boundary:

- `CB` passes;
- `BC` does not expose the declared regression;
- `CC` does not pass;
- `M1` rejects or `M2` accepts.

This is a regression-preservation probe, not a general oracle-strength benchmark.

### `wrong-reason-base-import-failure`

Fixed mechanism:

- base code contains `is_admin` but not `normalize_role`;
- candidate code adds both the role fix and `normalize_role`;
- candidate tests import `is_admin` and `normalize_role` at module import time;
- under `base implementation + candidate tests`, import fails before the intended assertions execute;
- base tests pass under both implementation worlds;
- candidate tests pass under the candidate implementation.

The same scenario identifier and the same source/test bytes are used for both observer arms. Only observer-derived descriptor fields differ: observer, observer ID, command, expected states, expected methods, and descriptor digest.

#### Exit-code arm

`exit-code-v1` maps the ordinary nonzero process status to configured `fail`. It cannot distinguish the import error from an intended assertion failure:

```text
BB = pass
BC = fail  / test_failure_untyped
CB = pass
CC = pass
```

The resulting canonical-looking matrix is complete and all four nested methods accept. This is the controlled false-assurance arm.

#### Typed-receipt arm

The built-in unittest adapter records zero assertion failures and at least one test error. DeltaWitness preserves `BC` as `error`, so all methods requiring that state are indeterminate:

```text
BB = pass
BC = error / predeclared import_error
CB = pass
CC = pass
```

Receipt v1 reports the runtime class `test_error`. It does **not** claim to distinguish import, collection, setup, dependency, or infrastructure subtypes. `import_error` is independently fixed ground truth for these exact owned-synthetic bytes, not a subtype inferred from the generic receipt.

Falsification boundary:

- the exit-code arm does not produce the canonical-looking matrix;
- the typed arm records an assertion failure or complete semantic `fail`;
- source/test bytes or scenario identity differ between arms;
- method differences arise from different state sets rather than observer semantics;
- the missing-symbol import is itself the intended oracle;
- harmless environment variation changes the declared mechanism.

This single pair does not estimate how often wrong-reason failures occur in real patches.

## Required but not yet generated

| Planned family | Required distinction before implementation |
|---|---|
| assertion or test weakening | materially weakened oracle versus behavior-preserving test refactor |
| unrelated assertion failure | intended regression exposure versus a different assertion sharing the same failure channel |
| collection/setup/dependency/infrastructure error | runtime subtype evidence or independently reviewed ground truth without post-result relabeling |
| semantically invalid hybrid | pre-execution applicability rather than inference from command failure |
| no-op or already-resolved task | justified no-change outcome versus unnecessary implementation or test edits |
| nondeterministic/environment-drift case | repeated execution, aggregation rule, and uncertainty policy |

These identifiers must not enter `SUPPORTED_FAMILIES` until they have exact generation rules, controls, deterministic labels, red-first integration tests, and a reviewed ambiguity boundary.

## Observer boundary

`O0_EXIT_CODE` preserves only configured process classes. A nonzero command classified as failure receives `test_failure_untyped`, even when the underlying mechanism is an execution error.

`O1_TYPED_RECEIPT` distinguishes assertion failure from generic test error and other receipt outcomes. Receipt v1 does not provide a complete failure-cause taxonomy or authenticate the producer.

The observer arm is part of the descriptor digest. Typed failure causes cannot be retrofitted onto an exit-code fixture, and changing observer fields without changing derived state/method semantics is rejected.

## Schema compatibility boundary

The fixture descriptor, identity, and binding schemas remain structurally versioned as v1 during development. Adding the wrong-reason family expands their pre-freeze family and failure-cause enums while preserving validity and digest meaning for existing artifacts.

Consequences:

- existing v1 artifacts remain valid and unchanged;
- an older verifier may reject a new-family artifact;
- exact verifier and generator commits must be retained;
- the frozen protocol must pin immutable schema bytes and implementation versions;
- no held-out material may be generated while the schemas remain mutable.

## Population boundary

The fixtures are controlled mechanism probes. They do not estimate:

- mechanism prevalence in real coding-agent patches;
- language, framework, patch-size, or dependency distributions;
- invalid-hybrid frequency;
- operational cost;
- observer accuracy on a held-out population;
- method effectiveness or superiority.

Development execution may test plumbing, applicability, timing, and analysis code. Inspected development cases cannot later become confirmatory holdout cases.

## Falsification and redesign

Narrow or redesign the taxonomy if:

- two families encode the same mechanism and control contrast;
- labels depend on observed DeltaWitness output rather than pre-execution semantics;
- harmless representation changes alter the family without changing its mechanism;
- the control does not isolate the intended evidence increment;
- expected labels become free-form values that cannot be recomputed;
- external reviewers cannot infer the boundary from the descriptor and fixed bytes.

## Claim boundary

This taxonomy establishes only a pre-freeze vocabulary and four deterministic owned-synthetic mechanism probes. The paired wrong-reason case shows one controlled observer-dependent decision difference. It does not establish completeness, representativeness, prevalence, empirical effectiveness, general superiority of typed receipts, scientific novelty, protocol freeze, independent reproduction, or authorization for pilot or held-out execution.
