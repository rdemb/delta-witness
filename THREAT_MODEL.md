# Threat Model

## Protected claims

DeltaWitness currently supports twelve narrow statement classes.

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

### DW-001 declared witness-test localization

> Given one verified matrix report and one predeclared standard-library unittest selector declaration, the localization verifier records whether the exact selector exhibits typed `BC`/`CC` discrimination under reconstructed Git states and rejects source, selector, command, receipt, state, or digest substitution.

### DW-001 paired import-error observer probe

> Given one fixed owned-synthetic scenario with identical source/test mechanism and scenario identity, `exit-code-v1` accepts a canonical-looking `pass / fail / pass / pass` matrix when `BC` terminates in a pre-assertion import error, while `outcome-receipt-v1` preserves generic `test_error` evidence and makes every method requiring `BC` indeterminate.

### DW-001 unrelated-assertion negative control

> Given one fixed owned-synthetic scenario with a non-discriminating claim-facing assertion and a collateral assertion as the sole `BC` failure source, both observer arms and all nested state-set methods accept the canonical matrix, while declared-selector localization exposes that the claim-facing selector is not the discriminating witness.

### DW-001 weak-proxy-oracle negative control

> Given one fixed owned-synthetic task, exact current evidence accepts a genuine typed and localized fail-to-pass selector, while one fixed claim-violating mutant survives that selector and fails a separately fixed hidden development claim check.

### DW-001 development mechanism pilot

> Given the exact committed ten-arm development plan, the runner derives fixed case inputs, executes and verifies every artifact chain, derives five controlled contrasts, refuses primary-denominator eligibility, and retains a canonical archive whose complete directory bundle can be reconstructed and reverified.

### DW-001 ecological source universe

> Given the exact design-only source-universe artifact, the verifier records reviewed candidate benchmark implementation revisions, repository-level license metadata, known biases, and unresolved authorization, sampling, environment, review, and containment blockers while keeping execution authorization, sampling-frame freeze, and holdout selection false.

The import, unrelated-assertion, and weak-proxy statements are controlled negative or contrast evidence. The development pilot establishes pipeline behavior for its sealed five-family synthetic population. The ecological source universe is design metadata only. None is a prevalence, accuracy, oracle-adequacy, mutation-adequacy, ecological-effectiveness, or general-superiority claim.

None of these statements establishes full program correctness, universal causality, vulnerability removal, production safety, taxonomy completeness, oracle relevance or strength, empirical superiority, scientific novelty, legal admissibility, or authorization to deploy, execute an external repository, or inspect a holdout.

## Assets

The design aims to protect:

- exact canonical, hybrid, coalition, and generated-fixture Git identity;
- complete changed-path classification and deterministic intervention units;
- claim, command, specification, observer, state, tree, and commit bindings;
- separation of assertion failure from execution or infrastructure error;
- separation of generic runtime error from independently fixed failure subtype;
- separation of suite-level failure from exact declared-selector provenance;
- separation of selector provenance from semantic oracle relevance and oracle strength;
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
- direct negative-control evidence showing which assertion is the sole suite-level failure source;
- exact declared selector identity, adapter-derived command, typed `BC`/`CC` observations, and localization relation;
- fixed weak-proxy task, candidate, mutant, declared test, hidden check, and five typed control executions;
- refusal to infer mutation adequacy from one surviving or killed mutant;
- exact development-pilot plan order, case IDs, expected decisions, selectors, and analysis contract;
- refusal to publish a partial pilot bundle or aggregate an invalid case;
- complete archive path set, embedded-document digests, semantic index digest, and reconstructed bundle relations;
- permanent development-only and denominator-ineligible status for mechanism-pilot and weak-oracle cases;
- design-only ecological source metadata from accidental execution authorization or holdout selection;
- public artifacts from accidental disclosure of absolute paths, environment values, credentials, private output, or unauthorized material;
- separation between consecutive claims, coalitions, selectors, mutation controls, scenarios, pilot cases, and study artifacts.

## Adversaries and failure sources

The model includes:

- an AI coding agent that creates a misleading patch, weak test, collateral change, or self-confirming result;
- a contributor that deliberately weakens, skips, replaces, or misdirects an oracle;
- a candidate suite whose claim-facing assertion is non-discriminating while an unrelated assertion creates fail-to-pass behavior;
- a declared selector that genuinely fails on base and passes on candidate but checks only a proxy property;
- an incorrect implementation that preserves the proxy property and survives the declared selector;
- a hidden claim check selected or rewritten after observing mutant survival;
- a mutation operator, mutant set, threshold, or score selected after results are visible;
- a patch author that groups paths to manipulate attribution;
- stale, unrelated, incorrectly selected, or substituted Git refs;
- hostile Git overrides, replacement objects, hooks, filters, configuration, or binaries;
- omitted, overlapping, multiply classified, execution-sensitive, or unsafe paths;
- changed submodules or links with unresolved or escaping state;
- commands that return success without effective assertions;
- runners that reuse one exit code for assertion, import, collection, setup, dependency, teardown, producer, or infrastructure failure;
- a typed adapter that reports a genuine assertion failure while a caller overstates its relevance or strength;
- a typed adapter that reports only a generic error while a caller overstates a precise subtype;
- post-result relabeling of a generic error as `import_error`, `setup_error`, or another mechanism;
- post-result relabeling of an unrelated or weak assertion as a sufficient regression oracle;
- missing, malformed, oversized, stale, contradictory, or state-mismatched receipts;
- tested code that reads the visible invocation binding and forges a receipt;
- a declared selector copied to another claim, specification, report, or Git state;
- selector renaming, non-discovery, duplication, dynamic suite generation, or adapter drift;
- invalid partial patches, nondeterminism, or environment drift;
- background processes or external effects that survive repository resets;
- one claim, selector, coalition, or mutation control contaminating later execution;
- raw output containing credentials or private data;
- tampered reports, projections, declarations, localizations, challenges, manifests, results, fixture identities, bindings, or direct-control records;
- recomputation of unkeyed digests after semantic modification;
- hidden-state leakage or mixed observer arms;
- false ownership, license, authorization, reviewer, or independence declarations;
- a valid artifact paired with the wrong report, manifest, projection, declaration, localization, fixture, descriptor, or expected digest;
- a descriptor relabeled to another family after outcomes are known;
- a scenario pair that changes source/test bytes or scenario identity while claiming an observer-only contrast;
- a negative control whose collateral assertion is not actually the sole discrimination source;
- a weak-oracle challenge whose mutant does not violate the fixed claim or whose hidden check merely restates the proxy property;
- a modified, reordered, or partially executed development-pilot plan;
- a runner that accepts free-form code, commands, selectors, expectations, exclusions, or denominator decisions after plan sealing;
- one missing or invalid case hidden by an aggregate headline score;
- a development case relabeled as holdout or primary-denominator eligible;
- negative, NaN, infinite, or silently zero missing cost values;
- partial output published before every case and relation verifies;
- a pilot index whose stored labels or contrasts are trusted instead of recomputed;
- an archive with duplicate, missing, unsafe, reordered, substituted, or unexpected embedded paths;
- coordinated replacement of embedded documents followed by recomputed file and archive digests;
- a fixed synthetic mechanism or weak-oracle challenge presented as an ecological effectiveness result;
- temporary archive transport or branch-write capability accidentally retained as a permanent permission;
- a public benchmark label or repository-level license silently treated as instance execution authorization;
- a moving benchmark repository silently treated as an immutable dataset release;
- a sampling frame, unit of analysis, reviewer protocol, or holdout selected after outcome inspection;
- a substituted specification digest hidden by recomputed metadata;
- a non-empty or symbolic-link destination redirecting or overwriting fixture or pilot output;
- malicious Python, Git, filesystem, dependency, kernel, or container behavior;
- coordinated replacement of a complete artifact chain and all expected digests;
- misuse of a green matrix, `SUPPORTED_IN_SCOPE`, `ATTRIBUTION_AVAILABLE`, projected `accept`, typed assertion failure, discriminating selector, valid fixture/binding, verified pilot, source-universe record, or one controlled mutant as proof of correctness, oracle adequacy, effectiveness, or safety;
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
22. Receipt v1 does not identify which assertion is relevant or strong enough for the declared claim.
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
38. Exact influence remains conditional on the declared Boolean witness and does not establish oracle relevance or strength.

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
50. Projected `accept` means only that the required state predicate matched; it does not establish why a state failed or whether its oracle is sufficient.

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
75. Fixed-family adapters accept no caller-provided executable source, test, prompt, hidden-check, or mutant bytes.

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

### Declared witness-test localization

86. A declaration binds one source specification digest, claim ID, adapter/version, ordered unique unittest selectors, adapter-derived commands, and one fixed aggregate rule.
87. Callers cannot provide a selector command independently from adapter derivation.
88. Missing, duplicate, malformed, unsafe, or ambiguous selectors fail closed.
89. The runner reconstructs exact `BC` and `CC` Git states from the verified source report and current repository refs.
90. Every selector executes through `outcome-receipt-v1` with a state-specific invocation binding.
91. A normal selector receipt represents exactly one logical test identity under the supported adapter.
92. Selector `BC = assertion_failure` and `CC = pass` yields `discriminating` only when all structural, process, receipt, Git, and source relations verify.
93. Pass in both states yields `non_discriminating`; non-pass `CC` yields `candidate_invalid`; incomplete evidence yields `indeterminate`.
94. Per-selector evidence remains visible and indeterminate evidence is never collapsed into non-discrimination.
95. Declaration and localization digests cover stable semantic evidence; complete localization report digest covers the complete artifact.
96. Recomputed digests cannot hide selector, command, claim, specification, producer, receipt, tree, commit, or source-report substitution.
97. A discriminating selector proves only the exact declared transition, not semantic claim relevance or oracle strength.
98. Public selector artifacts exclude raw output and absolute local paths by default.

### Paired import-error observer probe

99. Both arms use the same scenario ID, family, control role, generator, template, timeout, path categories, and source/test bytes.
100. Only observer-derived descriptor fields may differ.
101. Candidate tests import a fixed candidate-introduced symbol before assertions.
102. `O0_EXIT_CODE` records `BC = fail` and produces the declared complete accepted matrix.
103. `O1_TYPED_RECEIPT` records `BC = error`, receipt outcome `test_error`, zero assertion failures, at least one error, and incomplete evidence.
104. `M0` remains `accept`; `M1`–`M3` become `indeterminate` only in the typed arm.
105. `import_error` remains predeclared fixture ground truth and is never presented as a receipt-v1 runtime subtype.
106. Both manifests remain development-partition and primary-denominator ineligible.
107. Public artifacts contain no raw traceback or absolute local path.

### Unrelated-assertion negative control

108. Both arms use the same scenario ID, family, control role, generator, template, timeout, path categories, and source/test bytes.
109. Base and candidate expose fixed claim-facing and collateral behavior dimensions.
110. The claim-facing viewer test executes the declared behavior but asserts only a property that passes on base and candidate.
111. A separate fixed collateral assertion is the sole source of `BC = fail`.
112. Direct controls require the claim-facing test to pass against both code versions.
113. Direct controls require the complete candidate suite to fail against base code and the suite without the collateral assertion to pass.
114. `O0_EXIT_CODE` records `BC = fail` with cause `test_failure_untyped`.
115. `O1_TYPED_RECEIPT` records `BC = fail`, outcome `test_failure`, at least one assertion failure, and zero errors.
116. Both reports remain complete and supported and `M0` through `M3` accept.
117. Declared-selector localization classifies the claim-facing selector as non-discriminating.
118. Both manifests remain development-partition and primary-denominator ineligible.
119. Public artifacts contain no raw failure narrative or absolute local path.
120. The result is documented as a limitation and is never presented as oracle-relevance validation.

### Weak-proxy-oracle negative control

121. The task prompt, base, candidate, candidate tests, mutant, hidden claim check, declared selector, hidden selector, and expected outcomes are fixed before execution.
122. The task is labeled `fixed_owned_synthetic_agent_workflow_surrogate` and carries no model identity.
123. Both observer arms produce the canonical `pass / fail / pass / pass` matrix and `M0` through `M3` accept.
124. Under typed observation, `BC` is a real assertion failure with at least one failure and zero errors.
125. The exact declared selector localizes as `supported` and `discriminating`.
126. The fixed mutant preserves the declared Boolean proxy while violating viewer denial.
127. The declared selector fails on base and passes on candidate and mutant.
128. The fixed hidden development claim check passes on candidate and fails on mutant.
129. The hidden check is not exposed as a general oracle or confirmatory holdout.
130. Exactly five ordered shell-free typed controls execute with fixed implementation, role, selector, source/test digest, command, binding, return code, receipt, and counts.
131. Every control uses `outcome-receipt-v1`; missing, malformed, contradictory, or multi-test evidence fails closed.
132. Source preflight independently verifies descriptor, identity, matrix report, projection, declaration, and localization relations.
133. The challenge binds stable semantic views of projection and localization evidence rather than volatile timestamps or durations.
134. Repeated clean execution of equivalent sources emits identical challenge semantics and canonical bytes.
135. `challenge_sha256` covers stable challenge semantics and `report_sha256` covers the complete artifact.
136. Recomputing both digests cannot hide task, source, selector, mutant, control, finding, limitation, or denominator substitution because the verifier reconstructs the complete artifact.
137. `primary_denominator_eligible` is always false.
138. Raw stdout, stderr, traceback, absolute paths, credentials, and environment values are excluded.
139. One surviving mutant does not establish mutation-score adequacy or general oracle weakness.
140. The challenge is never presented as an ecological agent evaluation, model comparison, or Gate 1 completion.

### Execution, packaging, and publication

141. Commands execute without a shell.
142. The full host environment is not inherited.
143. Raw output is excluded unless explicitly requested.
144. Absolute repository and specification paths are excluded from public artifacts.
145. Default reports live in private Git metadata.
146. Ambiguous configuration and harness errors stop analysis.
147. Editable-install and installed-wheel smoke execute complete fixture, localization, challenge, and pilot paths for supported development probes.
148. Packaged smoke is not independent reproduction.
149. Every exported fixture, binding, report, projection, declaration, localization, challenge, manifest, result, pilot index, archive, or source-universe artifact requires privacy and boundary review.
150. No current development challenge authorizes execution of external or untrusted repositories.

### Development mechanism pilot plan and runner

151. The historical plan contains exactly ten ordered development arms derived from its sealed five-family population and two observer arms.
152. The plan pins exact protocol and evidence-producing implementation commits and records exact contract versions, case IDs, descriptors, specification digests, state/method expectations, selectors, analysis rules, and cost policy.
153. The plan contains no holdout lock and every case is primary-denominator ineligible.
154. Recomputing `plan_sha256` cannot hide a changed family, observer, selector, expectation, order, cost policy, or denominator field because the verifier rebuilds the canonical plan.
155. The runner verifies the complete plan before creating final output.
156. The runner derives executable descriptors and declarations and accepts no free-form executable fixture input or expected labels.
157. Every required per-case artifact is independently verified before case acceptance.
158. Unexpected method or localization results stop execution and are not silently relabeled.
159. Aggregate analysis is derived from verified case tables and is withheld when any controlled contrast is unexpected.
160. The index emits no headline score and forbids ecological inference.
161. Per-case cost fields reject negative, non-finite, and silently zero missing values; human review missingness remains explicit.
162. The public runner requires an absent final destination, stages adjacent to it, self-verifies the exact bundle, and publishes through one same-filesystem rename only after success.
163. A failed run removes staging output and leaves final output absent.
164. A development pilot cannot create holdout or confirmatory eligibility.

### Development mechanism pilot archive

165. The archive contains exactly the sorted unique safe relative JSON paths derived from the sealed plan.
166. Missing, duplicate, unsafe, linked, special, reordered, substituted, or unexpected JSON and non-JSON entries fail closed.
167. Every embedded file record has a canonical digest over path and document.
168. `archive_sha256` covers the complete archive with its own field normalized to `null`.
169. Archive verification requires the committed plan digest and embedded index semantic digest.
170. The archive verifier reconstructs the complete directory bundle and reruns all artifact-specific and cross-artifact verifiers.
171. The verifier rematerializes every retained synthetic fixture from its descriptor and requires exact identity equality.
172. A complete archive digest may vary with volatile timestamps or costs; the semantic index digest is the repeated-run comparison field.
173. The canonical archive remains development-only and contains no raw output or absolute local paths.
174. Historical temporary artifact-upload and branch-write mechanisms are removed from the final workflow and are not product capabilities.

### Ecological source-universe design

175. The source-universe artifact is reconstructed from fixed reviewed metadata and one reviewed DeltaWitness `main` commit.
176. Candidate benchmark implementation repositories are pinned to exact commits; moving branches are not accepted as identities.
177. Repository-level SPDX metadata is recorded separately from dataset-release, underlying-project, patch, test, environment, execution, redistribution, and publication authorization.
178. Dataset releases remain explicitly unpinned until immutable release metadata and instance manifests are reviewed.
179. Environment feasibility remains `unreviewed` and containment remains `unaccepted`.
180. Root and per-source execution authorization remain false.
181. Target population, sampling frame, unit of analysis, reviewer protocol, precision target, and development/holdout split remain unfrozen.
182. `holdout_selected` and `holdout_inspected` remain false.
183. Known biases and unresolved blockers remain machine-readable and cannot be deleted after digest recomputation.
184. Recomputed universe digest cannot hide source, revision, license, authorization, containment, sampling, or holdout substitution because the verifier reconstructs the canonical artifact.
185. The artifact contains metadata only and excludes dataset rows, issue texts, patches, tests, source code, credentials, local paths, and holdout material.
186. A valid source-universe artifact does not authorize download, instance admission, repository execution, or ecological inference.

## Residual risks

### No operating-system sandbox

DeltaWitness and its generators are not containment systems. Executed code can read or modify accessible files, use the network, start processes, exhaust resources, affect external systems, exploit local dependencies, or forge a visible receipt binding.

Use a separately secured disposable environment without credentials for untrusted code. Current owned-synthetic challenges do not make external execution safe.

### Git state is not a complete environment model

Trees and commits do not bind interpreter, compiler, dependencies, kernel, hardware, locale, clock, network, external services, filesystem behavior, or container image.

Equivalent Git objects do not establish equivalent execution environments.

### Symbolic-link checks are narrow

Rejecting changed links and a linked fixture destination does not establish trust in unchanged links, destination ancestors, mounts, namespaces, or external paths.

### Typed receipts are not attestations or complete diagnoses

The cooperating adapter improves failure/error precision, but receipts are unsigned and binding is visible. The import probe shows one distinction between assertion failure and generic error. It does not show reliable error-subtype diagnosis or resistance to malicious tested code.

### Exact selector provenance is not semantic relevance

The unrelated-assertion control demonstrates that suite-level fail-to-pass can be caused by collateral behavior. Declared-selector localization improves provenance by executing an exact predeclared logical test, but operator declaration can still be wrong, incomplete, or adversarial.

A discriminating selector does not prove that its assertion expresses the intended claim.

### Typed localized fail-to-pass is not oracle strength

The weak-proxy challenge demonstrates that a real typed assertion failure and exact selector fail-to-pass transition can assert only a proxy property. One fixed claim-violating mutant survives that selector.

This does not define a complete mutation set, prove that the hidden check is complete, or estimate the prevalence of weak oracles. A future oracle-strength layer requires predeclared mutation operators, positive and negative controls, measured error rates, applicability, cost, and an independent policy boundary.

An LLM-generated explanation cannot count as independent confirmation.

### Ground-truth subtype and intent risk

Fixed synthetic mechanism labels are auditable from owned bytes and direct controls. Real-corpus failure subtypes, claim relevance, intended behavior, and mutation validity may be ambiguous and susceptible to post-result relabeling.

A frozen ecological protocol needs independent pre-execution review, disagreement handling, and unknown labels where evidence is insufficient.

### Fixed synthetic pilot and challenges are not ecological evidence

The pilot arms and later weak-proxy task are designed mechanism probes, not independent or representative samples. Successful execution establishes pipeline behavior and specific counterexamples only.

They cannot support prevalence, accuracy, precision, recall, superiority, model-quality, or production-utility claims and cannot later become a holdout.

### Pilot plan and execution provenance are not authenticated

The plan pins protocol and evidence-producing implementation commits. Later archive packaging, workflow, and transport revisions are recorded separately in Git history. Current unkeyed records do not prove who executed the plan, that the run occurred at a claimed time, or that workflow metadata is complete.

### Costs are diagnostics, not native-method or population estimates

Per-case timings and byte counts are environment-sensitive. Full-matrix projection does not measure native `M0`, `M1`, or `M2` runtime. Human review time is unmeasured. The archive preserves these limitations rather than imputing zero.

### Historical transport capability

The canonical archive required separately reviewed one-time GitHub artifact transport and an exact branch-scoped write. Both mechanisms were removed before final validation. Their historical use expands the trusted process for that run but does not create a continuing upload or write capability.

### Path interventions are coarse

One path may contain multiple changes and one change may span paths. Rename or grouping choices alter the coalition game. Influence values are not correctness, severity, ownership, blame, oracle relevance, or oracle strength.

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

The development pilot executes 40 matrix states and 12 selector states. The weak-proxy challenge adds five fixed typed controls. These counts do not establish a safe resource bound for ecological repositories.

### Publication metadata can remain sensitive

Artifacts may expose commands, relative paths, Git IDs, scenario/family labels, prompts, test selectors, mutant identifiers, reviewer records, authorization references, exclusions, deviations, digests, counts, timings, and costs. Low-entropy digests can reveal equality or permit guessing.

## Safe operation

- Run only trusted repositories and commands, or use a separately secured disposable environment.
- Verify exact refs, cleanliness, specification, and path classification before execution.
- Prefer typed observers when a trusted adapter exists, but never treat receipts as attestations.
- Do not infer a precise error subtype from generic `test_error` without independently fixed evidence.
- Do not infer claim relevance from suite `test_failure`, failure counts, or a canonical matrix.
- Do not infer oracle strength from one discriminating selector or one surviving/killed mutant.
- Require selector declarations before execution and preserve every per-selector outcome.
- Freeze mutation operators, mutant sets, hidden checks, thresholds, and exclusions before outcome inspection when they are used for evaluation.
- Treat execution-sensitive configuration and generated inputs as code.
- Review every incomplete state, invalid hybrid, endpoint anchor, selector, coalition, and mutation control before interpretation.
- Treat exact influence as enumeration over declared units, not complete causality.
- Strict-decode and verify every report, projection, descriptor, identity, binding, declaration, localization, challenge, manifest, result, pilot plan, pilot index, pilot archive, and source-universe artifact separately.
- Verify generated identity against its repository before using its commits.
- Require paired observer probes to hold mechanism and scenario identity constant.
- Require oracle-relevance controls to prove directly which assertion is the sole suite-level failure source.
- Require weak-oracle controls to prove both mutant survival under the declared selector and claim violation under a separately fixed development check.
- Run only an exact sealed pilot plan and reject runtime free-form cases or expectations.
- Require complete staged-bundle and reconstructed-archive verification before interpreting a pilot result.
- Keep every mechanism-pilot and weak-oracle case development-only and outside the primary denominator.
- Keep ecological execution unauthorized until instance licensing, sampling, review, environment, and containment contracts are accepted.
- Preserve exclusions, disputes, negative results, surviving mutants, missing costs, and deviations rather than deleting or imputing them.
- Do not interpret fixed synthetic evidence as ecological effectiveness or holdout evidence.
- Do not run a DW-001 holdout while protocol and authorization gates are incomplete.
- Never interpret a green final state, `SUPPORTED_IN_SCOPE`, `ATTRIBUTION_AVAILABLE`, projected `accept`, typed assertion failure, discriminating selector, valid fixture/binding, verified synthetic pilot, source-universe record, or one fixed mutation challenge as full correctness, oracle adequacy, general effectiveness, production readiness, or deployment authorization.