# DW-001 Statement-Coverage Threat Boundary v1

## Status

This document supplements the repository-wide threat model for the development-only `stdlib-statement-trace-v1` baseline. The baseline executes only fixed project-owned bytes. It is not a containment system and does not authorize external repository execution.

## Protected statement

> Given the exact verified mutation plan, catalog, mutation-result semantic identity, candidate source, target symbol, target-line set, and selector profiles, the baseline records invocation-bound typed selector outcomes and current-thread Python statement traces, derives exact profile line-set signatures, and compares them with the frozen mutation result while preserving expected, unexpected, and indeterminate evidence separately.

This statement does not establish coverage adequacy, oracle strength, mutation adequacy, method superiority, ecological effectiveness, or deployment safety.

## Assets

The design aims to protect:

- exact plan, catalog, mutation-result, source, AST, and target identities;
- exact profile and selector order;
- exact source and test SHA-256 relations;
- shell-free child commands;
- invocation binding among experiment, source, target, profile, selector, command, observer, and trace producer;
- separation of typed selector outcome from statement-trace status;
- separation of complete empty coverage from indeterminate tracing;
- exact target-function call count;
- sorted unique covered target-line sets;
- positive per-line hit counts;
- profile union and intersection derivation;
- separation of primary set comparison from diagnostic hit magnitude;
- separation of frozen expected signatures from observed signatures;
- retention of complete preregistration-divergent traces as negative results;
- rejection of malformed or contradictory evidence even when labelled unexpected;
- comparison with the exact verified generic-mutant table;
- recomputation of comparison and analysis fields;
- refusal to emit scores, thresholds, blockers, holdout status, ecological inference, or primary-denominator eligibility;
- public artifacts from raw output, absolute paths, source/test bodies, credentials, and environment values.

## Adversaries and failure sources

The model includes:

- a trace producer that writes malformed, oversized, duplicate-key, linked, stale, or substituted JSON;
- a trace receipt copied across selectors, profiles, source revisions, targets, or experiments;
- a target path that is absolute, traverses parents, uses a link, escapes the disposable root, or resolves to different source bytes;
- target-line identities that are negative, duplicated, unsorted, outside the declared target, or changed after outcomes are visible;
- line-hit records that are duplicated, unsorted, zero, negative, non-integer, non-finite, or inconsistent with covered lines;
- a pre-existing trace function that prevents the fixed producer from establishing its declared semantics;
- tested code that changes or disables tracing;
- tested code that executes target behavior in another thread, process, native extension, generated code object, wrapper, or alternate path;
- code-object filename or symbol-name ambiguity;
- stale Python module cache in same-process test fixtures;
- source, test, selector, command, binding, receipt, profile, comparison, analysis, policy, or cost substitution;
- a candidate selector that fails or errors but whose trace is interpreted as normal successful coverage;
- a timeout or producer failure treated as empty coverage;
- raw hit-count magnitude treated as oracle strength despite different profile cardinality;
- a complete unexpected signature rejected as a harness error;
- malformed or receipt-contradictory evidence accepted because it is labelled unexpected;
- a frozen mutation result replaced with another valid result;
- generic-mutant outcomes summarized incorrectly or mixed with the historical control;
- unkeyed digests recomputed after coordinated semantic replacement;
- resource exhaustion, filesystem effects, network access, process creation, or malicious host/runtime behavior;
- public exposure of sensitive commands, paths, source/test material, output, identities, or environment values;
- overstatement of one owned-synthetic comparison as a general result.

## Invariants

1. Plan and catalog pass their authoritative semantic verifiers before coverage execution.
2. The mutation result passes its authoritative semantic verifier and equals the frozen semantic digest.
3. Source path, symbol, source digest, AST digest, target ID, and target line are exact fixed values.
4. Only the two frozen profiles and three frozen candidate selectors execute.
5. The runner accepts no caller-provided executable bytes, target, selector, expectation, comparison, score, or policy.
6. Each selector runs in a disposable directory containing only fixed project-owned source and test bytes required by the probe.
7. Commands execute without a shell under the existing reduced process environment.
8. Each child receives one deterministic invocation binding covering every stable execution relation.
9. The typed outcome receipt and trace receipt use the same binding.
10. A normal selector pass/fail requires typed receipt/process agreement.
11. The trace receipt is a bounded regular non-link strict UTF-8 JSON document with exact fields and duplicate-key rejection.
12. Trace target path is normalized, relative, contained under the disposable root, regular, non-link, and source-digest matched.
13. A trace call counts only when the resolved code filename and code-object name match the exact target.
14. A line event counts only when it belongs to the declared target-line set.
15. `complete` trace status requires a nonnegative call count, null error, and internally consistent line evidence.
16. `indeterminate` trace status requires null call count, empty line evidence, and a stable non-empty error code.
17. Missing, malformed, unavailable, or failed tracing becomes indeterminate, never complete empty coverage.
18. Candidate failure, error, or timeout cannot become ordinary complete selector coverage.
19. Per-selector expected outcome and expected line set remain separate from observed outcome and trace.
20. Complete preregistration-divergent evidence remains a valid result with recomputed non-concordance.
21. Profile union, intersection, hit counts, pass status, coverage status, concordance, and cost are derived from ordered selector evidence.
22. Hit-count magnitude is diagnostic and cannot determine profile discrimination.
23. Statement discrimination is derived only from complete profile union/intersection sets.
24. Mutation discrimination is derived only from verified generic-mutant profile outcomes; the candidate, historical control, and generation-only records are excluded.
25. Coverage-dependent comparison values are null when either coverage profile is incomplete.
26. Analysis status is derived as expected, unexpected, or indeterminate.
27. Policy fields remain null or false and cannot be changed by result concordance.
28. All timing and count values are finite and nonnegative.
29. Stable semantic digest and complete report digest are recomputed independently.
30. Raw source/test bodies, stdout, stderr, tracebacks, absolute paths, credentials, and environment values are absent from public artifacts.
31. Editable and installed-wheel smoke execute the complete fixed baseline on every supported Python version.
32. A valid result remains development-only and primary-denominator ineligible.

## Residual risks

### Tracing is not containment

`sys.settrace` observes selected Python execution events. It does not restrict filesystem access, network use, process creation, native code, resources, or external effects.

### Current-thread scope

The API is thread-specific. Relevant behavior executed outside the current traced thread may be absent. The current fixed fixture is single-threaded; this does not generalize to external repositories.

### Python implementation dependence

Trace event semantics, code filenames, frames, line tables, optimizations, and compiler behavior remain part of the trusted runtime. Runtime implementation and version are recorded, but not authenticated.

### Tested code can interfere

Code under test may inspect, replace, or disable tracing and can see the invocation binding. Current fixed owned-synthetic bytes do not resist a malicious target.

### Statement sets are coarse

Executing the same source line does not imply the same inputs, branch behavior, data flow, assertions, side effects, or semantic coverage. Different line sets also do not by themselves prove different oracle strength.

### Function and filename matching are narrow

The adapter matches one resolved code filename and one `co_name`. Decorators, wrappers, generated functions, aliases, nested functions, dynamic compilation, or alternate import paths can make this scope incomplete or misleading.

### Hit counts are confounded

Counts vary with selector cardinality, loops, repeated calls, framework behavior, and runtime. They are retained as diagnostics and are not a quality metric.

### Direct baseline is not mature coverage tooling

The standard-library adapter is a narrow dependency-free research control. It is not a replacement for Coverage.py, branch coverage, condition coverage, or other mature instrumentation.

### Mutation comparison is narrow

The frozen mutation table contains three generic mutants over one source. An incremental signal in this exact case does not establish broader mutation value.

### Integrity is not authentication

All digests are unkeyed. Complete coordinated replacement remains possible when separately trusted expected identities are also replaced.

### Repetition is limited

Each selector executes once per run. Stable results across the supported CI matrix do not establish behavior under stochastic tests or other environments.

### Publication metadata can be sensitive

Selectors, commands, source/test digests, target lines, bindings, receipt metadata, hit counts, runtime versions, and costs may reveal repository structure or equality. Export remains review-required.

## Safe operation

- Execute only fixed owned-synthetic bytes under this baseline.
- Treat any external repository execution as unauthorized until containment and admission contracts exist.
- Verify plan, catalog, mutation result, source, target, and selectors before execution.
- Preserve complete unexpected signatures and indeterminate traces.
- Never convert missing trace evidence to empty coverage.
- Never infer oracle strength from statement coverage or hit counts alone.
- Never infer general mutation superiority from this comparison.
- Keep scores, thresholds, merge blockers, holdout status, ecological inference, and primary-denominator eligibility disabled.
- Review every exported artifact for commands, selectors, paths, digests, bindings, receipt metadata, runtime identity, counts, and costs.

## Claim boundary

A valid artifact establishes only the exact selector outcomes, exact declared-target statement traces, derived profile line-set signatures, their relation to one frozen mutation result, and bounded costs for the fixed owned-synthetic experiment.

It does not establish full coverage, coverage adequacy, oracle strength, mutation adequacy, method superiority, external safety, ecological performance, legal admissibility, or deployment authorization.
