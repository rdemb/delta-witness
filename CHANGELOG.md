# Changelog

## Unreleased

- Add the fixed `wrong-reason-unrelated-assertion` DW-001 family as an oracle-relevance negative control with identical scenario identity and source/test mechanism across exit-code and typed-receipt arms.
- Prove directly that the claim-facing viewer assertion passes on both base and candidate implementations while a separate collateral `version_label == "v2"` assertion is the sole source of `BC = fail`.
- Demonstrate one controlled limitation where `O0_EXIT_CODE` records `test_failure_untyped`, `O1_TYPED_RECEIPT` records a genuine `test_failure` with assertion failures and zero errors, and both observers still yield a complete accepted `M0`–`M3` witness.
- Keep outcome semantics and oracle relevance as separate layers: typed assertion failure does not identify which assertion witnessed the declared claim or establish oracle adequacy.
- Extend the pre-freeze fixture descriptor, identity, and binding family enums without rewriting existing artifacts; exact verifier and schema commits remain required until protocol freeze.
- Exercise the unrelated-assertion control through descriptor, identity, materialized repository, manifest, fixture-manifest binding, strict report, projection, editable install, and installed wheel.
- Add the fixed `wrong-reason-base-import-failure` DW-001 family as a paired observer probe with identical source/test mechanism and scenario identity across exit-code and typed-receipt arms.
- Demonstrate one controlled case where `exit-code-v1` treats a pre-assertion import error as semantic `fail`, producing a complete accepted `M0`–`M3` witness, while `outcome-receipt-v1` preserves generic `test_error` evidence and makes `M1`–`M3` indeterminate.
- Keep runtime and ground-truth layers explicit: receipt v1 reports generic `test_error`; `import_error` is fixed pre-execution ground truth for the exact owned-synthetic bytes and is not inferred from the receipt.
- Require observer-pair tests to hold scenario ID and source/test bytes constant and allow only declared observer-derived descriptor fields to differ.
- Extend pre-freeze fixture descriptor, identity, and binding family/cause enums while preserving existing artifact validity and digest meaning; exact verifier commits remain mandatory for reproduction.
- Exercise the paired observer probe through descriptor, identity, materialized repository, manifest, fixture-manifest binding, strict matrix report, projection, editable install, and installed wheel.
- Add `deltawitness.dw001-fixture-manifest-binding.v1` as a strict relation among one verified fixture descriptor, fixture identity, and scenario manifest without mutating any issued scenario-manifest v1 fields.
- Derive fixture-manifest bindings only from independently verified source artifacts and recompute the complete relation before accepting `binding_sha256`.
- Separate verified relations, manifest-owned governance fields, and fixture-only Git/specification fields in a machine-readable scope contract.
- Reject mismatched commits, paths, observer arms, commands, state semantics, method decisions, family labels, malformed objects, private paths, and recomputed-digest relation substitutions.
- Bind fixture identity specification SHA-256 to the exact descriptor-derived specification bytes instead of accepting a self-consistent substituted digest.
- Exercise fixture binding construction and verification from editable and installed-wheel packages on Python 3.11–3.14.
- Add a versioned DW-001 scenario taxonomy that separates five implemented deterministic mechanism probes from required but unsupported future families.
- Add strict fixture-descriptor and fixture-identity schemas with semantic recomputation of expected nested-method decisions.
- Add a shell-free owned-synthetic Python/Git generator with fixed bytes, Git metadata, timestamps, messages, SHA-1 object identities, and specification digests.
- Require equivalent descriptors to reproduce identical base/head commits and trees across clean directories under the supported Git object model.
- Reject unsupported descriptors, non-empty destinations, and symbolic-link destination paths before synthetic fixture materialization.
- Verify generated repositories against recorded commit, tree, ancestry, cleanliness, and specification identities, and exercise the strict matrix-report-to-projection artifact chain.
- Exclude absolute destinations, usernames, environment values, and raw Git output from public fixture identities while retaining explicit residual trust boundaries.
- Add versioned DW-001 scenario-manifest and result-record contracts for pre-execution ground truth and post-execution evidence.
- Recompute method ground truth from ordered state applicability and expected outcomes instead of trusting stored labels.
- Bind result records explicitly to the supplied scenario manifest and DW-001 projection, including scenario, partition, Git endpoints, observer arm, applicability, source digests, decisions, concordance, and denominator membership.
- Add development and committed-holdout partition locks, public-safe provenance fields, reviewer independence disclosures, exclusions, protocol deviations, and explicit cost missingness.
- Prevent partition relabeling, denominator drift, unapproved deviations, exclusion-with-eligibility, wrong manifest/projection links, and non-finite cost values from being hidden by recomputed unkeyed digests.
- Reject results-visible applied deviations that attempt to retain confirmatory eligibility, and preflight malformed source artifacts before cross-artifact dereferencing.
- Add strict JSON Schemas for scenario manifests and result records while retaining the Python semantic verifier as authoritative for relational and cross-artifact invariants.
- Document the study-contract integrity, privacy, authentication, protocol-freeze, and publication boundaries without authorizing a development pilot or held-out execution.
- Add deterministic DW-001 projections for nested final-state, fail-to-pass, regression-preservation, and four-state method predicates from one integrity-verified matrix report.
- Keep observer semantics as a separate controlled factor by rejecting mixed-observer source reports and recording explicit exit-code and typed-receipt arms.
- Preserve `accept`, `reject`, `indeterminate`, and independently declared `not_applicable` outcomes without exposing hidden states to weaker projected methods.
- Recompute projection applicability, shared state slices, claim decisions, method decisions, and reason codes before accepting `projection_sha256`; a recomputed unkeyed digest cannot hide semantic inconsistency.
- Add the draft DW-001 development-pilot protocol, projection schema, integrity boundary, and adversarial regression fixtures without freezing the protocol or authorizing held-out execution.
- Reject duplicate object keys at every nesting level when loading matrix and influence reports.
- Convert malformed UTF-8 report bytes into fail-closed `ReportError` outcomes before digest verification.
- Preserve existing report schemas, canonical bytes, semantic digests, and valid-report behavior.
- Reject ancestor/descendant changed-path sets from file-to-directory or directory-to-file transitions before matrix or influence materialization.
- Preserve CLI outcome semantics for influence prerequisites: complete-but-unsupported witnesses return `1`, while incomplete or unsafe execution remains `2`.
- Keep patch-influence report schemas, digest algorithms, coalition metrics, and public claim boundaries unchanged.

## 0.0.3 - 2026-08-15

- Added `deltawitness influence` for exhaustive intervention analysis of patches with at most eight changed code paths.
- Added exact evaluation of every code-path coalition under both base and candidate test worlds.
- Added `supported`, `unsupported`, and `indeterminate` coalition semantics that preserve incomplete execution instead of treating it as negative evidence.
- Added mandatory endpoint anchors against the canonical four-state matrix and withheld attribution when held-constant paths alter endpoint semantics.
- Added exact Git tree and deterministic synthetic commit identities for every intervention state.
- Added every inclusion-minimal witness-sufficient coalition, global necessity, full-context necessity, standalone sufficiency, and paths absent from every minimal coalition.
- Added positive and negative marginal swing counts without assuming monotonicity.
- Added exact rational Shapley allocation, normalized Banzhaf influence, pairwise Banzhaf interaction, and an efficiency residual.
- Added report schema `deltawitness.patch-influence.v1` with `influence_sha256` and complete-report integrity verification.
- Added shared claim-state observation logic used by both canonical and intervention execution.
- Added synthetic mathematical fixtures for collateral, alternative, jointly necessary, and non-monotonic path structures.
- Added end-to-end fixtures for collateral changes, invalid partial import graphs, execution-sensitive documentation, and report tampering.
- Expanded the self-contained demonstration to run typed four-state verification, exact influence analysis, and integrity verification without dirtying the repository.
- Added the Exact Patch Influence protocol, architecture, threat model, evaluation hypotheses, prior-art boundary, and falsification criteria.

## 0.0.2 - 2026-08-15

- Rejected changed symbolic-link entries before counterfactual hybrid-state materialization.
- Added the optional `outcome-receipt-v1` observer for typed test outcomes.
- Added deterministic invocation bindings over claim, command, specification, state, tree, and commit identities.
- Added strict, bounded, duplicate-key-safe JSON receipt parsing with regular-file and symbolic-link checks.
- Added dual-channel consistency checks between receipt semantics and configured process exit codes.
- Added a built-in standard-library `unittest` receipt producer that distinguishes assertion failures from test errors, empty discovery, ineffective all-skipped execution, and unexpected successes.
- Added aggregate logical-test accounting that handles multiple failing subtests conservatively.
- Added report schema `0.3` with observer protocol, binding, receipt digest, producer, counts, outcome, and stable observer-error fields.
- Bound typed observer evidence into the semantic witness digest while preserving integrity verification for earlier schema `0.2` reports.
- Added adversarial tests for missing, malformed, oversized, state-mismatched, contradictory, and symbolic-link receipts.
- Added protocol, architecture, threat-model, roadmap, and public claim-boundary documentation.

## 0.0.1 - 2026-08-15

- Added the initial four-state counterfactual matrix.
- Added NUL-safe Git path parsing and explicit change classification.
- Added ancestry checks and changed-submodule rejection.
- Added exact tree IDs and deterministic synthetic commits for hybrid states.
- Added per-claim state restoration to prevent cross-claim contamination.
- Added sanitized command environments and raw-output exclusion by default.
- Added stable witness and exact report digests with an integrity-verification command.
- Added a self-contained demo, tests, threat model, research boundary, and publication policy.
- Added option-safe Git ref resolution and portable hashing for non-UTF-8 Git path bytes.
- Added explicit, disjoint pass/fail exit-code classes and incomplete-run handling.
- Moved the default report into private Git metadata to preserve working-tree cleanliness.
- Reduced the Git subprocess environment, disabled replacement objects, and rejected unsafe cross-platform changed paths.
