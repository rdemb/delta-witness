# Changelog

## Unreleased

### Claim-scoped statement-coverage baseline

- Add `deltawitness.dw001-statement-coverage-result.v1` as a strict development-only direct-baseline contract over the exact frozen mutation plan, catalog, source target, selector profiles, and mutation-result semantic digest.
- Add `deltawitness.statement-trace-receipt.v1`, a bounded invocation-bound trace artifact for one exact relative source path, symbol, source digest, and target-line set.
- Add the `stdlib-statement-trace-v1` adapter using current-thread `sys.settrace` call and line events for fixed project-owned Python fixtures.
- Execute the exact strong authorization selectors and weak Boolean-proxy selector against the same unmutated candidate source.
- Record per-selector typed outcomes, target-function call count, covered target-line set, per-line hit counts, trace status, trace diagnostics, and trace digest.
- Derive profile union and intersection line sets independently from raw hit-count magnitude; hit counts remain diagnostics because profile selector counts differ.
- Compare the statement signatures with the independently verified frozen claim-scoped mutation result.
- Retain complete preregistration-divergent coverage signatures as valid negative results with `analysis.status = unexpected`.
- Preserve missing, malformed, unavailable, or failed trace evidence as `indeterminate`; it is never converted into an empty covered-line set.
- Recompute selector, profile, comparison, analysis, policy, cost, semantic-digest, and complete-report relations before accepting the artifact.
- Keep quality score, headline score, universal threshold, merge-blocker authorization, ecological inference, holdout selection, primary-denominator eligibility, and coverage/mutation superiority claims null or false.
- Add adversarial tests for duplicate keys, symbolic links, target substitution, line-set drift, hit-count drift, indeterminate evidence, non-finite values, policy drift, and recomputed-digest tampering.
- Add direct probe regressions for both normal dual-receipt production and fail-closed `producer_error` plus bound indeterminate trace fallback.
- Fix trace-receipt serialization to append a byte newline to canonical JSON bytes rather than concatenating text and bytes; the former implementation raised `TypeError` and prevented both normal and fallback trace receipts.
- Exercise the complete statement-coverage path from editable and force-reinstalled wheel packages on Python 3.11–3.14.
- Document the direct prior-art boundary, execution model, privacy boundary, falsification criteria, and narrow current observation that both fixed profiles cover the same target statement while the frozen mutation table distinguishes them.

### Claim-scoped mutation result

- Add `deltawitness.dw001-claim-scoped-mutation-result.v1` as a strict development-only result contract over the exact frozen mutation plan and catalog.
- Execute only the candidate baseline, three generic generated mutants, and the separately labeled historical PR #34 control through 25 invocation-bound typed selector commands.
- Retain duplicate, invalid, and not-applicable generation records with explicit zero-command non-execution reasons and exclude them from killed/survived denominators.
- Store frozen expected evidence separately from observed evidence and recompute selector, profile, reference, record, summary, and analysis concordance.
- Retain complete preregistration-divergent observations as negative results rather than converting them into harness errors.
- Continue to reject malformed, substituted, contradictory, aggregate-inconsistent, non-finite, or digest-tampered evidence even when labelled unexpected.
- Separate stable result semantics from runtime diagnostics through semantic and complete-report digests.
- Keep mutation score, thresholds, merge blockers, holdout selection, ecological inference, and primary-denominator eligibility disabled.

### Claim-scoped mutation design

- Add deterministic pre-execution mutation plan and mutant catalog contracts for one fixed project-owned Python source and one exact AST return-expression target.
- Freeze three outcome-blind generic operators before mutation-test outcomes: return `False`, return `True`, and replace one `==` comparison with `!=`.
- Retain generated, duplicate, not-applicable, and invalid mutation records with exact source, AST, target, and mutant identities.
- Freeze paired strong-authorization and weak-Boolean-proxy selector profiles over the same source and generic mutants.
- Keep the previously observed `nonempty-role-boolean-v1` mutant as a separately labelled historical control outside generic-operator evidence.

### DW-001 selector and oracle controls

- Add exact declared unittest-selector localization under reconstructed `base_candidate` and `candidate_candidate` states.
- Add the fixed import-error observer contrast showing that raw exit codes can accept a pre-assertion error as fail-to-pass while typed receipts preserve incomplete evidence.
- Add the unrelated-assertion negative control showing that genuine typed suite failure does not establish claim relevance.
- Add the weak-proxy negative control showing that a genuine typed, localized fail-to-pass selector can still admit a fixed claim-violating mutant.
- Add strict fixture, identity, fixture-manifest binding, scenario-manifest, result-record, projection, localization, challenge, pilot-plan, pilot-index, pilot-archive, and ecological-source-universe contracts.
- Execute and retain the sealed five-family, ten-arm owned-synthetic development mechanism pilot without headline score or ecological inference.

## 0.0.3 - 2026-08-15

- Added `deltawitness influence` for exhaustive intervention analysis of patches with at most eight changed code paths.
- Added exact evaluation of every path coalition under both base and candidate test worlds.
- Added endpoint anchors, complete/unsupported/indeterminate coalition semantics, deterministic Git identities, minimal sufficient coalitions, necessity, sufficiency, marginal swings, exact rational Shapley allocation, normalized Banzhaf influence, pairwise interaction, and monotonicity diagnostics.
- Withhold all exact attribution when the coalition table is incomplete or endpoint semantics are inconsistent.
- Added the exact patch-influence schema, semantic and complete-report integrity verification, end-to-end fixtures, documentation, threat boundaries, and public demonstration.

## 0.0.2 - 2026-08-15

- Added the optional invocation-bound `outcome-receipt-v1` observer.
- Added dual-channel receipt and exit-code consistency checks.
- Added a built-in standard-library unittest receipt producer distinguishing assertion failure from generic test error, empty discovery, ineffective all-skipped execution, and unexpected success.
- Added strict bounded duplicate-key-safe receipt parsing and schema `0.3` observer evidence.
- Rejected changed symbolic-link entries before counterfactual state construction.

## 0.0.1 - 2026-08-15

- Added the initial four-state Git matrix.
- Added NUL-safe changed-path parsing, explicit exclusive path classification, ancestry checks, changed-submodule rejection, exact state tree IDs, deterministic synthetic hybrid commits, per-claim restoration, reduced execution environments, raw-output exclusion, and semantic plus complete report digests.
- Added the initial self-contained demo, test suite, architecture, threat model, research boundary, and publication policy.
