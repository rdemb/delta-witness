# Statement-Coverage Direct Baseline Architecture v1

## Status

This document defines the architecture of one development-only direct baseline used by DW-001. It supplements the repository-wide architecture and does not authorize external repository execution, coverage policy, merge blocking, ecological inference, or holdout use.

## Position in the evidence stack

```text
four-state witness
    -> exact declared-selector localization
    -> fixed mutation design
    -> typed mutation-result table
    -> statement-coverage direct baseline
    -> broader calibration and policy (future)
```

The baseline is deliberately evaluated **after** the source, target, selectors, mutants, and mutation-result identity have been frozen. Its purpose is to test whether a substantially simpler dynamic signal explains the same bounded strong-versus-weak oracle contrast.

## Components

### 1. Frozen source inputs

The result runner accepts only independently verified versions of:

- `claim-scoped-mutation-plan.v1.json`;
- `claim-scoped-mutant-catalog.v1.json`;
- the exact typed mutation result with its frozen semantic digest.

The source relation is fixed to:

```text
source_id = authorization-predicate-candidate-v1
path      = src/access.py
symbol    = is_admin
target    = line 2
```

The public runner accepts no caller-provided source body, test body, selector, target, expected signature, mutation result, score, threshold, or policy decision.

### 2. Parent result runner

`src/deltawitness/dw001_statement_coverage.py`:

1. verifies the plan, catalog, and mutation result;
2. derives exact profile and selector identities;
3. materializes fixed project-owned candidate and test bytes in a disposable directory;
4. derives a shell-free child command and invocation binding;
5. executes one child process per selector;
6. verifies typed outcome and trace receipts;
7. derives selector and profile coverage semantics;
8. compares the statement signatures with the frozen mutation table;
9. derives analysis, policy, cost, semantic digest, and complete report digest;
10. self-verifies the complete result before returning it.

### 3. Child trace producer

`src/deltawitness/statement_trace_probe.py`:

- uses standard-library unittest framework APIs;
- installs a current-thread `sys.settrace` callback;
- accepts only a normalized relative target path, exact symbol, exact source digest, and positive target-line set;
- resolves the target under the current disposable working directory;
- rejects target-path escape, links, non-files, and source-digest mismatch;
- counts a function call only when both resolved code filename and `co_name` match;
- retains line events only when the executed line belongs to the declared target set;
- emits the existing outcome receipt and a separate trace receipt;
- restores any prior tracing state before result interpretation.

### 4. Statement-trace receipt

The trace receipt has its own schema, producer identity, invocation binding, target relation, status, call count, covered-line set, line-hit records, diagnostic code, and complete digest.

```text
trace_status = complete | indeterminate
```

For `complete`:

- `function_calls` is a nonnegative integer;
- covered lines are sorted, unique, positive, and contained in the target set;
- line-hit records are sorted, unique, and positive;
- `trace_error` is null.

For `indeterminate`:

- `function_calls` is null;
- covered lines and hit records are empty;
- a stable non-empty trace error is required.

A complete zero-call trace is valid complete negative evidence. An indeterminate trace is never represented as complete empty coverage.

## Invocation binding

The statement-coverage binding includes:

- result and adapter schema identity;
- plan and catalog digests;
- mutation-result semantic digest;
- profile and selector identity;
- source and test digest;
- target ID and target-line set;
- exact child command;
- outcome observer;
- trace schema and producer identity.

The binding reduces accidental cross-selector or cross-experiment reuse. It is visible to tested code and is not producer authentication.

## Selector semantics

Every selector retains independently:

```text
expected_observed
observed
outcome_concordant
expected_covered_lines
coverage_status
coverage_concordant
concordant
```

Coverage status is:

```text
complete
candidate_invalid
indeterminate
```

A passing selector with a complete trace can produce either concordant or unexpected coverage. A failing candidate selector is not interpreted as normal coverage evidence. Error, timeout, or unavailable tracing is indeterminate.

## Profile aggregation

For each frozen profile, the runner derives:

- exact selector order;
- union of selector target-line sets;
- intersection of selector target-line sets;
- per-line aggregate hit counts as diagnostics;
- all-selectors-passed status;
- profile coverage status;
- profile concordance;
- measured command and timing costs.

The primary comparison uses union and intersection **sets**, not raw hit-count magnitude. This prevents profile cardinality from masquerading as oracle strength.

## Coverage-versus-mutation comparison

The result reports separately:

```text
statement_coverage_discriminates_profiles
mutation_discriminates_profiles
coverage_and_mutation_agree
incremental_mutation_signal_observed
```

The statement result is derived only when both profiles have complete coverage evidence. The mutation result is derived from the independently verified generic-mutant table. If coverage is incomplete, coverage-dependent comparison fields are null.

These fields are evidence relations, not policy decisions.

## Expected, unexpected, and indeterminate result flow

```text
complete and preregistration-concordant
    -> analysis.status = expected

complete and preregistration-divergent
    -> analysis.status = unexpected

any selector trace indeterminate
    -> analysis.status = indeterminate
```

A complete unexpected signature is a valid negative result. It does not cause the runner to rewrite the source, target, selectors, expected signature, or mutation result.

Malformed or relationally inconsistent evidence remains invalid and cannot be rescued by an `unexpected` label.

## Integrity model

### Stable semantic digest

The semantic digest retains:

- source and target identities;
- profiles, selectors, commands, and invocation bindings;
- outcome receipts;
- complete trace receipts;
- covered-line sets and hit counts;
- expected and observed semantics;
- comparison, analysis, policy, and command counts.

It normalizes creation time, runtime identity, selector durations, output digests, and measured CPU/wall time.

### Complete report digest

The complete report digest binds the entire artifact including runtime and cost diagnostics.

The verifier reconstructs all derivable relations. Digest recomputation alone cannot authorize changed source, target, selector, command, trace, aggregate, comparison, policy, or denominator semantics.

## Packaging and supported runtimes

CI exercises:

- editable installation;
- public API import;
- full statement-coverage smoke;
- strict public-tree validation;
- source compilation;
- full test suite;
- existing end-to-end matrix and influence demo;
- wheel build without dependency resolution;
- force-reinstalled wheel API and complete smoke.

The supported CI matrix is Python 3.11–3.14. Cross-version agreement is required for stable target-line signatures and result semantic digest.

## Architectural non-claims

This layer does not establish:

- full line, branch, path, condition, data-flow, or semantic coverage;
- coverage adequacy;
- oracle relevance or strength;
- mutation adequacy;
- method superiority;
- execution containment;
- producer authenticity;
- policy or merge authorization;
- ecological or held-out effectiveness.

See also:

- [DW-001 Claim-Scoped Statement-Coverage Baseline v1](../research/DW-001/STATEMENT_COVERAGE_BASELINE_V1.md)
- [Statement-Coverage Threat Boundary v1](../research/DW-001/STATEMENT_COVERAGE_THREAT_BOUNDARY_V1.md)
- [Repository Architecture](ARCHITECTURE.md)
- [Repository Threat Model](../THREAT_MODEL.md)
