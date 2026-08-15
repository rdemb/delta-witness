# Threat Model

## Protected claims

DeltaWitness currently supports two narrow classes of statement.

### Canonical change witness

> Under declared commands and exact Git states, the candidate implementation-side tree changes the observed behavior relative to the base tree, while the candidate test-side tree acts as a counterfactual witness.

When a typed observer is enabled, the statement is further bounded by the semantic outcome reported by a cooperating test adapter.

### Exact patch influence

> For a bounded set of changed code paths, under the recorded test worlds and exact intervention states, selecting or removing each path changes the declared Boolean witness according to the complete coalition table and released attribution metrics.

Neither statement establishes full program correctness, universal causality, vulnerability removal, production safety, or authorization to deploy.

## Assets

The current design aims to protect:

- integrity of canonical and intervention state construction;
- binding between observations and exact Git objects;
- explicit claim boundaries and expectations;
- typed outcomes from accidental cross-claim or cross-state reuse;
- separation between complete failures and incomplete execution;
- deterministic path ordering and coalition identities;
- endpoint consistency between canonical and influence analyses;
- exactness of released coalition metrics;
- report integrity after generation;
- host environment variables from accidental inheritance;
- raw command output from accidental publication by default;
- separation between consecutive claims and coalitions.

## Adversaries and failure sources

The model includes:

- an AI coding agent that unintentionally creates a misleading patch, weak test, or collateral change;
- a contributor that deliberately weakens, skips, replaces, or misdirects a relevant oracle;
- a patch author who splits or groups changes across paths to manipulate file-level attribution;
- stale, unrelated, or incorrectly selected Git refs;
- hostile process-level Git environment overrides and replacement objects;
- changed paths that are omitted, multiply classified, or incorrectly labeled as documentation;
- documentation or configuration paths that influence execution while being held constant;
- filenames that break line-delimited parsing or trigger pathspec interpretation;
- changed submodule entries with unresolved external state;
- changed symbolic-link entries whose targets escape the declared path boundary;
- commands that return success without meaningful assertions;
- test runners that reuse one exit code for assertion, collection, import, setup, teardown, or infrastructure failures;
- missing, stale, malformed, oversized, contradictory, or state-mismatched receipts;
- a malicious command that reads its invocation binding and forges a syntactically valid receipt;
- invalid partial patches that break imports, schemas, generated artifacts, dependency relationships, or build graphs;
- nondeterministic tests that make coalition truth values unstable;
- combinatorial resource amplification caused by `2^n` exact interventions;
- background processes or persistent external effects that survive worktree resets;
- one claim or coalition contaminating a later execution through generated files or shared services;
- command output containing credentials or private data;
- tampering with generated reports or attribution metrics;
- misuse of Shapley, Banzhaf, or interaction values as proof of correctness, blame, or business value;
- sensitive command arguments, repository paths, or low-entropy output being exposed through a report;
- unrecorded toolchain, dependency, operating-system, or external-service drift;
- malicious repository content executed with the operator's privileges.

## Security and integrity invariants in v0.0.3

### Git and classification

1. Base and candidate resolve to different immutable commits.
2. The base commit is an ancestor of the candidate commit.
3. The repository is clean before every top-level analysis.
4. Git subprocesses ignore external repository, index, object-directory, global-config, and replacement-object overrides.
5. Git paths are read through a NUL-delimited interface and unsafe cross-platform paths are rejected.
6. Internal pathspecs are interpreted literally.
7. Every changed path is classified exactly once.
8. Changed Git submodule entries are rejected.
9. Changed symbolic-link entries are rejected before state materialization.

### Canonical matrix

10. Each matrix state has an exact tree ID and commit ID.
11. Hybrid states use deterministic synthetic commits.
12. Each claim begins from a reset and cleaned state commit.
13. Every matrix expectation is explicit.
14. Pass and fail exit-code classes are explicit and disjoint.
15. Timeouts and unknown exit codes mark the observation incomplete.

### Typed observations

16. Receipt-aware observations receive a deterministic binding over claim, command, specification, observer, state, tree, and commit.
17. Outcome receipts must be bounded regular files with strict UTF-8 JSON, exact fields, duplicate-key rejection, internally consistent counts, and an exact binding match.
18. A typed pass or failure is accepted only when receipt semantics and configured process exit codes agree.
19. Missing, malformed, inconclusive, or contradictory receipts mark the observation incomplete.
20. Receipt outcome, producer, counts, digest, binding, and observer error are included in the semantic digest.

### Exact influence

21. Exact influence starts only from a complete, supported canonical `pass / fail / pass / pass` witness.
22. Intervention units are the deterministic sorted set of changed paths classified as code.
23. Exact analysis is rejected above eight changed code paths.
24. Every one of the `2^n` coalitions is executed; no result is silently sampled, pruned, or imputed.
25. Every coalition is evaluated under both base and candidate test worlds.
26. Candidate documentation paths are held constant and explicitly recorded.
27. Four endpoint anchors compare influence endpoints with the canonical matrix.
28. Full-coalition trees must equal canonical candidate-side trees.
29. Empty-coalition semantics must match canonical base-side outcomes; empty tree equality is additionally required when no documentation changed.
30. Any incomplete coalition withholds all exact attribution metrics.
31. Any endpoint inconsistency withholds all exact attribution metrics.
32. An empty coalition that already satisfies the witness or a full coalition that does not satisfy it withholds attribution.
33. No monotonicity assumption is used; negative marginal edges are preserved.
34. Shapley, Banzhaf, and interaction values are computed with exact rational arithmetic before decimal rendering.
35. Exact metrics, anchors, coalition identities, Git objects, and observer evidence are included in `influence_sha256`.

### Execution and publication

36. Commands execute without a shell.
37. The full host environment is not inherited.
38. Raw output is excluded unless explicitly requested.
39. Absolute repository and specification paths are excluded from reports.
40. Default reports are stored in private Git metadata rather than the working tree.
41. Ambiguous configuration and harness errors stop the analysis.
42. Semantic and complete-report digests are independently verifiable.

## Residual risks

### No operating-system sandbox

The runner is not a security sandbox. Repository-local Git configuration, attributes, generic clean/smudge filters, platform checkout rules, unchanged symbolic links, and the shared object database can still influence materialization or execution.

A command can still:

- read or modify files accessible to the current operating-system user;
- access the network;
- start background processes;
- consume excessive CPU, memory, storage, process, or network resources;
- inspect or modify the shared Git object store or refs through linked worktrees;
- affect external databases, services, caches, or queues;
- exploit the interpreter, Git, kernel, or another local dependency;
- deliberately forge a receipt using the binding exposed in its environment.

Exact influence multiplies these risks across all coalitions. Use a separately secured disposable environment for code that is not fully trusted.

### State construction is not a complete environment model

The witness binds Git trees and commits, not the complete operating-system image, executable binaries, dependency graph, compiler, interpreter, kernel, locale database, hardware, clock, network responses, or external service state.

Equivalent Git states can produce different observations in different environments. Identical exit codes or receipts do not establish equivalent execution.

Repository-local filters and generated artifacts can also create worktree content not represented solely by the recorded blob IDs. This remains a known limitation until materialization is moved into a locked reproducible environment with independent tree verification after checkout.

### Changed-link rejection is narrow

Rejecting changed symbolic-link entries prevents overlays across modified link boundaries. It does not prove that every unchanged path reachable by a command is a regular file or repository-contained, and it does not prevent commands from following existing links elsewhere on the filesystem.

### Typed receipts are cooperating-producer evidence

`exit-code-v1` remains coarse and may confuse assertion failure with other failure classes.

`outcome-receipt-v1` improves semantic precision for a cooperating adapter, but the binding is visible and the receipt is unsigned. It prevents accidental reuse and detects malformed or contradictory evidence; it does not authenticate the producer, establish adapter integrity, or prove oracle relevance.

The built-in `unittest` producer executes inside the tested Python environment and can be influenced by import resolution or malicious repository code.

### Path-level interventions are coarse

A path can contain multiple semantic changes, and one semantic change can span multiple paths. Renaming, splitting, or combining files can alter the coalition game without altering intended behavior.

A zero influence value means only that a path did not change the declared witness across the recorded coalitions. It does not prove that the path is unnecessary in production or irrelevant to untested behavior.

A high value means only that the path changes the witness frequently or necessarily under the chosen units. It does not prove correctness, desirability, severity, ownership, or blame.

### Invalid hybrid states

Partial interventions can create states that no developer would intentionally build. Missing imports, incompatible schemas, generated-code drift, dependency mismatches, or setup errors make a coalition indeterminate.

The current protocol correctly withholds exact metrics when any coalition is indeterminate, but this may make the method inapplicable to many tightly coupled patches. A low applicability rate is a possible negative research result, not a reason to reinterpret errors as failures.

### Held-constant documentation can hide interactions

Candidate documentation changes are held constant so the full coalition matches the candidate. Endpoint anchors detect some execution leakage, but intermediate interactions between documentation-labeled paths and selected code paths may remain.

Execution-sensitive configuration should be classified as code. Classification policy remains an operator responsibility.

### Nondeterminism

Version `0.0.3` executes each state once. A flaky test can produce an unstable coalition table and misleading exact metrics even though enumeration is combinatorially complete.

Repeated execution, uncertainty estimates, stochastic witness functions, and stability thresholds remain future work. Until then, exact refers to subset enumeration, not certainty about a stochastic system.

### Resource amplification

At eight code paths and one claim, influence analysis can invoke 512 coalition commands plus the canonical matrix. Multiple claims multiply that cost. Background work, disk growth, external side effects, and rate limits can compound across executions.

The current implementation has per-command timeouts but does not impose complete CPU, memory, process-count, storage, or network limits.

### Report integrity is not authentication

`witness_sha256`, `influence_sha256`, and `report_sha256` are unkeyed. They detect modification only when compared with separately trusted values. An attacker who can replace a report can recompute all digests.

Signing, DSSE, in-toto statements, Sigstore, environment provenance, and producer identity remain future layers.

### Publication metadata can still be sensitive

Reports record declared commands, changed paths, claim descriptions, Git object IDs, observer metadata, selected path coalitions, output digests, and aggregate counts. Command arguments must not contain secrets. Output and receipt digests can reveal equality and can be brute-forced when the underlying value has low entropy.

Every exported report requires human review.

## Safe operation

- Run DeltaWitness only on repositories and commands you trust.
- Use an isolated, disposable, resource-bounded environment without production credentials for all other code.
- Prefer typed observers when a trusted adapter exists, but never treat a receipt as an attestation.
- Classify every execution-sensitive manifest, configuration file, generated-code input, and build script as code.
- Review endpoint anchors and every indeterminate coalition before interpreting influence.
- Treat exact influence as exact enumeration over declared path units, not proof of full causality.
- Review every report before publication, especially reports generated with `--include-output`.
- Never interpret `SUPPORTED_IN_SCOPE` or `ATTRIBUTION_AVAILABLE` as proof that a patch is correct, secure, complete, minimal, production-ready, or authorized for deployment.
