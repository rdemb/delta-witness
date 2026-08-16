# DW-001 Scenario Taxonomy v1

**Status:** development-pilot design contract; not frozen; no pilot or held-out execution authorized.

This taxonomy defines the mechanism and control labels used by the first deterministic owned-synthetic DW-001 fixture generator. A family identifier is not a narrative tag: its expected four-state observations and nested-method decisions are recomputed by the fixture-descriptor verifier.

The current generator intentionally implements only three families. The remaining issue #2 families stay visible as required future work rather than being silently treated as covered.

## Taxonomy invariants

Every scenario family must define:

- one falsifiable false-assurance mechanism or control purpose;
- whether it is a valid-patch control or a false-assurance case;
- state applicability before execution;
- expected `BB`, `BC`, `CB`, and `CC` semantic outcomes;
- expected `M0_FINAL`, `M1_F2P`, `M2_F2P_P2P`, and `M3_FOUR_STATE` decisions;
- observer requirements and the failure-cause boundary;
- at least one contrast or counterexample that would invalidate the family label.

Stored method decisions are not authoritative. They are derived from state semantics using the DW-001 predicate contract.

## Implemented deterministic subset

| Family ID | Role | Expected states `BB / BC / CB / CC` | Expected methods `M0 / M1 / M2 / M3` | Evidence increment isolated |
|---|---|---|---|---|
| `valid-discriminating-regression` | valid-patch control | `pass / fail / pass / pass` | `accept / accept / accept / accept` | control showing that every nested method can accept a valid discriminating repair |
| `non-discriminating-candidate-test` | false-assurance case | `pass / pass / pass / pass` | `accept / reject / reject / reject` | incremental value of `BC` beyond final-state execution |
| `candidate-regression-against-base-tests` | false-assurance case | `pass / fail / fail / pass` | `accept / accept / reject / reject` | incremental value of `CB` beyond fail-to-pass validation |

### `valid-discriminating-regression`

Mechanism:

- the base implementation accepts any non-empty role;
- the candidate implementation accepts only `admin`;
- the candidate test adds a viewer-denial assertion;
- original tests remain satisfied.

This is a positive control, not evidence that all real valid patches have this shape.

Falsification boundary:

- `BC` does not produce a semantic assertion failure;
- `CB` does not pass;
- any required state is indeterminate;
- a weaker method rejects because it consumed an undeclared hidden state.

### `non-discriminating-candidate-test`

Mechanism:

- the candidate implementation repairs the role check;
- the added candidate test exercises another administrator example that already passes on the base;
- final-state execution remains green without demonstrating candidate-test discrimination.

The family tests only the missing `BC` discrimination signal. It does not claim the patch itself is incorrect.

Falsification boundary:

- the candidate test fails on the base;
- the family depends on an execution error rather than a semantic pass;
- `M0` rejects or `M1` accepts under the frozen predicate.

### `candidate-regression-against-base-tests`

Mechanism:

- candidate tests check administrator and viewer behavior;
- the candidate implementation satisfies those tests;
- an original missing-role denial test is absent from the candidate test world;
- the candidate implementation regresses that original behavior.

The family isolates regression preservation through `CB`. It is not a general oracle-strength benchmark.

Falsification boundary:

- `CB` passes;
- `BC` does not fail for the declared regression witness;
- the final candidate does not pass its candidate tests;
- `M1` rejects or `M2` accepts under the frozen predicate.

## Required but not yet generated

The following families remain required by issue #2, but are not supported by generator v1:

| Planned family | Required distinction before implementation |
|---|---|
| assertion or test weakening | distinguish a materially weakened oracle from a behavior-preserving test refactor |
| wrong-reason base failure | pair a genuine assertion exposure with an import, setup, dependency, or unrelated assertion failure using the same ordinary exit code |
| collection/import/setup failure | preserve typed execution error as `indeterminate`, never as the intended semantic `fail` |
| semantically invalid hybrid | declare applicability from independently reviewed ground truth rather than inferring it from command failure |
| no-op or already-resolved task | distinguish a justified no-change outcome from unnecessary implementation or test edits |

These identifiers must not be added to `SUPPORTED_FAMILIES` until they have:

- exact synthetic bytes or another auditable generator rule;
- positive and negative controls;
- typed expected failure causes;
- deterministic state and method labels;
- red-first integration tests;
- a reviewed ambiguity boundary.

## Observer boundary

The same structural family may be instantiated under either:

- `O0_EXIT_CODE`, where an ordinary semantic failure is recorded as `test_failure_untyped`;
- `O1_TYPED_RECEIPT`, where a cooperating adapter can record `assertion_failure` distinctly from import, collection, setup, timeout, and producer errors.

The observer arm is part of the descriptor digest. A typed failure cause must not be retrofitted onto an exit-code-only fixture.

## Population boundary

The implemented fixtures are controlled mechanism probes. They are not an estimate of:

- the prevalence of false-assurance mechanisms in real coding-agent patches;
- the distribution of languages, frameworks, patch sizes, or dependency graphs;
- real-world invalid-hybrid frequency;
- expected operational cost;
- method effectiveness on a held-out population.

A development pilot may use them to test plumbing, applicability logic, timing boundaries, and analysis code. They cannot become confirmatory held-out cases after their outcomes have been inspected.

## Falsification and redesign

Narrow or redesign the taxonomy if:

- two families produce the same mechanism and control contrast;
- a label depends on observed DeltaWitness output rather than pre-execution semantics;
- harmless representation changes alter the family label without changing the mechanism;
- the implemented control cannot distinguish the intended evidence increment;
- the family requires free-form expected method labels that cannot be recomputed;
- external reviewers cannot agree on the mechanism boundary from the descriptor and synthetic bytes.

## Claim boundary

This taxonomy establishes only a versioned vocabulary and three deterministic owned-synthetic mechanism probes for development-pilot preparation. It does not establish completeness, representativeness, realism, empirical effectiveness, scientific novelty, protocol freeze, independent reproduction, or authorization for held-out execution.
