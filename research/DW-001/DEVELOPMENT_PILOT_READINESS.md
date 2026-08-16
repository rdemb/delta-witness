# DW-001 Development Mechanism Pilot v1 — Readiness Boundary

**Status:** planning and pre-execution contract design only. The development pilot is not yet authorized to execute. The DW-001 protocol remains draft and unfrozen. No holdout material exists in this workstream.

## Purpose

DeltaWitness now has enough deterministic study infrastructure to stop adding assurance layers temporarily and test whether the complete evidence chain can be executed, retained, verified, and analyzed as one controlled development corpus.

The first pilot is deliberately a **mechanism pilot**, not an effectiveness study.

It asks:

> Can the current five fixed owned-synthetic families and both observer arms produce one complete, public-safe, internally consistent development bundle and machine-derived contrast analysis without manual artifact repair or post-result relabeling?

It does not ask how frequently these mechanisms occur in real coding-agent patches.

## Fixed population boundary

The executable plan must contain exactly ten ordered case-arms:

| Order | Case-arm ID | Family | Observer |
|---:|---|---|---|
| 1 | `dev-v1-valid-o0` | `valid-discriminating-regression` | `O0_EXIT_CODE` |
| 2 | `dev-v1-valid-o1` | `valid-discriminating-regression` | `O1_TYPED_RECEIPT` |
| 3 | `dev-v1-nondiscriminating-o0` | `non-discriminating-candidate-test` | `O0_EXIT_CODE` |
| 4 | `dev-v1-nondiscriminating-o1` | `non-discriminating-candidate-test` | `O1_TYPED_RECEIPT` |
| 5 | `dev-v1-candidate-regression-o0` | `candidate-regression-against-base-tests` | `O0_EXIT_CODE` |
| 6 | `dev-v1-candidate-regression-o1` | `candidate-regression-against-base-tests` | `O1_TYPED_RECEIPT` |
| 7 | `dev-v1-import-error-o0` | `wrong-reason-base-import-failure` | `O0_EXIT_CODE` |
| 8 | `dev-v1-import-error-o1` | `wrong-reason-base-import-failure` | `O1_TYPED_RECEIPT` |
| 9 | `dev-v1-unrelated-assertion-o0` | `wrong-reason-unrelated-assertion` | `O0_EXIT_CODE` |
| 10 | `dev-v1-unrelated-assertion-o1` | `wrong-reason-unrelated-assertion` | `O1_TYPED_RECEIPT` |

Every case-arm is permanently:

```text
partition = development
primary_denominator_eligible = false
```

These exact generated cases and all inspected derivatives are prohibited from any later confirmatory holdout.

## Execution authorization gate

No pilot command may execute until one strict machine-readable plan fixes:

- exact protocol and implementation commit;
- exact generator and all artifact schema commits;
- the ten ordered case-arm IDs above;
- deterministic scenario IDs;
- family, observer, control role, and partition;
- expected matrix states and failure causes;
- expected `M0`–`M3` decisions and reasons;
- exact claim-witness selector declarations where localization is required;
- explicit `localization_required` or `not_applicable` status for every arm;
- the fixed aggregate localization rule;
- artifact retention and public-safe output rules;
- cost fields, timing boundary, command-count definition, and missingness policy;
- exclusions and deviations allowed during the development pilot;
- canonical plan digest.

No runtime argument may introduce free-form fixture code, tests, commands, selectors, expected labels, or denominator decisions.

The selector table is not yet frozen by this readiness note. In particular, every family-specific selector must be verified against the fixed generated candidate-test bytes and committed in the executable plan before authorization.

## Required artifact chain

For every case-arm, the runner must construct and independently verify:

```text
pilot plan entry
    -> fixture descriptor
    -> materialized synthetic repository
    -> fixture identity
    -> development scenario manifest
    -> fixture-manifest binding
    -> strict matrix report
    -> nested M0-M3 projection
    -> claim-witness declaration, when required
    -> claim-witness localization, when required
    -> development result record
    -> public-safe pilot index entry
```

A digest-valid object is insufficient. Every existing semantic and cross-artifact verifier remains mandatory.

Aggregate analysis must not be released when one required artifact is missing, malformed, relation-invalid, or inconsistent with the plan.

## Required controlled contrasts

The machine-derived analysis must preserve at least these contrasts:

### Candidate-test discrimination

```text
non-discriminating family:
M1 versus M0
```

### Original-test preservation

```text
candidate-regression family:
M2 versus M1
```

### Outcome-semantics contrast

```text
import-error family:
O1 versus O0
```

### Broad-suite versus declared-witness localization

```text
unrelated-assertion family:
broad canonical witness versus claim-facing selector
```

### Positive control

```text
valid-discriminating family:
all methods under both observer arms
```

The analysis must retain full per-case method and selector tables. It may not replace them with one headline score.

## Cost boundary

The pilot must distinguish:

- full four-state decision-equivalence execution;
- selector-localization execution;
- artifact construction and verification;
- native state counts for any separately measured weaker method;
- human review time, or explicit unmeasured status.

Required machine fields include, where support exists:

- wall-clock seconds;
- CPU seconds;
- executed matrix states;
- executed selector states;
- command count;
- artifact count;
- public bundle byte count;
- review time or missingness reason.

NaN, infinity, negative values, and silent zero-for-missing are invalid.

Projected `M0`, `M1`, and `M2` decisions from one full matrix must not be presented as their native runtime cost.

## Analysis boundary

The ten case-arms are designed mechanism probes, not independent ecological samples.

The development pilot may establish:

- whether the complete artifact pipeline executes without manual repair;
- whether expected positive and negative controls remain distinguishable;
- whether analysis can be regenerated from retained artifacts alone;
- approximate execution and artifact-management cost in the tested environment;
- implementation defects, missing contracts, and review burden.

It may not establish:

- real-world prevalence;
- general accuracy, precision, recall, or superiority;
- statistically meaningful confidence intervals for coding-agent populations;
- a confirmatory primary endpoint;
- a holdout precision target derived as though the ten arms were random samples.

## Negative-result policy

The pilot must retain and report:

- typed import-error indeterminacy;
- non-discriminating declared selector evidence;
- broad-suite/selector disagreement;
- unexpected exclusions or deviations;
- incomplete artifacts or verifier disagreements;
- failed hypotheses and runner failures.

A known negative control becoming unexpectedly green or a positive control becoming unexpectedly incomplete is a pilot failure requiring diagnosis. It is not repaired by relabeling the expected result.

## Reproducibility boundary

Repeated execution in equivalent fresh directories must preserve:

- plan digest;
- ordered case IDs;
- fixture descriptors and identities;
- exact Git trees and commits;
- stable matrix witness semantics;
- projection, declaration, binding, localization, result, and pilot-index semantic digests where their contracts exclude volatile fields.

Timestamps, durations, and complete artifact digests may differ only where their schemas explicitly classify those fields as volatile.

This requirement does not bind the complete Python, Git, operating-system, dependency, kernel, hardware, filesystem, locale, network, or container environment.

## Safety and publication

The pilot runner remains unsandboxed and may execute repository tests repeatedly. It must run only fixed project-owned synthetic material in a disposable, non-sensitive environment without credentials or unrelated data.

The public bundle must exclude:

- absolute paths;
- raw stdout, stderr, and tracebacks;
- usernames, credentials, and environment values;
- private endpoints;
- arbitrary source or test content outside the fixed public fixtures;
- prohibited extra fields.

Git identities, relative paths, commands, test IDs, producer metadata, counts, timings, and digests remain publication metadata requiring review.

No CI artifact upload, external storage, telemetry, or network publication is authorized by this note.

## Prior-art boundary

Benchmark harnesses, experiment manifests, preregistration, reproducible research bundles, SWE-bench and TDD-Bench evaluation pipelines, structured test reports, content-addressed artifacts, and study-data lineage are established.

No novelty claim is made for executing a benchmark plan or indexing a result bundle.

The narrow question is whether DeltaWitness can apply its complete multi-artifact evidence chain to controlled positive and negative mechanisms without hidden state, post-hoc relabeling, manual artifact repair, or denominator drift.

## Readiness decision

The development mechanism pilot is **not authorized** by this document alone.

Authorization requires all of the following on one reviewed branch:

- strict plan and index schemas;
- semantic plan verifier;
- exact committed ten-arm plan;
- red-first runner and analysis contracts;
- public-tree, compile, full-suite, demo, wheel, installed-package, privacy, and threat-boundary validation;
- no unresolved review comments;
- an explicit PR statement that the execution remains development-only and non-confirmatory.

## Claim boundary

Completion of the future pilot would establish only that the fixed owned-synthetic development mechanism plan executed and produced an internally consistent, public-safe, reproducible artifact bundle and analysis.

It would not establish real-world effectiveness, superiority, oracle adequacy, protocol freeze, confirmatory holdout readiness, independent reproduction, producer authentication, containment, production readiness, scientific novelty, or award-level significance.
