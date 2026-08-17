# DW-001 Selector-Context Interaction Witness Lattice Plan v1

## Status

This document records a **design-only preregistration** for issue #47. The source bytes, test bytes, truth table, selectors, profiles, path hypotheses, mutation operators, generation controls, expected mutant incidence table, integrity rules, safety boundary, and claim boundary are frozen before the new source, selectors, Coverage.py measurements, or mutant outcomes are executed or inspected.

The current implementation may parse, transform, unparse, reparse, and compile fixed project-owned bytes to derive identities. It does **not** execute the candidate, tests, Coverage.py, or mutants.

```text
execution_status                  = not_implemented
execution_authorized              = false
holdout_selected                  = false
primary_denominator_eligible      = false
quality_score                     = null
headline_score                    = null
universal_threshold               = null
merge_blocker_authorized          = false
mcdc_certification_claim_allowed  = false
scientific_novelty_claim_allowed  = false
```

A later result implementation must begin from a merged commit containing this preregistration. It may not rewrite this design after outcomes are visible.

## 1. Motivation

PR #46 established one exact owned-synthetic direct-baseline result:

```text
profile-level stdlib statement signatures equal
profile-level Coverage.py statement signatures equal
profile-level Coverage.py target-arc signatures equal
frozen generic mutation outcomes different
```

That result retains exact selector contexts, but its primary profile comparison reduces each profile to statement and arc unions/intersections. Such set aggregation can discard **which execution path shapes occurred together in individual logical tests**.

The present experiment tests that information-loss hypothesis directly in one fixed two-condition authorization control. It does not modify the PR #46 source, selectors, observations, or digests.

## 2. Research question

> For one preregistered two-condition owned-synthetic authorization function, can an exact selector-context path partition preserve condition-interaction evidence that is lost by profile-level statement and arc union/intersection, and does that retained partition relation agree with a separately frozen asymmetric mutant-outcome table?

This is a falsifiable question about one exact control. It is not a general coverage, MC/DC, oracle-strength, mutation-adequacy, coding-agent, or ecological claim.

## 3. Frozen upstream evidence

```text
PR #46 merge commit:
  1e7f1c627d23bb54df0753ef7e3452a746c2f520

Coverage.py result semantic SHA-256:
  ec0c2fdd5ac24ba53eb895d9014aab623d2631125b8512ba0e0cbf5105f21ee8

Coverage.py result report SHA-256:
  8b248757374ebff4195bad181ad02bc5b0bfc61fa2e21ebf45549686c33d2c41

Frozen mutation-result semantic SHA-256:
  9e101bca85fd630bf5bdb2a6030d9fdab93eb3eac54b03f4aab99012c28086b6

Frozen stdlib statement-result semantic SHA-256:
  353e887ccb43561f1a0749e7948dd40bd7019534e93b5dca5b11ea16d49f68c6

Coverage.py distribution-manifest SHA-256:
  28f6430e45fcfda973a1fcd57157e2317f096cc2774e8281244eaf18a9d0dd3f
```

The new source and selectors are distinct from the PR #46 case. The prior result is referenced but not modified.

## 4. Prior-art boundary

Established direct or conceptual baselines include:

- Coverage.py `7.15.2` statement, arc, branch-statistic, and measurement-context APIs;
- path and structural coverage;
- modified condition/decision coverage;
- combinatorial input/configuration coverage;
- checked coverage and dynamic slicing to an oracle;
- mutation testing, selective mutation, and equivalent-mutant analysis;
- the general test-oracle problem.

The exact reviewed sources, their relevance, and their non-claims are frozen in:

```text
research/DW-001/interaction-witness-prior-art-log.v1.json
```

```text
prior_art_log_sha256:
  af6cb9782ea01a0e58baed8cfc1a4895dc1a53ed934498b307c6b05e8634c44f

novelty_status:
  not_established

systematic_review_complete:
  false
```

No novelty is claimed for contexts, path coverage, MC/DC, combinatorial coverage, checked coverage, mutation testing, truth-table analysis, or integrity digests.

The narrower planned difference is an integrity-bound comparison among:

1. profile statement union/intersection;
2. profile executed-arc union/intersection;
3. an order-independent multiset of exact per-selector statement-and-arc path shapes, with selector/context/binding identities retained separately;
4. fixed truth-table condition-independence witnesses;
5. a complete typed incidence table for predeclared claim-violating mutants.

If a simpler baseline captures the same complete relation with less complexity, the design should be narrowed or replaced.

## 5. Frozen source and target

The candidate source is fixed conceptually as:

```python
def is_authorized(user):
    role_ok = user.get("role") == "admin"
    mfa_ok = user.get("mfa") is True
    if role_ok:
        role_gate = True
    else:
        role_gate = False
    if mfa_ok:
        mfa_gate = True
    else:
        mfa_gate = False
    return role_gate and mfa_gate
```

The public plan records identities rather than the source body:

```text
source_id:
  two-condition-authorization-candidate-v1

source_path:
  src/access.py

source_symbol:
  is_authorized

source_sha256:
  c0e8af980cdc0d304af77ec85222e36cf1d8a3b88bd1e18b0277699a086c0a7b

semantic_ast_sha256:
  67d1540a8c3b88e24ae8f3ea39ab27df2f8ef738545a709004394207636b83a3

source_line_count:
  12
```

The exact mutation target is the final two-operand `and` expression:

```text
target_id:
  6b20aa0ad5180288edffc9644e85252a774c2efb0c8ee9a32852b0d0ca50728e

node_kind:
  Return.value/BoolOp.And

source_position:
  line 12, columns 11–33

operands:
  [role_gate, mfa_gate]

coverage_target_lines:
  [2, 3, 4, 5, 7, 8, 9, 11, 12]
```

The explicit control-flow decisions exist so every profile can have the same aggregate statement and arc sets while individual selectors retain different path combinations.

## 6. Frozen test identity and truth table

```text
test_id:
  two-condition-authorization-selectors-v1

test_path:
  tests/test_access.py

test_sha256:
  02d1069245ae05a76a128aada50affbbe04c83f40f06ce7f4e7f8dde5cdd4bdc

selector_count:
  4
```

| Quadrant | `role_ok` | `mfa_ok` | Expected decision | Exact selector |
|---|---:|---:|---:|---|
| `TT` | true | true | allow | `test_access.AccessTests.test_admin_with_mfa_is_allowed` |
| `TF` | true | false | deny | `test_access.AccessTests.test_admin_without_mfa_is_denied` |
| `FT` | false | true | deny | `test_access.AccessTests.test_viewer_with_mfa_is_denied` |
| `FF` | false | false | deny | `test_access.AccessTests.test_viewer_without_mfa_is_denied` |

Each truth-table entry has a digest-bound selector identity covering the test digest, quadrant, input, selector, and expected decision.

A later runner must execute each exact candidate selector through `outcome-receipt-v1` as exactly one logical unittest. Candidate selector pass is preregistered but not yet observed.

## 7. Frozen selector profiles

| Order | Profile | Quadrants | Role |
|---:|---|---|---|
| 1 | `diagonal-only-v1` | `TT`, `FF` | diagonal negative control |
| 2 | `mfa-independence-v1` | `TT`, `TF`, `FF` | one-condition independence control |
| 3 | `role-independence-v1` | `TT`, `FT`, `FF` | one-condition independence control |
| 4 | `mcdc-basis-v1` | `TT`, `TF`, `FT` | two-condition independence control |
| 5 | `full-truth-table-v1` | `TT`, `TF`, `FT`, `FF` | full truth-table control |

Profile names describe frozen input relations. They do not rank test quality.

The three-selector profiles have equal cardinality. This controls against the trivial explanation that a different path-partition digest reflects only a different number of selectors.

`mcdc-basis-v1` is one fixed direct control for a two-condition conjunction. It is not a general MC/DC implementation or certification claim.

## 8. Frozen per-quadrant structural hypotheses

### `TT`

```text
executed statements:
  [2, 3, 4, 5, 8, 9, 12]

missing statements:
  [1, 7, 11]

executed arcs:
  [[-1, 2], [2, 3], [3, 4], [4, 5],
   [5, 8], [8, 9], [9, 12], [12, -1]]

path_shape_sha256:
  1d96c8895c09bf56a9617e7927e31a9eccaf5cdc9c67f24880fc77abd0255361
```

### `TF`

```text
executed statements:
  [2, 3, 4, 5, 8, 11, 12]

missing statements:
  [1, 7, 9]

executed arcs:
  [[-1, 2], [2, 3], [3, 4], [4, 5],
   [5, 8], [8, 11], [11, 12], [12, -1]]

path_shape_sha256:
  46ab1e2b779a82855ec5188f0b2980d78d4b1506b5b5d37a2c4ea45922c78236
```

### `FT`

```text
executed statements:
  [2, 3, 4, 7, 8, 9, 12]

missing statements:
  [1, 5, 11]

executed arcs:
  [[-1, 2], [2, 3], [3, 4], [4, 7],
   [7, 8], [8, 9], [9, 12], [12, -1]]

path_shape_sha256:
  9f7fe46e5b626c9922262f8768090479c8ed0a9babcaf337db2d56eb240cbf48
```

### `FF`

```text
executed statements:
  [2, 3, 4, 7, 8, 11, 12]

missing statements:
  [1, 5, 9]

executed arcs:
  [[-1, 2], [2, 3], [3, 4], [4, 7],
   [7, 8], [8, 11], [11, 12], [12, -1]]

path_shape_sha256:
  111e352da3d2c92ab8ddaa1b8a3e79b9e3b58c9f9b6199f061f8349773f89d56
```

Coverage.py negative endpoints are expected entry/exit sentinels, not source lines.

Each selector is expected to retain branch statistics:

```text
line 4: total_exits=2, taken_exits=1
line 8: total_exits=2, taken_exits=1
missing_branch_count=2
missing_branch_arc_identity_status=unavailable-public-api
```

The exact public-API observations have not yet been made. Every divergence must remain visible.

## 9. H1 — aggregate structural equivalence

All five profiles are preregistered to have the same complete profile-level aggregates:

```text
statement union:
  [2, 3, 4, 5, 7, 8, 9, 11, 12]

statement intersection:
  [2, 3, 4, 8, 12]

arc union:
  [[-1, 2], [2, 3], [3, 4], [4, 5], [4, 7], [5, 8],
   [7, 8], [8, 9], [8, 11], [9, 12], [11, 12], [12, -1]]

arc intersection:
  [[-1, 2], [2, 3], [3, 4], [12, -1]]
```

Therefore:

```text
statement_union_intersection_discriminates_profiles = false
arc_union_intersection_discriminates_profiles       = false
```

This is a hypothesis, not an acceptance condition.

## 10. H2 — anonymous path-multiset discrimination

For each selector, define a path shape from exactly:

```text
executed_statement_set
executed_arc_set
```

The anonymous profile representation is an order-independent **multiset** of path-shape digests. It excludes:

```text
selector
selector_id
quadrant_id
context_id
invocation_binding
hit_count_magnitude
```

Those identities remain bound separately in selector records. Their exclusion from the anonymous key prevents profile discrimination from being manufactured by names or bindings.

Multiplicity is retained explicitly. Two identical path shapes cannot be silently collapsed into one set member.

Expected profile multiset digests:

```text
diagonal-only-v1:
  43030e3791c320d717807e2d2bf9677292c67e57350cf0aa9fca6d8a7e984dd5

mfa-independence-v1:
  9c3e35b470b3c42df525c6552b50299249a34a79ffe4ce7c56db083b8b1f0879

role-independence-v1:
  430503c94590e882f43c27015584d955f2783194c33b233919bd86a582f0a3bf

mcdc-basis-v1:
  c965ac7e5a1e1d6a3cb5367487fd1f85f77529583d3d9bf14654bb26f8eebedc

full-truth-table-v1:
  3f4b67b6016ad18caaf6637327dd00a17d62e1c4fd2275fc7f9c5fe10521cd7f
```

The five signatures—and the three equal-cardinality signatures—are preregistered as distinct.

The primary comparison uses sets and multisets, not hit-count magnitude.

## 11. H3 — fixed condition-independence witnesses

The exact truth-table relations are:

```text
MFA independence witness:
  TT paired with TF

role independence witness:
  TT paired with FT
```

| Profile | MFA independence | Role independence |
|---|---:|---:|
| `diagonal-only-v1` | false | false |
| `mfa-independence-v1` | true | false |
| `role-independence-v1` | false | true |
| `mcdc-basis-v1` | true | true |
| `full-truth-table-v1` | true | true |

These relations are derived from frozen truth-table membership. They do not depend on future coverage or mutation observations.

## 12. Frozen mutation operators

The outcome-blind generic operator set is:

```text
drop-mfa-conjunct-v1
drop-role-conjunct-v1
or-gates-v1
constant-false-v1
constant-true-v1
```

Conceptual transformations:

```text
drop-mfa-conjunct-v1:
  return role_gate

drop-role-conjunct-v1:
  return mfa_gate

or-gates-v1:
  return role_gate or mfa_gate

constant-false-v1:
  return False

constant-true-v1:
  return True
```

Generation controls:

```text
duplicate-false-control-v1          -> duplicate
not-applicable-addition-control-v1  -> not_applicable
invalid-render-control-v1           -> invalid
```

The deterministic catalog contains:

```text
5 generated
1 duplicate
1 not_applicable
1 invalid
```

The catalog records source, semantic-AST, target, mutant, duplicate, invalid, and not-applicable identities. It contains no execution outcome, killed/survived label, receipt, or timing.

```text
catalog_sha256:
  2b06a86180a45fcd495c0bcf39365dde0cb590507e9a3528714f9ef58526308e
```

Survival must never be interpreted as equivalence.

## 13. H4 — frozen asymmetric mutant incidence

Expected profile outcomes:

| Mutant | Diagonal | MFA independence | Role independence | MC/DC basis | Full table |
|---|---:|---:|---:|---:|---:|
| `drop-mfa-conjunct-v1` | survive | kill | survive | kill | kill |
| `drop-role-conjunct-v1` | survive | survive | kill | kill | kill |
| `or-gates-v1` | survive | kill | kill | kill | kill |
| `constant-false-v1` | kill | kill | kill | kill | kill |
| `constant-true-v1` | kill | kill | kill | kill | kill |

This matrix is independently derivable from the frozen truth table and profile memberships. It is committed before execution.

A later runtime table must precede every summary and preserve:

```text
expected_outcome
observed_outcome
concordant
```

Tool error, timeout, missing receipt, context ambiguity, candidate invalidity, or unavailable measurement remains `indeterminate`, never killed or survived.

## 14. H5 — bounded cross-evidence agreement

For the dropped-conjunct controls only:

```text
MFA independence witness
    agrees with kill(drop-mfa-conjunct-v1)

role independence witness
    agrees with kill(drop-role-conjunct-v1)
```

For `or-gates-v1`, either fixed independence witness is expected to kill the mutant.

This is one exact Boolean-control relation. It does not establish that a path partition predicts arbitrary mutant detection or oracle strength.

## 15. Future result semantics

The later result contract must retain, before summaries:

- exact plan, catalog, prior-art, PR #46, and Coverage.py distribution identities;
- exact source, target, truth-table, profile, selector, test, command, binding, and context identities;
- typed one-logical-test outcome receipts;
- executable, executed, missing, target, arc, branch-statistic, and context evidence per selector;
- anonymous path shapes and path multisets, with multiplicity explicit;
- profile statement and arc union/intersection;
- truth-table independence witnesses;
- complete candidate and mutant selector tables;
- expected, observed, and concordance values at selector, profile, mutant, comparison, and analysis levels;
- complete unexpected results;
- explicit indeterminate evidence;
- finite nonnegative costs;
- stable semantic and complete-report digests;
- null/false policy fields.

A verifier must reconstruct those relations independently. Matching an unkeyed digest is insufficient.

## 16. Red-first requirements for the later result PR

Before outcome implementation, failing tests must require at least:

1. exact source, test, AST, target, quadrant, selector, profile, operator, mutant, plan, catalog, prior-art, and PR #46 identities;
2. every exact candidate selector passes through one typed logical-test receipt;
3. unique selector contexts and zero cross-contamination;
4. exact per-selector statement, arc, branch-statistic, and context records;
5. profile aggregates derived from complete selector records;
6. order-independent path multisets with multiplicity preserved;
7. selector reorder invariance and selector replacement sensitivity;
8. expected, observed, unexpected, and indeterminate semantics;
9. measured-empty versus unavailable separation;
10. complete typed mutant incidence before summaries;
11. independent truth-table and mutant-relation reconstruction;
12. rejection of source, test, target, quadrant, selector, context, producer, receipt, path, mutant, aggregate, comparison, policy, cost, or digest substitution;
13. rejection of duplicate JSON keys, unsafe links/paths, absolute-path disclosure, wrong types, reordered normative arrays, extra fields, NaN, infinity, and negative costs;
14. dependency-free base operation without Coverage.py;
15. editable, installed-wheel, clean offline research-extra, dependency-removal, and Python 3.11–3.14 reproduction.

Tests may not be weakened after outcomes are visible.

## 17. Falsification and redesign criteria

Narrow, redesign, or stop this line if:

1. profile statement or arc union/intersection differs after exact bytes are frozen;
2. anonymous path multisets are unstable across clean Python 3.11–3.14 runs;
3. profiles differ only through selector names or cardinality artifacts;
4. a simpler truth-table or MC/DC representation captures the same complete relation with less complexity;
5. Coverage.py contexts add no evidence beyond already frozen input labels;
6. mutation outcomes require post-outcome operator or selector tuning;
7. the asymmetric mutant table diverges from preregistration;
8. equivalent, invalid, or indeterminate mutants dominate the design;
9. representation changes alter path identities without semantic change;
10. the verifier cannot reject coordinated substitution beyond digest recomputation;
11. publication or execution cost exceeds the bounded evidence value.

A complete divergence is a valid `unexpected` result. The source, tests, profiles, operators, expected paths, expected mutant outcomes, or exclusion criteria must not be repaired after observation.

## 18. Cost model

The frozen future workload contains:

```text
unique candidate selector commands:
  4

unique generic-mutant selector commands:
  20
```

Profile outcomes should be derived from those unique selector observations rather than rerunning duplicated selectors for every profile membership.

This count does not include verifier-only work, packaging checks, negative regressions, or the existing PR #46 baseline. It is not a resource guarantee or an estimate for external repositories.

## 19. Integrity artifacts

```text
plan:
  research/DW-001/interaction-witness-lattice-plan.v1.json

plan schema:
  research/DW-001/schema/interaction-witness-lattice-plan.schema.json

plan_sha256:
  a79a500feb94c8ad78fe4633f9ca176465113de6297db2d07b2d005f5318e1f1

mutant catalog:
  research/DW-001/interaction-witness-lattice-mutant-catalog.v1.json

catalog schema:
  research/DW-001/schema/interaction-witness-lattice-mutant-catalog.schema.json

catalog_sha256:
  2b06a86180a45fcd495c0bcf39365dde0cb590507e9a3528714f9ef58526308e

prior-art log:
  research/DW-001/interaction-witness-prior-art-log.v1.json

prior_art_log_sha256:
  af6cb9782ea01a0e58baed8cfc1a4895dc1a53ed934498b307c6b05e8634c44f
```

The Python verifiers reconstruct exact semantic artifacts from fixed constants. Recomputed digests cannot hide reordered profiles/operators, changed source/test/target identities, changed expected path sets, changed mutant incidence, policy escalation, or novelty-claim substitution.

All current digests remain unkeyed integrity checks, not producer authentication.

## 20. Safety and publication boundary

Only fixed project-owned synthetic bytes are present. The design verifier is not a sandbox.

This preregistration authorizes no:

- candidate or mutant execution;
- Coverage.py measurement;
- external repository or benchmark;
- SWE-bench or TDD-Bench;
- holdout access;
- private data or secret;
- upload, telemetry, or remote service;
- plug-in or auto-start;
- subprocess coverage or concurrency adapter;
- persistent raw `.coverage` publication;
- score, threshold, or merge blocker;
- release, deployment, or `main` ruleset.

The committed JSON artifacts exclude source and test bodies. Selector names, truth-table labels, path/target identities, mutant IDs, digests, and future contexts remain publication metadata requiring review.

## 21. Claim boundary

Merging this preregistration may establish only that exact design choices, identities, hypotheses, controls, direct-baseline boundaries, and future result semantics were committed before execution.

It establishes **no observed result** and does not establish:

- that profile aggregation actually loses useful information;
- that Coverage.py contexts add useful evidence;
- that the path multisets are stable or discriminating at runtime;
- that the mutation table matches preregistration;
- general path, branch, condition, MC/DC, checked-coverage, or mutation adequacy;
- complete oracle strength or patch correctness;
- coding-agent prevalence or ecological effectiveness;
- method superiority;
- a score, threshold, or merge policy;
- containment, authentication, Gate 0 or Gate 1 completion;
- production readiness;
- scientific novelty or award-level significance.
