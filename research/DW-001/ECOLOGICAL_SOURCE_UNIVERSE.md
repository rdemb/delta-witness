# DW-001 Ecological Source Universe

**Status:** initial design-only source screening. No dataset release is pinned, no instance is selected, no execution is authorized, and no holdout exists.

Machine-verifiable artifact:

```text
research/DW-001/ecological-source-universe.v1.json
```

Structural schema:

```text
research/DW-001/schema/ecological-source-universe.schema.json
```

Semantic implementation:

```text
src/deltawitness/dw001_ecological.py
```

## Purpose

The completed owned-synthetic development mechanism pilot establishes that the DeltaWitness artifact chain works for five fixtures designed by this project. It does not define a population from which effectiveness, applicability, or cost can be inferred.

The ecological source universe is the first fail-closed boundary between that mechanism pilot and any future execution on real repositories.

A candidate source record means only:

> This benchmark family is sufficiently relevant to merit deeper license, authorization, sampling, environment, containment, and bias review.

It does not mean:

- the dataset is immutable;
- its instances are licensed uniformly;
- historical repository code may be executed safely or lawfully;
- the benchmark represents coding-agent patches generally;
- the benchmark supplies the ground truth DW-001 needs;
- an instance may enter development, pilot, or holdout sets.

## Root invariants

The initial universe fixes:

```text
status                = design_only
execution_authorized  = false
holdout_selected      = false
holdout_inspected     = false
```

Its decision record additionally fixes:

```text
candidate_sources_only                = true
target_population_status              = unfrozen
sampling_frame_status                 = unfrozen
unit_of_analysis_status               = unfrozen
license_and_authorization_status      = pending
review_protocol_status                = unfrozen
containment_required                   = true
containment_status                     = unaccepted
precision_target_status               = unfrozen
development_holdout_split_status      = unfrozen
no_ecological_execution               = true
no_holdout_selection                   = true
no_holdout_inspection                  = true
```

The semantic verifier reconstructs the complete artifact from the reviewed DeltaWitness `main` SHA and fixed source records. Recomputing `universe_sha256` cannot authorize execution, freeze sampling, select a holdout, or remove a blocker.

## Candidate 1: SWE-bench

Pinned implementation-repository review point:

```text
repository             = SWE-bench/SWE-bench
repository_commit_sha  = ca6e4e0d252f32f8762625b73575d5dee49d0a5a
repository_license     = MIT
paper                   = arXiv:2310.06770
```

Relevant artifact classes include issue text, repository identity, base commit, gold patch, test patch, `FAIL_TO_PASS`, `PASS_TO_PASS`, and environment metadata.

### Potential value

SWE-bench supplies real GitHub issue-resolution instances with exact repository context and widely used fail-to-pass / pass-to-pass evaluation semantics. It is a direct baseline family for testing whether `BB` and full matrix consistency add evidence beyond `BC + CB + CC`.

### Unresolved boundaries

The MIT license above is the license of the benchmark implementation repository. It is not treated as proof that every underlying project, issue, patch, test body, container artifact, or redistributed dataset field has identical publication or execution rights.

Before any instance can be considered:

- pin one immutable dataset release and digest;
- review the license and provenance of every selected underlying repository instance;
- define the authorization basis for executing historical project code and tests;
- accept a containment profile;
- define environment reconstruction and network behavior;
- preserve repository and issue-lineage clustering;
- assess benchmark contamination, issue-selection, language, and solvability filtering.

## Candidate 2: TDD-Bench Verified

Pinned implementation-repository review point:

```text
repository             = IBM/TDD-Bench-Verified
repository_commit_sha  = 3df8be066e486789d0b8e0d2865a3a4422b4560f
repository_license     = Apache-2.0
paper                   = arXiv:2412.02883
```

Relevant artifact classes include issue text, repository/base identity, gold patch, generated or gold test patch, fail-to-pass evidence, isolated relevant-test execution, and change-coverage metadata.

### Potential value

TDD-Bench Verified is closer to the declared-test question: it studies tests generated before issue resolution, uses human/harness filtering, and includes isolated relevant-test and coverage-oriented evidence. It may provide a useful baseline for declared logical-test localization.

### Unresolved boundaries

The Apache-2.0 license above is the benchmark implementation-repository license, not a blanket authorization for every underlying project instance or generated test artifact.

Before any instance can be considered:

- pin one immutable dataset artifact and digest;
- review every underlying project license and execution authorization;
- distinguish human-authored, generated, transformed, and uncertain test provenance;
- map isolated relevant-test semantics to DW-001 claims without post-outcome relabeling;
- accept containment and environment reconstruction;
- determine whether inference concerns test generation, patch verification, or only the named benchmark population;
- account for human verification and inclusion filtering.

## Why repository commits are retained now

The source records pin the exact benchmark code/docs reviewed while designing the universe. They do **not** pin a dataset release.

This separation is intentional:

```text
benchmark implementation commit
    != immutable dataset manifest
    != selected sampling frame
    != execution authorization
```

A future update must add a new versioned source artifact rather than silently reinterpret these repository commits as dataset identities.

## Bias and clustering boundary

Both candidates are curated benchmarks, not probability samples of all coding-agent patches. Expected biases include:

- repository and issue inclusion rules;
- language and framework composition;
- solvability and environment-reconstruction filters;
- human gold-patch and test provenance;
- benchmark contamination and memorization;
- source-specific harness behavior;
- correlated instances from the same repository or issue lineage;
- availability bias toward successful, public, reproducible issue histories.

These biases must shape the target-population wording and uncertainty analysis. More instances do not repair an undefined sampling frame.

## Execution boundary

No source record in v1 may be passed to the DeltaWitness runner.

Execution requires, at minimum:

1. immutable dataset and instance identity;
2. instance-level license and authorization review;
3. accepted sampling and deduplication rules;
4. accepted reviewer and ground-truth protocol;
5. accepted containment and environment profile;
6. development-only partition assignment;
7. privacy and disclosure review;
8. a separately approved execution artifact or protocol version.

Public availability is not an execution capability.

## Holdout boundary

No holdout member, manifest, digest, selector, or label is present in the source universe.

The universe may support later sampling-frame design. It must not be used to:

- inspect candidate holdout outcomes;
- select easy or favorable instances after method results are visible;
- move development cases into a holdout;
- imply that source order is randomized sampling;
- treat an unresolved candidate source as committed study material.

## Claim boundary

The v1 artifact establishes only that two initial benchmark families and their unresolved blockers are represented deterministically against one exact DeltaWitness `main` revision.

It does not establish authorization, immutable datasets, sampling validity, environment feasibility, reviewer availability, containment, effectiveness, superiority, protocol freeze, holdout readiness, independent reproduction, production readiness, scientific novelty, or award-level significance.
