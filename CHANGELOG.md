# Changelog

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
