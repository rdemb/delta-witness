"""Public DW-001 study-contract API with a fail-closed post-unblinding guard.

The internal module implements the versioned manifest/result contracts. This
public boundary adds an independent policy check: an applied deviation made
after results were visible cannot retain confirmatory eligibility.
"""

from __future__ import annotations

from typing import Any

from . import _dw001_contracts as _core

DW001ContractError = _core.DW001ContractError
RESULT_SCHEMA_VERSION = _core.RESULT_SCHEMA_VERSION
SCENARIO_SCHEMA_VERSION = _core.SCENARIO_SCHEMA_VERSION
STUDY_ID = _core.STUDY_ID
compute_result_sha256 = _core.compute_result_sha256
compute_scenario_manifest_sha256 = _core.compute_scenario_manifest_sha256
seal_scenario_manifest = _core.seal_scenario_manifest
verify_scenario_manifest_document = _core.verify_scenario_manifest_document


def _post_unblinding_deviation_errors(document: object) -> list[str]:
    """Return policy errors that cannot be inferred from digest consistency."""

    if not isinstance(document, dict):
        return []
    deviations = document.get("deviations")
    if not isinstance(deviations, list):
        return []

    errors: list[str] = []
    for index, item in enumerate(deviations):
        if (
            isinstance(item, dict)
            and item.get("status") == "applied"
            and item.get("results_visible") is True
            and item.get("confirmatory_impact") == "none"
        ):
            errors.append(
                f"result record.deviations[{index}]: results-visible applied "
                "deviation cannot retain confirmatory eligibility"
            )
    return errors


def _require_no_post_unblinding_confirmatory_deviation(document: object) -> None:
    errors = _post_unblinding_deviation_errors(document)
    if errors:
        raise DW001ContractError(errors[0])


def seal_result_record(document: object) -> dict[str, Any]:
    """Seal only records that respect the post-unblinding deviation boundary."""

    _require_no_post_unblinding_confirmatory_deviation(document)
    return _core.seal_result_record(document)


def verify_result_record_document(document: object) -> tuple[bool, tuple[str, ...]]:
    """Verify core semantics, digest integrity, and post-unblinding policy."""

    valid, errors = _core.verify_result_record_document(document)
    combined = tuple(
        dict.fromkeys((*errors, *_post_unblinding_deviation_errors(document)))
    )
    return valid and not combined, combined


def verify_result_against_sources(
    result: object,
    manifest: object,
    projection: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify all source bindings plus the post-unblinding deviation policy."""

    valid, errors = _core.verify_result_against_sources(result, manifest, projection)
    combined = tuple(
        dict.fromkeys((*errors, *_post_unblinding_deviation_errors(result)))
    )
    return valid and not combined, combined


__all__ = [
    "DW001ContractError",
    "RESULT_SCHEMA_VERSION",
    "SCENARIO_SCHEMA_VERSION",
    "STUDY_ID",
    "compute_result_sha256",
    "compute_scenario_manifest_sha256",
    "seal_result_record",
    "seal_scenario_manifest",
    "verify_result_against_sources",
    "verify_result_record_document",
    "verify_scenario_manifest_document",
]
