# DW-001 Coverage.py Direct-Baseline Threat Boundary v1

## Status

This document supplements the repository-wide `THREAT_MODEL.md` for the optional development-only `coveragepy-public-api-v1` baseline.

The baseline executes only fixed project-owned synthetic source and test bytes in disposable nonsensitive directories. Coverage.py and the DeltaWitness runner are observation mechanisms, not containment systems. This document does not authorize external repository execution.

## Protected statement

> Given the exact verified mutation plan, mutant catalog, frozen mutation-result semantic identity, frozen stdlib statement-result semantic identity, candidate source, target, and selector profiles, the direct baseline records invocation-bound typed selector outcomes and exact Coverage.py statement, arc, branch-stat, and static-context evidence; derives profile set signatures; and compares those signatures with the frozen stdlib and mutation evidence while preserving expected, unexpected, and indeterminate outcomes separately.

This statement does not establish coverage adequacy, oracle strength, mutation adequacy, method superiority, ecological effectiveness, or deployment safety.

## Assets

The design aims to protect:

- exact Coverage.py package, version, selected artifact filename, selected artifact digest, source commit, tag object, license, and distribution-manifest identity;
- the base package's zero-runtime-dependency path;
- the optional `research` extra boundary;
- offline installation of the exact verified universal wheel;
- absence of package-manager and network operations during measurement;
- exact plan, catalog, mutation-result, stdlib-result, source, target, profile, selector, command, and test identities;
- one unique static context per exact selector;
- one shared invocation binding across typed outcome and Coverage.py receipts;
- shell-free child execution under the reduced process environment;
- disabled ambient configuration, plug-ins, auto-start, concurrency, subprocess coverage, and persistent data files;
- exact executable, executed, missing, target, arc, branch-stat, and context relations;
- separation of a complete measured empty set from unavailable measurement;
- separation of complete preregistration-divergent evidence from malformed evidence;
- separation of statement/arc set comparison from hit-count or magnitude scoring;
- profile union and intersection derivation from complete selector records;
- recomputation of stdlib, Coverage.py, and mutation comparison relations;
- finite nonnegative measured costs;
- semantic and complete-report digest integrity;
- exclusion of raw `.coverage` databases, source/test bodies, raw output, tracebacks, absolute paths, credentials, and environment values from public artifacts;
- permanent development-only, holdout-false, primary-denominator-ineligible, non-blocking status.

## Adversaries and failure sources

The model includes:

- a substituted Coverage.py package version, artifact, source identity, or license record;
- a correctly named artifact with different bytes;
- a source distribution or platform-specific wheel silently substituted for the reviewed universal wheel;
- a package/version metadata check presented as cryptographic proof of loaded runtime bytes;
- a modified installed environment after pre-install artifact verification;
- ambient `.coveragerc`, `setup.cfg`, `tox.ini`, or `pyproject.toml` configuration changing measurement semantics;
- a Coverage.py plug-in loaded from configuration or programmatic registration;
- `COVERAGE_PROCESS_START`, `COVERAGE_RCFILE`, or another Coverage-related environment variable activating ambient collection;
- a pre-existing active Coverage.py collector;
- concurrency or subprocess measurement broadening execution scope;
- persistent SQLite `.coverage` data created, linked, retained, substituted, or published;
- a source or output path that is absolute, linked, parent-traversing, escaping, special, oversized, or stale;
- changed source or test bytes retaining old metadata;
- selector, profile, context, command, target, or receipt substitution;
- the same context copied across selectors;
- multiple contexts contaminating one selector's line or arc data;
- a measured filename outside the exact target;
- executable, executed, missing, target, arc, or branch-stat sets that are duplicated, reordered, malformed, contradictory, non-integer, negative, or substituted;
- missing branch-arc identities invented when the selected public API does not expose them;
- unavailable measurement represented as complete empty measurement;
- tool error, timeout, missing data, or context ambiguity represented as complete evidence;
- a complete preregistration-divergent result suppressed as a harness failure;
- malformed or receipt-contradictory evidence accepted merely because it is labeled unexpected;
- result summaries, profile aggregates, comparison relations, analysis, policy, or costs edited independently from selector evidence;
- negative, NaN, infinite, or silently zero missing costs;
- semantic and report digests recomputed after coordinated semantic substitution;
- raw paths, contexts, selectors, commands, digests, costs, or database bytes exposing private repository information;
- one fixed synthetic result presented as population, agent, policy, or method-superiority evidence;
- malicious tested code reading files, using the network, starting processes, exhausting resources, modifying tracing, forging visible bindings, or exploiting the host;
- malicious Coverage.py, Python, SQLite, filesystem, kernel, package manager, CI image, or dependency behavior.

## Trust boundaries

### Upstream publication and artifact acquisition

The review trusts official PyPI metadata, the exact upstream source commit and tag, the upstream license, and the upstream publication workflow as provenance inputs. Trusted Publishing and Sigstore transparency metadata are recorded. They do not authenticate the runtime after arbitrary local compromise.

The network is used only by the explicit preparation step that downloads the exact hash-locked wheel. Measurement code performs no download, upload, telemetry, or remote call.

### Package installation

The wheel filename and SHA-256 are checked before offline `--no-index --no-deps` installation. The universal pure-Python wheel is selected to avoid native build and interpreter/platform artifact variance. The source distribution is recorded but unselected.

Installation trusts `pip`, the Python environment, filesystem, and wheel processing. The current chain is integrity-bound but unsigned by DeltaWitness.

### Measurement child

Each selector runs in a separate child process and disposable directory containing only fixed source and test bytes. The child imports Coverage.py lazily, checks exact distribution and module versions, rejects ambient Coverage environment variables and an already active collector, and constructs Coverage through documented public APIs.

The child process is not a sandbox. Its separation limits state carryover but does not contain malicious code or dependencies.

### Coverage.py data model

`data_file=None` prevents persistent data-file output. Coverage.py still uses its SQLite-backed data model in memory. The runner extracts only reviewed bounded relations and discards the process and directory.

The design trusts Coverage.py's public API semantics for executable statements, measured lines, arcs, branch statistics, contexts, and query filtering. It does not inspect or publish raw database tables.

### Public result

The public result includes fixed relative paths, selector/context identities, commands, digests, exact statement and arc sets, branch statistics, runtime identity, and costs. These fields are publication metadata and require review even though the current source is project-owned synthetic material.

## Security and integrity invariants

1. The base project dependency list remains empty.
2. Coverage.py is declared only in the optional `research` extra and exact hash-locked research requirements file.
3. The selected artifact is exactly `coverage-7.15.2-py3-none-any.whl` with SHA-256 `eb6bcae8d1a9d305351ecb108232441d11c5cfe9de840a04388ba5d2db8d735c`.
4. The exact distribution manifest is semantically reconstructed and digest-verified before use.
5. The artifact verifier accepts only one bounded regular non-link file with the exact selected filename and digest.
6. Installation after artifact verification uses `--no-index --no-deps`.
7. Measurement performs no package-manager or network operation.
8. Importing the base package, provenance contract, or result verifier does not import Coverage.py.
9. Missing Coverage.py leaves the base product usable and makes direct measurement indeterminate rather than silently substituting another implementation.
10. Exact plan, catalog, mutation result, and stdlib statement result pass their authoritative verifiers before Coverage.py execution.
11. Mutation and stdlib semantic identities equal the frozen digests.
12. Source path, source digest, AST digest, symbol, target ID, and target line are exact frozen values.
13. Only the exact two profiles and three selectors execute.
14. Commands are reconstructed from fixed relations and execute without a shell.
15. Each selector receives a unique deterministic static context and invocation binding.
16. The typed outcome and Coverage.py receipt share the same binding.
17. Normal selector pass/fail requires typed receipt/process agreement for exactly one logical test.
18. A timeout retains no completed typed receipt and cannot become complete measurement.
19. Coverage.py runtime identity must be exact for complete measurement.
20. `config_file=False`, `plugins=()`, `auto_data=False`, `data_file=None`, `timid=True`, `branch=True`, `concurrency=None`, and `check_preimported=False` are fixed.
21. Ambient Coverage environment variables or a pre-existing active collector prevent complete measurement.
22. The output receipt is a bounded regular non-link strict UTF-8 JSON document with duplicate-key and non-finite-value rejection.
23. The target path is normalized, relative, contained, regular, non-link, and source-digest matched.
24. Measured files contain only the exact target relative path.
25. Complete statement evidence uses sorted unique positive executable, executed, missing, measured, and target line sets.
26. Executed is a subset of executable; missing equals executable minus executed; measured lines equal executed lines.
27. Target statement sets are exact intersections or differences against the frozen target-line set.
28. Complete arc evidence uses sorted unique integer pairs and preserves Coverage.py negative entry/exit sentinels.
29. Context arcs are a subset of all arcs; target arcs are reconstructed from arcs touching the target-line set.
30. Branch statistics use sorted unique positive source lines and finite nonnegative integer totals/taken counts with taken not exceeding total.
31. Missing branch counts are reconstructed from branch statistics.
32. Exact missing-branch arc identities remain null and labeled `unavailable-public-api`; they cannot be invented.
33. Measured contexts contain only the exact selector context.
34. Every measured line is bound exactly once to only the exact selector context.
35. Query-context lines and arcs equal the retained statement and context-arc evidence.
36. An indeterminate receipt contains a stable error code and null measurement evidence, never empty complete evidence.
37. A complete measured empty set remains distinguishable from indeterminate measurement.
38. Selector status, expected/observed concordance, statement concordance, branch completeness, context partition, and costs are derived.
39. Profile union and intersection sets are derived only from complete ordered selector records.
40. Incomplete profiles expose null aggregate sets.
41. Statement and branch discrimination compare exact profile union/intersection sets, never magnitudes.
42. Mutation discrimination is derived only from the independently verified generic-mutant table.
43. Stdlib/Coverage.py agreement, Coverage.py/mutation agreement, and incremental-signal relations are independently recomputed.
44. Complete preregistration-divergent evidence remains `unexpected`; missing or ambiguous evidence remains `indeterminate`.
45. Quality score, headline score, universal threshold, merge-blocker authorization, ecological inference, holdout selection, primary-denominator eligibility, and method-superiority claims remain null or false.
46. All process, Coverage.py wall, and Coverage.py CPU costs are finite and nonnegative, with missingness explicit.
47. Semantic digest excludes timestamps, runtime, output digests, and measured timings while retaining stable evidence and policy semantics.
48. Complete report digest binds the full public-safe report.
49. Recomputed digests cannot hide source, target, selector, command, context, receipt, statement, arc, aggregate, comparison, analysis, cost, or policy substitution because the verifier reconstructs those relations independently.
50. Editable and installed-wheel runs reproduce the frozen semantic digest on Python 3.11–3.14.
51. The optional research extra installs from a clean offline wheelhouse containing only the selected Coverage.py and built DeltaWitness wheels.
52. Uninstalling Coverage.py leaves existing base-package and stdlib-baseline smokes green.
53. Public artifacts contain no source/test bodies, raw stdout/stderr, tracebacks, raw `.coverage` bytes, absolute paths, credentials, or environment values.
54. The result remains development-only and does not authorize external execution, a holdout, release, deployment, or merge policy.

## Residual risks

### Artifact identity is not runtime attestation

Pre-install wheel hashing establishes the bytes supplied to the installer. It does not prove that Python later imports only those bytes after arbitrary filesystem or environment compromise.

### Trusted Publishing is not semantic assurance

Trusted Publishing and transparency metadata strengthen publication provenance. They do not establish absence of defects, malicious behavior, semantic suitability, or safety for this use.

### Ambient-state rejection is bounded

The child disables configuration discovery and programmatic plug-ins and rejects Coverage-prefixed environment variables and an already active collector. It cannot prove that Python startup files, site customization, import hooks, monkeypatching, filesystem overlays, or modified package bytes did not change behavior.

### In-memory SQLite is still trusted code

`data_file=None` avoids a persistent `.coverage` file but does not remove SQLite or Coverage.py data-model code from the trusted computing base.

### Public APIs can be incomplete for the research question

The selected contract records exact executed arcs and branch statistics. It does not claim exact missing-branch arc identities where the public API boundary used by the baseline does not provide them.

### Context identity is not authentication

Static contexts and invocation bindings are visible strings. They improve partition and substitution checks but do not resist malicious tested code or a compromised producer.

### Coverage is a coarse observation

Identical statement and arc sets do not imply identical assertions, input partitions, conditions, data flow, side effects, outputs, security properties, or semantic coverage.

### The frozen source has no conditional branch point

The observed arcs are entry and exit arcs for a straight-line return expression. The result is still useful as a direct baseline, but it is not evidence about branch-discrimination behavior on conditional control flow.

### One result does not calibrate a method

The exact mutation difference in this case may reflect the selected source, mutants, profiles, or checks. It cannot establish prevalence, precision, recall, adequacy, or superiority.

### Measurement cost is environment-specific

Hosted CI timings are diagnostics. They do not predict external repository cost, resource amplification, or native method performance.

### No operating-system sandbox

Fixed project-owned code is authorized because it is reviewed and synthetic. The runner would not safely contain untrusted code, a malicious dependency, filesystem access, network use, process creation, resource exhaustion, or host exploitation.

### Integrity is not authentication

All current digests are unkeyed. Coordinated replacement of the complete trusted chain can be resealed. DeltaWitness makes no signed-attestation claim.

## Safe operation

- Install Coverage.py only through the exact research-extra and hash-locked artifact path.
- Verify the wheel before offline installation.
- Keep dependency download separate from measurement.
- Execute only fixed project-owned synthetic source and tests.
- Use disposable nonsensitive environments without credentials.
- Keep configuration discovery, plug-ins, auto-start, persistent data, concurrency, and subprocess coverage disabled.
- Reject active or ambient Coverage.py state.
- Verify both typed and Coverage.py receipts and their shared binding.
- Preserve exact selector contexts and reject cross-contamination.
- Preserve missing-versus-empty and expected-versus-unexpected distinctions.
- Never invent missing-branch arc identities.
- Never infer oracle strength from statement or arc equality alone.
- Never infer mutation superiority from one incremental signal.
- Never publish raw `.coverage` data.
- Review commands, selectors, contexts, paths, digests, runtimes, and costs before export.
- Keep scores, thresholds, blockers, holdout, ecological inference, method-superiority claims, release, deployment, and external execution disabled.

## Claim boundary

A valid artifact establishes only the exact typed outcomes, statement sets, arc sets, branch statistics, contexts, profile aggregates, comparison relations, policy, and bounded costs of the fixed owned-synthetic experiment under the reviewed Coverage.py distribution and configuration.

It does not establish complete coverage, coverage adequacy, oracle strength, mutation adequacy, Coverage.py security, method superiority, external safety, ecological performance, legal admissibility, production readiness, or scientific novelty.
