# DW-001 Statement-Coverage Comparison Protocol v1

**Status:** frozen owned-synthetic development protocol for one direct-baseline comparison. It is not the DW-001 ecological protocol, not a holdout, and not an authorization to execute external repositories.

## 1. Research question

> For the exact fixed authorization predicate and selector profiles, does claim-target statement coverage distinguish the strong authorization oracle from the weak Boolean proxy, and does the already frozen mutation-result table provide an incremental signal beyond that coverage baseline?

## 2. Frozen source artifacts

The protocol requires the exact verified artifacts:

```text
plan_sha256
0ebf64e1de76849050c86d8a4d53d72d8067561ab48b4bd5a4083495dc99fe37

catalog_sha256
7b3e405bd3893f532c0ccfa16e9cc208422bbdd20dfe82a002c99342a04201c0

mutation_result_semantic_sha256
9e101bca85fd630bf5bdb2a6030d9fdab93eb3eac54b03f4aab99012c28086b6

target_id
3cdfc367a78a09b257147fb236e80785d936177da231924f43e2d3d5fbd80e2e
```

Fixed source relation:

```text
source_id = authorization-predicate-candidate-v1
path      = src/access.py
symbol    = is_admin
target    = [2]
```

## 3. Frozen profiles

### Strong authorization profile

```text
test_access.AccessTests.test_admin_is_allowed
test_access.AccessTests.test_viewer_is_denied
```

### Weak Boolean-proxy profile

```text
test_access.AccessTests.test_viewer_result_is_boolean
```

No selector may be added, removed, reordered, renamed, or replaced after trace results are visible.

## 4. Frozen adapter

```text
adapter_id          = stdlib-statement-trace-v1
outcome observer    = outcome-receipt-v1
trace API           = sys.settrace
trace thread scope  = current-thread
trace schema        = deltawitness.statement-trace-receipt.v1
```

The adapter observes only the exact declared source path, symbol, source digest, and target-line set.

## 5. Execution population

Only the unmutated fixed candidate executes under this protocol. Mutants are not re-executed.

```text
2 profiles
3 selectors
3 child commands
```

The previously frozen mutation-result artifact is consumed as a verified comparison source.

## 6. Selector prerequisites

For ordinary complete coverage interpretation, every selector must:

- execute one logical test;
- return typed `pass` through receipt/process agreement;
- emit a valid trace receipt;
- report `trace_status = complete`.

A candidate selector failure yields `candidate_invalid`. Error, timeout, missing trace, malformed trace, or unavailable tracing yields `indeterminate`.

## 7. Frozen expected selector signatures

For all three selectors:

```text
expected_observed      = pass
expected_covered_lines = [2]
expected_function_calls = 1
```

Function-call count and hit count are diagnostic. The primary profile comparison uses covered-line sets.

## 8. Frozen expected profile signatures

```text
strong union        = [2]
strong intersection = [2]
weak union          = [2]
weak intersection   = [2]
```

Expected diagnostic aggregate hits:

```text
strong line 2 hits = 2
weak line 2 hits   = 1
```

The hit-count difference follows profile selector cardinality and is not a strength claim.

## 9. Frozen comparison hypotheses

```text
expected_statement_coverage_discriminates_profiles = false
expected_mutation_discriminates_profiles           = true
expected_coverage_and_mutation_agree                = false
expected_incremental_mutation_signal_observed       = true
```

## 10. Outcome semantics

### Selector coverage status

```text
complete
candidate_invalid
indeterminate
```

### Top-level analysis status

```text
expected
unexpected
indeterminate
```

Precedence:

```text
indeterminate
    before unexpected
    before expected
```

A complete unexpected signature remains a valid negative result. It does not authorize post-hoc changes to source, target, selectors, expectations, or the mutation result.

## 11. Profile aggregation

When every selector in a profile has complete coverage evidence:

- `union_lines` is the sorted union of selector covered-line sets;
- `intersection_lines` is the sorted intersection;
- `line_hits` is the sorted sum of per-selector hit records;
- `all_selectors_passed` is derived from typed selector outcomes;
- profile concordance is derived from expected and observed pass/coverage signatures.

When any selector is indeterminate or candidate-invalid, line-set aggregates are null and no ordinary coverage comparison is emitted for that profile.

## 12. Mutation comparison

`mutation_discriminates_profiles` is derived only from generic-mutant records in the verified frozen mutation result.

The following do not enter this comparison:

- candidate baseline;
- historical PR #34 control;
- duplicate generation record;
- invalid generation record;
- not-applicable generation record.

If any generic strong or weak mutation-profile outcome is indeterminate, mutation discrimination is null.

## 13. Primary interpretation

A result matching the frozen hypothesis supports only this statement:

> Under the exact fixed source, selectors, target statement, and mutation table, both selector profiles execute the same target-statement set while the frozen generic mutants produce different strong-versus-weak outcomes.

It does not support:

- statement coverage is generally inadequate;
- mutation testing is generally superior;
- the weak selector is always unsafe;
- the three-mutant set is adequate;
- coverage or mutation should block a merge.

## 14. Integrity and reproducibility

The result must:

- strict-decode and semantically verify every source artifact;
- bind every child invocation to exact stable relations;
- verify typed outcome and trace receipt consistency;
- recompute selector, profile, comparison, analysis, policy, and cost fields;
- recompute stable semantic and complete-report digests;
- reproduce stable source, target, profile, line-set, comparison, and semantic-digest identities on Python 3.11–3.14;
- pass from editable and force-reinstalled wheel packages.

Runtime timestamps, implementation identity, command durations, output digests, and measured wall/CPU time are excluded from semantic equality but remain in the complete report.

## 15. Negative-result retention

If a complete selector covers a different target-line set:

- retain the complete trace;
- recompute selector and profile non-concordance;
- recompute comparison values;
- set `analysis.status = unexpected`;
- keep the artifact development-only and denominator-ineligible.

Do not alter the frozen target or expected signature to make the result concordant.

## 16. Indeterminate retention

If tracing cannot be established or verified:

- retain a bound indeterminate trace with a stable error code where possible;
- set selector and profile coverage status to indeterminate;
- set coverage-dependent comparison values to null;
- set `analysis.status = indeterminate`;
- do not report empty coverage.

## 17. Safety boundary

Execution is limited to fixed project-owned Python source and test bytes in disposable temporary directories.

No network, telemetry, upload, external repository, benchmark instance, package manager, third-party coverage engine, secret, remote execution service, or new repository permission is introduced.

The runner is not a sandbox. Host Python, `sys.settrace`, unittest, filesystem, operating system, and process environment remain trusted.

## 18. Falsification criteria

Narrow or redesign if:

- target events cannot be bound reproducibly to exact source and symbol;
- tracing changes selector outcomes;
- Python 3.11–3.14 disagree on stable target-line sets;
- missing trace becomes empty coverage;
- hit-count magnitude determines the profile conclusion;
- complete unexpected results cannot be retained;
- malformed or contradictory evidence is accepted as unexpected;
- Coverage.py or a simpler direct interface supplies the same exact evidence with materially less complexity;
- the comparison requires changing frozen inputs after execution.

## 19. Policy refusal

The result must retain:

```text
quality_score                        = null
headline_score                       = null
universal_threshold                  = null
merge_blocker_authorized             = false
ecological_inference_allowed         = false
holdout_selected                     = false
primary_denominator_eligible         = false
coverage_superiority_claim_allowed   = false
mutation_superiority_claim_allowed   = false
```

## 20. Publication wording

Permitted:

> In one fixed owned-synthetic authorization case, the strong and weak selector profiles execute the same declared target-statement set, while the previously frozen generic mutation table distinguishes their outcomes.

Not permitted:

> Mutation testing is superior to coverage.

> Statement coverage cannot evaluate coding-agent tests.

> The result validates oracle strength, mutation adequacy, merge blocking, or production safety.

Every public statement must cite the exact immutable implementation and result revision and retain the development-only boundary.
