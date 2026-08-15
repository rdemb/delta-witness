# DW-001 Baseline Specification

**Status:** draft baseline contract; not preregistered; not frozen.

**Repository anchor:** `a29eb1476bec42bfcbfe6758f05bb70667b056c7`.

This document defines the baseline dimensions that must be fixed before DW-001 evaluates any held-out scenario. It prevents the study from comparing a weak caricature of existing practice with the complete DeltaWitness stack.

## 1. Unit of evaluation

The primary unit is one independently labeled patch scenario containing:

- an immutable base implementation-side Git tree;
- an immutable candidate implementation-side Git tree;
- an immutable base test-side Git tree;
- an immutable candidate test-side Git tree;
- one or more declared claims;
- a frozen command, timeout, observer, and expected semantic signature;
- an applicability and ground-truth label defined without inspecting method output.

A scenario may produce multiple command observations, but it contributes one paired method decision per frozen aggregation rule.

## 2. Canonical state names

| State | Implementation side | Test side |
|---|---|---|
| `BB` | base | base |
| `BC` | base | candidate |
| `CB` | candidate | base |
| `CC` | candidate | candidate |

The expected supported four-state witness for a discriminating regression repair is:

```text
BB = pass
BC = fail
CB = pass
CC = pass
```

A process nonzero status is not automatically a semantic `fail`. The observer contract determines whether the observation is `pass`, `fail`, or `indeterminate`.

## 3. Controlled state-set methods

All primary methods must use the same Git materializer, claim configuration, command construction, timeout, environment sanitizer, and observer implementation. The only intended difference is which state observations are available to the method predicate.

### `M0_FINAL`

Evidence:

```text
CC
```

Acceptance predicate:

```text
CC == pass
```

Interpretation: conventional green final-state execution. It does not ask whether the candidate test exposed old behavior or whether original tests remain satisfied.

### `M1_F2P`

Evidence:

```text
BC, CC
```

Acceptance predicate:

```text
BC == fail and CC == pass
```

Interpretation: canonical two-state fail-to-pass validation of the candidate witness.

### `M2_F2P_P2P`

Evidence:

```text
BC, CB, CC
```

Acceptance predicate:

```text
BC == fail and CB == pass and CC == pass
```

Interpretation: fail-to-pass validation plus preservation of the original test world on the candidate implementation. This is the strongest controlled three-state baseline and is the primary comparator for the incremental value of `BB`.

This is conceptually related to benchmark grading that separates `FAIL_TO_PASS` from `PASS_TO_PASS`, but it is not identical to every benchmark harness. SWE-bench groups named tests within its evaluation harness; DeltaWitness materializes separate base and candidate test-side Git trees. The difference must remain explicit.

### `M3_FOUR_STATE`

Evidence:

```text
BB, BC, CB, CC
```

Acceptance predicate:

```text
BB == pass and BC == fail and CB == pass and CC == pass
```

Interpretation: complete four-state witness with an independently checked base/base endpoint.

## 4. Primary incremental contrasts

| Contrast | Added evidence | Primary interpretation |
|---|---|---|
| `M1 - M0` | `BC` | candidate-test discrimination against the base implementation |
| `M2 - M1` | `CB` | preservation of the original test world by the candidate implementation |
| `M3 - M2` | `BB` | validity of the base/base endpoint and full matrix consistency |

The contrasts are paired differences in method decisions on the same scenarios. They do not establish universal causal effects.

## 5. Observation modes

Every controlled state-set method must be evaluated under both observation modes when the scenario supports both.

### `O0_EXIT_CODE`

- configured, disjoint pass and fail exit-code sets;
- timeout and unknown return codes are indeterminate;
- no structured distinction between assertion failure and test-runner error beyond the configured process status.

### `O1_TYPED_RECEIPT`

- invocation-bound `outcome-receipt-v1` receipt;
- explicit framework outcome classes;
- receipt/process-exit consistency check;
- malformed, missing, stale, mismatched, oversized, or internally inconsistent evidence is indeterminate.

Primary observer contrast:

```text
O1_TYPED_RECEIPT - O0_EXIT_CODE
```

This contrast measures typed-outcome evidence. It must not be attributed to the number of matrix states.

## 6. Factorial method identifiers

Each primary result row must use an explicit combined identifier:

```text
M0_FINAL__O0_EXIT_CODE
M0_FINAL__O1_TYPED_RECEIPT
M1_F2P__O0_EXIT_CODE
M1_F2P__O1_TYPED_RECEIPT
M2_F2P_P2P__O0_EXIT_CODE
M2_F2P_P2P__O1_TYPED_RECEIPT
M3_FOUR_STATE__O0_EXIT_CODE
M3_FOUR_STATE__O1_TYPED_RECEIPT
```

Unsupported combinations must be labeled `not_applicable`; they must not be silently omitted.

## 7. Decision-equivalence and cost executions

One execution design cannot simultaneously maximize observation equivalence and measure method-specific cost without qualification.

### 7.1 Decision-equivalence projection

For detection comparisons, execute the complete state set once with a fixed observer and project the nested method decisions from the same immutable observations. This removes run-to-run drift from the state-set contrast.

Requirements:

- all projected methods consume byte-identical observations for shared states;
- projection code is deterministic and independently tested;
- a method cannot inspect states outside its declared evidence set;
- projection output records the source report digest and allowed state set.

### 7.2 Independent cost execution

For operational cost, execute each method using only its required states.

Requirements:

- randomized or counterbalanced method order;
- warm-cache and cold-cache policy fixed before measurement;
- setup, checkout, command, verification, and review time reported separately where measurable;
- state count, command count, wall time, CPU time, and peak resource use retained;
- retries and stochastic repetitions governed by one frozen policy.

Detection estimates must use the equivalence projection unless a preregistered reason requires independent executions. Cost estimates must not be taken from the projected full run and presented as method-specific runtime.

## 8. Direct reference baselines

### 8.1 SWE-bench grading

Reference artifacts:

- paper: https://arxiv.org/abs/2310.06770
- reviewed implementation: https://github.com/SWE-bench/SWE-bench/blob/128cbd1a5759694874e6bd56624cb2fd6fb079e2/swebench/harness/grading.py

Relevant dimensions:

- separate `FAIL_TO_PASS` and `PASS_TO_PASS` groups;
- full resolution requires both resolution and maintenance criteria;
- current reviewed code rejects several missing-run, infrastructure, and log/exit inconsistency cases.

Baseline role:

- direct semantic reference for issue-resolution plus regression preservation;
- not an exact substitute for Git-native separate test worlds;
- any claimed incremental value of `BB` must be measured against `M2`, not only against final-state CI.

### 8.2 TDD-Bench Verified

Reference artifacts:

- paper: https://arxiv.org/abs/2412.02883
- official implementation: https://github.com/IBM/TDD-Bench-Verified

Relevant dimensions:

- generated tests are expected to fail before the reference repair and pass after it;
- coverage adequacy is evaluated separately from fail-to-pass behavior;
- human and execution filtering are part of benchmark construction.

Baseline role:

- direct reference for candidate-test discrimination;
- coverage adequacy is an oracle-quality dimension, not evidence supplied by the current DeltaWitness core;
- the first DW-001 study must not imply that typed outcomes substitute for coverage or semantic adequacy.

## 9. Adjacent patch-assessment methods

| Method family | Representative source | Relation to DW-001 | Initial executable-baseline decision |
|---|---|---|---|
| Delta debugging | https://doi.org/10.1109/32.988498 | isolates failure-inducing inputs or changes | exclude from H0 primary comparison; retain for later H2 influence study |
| Causal/change localization | https://doi.org/10.1145/1062455.1062522 | searches change combinations linked to failures | exclude from H0 primary; evaluate under patch-influence study |
| PATCH-SIM | https://arxiv.org/abs/1706.09120 | compares execution behavior across buggy and patched programs | candidate secondary baseline if artifact/language fit is feasible |
| DiffTGen | https://doi.org/10.1145/3092703.3092718 | generates tests that expose patch/reference semantic differences | candidate secondary baseline; requires reference patch and Java-oriented tooling |
| Opad | https://doi.org/10.1145/3106237.3106274 | uses generated tests with crash and memory-safety oracles | candidate secondary baseline for compatible native-code scenarios |
| RGT patch assessment | https://arxiv.org/abs/1909.13694 | generates tests from a human reference patch | candidate secondary baseline; requires trusted reference patches |
| Invalidator | https://arxiv.org/abs/2301.01113 | combines invariant and syntactic patch assessment | adjacent correctness classifier, not a state-set baseline |
| ChangeGuard | https://doi.org/10.1145/3715760 | compares behavior for intended behavior-preserving changes | candidate secondary baseline for preservation scenarios |
| P³ | https://doi.org/10.1145/3763145 | constructs product programs for relational patch specifications | adjacent relational-analysis baseline; currently C- and specification-oriented |
| RETRACE | https://arxiv.org/abs/2608.08950 | checks semantic alignment between patch and reported problem | complementary semantic verifier, not a test-state baseline |

The final protocol must record artifact availability, language compatibility, safety constraints, setup cost, and exclusion rationale. “Different method” is not a sufficient exclusion reason.

## 10. Method decision outputs

Every method/scenario result must be one of:

- `accept`;
- `reject`;
- `indeterminate`;
- `not_applicable`.

For each result retain:

- method and observer identifier;
- allowed state set;
- exact input state identities;
- per-state semantic outcome;
- decision predicate version;
- missing or contradictory evidence reason;
- source observation/report digest;
- execution and review cost fields.

Binary post-processing may be derived for a named analysis, but the four-way primary record must remain available.

## 11. Minimum baseline QA

Before held-out execution:

- [ ] every acceptance predicate has truth-table tests;
- [ ] projection code cannot access undeclared states;
- [ ] exit-code and typed-receipt arms use the same state inputs;
- [ ] `indeterminate` is never converted into a semantic fail;
- [ ] `not_applicable` is retained in denominators and flow counts;
- [ ] a false-assurance scenario is detected by the expected incremental contrast;
- [ ] a valid patch is not rejected solely because a method received hidden evidence;
- [ ] cost runs execute only the states declared by the method;
- [ ] baseline versions and source identities are frozen;
- [ ] exclusions and deviations are machine-readable.

## 12. Claim boundary

This specification defines a fairer comparison contract. It does not show that the four-state method adds value, that typed receipts improve accuracy, that the selected adjacent methods are sufficient, or that any result will generalize beyond the frozen scenario population.
