# Threat Model

## Protected claims

DeltaWitness currently supports seven narrow statement classes.

### Canonical change witness

> Under declared commands and exact Git states, the candidate implementation-side tree changes observed behavior relative to the base tree, while candidate tests act as a counterfactual witness.

A typed observer further bounds that statement by a cooperating adapter's semantic outcome.

### Exact patch influence

> For at most eight changed code paths, under recorded test worlds and exact intervention states, selecting or removing each path changes the declared Boolean witness according to a complete coalition table and released exact metrics.

### DW-001 baseline projection

> Given one verified schema `0.3` matrix report, one homogeneous observer arm, a scenario identifier, and independently declared applicability, the projection records deterministic `M0_FINAL`, `M1_F2P`, `M2_F2P_P2P`, and `M3_FOUR_STATE` decisions without exposing undeclared state outcomes to weaker methods.

### DW-001 study contracts

> Given one pre-execution scenario manifest, one verified projection, and one post-execution result, contract verifiers recompute ground-truth labels, partition and review eligibility, exclusions, deviations, costs, outcomes, denominator membership, and explicit artifact relations.

### DW-001 synthetic fixture identity

> Given one verified supported descriptor and one trusted literal destination, the owned-synthetic generator materializes fixed bytes into exact Git objects and emits a public-safe identity whose descriptor, Git, specification, state, and method semantics can be rechecked.

### DW-001 fixture-manifest binding

> Given one verified descriptor, fixture identity, and scenario manifest, the binding verifier checks their shared study, scenario, commit, path, execution, observer, state, method, family, and specification relations without repurposing manifest v1 fields.

### DW-001 paired wrong-reason observer probe

> Given one fixed owned-synthetic scenario with identical source/test mechanism and scenario identity, `exit-code-v1` accepts a canonical-looking `pass / fail / pass / pass` matrix when `BC` terminates in a pre-assertion import error, while `outcome-receipt-v1` preserves generic `test_error` evidence and makes every method requiring `BC` indeterminate.

This last statement is one controlled development probe. It is not a prevalence, accuracy, or general superiority claim.

None of these statements establishes full program correctness, universal causality, vulnerability removal, production safety, taxonomy completeness, empirical superiority, scientific novelty, legal admissibility, or authorization to deploy, run a pilot, or execute a holdout.

## Assets

The design aims to protect:

- exact canonical, hybrid, coalition, and generated-fixture Git identity;
- complete changed-path classification and deterministic intervention units;
- claim, command, specification, observer, state, tree, and commit bindings;
- separation of assertion failure from execution or infrastructure error;
- separation of generic runtime error from independently fixed failure subtype;
- separation of unsupported evidence from incomplete execution;
- endpoint consistency and completeness of exact influence tables;
- exact arithmetic and semantic integrity of released metrics;
- hidden-state isolation and homogeneous observer arms;
- pre-execution ground truth from post-execution evidence;
- development and holdout partition boundaries;
- reviewer, exclusion, deviation, denominator, and cost semantics;
- deterministic fixture descriptor, identity, Git, and specification semantics;
- correspondence between generated fixture and scenario manifest;
- equality of source/test mechanism across paired observer arms;
- public artifacts from accidental disclosure of absolute paths, environment values, credentials, private output, or unauthorized material;
- separation between consecutive claims, coalitions, scenarios, and study artifacts.

## Adversaries and failure sources

The model includes:

- an AI coding agent that creates a misleading patch, weak test, collateral change, or self-confirming result;
- a contributor that deliberately weakens, skips, replaces, or misdirects an oracle;
- a patch author that groups paths to manipulate attribution;
- stale, unrelated, incorrectly selected, or substituted Git refs;
- hostile Git overrides, replacement objects, hooks, filters, configuration, or binaries;
- omitted, overlapping, multiply classified, execution-sensitive, or unsafe paths;
- changed submodules or links with unresolved or escaping state;
- commands that return success without effective assertions;
- runners that reuse one exit code for assertion, import, collection, setup, dependency, teardown, producer, or infrastructure failure;
- a typed adapter that reports only a generic error while a caller overstates a precise subtype;
- post-result relabeling of a generic error as `import_error`, `setup_error`, or another mechanism;
- missing, malformed, oversized, stale, contradictory, or state-mismatched receipts;
- tested code that reads the visible invocation binding and forges a receipt;
- invalid partial patches, nondeterminism, or environment drift;
- background processes or external effects that survive repository resets;
- one claim or coalition contaminating later execution;
- raw output containing credentials or private data;
- tampered reports, projections, manifests, results, fixture identities, or bindings;
- recomputation of unkeyed digests after semantic modification;
- hidden-state leakage or mixed observer arms;
- false ownership, license, authorization, reviewer, or independence declarations;
- a valid artifact paired with the wrong report, manifest, projection, fixture, descriptor, or expected digest;
- a descriptor relabeled to another family after outcomes are known;
- a scenario pair that changes source/test bytes or scenario identity while claiming an observer-only contrast;
- a substituted specification digest hidden by recomputed metadata;
- a non-empty or symbolic-link destination redirecting or overwriting fixture output;
- malicious Python, Git, filesystem, dependency, kernel, or container behavior;
- coordinated replacement of a complete artifact chain and all expected digests;
- misuse of a green matrix, `SUPPORTED_IN_SCOPE`, `ATTRIBUTION_AVAILABLE`, projected `accept`, fixture identity, binding validity, or one observer contrast as proof of correctness or safety;
- malicious repository content executed with operator privileges.

## Security and integrity invariants

### Git and classification

1. Base and candidate resolve to distinct immutable commits.
2. Base is an ancestor of candidate.
3. The repository is clean before top-level analysis.
4. Git subprocesses ignore external repository, index, object-directory, global-config, and replacement-object overrides.
5. Git paths use NUL-delimited parsing and unsafe cross-platform forms are rejected.
6. Internal pathspecs are literal.
7. Every changed path is classified exactly once and the complete set is prefix-free.
8. Changed submodules and symbolic links are rejected before materialization.

### Canonical matrix

9. Every state records exact tree and commit IDs.
10. Hybrid states use deterministic synthetic commits.
11. Each claim begins from reset and clean state.
12. Every expectation is explicit.
13. Pass and fail exit classes are explicit and disjoint.
14. Timeout or unclassified exit makes the observation incomplete.
15. Complete-but-unsupported evidence remains distinct from unsafe or incomplete execution.

### Typed observations

16. Receipt-aware execution receives a deterministic binding over claim, command, specification, observer, state, tree, and commit.
17. Receipts are bounded regular files with strict UTF-8 JSON, exact fields, duplicate-key rejection, count consistency, and binding equality.
18. Typed pass or failure requires receipt/process agreement.
19. Missing, malformed, inconclusive, stale, contradictory, or non-assertion error receipts make the state incomplete.
20. Receipt outcome, producer, counts, digest, binding, and observer error enter the semantic digest.
21. Receipt v1 distinguishes assertion failure from generic test error, not every error subtype.
22. A failure subtype recorded in fixture or manifest ground truth must be fixed independently before execution or remain generic.
23. A typed receipt is cooperating-producer evidence, not authentication.

### Exact influence

24. Influence starts only from a complete supported canonical `pass / fail / pass / pass` witness.
25. Intervention units are sorted changed code paths.
26. More than eight code paths are rejected before coalition execution.
27. Every `2^n` coalition runs under base and candidate test worlds; no value is sampled, pruned, or imputed.
28. Candidate documentation is held constant and recorded.
29. Four endpoint anchors compare intervention endpoints with canonical states.
30. Full-coalition trees equal canonical candidate-side trees.
31. Empty-coalition outcomes equal canonical base-side outcomes; tree equality is additionally required when no documentation changed.
32. Any incomplete coalition or inconsistent endpoint withholds all exact metrics.
33. An already-sufficient empty coalition or insufficient full coalition withholds attribution.
34. No monotonicity assumption is imposed; negative marginal edges are retained.
35. Shapley, Banzhaf, and interaction values use exact rational arithmetic before rendering.
36. Metrics, anchors, coalitions, Git identities, and observer evidence enter `influence_sha256`.

### DW-001 projection

37. Projection starts from a strict-decoded, semantically verified schema `0.3` report.
38. Every source claim uses canonical expectations and one observer arm.
39. Method state sets are fixed as `CC`, `BC+CC`, `BC+CB+CC`, and `BB+BC+CB+CC`.
40. Each method payload contains only its declared observations.
41. `not_applicable` comes only from pre-execution annotation.
42. For applicable methods, indeterminate evidence precedes rejection.
43. Exact fields, canonical identifiers, ordered methods, and ordered state slices are required.
44. Claim and method decisions, reasons, contradictions, indeterminate states, and applicability are recomputed.
45. Shared observations serialize identically wherever exposed.
46. `projection_sha256` covers the complete projection with its own field normalized to `null`.
47. A projection does not establish correspondence to omitted report bytes; the source report remains separately required.

### Scenario manifest and result contracts

48. Manifests and results use exact root and nested fields with deterministic ordering.
49. Builders seal artifacts only after semantic validation.
50. Development manifests require an uncommitted development lock; holdout manifests require the declared commitment form.
51. Manifest verification recomputes provenance conditions, endpoints, path relations, observer IDs, exit classes, state/cause consistency, method labels, review status, and denominator eligibility.
52. An approved manifest requires an approving reviewer declared independent of scenario author and implementation; rejection takes precedence.
53. Included results contain no exclusion metadata; excluded results require code, reason, and decision reference.
54. Applied deviations require approval; rejected deviations carry no approval or confirmatory impact.
55. Exploratory-only, excluded, or results-visible deviations cannot silently preserve confirmatory eligibility.
56. Decisions, reasons, concordance, denominator membership, and cost missingness are recomputed.
57. Cross-artifact result verification preflights sources and checks manifest, projection, report, witness, observer, decision, and denominator relations.
58. Internal commitment fields do not prove that a commitment predates execution.

### Synthetic fixture generator

59. A descriptor uses exact fields, supported versions and families, canonical paths, one observer arm, and method labels derived from states.
60. Unsupported descriptors fail before materialization.
61. The destination is absent or a literal empty directory; a symbolic-link final path is rejected.
62. The generator never deletes existing destination content.
63. Git runs without a shell, with fixed metadata, timestamps, messages, object format, and known staged paths under a reduced environment.
64. The generated repository is clean after candidate commit.
65. Identity records descriptor, generator, template, observer, Git, path, state, method, and specification identities.
66. Public identity excludes absolute destination paths, usernames, environment values, and raw Git output.
67. Equivalent descriptors reproduce the same identity in clean supported directories.
68. Materialized verification checks `HEAD`, base ancestry, exact trees, cleanliness, and specification bytes.
69. Public identity verification recomputes descriptor-derived specification bytes.
70. Descriptor and identity digests cover complete documents with their own fields normalized to `null`.

### Fixture-manifest binding

71. The builder accepts only independently verified descriptor, identity, and manifest sources.
72. All binding values are derived; callers provide no free-form duplicated relation data.
73. Descriptor-to-identity family, generator, template, observer, paths, states, methods, and descriptor digest agree.
74. Manifest provenance, base/head commits, paths, observer, command, timeout, ground truth, and family agree.
75. Specification path belongs to declared documentation paths and digest equals descriptor-derived bytes.
76. `relation_scope` distinguishes verified relations, manifest-owned governance fields, and fixture-only values.
77. Binding cannot change partition, review, authorization, or denominator eligibility.
78. The verifier re-verifies all sources, rejects malformed structures with typed diagnostics, recomputes `binding_sha256`, re-derives the canonical relation, and requires exact equality.
79. Recomputed binding digests cannot hide mismatched sources.

### Paired wrong-reason observer probe

80. Both arms use the same scenario ID, family, control role, generator, template, timeout, path categories, and source/test bytes.
81. Only observer-derived descriptor fields may differ.
82. Candidate tests import a fixed candidate-introduced symbol before assertions.
83. `O0_EXIT_CODE` must record `BC = fail` with no typed receipt evidence and produce the declared complete accepted matrix.
84. `O1_TYPED_RECEIPT` must record `BC = error`, receipt outcome `test_error`, zero assertion failures, at least one error, and incomplete evidence.
85. `M0` remains `accept`; `M1`–`M3` become `indeterminate` only in the typed arm.
86. `import_error` remains predeclared fixture ground truth and is never presented as a receipt-v1 runtime subtype.
87. Both manifests remain development-partition and primary-denominator ineligible.
88. Public descriptor, identity, binding, report, and projection artifacts contain no raw traceback or absolute local path.

### Execution and publication

89. Commands execute without a shell.
90. The full host environment is not inherited.
91. Raw output is excluded unless explicitly requested.
92. Absolute repository and specification paths are excluded from public artifacts.
93. Default reports live in private Git metadata.
94. Ambiguous configuration and harness errors stop analysis.
95. Every exported fixture, binding, report, projection, manifest, and result requires privacy and boundary review.

## Residual risks

### No operating-system sandbox

DeltaWitness and its generator are not containment systems. Executed code can read or modify accessible files, use the network, start processes, exhaust resources, affect external systems, exploit local dependencies, or forge a visible receipt binding.

Use a separately secured disposable environment without credentials for untrusted code.

### Git state is not a complete environment model

Trees and commits do not bind interpreter, compiler, dependencies, kernel, hardware, locale, clock, network, external services, filesystem behavior, or container image.

Equivalent Git objects do not establish equivalent execution environments.

### Symbolic-link checks are narrow

Rejecting changed links and a linked fixture destination does not establish trust in unchanged links, destination ancestors, mounts, namespaces, or external paths.

### Typed receipts are not attestations or complete diagnoses

The cooperating adapter improves failure/error precision, but receipts are unsigned and binding is visible. The wrong-reason probe shows one distinction between assertion failure and generic error. It does not show reliable import/setup/collection subtype diagnosis or resistance to malicious tested code.

### Ground-truth subtype risk

A fixed synthetic `import_error` label is auditable from owned bytes. Real-corpus failure subtypes may be ambiguous and susceptible to post-result relabeling. The frozen protocol needs an independent pre-execution review procedure or must retain generic labels.

### Path interventions are coarse

One path may contain multiple changes and one change may span paths. Rename or grouping choices alter the coalition game. Influence values are not correctness, severity, ownership, or blame.

### Invalid hybrids and nondeterminism

Partial states may be impossible or unrepresentative. DeltaWitness withholds metrics when execution is indeterminate, which may reduce applicability.

Each state currently executes once. Exact means complete subset enumeration, not certainty about stochastic behavior.

### Projections and contracts are not source attestations

Verifiers establish internal and supplied cross-artifact consistency. They cannot prove ground truth predates execution, reviewers are who they claim, authorizations are genuine, omitted scenarios never existed, or a holdout index is complete.

### Fixture and binding scope

The generator trusts Python, Git, filesystem, and destination ancestry. Fixed SHA-1 object identities are object-model identities, not provenance or cross-platform claims.

Manifest v1 lacks tree and specification-digest fields; the binding treats them as fixture-only. Tree-to-commit correspondence still requires the materialized repository.

### Integrity is not authentication

All current digests are unkeyed. An actor able to replace a complete chain can recompute every digest.

Signing, DSSE, in-toto, Sigstore, SCITT, immutable timestamping, delegation identity, and transparency remain future layers. A signature authenticates bytes, not semantics.

### Resource amplification

At eight paths and one claim, influence can execute 512 coalition commands plus the canonical matrix. Per-command timeouts do not bound total CPU, memory, storage, process count, or network use.

### Publication metadata can remain sensitive

Artifacts may expose commands, relative paths, Git IDs, scenario/family labels, reviewer records, authorization references, exclusions, deviations, digests, counts, and costs. Low-entropy digests can reveal equality or permit guessing.

## Safe operation

- Run only trusted repositories and commands, or use a separately secured disposable environment.
- Verify exact refs, cleanliness, specification, and path classification before execution.
- Prefer typed observers when a trusted adapter exists, but never treat receipts as attestations.
- Do not infer a precise error subtype from generic `test_error` without independently fixed evidence.
- Treat execution-sensitive configuration and generated inputs as code.
- Review every incomplete state, invalid hybrid, endpoint anchor, and coalition before interpretation.
- Treat exact influence as enumeration over declared units, not complete causality.
- Strict-decode and verify every report, projection, descriptor, identity, binding, manifest, and result separately.
- Verify generated identity against its repository before using its commits.
- Require paired observer probes to hold mechanism and scenario identity constant.
- Preserve exclusions and deviations rather than deleting them.
- Do not run DW-001 pilot or holdout while protocol and authorization gates are incomplete.
- Never interpret a green final state, `SUPPORTED_IN_SCOPE`, `ATTRIBUTION_AVAILABLE`, projected `accept`, valid fixture/binding, or one controlled observer contrast as full correctness, general effectiveness, production readiness, or deployment authorization.
