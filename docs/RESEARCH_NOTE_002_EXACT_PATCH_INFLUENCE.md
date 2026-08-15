# Research Note 002: Exact Interventional Patch Influence

**Status:** implementation-backed research hypothesis. No confirmatory evaluation or scientific novelty claim has been completed.

## Motivation

Coding agents can make technically valid but unnecessary changes. FixedBench evaluates tasks whose reported issue is already resolved and finds that tested coding agents still propose undesirable production-code changes in 35 to 65 percent of cases. Preprint: https://arxiv.org/abs/2605.07769

Agent-authored tests can also provide weak behavioral evidence. Banik et al. analyze 86,156 test-file patches from 33,596 agent-authored pull requests and report weak or absent explicit oracle signals in 80.2 percent of the analyzed patches. Preprint: https://arxiv.org/abs/2606.18168

Passing tests are therefore not enough to infer that:

- every changed production file was required;
- a large patch implements one coherent mechanism;
- alternative or redundant fixes are absent;
- compensating changes are benign;
- the tests constrain the intended behavior strongly enough.

Automated patch-correctness research has long studied plausible but incorrect patches, including semantic and syntactic assessment systems such as Invalidator: https://arxiv.org/abs/2301.01113

Recent work also formalizes why test-suite overfitting cannot be universally decided from finite tests alone. ICSE 2026 NIER page: https://conf.researchr.org/details/icse-2026/icse-2026-nier/4/The-Undecidability-of-Overfitting-in-Automated-Program-Repair

DeltaWitness does not attempt to solve that undecidable general problem. It asks a narrower, falsifiable question about exact interventions on the changed paths of a bounded patch.

## Research question

> Does exact coalition replay over changed code paths reveal useful witness structure—necessary, sufficient, redundant, synergistic, or antagonistic changes—that is missed by final-state CI, four-state fail-to-pass verification, and leave-one-out analysis?

The response variable is the declared test witness under exact Git states. The study does not treat that witness as full semantic correctness.

## Relation to prior art

### Delta debugging

Delta debugging systematically isolates failure-inducing inputs or changes. Foundational work includes:

- Andreas Zeller and Ralf Hildebrandt, "Simplifying and Isolating Failure-Inducing Input," IEEE Transactions on Software Engineering, 2002: https://doi.org/10.1109/32.988498
- Holger Cleve and Andreas Zeller, "Locating Causes of Program Failures," ICSE 2005: https://doi.org/10.1145/1062455.1062522

Weighted Delta Debugging extends search by prioritizing likely relevant elements: https://arxiv.org/abs/2411.19410

DeltaWitness v1 deliberately uses exact enumeration rather than a minimizing search. For at most eight path units, the full Boolean response surface permits reporting every minimal supported coalition, all negative edges, and exact interaction metrics. This trades scalability for completeness and removes search-order dependence within the chosen units.

### Cooperative-game attribution

Shapley and Banzhaf values are established methods for allocating or measuring marginal influence in a coalition game. DeltaWitness applies their exact signed forms to the Boolean witness table.

This application inherits known limitations:

- attribution depends on the chosen units;
- correlated or bundled paths can divide credit differently;
- high influence is not normative value;
- a zero value under one witness does not imply global irrelevance;
- non-monotonic games can produce negative contributions.

### Independent patch verification

RETRACE uses bidirectional reconstruction to independently compare the problem implied by a patch with the reported issue and reports improved Pass@1 on SWE-bench Verified. Preprint: https://arxiv.org/abs/2608.08950

That semantic alignment signal is complementary to DeltaWitness. RETRACE asks what problem the patch appears to solve. Exact Patch Influence asks which controlled path interventions alter a declared executable witness. Neither subsumes the other.

## Hypotheses

### H1: collateral-change detection

For synthetic and curated patches containing one behaviorally relevant path and one unrelated changed path, exact influence will assign zero marginal influence to the unrelated path and exclude it from every minimal witness-sufficient coalition.

### H2: interaction recovery

For patches with known AND, OR, compensating, and antagonistic path structure, exact pairwise interaction will recover the expected sign and every inclusion-minimal supported coalition.

### H3: endpoint leakage detection

When a path classified as documentation changes test execution, holding candidate documentation constant will make at least one empty-coalition anchor inconsistent with the canonical matrix, withholding attribution.

### H4: incomplete-state discipline

When a partial intervention causes import, setup, dependency, timeout, or observer failure, the coalition will remain `indeterminate` and exact metrics will be withheld rather than treating the state as unsupported.

### H5: incremental evidence over leave-one-out

On patches with alternative sufficient changes or higher-order interactions, the complete coalition table will identify structures that full-context leave-one-out cannot recover.

### H6: bounded operational cost

For patches with at most eight changed code paths and deterministic fast tests, exact enumeration will remain operationally practical for high-value review, while reporting its exponential execution cost explicitly.

## Methods to compare

### M0: final-state CI

Evaluate candidate implementation plus candidate tests.

### M1: canonical four-state witness

Evaluate base/candidate implementation-side trees against base/candidate tests.

### M2: full-context leave-one-path-out

Evaluate the complete candidate and one intervention for each path removed from the complete patch.

### M3: delta-debugging minimization

Search for one 1-minimal witness-sufficient subset using a documented deterministic order.

### M4: exact patch influence

Evaluate all `2^n` path coalitions, two test worlds per coalition, typed outcomes where adapters exist, endpoint anchors, exact minimal coalitions, signed marginal metrics, and integrity-verifiable reports.

All methods must use the same base/head commits, path units, test commands, timeout policy, environment, and observer semantics where applicable.

## Scenario taxonomy

### Controlled synthetic families

- one necessary path plus one collateral path;
- two alternative individually sufficient paths;
- two jointly necessary paths;
- three-path majority or threshold behavior;
- one path that is harmful unless compensated by another;
- multiple inclusion-minimal supported coalitions of different sizes;
- path deletion and path addition;
- changed dependency manifest classified as code;
- invalid partial import graph;
- setup or collection failure in one coalition;
- documentation leakage into execution;
- flaky outcome introduced by one path;
- weak candidate test that makes the empty coalition supported.

### Curated public patches

A later development corpus may use permissively licensed public repositories and patches whose relevant path structure can be established independently. Every patch must be reproducible locally, small enough for exact enumeration, free of embargoed vulnerability details, and accompanied by a documented ground-truth process.

### Agent-authored patches

A held-out evaluation may sample public agent-authored pull requests with no more than eight changed code paths. Inclusion must not depend on observed DeltaWitness results. The protocol must define licensing, privacy, repository stability, dependency locking, and exclusion rules before collection.

## Primary outcomes

### Minimal-coalition recovery

For scenarios with independently constructed ground truth:

```text
precision and recall of inclusion-minimal supported coalitions
```

### Path-role recovery

Evaluate:

- globally necessary paths;
- paths in no minimal coalition;
- standalone-sufficient paths;
- full-context necessity;
- positive and negative marginal edges;
- pairwise interaction sign.

### Incremental finding rate

Measure the fraction of scenarios where M4 reports a validated structure not recoverable from M0, M1, or M2.

### Invalid-intervention rate

```text
indeterminate coalitions / all coalitions
```

Report by scenario family and cause. Do not remove invalid coalitions from the denominator to make the method appear cleaner.

### Endpoint inconsistency rate

Measure how often held-constant non-code paths change empty or full endpoint semantics.

### Operational cost

Record:

- total command executions;
- wall-clock duration;
- synthetic Git object count;
- report size;
- receipt size;
- peak resource use where reliable measurement exists.

## Exactness criteria

A result may be labeled **exact** only when:

1. every coalition in the declared unit set is evaluated;
2. every coalition is complete;
3. all four endpoint anchors are consistent;
4. the empty coalition is unsupported;
5. the full coalition is supported;
6. path order and unit definitions are recorded;
7. the report integrity digests verify.

Any sampling, pruning, timeout-based omission, or model-based estimate must use a different schema and must not reuse the word exact.

## Statistical plan

Synthetic deterministic scenarios should first be reported with exact truth tables and exact recovery counts.

For a larger clustered corpus, patches from the same repository and scenario family are not independent. A confirmatory analysis should estimate method effects with uncertainty that accounts for repository and family clustering. The model, exclusions, and primary endpoint must be frozen before held-out execution.

No post-hoc regrouping of path units may be used to improve attribution results without being reported as exploratory analysis.

## Current implementation evidence

The `0.0.3` development suite includes:

- exact rational tests for one relevant plus one collateral path;
- alternative sufficient paths with negative interaction;
- jointly necessary paths with positive interaction;
- a non-monotonic XOR game with negative edges;
- end-to-end Git materialization of a necessary and collateral path;
- an invalid partial import graph that withholds metrics;
- documentation leakage that breaks endpoint anchors;
- influence-metric tampering that invalidates both semantic and full-report digests;
- a self-contained CLI demonstration that verifies both matrix and influence reports.

Passing these fixtures supports implementation conformance only. It is not evidence of real-world usefulness, scientific novelty, or superiority over prior methods.

## Threats to validity

### Unit dependence

Whole-file paths are coarse. Splitting one change across files or combining changes in one file can alter the game and its attribution.

### Partial oracles

Tests can miss behavior, assert the wrong property, overuse mocks, or pass for incidental reasons.

### Invalid hybrids

Partial patches can violate build, import, schema, generated-code, or dependency constraints even when both endpoints are valid.

### Environment drift

The current witness does not completely bind the operating-system image, compiler, interpreter, dependencies, kernel, or network responses.

### Nondeterminism

One execution per coalition cannot estimate flakiness or a stochastic success probability.

### Documentation policy

Candidate documentation is held constant. Anchors detect endpoint changes, but other intermediate interactions with documentation may remain possible.

### External validity

Results on small exact patches may not transfer to large refactors or multi-repository changes.

## Falsification and redesign criteria

Narrow, redesign, or abandon the feature if:

- realistic patches exceed the exact cap too frequently for meaningful use;
- invalid hybrid states dominate and prevent exact tables;
- leave-one-out or delta debugging recovers the same actionable information at much lower cost;
- exact metrics are unstable under harmless refactoring or reasonable path regrouping;
- pairwise interaction is routinely misinterpreted without semantic review;
- endpoint anchors fail to detect important hidden execution dependencies;
- existing tools provide equivalent evidence with stronger guarantees;
- independent operators cannot reproduce the trees, outcomes, or exact arithmetic.

## Publication gate

Do not publish a headline claim about patch causality or scientific novelty until:

1. the systematic prior-art search is completed and versioned;
2. the development corpus is frozen;
3. the held-out manifest is committed and timestamped;
4. at least one external operator reproduces an exact report;
5. the statistical analysis plan is preregistered;
6. negative and incomplete results are included;
7. the report survives independent technical review.

## Claim boundary

A path's exact influence value means only that selecting or removing that path changes the declared Boolean witness across the enumerated coalitions under the recorded environment.

It does not establish:

- correctness or security outside the tests;
- author intent;
- vulnerability severity;
- production impact;
- legal or organizational responsibility;
- universal causal importance;
- the absence of another untested patch.
