# DW-001 Ecological Development Corpus Protocol

**Status:** DRAFT DESIGN ONLY — NO DATASET RELEASE PINNED — NO CORPUS EXECUTION AUTHORIZED — NO HOLDOUT SELECTED OR INSPECTED.

**Design identifier:** `DW-001-ECOLOGICAL-DESIGN-V1`.

**Reviewed DeltaWitness baseline:** `6dada3bdde890eafe287cf6abdae76aaf7940cbb`.

This document defines the decisions that must be fixed before DeltaWitness may execute an authorized ecological development corpus. It is not a preregistration, corpus manifest, containment approval, or holdout commitment.

## 1. Evidence gap

The completed five-family / ten-arm owned-synthetic pilot established:

- complete artifact-chain feasibility;
- expected controlled state-set contrasts;
- one observer-dependent import-error contrast;
- one declared-witness mismatch control;
- stable synthetic semantic index and canonical archive retention.

It did not establish:

- prevalence of any failure mechanism;
- applicability on real repositories;
- paired effectiveness of `M3` over `M2`;
- over-refusal on valid patches;
- observer or localization accuracy on ecological instances;
- environment-reconstruction or containment feasibility;
- realistic execution and review cost;
- generalization beyond the exact synthetic population.

An ecological design is therefore the next evidence prerequisite. Adding another assurance layer would not resolve this gap.

## 2. Candidate research question

> On an authorized and explicitly bounded ecological development frame, what are the applicability, paired decision differences, failure-cause outcomes, declared-witness outcomes, and execution/review costs of `M0` through `M3` under controlled observer semantics?

This question remains provisional until the target population, accessible frame, ground truth, and feasible containment boundary are accepted.

## 3. Candidate target population

Initial wording under review:

> Python issue-resolution changes in public or explicitly authorized repositories where an implementation change and associated test evidence can be reconstructed from immutable Git objects, executed in an accepted disposable environment, and independently reviewed for issue scope and state applicability.

This is not yet an accepted population. It excludes, unless separately added:

- languages without a typed observer and deterministic fixture boundary;
- tasks requiring uncontrolled network or private services;
- changes without lawful and reproducible artifact access;
- patches whose base/head or test provenance cannot be fixed;
- repositories that cannot be executed under the accepted containment policy;
- issue types whose hybrid states cannot be reviewed meaningfully.

## 4. Accessible source universe

The initial machine-readable source universe contains only two candidate source classes:

```text
SWE-bench
TDD-Bench Verified
```

Both remain:

```text
dataset_reference_status       = unpinned
authorization_review_status    = pending
containment_status             = unaccepted
execution_authorized           = false
```

The source universe is documented in `ECOLOGICAL_SOURCE_UNIVERSE.md`. No candidate is an accepted sampling frame.

## 5. Unit of analysis

One candidate ecological unit should bind:

- source universe and immutable dataset release;
- immutable source-instance ID;
- underlying repository identity and license review;
- exact base and candidate commits, or deterministic patch application identity;
- issue/claim text and interpretation boundary;
- code, test, documentation, dependency, generated-input, and execution-sensitive path categories;
- source `FAIL_TO_PASS`, `PASS_TO_PASS`, or equivalent test metadata;
- declared witness-test selectors or explicit absence;
- environment/container identity and dependency reconstruction;
- patch/test authorship and transformation provenance where known;
- pre-execution state applicability;
- reviewer labels and disagreement records;
- exclusion, deviation, privacy, and publication status.

Near-duplicate issue, patch, test, and repository lineages require explicit relation identifiers. They cannot silently enter multiple partitions.

## 6. Sampling alternatives under review

No sampling method is selected in v1. The design review must compare:

1. stratified probability sampling from one immutable benchmark frame;
2. repository-clustered sampling;
3. two-stage outcome-blinded eligibility screening followed by stratified sampling;
4. purposive maximum-variation development sampling with explicitly non-probabilistic inference.

Potential strata or covariates include:

- benchmark source;
- repository;
- issue category;
- patch size and changed-path count;
- code-only versus code-and-test co-change;
- test framework;
- agent versus human provenance where known;
- dependency or generated-code involvement;
- security-sensitive versus ordinary functionality;
- expected hybrid-state feasibility.

The frozen design must state whether its estimates concern only the named benchmark population or a broader target population. Sample size cannot repair a convenience sample.

## 7. Eligibility before outcomes

Inclusion and exclusion rules must be fixed before DeltaWitness outcomes are visible.

Candidate inclusion requirements:

- immutable source and repository identity;
- reviewed license and execution authorization;
- accepted containment/environment reconstruction;
- supported language and observer adapter;
- exact, non-overlapping path classification;
- reproducible base and candidate states;
- independently interpretable issue scope;
- reviewable state applicability;
- no unresolved disclosure, privacy, secret, or legal blocker.

Every exclusion retains:

- source instance ID;
- stable reason code;
- decision and reviewer references;
- outcome-visibility status;
- denominator effect;
- date and protocol version.

An outcome-visible exclusion cannot silently preserve confirmatory eligibility.

## 8. Ground truth

Ground truth is not derived from DeltaWitness decisions.

Required dimensions should include:

- patch validity within issue scope;
- false-assurance mechanism or `none` / `ambiguous` / `unknown`;
- state applicability;
- expected state outcomes and failure-cause class;
- claim-facing test identity or absence;
- declared-test relevance with uncertainty;
- original-test regression significance;
- license, authorization, and publication status.

The design must preserve `unknown` and disagreement. It must not force binary labels where reviewers cannot distinguish intent or relevance.

## 9. Reviewer protocol

Before ecological execution:

1. reviewer instructions and examples are versioned;
2. initial reviewers are blinded to DeltaWitness method and localization outputs;
3. at least two genuinely independent reviewers label a calibration subset;
4. initial labels are retained before adjudication;
5. raw agreement, missingness, and a preselected scale-appropriate agreement statistic are reported;
6. adjudication rules and adjudicator conflicts are fixed;
7. authorship, implementation, repository, and benchmark conflicts are disclosed;
8. deterministic synthetic metadata is never counted as independent human review.

If genuine independent review is unavailable, the result remains exploratory and cannot establish frozen holdout labels.

## 10. Methods and controlled factors

Nested methods remain:

```text
M0_FINAL      = CC
M1_F2P        = BC + CC
M2_F2P_P2P    = BC + CB + CC
M3_FOUR_STATE = BB + BC + CB + CC
```

Observer arms remain separate:

```text
O0_EXIT_CODE
O1_TYPED_RECEIPT
```

Declared logical-test localization remains a separate factor. A localized selector transition does not become part of the definition of `M3`.

The design must fix:

- whether every instance runs both observers;
- observer execution order or counterbalancing;
- localization availability and required adapter;
- handling of mixed frameworks;
- timeout and repetition policy;
- whether influence analysis is excluded from primary outcomes;
- how adapter-unavailable and invalid-hybrid cases enter denominators.

## 11. Applicability and incomplete evidence

Runtime failure cannot create `not_applicable`.

Pre-execution review classifies each state as:

- applicable;
- not applicable for a recorded semantic reason;
- uncertain under a predefined safe resolution procedure.

The study must retain:

- all-instance applicability;
- method-specific applicability;
- invalid-hybrid rate;
- indeterminate rate and cause;
- environment-reconstruction exclusions;
- associations with source, repository, patch, framework, and path structure.

A high non-applicability rate is a primary result, not a nuisance to remove after execution.

## 12. Candidate outcomes

### Paired method outcomes

Retain all four decisions:

```text
accept
reject
indeterminate
not_applicable
```

Report paired case tables for:

```text
M1 - M0
M2 - M1
M3 - M2
O1 - O0
localization available - localization unavailable
```

No single accuracy score may replace these flows.

### Candidate primary estimand

Under review:

```text
unsafe acceptance(M2) - unsafe acceptance(M3)
```

A companion valid-patch estimand is required to expose over-refusal. Neither is accepted until labels and feasible sampling are defined.

### Failure-cause outcomes

Score only the classes actually emitted by the adapter against independently fixed labels. Generic `test_error` must not be scored as an import/setup/dependency subtype.

## 13. Cost protocol

Separate:

1. full-matrix decision-equivalence execution;
2. native execution of only the states required by each method.

Record:

- environment build time;
- wall-clock and CPU time;
- state and command counts;
- repetition and retry counts;
- peak memory and storage where available;
- public/private artifact bytes;
- eligibility review time;
- ground-truth review time;
- adjudication time;
- result-review time;
- explicit missingness.

A full matrix projected to `M0` is not native `M0` cost.

## 14. Uncertainty and precision

Before execution, fix:

- primary estimand;
- analysis population;
- interval method;
- repository/issue clustering treatment;
- indeterminate, excluded, and not-applicable handling;
- multiplicity policy;
- minimally meaningful paired difference or target interval width;
- sample-size calculation or simulation;
- stopping and maximum-expansion rules;
- whether sequential inspection is prohibited or preregistered.

Rare unsafe-acceptance events require event counts and exact uncertainty, not only asymptotic percentages.

Development feasibility data may inform assumptions. Held-out outcomes may not.

## 15. Development and holdout separation

At least three disjoint sets are required:

```text
method-development / calibration
protocol pilot
committed holdout
```

Requirements:

- repository or issue-lineage grouping where leakage is plausible;
- inspected development cases never enter holdout;
- immutable IDs and source digests;
- frozen protocols, adapters, environments, metrics, exclusions, and adjudication before holdout unblinding;
- public or independently timestamped holdout membership commitment;
- permanent retention of deviations without rewriting the commitment.

This protocol version selects and inspects no holdout.

## 16. Containment prerequisite

The current runner is not a sandbox. No ecological code may execute until a containment profile is accepted.

Minimum design questions:

- disposable image identity;
- no host credentials or unrelated data;
- network default-deny or explicitly modeled endpoints;
- CPU, memory, process, storage, and wall-clock limits;
- writable filesystem scope;
- artifact export allowlist;
- dependency and image provenance;
- cleanup and external side-effect review;
- malicious test-code behavior.

A public benchmark is not trusted code merely because its metadata is public.

## 17. Freeze prerequisites

Before any ecological development run:

- [ ] immutable dataset release and digest;
- [ ] source/instance license and authorization table;
- [ ] accepted target population and sampling frame;
- [ ] unit-of-analysis schema;
- [ ] deduplication and clustering rules;
- [ ] fixed eligibility and exclusion policy;
- [ ] reviewer handbook, forms, and adjudication protocol;
- [ ] accepted containment/environment profile;
- [ ] fixed method, observer, localization, timeout, and repetition rules;
- [ ] fixed metrics and denominators;
- [ ] cost protocol;
- [ ] precision/sample-size analysis;
- [ ] development/holdout split and commitment procedure;
- [ ] privacy, disclosure, and publication review;
- [ ] exact protocol, implementation, adapter, schema, and image commits.

All boxes remain open in this draft.

## 18. Falsification and narrowing

Narrow or stop the study if:

- the source frame supports inference only to a named benchmark subset;
- license or authorization cannot be established;
- containment or environment failure dominates;
- reviewer agreement is inadequate and uncertainty cannot be represented honestly;
- `M3` is rarely applicable;
- `M3` adds little paired detection beyond `M2`;
- typed observation adds little correct cause separation or unacceptable indeterminacy;
- localization adds no evidence beyond simpler targeted commands;
- over-refusal or cost is operationally unacceptable;
- results are unstable under harmless environment changes;
- sampling or labels require outcome-visible repair;
- a direct baseline provides the same evidence more rigorously or simply.

Negative findings are valid results.

## 19. Claim boundary

This draft establishes only a set of decisions and blockers that must be resolved before ecological development execution.

It does not establish a representative corpus, authorized execution, accepted containment, independent ground truth, a precision target, a holdout, empirical effectiveness, superiority, protocol freeze, independent reproduction, production readiness, scientific novelty, or award-level significance.
