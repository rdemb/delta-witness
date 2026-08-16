# Threat Model

## Protected claims

DeltaWitness currently supports four narrow classes of statement.

### Canonical change witness

> Under declared commands and exact Git states, the candidate implementation-side tree changes the observed behavior relative to the base tree, while the candidate test-side tree acts as a counterfactual witness.

When a typed observer is enabled, the statement is further bounded by the semantic outcome reported by a cooperating test adapter.

### Exact patch influence

> For a bounded set of changed code paths, under the recorded test worlds and exact intervention states, selecting or removing each path changes the declared Boolean witness according to the complete coalition table and released attribution metrics.

### DW-001 baseline projection

> Given one integrity-verified schema `0.3` matrix report, one homogeneous observer arm, a scenario identifier, and an independently declared applicability annotation, the projection records deterministic decisions for the nested `M0_FINAL`, `M1_F2P`, `M2_F2P_P2P`, and `M3_FOUR_STATE` predicates without exposing undeclared state observations to weaker methods.

### DW-001 study contracts

> Given one pre-execution scenario manifest, one verified DW-001 projection, and one post-execution result record, the contract verifiers recompute ground-truth method labels, partition and review eligibility, exclusions, deviations, cost missingness, method outcomes, denominator membership, and explicit manifest–projection–result bindings.

None of these statements establishes full program correctness, universal causality, vulnerability removal, production safety, empirical superiority, scientific novelty, or authorization to deploy or execute a held-out study.

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
- integrity and semantic consistency of matrix, influence, projection, scenario-manifest, and result-record artifacts;
- hidden-state isolation between nested DW-001 methods;
- homogeneous observer-arm separation in DW-001 projections and results;
- explicit separation between pre-execution non-applicability and observed execution failure;
- source-report identities recorded by projections and results;
- pre-execution ground truth from post-execution evidence;
- development and committed-holdout partition declarations;
- public-safe ownership, licensing, and authorization provenance;
- reviewer identity, independence disclosure, decision, and rationale;
- exclusion and deviation records from silent denominator removal;
- exact denominator membership and missing-cost semantics;
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
- ancestor/descendant changed paths from file-to-directory or directory-to-file transitions that make declared path units overlap;
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
- tampering with generated reports, attribution metrics, projected method decisions, scenario ground truth, or result records;
- recomputing an unkeyed digest after changing applicability, partition, review status, method labels, exclusions, deviations, cost data, or denominator membership;
- leaking a hidden matrix state into a weaker projected method;
- mixing exit-code and typed-receipt observers inside one projected comparison arm;
- labeling an execution error as `not_applicable` after observing the result;
- relabeling a holdout scenario as development or changing holdout membership after unblinding;
- constructing a holdout manifest with a digest that was not externally committed before execution;
- omitting or falsifying ownership, license, or authorization provenance;
- approving ground truth without a reviewer independent of the implementation;
- changing stored method ground truth without changing its constituent state labels;
- linking a result to the wrong manifest, projection, matrix report, or witness digest;
- excluding an unfavorable result while leaving it eligible for the primary denominator;
- applying an unapproved protocol deviation or preserving confirmatory eligibility after an exploratory-only deviation;
- encoding missing execution or review costs as zero;
- replacing the complete source report, projection, manifest, result, and expected digest set;
- misuse of Shapley, Banzhaf, interaction, projected baseline decisions, or study-contract concordance as proof of correctness, blame, or business value;
- sensitive command arguments, repository paths, reviewer identifiers, authorization references, scenario labels, or low-entropy output being exposed through an artifact;
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
7. Every changed path is classified exactly once, and the complete changed-path set is prefix-free; ancestor/descendant pairs are rejected before any state materialization.
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

### DW-001 projection

36. Projection starts from a schema `0.3` matrix report whose semantic and complete-report digests verify.
37. Every source claim uses the canonical DW-001 expectations and one homogeneous supported observer arm.
38. The ordered method state sets are fixed as `CC`, `BC+CC`, `BC+CB+CC`, and `BB+BC+CB+CC`.
39. Each method payload contains only its declared required state observations.
40. `not_applicable` comes only from an external state-to-reason declaration and is never inferred from execution output.
41. For applicable methods, an indeterminate required state takes precedence over a contradictory complete state.
42. The projection verifier requires exact root and nested field sets, canonical identifiers, ordered methods, and ordered state slices.
43. The verifier independently recomputes claim decisions, method decisions, reason codes, contradicted states, indeterminate states, and applicability partitions before accepting the projection digest.
44. A state shared by multiple nested methods must have an identical serialized observation in every method that exposes it.
45. `projection_sha256` covers the complete projection with its own field normalized to `null`.
46. A standalone projection cannot establish correspondence to source-report bytes; the retained source report must be strict-decoded, verified separately, and compared with the projection's recorded source identity.

### DW-001 study contracts

47. Scenario manifests and result records use exact root and nested field sets with deterministic method and state ordering.
48. A scenario manifest is sealed only after its semantic invariants pass.
49. Development manifests require an uncommitted development partition lock; holdout manifests require a 64-character commitment digest and `dw001-holdout-index-v1` scope.
50. The manifest verifier recomputes provenance conditions, distinct Git endpoints, disjoint prefix-free paths, observer IDs, disjoint exit classes, state applicability, expected observations, and failure-cause consistency.
51. Stored method ground-truth labels and reason codes are recomputed from ordered state ground truth and are never trusted as free-form labels.
52. An approved manifest requires an approving reviewer independent of both the scenario author and the implementation; a rejection takes precedence.
53. Manifest-level denominator eligibility is recomputed from holdout partition, approved review, and method applicability.
54. A result record is sealed only after its semantic invariants pass.
55. Included results carry no exclusion metadata; excluded results require a code, reason, and decision reference.
56. Applied deviations require approval references. Rejected deviations carry no approval or confirmatory impact. Exploratory-only and excluded deviations remove primary-denominator eligibility.
57. Expected and observed four-way decisions, reason codes, concordance, denominator eligibility, and denominator reason codes are recomputed before accepting the result digest.
58. Measured costs require finite nonnegative values. `not_run` and `unavailable` require null quantitative values and an explicit missing reason.
59. Cross-artifact verification independently validates the manifest, projection, and result and then compares scenario, partition, Git endpoints, observer arm, applicability, method decisions, concordance, source digests, and denominator membership.
60. `manifest_sha256` and `result_sha256` cover their complete artifacts with their own fields normalized to `null`.
61. The schemas define structural interoperability; the Python verifier remains authoritative for relational and cross-artifact invariants.
62. A scenario commitment recorded inside a manifest does not establish that the commitment predates execution; externally timestamped immutable recording remains required before a holdout.

### Execution and publication

63. Commands execute without a shell.
64. The full host environment is not inherited.
65. Raw output is excluded unless explicitly requested.
66. Absolute repository and specification paths are excluded from reports.
67. Default reports are stored in private Git metadata rather than the working tree.
68. Ambiguous configuration and harness errors stop the analysis.
69. Semantic and complete-artifact digests are independently verifiable within their documented boundaries.

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

Rejecting changed symbolic-link entries prevents overlays across modified link boundaries. It does not establish that every unchanged path reachable by a command is a regular file or repository-contained, and it does not prevent commands from following existing links elsewhere on the filesystem.

### Typed receipts are cooperating-producer evidence

`exit-code-v1` remains coarse and may confuse assertion failure with other failure classes.

`outcome-receipt-v1` improves semantic precision for a cooperating adapter, but the binding is visible and the receipt is unsigned. It prevents accidental reuse and detects malformed or contradictory evidence; it does not authenticate the producer, establish adapter integrity, or establish oracle relevance.

The built-in `unittest` producer executes inside the tested Python environment and can be influenced by import resolution or malicious repository code.

### Path-level interventions are coarse

A path can contain multiple semantic changes, and one semantic change can span multiple paths. Renaming, splitting, or combining files can alter the coalition game without altering intended behavior.

The current materializer additionally refuses file-to-directory and directory-to-file transitions when Git reports both an ancestor and descendant changed path. Supporting those transitions would require a different intervention-unit model or explicit grouping semantics; silently treating both paths as independent would make coalition membership diverge from the materialized tree.

A zero influence value means only that a path did not change the declared witness across the recorded coalitions. It does not establish that the path is unnecessary in production or irrelevant to untested behavior.

A high value means only that the path changes the witness frequently or necessarily under the chosen units. It does not establish correctness, desirability, severity, ownership, or blame.

### Invalid hybrid states

Partial interventions can create states that no developer would intentionally build. Missing imports, incompatible schemas, generated-code drift, dependency mismatches, or setup errors make a coalition indeterminate.

The current protocol correctly withholds exact metrics when any coalition is indeterminate, but this may make the method inapplicable to many tightly coupled patches. A low applicability rate is a possible negative research result, not a reason to reinterpret errors as failures.

### Held-constant documentation can hide interactions

Candidate documentation changes are held constant so the full coalition matches the candidate. Endpoint anchors detect some execution leakage, but intermediate interactions between documentation-labeled paths and selected code paths may remain.

Execution-sensitive configuration should be classified as code. Classification policy remains an operator responsibility.

### DW-001 projections are controlled ablations, not source attestations

A projection intentionally copies only the state slices needed by each nested method. Its semantic verifier can establish internal consistency of the serialized projection, but it cannot reconstruct omitted source-report fields or establish that the recorded source digests correspond to retained source bytes.

The source matrix report and projection must therefore be verified separately and linked through a trusted comparison of their recorded digests. An attacker able to replace both artifacts can recompute all current unkeyed digests.

Scenario identifiers and non-applicability reasons require a separately governed manifest. A projection verifier cannot determine whether ground truth was fixed independently, relabeled after observing results, or authorized for use in a held-out study.

### Study contracts are not preregistration or authentication

The scenario-manifest verifier can establish internal consistency of the recorded ground truth, partition lock, provenance fields, and reviewer declarations. It cannot establish that:

- the ground truth was authored before execution;
- the reviewer is the claimed person;
- the reviewer was organizationally independent;
- the license or authorization reference is genuine or sufficient;
- the holdout commitment was publicly recorded before unblinding;
- an omitted scenario never existed;
- the complete holdout index matches a privately retained corpus.

The result verifier and cross-artifact verifier can identify inconsistent links among supplied artifacts. They cannot detect coordinated replacement of the complete artifact chain and all expected unkeyed digests.

A development or holdout executor can still violate an external protocol rule without recording a deviation. Detection depends on execution logs, independent review, and immutable workflow evidence outside these artifacts.

The current protocol remains a development-pilot draft. Contract conformance does not authorize pilot or holdout execution and does not establish empirical effectiveness.

### Nondeterminism

Version `0.0.3` executes each state once. A flaky test can produce an unstable coalition table and misleading exact metrics even though enumeration is combinatorially complete.

Repeated execution, uncertainty estimates, stochastic witness functions, and stability thresholds remain future work. Until then, exact refers to subset enumeration, not certainty about a stochastic system.

### Resource amplification

At eight code paths and one claim, influence analysis can invoke 512 coalition commands plus the canonical matrix. Multiple claims multiply that cost. Background work, disk growth, external side effects, and rate limits can compound across executions.

The current implementation has per-command timeouts but does not impose complete CPU, memory, process-count, storage, or network limits.

### Artifact integrity is not authentication

`witness_sha256`, `influence_sha256`, `report_sha256`, `projection_sha256`, `manifest_sha256`, and `result_sha256` are unkeyed. They detect modification only when compared with separately trusted values. An attacker who can replace an artifact can recompute its digests.

Signing, DSSE, in-toto statements, Sigstore, immutable timestamping, environment provenance, and producer identity remain future layers.

### Publication metadata can still be sensitive

Reports, projections, manifests, and results can record declared commands, changed paths, claim descriptions, Git object IDs, observer metadata, scenario identifiers, applicability reasons, reviewer identifiers and rationales, license or authorization references, exclusions, deviations, output digests, aggregate counts, and cost data.

Command arguments, reviewer records, authorization references, and scenario metadata must not contain secrets or private infrastructure details. Output and receipt digests can reveal equality and can be brute-forced when the underlying value has low entropy.

Every exported artifact requires human review.

## Safe operation

- Run DeltaWitness only on repositories and commands you trust.
- Use an isolated, disposable, resource-bounded environment without production credentials for all other code.
- Prefer typed observers when a trusted adapter exists, but never treat a receipt as an attestation.
- Classify every execution-sensitive manifest, configuration file, generated-code input, and build script as code.
- Review endpoint anchors and every indeterminate coalition before interpreting influence.
- Treat exact influence as exact enumeration over declared path units, not proof of full causality.
- Strict-decode and verify the source matrix report, projection, scenario manifest, and result separately; then verify explicit cross-artifact bindings.
- Treat scenario applicability and expected outcomes as pre-execution ground truth, not values inferred from failed commands.
- Independently review license and authorization references before using external material.
- Do not interpret a manifest's internal commitment field as proof of a timely holdout commitment; record the complete commitment externally before execution.
- Preserve excluded results and deviations rather than deleting them from the evidence chain.
- Do not execute a DW-001 development pilot or holdout while the protocol is marked draft or before the corresponding authorization and freeze gates are complete.
- Review every report, projection, manifest, and result before publication, especially artifacts containing non-public scenario or reviewer metadata.
- Never interpret `SUPPORTED_IN_SCOPE`, `ATTRIBUTION_AVAILABLE`, a projected `accept`, or a concordant result as proof that a patch is correct, secure, complete, minimal, empirically superior, production-ready, or authorized for deployment.
