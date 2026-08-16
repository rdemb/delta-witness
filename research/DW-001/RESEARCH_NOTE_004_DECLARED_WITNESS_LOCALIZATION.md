# Research Note 004: Declared Logical-Test Witness Localization

**Status:** design decision for issue #26; implementation not yet accepted; DW-001 remains draft and unfrozen.

## Observation that triggered this note

The fixed `wrong-reason-unrelated-assertion` control produces:

```text
BB / BC / CB / CC = pass / fail / pass / pass
M0 / M1 / M2 / M3 = accept / accept / accept / accept
```

under both exit-code and typed-receipt observation.

The typed arm correctly records a genuine assertion failure. Direct controls nevertheless show that:

- the claim-facing viewer assertion passes on base and candidate implementations;
- an unrelated collateral version-label assertion is the sole source of `BC = fail`.

Therefore:

```text
real assertion failure
    + typed outcome
    + canonical four-state witness
    != claim-oracle relevance
```

## Current configuration capability

One `[[claim]]` contains one command. The command is integrity-bound to:

- claim ID;
- specification digest;
- observer;
- state;
- exact tree and commit;
- process and optional typed receipt evidence.

The command may already select one test, several tests, one file, or a complete suite. DeltaWitness therefore does **not** lack arbitrary command selection.

What it lacks is a separate machine-readable distinction between:

```text
claim witness selectors
    versus
broad regression guard command
```

and selector-specific evidence that is evaluated only in candidate-test states.

## Simpler-alternative analysis

### Alternative A: configure two ordinary claims

A natural proposal is:

1. one broad suite claim with `BC = any` and pass requirements for `BB`, `CB`, and `CC`;
2. one localized claim whose command selects the intended candidate test.

This does not work generally for candidate-added tests.

The ordinary claim command executes in all four states. A candidate-only logical test does not exist in the `BB` or `CB` test trees. Selecting it there correctly produces a load or discovery error, not semantic pass or fail. `expect = "any"` intentionally accepts only complete `pass` or `fail`; it does not convert missing-test or import errors into valid evidence.

Allowing state-dependent commands inside the canonical claim would alter the current four-state contract and make cross-state interpretation harder.

### Alternative B: make the broad suite command the declared witness

This preserves current mechanics but does not solve the observed ambiguity. The unrelated collateral assertion remains able to satisfy `BC = fail`.

### Decision

Retain the canonical four-state core unchanged. Evaluate a separate optional localization layer that runs declared candidate-test selectors only under:

```text
BC = base implementation + candidate tests
CC = candidate implementation + candidate tests
```

The layer must remain subordinate evidence. It cannot establish that an operator selected the semantically correct test.

## Direct baselines

### SWE-bench

SWE-bench datasets explicitly store `FAIL_TO_PASS` and `PASS_TO_PASS` test-case sets. This establishes test-case localization as a direct baseline, not a DeltaWitness novelty.

Source:

- `SWE-bench/SWE-bench`, dataset guide and grading implementation.

### TDD-Bench Verified

TDD-Bench Verified defines a prediction as tests that should fail on the old code and pass on the resolved code. Its paper and official repository state that the harness runs relevant tests in isolation and measures coverage over changed code.

Sources:

- IBM/TDD-Bench-Verified;
- arXiv:2412.02883.

### Framework selectors

Python `unittest` provides:

- `TestCase.id()` for a logical test identifier;
- `TestLoader.loadTestsFromName()` and `loadTestsFromNames()` for exact dotted-name selection.

pytest provides node IDs for exact module, class, method, and function selection.

The initial DeltaWitness adapter should use standard-library `unittest` only. A pytest adapter is a separate future contract.

### Test-oracle and adequacy literature

The test-oracle problem, mutation testing, assertion adequacy, and coincidental correctness are established.

Primary references:

- Earl T. Barr, Mark Harman, Phil McMinn, Muzammil Shahbaz, and Shin Yoo, “The Oracle Problem in Software Testing: A Survey,” IEEE Transactions on Software Engineering, DOI `10.1109/TSE.2014.2372785`;
- Yue Jia and Mark Harman, “An Analysis and Survey of the Development of Mutation Testing,” IEEE Transactions on Software Engineering, DOI `10.1109/TSE.2010.62`.

No novelty claim is made for logical test IDs, isolated execution, fail-to-pass, coverage, or mutation testing.

## Candidate artifact split

### Pre-execution declaration

Provisional schema name:

```text
deltawitness.claim-witness-declaration.v1
```

The declaration should contain:

- source specification digest;
- claim ID;
- adapter ID and version;
- ordered unique selectors;
- aggregate rule;
- canonical command derived from selectors by the adapter;
- declaration status and review metadata only if required by the study protocol;
- declaration digest.

Callers must not supply both selectors and an independent free-form command.

### Post-execution localization report

Provisional schema name:

```text
deltawitness.claim-witness-localization.v1
```

For every selector, record exact `BC` and `CC`:

- tree and commit IDs;
- invocation binding;
- observer;
- process status;
- typed receipt outcome and aggregate counts;
- selector classification;
- stable diagnostic code;
- no raw output by default.

The report must bind the declaration, source matrix report, claim, specification, and exact Git states.

## Initial classifications

Per selector:

```text
discriminating
    BC = typed assertion failure
    CC = pass

non_discriminating
    BC = pass
    CC = pass

candidate_invalid
    CC = complete fail

indeterminate
    BC or CC = error, timeout, missing selector,
    contradictory receipt, unsupported adapter behavior,
    or other incomplete observation
```

`indeterminate` is not converted into `non_discriminating`.

The aggregate rule must be fixed before execution. Initial candidate:

```text
at_least_one_discriminating_and_none_indeterminate
```

This rule remains provisional until positive and negative controls are evaluated.

## Controlled hypotheses

### H1: valid regression

The declared viewer-denial selector from `valid-discriminating-regression` is `discriminating`.

### H2: unrelated assertion

For `wrong-reason-unrelated-assertion`:

- the broad suite remains a complete accepted canonical witness;
- the declared claim-facing viewer selector is `non_discriminating`;
- the collateral version-label test may be fail-to-pass but is outside the declared witness set;
- localization therefore exposes a mismatch between broad-suite and declared-witness evidence.

### H3: import error

For `wrong-reason-base-import-failure`, selecting the candidate logical test remains `indeterminate` on `BC` because module import fails before test execution.

### H4: source substitution

A declaration or report paired with a different claim, selector list, canonical command, specification, matrix report, tree, commit, or observer is rejected even after all unkeyed digests are recomputed.

## Falsification and simpler-alternative criteria

Abandon or narrow the new layer if:

- an existing two-claim configuration provides equivalent evidence without state-dependent ambiguity;
- `unittest` logical IDs are unstable under the supported discovery boundary;
- selector execution materially changes fixture/setup semantics;
- valid controls are over-refused;
- declaration review cannot prevent post-result selector relabeling;
- the artifact adds no detection beyond direct command inspection;
- framework-specific complexity exceeds its evidentiary value;
- independent reviewers cannot distinguish declared localization from semantic relevance.

## Safety and privacy boundary

The proposed layer runs repository tests and is not a sandbox. It must use the same disposable, non-sensitive execution boundary as the matrix.

Public artifacts must not contain:

- absolute paths;
- usernames or credentials;
- environment values;
- raw traceback or process output;
- private source or test content;
- external endpoints.

Logical test IDs, commands, Git identities, counts, and digests may still be sensitive metadata and require publication review.

## Claim boundary

A valid localization report would establish only that exact operator-declared logical tests were requested and that their recorded `BC`/`CC` outcomes match the fixed classification rule under exact Git states.

It would not establish:

- that the declared selectors are semantically correct for the claim;
- complete oracle adequacy or strength;
- mutation or coverage adequacy;
- protection against a malicious adapter or repository;
- empirical effectiveness or generalization;
- authorization to block merges;
- protocol freeze, pilot, or holdout authorization;
- producer authentication or containment;
- independent reproduction;
- production readiness or scientific novelty.
