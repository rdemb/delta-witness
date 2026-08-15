# Research Note 000: Prior-Art and Novelty Boundary

**Status:** living research map, updated for DeltaWitness `0.0.3`.

**Important:** this document does not establish scientific novelty. It records the current prior-art boundary, the narrower hypotheses implemented by DeltaWitness, and the evidence required before any novelty or superiority claim is permitted.

## 1. Problem decomposition

A coding agent can change implementation code, change tests, execute the final repository, and report success. That single workflow collapses several different questions:

```text
Did the command run?
Did tests execute rather than fail during collection or setup?
Did an assertion expose the old behavior?
Does the candidate satisfy the new witness?
Do the original tests still pass?
Which changed implementation paths influence that witness?
Are the tests relevant and strong?
Is the patch correct outside the tests?
Was the environment reproducible?
Who produced the evidence?
Is deployment authorized?
```

No one signal answers all of these questions. DeltaWitness therefore separates them into layers.

| Layer | Current DeltaWitness mechanism | Current claim boundary |
|---|---|---|
| State identity | Exact Git trees and commits | Identifies repository states, not the full execution environment |
| Counterfactual behavior | Four-state base/candidate implementation and test matrix | Supports a declared executable witness, not full correctness |
| Outcome semantics | Exit-code classes or typed outcome receipts | Distinguishes assertion failure from error states for cooperating adapters |
| Bounded intervention influence | Exact path-coalition replay under two test worlds | Attributes one Boolean witness over chosen file-level units |
| Oracle relevance and strength | Not yet implemented | Remains outside the current evidence boundary |
| Full patch causality | Not established | Tests and file interventions are partial evidence only |
| Environment provenance | Not yet complete | Git identity does not bind the operating system or dependencies |
| Producer authentication | Not implemented | Current digests are unkeyed integrity checks, not attestations |
| Authorization | Not implemented | A supported report does not authorize merge or deployment |

## 2. Established prior art

### 2.1 Fail-to-pass validation

Testing a candidate test against the old implementation and the fixed implementation is established practice in automated program repair and software-engineering benchmarks. TDD-Bench Verified explicitly uses fail-to-pass test validation:

- https://github.com/kanishkamisra/tdd-bench-verified

DeltaWitness does not claim novelty for the observation:

```text
candidate test fails before the fix
candidate test passes after the fix
```

Its four-state matrix additionally runs the original tests against both implementation-side trees, binds hybrid states to exact Git objects, and records machine-verifiable evidence. Whether that additional state and evidence produce useful incremental detection remains an empirical question.

### 2.2 Delta debugging and change isolation

Systematic isolation of failure-inducing inputs and changes is established by delta debugging:

- Andreas Zeller and Ralf Hildebrandt, "Simplifying and Isolating Failure-Inducing Input," IEEE Transactions on Software Engineering, 2002: https://doi.org/10.1109/32.988498
- Holger Cleve and Andreas Zeller, "Locating Causes of Program Failures," ICSE 2005: https://doi.org/10.1145/1062455.1062522

Weighted Delta Debugging and later variants improve search order or efficiency:

- https://arxiv.org/abs/2411.19410

DeltaWitness `0.0.3` deliberately does not claim to invent patch minimization. For at most eight changed code paths, it enumerates every coalition rather than returning one order-dependent 1-minimal subset. The hypothesis is that a complete non-monotonic response surface, two test worlds, typed execution outcomes, endpoint anchors, and integrity-verifiable Git states reveal interaction structures that one minimizing search or full-context leave-one-out can miss.

### 2.3 Patch correctness and overfitting

Passing a finite test suite does not prove semantic correctness. Automated program-repair research has long studied plausible but incorrect patches and test-suite overfitting.

Examples include:

- Invalidator, combining semantic and syntactic reasoning for patch assessment: https://arxiv.org/abs/2301.01113
- An ICSE 2026 NIER result formalizing limits of deciding overfitting from finite tests: https://conf.researchr.org/details/icse-2026/icse-2026-nier/4/The-Undecidability-of-Overfitting-in-Automated-Program-Repair

DeltaWitness does not attempt to solve the general patch-correctness problem. Its reports remain bounded to declared tests, exact repository states, observers, and intervention units.

### 2.4 Behavioral change validation

Pairwise and relational execution have been used to determine whether a change preserves or alters behavior. Relevant directions include:

- ChangeGuard, which validates behavior-preserving changes through comparative execution: https://arxiv.org/abs/2405.01594
- Product-program approaches that reason about two related program executions: https://arxiv.org/abs/2501.13158

These approaches establish that cross-version relational reasoning is not new. DeltaWitness must demonstrate that its specific Git-native post-change workflow, state construction, evidence artifacts, and bounded intervention table provide useful operational evidence beyond existing behavioral validation.

### 2.5 Test-oracle quality

A test can execute and still provide weak evidence. Banik et al. analyze 86,156 agent-authored test-file patches and report weak or absent explicit oracle signals in 80.2 percent of the analyzed patches:

- https://arxiv.org/abs/2606.18168

This motivates a future Test Integrity Layer. It does not validate DeltaWitness's current matrix or influence metrics. Typed outcomes distinguish assertion failure from execution error; they do not establish that the assertion is relevant or strong.

### 2.6 Test-runner outcome semantics

Popular test frameworks expose richer semantics than one process exit code.

- Python `unittest.TestResult` distinguishes failures, errors, skips, expected failures, unexpected successes, and subtest outcomes: https://docs.python.org/3/library/unittest.html
- Pytest publishes separate exit codes for failed tests, interruption, internal errors, usage errors, and no collected tests: https://docs.pytest.org/en/stable/reference/exit-codes.html

DeltaWitness's `outcome-receipt-v1` protocol is an implementation hypothesis: a strict invocation-bound receipt plus process-exit agreement may reduce false regression witnesses. The underlying framework semantics are established prior art.

### 2.7 Agent evaluation and machine-readable evidence

NIST's work on evaluation probes for agentic AI emphasizes machine-readable evidence and auditable claim-to-evidence traces:

- https://www.nist.gov/programs-projects/building-evaluation-probes-agentic-ai

This supports the design principle that an agent's narrative should not be the sole evidence channel. It does not imply that DeltaWitness follows a NIST standard or has been reviewed by NIST.

### 2.8 Independent patch verification

RETRACE reconstructs the problem implied by a patch and compares it with the reported issue:

- https://arxiv.org/abs/2608.08950

That semantic alignment question is complementary to DeltaWitness's executable intervention question. RETRACE asks what problem a patch appears to solve. DeltaWitness asks which exact code-path selections alter a declared test witness. Neither method establishes complete correctness, and neither currently subsumes the other.

### 2.9 Unnecessary agent changes

FixedBench evaluates coding tasks whose reported problem is already resolved and reports that tested agents still make undesirable production-code changes in a substantial fraction of tasks:

- https://arxiv.org/abs/2605.07769

This motivates explicit detection of collateral and unnecessary changes. It does not establish that exact path influence is the best or most scalable solution.

### 2.10 Cooperative-game attribution

Shapley and Banzhaf values are established methods for allocating or measuring marginal influence in coalition games. DeltaWitness applies exact signed forms to a Boolean witness function over changed paths.

The project does not claim novelty for either metric. Their use introduces known limitations:

- attribution depends on the chosen units;
- splitting or combining files can change allocations;
- correlated or substitutable paths divide credit differently;
- negative values can appear in non-monotonic games;
- influence is descriptive, not a normative measure of correctness, ownership, or blame.

## 3. Current implementation-backed hypotheses

DeltaWitness currently evaluates three narrower hypotheses.

### H0: four-state witness

A Git-native four-state matrix may detect regressions or misleading candidate tests that final-state CI and two-state fail-to-pass validation miss.

Required evidence:

- paired comparison against correctly implemented baselines;
- false-assurance and valid-witness acceptance rates;
- cost and applicability;
- held-out evaluation;
- independent reproduction.

### H1: typed failure semantics

An invocation-bound structured receipt may distinguish genuine assertion failure from collection, import, setup, teardown, no-test, skip-only, and producer-error states more safely than a generic nonzero exit code.

See:

- [Outcome Receipt Protocol v1](OUTCOME_RECEIPT_V1.md)
- [Research Note 001](RESEARCH_NOTE_001_TYPED_FAILURES.md)

Required evidence:

- comparison with documented exit-code baselines;
- adapters implemented independently of the core repository;
- adversarial and real-world runner scenarios;
- unsafe-acceptance and over-refusal analysis.

### H2: exact interventional patch influence

For a small patch, complete path-coalition replay under both base and candidate test worlds may identify witness-necessary, witness-sufficient, redundant, synergistic, and antagonistic changed paths more completely than final-state CI, leave-one-out, or one delta-debugging result.

See:

- [Exact Patch Influence v1](PATCH_INFLUENCE_V1.md)
- [Research Note 002](RESEARCH_NOTE_002_EXACT_PATCH_INFLUENCE.md)

Required evidence:

- exact recovery on independently defined synthetic structures;
- comparison with leave-one-out and delta debugging;
- applicability and invalid-hybrid rates on public patches;
- stability under reasonable path regrouping and refactoring;
- operational cost;
- external reproduction.

## 4. Provisional contribution under evaluation

The potentially distinctive element is not any single component. It is the combined evidence chain:

```text
immutable Git endpoints
    -> exact four-state replay
    -> typed and invocation-bound outcome semantics
    -> complete bounded path interventions under two test worlds
    -> endpoint consistency gates
    -> exact non-monotonic coalition metrics
    -> integrity-verifiable machine-readable reports
```

This combination is currently an engineering and research hypothesis. It must not be described as scientifically novel until direct competitors and adjacent methods have been reviewed systematically and the incremental evidence has been measured.

## 5. Novelty-review protocol still required

Before a novelty claim, the project must publish a reproducible prior-art review containing:

1. databases and search engines used;
2. exact search strings;
3. search dates;
4. inclusion and exclusion criteria;
5. deduplication method;
6. title/abstract and full-text screening records;
7. extracted comparison dimensions;
8. excluded close matches and reasons;
9. versioned evidence table;
10. external review of the nearest-neighbor set.

At minimum, the review must cover:

- automated program repair and patch correctness;
- fail-to-pass and regression-test validation;
- delta debugging and patch minimization;
- behavioral equivalence and product programs;
- mutation testing and test-oracle assessment;
- causal debugging and intervention analysis;
- Shapley and Banzhaf attribution for software artifacts;
- provenance and software attestations;
- agent trace evaluation and coding-agent benchmarks.

The current literature notes are exploratory, not a systematic review.

## 6. Falsification criteria

The project should narrow, redesign, or abandon a layer when evidence shows that:

- it does not reduce unsafe acceptance relative to a fair baseline;
- it rejects too many valid cases to be operationally useful;
- incomplete or invalid hybrid states dominate realistic patches;
- the same information is available from a simpler established method;
- results are unstable under harmless refactoring or unit regrouping;
- the cost exceeds incremental evidence value;
- external operators cannot reproduce the states, results, or arithmetic;
- a claimed invariant cannot be enforced fail-closed;
- public reports encourage stronger interpretations than the evidence supports.

A negative result is a valid research outcome and must be published with the same care as a positive one.

## 7. Current status

| Question | Status |
|---|---|
| Working four-state Git prototype | Implemented and synthetically tested |
| Typed outcome receipts | Implemented for a cooperating `unittest` adapter |
| Exact path-coalition enumeration | Implemented up to eight changed code paths |
| Exact rational influence metrics | Implemented with invariant checks |
| Safe execution of untrusted code | Not implemented |
| Test-oracle relevance or strength | Not implemented |
| Repeated stochastic evaluation | Not implemented |
| Locked environment provenance | Not implemented |
| Signed producer authentication | Not implemented |
| Systematic prior-art review | Not completed |
| Held-out empirical evaluation | Not completed |
| Independent reproduction | Not completed |
| Scientific novelty | Not established |
| Production readiness | Not established |

## 8. Public wording rule

Permitted:

> DeltaWitness is evaluating a Git-native evidence chain for counterfactual patch verification, typed test outcomes, and exact bounded path influence.

Not permitted without future evidence:

> DeltaWitness proves patch correctness.

> DeltaWitness is the first causal verifier for AI code.

> DeltaWitness is scientifically proven to outperform existing methods.

> A high influence score identifies the true cause or the responsible author.

Public claims must remain narrower than the current evidence, even when the long-term ambition is much larger.
