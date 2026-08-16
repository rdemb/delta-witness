# Claim-Witness Localization Threat Boundary

**Status:** applies to optional `unittest-test-id-v1` DW-001 development evidence. The protocol remains draft and unfrozen. This document does not authorize a pilot, holdout, merge blocker, or production deployment.

## Protected statement

The localization layer supports one narrow statement:

> For one verified source matrix report, one configured claim, one pre-execution declaration, and one ordered set of exact standard-library `unittest` selectors, DeltaWitness reconstructed the recorded Git states, executed each adapter-derived selector command under exact `BC` and `CC`, and produced the recorded typed selector classifications.

This statement does **not** establish that the declared selectors are semantically relevant, sufficient, strong, honest, or complete for the claim.

## Assets

The design protects:

- source specification, claim, broad matrix report, witness, base/head, state tree, and state commit identity;
- ordered selector identity and duplicate-free declaration semantics;
- canonical selector command derivation;
- separation of broad suite evidence from declared selector evidence;
- exact one-logical-test cardinality for normal selector receipts;
- producer name/version and invocation binding;
- preservation of missing, import, setup, producer, timeout, or contradictory execution as `indeterminate`;
- separation of `candidate_invalid` from ordinary non-discrimination;
- semantic and complete-report digests;
- fresh-checkout reconstruction of unreferenced synthetic matrix commits;
- exclusion of raw output and absolute local paths from public reports.

## Adversaries and failure sources

The model includes:

- an operator who declares a collateral but discriminating selector instead of the claim-facing selector;
- a selector declaration created or changed after results are visible;
- duplicate, reordered, malformed, path-like, or dynamically generated selectors;
- a free-form command that differs from declared selector semantics;
- a missing selector represented as a framework load error;
- one selector command that actually executes multiple logical tests;
- a receipt from another syntactically valid producer;
- a stale or substituted invocation binding;
- substituted source report, witness, specification, claim, base/head, tree, or commit identities;
- a fresh checkout that lacks unreferenced synthetic `BC`/`CB` commits;
- changed path classification, checkout behavior, Git configuration, or unsupported Git entries;
- a typed assertion failure caused by unrelated behavior;
- a malicious test or adapter that forges unsigned receipt evidence;
- nondeterministic selector behavior;
- non-finite durations, unhashable malformed values, duplicate JSON keys, or invalid UTF-8;
- raw traceback or output containing credentials or private data;
- coordinated replacement of the complete unkeyed artifact chain.

## Security and integrity invariants

1. A declaration uses exact fields and one supported adapter/version.
2. Claim IDs use the same restricted syntax as the core specification.
3. Selectors are fully qualified dotted `unittest` logical-test names.
4. Selector order is canonical artifact content; duplicates are rejected.
5. Every selector command is derived by the adapter and cannot be supplied independently.
6. The aggregate rule is fixed before execution.
7. The source matrix report is strict-decoded and semantically verified before localization.
8. The declaration specification and claim must match the supplied configuration and source report.
9. Base/head commits must resolve exactly in the current repository.
10. Current changed-path classification must equal the source report classification.
11. Unsupported submodule or symbolic-link changes remain rejected.
12. `BB`, `BC`, `CB`, and `CC` trees and commits are reconstructed deterministically and must match the source report exactly.
13. State reconstruction executes no test command and leaves the repository clean.
14. Localization executes only exact `BC` and `CC` commits from the verified report.
15. The command always uses `outcome-receipt-v1` and the canonical adapter command.
16. The invocation binding covers claim, command, specification, observer, state, tree, and commit.
17. Receipt producer name is exactly `deltawitness-unittest`.
18. Receipt producer version equals the localization report tool version.
19. A normal selector receipt represents exactly one logical test.
20. Missing selectors and import/setup/load errors remain typed `error` and classify as `indeterminate`.
21. Timeout remains `indeterminate`.
22. Candidate typed failure classifies as `candidate_invalid`, not `unsupported`.
23. `indeterminate` takes aggregate precedence over candidate invalidity and support.
24. The verifier reconstructs receipt bytes and requires exact receipt digest equality.
25. The verifier recomputes selector classifications and aggregate status.
26. Non-finite durations and malformed or unhashable fields fail closed with typed diagnostics.
27. `localization_sha256` binds stable localization semantics and exact source-report identity.
28. `report_sha256` binds the complete document.
29. Raw stdout and stderr are `null` in the public artifact.
30. Existing four-state matrix semantics remain unchanged and usable without localization.

## Residual risks

### Declaration honesty

The system proves which selectors were declared, not that they are the correct claim witnesses. A contributor can honestly declare a collateral selector unless governance or review detects the mismatch.

### Framework semantics

`unittest-test-id-v1` trusts standard-library discovery/loading behavior and the repository's import, fixture, setup, teardown, and monkeypatch semantics. A selector executed in isolation may not behave like the same test inside a complete suite.

### Unsigned cooperating producer

The receipt binding is visible to tested code and the producer is not authenticated. Producer-name and version checks prevent accidental substitution, not a malicious repository that can emit a syntactically valid receipt.

### No sandbox

Tests run with operator privileges inside the ordinary DeltaWitness execution boundary. They can access files, network, processes, credentials, and external systems available to that environment.

### Environment incompleteness

Exact Git objects do not bind Python, Git, dependencies, kernel, hardware, filesystem, locale, clock, network, container image, or external services.

### Nondeterminism

Each selector currently executes once. A stable selector ID and exact Git state do not establish deterministic behavior. Repetition and uncertainty remain future protocol work.

### Unkeyed integrity

All current digests are unkeyed. An actor able to replace the repository, declaration, source report, localization report, and all separately trusted digests can replace the complete chain.

### Semantic limitation

`discriminating` means only typed fail on `BC` and pass on `CC`. It does not establish that the selector asserts the intended behavior, covers changed code, resists coincidental correctness, or rejects plausible incorrect implementations.

## Safe operation

- Use only trusted repositories or a separately secured disposable environment without credentials.
- Require declarations to be fixed and reviewed before selector execution where a study protocol depends on them.
- Preserve broad suite evidence separately from selector localization.
- Treat `supported` as declared-set fail-to-pass evidence, not oracle validation.
- Review every `indeterminate` and `candidate_invalid` selector explicitly.
- Do not infer claim relevance from receipt failure counts.
- Do not publish logical test IDs, Git identities, commands, or digests without privacy review.
- Do not use this layer as an automatic merge blocker before empirical calibration.
- Do not mark Gate 0, protocol freeze, pilot authorization, or production readiness from localization evidence.

## Public wording boundary

Permitted:

> DeltaWitness can bind operator-declared logical unittest selectors to exact BC/CC typed observations and report whether the declared set contains a fail-to-pass selector.

Not permitted:

> DeltaWitness proved that the selected tests are the correct or sufficient oracle for the claim.

> A supported localization report proves patch correctness, security, production readiness, or deployment authorization.
