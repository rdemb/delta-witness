# Changelog

## Unreleased

No unreleased changes are currently declared.

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
