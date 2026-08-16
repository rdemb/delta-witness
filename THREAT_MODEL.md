# Threat Model

## Protected claims

DeltaWitness currently supports six narrow statement classes.

### Canonical change witness

> Under declared commands and exact Git states, the candidate implementation-side tree changes the observed behavior relative to the base tree, while the candidate test-side tree acts as a counterfactual witness.

A typed observer further bounds the statement by the semantic outcome reported by a cooperating adapter.

### Exact patch influence

> For at most eight changed code paths, under the recorded test worlds and exact intervention states, selecting or removing each path changes the declared Boolean witness according to the complete coalition table and released exact metrics.

### DW-001 baseline projection

> Given one verified schema `0.3` matrix report, one homogeneous observer arm, a scenario identifier, and independently declared applicability, the projection records deterministic `M0_FINAL`, `M1_F2P`, `M2_F2P_P2P`, and `M3_FOUR_STATE` decisions without exposing undeclared state outcomes to weaker methods.

### DW-001 study contracts

> Given one pre-execution scenario manifest, one verified projection, and one post-execution result, the contract verifiers recompute ground-truth labels, partition and review eligibility, exclusions, deviations, costs, outcomes, denominator membership, and explicit manifest–projection–result relations.

### DW-001 synthetic fixture identity

> Given one verified supported descriptor and one trusted literal destination, the owned-synthetic generator materializes fixed template bytes into exact Git objects and emits a public-safe identity whose descriptor, Git, specification, state, and method semantics can be rechecked.

### DW-001 fixture-manifest binding

> Given one verified fixture descriptor, fixture identity, and scenario manifest, the binding verifier checks their shared study, scenario, commit, path, execution, observer, state, method, family, and specification relations without mutating any issued v1 source schema.

None of these statements establishes full program correctness, universal causality, vulnerability removal, production safety, empirical superiority, scientific novelty, legal admissibility, or authorization to deploy, run a pilot, or execute a holdout.

## Assets

The design aims to protect:

- exact canonical, hybrid, and coalition Git state identity;
- complete changed-path classification and deterministic intervention units;
- claim, command, specification, observer, state, tree, and commit bindings;
- separation of assertion failure from execution or infrastructure failure;
- separation of unsupported evidence from incomplete execution;
- endpoint consistency between canonical and influence analyses;
- completeness and exact arithmetic of released influence metrics;
- semantic and complete-artifact integrity of matrix and influence reports;
- hidden-state isolation and homogeneous observer arms in DW-001 projections;
- pre-execution ground truth from post-execution evidence;
- development and holdout partition declarations;
- reviewer, exclusion, deviation, denominator, and cost semantics;
- deterministic fixture descriptor, identity, Git, and specification semantics;
- explicit correspondence between a generated fixture and scenario manifest;
- preservation of manifest-owned governance fields during fixture binding;
- public artifacts from accidental disclosure of absolute paths, environment values, credentials, private output, or unauthorized material;
- separation between consecutive claims, coalitions, scenarios, and study artifacts.

## Adversaries and failure sources

The model includes:

- an AI coding agent that unintentionally creates a misleading patch, weak test, collateral change, or self-confirming result;
- a contributor that deliberately weakens, skips, replaces, or misdirects an oracle;
- a patch author that splits or groups changes to manipulate path-level attribution;
- stale, unrelated, incorrectly selected, or substituted Git refs;
- hostile process-level Git overrides, replacement objects, hooks, filters, or configuration;
- omitted, multiply classified, overlapping, execution-sensitive, or unsafe changed paths;
- changed submodules or symbolic links with unresolved or escaping state;
- commands that return success without effective assertions;
- runners that reuse one exit code for assertion, collection, import, setup, teardown, dependency, or infrastructure failures;
- missing, malformed, oversized, stale, contradictory, or state-mismatched receipts;
- a malicious command that reads an exposed invocation binding and forges a syntactically valid receipt;
- partial patches that break imports, schemas, generated artifacts, dependencies, or build graphs;
- nondeterministic tests and environment drift;
- background processes or external effects that survive repository resets;
- one claim or coalition contaminating a later execution;
- raw output containing credentials or private data;
- tampered reports, projections, manifests, results, fixture identities, or relation records;
- recomputation of unkeyed digests after semantic modification;
- hidden-state leakage into weaker methods;
- observer-arm mixing;
- post-result relabeling of applicability, family, partition, exclusion, or denominator membership;
- false or insufficient ownership, licensing, authorization, or reviewer declarations;
- a valid result paired with the wrong manifest, projection, report, witness, fixture, or descriptor;
- a descriptor and identity relabeled to another family after expected outcomes are known;
- a substituted specification digest hidden by recomputed identity metadata;
- a scenario manifest copied from another fixture with a colliding scenario identifier;
- path, observer, command, state, method, or family drift across independently valid artifacts;
- a non-empty or symbolic-link destination redirecting or overwriting fixture output;
- a malicious `git` or Python executable resolved from the operator environment;
- coordinated replacement of a complete artifact chain and all expected digests;
- misuse of `SUPPORTED_IN_SCOPE`, `ATTRIBUTION_AVAILABLE`, projected `accept`, concordance, fixture identity, or binding validity as a correctness or security claim;
- malicious repository content executed with the operator's privileges.

## Security and integrity invariants

### Git and classification

1. Base and candidate resolve to distinct immutable commits.
2. Base is an ancestor of candidate.
3. The repository is clean before each top-level analysis.
4. Git subprocesses ignore external repository, index, object-directory, global-config, and replacement-object overrides.
5. Git paths use NUL-delimited parsing and unsafe cross-platform forms are rejected.
6. Internal pathspecs are literal.
7. Every changed path is classified exactly once and the complete path set is prefix-free.
8. Changed submodule entries are rejected.
9. Changed symbolic-link entries are rejected before state materialization.

### Canonical matrix

10. Every state records exact tree and commit IDs.
11. Hybrid states use deterministic synthetic commits.
12. Each claim begins from a reset and cleaned state commit.
13. Every expected state is explicit.
14. Pass and fail exit-code classes are explicit and disjoint.
15. Timeout or unclassified exit status makes the observation incomplete.
16. A complete-but-unsupported witness remains distinct from unsafe or incomplete execution.

### Typed observations

17. Receipt-aware execution receives a deterministic binding over claim, command, specification, observer, state, tree, and commit.
18. Receipts are bounded regular files with strict UTF-8 JSON, exact fields, duplicate-key rejection, internally consistent counts, and an exact binding match.
19. Typed pass or failure requires agreement between receipt semantics and configured process exits.
20. Missing, malformed, inconclusive, stale, or contradictory receipts make the observation incomplete.
21. Receipt outcome, producer, counts, digest, binding, and observer error enter the semantic digest.
22. A typed receipt is cooperating-producer evidence, not authentication.

### Exact influence

23. Influence starts only from a complete supported canonical `pass / fail / pass / pass` witness.
24. Intervention units are the sorted changed code paths.
25. More than eight code paths are rejected before coalition execution.
26. Every one of the `2^n` coalitions runs under both base and candidate test worlds; no value is sampled, pruned, or imputed.
27. Candidate documentation is held constant and explicitly recorded.
28. Four endpoint anchors compare intervention endpoints with the canonical matrix.
29. Full-coalition trees equal canonical candidate-side trees.
30. Empty-coalition outcomes equal canonical base-side outcomes; tree equality is additionally required when no documentation changed.
31. Any incomplete coalition or inconsistent endpoint withholds all exact metrics.
32. An already-sufficient empty coalition or insufficient full coalition withholds attribution.
33. No monotonicity assumption is imposed; negative marginal edges are retained.
34. Shapley, Banzhaf, and interaction values use exact rational arithmetic before rendering.
35. Metrics, anchors, coalitions, Git identities, and observer evidence enter `influence_sha256`.

### DW-001 projection

36. Projection starts from a strict-decoded, semantically verified schema `0.3` report.
37. Every source claim uses canonical expectations and one homogeneous observer arm.
38. Method state sets are fixed as `CC`, `BC+CC`, `BC+CB+CC`, and `BB+BC+CB+CC`.
39. Each method payload contains only its declared state observations.
40. `not_applicable` comes only from pre-execution annotation.
41. For applicable methods, indeterminate evidence precedes rejection.
42. The verifier requires exact fields, canonical identifiers, ordered methods, and ordered state slices.
43. Claim and method decisions, reasons, contradictions, indeterminate states, and applicability are recomputed.
44. Shared state observations must serialize identically wherever exposed.
45. `projection_sha256` covers the complete projection with its own field normalized to `null`.
46. A projection does not establish correspondence to omitted source-report bytes; the source report remains separately required.

### Scenario manifest and result contracts

47. Manifests and results use exact root and nested field sets with deterministic ordering.
48. Builders seal artifacts only after semantic validation.
49. Development manifests require an uncommitted development lock; holdout manifests require the declared holdout commitment form.
50. Manifest verification recomputes provenance conditions, distinct endpoints, path relations, observer IDs, exit classes, state/cause consistency, method labels, review status, and denominator eligibility.
51. An approved manifest requires an approving reviewer declared independent of scenario author and implementation; rejection takes precedence.
52. Included results contain no exclusion metadata; excluded results require code, reason, and decision reference.
53. Applied deviations require approval; rejected deviations carry no approval or confirmatory impact.
54. Exploratory-only, excluded, or results-visible applied deviations cannot silently preserve confirmatory eligibility.
55. Expected and observed decisions, reasons, concordance, denominator membership, and cost missingness are recomputed.
56. Measured costs are finite and nonnegative; unavailable values remain explicit nulls with reasons.
57. Cross-artifact result verification preflights sources and checks manifest, projection, report, witness, observer, decision, and denominator relations.
58. `manifest_sha256` and `result_sha256` cover complete artifacts with their own fields normalized to `null`.
59. Internal commitment fields do not prove that a commitment predates execution.

### Synthetic fixture generator

60. A descriptor uses exact fields, supported versions and families, canonical paths, one observer arm, and method labels derived from state semantics.
61. Unsupported descriptors fail before materialization.
62. The destination is absent or a literal empty directory; a symbolic-link final path is rejected.
63. The generator never deletes existing destination content.
64. Git runs without a shell, with fixed author/committer metadata, timestamps, messages, object format, and known staged paths under a reduced environment.
65. The generated repository is clean after the candidate commit.
66. The identity records descriptor, generator, template, observer, Git, path, state, method, and specification identities.
67. Public identity excludes absolute destination paths, usernames, environment values, and raw Git output.
68. Equivalent descriptors are required to reproduce the same identity in clean supported CI directories.
69. Materialized verification checks `HEAD`, base ancestry, exact trees, cleanliness, and specification bytes.
70. Public identity verification recomputes descriptor-derived specification bytes and rejects a substituted digest after identity re-signing.
71. `descriptor_sha256` and `identity_sha256` cover complete documents with their own fields normalized to `null`.

### Fixture-manifest binding

72. The binding builder accepts only independently verified descriptor, identity, and manifest sources.
73. All binding fields are derived; callers provide no free-form duplicated relation values.
74. Descriptor-to-identity family, generator, template, observer, paths, state semantics, method semantics, and descriptor digest must agree.
75. The manifest must declare owned-synthetic provenance and exact matching base/head commits, paths, observer arm, command, timeout, ground truth, and family mechanism.
76. The specification path must belong to the declared documentation paths and its digest must equal descriptor-derived bytes.
77. `relation_scope` distinguishes verified relations, manifest-owned governance fields, and fixture-only values absent from manifest v1.
78. Binding cannot change partition, review, authorization, or denominator eligibility.
79. The verifier re-verifies all sources, rejects malformed structures with typed diagnostics, recomputes `binding_sha256`, re-derives the canonical relation, and requires exact canonical equality.
80. Recomputed binding digests cannot hide mismatched source artifacts.
81. Existing descriptor, identity, and manifest v1 schemas and digest meanings remain unchanged.

### Execution and publication

82. Commands execute without a shell.
83. The full host environment is not inherited.
84. Raw output is excluded unless explicitly requested.
85. Absolute repository and specification paths are excluded from public artifacts.
86. Default reports live in private Git metadata rather than the working tree.
87. Ambiguous configuration and harness errors stop analysis.
88. Every exported fixture, binding, report, projection, manifest, and result requires privacy and boundary review.

## Residual risks

### No operating-system sandbox

DeltaWitness, its generator, and its smoke tests are not containment systems. Executed code can read or modify accessible files, use the network, start processes, exhaust resources, affect external systems, exploit local dependencies, or forge a visible receipt binding.

Use disposable, non-sensitive, resource-bounded environments without credentials for code that is not fully trusted.

### Git state is not a complete environment model

Recorded trees and commits do not bind the interpreter, compiler, dependencies, kernel, hardware, locale, clock, network, external services, filesystem behavior, or container image.

Repository-local attributes, filters, generated files, unchanged links, and platform checkout behavior may alter execution. Equivalent Git objects do not establish equivalent environments.

### Symbolic-link checks are narrow

Rejecting changed links and a symbolic-link fixture destination does not establish trust in unchanged links, destination ancestors, mounts, namespaces, or files outside the repository.

### Typed receipts are not attestations

A cooperating adapter improves outcome precision, but receipts are unsigned and the invocation binding is visible to tested code. Receipt validation prevents accidental reuse and malformed evidence; it does not authenticate the producer or establish oracle relevance.

### Path interventions are coarse

One path may contain multiple semantic changes and one change may span several paths. Rename or grouping choices alter the coalition game. A zero or high influence value has meaning only for the declared witness and intervention units; it is not production necessity, correctness, severity, ownership, or blame.

### Invalid hybrids and nondeterminism

Partial states may be impossible or unrepresentative. DeltaWitness withholds metrics when any coalition is indeterminate, which may reduce applicability.

Each state currently executes once. Exact means complete subset enumeration, not certainty about stochastic behavior. Repetition policy and uncertainty remain future protocol work.

### Held-constant documentation

Candidate documentation is held constant during influence analysis. Endpoint anchors detect some leakage, but intermediate interactions may remain. Execution-sensitive configuration must be classified as code.

### Projections and contracts are not source attestations

Projection and study verifiers establish internal and supplied cross-artifact consistency. They cannot establish that ground truth was fixed before execution, reviewers are who they claim, authorizations are genuine, omitted scenarios never existed, or the holdout index is complete.

### Fixture identity and binding are scoped relations

The generator depends on the Python runtime, local `git`, filesystem, and trusted destination ancestors. Fixed SHA-1 Git identities are object-model identities, not a collision-resistance, provenance, or cross-platform claim.

The fixture-manifest binding verifies fields represented in its sources. Manifest v1 does not contain fixture tree IDs or specification SHA, so the binding explicitly treats them as fixture-only. Tree-to-commit correspondence still requires the separately verified materialized repository.

### Integrity is not authentication

All current digests are unkeyed. They detect modification only against separately trusted sources or expected values. An actor able to replace a complete artifact chain can recompute every digest.

Signing, DSSE, in-toto, Sigstore, SCITT, immutable timestamping, delegation identity, and transparency logging remain separate future layers. A signature would authenticate bytes, not make false semantics true.

### Resource amplification

At eight paths and one claim, influence can execute 512 coalition commands plus the canonical matrix. Multiple claims multiply cost and side effects. Per-command timeouts do not bound total CPU, memory, storage, process count, or network use.

### Publication metadata can remain sensitive

Artifacts may expose commands, relative paths, Git IDs, scenario/family labels, applicability reasons, reviewer records, authorization references, exclusions, deviations, digests, counts, and costs. Low-entropy digests can reveal equality or permit guessing.

## Safe operation

- Run only on trusted repositories and commands, or inside a separately secured disposable environment.
- Verify exact refs, repository cleanliness, specification, and changed-path classification before execution.
- Prefer typed observers when a trusted adapter exists, but never treat a receipt as an attestation.
- Treat execution-sensitive configuration and generated-code inputs as code.
- Review every incomplete state, invalid hybrid, endpoint anchor, and coalition before interpretation.
- Treat exact influence as exact enumeration over declared units, not complete program causality.
- Strict-decode and verify every report, projection, descriptor, identity, binding, manifest, and result separately.
- Verify generated fixture identity against the materialized repository before using its commits.
- Derive and verify the fixture-manifest binding before matrix execution for generated DW-001 scenarios.
- Treat applicability and ground truth as pre-execution decisions, not values inferred from runtime failure.
- Independently review license, authorization, reviewer, and holdout-commitment claims.
- Preserve excluded results and deviations rather than deleting them.
- Do not run a DW-001 pilot or holdout while the protocol is draft or its authorization gates are incomplete.
- Never interpret a green final state, `SUPPORTED_IN_SCOPE`, `ATTRIBUTION_AVAILABLE`, projected `accept`, fixture identity, valid binding, or concordant result as full correctness, security, completeness, empirical superiority, production readiness, or deployment authorization.
