# DW-001 Coverage.py Direct Baseline Result v1

## Status

This document records one development-only direct-baseline result over the exact project-owned synthetic source, target, selectors, stdlib statement result, and mutation result frozen before Coverage.py execution.

The result is not ecological evidence. It is not eligible for a primary denominator, score, threshold, merge blocker, holdout claim, production claim, method-superiority claim, or novelty claim.

## 1. Frozen inputs

```text
plan_sha256:
  0ebf64e1de76849050c86d8a4d53d72d8067561ab48b4bd5a4083495dc99fe37
catalog_sha256:
  7b3e405bd3893f532c0ccfa16e9cc208422bbdd20dfe82a002c99342a04201c0
mutation_result_semantic_sha256:
  9e101bca85fd630bf5bdb2a6030d9fdab93eb3eac54b03f4aab99012c28086b6
stdlib_statement_result_semantic_sha256:
  353e887ccb43561f1a0749e7948dd40bd7019534e93b5dca5b11ea16d49f68c6
source_id:
  authorization-predicate-candidate-v1
source_path:
  src/access.py
source_sha256:
  7bfbd2d0a642c6d7f7da05ece2f4464d31df53a28d1ffed12c5752bc492d8965
target_id:
  3cdfc367a78a09b257147fb236e80785d936177da231924f43e2d3d5fbd80e2e
target_symbol:
  is_admin
target_lines:
  [2]
```

Frozen selector profiles:

```text
strong-authorization-oracle-v1:
  - test_access.AccessTests.test_admin_is_allowed
  - test_access.AccessTests.test_viewer_is_denied

weak-boolean-proxy-v1:
  - test_access.AccessTests.test_viewer_result_is_boolean
```

No source, test, target, selector, profile, expected signature, comparison hypothesis, or mutation evidence was changed after Coverage.py output became visible.

## 2. Direct baseline identity

```text
package:
  coverage
version:
  7.15.2
selected_artifact:
  coverage-7.15.2-py3-none-any.whl
selected_artifact_sha256:
  eb6bcae8d1a9d305351ecb108232441d11c5cfe9de840a04388ba5d2db8d735c
distribution_manifest_sha256:
  28f6430e45fcfda973a1fcd57157e2317f096cc2774e8281244eaf18a9d0dd3f
upstream_source_commit:
  coveragepy/coveragepy@50d865908dfeb21a0bf1e6f05db578c11662f8dd
license:
  Apache-2.0
scope:
  research-extra-only
```

The issue-nominated source distribution was verified as provenance evidence but was not selected for execution. The exact selected wheel and dependency decision are documented in `COVERAGEPY_DEPENDENCY_PROVENANCE_V1.md`.

## 3. Fixed measurement configuration

Each selector executed in its own disposable directory and child process using only fixed project-owned source and test bytes.

```text
data_file:
  null
auto_data:
  false
timid:
  true
branch:
  true
config_file:
  false
source_dirs:
  [src]
concurrency:
  null
check_preimported:
  false
context_strategy:
  static-selector-context-v1
messages:
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

Every selector had a unique exact context identity of the form:

```text
dw001-coveragepy-v1:<profile_id>:<selector>
```

The typed unittest receipt and Coverage.py receipt shared one independently reconstructed invocation binding.

## 4. Observed selector evidence

All three frozen selectors produced typed `pass` outcomes with exactly one logical test and complete Coverage.py evidence.

For every selector:

```text
executable statements:
  [1, 2]
executed statements:
  [2]
missing statements:
  [1]
target executable:
  [2]
target executed:
  [2]
target missing:
  []
all arcs:
  [[-1, 2], [2, -1]]
context arcs:
  [[-1, 2], [2, -1]]
target arcs:
  [[-1, 2], [2, -1]]
branch stats:
  []
missing branch count:
  0
missing branch arc identities:
  unavailable through the selected public-API contract
measured contexts:
  [the exact selector context]
context partition valid:
  true
```

Coverage.py line `1` is executable static source according to `analysis2`, but it was not executed during measurement because the test suite loader imported the fixed module before the explicit collector started. Line `2` is the declared target and was executed by every selector.

Negative arc endpoints are Coverage.py entry/exit sentinels. This result stores their exact observed identities; it does not reinterpret them as source lines.

## 5. Profile aggregates

```text
strong statement union:
  [2]
strong statement intersection:
  [2]
weak statement union:
  [2]
weak statement intersection:
  [2]

strong arc union:
  [[-1, 2], [2, -1]]
strong arc intersection:
  [[-1, 2], [2, -1]]
weak arc union:
  [[-1, 2], [2, -1]]
weak arc intersection:
  [[-1, 2], [2, -1]]
```

Both context partitions were complete and uncontaminated. Aggregate sets were reconstructed from complete ordered selector records. Hit-count or execution-magnitude comparisons were not used.

## 6. Predeclared comparison result

| Relation | Observed |
|---|---:|
| `stdlib_statement_discriminates_profiles` | `false` |
| `coveragepy_statement_discriminates_profiles` | `false` |
| `coveragepy_branch_discriminates_profiles` | `false` |
| `mutation_discriminates_profiles` | `true` |
| `stdlib_and_coveragepy_statement_agree` | `true` |
| `coveragepy_branch_and_mutation_agree` | `false` |
| `incremental_branch_signal_observed` | `false` |
| `incremental_mutation_signal_beyond_coveragepy_observed` | `true` |

All eight observed relations matched the preregistration, so the result-level analysis status is `expected`.

This means only that, in this exact frozen synthetic case, the selected Coverage.py statement and arc-set evidence did not distinguish the two profiles while the previously frozen generic-mutation table did.

## 7. Frozen artifact identities

```text
coveragepy_result_semantic_sha256:
  ec0c2fdd5ac24ba53eb895d9014aab623d2631125b8512ba0e0cbf5105f21ee8
coveragepy_result_report_sha256:
  8b248757374ebff4195bad181ad02bc5b0bfc61fa2e21ebf45549686c33d2c41
```

Frozen public-safe report:

```text
research/DW-001/coveragepy-baseline-result.v1.json
```

The semantic digest excludes timestamps, runtime identity, output digests, and measured timing values while retaining source, selector, typed receipt, Coverage.py distribution, configuration, statement, arc, context, profile, comparison, analysis, and policy relations. The complete report digest additionally binds the frozen runtime and cost diagnostics.

## 8. Measured costs

The frozen Python 3.11 CI report recorded:

```text
selector commands:
  3
process wall-clock total:
  0.493240 seconds
Coverage.py wall-clock total:
  0.163706 seconds
Coverage.py CPU total:
  0.163704 seconds
```

These values are diagnostics for one hosted CI run. They are not performance guarantees, cross-tool benchmarks, native stdlib/mutation cost comparisons, resource bounds for external repositories, or population estimates.

## 9. Reproduction evidence

The exact semantic digest was reproduced under:

- Python 3.11;
- Python 3.12;
- Python 3.13;
- Python 3.14;
- editable DeltaWitness installation;
- force-reinstalled DeltaWitness base wheel;
- the optional `research` extra installed from a clean offline wheelhouse.

The CI path also uninstalled Coverage.py and reran the existing stdlib statement baseline, confirming that the base product remains dependency-free and functional without the optional package.

## 10. Negative-result and verifier behavior

The contract retains:

- complete preregistration-divergent evidence as `unexpected`;
- missing optional dependency, tool error, timeout, missing data, or context ambiguity as `indeterminate`;
- a complete measured empty set separately from unavailable measurement.

The verifier independently reconstructs and checks:

- package and artifact provenance;
- source, target, selector, test, command, context, and invocation identity;
- typed outcome receipt/process agreement;
- Coverage.py receipt structure and digest;
- statement and arc sets;
- context-to-line and context-to-arc partitions;
- profile union and intersection sets;
- stdlib, Coverage.py, and mutation comparison relations;
- expected/observed concordance;
- policy and finite nonnegative costs;
- semantic and complete-report digests.

Adversarial regressions cover producer, version, artifact, source, test, selector/context, context-contamination, statement, arc, aggregate, comparison, missing-versus-empty, digest-recomputation, duplicate-key, symbolic-link, absolute-path, wrong-type, extra-field, negative, NaN, and infinite-cost substitutions.

## 11. Limitations

- One project-owned synthetic source and three selectors are not a population.
- Statement and arc equality does not establish equal assertions, data flow, conditions, side effects, or semantic coverage.
- Arc sets for this straight-line function contain entry and exit only; no conditional branch point exists in the frozen source.
- The selected public API exposes aggregate missing-branch counts through branch statistics, but this contract does not claim exact missing-branch arc identities when they are unavailable through that API boundary.
- Static contexts identify the exact selector measurement process, but unsigned receipts and visible bindings are not attestations.
- Coverage.py and `sys.settrace` are observation mechanisms, not containment.
- Fixed owned-synthetic success does not authorize external repository execution.
- A surviving or killed mutation table is not complete oracle-strength evidence.
- Internal consistency and reproducibility do not establish ecological validity or scientific novelty.

## 12. Claim boundary

The result supports only this bounded statement:

> For one exact project-owned synthetic authorization predicate, the two frozen selector profiles produced identical target statement sets and identical target-related Coverage.py arc sets under exact static selector contexts, while the already frozen generic-mutation table distinguished the profiles.

It does not support any claim that:

- coverage is generally insufficient;
- Coverage.py is weak or unsuitable;
- mutation testing is generally better or sufficient;
- the mutation table captures complete oracle strength;
- branch coverage cannot distinguish meaningful test suites;
- the method is ready to block merges;
- DeltaWitness works on real coding agents or external repositories;
- Gate 0 or Gate 1 has been completed;
- the project is production-ready;
- scientific novelty has been established.
