# Threat Model

## Protected claims

DeltaWitness currently supports nine narrow statement classes.

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

### DW-001 paired import-error observer probe

> Given one fixed owned-synthetic scenario with identical source/test mechanism and scenario identity, `exit-code-v1` accepts a canonical-looking `pass / fail / pass / pass` matrix when `BC` terminates in a pre-assertion import error, while `outcome-receipt-v1` preserves generic `test_error` evidence and makes every method requiring `BC` indeterminate.

### DW-001 unrelated-assertion negative control

> Given one fixed owned-synthetic scenario with a non-discriminating claim-facing assertion and a collateral assertion as the sole `BC` failure source, both observer arms and all nested state-set methods accept the canonical matrix even though the failing assertion is unrelated to the declared authorization claim.

### DW-001 development mechanism pilot

> Given the exact committed ten-arm development plan, the runner derives fixed case inputs, executes and verifies every artifact chain, derives five controlled contrasts, refuses primary-denominator eligibility, and retains a canonical archive whose complete directory bundle can be reconstructed and reverified.

The final three statements are controlled development evidence. The import pair isolates one observer distinction. The unrelated-assertion case establishes a known limitation. The development pilot establishes pipeline and artifact-chain behavior for five fixed synthetic families. None is a prevalence, accuracy, oracle-adequacy, ecological-effectiveness, or general-superiority claim.

None of these statements establishes full program correctness, universal causality, vulnerability removal, production safety, taxonomy completeness, oracle relevance, empirical superiority, scientific novelty, legal admissibility, or authorization to deploy or execute a holdout.

## Assets

The design aims to protect:

- exact canonical, hybrid, coalition, and generated-fixture Git identity;
- complete changed-path classification and deterministic intervention units;
- claim, command, specification, observer, state, tree, and commit bindings;
- separation of assertion failure from execution or infrastructure error;
- separation of generic runtime error from independently fixed failure subtype;
- separation of assertion failure from claim-oracle relevance;
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
- direct negative-control evidence showing which assertion is the sole `BC` failure source;
- exact development-pilot plan order, case IDs, expected decisions, selectors, and analysis contract;
- refusal to publish a partial pilot bundle or aggregate an invalid case;
- complete archive path set, embedded-document digests, semantic index digest, and reconstructed bundle relations;
- permanent development-only and denominator-ineligible status for mechanism-pilot cases;
- public artifacts from accidental disclosure of absolute paths, environment values, credentials, private output, or unauthorized material;
- separation between consecutive claims, coalitions, scenarios, pilot cases, and study artifacts.

## Adversaries and failure sources

The model includes:

- an AI coding agent that creates a misleading patch, weak test, collateral change, or self-confirming result;
- a contributor that deliberately weakens, skips, replaces, or misdirects an oracle;
- a candidate suite whose claim-facing assertion is non-discriminating while an unrelated assertion creates fail-to-pass behavior;
- a patch author that groups paths to manipulate attribution;
- stale, unrelated, incorrectly selected, or substituted Git refs;
- hostile Git overrides, replacement objects, hooks, filters, configuration, or binaries;
- omitted, overlapping, multiply classified, execution-sensitive, or unsafe paths;
- changed submodules or links with unresolved or escaping state;
- commands that return success without effective assertions;
- runners that reuse one exit code for assertion, import, collection, setup, dependency, teardown, producer, or infrastructure failure;
- a typed adapter that reports a genuine assertion failure while a caller overstates its relevance to the declared claim;
- a typed adapter that reports only a generic error while a caller overstates a precise subtype;
- post-result relabeling of a generic error as `import_error`, `setup_error`, or another mechanism;
- post-result relabeling of an unrelated assertion as the intended regression oracle;
- missing, malformed, oversized, stale, contradictory, or state-mismatched receipts;
- tested code that reads the visible invocation binding and forges a receipt;
- invalid partial patches, nondeterminism, or environment drift;
- background processes or external effects that survive repository resets;
- one claim or coalition contaminating later execution;
- raw output containing credentials or private data;
- tampered reports, projections, manifests, results, fixture identities, bindings, or direct-control records;
- recomputation of unkeyed digests after semantic modification;
- hidden-state leakage or mixed observer arms;
- false ownership, license, authorization, reviewer, or independence declarations;
- a valid artifact paired with the wrong report, manifest, projection, fixture, descriptor, or expected digest;
- a descriptor relabeled to another family after outcomes are known;
- a scenario pair that changes source/test bytes or scenario identity while claiming an observer-only contrast;
- a negative control whose collateral assertion is not actually the sole discrimination source;
- a modified, reordered, or partially executed development-pilot plan;
- a runner that accepts free-form code, commands, selectors, expectations, exclusions, or denominator decisions after plan sealing;
- one missing or invalid case hidden by an aggregate headline score;
- a development case relabeled as holdout or primary-denominator eligible;
- negative, NaN, infinite, or silently zero missing cost values;
- partial output published before every case and relation verifies;
- a pilot index whose stored labels or contrasts are trusted instead of recomputed;
- an archive with duplicate, missing, unsafe, reordered, or substituted embedded paths;
- coordinated replacement of embedded documents followed by recomputed file and archive digests;
- a fixed synthetic mechanism pilot presented as an ecological effectiveness result;
- temporary archive transport or branch-write capability accidentally retained as a permanent permission;
- a substituted specification digest hidden by recomputed metadata;
- a non-empty or symbolic-link destination redirecting or overwriting fixture or pilot output;
- malicious Python, Git, filesystem, dependency, kernel, or container behavior;
- coordinated replacement of a complete artifact chain and all expected digests;
- misuse of a green matrix, `SUPPORTED_IN_SCOPE`, `ATTRIBUTION_AVAILABLE`, projected `accept`, typed assertion failure, valid fixture/binding, verified pilot, or one controlled contrast as proof of correctness, oracle relevance, effectiveness, or safety;
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
22. Receipt v1 does not identify which assertion is relevant to the declared claim.
23. A failure subtype recorded in fixture or manifest ground truth must be fixed independently before execution or remain generic.
24. A typed receipt is cooperating-producer evidence, not authentication.

### Exact influence

25. Influence starts only from a complete supported canonical `pass / fail / pass / pass` witness.
26. Intervention units are sorted changed code paths.
27. More than eight code paths are rejected before coalition execution.
28. Every `2^n` coalition runs under base and candidate test worlds; no value is sampled, pruned, or imputed.
29. Candidate documentation is held constant and recorded.
30. Four endpoint anchors compare intervention endpoints with canonical states.
31. Full-coalition trees equal canonical candidate-side trees.
32. Empty-coalition outcomes equal canonical base-side outcomes; tree equality is additionally required when no documentation changed.
33. Any incomplete coalition or inconsistent endpoint withholds all exact metrics.
34. An already-sufficient empty coalition or insufficient full coalition withholds attribution.
35. No monotonicity assumption is imposed; negative marginal edges are retained.
36. Shapley, Banzhaf, and interaction values use exact rational arithmetic before rendering.
37. Metrics, anchors, coalitions, Git identities, and observer evidence enter `influence_sha256`.
38. Exact influence remains conditional on the declared Boolean witness and does not establish oracle relevance.

### DW-001 projection

39. Projection starts from a strict-decoded, semantically verified schema `0.3` report.
40. Every source claim uses canonical expectations and one observer arm.
41. Method state sets are fixed as `CC`, `BC+CC`, `BC+CB+CC`, and `BB+BC+CB+CC`.
42. Each method payload contains only its declared observations.
43. `not_applicable` comes only from pre-execution annotation.
44. For applicable methods, indeterminate evidence precedes rejection.
45. Exact fields, canonical identifiers, ordered methods, and ordered state slices are required.
46. Claim and method decisions, reasons, contradictions, indeterminate states, and applicability are recomputed.
47. Shared observations serialize identically wherever exposed.
48. `projection_sha256` covers the complete projection with its own field normalized to `null`.
49. A projection does not establish correspondence to omitted report bytes; the source report remains separately required.
50. Projected `accept` means only that the required state predicate matched; it does not establish why a failing state failed.

### Scenario manifest and result contracts

51. Manifests and results use exact root and nested fields with deterministic ordering.
52. Builders seal artifacts only after semantic validation.
53. Development manifests require an uncommitted development lock; holdout manifests require the declared commitment form.
54. Manifest verification recomputes provenance conditions, endpoints, path relations, observer IDs, exit classes, state/cause consistency, method labels, review status, and denominator eligibility.
55. An approved manifest requires an approving reviewer declared independent of scenario author and implementation; rejection takes precedence.
56. Included results contain no exclusion metadata; excluded results require code, reason, and decision reference.
57. Applied deviations require approval; rejected deviations carry no approval or confirmatory impact.
58. Exploratory-only, excluded, or results-visible deviations cannot silently preserve confirmatory eligibility.
59. Decisions, reasons, concordance, denominator membership, and cost missingness are recomputed.
60. Cross-artifact result verification preflights sources and checks manifest, projection, report, witness, observer, decision, and denominator relations.
61. Internal commitment fields do not prove that a commitment predates execution.
62. Manifest ground truth does not become correct merely because it is internally consistent and digest-valid.

### Synthetic fixture generator

63. A descriptor uses exact fields, supported versions and families, canonical paths, one observer arm, and method labels derived from states.
64. Unsupported descriptors fail before materialization.
65. The destination is absent or a literal empty directory; a symbolic-link final path is rejected.
66. The generator never deletes existing destination content.
67. Git runs without a shell, with fixed metadata, timestamps, messages, object format, and known staged paths under a reduced environment.
68. The generated repository is clean after candidate commit.
69. Identity records descriptor, generator, template, observer, Git, path, state, method, and specification identities.
70. Public identity excludes absolute destination paths, usernames, environment values, and raw Git output.
71. Equivalent descriptors reproduce the same identity in clean supported directories.
72. Materialized verification checks `HEAD`, base ancestry, exact trees, cleanliness, and specification bytes.
73. Public identity verification recomputes descriptor-derived specification bytes.
74. Descriptor and identity digests cover complete documents with their own fields normalized to `null`.
75. Fixed-family adapters accept no caller-provided executable source or test bytes.

### Fixture-manifest binding

76. The builder accepts only independently verified descriptor, identity, and manifest sources.
77. All binding values are derived; callers provide no free-form duplicated relation data.
78. Descriptor-to-identity family, generator, template, observer, paths, states, methods, and descriptor digest agree.
79. Manifest provenance, base/head commits, paths, observer, command, timeout, ground truth, and family agree.
80. Specification path belongs to declared documentation paths and digest equals descriptor-derived bytes.
81. `relation_scope` distinguishes verified relations, manifest-owned governance fields, and fixture-only values.
82. Binding cannot change partition, review, authorization, or denominator eligibility.
83. The verifier re-verifies all sources, rejects malformed structures with typed diagnostics, recomputes `binding_sha256`, re-derives the canonical relation, and requires exact equality.
84. Recomputed binding digests cannot hide mismatched sources.
85. A valid binding does not establish that a test oracle is relevant or strong.

### Paired import-error observer probe

86. Both arms use the same scenario ID, family, control role, generator, template, timeout, path categories, and source/test bytes.
87. Only observer-derived descriptor fields may differ.
88. Candidate tests import a fixed candidate-introduced symbol before assertions.
89. `O0_EXIT_CODE` records `BC = fail` with no typed receipt evidence and produces the declared complete accepted matrix.
90. `O1_TYPED_RECEIPT` records `BC = error`, receipt outcome `test_error`, zero assertion failures, at least one error, and incomplete evidence.
91. `M0` remains `accept`; `M1`–`M3` become `indeterminate` only in the typed arm.
92. `import_error` remains predeclared fixture ground truth and is never presented as a receipt-v1 runtime subtype.
93. Both manifests remain development-partition and primary-denominator ineligible.
94. Public descriptor, identity, binding, report, and projection artifacts contain no raw traceback or absolute local path.

### Unrelated-assertion negative control

95. Both arms use the same scenario ID, family, control role, generator, template, timeout, path categories, and source/test bytes.
96. Base and candidate expose fixed claim-facing and collateral behavior dimensions.
97. The claim-facing viewer test executes the declared behavior but asserts only a property that passes on base and candidate.
98. A separate fixed collateral assertion is the sole source of `BC = fail`.
99. Direct controls require the claim-facing test to pass against both code versions.
100. Direct controls require the complete candidate suite to fail against base code and the suite without the collateral assertion to pass.
101. `O0_EXIT_CODE` records `BC = fail` with cause `test_failure_untyped`.
102. `O1_TYPED_RECEIPT` records `BC = fail`, outcome `test_failure`, at least one assertion failure, and zero errors.
103. Both reports remain complete and supported.
104. `M0` through `M3` accept under both observers.
105. Both manifests remain development-partition and primary-denominator ineligible.
106. Public artifacts contain no raw failure narrative or absolute local path.
107. The result is documented as a limitation and is never presented as oracle-relevance validation.

### Execution, packaging, and publication

108. Commands execute without a shell.
109. The full host environment is not inherited.
110. Raw output is excluded unless explicitly requested.
111. Absolute repository and specification paths are excluded from public artifacts.
112. Default reports live in private Git metadata.
113. Ambiguous configuration and harness errors stop analysis.
114. Editable-install and installed-wheel smoke execute complete fixture chains for supported development probes.
115. Packaged smoke is not independent reproduction.
116. Every exported fixture, binding, report, projection, manifest, result, pilot index, and archive requires privacy and boundary review.

### Development mechanism pilot plan and runner

117. The plan contains exactly ten ordered development case arms derived from the five supported families and two observer arms.
118. The plan pins exact protocol and evidence-producing implementation commits and records exact contract versions, case IDs, descriptors, specification digests, state/method expectations, selectors, analysis rules, and cost policy.
119. The plan contains no holdout lock and every case is primary-denominator ineligible.
120. Recomputing `plan_sha256` cannot hide a changed family, observer, selector, expectation, order, cost policy, or denominator field because the semantic verifier rebuilds the canonical plan.
121. The runner verifies the complete plan before creating final output.
122. The runner derives executable descriptors and declarations; it accepts no free-form executable fixture input or expected labels.
123. Every required per-case artifact is independently verified before case acceptance.
124. Unexpected method or localization results stop execution; they are not silently relabeled to match the plan.
125. Aggregate analysis is derived from verified case tables and is withheld when any controlled contrast is unexpected.
126. The index emits no headline score and forbids ecological inference.
127. Per-case cost fields reject negative, non-finite, and silently zero missing values; human review missingness remains explicit.
128. The runner stages output, self-verifies the complete bundle, and publishes only after success.
129. Non-empty and symbolic-link final destinations are rejected; a failed run removes staging output.
130. A development pilot cannot create holdout or confirmatory eligibility.

### Development mechanism pilot archive

131. The archive contains only sorted unique safe relative JSON paths and object-valued documents.
132. Every embedded file record has a canonical digest over path and document.
133. `archive_sha256` covers the complete archive with its own field normalized to `null`.
134. Archive verification requires the committed plan digest and the embedded index semantic digest.
135. The archive verifier reconstructs the complete directory bundle and reruns all artifact-specific and cross-artifact verifiers.
136. The verifier rematerializes every retained synthetic fixture from its descriptor and requires exact identity equality.
137. Duplicate, missing, unsafe, reordered, or substituted paths are rejected even after digest recomputation.
138. A complete archive digest is not stable when volatile timestamps or costs change; the semantic index digest is the repeated-run comparison field.
139. The canonical archive remains development-only and contains no raw output or absolute local paths.
140. Historical temporary artifact-upload and branch-write mechanisms are removed from the final workflow and are not product capabilities.

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

The cooperating adapter improves failure/error precision, but receipts are unsigned and binding is visible. The import probe shows one distinction between assertion failure and generic error. It does not show reliable import/setup/collection subtype diagnosis or resistance to malicious tested code.

### Typed assertion failure is not oracle relevance

The unrelated-assertion negative control demonstrates that a genuine assertion failure can be caused entirely by collateral behavior while a claim-facing assertion remains non-discriminating. Four-state replay and typed outcomes cannot by themselves identify which assertion witnessed the claim.

A future oracle-integrity layer must have independent ground truth, positive and negative fixtures, measured error rates, and a separate policy boundary. An LLM-generated explanation cannot count as independent confirmation.

### Ground-truth subtype and intent risk

A fixed synthetic `import_error` or `unrelated_assertion` label is auditable from owned bytes and direct controls. Real-corpus failure subtypes and claim relevance may be ambiguous and susceptible to post-result relabeling. The frozen protocol needs an independent pre-execution review procedure or must retain generic/unknown labels.

### Fixed synthetic pilot is not ecological evidence

The ten arms are designed mechanism probes, not independent or representative samples. Successful execution and expected contrasts establish pipeline behavior only.

The pilot cannot support prevalence, accuracy, precision, recall, superiority, or production-utility claims. Its exact cases are permanently development-only and cannot later become a holdout.

### Pilot plan and execution provenance are not authenticated

The plan pins protocol and evidence-producing implementation commits. Later archive packaging, workflow, and transport revisions are recorded separately in GitHub history and the pilot result document. Current unkeyed records do not prove who executed the plan, that the run occurred at a claimed time, or that GitHub workflow metadata is complete.

### Costs are diagnostics, not native-method or population estimates

Per-case timings and byte counts are environment-sensitive. Full-matrix projection does not measure native `M0`, `M1`, or `M2` runtime. Human review time is unmeasured. The archive preserves these limitations rather than imputing zero.

### Historical transport capability

The canonical archive required separately reviewed one-time GitHub artifact transport and an exact branch-scoped write. Both mechanisms were removed before final validation. Their historical use expands the trusted process for that run but does not create a continuing DeltaWitness upload or write capability.

### Path interventions are coarse

One path may contain multiple changes and one change may span paths. Rename or grouping choices alter the coalition game. Influence values are not correctness, severity, ownership, blame, or oracle relevance.

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

The development pilot executes 40 matrix states and 12 selector states. Its fixed command count does not establish a safe resource bound for ecological repositories.

### Publication metadata can remain sensitive

Artifacts may expose commands, relative paths, Git IDs, scenario/family labels, test selectors, reviewer records, authorization references, exclusions, deviations, digests, counts, timings, and costs. Low-entropy digests can reveal equality or permit guessing.

## Safe operation

- Run only trusted repositories and commands, or use a separately secured disposable environment.
- Verify exact refs, cleanliness, specification, and path classification before execution.
- Prefer typed observers when a trusted adapter exists, but never treat receipts as attestations.
- Do not infer a precise error subtype from generic `test_error` without independently fixed evidence.
- Do not infer claim relevance from `test_failure`, failure counts, or a canonical matrix.
- Treat execution-sensitive configuration and generated inputs as code.
- Review every incomplete state, invalid hybrid, endpoint anchor, and coalition before interpretation.
- Treat exact influence as enumeration over declared units, not complete causality.
- Strict-decode and verify every report, projection, descriptor, identity, binding, manifest, result, pilot plan, pilot index, and pilot archive separately.
- Verify generated identity against its repository before using its commits.
- Require paired observer probes to hold mechanism and scenario identity constant.
- Require oracle negative controls to prove directly which assertion is the sole failure source.
- Run only an exact sealed pilot plan and reject any runtime free-form case or expectation input.
- Require complete staged-bundle and reconstructed-archive verification before interpreting a pilot result.
- Keep every mechanism-pilot case development-only and outside the primary denominator.
- Preserve exclusions, disputes, negative results, missing costs, and deviations rather than deleting or imputing them.
- Do not interpret the fixed synthetic pilot as ecological effectiveness or holdout evidence.
- Do not run a DW-001 holdout while protocol and authorization gates are incomplete.
- Never interpret a green final state, `SUPPORTED_IN_SCOPE`, `ATTRIBUTION_AVAILABLE`, projected `accept`, typed assertion failure, valid fixture/binding, verified synthetic pilot, or one controlled contrast as full correctness, oracle relevance, general effectiveness, production readiness, or deployment authorization.
