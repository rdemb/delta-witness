# DW-001 Selector-Context Interaction Witness Lattice Result v1

## Status

This document records one development-only result over the exact project-owned synthetic source, tests, truth table, selector profiles, path hypotheses, mutation operators, mutant identities, expected incidence table, and direct-baseline boundary merged before authorized execution in PR #48.

```text
preregistration_merge_commit:
  7eef6ffe296081449427ccf550a6bc75a91218c2

execution_protocol_sha256:
  e10a9e287555ee8a1b8c0a9b7768d2f949c04a70081a778d51fefb78c1276912

plan_sha256:
  a79a500feb94c8ad78fe4633f9ca176465113de6297db2d07b2d005f5318e1f1

catalog_sha256:
  2b06a86180a45fcd495c0bcf39365dde0cb590507e9a3528714f9ef58526308e

prior_art_log_sha256:
  af6cb9782ea01a0e58baed8cfc1a4895dc1a53ed934498b307c6b05e8634c44f
```

The result is not ecological evidence. It is not eligible for a primary denominator, score, threshold, merge blocker, holdout claim, MC/DC certification, method-superiority claim, production claim, scientific-novelty claim, or award-level claim.

## 1. Research question

> For one preregistered two-condition owned-synthetic authorization function, can exact selector-context path partitions preserve condition-interaction evidence that is lost by profile-level statement and arc union/intersection, and does that retained partition relation agree with a separately frozen asymmetric mutant-outcome table?

The question was frozen before the authorized result branch executed the source, selectors, Coverage.py measurements, or mutants.

## 2. Exact owned-synthetic case

The source evaluates two authorization conditions:

```text
role_ok = role is admin
mfa_ok  = MFA is present
allow   = role_ok AND mfa_ok
```

Exact source and test identities:

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

test_id:
  two-condition-authorization-selectors-v1

test_sha256:
  02d1069245ae05a76a128aada50affbbe04c83f40f06ce7f4e7f8dde5cdd4bdc

target_id:
  6b20aa0ad5180288edffc9644e85252a774c2efb0c8ee9a32852b0d0ca50728e
```

Frozen truth table:

| Quadrant | Role condition | MFA condition | Expected decision |
|---|---:|---:|---:|
| `TT` | true | true | allow |
| `TF` | true | false | deny |
| `FT` | false | true | deny |
| `FF` | false | false | deny |

All four exact candidate selectors passed through invocation-bound typed receipts as one logical unittest each. Every Coverage.py measurement was complete and retained one unique static selector context with no cross-contamination.

## 3. Exact Coverage.py boundary

```text
package:
  coverage

version:
  7.15.2

distribution_manifest_sha256:
  28f6430e45fcfda973a1fcd57157e2317f096cc2774e8281244eaf18a9d0dd3f

public_api_only:
  true

data_file:
  null

timid:
  true

branch:
  true

config_file:
  false

plugins:
  []

auto_start:
  false

subprocess_measurement:
  false

network_during_measurement:
  false
```

Each selector executed in its own child process and disposable nonsensitive directory. The runner is not a sandbox.

## 4. Observed per-selector path evidence

### `TT`

```text
selector:
  test_access.AccessTests.test_admin_with_mfa_is_allowed

executed statements:
  [2, 3, 4, 5, 8, 9, 12]

executed arcs:
  [[-1, 2], [2, 3], [3, 4], [4, 5],
   [5, 8], [8, 9], [9, 12], [12, -1]]

path_shape_sha256:
  1d96c8895c09bf56a9617e7927e31a9eccaf5cdc9c67f24880fc77abd0255361
```

### `TF`

```text
selector:
  test_access.AccessTests.test_admin_without_mfa_is_denied

executed statements:
  [2, 3, 4, 5, 8, 11, 12]

executed arcs:
  [[-1, 2], [2, 3], [3, 4], [4, 5],
   [5, 8], [8, 11], [11, 12], [12, -1]]

path_shape_sha256:
  46ab1e2b779a82855ec5188f0b2980d78d4b1506b5b5d37a2c4ea45922c78236
```

### `FT`

```text
selector:
  test_access.AccessTests.test_viewer_with_mfa_is_denied

executed statements:
  [2, 3, 4, 7, 8, 9, 12]

executed arcs:
  [[-1, 2], [2, 3], [3, 4], [4, 7],
   [7, 8], [8, 9], [9, 12], [12, -1]]

path_shape_sha256:
  9f7fe46e5b626c9922262f8768090479c8ed0a9babcaf337db2d56eb240cbf48
```

### `FF`

```text
selector:
  test_access.AccessTests.test_viewer_without_mfa_is_denied

executed statements:
  [2, 3, 4, 7, 8, 11, 12]

executed arcs:
  [[-1, 2], [2, 3], [3, 4], [4, 7],
   [7, 8], [8, 11], [11, 12], [12, -1]]

path_shape_sha256:
  111e352da3d2c92ab8ddaa1b8a3e79b9e3b58c9f9b6199f061f8349773f89d56
```

Negative arc endpoints are Coverage.py entry/exit sentinels, not source lines.

## 5. Aggregate structural result

All five frozen profiles produced identical complete profile-level aggregates:

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
statement_aggregate_discriminates_profiles = false
arc_aggregate_discriminates_profiles       = false
```

The experiment does not use statement or arc hit-count magnitude in the primary comparison.

## 6. Selector-path multiset result

Each per-selector path shape contains only:

```text
executed statement set
executed arc set
```

The anonymous profile representation excludes selector names, selector IDs, quadrant labels, contexts, invocation bindings, and hit-count magnitude. Those identities remain retained separately in the complete result.

The representation is an order-independent multiset and preserves multiplicity.

Observed profile path-multiset digests:

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

All five signatures were distinct. The three equal-cardinality three-selector profiles were also distinct.

Therefore:

```text
anonymous_path_multiset_discriminates_profiles = true
equal_cardinality_path_multisets_distinct       = true
```

This is an exact representation result in one fixed control. It is not dynamic slicing, checked coverage, general path coverage, condition coverage, or a general test-quality measure.

## 7. Condition-independence controls

Frozen truth-table relations:

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

These are exact truth-table membership relations. `mcdc-basis-v1` is a fixed two-condition control, not a general MC/DC implementation or certification.

## 8. Complete mutant incidence result

Exactly five generated generic mutants executed under the same four selectors. Duplicate, invalid, and not-applicable catalog records remained non-executed.

| Mutant | `TT` | `TF` | `FT` | `FF` |
|---|---:|---:|---:|---:|
| `drop-mfa-conjunct-v1` | pass | fail | pass | pass |
| `drop-role-conjunct-v1` | pass | pass | fail | pass |
| `or-gates-v1` | pass | fail | fail | pass |
| `constant-false-v1` | fail | pass | pass | pass |
| `constant-true-v1` | pass | fail | fail | fail |

Derived profile outcomes:

| Mutant | Diagonal | MFA independence | Role independence | MC/DC basis | Full table |
|---|---:|---:|---:|---:|---:|
| `drop-mfa-conjunct-v1` | survived | killed | survived | killed | killed |
| `drop-role-conjunct-v1` | survived | survived | killed | killed | killed |
| `or-gates-v1` | survived | killed | killed | killed | killed |
| `constant-false-v1` | killed | killed | killed | killed | killed |
| `constant-true-v1` | killed | killed | killed | killed | killed |

Every selector and profile outcome matched the preregistration. The complete table precedes the summary.

```text
mutation_score = null
```

Survival does not establish equivalence. Five fixed mutants do not establish mutation adequacy or operator representativeness.

## 9. Cross-evidence comparison

Observed relations:

```text
statement_aggregate_discriminates_profiles                 = false
arc_aggregate_discriminates_profiles                       = false
anonymous_path_multiset_discriminates_profiles             = true
equal_cardinality_path_multisets_distinct                  = true
mfa_independence_agrees_with_drop_mfa                      = true
role_independence_agrees_with_drop_role                    = true
any_independence_agrees_with_or_gates                      = true
comparison.concordant                                      = true
analysis.status                                            = expected
```

The bounded observation is:

> In this exact two-condition owned-synthetic case, profile-level statement and executed-arc union/intersection lost the per-selector path-combination distinction, while an anonymous multiset of exact selector path shapes retained it. The fixed truth-table condition-independence relations also agreed with the separately frozen dropped-conjunct and connector mutant incidence table.

That statement applies only to this frozen control.

## 10. Integrity and negative-result semantics

The verifier independently reconstructs:

- PR #48 merge, execution protocol, plan, catalog, prior-art, Coverage.py manifest, and PR #46 identities;
- source, test, AST, target, truth-table, selector, profile, operator, and mutant identities;
- candidate and mutant commands and invocation bindings;
- typed receipt/process agreement;
- Coverage.py distribution, configuration, statement, arc, branch-statistic, and context evidence;
- per-selector path shapes;
- anonymous path multisets and multiplicity;
- profile statement and arc union/intersection;
- truth-table condition-independence witnesses;
- mutant selector and profile outcomes;
- summary, comparison, analysis, policy, and finite costs;
- semantic and complete-report digests.

Regression tests retain:

- a complete structurally valid preregistration-divergent result as `unexpected`;
- tool error, timeout, missing optional dependency, missing data, or context ambiguity as `indeterminate`;
- complete measured-empty evidence separately from unavailable measurement;
- rejection of source, test, target, selector, quadrant, context, path, mutant, aggregate, comparison, policy, cost, producer, receipt, or digest substitution;
- rejection of duplicate keys, unsafe links and paths, absolute-path disclosure, wrong types, extra fields, reordered normative arrays, negative costs, NaN, and infinity.

Matching an unkeyed digest alone is insufficient.

## 11. Reproduction

The complete result was reproduced under:

- Python 3.11;
- Python 3.12;
- Python 3.13;
- Python 3.14;
- editable DeltaWitness installation;
- force-reinstalled DeltaWitness base wheel;
- exact hash-verified Coverage.py `7.15.2` universal wheel installed offline;
- Coverage.py removal followed by dependency-free design and verifier smokes.

Stable result semantic identity:

```text
semantic_sha256:
  bc2ab879595da61815a17dcc33a09c6334b93dea3fd464f2fe4a5437944ebb77
```

Public-safe checkpoint:

```text
research/DW-001/interaction-witness-lattice-result-checkpoint.v1.json

checkpoint_sha256:
  40cf297679c83809368e53f35796d817761c25746302530f29fa4dda603277fc
```

The checkpoint retains stable research semantics and the complete outcome tables. Volatile process receipts, commands, contexts, runtime identity, and costs remain in reproducible full reports rather than the stable checkpoint.

One Python 3.11 hosted-run report is retained in the checkpoint explicitly as diagnostic-only evidence:

```text
workflow run:
  32063085079

workflow job:
  95488644926

head SHA:
  050b11760c2c42da274ca20f86ce21d91f6d5b9e

report_sha256:
  f67aa03c024852297db256a70f270f1600f347a7d81e95a0a2337ec4efb79632

process wall-clock:
  1.993077 seconds

Coverage.py wall-clock:
  0.229917 seconds

Coverage.py CPU:
  0.229885 seconds
```

These timings are not performance guarantees, native-method comparisons, or external-repository cost estimates.

## 12. Prior-art boundary

Established work includes:

- Coverage.py statement, arc, branch-statistic, and measurement-context APIs;
- path and basis-path coverage;
- modified condition/decision coverage;
- combinatorial input/configuration coverage;
- checked coverage and dynamic slicing to an oracle;
- mutation testing, selective mutation, and equivalent-mutant analysis;
- the test-oracle problem.

The exact prior-art log records:

```text
novelty_status                         = not_established
systematic_review_complete             = false
scientific_novelty_claim_allowed       = false
award_level_significance_claim_allowed = false
```

This result does not establish that the selector-path multiset is a novel method or that it is preferable to simpler truth-table, MC/DC, combinatorial, checked-coverage, or mutation baselines.

## 13. Limitations

- One project-owned synthetic Boolean conjunction is not a population.
- The source was intentionally constructed to make aggregate signatures equal and per-selector paths distinct.
- The truth-table labels are known project-owned ground truth.
- Selector paths retain control-flow co-occurrence, not data or control dependence to assertions.
- Static contexts identify measurement partitions but are visible strings, not authentication.
- Python and Coverage.py line/arc representations can change without an intended semantic change.
- The five mutants are fixed controls, not a representative mutation model.
- Surviving mutants may be non-equivalent or equivalent; this experiment does not solve equivalence.
- A matching incidence table does not estimate precision, recall, prevalence, or ecological effectiveness.
- Runtime and cost diagnostics are environment-specific.
- Coverage.py, Python, SQLite, filesystem, operating system, CI image, and dependencies remain trusted.
- The runner is not a sandbox.
- All digests are unkeyed integrity evidence, not signed attestations.
- The public merge establishes reproducible ordering, not proof that no private execution occurred earlier.

## 14. Policy boundary

```text
quality_score                         = null
headline_score                        = null
universal_threshold                   = null
merge_blocker_authorized              = false
ecological_inference_allowed          = false
holdout_selected                      = false
primary_denominator_eligible          = false
mcdc_certification_claim_allowed      = false
coverage_superiority_claim_allowed    = false
mutation_superiority_claim_allowed    = false
method_superiority_claim_allowed      = false
scientific_novelty_claim_allowed      = false
award_level_significance_claim_allowed = false
production_readiness_claim_allowed    = false
```

## 15. Claim boundary

The result supports only this bounded statement:

> For one exact preregistered project-owned two-condition authorization control, five selector profiles had identical profile-level executed-statement and executed-arc union/intersection signatures, but distinct order-independent multisets of their exact per-selector statement-and-arc path shapes. The fixed truth-table condition-independence relations agreed with the separately frozen incidence of five generated Boolean fault controls.

It does not support any claim that:

- statement or branch coverage is generally insufficient;
- Coverage.py is weak or unsuitable;
- selector-path multisets measure complete oracle strength;
- the representation is path coverage, checked coverage, dynamic slicing, or general MC/DC;
- mutation testing is generally superior or sufficient;
- five mutants establish mutation adequacy;
- the relation predicts arbitrary fault detection;
- the method works on real coding agents or external repositories;
- an ecological result, score, threshold, or merge blocker is justified;
- Gate 0 or Gate 1 is complete;
- the runner provides containment or authentication;
- the project is production-ready;
- scientific novelty or award-level significance has been demonstrated.
