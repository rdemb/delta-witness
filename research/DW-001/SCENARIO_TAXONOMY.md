# DW-001 Scenario Taxonomy v1

**Status:** development-pilot design contract; not frozen; no held-out execution authorized.

This taxonomy defines mechanism and control labels for deterministic owned-synthetic DW-001 fixtures. A family identifier is not a narrative tag: expected four-state observations, failure-cause declarations, and nested-method decisions are recomputed by the fixture verifier.

The current generator implements six controlled families. The committed ten-arm development mechanism pilot retains the five-family population that was sealed before `weak-proxy-oracle` existed; this later family is a separate development-only Gate 1 negative control. Remaining issue #2 mechanisms stay explicit rather than being silently treated as covered. The schemas remain pre-freeze, so every result must pin the exact implementation commit because older v1 verifiers do not understand families added later during development.

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

A family may expose a limitation of a later evidence layer even when the four-state matrix behaves canonically. Such a result must not be relabeled as a matrix failure.

## Implemented deterministic subset

| Family ID | Role | Observer | Expected states `BB / BC / CB / CC` | Expected methods `M0 / M1 / M2 / M3` | Isolated contrast |
|---|---|---|---|---|---|
| `valid-discriminating-regression` | valid-patch control | `O0` or `O1` | `pass / fail / pass / pass` | `accept / accept / accept / accept` | positive control for a valid discriminating repair |
| `non-discriminating-candidate-test` | false-assurance case | `O0` or `O1` | `pass / pass / pass / pass` | `accept / reject / reject / reject` | incremental value of `BC` beyond final-state execution |
| `candidate-regression-against-base-tests` | false-assurance case | `O0` or `O1` | `pass / fail / fail / pass` | `accept / accept / reject / reject` | incremental value of `CB` beyond fail-to-pass validation |
| `wrong-reason-base-import-failure` | false-assurance case | `O0` | `pass / fail / pass / pass` | `accept / accept / accept / accept` | exit-code-only false assurance from a pre-assertion import error |
| `wrong-reason-base-import-failure` | false-assurance case | `O1` | `pass / error / pass / pass` | `accept / indeterminate / indeterminate / indeterminate` | typed preservation of error rather than semantic failure |
| `wrong-reason-unrelated-assertion` | false-assurance case | `O0` | `pass / fail / pass / pass` | `accept / accept / accept / accept` | untyped assertion-channel evidence does not establish claim relevance |
| `wrong-reason-unrelated-assertion` | false-assurance case | `O1` | `pass / fail / pass / pass` | `accept / accept / accept / accept` | a genuine typed assertion failure can still be unrelated to the claim |
| `weak-proxy-oracle` | false-assurance case | `O0` | `pass / fail / pass / pass` | `accept / accept / accept / accept` | a localized fail-to-pass selector can assert only a proxy property |
| `weak-proxy-oracle` | false-assurance case | `O1` | `pass / fail / pass / pass` | `accept / accept / accept / accept` | a typed localized selector can still admit a fixed claim-violating mutant |

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
- candidate tests import both symbols before the intended assertions execute;
- under `base implementation + candidate tests`, import fails before the intended assertions execute;
- base tests pass under both implementation worlds;
- candidate tests pass under the candidate implementation.

The same scenario identifier and source/test bytes are used for both observer arms. Only observer-derived descriptor fields differ: observer, observer ID, command, expected states, expected methods, specification, and resulting identities.

#### Exit-code arm

```text
BB = pass
BC = fail / test_failure_untyped
CB = pass
CC = pass
```

The resulting canonical-looking matrix is complete and all four nested methods accept.

#### Typed-receipt arm

```text
BB = pass
BC = error / predeclared import_error
CB = pass
CC = pass
```

The built-in unittest adapter records zero assertion failures and at least one test error. Methods requiring `BC` become indeterminate.

Receipt v1 reports the runtime class `test_error`. It does not claim to distinguish import, collection, setup, dependency, or infrastructure subtypes. `import_error` is independently fixed ground truth for the exact owned-synthetic bytes.

Falsification boundary:

- the exit-code arm does not produce the canonical-looking matrix;
- the typed arm records assertion failure or complete semantic `fail`;
- source/test bytes or scenario identity differ between arms;
- method differences arise from different state sets rather than observer semantics;
- the missing-symbol import is itself the intended oracle;
- harmless environment variation changes the declared mechanism.

This pair isolates one failure/error distinction. It does not estimate prevalence in real patches.

### `wrong-reason-unrelated-assertion`

Fixed mechanism:

- base `is_admin` remains buggy and candidate `is_admin` repairs viewer behavior;
- base `version_label()` returns `v1` and candidate `version_label()` returns `v2` as a collateral change;
- the claim-facing viewer test executes `is_admin({"role": "viewer"})` but asserts only that the result is a Boolean;
- that claim-facing assertion passes on base and candidate;
- a separate assertion requires `version_label() == "v2"`;
- the collateral assertion is the sole source of `BC = fail`;
- removing that assertion makes `BC` pass.

The same scenario identifier and byte-identical source/test mechanism are used under both observer arms.

#### Exit-code arm

```text
BB = pass
BC = fail / test_failure_untyped
CB = pass
CC = pass
```

#### Typed-receipt arm

```text
BB = pass
BC = fail / assertion_failure
CB = pass
CC = pass
```

All nested methods accept under both arms. Declared-selector localization later classifies the claim-facing selector as `non_discriminating` and keeps the collateral selector separate.

This is a negative control for oracle relevance:

```text
real assertion failure
    + typed outcome
    + canonical four-state witness
    != claim-oracle relevance
```

Falsification boundary:

- the claim-facing assertion fails on base;
- the collateral assertion is not the sole `BC` failure source;
- either observer records `error` or `timeout`;
- source/test bytes or scenario identity differ between arms;
- any nested method rejects or becomes indeterminate;
- the collateral behavior is materially part of the declared authorization claim;
- the mechanism requires post-result free-form intent.

The family does not define an oracle-relevance detector. It motivates a separate declared-selector relation.

### `weak-proxy-oracle`

Fixed task prompt:

```text
Fix is_admin so only the admin role is authorized and add a regression test proving that a viewer is denied.
```

Fixed mechanism:

- base `is_admin` returns the raw role value;
- candidate `is_admin` returns whether the role equals `admin`;
- the declared viewer test asserts only that the returned value is a Boolean;
- the declared selector therefore fails on base and passes on candidate;
- the complete four-state matrix is canonical under both observers;
- typed `BC` is a genuine assertion failure;
- declared-selector localization is `supported` and `discriminating`;
- a fixed mutant `return bool(user.get("role"))` also passes the declared selector while authorizing a viewer;
- a separately fixed hidden development claim check passes on candidate and fails on the mutant.

Expected current evidence:

```text
BB / BC / CB / CC = pass / fail / pass / pass
M0 / M1 / M2 / M3 = accept / accept / accept / accept
localization       = supported / discriminating
```

Expected mutation controls:

```text
base      + declared selector = fail
candidate + declared selector = pass
mutant    + declared selector = pass
candidate + hidden claim      = pass
mutant    + hidden claim      = fail
```

This is a negative control for oracle strength:

```text
typed assertion failure
    + canonical four-state witness
    + exact declared-selector fail-to-pass localization
    != sufficient oracle strength
```

Falsification boundary:

- the declared selector is not a real assertion failure on base;
- it does not pass on candidate;
- current localization does not classify it as discriminating;
- any current nested method rejects or becomes indeterminate;
- the fixed mutant fails the declared selector;
- the hidden claim check passes on the mutant;
- candidate or mutant bytes contain additional confounding changes;
- the hidden check merely restates the proxy property;
- repeated clean execution changes stable challenge semantics.

The family and challenge do not define a mutation score, prove that the hidden check is complete, or estimate real-agent behavior.

Complete challenge boundary:

```text
research/DW-001/WEAK_ORACLE_CHALLENGE.md
research/DW-001/schema/weak-oracle-challenge.schema.json
src/deltawitness/dw001_oracle_challenge.py
```

## Required but not yet generated

| Planned family | Required distinction before implementation |
|---|---|
| assertion or test weakening | materially weakened oracle versus behavior-preserving test refactor |
| broader collection/setup/dependency/infrastructure error | runtime subtype evidence or independently reviewed ground truth without post-result relabeling |
| semantically invalid hybrid | pre-execution applicability rather than inference from command failure |
| no-op or already-resolved task | justified no-change outcome versus unnecessary implementation or test edits |
| nondeterministic/environment-drift case | repeated execution, aggregation rule, and uncertainty policy |
| over-mocked claim boundary | necessary isolation versus mocks that replace the behavior under test |

These identifiers must not enter `SUPPORTED_FAMILIES` until they have exact generation rules, controls, deterministic labels, red-first integration tests, and a reviewed ambiguity boundary.

## Observer boundary

`O0_EXIT_CODE` preserves only configured process classes. A nonzero command classified as failure receives `test_failure_untyped`, even when the underlying mechanism is execution error.

`O1_TYPED_RECEIPT` distinguishes assertion failure from generic test error and other receipt outcomes. Receipt v1 does not provide a complete failure-cause taxonomy, establish assertion relevance or strength, or authenticate the producer.

The observer arm is part of the descriptor digest. Typed failure causes cannot be retrofitted onto an exit-code fixture, and changing observer fields without changing derived state/method semantics is rejected.

## Oracle-relevance and oracle-strength boundaries

A typed `test_failure` establishes only that the cooperating adapter observed assertion failure under its aggregation rules. Declared-selector localization additionally establishes which predeclared logical test produced the recorded `BC`/`CC` transition. Neither establishes:

- that the declared selector encodes the intended behavior;
- that the assertion rejects plausible incorrect implementations;
- that the oracle is complete or mutation-adequate;
- that mocks, skips, fixtures, selection, or environment effects preserve meaning;
- that a hidden or independent oracle would agree.

The unrelated-assertion family is a negative control for suite-level failure provenance. The weak-proxy family is a negative control for assertion strength after selector provenance has been resolved.

Absence of either warning signal must not be interpreted as oracle adequacy.

## Schema compatibility boundary

The fixture descriptor, identity, and binding schemas remain structurally versioned as v1 during development. Adding controlled families expands their pre-freeze family and failure-cause enums while preserving validity and digest meaning for existing artifacts.

Consequences:

- existing v1 artifacts remain valid and unchanged;
- an older verifier may reject a new-family artifact;
- exact verifier and generator commits must be retained;
- the frozen protocol must pin immutable schema bytes and implementation versions;
- no held-out material may be generated while schemas remain mutable.

The historical ten-arm development-pilot plan and archive remain fixed to their original five-family population and are not silently rewritten to include later controls.

## Population boundary

The fixtures are controlled mechanism probes. They do not estimate:

- mechanism prevalence in real coding-agent patches;
- language, framework, patch-size, or dependency distributions;
- operational cost on ecological repositories;
- observer, localization, or mutation-analysis accuracy on a held-out population;
- method effectiveness, superiority, or deployment value.

Development execution may test plumbing and falsify over-broad interpretations. Inspected development cases cannot later become confirmatory holdout cases.

## Falsification and redesign

Narrow or redesign the taxonomy if:

- two families encode the same mechanism and control contrast;
- labels depend on observed DeltaWitness output rather than pre-execution semantics;
- harmless representation changes alter the family without changing its mechanism;
- the control does not isolate the intended evidence increment or limitation;
- expected labels become free-form values that cannot be recomputed;
- external reviewers cannot infer the boundary from fixed bytes and declared relations.

## Claim boundary

This taxonomy establishes only a pre-freeze vocabulary and six deterministic owned-synthetic mechanism probes. The import-error pair isolates one observer-dependent difference. The unrelated-assertion pair shows that typed suite failure does not establish claim relevance. The weak-proxy challenge shows one case where exact declared-selector fail-to-pass evidence still does not reject one fixed claim-violating mutant.

It does not establish completeness, representativeness, prevalence, empirical effectiveness, general superiority of typed receipts, a validated oracle-relevance or oracle-strength method, mutation adequacy, scientific novelty, protocol freeze, independent reproduction, or authorization for held-out execution.