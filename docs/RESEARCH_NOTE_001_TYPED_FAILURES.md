# Research Note 001: Typed Failure Semantics

**Status:** implementation-backed research hypothesis. No confirmatory evaluation has been completed.

## Problem

Counterfactual patch evaluation often treats a nonzero test-process status as evidence that a candidate test exposed behavior in the base implementation. That inference is invalid when the same channel also carries collection, import, setup, teardown, dependency, usage, interruption, or internal-runner errors.

The core epistemic error is:

```text
process did not succeed
        therefore
intended regression oracle fired
```

The conclusion does not follow from the premise.

## Research question

> Does replacing coarse exit-code-only observation with a strict, invocation-bound typed outcome receipt reduce unsafe acceptance of invalid counterfactual witnesses without causing unacceptable rejection of valid witnesses?

This question is separable from whether a failing test is relevant, strong, non-flaky, or causally connected to the patch. Typed failure semantics address **what kind of runner outcome occurred**, not **whether the oracle is good**.

## Technical motivation

Python's `unittest.TestResult` distinguishes explicit assertion failures from unexpected errors and separately records skips, expected failures, unexpected successes, and subtest outcomes. The framework therefore exposes more semantic information than a single process code. Official documentation: https://docs.python.org/3/library/unittest.html

Pytest similarly defines separate public exit codes for failed tests, interruption, internal error, command-line usage error, and absence of collected tests. Official documentation: https://docs.pytest.org/en/stable/reference/exit-codes.html

NIST's work on evaluation probes for agentic AI emphasizes machine-readable evidence and auditable claim-to-evidence traces rather than relying only on narrative model reports. Project description: https://www.nist.gov/programs-projects/building-evaluation-probes-agentic-ai

Oracle quality remains a separate major risk. Banik et al. report weak or absent explicit oracle signals in 80.2 percent of 86,156 analyzed agent-authored test-file patches. Preprint: https://arxiv.org/abs/2606.18168

These sources motivate richer observation, but they do not establish that DeltaWitness's receipt protocol is novel, sufficient, or operationally beneficial.

## Hypotheses

### H1: unsafe-acceptance reduction

For scenarios where candidate tests cannot execute because of discovery, import, setup, or producer failure, `outcome-receipt-v1` will produce a lower unsafe acceptance rate than an exit-code-only baseline configured to treat the runner's generic failure status as `fail`.

### H2: valid-witness preservation

For deterministic scenarios in which candidate tests execute and produce a genuine assertion failure on the base implementation-side tree, `outcome-receipt-v1` will preserve acceptance at a rate not materially worse than the exit-code-only baseline.

### H3: contradiction detection

A valid-looking receipt whose semantic outcome contradicts the process exit code will be rejected as incomplete in every matrix state.

### H4: evidence binding

Changing the typed outcome, aggregate counts, producer identity, receipt digest, observer error, or invocation binding in an issued schema `0.3` report will invalidate `witness_sha256`.

## Methods to compare

### M0: final-state CI

```text
candidate implementation + candidate tests
```

A process success is accepted. All other outcomes are rejected or surfaced according to the host CI system.

### M1: four-state replay with exit codes

DeltaWitness `exit-code-v1` with configured pass and fail code classes.

### M2: four-state replay with typed receipts

DeltaWitness `outcome-receipt-v1` with a structured adapter and dual-channel receipt/exit consistency.

M1 and M2 use the same Git states, commands, timeouts, and expected matrix. Only the observation channel differs.

## Initial scenario taxonomy

Each scenario must have an independent ground-truth label assigned before execution.

| Family | Example | Ground-truth witness validity |
|---|---|---:|
| Assertion transition | Candidate assertion fails on base and passes on candidate | valid |
| Import failure | Candidate test imports a missing module | invalid |
| Discovery failure | Test module cannot be collected | invalid |
| Setup failure | Fixture or setup raises before the assertion | invalid |
| Teardown failure | Assertion passes but teardown raises | invalid |
| No tests | Selection matches no executable tests | invalid |
| All skipped | Every selected test is skipped | invalid |
| Expected-failure only | No normal pass or failure is observed | invalid for the default policy |
| Unexpected success | A test marked as expected failure passes | invalid / review-required |
| Missing receipt | Command never writes the expected document | invalid |
| Malformed receipt | Schema, JSON, counts, or fields are invalid | invalid |
| Binding mismatch | Receipt belongs to another state or invocation | invalid |
| Exit contradiction | Receipt says pass while process reports failure, or conversely | invalid |
| Timeout | Execution exceeds the declared bound | invalid / incomplete |

Future adapters may add framework-specific states, but they must map them into a versioned public protocol without collapsing error-class outcomes into `test_failure`.

## Primary metrics

### Unsafe Witness Acceptance Rate

```text
UW AR = accepted invalid witness scenarios / all invalid witness scenarios
```

The principal safety question is whether a method accepts an invalid scenario as satisfying the declared counterfactual pattern.

### Valid Witness Acceptance Rate

```text
VW AR = accepted valid witness scenarios / all valid witness scenarios
```

This guards against a trivial method that rejects everything.

### Incomplete Observation Rate

```text
IOR = incomplete scenarios / all scenarios
```

Incomplete is not equivalent to detected invalidity. The study must report evidence-driven rejection separately from abstention or harness incompleteness.

### Incremental cost

Record wall-clock duration, process count, receipt size, and report size. The typed channel must justify its operational overhead.

## Analysis plan

The first development evaluation will use paired scenarios so that M1 and M2 observe the same underlying repository state. Report paired outcomes and exact counts before fitting any aggregate model.

For a confirmatory corpus with clustered mutations, estimate method effects with uncertainty that accounts for scenario-family and repository dependence. The exact statistical model will be frozen in the DW-001 preregistration before held-out execution.

No scenario may be excluded merely because it makes one method incomplete. Exclusions require a protocol-level reason that applies symmetrically across methods and must be reported.

## Current implementation evidence

The `0.0.2` development suite includes synthetic tests for:

- a genuine assertion transition;
- import error not satisfying an expected regression failure;
- empty discovery;
- all-skipped execution;
- multiple failing subtests counted as one logical test outcome;
- missing receipts;
- oversized and symbolic-link receipts;
- duplicate JSON keys;
- binding mismatch;
- semantically inconsistent counts and outcomes;
- receipt/exit contradiction;
- typed evidence tampering invalidating both witness and full-report digests.

Passing these tests supports only implementation conformance on the synthetic fixtures. It is not an empirical estimate of real-world effectiveness.

## Falsification and redesign criteria

The typed-receipt approach should be narrowed, redesigned, or removed if:

- M2 does not materially reduce unsafe acceptance over a correctly configured M1 baseline;
- adapters cannot derive reliable typed outcomes from framework APIs;
- producer shadowing or execution-context manipulation dominates the result;
- valid witnesses are rejected at an impractical rate;
- receipt integration cost exceeds the detection benefit;
- existing standards provide a directly compatible, stronger observation protocol;
- external reproduction finds that the schema or count model is ambiguous.

## Trust boundary

The receipt binding is visible to the child process. It prevents accidental reuse, not deliberate forgery. The current producer executes inside the tested Python environment and can be affected by import resolution or malicious repository code.

Therefore:

- a receipt is not an attestation;
- typed semantics are not producer authentication;
- aggregate counts are not proof of oracle relevance;
- a matching matrix is not proof of patch correctness;
- untrusted repositories still require separate containment;
- signed provenance and trusted adapter execution remain future layers.

## Next experiment

Add the scenario families above to the DW-001 development corpus, then compare M1 and M2 with a frozen decision rule. Do not run the held-out corpus until:

1. the scenario manifest is committed and hashed;
2. the protocol and exclusions are frozen;
3. an external operator reproduces at least one development scenario;
4. receipt adapters and baseline wrappers are version-pinned;
5. the preregistration is timestamped outside the mutable Git branch.
