# DW-001 Evidence-Gap Review

**Status:** pre-preregistration design review; not frozen; no evaluation results inspected.

**Reviewed repository state:** `a29eb1476bec42bfcbfe6758f05bb70667b056c7` (`v0.0.3` source state after pull request #10).

**Decision scope:** identify the minimum evidence and baseline corrections required before `research/DW-001/PROTOCOL.md` can be treated as a preregistration candidate.

This document is not an effectiveness, novelty, safety, or production-readiness claim. It records gaps that could otherwise make the first empirical study uninterpretable.

## 1. Research question under review

Issue #2 asks:

> Does the four-state witness detect materially important false-assurance cases that are missed by final-state CI and two-state fail-to-pass validation, at an acceptable execution and review cost?

The question is falsifiable, but the original issue text does not yet isolate four distinct sources of evidence:

1. candidate tests executed against the base implementation;
2. base tests executed against the candidate implementation;
3. the base implementation executed against the base tests as an endpoint-validity control;
4. typed outcome semantics versus generic exit-code interpretation.

A result that changes all four at once cannot identify why one method accepted or rejected a scenario.

## 2. Current evidence inventory

### FACT

The repository currently implements:

- exact Git-native `base_base`, `base_candidate`, `candidate_base`, and `candidate_candidate` states;
- explicit pass, fail, error, and timeout observations;
- optional invocation-bound `outcome-receipt-v1` evidence;
- integrity-verifiable four-state reports;
- exact bounded patch-path influence as a separate analysis layer;
- synthetic unit, integration, reproducibility, and end-to-end coverage.

### FACT

The repository does not currently contain:

- `research/DW-001/PROTOCOL.md`;
- a frozen scenario-generator specification;
- a development/holdout split;
- a public commitment procedure for the holdout manifest;
- frozen metric definitions;
- an independently reviewed ground-truth manifest;
- a systematic literature-search record;
- an external independent reproduction satisfying issue #4.

### OBSERVATION

The implemented core is sufficient to generate study evidence, but implementation completion is not empirical validation. Running the existing demonstration repeatedly would test engineering reproducibility on one synthetic structure, not the DW-001 hypothesis.

## 3. Baseline confounds that must be removed

### 3.1 State-set confound

A comparison of final-state CI with the complete four-state method changes three observations simultaneously. The study must include cumulative state ablations so that every additional state has an identifiable contrast.

Required controlled methods:

| ID | Evidence states | Question isolated |
|---|---|---|
| `M0_FINAL` | `candidate_candidate` | What does a green final repository accept? |
| `M1_F2P` | `base_candidate`, `candidate_candidate` | What is added by requiring the candidate witness to fail before the implementation change? |
| `M2_F2P_P2P` | `base_candidate`, `candidate_base`, `candidate_candidate` | What is added by checking that original tests remain satisfied by the candidate implementation? |
| `M3_FOUR_STATE` | all four states | What is added by independently validating the base/base endpoint and the complete matrix? |

Primary incremental contrasts:

```text
M1_F2P       - M0_FINAL       = candidate-test discrimination
M2_F2P_P2P   - M1_F2P         = original-test preservation
M3_FOUR_STATE - M2_F2P_P2P    = base-endpoint validity and full matrix consistency
```

The labels describe evidence increments, not causal effects in the scientific sense. The observed difference may still depend on scenario construction, runner behavior, and the declared oracle.

### 3.2 Observer-semantics confound

Typed receipts and the four-state matrix are separate hypotheses. Every controlled state-set method must be crossed with the same observation modes:

| ID | Observation rule | Intended contrast |
|---|---|---|
| `O0_EXIT_CODE` | configured disjoint pass/fail exit-code sets | conventional process-status evidence |
| `O1_TYPED_RECEIPT` | invocation-bound typed receipt plus exit-code agreement | structured assertion-versus-error evidence |

Primary observer contrast:

```text
O1_TYPED_RECEIPT - O0_EXIT_CODE = incremental typed-outcome evidence
```

The study must not credit the four-state matrix for a case detected only because one arm used typed receipts and another used raw exit codes.

### 3.3 Shared-engine confound

The primary ablation should reuse the same state materializer, command construction, timeout policy, observer implementation, and outcome classifier while revealing only the states allowed to each method. Otherwise, a method comparison becomes an implementation comparison.

A secondary ecological comparison may execute the closest official benchmark harnesses or reproduce their scoring semantics. It must be reported separately because differences in checkout logic, parsers, dependency images, and test selection can dominate the state-set comparison.

### 3.4 Oracle-quality confound

A typed assertion failure can still be irrelevant, weak, tautological, overfit, or unrelated to the claimed defect. DW-001 may classify scenarios using declared deterministic ground truth, but it must not interpret successful typed execution as test adequacy.

Oracle-strength, coverage, mutation score, and semantic issue alignment are secondary measurements or later studies. They are not silently inferred from a supported four-state witness.

### 3.5 Influence-layer confound

Exact path-coalition influence was implemented after issue #2 was opened. It must not be added to the primary DW-001 acceptance rule. Doing so would change the intervention, cost, and claim under study after the original question was defined.

Patch influence may be collected as an explicitly exploratory secondary artifact on compatible scenarios. It must not affect the primary method label or primary hypothesis test.

## 4. Direct and adjacent baselines

### Direct executable baselines

1. **Final-state CI semantics** — candidate implementation with candidate tests.
2. **Two-state fail-to-pass semantics** — candidate tests against base and candidate implementations.
3. **Fail-to-pass plus regression-preservation semantics** — the `FAIL_TO_PASS` and `PASS_TO_PASS` distinction used by SWE-bench-style grading.
4. **DeltaWitness four-state replay** — all four exact Git states.

The direct comparison is not against a caricature. `M2_F2P_P2P` must receive the strongest reasonable interpretation of benchmark-style fail-to-pass plus regression preservation before DeltaWitness receives credit for `base_base`.

### Adjacent analytical baselines

The prior-art review must explicitly assess, and either implement or justify excluding:

- delta debugging or patch minimization;
- PATCH-SIM-style execution-trace similarity;
- generated-test patch assessment such as RGT or DiffTGen;
- exception- or error-behavior patch assessment such as Opad;
- semantic/syntactic patch classifiers such as Invalidator;
- behavior-preservation comparison such as ChangeGuard;
- relational patch analysis such as P³;
- semantic issue/patch alignment such as RETRACE.

Not every adjacent method belongs in the first executable benchmark. Exclusion requires a recorded reason such as incompatible research question, unavailable artifact, unsupported language, need for a semantic specification, prohibitive setup cost, or inability to run safely on the selected corpus.

## 5. Ground-truth requirements

### DECISION

The expected label for every scenario must be defined independently of DeltaWitness output.

Each scenario manifest entry must contain at least:

- scenario identifier and family;
- source and license/authorization status;
- immutable base and candidate Git identities;
- declared implementation, test, and documentation paths;
- command and observer configuration;
- expected state-level semantic outcomes;
- expected accept, reject, or indeterminate decision for each controlled method;
- false-assurance mechanism being tested;
- whether every hybrid state is semantically meaningful;
- known environmental assumptions;
- rationale and reviewer identity;
- development or holdout partition.

### DECISION

Method outputs must not be used to repair the held-out ground truth after unblinding. A genuine ambiguity discovered after freeze becomes:

- an exclusion under a preregistered rule;
- a protocol deviation;
- or a reported ground-truth dispute.

It must not be silently relabeled to improve agreement.

## 6. Scenario families required before freeze

The issue #2 families remain appropriate, but each needs positive and negative controls.

| Family | Required control or contrast |
|---|---|
| Valid discriminating regression fix | semantically equivalent valid fixes with different diff shapes |
| Candidate test passes before and after | a genuinely discriminating candidate test for the same defect |
| Candidate breaks original regression | a valid fix preserving the original suite |
| Weakened/deleted original assertion | unchanged strong assertion and harmless test refactor |
| Wrong-reason base failure | genuine assertion exposure with the same process exit code |
| Collection/import/setup/dependency failure | genuine test failure under the same runner |
| Invalid hybrid state | valid separable change with similar path topology |
| Nondeterminism/environment drift | deterministic counterpart with the same nominal outcomes |

Additional minimum negative controls:

- no-op or already-resolved task;
- implementation-only change with no new test witness;
- test-only change with no implementation repair;
- documentation-only change;
- renamed or regrouped paths preserving behavior;
- runner command that succeeds without executing tests;
- all-skipped or expected-failure-only execution;
- candidate test that fails on an unrelated pre-existing defect.

## 7. Frozen outcome definitions required

The protocol must define method decisions before execution. At minimum:

- `accept`: the method's complete declared acceptance predicate is satisfied;
- `reject`: execution is complete and the predicate is contradicted;
- `indeterminate`: required evidence is missing, malformed, timed out, environmentally invalid, or otherwise incomplete;
- `not_applicable`: the method's required hybrid state or observer cannot be constructed under the frozen applicability rule.

`indeterminate` and `not_applicable` must not be collapsed into `reject` or removed from denominators without reporting both the numerator and denominator.

Primary measurements should include:

1. unsafe-acceptance rate on false-assurance scenarios;
2. valid-patch acceptance rate;
3. over-refusal rate on valid applicable patches;
4. indeterminate rate;
5. not-applicable or invalid-hybrid rate;
6. incremental detections for each state contrast;
7. failure-cause classification accuracy;
8. wall-clock time, executed-state count, and command-runtime multiplier;
9. manual-review time and disagreement rate.

Every rate requires an explicit denominator. Paired scenario-level contingency tables must be retained; one aggregate accuracy score is insufficient.

## 8. Sampling and precision gap

### UNKNOWN

The prevalence of each false-assurance mechanism in real coding-agent patches is not yet established. Therefore a single prevalence-weighted headline estimate would be premature.

### DECISION

The first frozen study should use a stratified scenario design and report family-specific estimates. A precision target, rather than an optimistic power calculation against an unknown effect size, is likely more defensible for the initial synthetic/curated study.

Before freeze, the protocol must specify:

- the minimum number of independent scenarios per family;
- the target confidence-interval width for key proportions;
- whether intervals are exact, Wilson, bootstrap, or hierarchical;
- how repeated stochastic runs are aggregated;
- how scenario-family imbalance is handled;
- which contrast is primary and which are secondary.

No sample-size target is fixed in this review because the scenario-generation cost and expected applicability rate have not yet been measured in a development pilot.

## 9. Holdout and commitment gap

The study needs a development corpus for debugging the generator and a held-out corpus for evaluation.

Before held-out execution:

1. serialize a canonical manifest containing scenario IDs, immutable source identities, partitions, expected labels, and protocol version;
2. compute a cryptographic digest over canonical bytes;
3. publish the digest and canonicalization procedure in an immutable Git commit or external preregistration service;
4. keep any sensitive raw material private under the publication policy;
5. record every post-commit deviation without rewriting the original commitment.

A Git commit alone timestamps the public protocol but does not make an undisclosed holdout credible. The manifest commitment must bind the actual held-out membership and expected-label material at the level permitted by disclosure constraints.

## 10. Environment and execution gap

The current runner is not a sandbox, and Git identities do not bind the complete environment.

### DECISION

DW-001 must use only synthetic, owned, licensed, or explicitly authorized targets in a disposable, non-sensitive environment. The protocol must record:

- operating system and architecture;
- Python and Git versions;
- package and toolchain manifests;
- locale, timezone, and relevant environment variables;
- network policy;
- resource limits;
- exact DeltaWitness commit;
- exact scenario-generator commit;
- exact command and timeout;
- retry and stochastic repetition policy.

Environment capture is evidence about conditions, not a containment claim.

## 11. Independent reproduction gate

Issue #4 remains open. The current maintainer and the same agent workflow cannot satisfy its independence criterion.

### DECISION

DW-001 design and development may proceed, but:

- Gate 0 remains incomplete;
- the independent-reproduction item in `ROADMAP.md` remains unchecked;
- no claim of externally reproduced behavior is permitted;
- a held-out empirical result must not be presented as independently reproduced unless an external operator follows the frozen procedure.

The reproduction protocol itself also needs an immutable target. A command that clones the moving default branch is insufficient for reproducing a version-specific claim unless it checks out an exact commit or signed/tagged release identity.

## 12. Cheapest resolving work before preregistration

The following sequence minimizes wasted implementation:

1. repair incorrect prior-art source identities;
2. publish a reproducible exploratory search log and direct-baseline table;
3. freeze controlled state-set and observer-factor semantics;
4. specify canonical scenario and result schemas;
5. implement a small development pilot only to estimate applicability, runtime, and scenario-generation cost;
6. use the pilot to set a precision target without inspecting held-out results;
7. freeze the protocol, generator version, metrics, exclusions, and holdout commitment;
8. execute the held-out study once under the deviation policy;
9. seek independent reproduction and external review.

## 13. Review conclusion

### FACT

No new execution capability is required before DW-001 can be designed. The existing core can support controlled state ablations.

### DECISION

The immediate prerequisite is narrower than a new feature: repair the source map and make the baseline/measurement design auditable. After that, the default priority remains DW-001 issue #2.

### CLAIM BOUNDARY

Completing this review shows only that known design confounds and evidence gaps were recorded before preregistration. It does not establish that the proposed controls are sufficient, that DeltaWitness outperforms any baseline, that the method is scientifically novel, or that Gate 0 is complete.
