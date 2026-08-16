# DW-001 Weak-Proxy-Oracle Challenge v1

**Status:** implemented and synthetically tested development-only negative control. Not an ecological coding-agent evaluation, mutation benchmark, oracle-strength score, merge policy, protocol freeze, or holdout result.

## 1. Problem

DeltaWitness now separates several evidence layers that are often collapsed into one green test run:

```text
process exit
    -> typed assertion failure versus execution error
    -> exact four-state behavior
    -> exact declared-test selector localization
```

Those layers still do not establish that the declared test is strong enough to reject plausible claim-violating implementations.

A test can be:

- a real assertion;
- genuinely fail-to-pass between base and candidate;
- the exact selector declared for the claim;
- correctly observed through a typed receipt;
- embedded in a complete canonical `BB / BC / CB / CC` witness;

and remain only a proxy for the intended behavior.

## 2. Fixed development task

Challenge identifier:

```text
weak-proxy-oracle-v1
```

Fixture family:

```text
weak-proxy-oracle
```

Fixed owned-synthetic task prompt:

```text
Fix is_admin so only the admin role is authorized and add a regression test proving that a viewer is denied.
```

The task is an **agent-workflow surrogate**. Candidate, tests, prompt, mutant, and hidden claim check are fixed project-owned bytes. No model output is sampled and `model_identity = null`.

This design prevents post-result prompt, candidate, or mutant selection. It does not estimate the behavior of any model, vendor, agent framework, or production workflow.

## 3. Base, candidate, and declared test

Base implementation:

```python
def is_admin(user):
    return user.get("role")
```

Candidate implementation:

```python
def is_admin(user):
    return user.get("role") == "admin"
```

Declared candidate selector:

```text
test_access.AccessTests.test_viewer_result_is_boolean
```

Declared test body:

```python
def test_viewer_result_is_boolean(self):
    self.assertIsInstance(is_admin({"role": "viewer"}), bool)
```

The assertion is genuine and discriminating:

```text
base      -> "viewer" -> not bool -> fail
candidate -> False    -> bool     -> pass
```

It does not establish the intended authorization property. It tests return type, not viewer denial.

## 4. Current DeltaWitness evidence

Under both `O0_EXIT_CODE` and `O1_TYPED_RECEIPT`:

```text
BB = pass
BC = fail
CB = pass
CC = pass
```

All nested state-set methods accept:

```text
M0_FINAL      = accept
M1_F2P        = accept
M2_F2P_P2P    = accept
M3_FOUR_STATE = accept
```

Declared-selector localization returns:

```text
aggregate_status = supported
selector classification = discriminating
```

Under `O1_TYPED_RECEIPT`, `BC` contains a real typed assertion failure with at least one failure and zero errors.

These observations are correct within their contracts. The limitation is not a misclassification by the receipt, matrix, projection, or localization verifier.

## 5. Fixed claim-violating mutant

Mutant identifier:

```text
nonempty-role-boolean-v1
```

Fixed mutant:

```python
def is_admin(user):
    return bool(user.get("role"))
```

The mutant preserves the weak proxy property:

```text
is_admin(viewer) -> True -> bool
```

It therefore passes the exact declared selector while still granting administrator authorization to a viewer.

Fixed hidden development claim selector:

```text
test_hidden_claim.HiddenClaimTests.test_viewer_is_denied
```

Hidden claim check:

```python
def test_viewer_is_denied(self):
    self.assertFalse(is_admin({"role": "viewer"}))
```

The hidden check passes on the candidate and fails on the mutant.

The hidden check is fixed mechanism evidence. It is not a general oracle, an ecological holdout, or a claim that hidden tests always capture intent.

## 6. Five controlled executions

The challenge executes exactly five shell-free typed controls:

| Implementation | Test role | Expected observation |
|---|---|---|
| base | declared selector | `fail` |
| candidate | declared selector | `pass` |
| mutant | declared selector | `pass` |
| candidate | hidden claim | `pass` |
| mutant | hidden claim | `fail` |

Every control binds:

- challenge, implementation, role, and selector identity;
- canonical selector command;
- exact source and test SHA-256;
- observer and producer identity;
- invocation binding;
- process return code;
- typed receipt digest, outcome, producer, and counts.

Raw stdout, stderr, tracebacks, temporary paths, and environment values are excluded.

## 7. Integrity contract

Schema:

```text
research/DW-001/schema/weak-oracle-challenge.schema.json
```

Implementation:

```text
src/deltawitness/dw001_oracle_challenge.py
```

The verifier independently checks:

1. fixture descriptor semantics and digest;
2. fixture identity semantics and descriptor relation;
3. matrix report semantics and complete-report integrity;
4. projection semantics and source-report relation;
5. declaration semantics and exact selector identity;
6. localization semantics and source-report relation;
7. complete supported canonical matrix;
8. `M0`–`M3 = accept`;
9. one supported, discriminating fixed selector;
10. exact fixed task, candidate, mutant, tests, controls, finding, and limitations;
11. `challenge_sha256` over stable semantic evidence;
12. `report_sha256` over the complete challenge artifact.

The challenge digest intentionally binds stable semantic views of projection and localization evidence rather than volatile creation times, durations, or complete-report digests. Repeated clean executions of the same fixed sources therefore emit byte-identical challenge artifacts.

Recomputing both unkeyed digests cannot hide mutant, control, source, finding, or denominator substitution because the verifier reconstructs the complete canonical artifact from supplied verified sources and fixed project-owned bytes.

## 8. Finding

For this exact owned-synthetic challenge:

```text
typed assertion failure
    + canonical four-state witness
    + declared-selector fail-to-pass localization
    != sufficient oracle strength
```

More precisely:

- the declared selector genuinely distinguishes base from candidate;
- the current evidence layers correctly accept that transition;
- one fixed claim-violating mutant survives the declared selector;
- the same mutant fails a separately fixed claim check.

This is a counterexample to an overly broad interpretation of accepted current evidence. It is not a complete method for measuring oracle strength.

## 9. Direct prior art

The underlying problems and techniques are established:

- Barr, Harman, McMinn, Shahbaz, and Yoo, **“The Oracle Problem in Software Testing: A Survey,”** IEEE Transactions on Software Engineering, DOI `10.1109/TSE.2014.2372785`;
- Jia and Harman, **“An Analysis and Survey of the Development of Mutation Testing,”** IEEE Transactions on Software Engineering, DOI `10.1109/TSE.2010.62`;
- mutation adequacy, partial and weak oracles, hidden tests, coincidental correctness, coverage, and assertion-quality analysis;
- Banik, Chowdhury, and Shamim, **“All Smoke, No Alarm: Oracle Signals in Agent-Authored Test Code,”** arXiv `2606.18168`;
- Hora and Robbes, **“Are Coding Agents Generating Over-Mocked Tests? An Empirical Study,”** arXiv `2602.00409`;
- Jhanglani et al., **“Beyond Test Presence: Assessing the Quality and Robustness of Agent-Generated Tests in Open-Source Projects,”** arXiv `2607.12068`;
- Dai et al., **“ABTest: Behavior-Driven Testing for AI Coding Agents,”** arXiv `2604.03362`;
- execution-grounded oracle synthesis and semantic mutation approaches, including Nexus, arXiv `2510.26423`, and TDAD, arXiv `2603.08806`.

No novelty claim is made for weak assertions, hidden tests, mutation testing, oracle synthesis, or agent testing.

The narrow DeltaWitness contribution under evaluation is the integration of a fixed weak-oracle counterexample into one deterministic, Git-native, typed, selector-localized, integrity-verifiable evidence chain with explicit non-claims.

Whether that integration is scientifically novel or practically superior remains unestablished.

## 10. Falsification and redesign

Narrow or abandon this challenge if:

- the declared selector is not a real assertion failure on base;
- it does not pass on candidate;
- current localization does not classify it as discriminating;
- any current nested method rejects or becomes indeterminate;
- the fixed mutant fails the declared selector;
- the hidden claim check passes on the mutant;
- the hidden claim check merely restates the declared proxy property;
- candidate or mutant bytes contain additional confounding changes;
- repeated clean executions do not preserve semantic challenge bytes;
- another existing fixture demonstrates the same limitation with fewer assumptions.

Narrow or abandon a future mutation layer if it cannot reject this negative control without materially rejecting valid positive controls, if mutation operators are selected after observing results, or if a scalar score hides surviving claim-violating mutants.

## 11. Security and privacy boundary

Only fixed project-owned Python bytes run in temporary directories.

The challenge adds no:

- network access;
- external repository execution;
- dependency or package-manager execution;
- external upload;
- telemetry;
- secret;
- repository permission;
- remote execution service;
- containment claim.

The host Python runtime, unittest adapter, filesystem, process environment, and operating system remain trusted. The runner is not a sandbox.

The receipt binding is visible to tested code and current digests are unkeyed. A coordinated actor able to replace the complete source and expected-digest chain can replace the evidence chain.

## 12. Non-claims

A valid challenge does not establish:

- prevalence of weak oracles in real agent patches;
- quality of any named model or coding agent;
- accuracy, precision, recall, or calibration of a mutation method;
- that the hidden claim check is complete;
- mutation score adequacy;
- code coverage adequacy;
- claim-oracle relevance in general;
- complete patch correctness, security, or production safety;
- authorization to execute public benchmark instances;
- ecological effectiveness or superiority;
- protocol freeze, holdout validity, or independent reproduction;
- Gate 0 or Gate 1 completion;
- production readiness or scientific novelty.

## 13. Next experimental decision

The next Gate 1 step should compare the smallest deterministic alternatives against this challenge and valid controls:

1. fixed claim-violating mutants;
2. mutation operators scoped to changed symbols or behavior;
3. assertion AST-delta signals;
4. changed-line and changed-branch coverage;
5. combinations of mutation and coverage evidence.

No headline score, merge blocker, or LLM judge is authorized before a frozen calibration protocol measures false positives, false negatives, applicability, cost, and disagreement.
