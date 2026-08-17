"""Public typed-result API for the frozen DW-001 mutation catalog.

The implementation retains complete but unexpected observations as valid
negative results. This facade keeps the public API narrow, exposes one test-only
observation seam used by regression fixtures, and enriches fail-closed verifier
diagnostics without changing validity decisions.
"""

from __future__ import annotations

from threading import RLock
from typing import Any

from . import _dw001_mutation_results as _implementation


RESULT_SCHEMA_VERSION = _implementation.RESULT_SCHEMA_VERSION
RESULT_ID = _implementation.RESULT_ID
DW001MutationResultError = _implementation.DW001MutationResultError

# Private sibling-fixture alias. Statement-coverage baselines must exercise the
# byte-identical candidate tests already frozen by the mutation-result contract
# rather than maintaining a second copy. It is intentionally omitted from
# __all__ and is not a caller-supplied execution surface.
_CALIBRATION_TESTS = _implementation._CALIBRATION_TESTS

# Deliberately module-scoped for one red-first regression that injects an
# internally consistent but preregistration-divergent observation. Product
# callers cannot supply an executor. The lock prevents cross-call contamination.
_execute_observation = _implementation._execute_observation
_expected_observation = _implementation._expected_observation
_EXECUTOR_LOCK = RLock()


def compute_mutation_result_semantic_sha256(document: dict[str, Any]) -> str:
    """Hash stable result semantics while excluding runtime and timing fields."""

    return _implementation.compute_mutation_result_semantic_sha256(document)


def compute_mutation_result_report_sha256(document: dict[str, Any]) -> str:
    """Hash the complete result with only its report digest normalized."""

    return _implementation.compute_mutation_result_report_sha256(document)


def run_claim_scoped_mutation_result(
    plan: object,
    catalog: object,
) -> dict[str, Any]:
    """Execute only the exact frozen owned-synthetic catalog and profiles."""

    with _EXECUTOR_LOCK:
        original = _implementation._execute_observation
        _implementation._execute_observation = _execute_observation
        try:
            return _implementation.run_claim_scoped_mutation_result(plan, catalog)
        finally:
            _implementation._execute_observation = original


def _difference_paths(
    expected: object,
    observed: object,
    *,
    path: str,
) -> list[str]:
    """Return precise structural paths while preserving type-sensitive equality."""

    if type(expected) is not type(observed):
        return [f"{path}: type or value mismatch"]
    if isinstance(expected, dict):
        errors: list[str] = []
        expected_keys = set(expected)
        observed_keys = set(observed)
        for key in sorted(expected_keys - observed_keys):
            errors.append(f"{path}.{key}: missing")
        for key in sorted(observed_keys - expected_keys):
            errors.append(f"{path}.{key}: unexpected")
        for key in sorted(expected_keys & observed_keys):
            errors.extend(
                _difference_paths(
                    expected[key],
                    observed[key],
                    path=f"{path}.{key}",
                )
            )
        return errors
    if isinstance(expected, list):
        errors = []
        if len(expected) != len(observed):
            errors.append(
                f"{path}: length mismatch; expected {len(expected)}, "
                f"observed {len(observed)}"
            )
        for index, (expected_item, observed_item) in enumerate(
            zip(expected, observed, strict=False)
        ):
            errors.extend(
                _difference_paths(
                    expected_item,
                    observed_item,
                    path=f"{path}[{index}]",
                )
            )
        return errors
    if expected != observed:
        return [f"{path}: value mismatch"]
    return []


def _diagnose_semantic_drift(
    document: object,
    plan: object,
    catalog: object,
) -> tuple[str, ...]:
    """Add field-level diagnostics without accepting any additional document."""

    if not isinstance(document, dict):
        return ()
    try:
        normalized_plan, normalized_catalog = _implementation._preflight(
            plan,
            catalog,
        )
        _, expected_records = _implementation._expected_templates(
            normalized_plan,
            normalized_catalog,
        )
    except Exception:
        return ()

    diagnostics: list[str] = []
    actual_records = document.get("records")
    if isinstance(actual_records, list):
        for index, expected_record in enumerate(expected_records):
            if index >= len(actual_records):
                break
            if expected_record.get("execution_status") != "executed":
                diagnostics.extend(
                    _difference_paths(
                        expected_record,
                        actual_records[index],
                        path=f"claim-scoped mutation result.records[{index}]",
                    )
                )

    policy = document.get("policy")
    if isinstance(policy, dict):
        diagnostics.extend(
            _difference_paths(
                _implementation._policy(),
                policy,
                path="claim-scoped mutation result.policy",
            )
        )

    candidate = document.get("candidate_baseline")
    if isinstance(candidate, dict) and isinstance(actual_records, list):
        try:
            expected_summary = _implementation._derive_summary(
                candidate,
                actual_records,
            )
        except Exception:
            pass
        else:
            summary = document.get("summary")
            if isinstance(summary, dict):
                diagnostics.extend(
                    _difference_paths(
                        expected_summary,
                        summary,
                        path="claim-scoped mutation result.summary",
                    )
                )

    return tuple(dict.fromkeys(diagnostics))


def verify_claim_scoped_mutation_result_document(
    document: object,
    plan: object,
    catalog: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify complete evidence and retain valid unexpected observations."""

    valid, errors = _implementation.verify_claim_scoped_mutation_result_document(
        document,
        plan,
        catalog,
    )
    if valid:
        return True, ()
    diagnostics = _diagnose_semantic_drift(document, plan, catalog)
    return False, tuple(dict.fromkeys((*diagnostics, *errors)))


__all__ = [
    "DW001MutationResultError",
    "RESULT_ID",
    "RESULT_SCHEMA_VERSION",
    "compute_mutation_result_report_sha256",
    "compute_mutation_result_semantic_sha256",
    "run_claim_scoped_mutation_result",
    "verify_claim_scoped_mutation_result_document",
]
