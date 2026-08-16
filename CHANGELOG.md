# Changelog

## Unreleased

- Add versioned DW-001 scenario-manifest and result-record contracts for pre-execution ground truth and post-execution evidence.
- Recompute method ground truth from ordered state applicability and expected outcomes instead of trusting stored labels.
- Bind result records explicitly to the supplied scenario manifest and DW-001 projection, including scenario, partition, Git endpoints, observer arm, applicability, source digests, decisions, concordance, and denominator membership.
- Add development and committed-holdout partition locks, public-safe provenance fields, reviewer independence disclosures, exclusions, protocol deviations, and explicit cost missingness.
- Prevent partition relabeling, denominator drift, unapproved deviations, exclusion-with-eligibility, wrong manifest/projection links, and non-finite cost values from being hidden by recomputed unkeyed digests.
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
