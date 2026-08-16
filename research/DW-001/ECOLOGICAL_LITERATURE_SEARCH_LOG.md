# DW-001 Ecological Corpus Literature Search Log

**Status:** reproducible initial search for corpus-design and direct-baseline planning. It does not establish completeness or scientific novelty.

**Search date:** 2026-08-16.

**Reviewed DeltaWitness main:** `6dada3bdde890eafe287cf6abdae76aaf7940cbb`.

## Search objectives

The search was scoped to five questions:

1. What direct benchmark baselines expose fail-to-pass and pass-to-pass evidence for real issue-resolution tasks?
2. What benchmark source may support declared-test localization or coverage-oriented comparison?
3. What sampling and empirical-software-engineering guidance is required before ecological inference?
4. What reviewer-agreement controls are appropriate for qualitative or categorical software-engineering labels?
5. What prior art already covers oracle adequacy, mutation testing, and failure-inducing input isolation?

## Search channels

Initial discovery used:

- arXiv title/identifier search;
- official benchmark repositories and documentation;
- ACM SIGSOFT Empirical Standards material;
- DOI and publisher metadata;
- reference chaining from the current DW-001 evidence-gap and baseline documents.

Repository source review used immutable Git commits rather than moving repository descriptions wherever possible.

## Queries

Representative queries:

```text
TDD-Bench Verified arXiv 2412.02883
SWE-bench FAIL_TO_PASS PASS_TO_PASS documentation
sampling in software engineering research critical review guidelines DOI
Empirical Standards for Software Engineering Research
inter-rater reliability agreement software engineering DOI
oracle problem software testing survey DOI
mutation testing survey DOI
failure-inducing input delta debugging DOI
```

The log does not claim that these strings exhaust terminology such as patch validation, test adequacy, causal testing, regression-test selection, benchmark curation, or agent evaluation.

## Direct benchmark baselines

### SWE-bench

Reference:

```text
Jimenez et al.
SWE-bench: Can Language Models Resolve Real-World GitHub Issues?
arXiv:2310.06770
ICLR 2024
```

Reviewed implementation repository:

```text
SWE-bench/SWE-bench
commit ca6e4e0d252f32f8762625b73575d5dee49d0a5a
repository license: MIT
```

Relevant evidence:

- real GitHub issue-resolution tasks;
- repository and base-commit identities;
- gold patch and test patch;
- `FAIL_TO_PASS` and `PASS_TO_PASS` test sets;
- environment/container metadata.

Direct-baseline role:

```text
FAIL_TO_PASS  ~ candidate-test discrimination baseline
PASS_TO_PASS  ~ original-test preservation baseline
```

Open questions:

- dataset release and instance manifest are not yet pinned;
- repository-level MIT license is not treated as every underlying project's license;
- source selection and environment reconstruction may induce substantial attrition;
- benchmark tasks are clustered by repository and curated for solvability;
- gold-patch evaluation is not identical to evaluating arbitrary agent-authored code-and-test co-changes.

### TDD-Bench Verified

Reference:

```text
Ahmed et al.
TDD-Bench Verified: Can LLMs Generate Tests for Issues Before They Get Resolved?
arXiv:2412.02883
```

Reviewed implementation repository:

```text
IBM/TDD-Bench-Verified
commit 3df8be066e486789d0b8e0d2865a3a4422b4560f
repository license: Apache-2.0
```

Relevant evidence:

- test generation before issue resolution;
- fail-to-pass evaluation;
- human and harness verification;
- isolated relevant-test execution;
- change-coverage-oriented metadata.

Direct-baseline role:

- candidate source for declared logical-test localization comparison;
- candidate source for testing whether isolated relevant-test evidence changes suite-level conclusions;
- benchmark for separating test-generation inference from patch-verification inference.

Open questions:

- dataset artifact and instance licenses are not pinned or reviewed;
- generated, human, transformed, and gold test provenance must remain separate;
- human verification creates useful quality control and selection bias simultaneously;
- coverage and relevant-test harness semantics must not be silently reinterpreted as DW-001 claim relevance.

## Sampling and empirical design

### Sampling guidance

Reference:

```text
Baltes and Ralph
Sampling in Software Engineering Research: A Critical Review and Guidelines
Empirical Software Engineering
DOI: 10.1007/s10664-021-10072-8
```

Design implications:

- distinguish target population, accessible frame, sample, and observed result set;
- report coverage error and selection bias;
- do not describe convenience or purposive samples as representative probability samples;
- preserve repository/issue clustering and duplicate lineage;
- align inference wording with the actual sampling process.

### Empirical standards

Reference:

```text
Ralph et al.
Empirical Standards for Software Engineering Research
arXiv:2010.03525
ACM SIGSOFT Empirical Standards repository
```

Design implications:

- select standards by study method rather than apply one generic checklist;
- define constructs, sampling, measurement, uncertainty, and limitations explicitly;
- retain negative results and deviations;
- make data and analysis provenance reviewable where license and privacy allow.

## Human review and agreement

Reference:

```text
Díaz et al.
Applying Inter-Rater Reliability and Agreement in collaborative Grounded Theory studies in software engineering
Journal of Systems and Software
DOI: 10.1016/j.jss.2022.111520
```

Design implications:

- raw agreement and scale-appropriate reliability/agreement statistics answer different questions;
- independent initial labels should be retained before adjudication;
- missingness, ambiguous labels, reviewer training, and disagreement should not disappear into consensus;
- the statistic must be selected after the label scale and review process are defined, not because one coefficient is conventional.

This paper addresses a qualitative coding context and is not automatically the correct statistic for every DW-001 label. The protocol must justify the chosen measure.

## Oracle and test-adequacy boundary

### Oracle problem

Reference:

```text
Barr, Harman, McMinn, Shahbaz, and Yoo
The Oracle Problem in Software Testing: A Survey
IEEE Transactions on Software Engineering
DOI: 10.1109/TSE.2014.2372785
```

Boundary:

- test execution and assertion failure do not establish that the oracle captures intended behavior;
- automated and partial oracles have explicit scope and error modes;
- DW-001 declared-test localization must remain narrower than semantic oracle adequacy.

### Mutation testing

Reference:

```text
Jia and Harman
An Analysis and Survey of the Development of Mutation Testing
IEEE Transactions on Software Engineering
DOI: 10.1109/TSE.2010.62
```

Boundary:

- mutation testing is established as an oracle/test-strength technique;
- adding future mutation evidence to DeltaWitness would be a separate measurement layer;
- a mutation score must not be substituted for issue-specific relevance or full correctness.

### Failure isolation

Reference:

```text
Zeller and Hildebrandt
Simplifying and Isolating Failure-Inducing Input
IEEE Transactions on Software Engineering
DOI: 10.1109/32.988498
```

Boundary:

- delta debugging and failure isolation are established;
- exact DeltaWitness path coalitions and future test-event localization must be compared with simpler minimization or targeted-execution baselines;
- failure-inducing input isolation does not itself establish desirable behavior or oracle adequacy.

## Preliminary decisions

The initial search supports these design decisions:

1. SWE-bench and TDD-Bench Verified are candidate source classes, not accepted corpora.
2. Repository implementation commits can be pinned now, but dataset releases and instance manifests remain unpinned.
3. Repository license does not authorize every underlying instance automatically.
4. Sampling-frame and inference wording must be fixed before execution.
5. Reviewer labels require independent initial review, retained disagreement, and a preselected agreement analysis.
6. `M0`–`M3`, observer arms, and declared-test localization remain separate factors.
7. Oracle adequacy and mutation strength remain future independent layers.
8. No ecological repository may execute before containment is accepted.

## Unresolved searches

Before protocol freeze, extend the search to:

- regression-test selection and test-impact analysis;
- benchmark contamination and memorization;
- benchmark instance licensing and redistribution;
- containerized evaluation threat models;
- clustered paired-outcome analysis;
- rare-event precision and sample-size simulation;
- human benchmark verification and adjudication;
- real coding-agent patch rejection and weak-oracle datasets;
- direct systems that combine code/test counterfactuals, typed outcomes, and integrity-bound evidence.

## Claim boundary

This log records an initial reproducible search and provisional design implications. It does not establish exhaustive prior-art coverage, source authorization, accepted sampling, a complete review protocol, a precision target, scientific novelty, or empirical effectiveness.
