# Declared Claim-Witness Localization v1

**Status:** optional DW-001 development evidence; protocol remains draft and unfrozen; no pilot or holdout execution is authorized.

## Purpose

The canonical four-state matrix answers whether the configured claim command produces the declared `BB / BC / CB / CC` pattern. A command may run one test, a selector set, one file, or a complete suite.

The fixed `wrong-reason-unrelated-assertion` negative control demonstrates a limitation:

```text
real assertion failure
    + typed outcome
    + canonical four-state witness
    != claim-oracle relevance
```

Its claim-facing viewer assertion passes against both implementations. A collateral version-label assertion is the sole source of `BC = fail`. Both observer arms and all nested matrix methods nevertheless accept.

Declared claim-witness localization adds a narrower question:

> Which exact operator-declared logical tests were requested under `BC` and `CC`, and what typed outcomes did those selectors produce?

It does not answer whether the operator selected the semantically correct tests.

## Why this is a separate layer

One ordinary `[[claim]]` command executes in all four matrix states. A candidate-added logical test does not exist in the `BB` or `CB` test trees. Selecting it there correctly produces a missing-test or load error rather than valid evidence.

Allowing state-dependent commands inside the canonical claim would change the four-state contract and make cross-state interpretation ambiguous.

Localization therefore:

- leaves the canonical matrix unchanged;
- requires an already verified source matrix report;
- executes declared candidate-test selectors only under exact `BC` and `CC` states;
- preserves the broad suite report as a separate regression guard;
- records a separate declaration and localization report.

The simpler-alternative analysis and direct baseline table are recorded in:

```text
research/DW-001/RESEARCH_NOTE_004_DECLARED_WITNESS_LOCALIZATION.md
```

## Initial adapter boundary

Adapter v1:

```text
id      = unittest-test-id-v1
version = 1
```

A selector is a fully qualified dotted standard-library `unittest` logical-test name, for example:

```text
test_access.AccessTests.test_viewer_is_denied
```

The adapter derives the only accepted command:

```text
python -m deltawitness.unittest_probe \
    --start-directory tests \
    --verbosity 0 \
    --test-name <selector>
```

Callers cannot provide an independent free-form selector command.

The built-in producer loads exact names through `unittest.TestLoader.loadTestsFromNames`. Normal selector evidence must report exactly one logical test. Missing selectors are represented by unittest's failed-test object and remain typed `test_error`, not `no_tests` or `non_discriminating`.

Unsupported dynamic suites, unstable generated identifiers, custom discovery semantics, or test frameworks other than standard-library `unittest` remain outside adapter v1.

## Pre-execution declaration

Schema:

```text
research/DW-001/schema/claim-witness-declaration.schema.json
```

Implementation:

```text
src/deltawitness/_claim_witness.py
src/deltawitness/claim_witness.py
```

The declaration records:

- schema version;
- source specification digest;
- configured claim ID;
- adapter ID and version;
- ordered unique selector list;
- fixed aggregate rule;
- adapter-derived command for every selector;
- `declaration_sha256` over canonical bytes with its own field normalized to `null`.

The declaration is pre-execution metadata. Reordering selectors changes canonical bytes. Duplicate, malformed, path-like, NUL-containing, or incomplete identifiers fail closed.

A valid declaration establishes only that the listed selectors and canonical commands are internally consistent. It does not establish that the selectors are relevant, sufficient, independent, or honestly chosen before results were visible.

## Source-report preconditions

Localization accepts one source matrix report that:

- uses schema `0.3`;
- was strict-decoded as UTF-8 JSON with duplicate-key rejection;
- passes matrix semantic and complete-report verification;
- contains exactly one configured claim matching the declaration claim ID;
- uses the same specification digest and configured broad command;
- records exact base/head and state tree/commit identities.

The source report may be complete or incomplete. This is intentional:

- a complete supported broad report can be compared with selector-specific localization;
- an incomplete import-error report can demonstrate selector indeterminacy;
- source incompleteness is not rewritten into selector non-discrimination.

The layer is diagnostic development evidence. A future confirmatory protocol must decide whether incomplete broad reports are eligible for any denominator.

## Exact state reconstruction

A source report can reference deterministic synthetic `BC` and `CB` commits that exist in the producer repository but are not referenced by branches and may not exist in an equivalent fresh checkout.

Before localization, the public boundary:

1. resolves exact base/head commits in the current repository;
2. re-enumerates changed paths under the supplied configuration;
3. requires identical code/test/documentation classification;
4. rejects unsupported Git entries;
5. reconstructs `BC` and `CB` trees by crossing exact test paths;
6. recreates deterministic synthetic commits using the canonical metadata contract;
7. requires all reconstructed `BB / BC / CB / CC` trees and commits to match the source report exactly;
8. requires the repository to remain clean.

No test command is executed during reconstruction.

This permits an equivalent fresh checkout with a different directory name to use the same source report while retaining exact Git-object identity. Failure to reproduce any tree, commit, classification, or specification stops localization.

## Selector execution

Every declared selector is executed independently under:

```text
base_candidate
candidate_candidate
```

For each state, the report records:

- exact state tree and commit;
- canonical selector command;
- invocation binding over claim, command, specification, observer, state, tree, and commit;
- process status and timeout;
- output digests;
- typed receipt digest, outcome, producer, and aggregate counts;
- stable observation error;
- raw stdout and stderr as `null`.

The required producer is:

```text
name    = deltawitness-unittest
version = localization.tool_version
```

For normal receipt outcomes, `tests_run` must equal exactly one. A syntactically valid receipt from another producer or a receipt claiming more than one logical test is rejected even if its unkeyed digest is recomputed.

The invocation binding is recomputed by the verifier. Substitution of selector, command, claim, specification, tree, commit, observer, producer, counts, or source report fails closed.

## Per-selector classifications

### `discriminating`

```text
BC = typed assertion failure
CC = pass
```

### `non_discriminating`

```text
BC = pass
CC = pass
```

### `candidate_invalid`

```text
CC = complete typed assertion failure
```

Candidate invalidity is not collapsed into ordinary non-discrimination.

### `indeterminate`

At least one state is:

- `error`;
- `timeout`;
- missing selector;
- missing, malformed, stale, or contradictory receipt;
- producer error;
- unsupported adapter behavior;
- otherwise incomplete.

`indeterminate` is never converted into `non_discriminating`.

## Aggregate rule

Adapter v1 fixes one aggregate rule before execution:

```text
at_least_one_discriminating_and_none_indeterminate
```

Precedence:

```text
any indeterminate       -> indeterminate
else any candidate_invalid -> candidate_invalid
else any discriminating -> supported
else                    -> unsupported
```

A mixed declaration with one non-discriminating selector and one discriminating selector is therefore `supported`. This means only that the declared set contains at least one observed fail-to-pass selector and no incomplete or candidate-invalid selector.

It does not establish that the discriminating selector is the correct claim oracle.

## Controlled evidence

### Valid regression control

The declared viewer-denial test in `valid-discriminating-regression` is `discriminating`.

### Unrelated-assertion negative control

For `wrong-reason-unrelated-assertion`:

- the broad suite remains a complete supported canonical matrix;
- the declared claim-facing viewer selector is `non_discriminating`;
- the collateral version-label selector is separately `discriminating`;
- declarations for those selectors have different digests;
- the collateral selector is not silently substituted into the claim declaration.

### Import-error control

For `wrong-reason-base-import-failure`, the candidate selector remains `indeterminate` on `BC` because module import fails before the logical test executes.

### Missing-selector control

A missing dotted test name produces typed `test_error` with one failed-test object and remains `indeterminate`.

## Integrity model

The localization report contains:

- declaration digest;
- exact source matrix report digest;
- source witness digest;
- specification digest;
- claim ID;
- base/head commits;
- adapter and aggregate rule;
- ordered selector results;
- `localization_sha256`;
- `report_sha256`.

`localization_sha256` covers the source binding and stable selector semantics while excluding volatile timestamp, durations, and raw output. Because it binds the exact source report digest, it identifies one particular source-report artifact rather than all independently repeated equivalent reports.

`report_sha256` covers the complete localization document with its own field normalized to `null`.

Both digests are unkeyed. An actor able to replace the declaration, source report, localization report, repository, and all separately trusted expected digests can replace the complete chain.

The layer provides integrity and relation checks, not producer authentication, non-repudiation, proof of time, or append-only history.

## Reproducibility boundary

Normative tests require:

- the same declaration to serialize identically;
- the same descriptor to materialize identical Git identities in different directories;
- source report synthetic state objects to be reconstructed in a fresh equivalent checkout;
- the same source report and declaration to yield the same localization semantic digest across directory names;
- worktrees and repositories to remain clean.

The evidence does not bind the full Python, Git, dependency, kernel, filesystem, hardware, locale, or container environment.

## Privacy and publication

Public artifacts must not include:

- raw process output or traceback;
- absolute local paths;
- usernames, credentials, or environment values;
- private source or test bytes;
- confidential endpoints;
- undeclared extra fields.

Logical test IDs, relative commands, Git identities, producer metadata, counts, and digests can still reveal project structure or equality and require publication review.

## Prior-art boundary

Test-case identifiers, isolated test execution, fail-to-pass validation, SWE-bench `FAIL_TO_PASS` and `PASS_TO_PASS` sets, TDD-Bench relevant-test execution, pytest node IDs, test-oracle analysis, mutation testing, and coincidental correctness are established.

No novelty claim is made for selectors, isolated execution, or fail-to-pass classification.

The narrow DeltaWitness contribution under evaluation is an integrity-bound relation among:

```text
operator declaration
    -> claim and specification
    -> adapter-derived selector command
    -> exact BC/CC Git states
    -> typed per-selector evidence
    -> broad source matrix report
```

Whether this relation improves real review outcomes remains an empirical question.

## Safety boundary

The layer executes repository tests and is not a sandbox. Exact selectors can still:

- read or modify accessible files;
- use the network;
- start processes;
- consume resources;
- affect external systems;
- exploit dependencies;
- forge an unsigned visible receipt binding.

Use only trusted repositories or a separately secured disposable environment without credentials or unrelated data.

## Non-claims

A valid declaration or localization report does not establish:

- that the operator selected the semantically correct tests;
- oracle adequacy or strength;
- mutation adequacy or changed-code coverage;
- protection against malicious tests, adapters, or runners;
- complete claim intent;
- empirical effectiveness, prevalence, or generalization;
- authorization to block merges;
- protocol freeze, pilot, or holdout authorization;
- producer authentication or containment;
- independent reproduction or Gate 0 completion;
- production readiness or scientific novelty.

The correct public description is:

> DeltaWitness can bind operator-declared logical unittest selectors to exact BC/CC typed observations and expose whether that declared set contains a fail-to-pass selector. It does not prove that the declaration is the right oracle for the claim.
