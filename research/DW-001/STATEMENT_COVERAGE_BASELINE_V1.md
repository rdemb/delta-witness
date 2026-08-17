# DW-001 Claim-Scoped Statement-Coverage Baseline v1

**Status:** development-only owned-synthetic direct-baseline evidence. This baseline is not a coverage-adequacy result, a mutation-testing superiority result, an ecological coding-agent evaluation, a merge policy, a holdout, or a production-safety claim.

## 1. Question

The frozen claim-scoped mutation experiment records one bounded contrast over one project-owned authorization predicate:

```text
strong authorization profile -> 3 / 3 generic mutants killed
weak Boolean-proxy profile    -> 3 / 3 generic mutants survived
```

Before expanding the mutant population, DW-001 asks whether a substantially simpler dynamic baseline exposes the same difference:

> Under the exact candidate source and exact frozen selectors, do the strong authorization profile and weak Boolean-proxy profile execute different claim-target statement sets, and what incremental signal—if any—does the frozen mutation table provide beyond that statement coverage?

## 2. Frozen source relation

The baseline accepts only the exact verified mutation plan, catalog, and mutation-result semantic identity:

```text
plan_sha256
0ebf64e1de76849050c86d8a4d53d72d8067561ab48b4bd5a4083495dc99fe37

catalog_sha256
7b3e405bd3893f532c0ccfa16e9cc208422bbdd20dfe82a002c99342a04201c0

mutation_result_semantic_sha256
9e101bca85fd630bf5bdb2a6030d9fdab93eb3eac54b03f4aab99012c28086b6

target_id
3cdfc367a78a09b257147fb236e80785d936177da231924f43e2d3d5fbd80e2e

source_id = authorization-predicate-candidate-v1
path      = src/access.py
symbol    = is_admin
target    = line 2
```

The runner accepts no caller-provided source, symbol, selector, target line, expected signature, mutation result, score, threshold, or policy decision.

## 3. Direct prior art and implementation boundary

Statement and line coverage are established software-testing techniques.

Python's standard-library `trace` module can count executed statement lines, produce annotated coverage listings, and list executed functions. Python's `sys.settrace` API supplies `call`, `line`, `return`, `exception`, and optional opcode events and is explicitly thread-specific. Coverage.py is the direct mature Python tooling baseline and adds capabilities including branch coverage.

Primary references:

- Python `trace` documentation: <https://docs.python.org/3/library/trace.html>
- Python `sys.settrace` documentation: <https://docs.python.org/3/library/sys.html#sys.settrace>
- Coverage.py branch coverage documentation: <https://coverage.readthedocs.io/en/latest/branch.html>

The current DeltaWitness adapter is intentionally narrower than these tools:

```text
adapter_id = stdlib-statement-trace-v1
trace API  = sys.settrace
thread     = current thread only
scope      = one exact source path, symbol, and target-line set
```

No novelty claim is made for tracing, statement coverage, line-hit counting, function-call counting, or profile comparison.

The question under test is narrower: whether an invocation-bound, exact claim-target statement signature adds or fails to add discrimination beyond the already localized selector, and how that compares with the frozen mutation evidence.

## 4. Frozen selector profiles

### Strong authorization profile

```text
test_access.AccessTests.test_admin_is_allowed
test_access.AccessTests.test_viewer_is_denied
```

### Weak Boolean-proxy profile

```text
test_access.AccessTests.test_viewer_result_is_boolean
```

Every selector must pass against the unmutated candidate before statement coverage can be interpreted.

## 5. Statement-trace receipt

Each child process emits two separate invocation-bound artifacts:

```text
outcome-receipt-v1
statement-trace-receipt-v1
```

The trace receipt binds:

- one invocation binding;
- producer name and version;
- exact relative source path;
- exact symbol;
- exact source SHA-256;
- exact target-line set;
- trace status;
- target-function call count;
- covered target-line set;
- per-target-line hit counts;
- stable trace error when indeterminate;
- complete trace-receipt digest.

Trace files must be bounded regular non-link UTF-8 JSON files with exact fields, recursive duplicate-key rejection, sorted unique positive line identities, positive hit counts, target-set containment, and digest agreement.

A complete trace may contain zero target calls and an empty target-line set. That is complete negative evidence, not an execution error. An indeterminate trace must contain no call count or coverage evidence and must retain a stable diagnostic code.

## 6. Execution path

For each of the three frozen selectors:

1. materialize the fixed candidate source and fixed candidate test bytes into a disposable directory;
2. derive the shell-free child command;
3. derive an invocation binding over plan, catalog, mutation result, profile, selector, source, tests, target, command, observer, and trace producer;
4. execute one logical unittest selector through `outcome-receipt-v1`;
5. install a current-thread `sys.settrace` callback in the child process;
6. count only frames whose resolved filename and code-object name match the exact target;
7. retain only declared target-line events;
8. load and verify both receipts;
9. derive selector, profile, comparison, analysis, policy, and cost evidence.

The fixed workload is:

```text
2 profiles
3 selectors
3 child commands
```

The coverage run does not execute mutants. It consumes the already verified mutation-result table as a separate comparison source.

## 7. Predeclared signatures

The candidate predicate is one executable return statement on line 2. The predeclared development hypothesis is:

```text
strong selector 1 target lines = [2]
strong selector 2 target lines = [2]
weak selector target lines     = [2]

strong profile union        = [2]
strong profile intersection = [2]
weak profile union          = [2]
weak profile intersection   = [2]
```

Therefore:

```text
statement_coverage_discriminates_profiles = false
mutation_discriminates_profiles           = true
coverage_and_mutation_agree                = false
incremental_mutation_signal_observed       = true
```

The current owned-synthetic execution matches this table on supported Python versions.

## 8. Why hit-count magnitude is not the primary comparison

The strong profile executes two selectors and the weak profile executes one. The expected diagnostic hit counts therefore differ:

```text
strong profile line 2 hits = 2
weak profile line 2 hits   = 1
```

That difference follows directly from profile cardinality. It is not evidence that the strong oracle is semantically stronger.

The primary comparison uses exact profile union and intersection **sets**. Per-line counts remain diagnostic and integrity-bound, but they cannot drive the discrimination result.

## 9. Expected and observed evidence remain separate

Every selector retains:

```text
expected_observed
observed
outcome_concordant
expected_covered_lines
coverage_status
coverage_concordant
concordant
```

Every profile retains predeclared union/intersection signatures, observed signatures, selector-pass status, coverage status, concordance, and cost.

The comparison retains predeclared and observed Boolean relations separately.

A complete invocation-bound trace that differs from the predeclared signature remains a valid negative result:

```text
complete unexpected coverage
    != malformed evidence
    != trace failure
```

Such a result sets:

```text
analysis.status = unexpected
```

and preserves the exact selector, profile, and comparison divergence.

## 10. Indeterminate precedence

The baseline treats any of the following as indeterminate coverage evidence:

- missing trace receipt;
- malformed or substituted trace receipt;
- unsupported or pre-existing tracing state;
- child timeout;
- typed outcome error;
- trace-producer error;
- unavailable trace semantics.

Indeterminate evidence is never converted into an empty covered-line set.

When either profile is not complete:

```text
statement_coverage_discriminates_profiles = null
coverage_and_mutation_agree                = null
incremental_mutation_signal_observed       = null
```

The independently verified mutation-result comparison remains visible, but no coverage conclusion is emitted.

## 11. Integrity model

The result has two unkeyed digests.

### `semantic_sha256`

Binds stable evidence including:

- plan, catalog, mutation-result, source, AST, and target identities;
- adapter and trace schema;
- profiles and selectors;
- commands and invocation bindings;
- typed receipt evidence;
- exact covered-line sets and line-hit counts;
- expected and observed signatures;
- comparison and analysis;
- policy and command counts.

It normalizes:

- creation time;
- runtime identity;
- selector durations;
- wall-clock and CPU times;
- stdout and stderr digests.

### `report_sha256`

Binds the complete artifact, including runtime and cost diagnostics.

The verifier reconstructs source relations, commands, bindings, trace structure, selector status, profile signatures, comparison, analysis, policy, costs, and both digests. Recomputing digests cannot make substituted or internally inconsistent evidence valid.

The digests do not authenticate the producer. An actor able to replace a complete trusted source and expected-digest chain can replace the evidence chain.

## 12. Security and privacy boundary

The runner executes only fixed project-owned Python source and test bytes in disposable temporary directories.

It adds no:

- external repository or benchmark execution;
- network access;
- package-manager or third-party coverage-tool invocation;
- upload or telemetry;
- secret or repository permission;
- remote execution service;
- containment claim.

The host Python implementation, `sys.settrace` semantics, filesystem, process environment, unittest adapter, and trace producer remain trusted.

`sys.settrace` is current-thread specific. Code that moves relevant behavior into other threads, native code, subprocesses, generated code, or callbacks outside the fixed target scope may not be represented. That limitation produces no general claim about coverage adequacy.

Public artifacts omit:

- source and test bodies;
- raw stdout, stderr, and tracebacks;
- absolute paths;
- usernames, credentials, and environment values;
- private endpoints.

Selectors, commands, source/test digests, invocation bindings, receipt metadata, line identities, hit counts, runtime identity, and costs remain publication metadata requiring review.

## 13. Falsification and redesign

Narrow or abandon this baseline if:

- tracing changes selector behavior;
- exact source/symbol filtering is not reproducible;
- Python 3.11–3.14 disagree on stable target-line sets;
- incomplete tracing is represented as empty coverage;
- hit-count magnitude drives the conclusion despite unequal profile cardinality;
- complete unexpected signatures cannot be retained;
- malformed or contradictory evidence is accepted as unexpected;
- Coverage.py or a simpler existing interface provides the same exact evidence contract with lower complexity;
- the result depends on changing the frozen source, target, selectors, mutation table, or expected signatures after execution.

A result where statement coverage distinguishes the profiles is valid and must not trigger post-hoc repair.

## 14. Current bounded observation

For the exact owned-synthetic candidate:

```text
strong profile union/intersection = [2] / [2]
weak profile union/intersection   = [2] / [2]
```

The statement-set baseline does not distinguish the profiles. The independently frozen mutation table does distinguish them.

This establishes one bounded incremental observation only:

```text
same claim-target statement set
    != same behavior under the frozen claim-scoped mutants
```

It does not establish that statement coverage is generally inadequate or that mutation testing is generally superior.

## 15. Policy refusal

The result fixes:

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

## 16. Claim boundary

A valid result establishes only:

- the typed selector outcomes;
- exact target-function call and statement-line evidence;
- profile union/intersection signatures;
- their relation to one exact frozen mutation-result table;
- bounded execution costs;
- expected, unexpected, or indeterminate analysis status.

It does not establish:

- general inadequacy of statement or branch coverage;
- general superiority of mutation testing;
- complete oracle relevance or strength;
- mutation adequacy;
- representativeness of the fixed source, selectors, or mutants;
- behavior on real coding agents or repositories;
- ecological effectiveness;
- merge-policy validity;
- containment, producer authentication, protocol freeze, independent reproduction, Gate 0 or Gate 1 completion;
- production readiness or scientific novelty.
