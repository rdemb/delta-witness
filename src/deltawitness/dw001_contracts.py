"""Draft DW-001 scenario-manifest and result-record contracts.

The initial verifier intentionally checks only artifact digests. Red-first
regressions on the draft branch demonstrate why semantic and cross-artifact
recomputation is required before this module can be merged.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .errors import DeltaWitnessError
from .reporting import sha256_document


STUDY_ID = "DW-001"
SCENARIO_SCHEMA_VERSION = "deltawitness.dw001-scenario-manifest.v1"
RESULT_SCHEMA_VERSION = "deltawitness.dw001-result-record.v1"


class DW001ContractError(DeltaWitnessError):
    """Raised when a DW-001 study contract cannot be constructed safely."""


def compute_scenario_manifest_sha256(document: dict[str, Any]) -> str:
    normalized = dict(document)
    normalized["manifest_sha256"] = None
    return sha256_document(normalized)


def compute_result_sha256(document: dict[str, Any]) -> str:
    normalized = dict(document)
    normalized["result_sha256"] = None
    return sha256_document(normalized)


def seal_scenario_manifest(document: object) -> dict[str, Any]:
    """Return a deterministic manifest carrying its unkeyed integrity digest."""

    if not isinstance(document, dict):
        raise DW001ContractError("Scenario manifest root must be an object")
    sealed = deepcopy(document)
    sealed["manifest_sha256"] = None
    sealed["manifest_sha256"] = compute_scenario_manifest_sha256(sealed)
    return sealed


def seal_result_record(document: object) -> dict[str, Any]:
    """Return a deterministic result record carrying its integrity digest."""

    if not isinstance(document, dict):
        raise DW001ContractError("Result record root must be an object")
    sealed = deepcopy(document)
    sealed["result_sha256"] = None
    sealed["result_sha256"] = compute_result_sha256(sealed)
    return sealed


def _verify_digest(
    document: object,
    *,
    field: str,
    label: str,
    computer: object,
) -> tuple[bool, tuple[str, ...]]:
    if not isinstance(document, dict):
        raise DW001ContractError(f"{label} root must be an object")
    expected = document.get(field)
    if not isinstance(expected, str) or len(expected) != 64:
        return False, (f"{field} is missing or invalid",)
    observed = computer(document)  # type: ignore[operator]
    if observed != expected:
        return False, (f"{label} digest mismatch: expected {expected}, computed {observed}",)
    return True, ()


def verify_scenario_manifest_document(document: object) -> tuple[bool, tuple[str, ...]]:
    """Verify the current draft manifest digest boundary."""

    return _verify_digest(
        document,
        field="manifest_sha256",
        label="scenario manifest",
        computer=compute_scenario_manifest_sha256,
    )


def verify_result_record_document(document: object) -> tuple[bool, tuple[str, ...]]:
    """Verify the current draft result-record digest boundary."""

    return _verify_digest(
        document,
        field="result_sha256",
        label="result record",
        computer=compute_result_sha256,
    )


def verify_result_against_sources(
    result: object,
    manifest: object,
    projection: object,
) -> tuple[bool, tuple[str, ...]]:
    """Draft cross-artifact verifier used to expose missing semantic checks."""

    errors: list[str] = []
    manifest_valid, manifest_errors = verify_scenario_manifest_document(manifest)
    if not manifest_valid:
        errors.extend(manifest_errors)
    result_valid, result_errors = verify_result_record_document(result)
    if not result_valid:
        errors.extend(result_errors)
    if not isinstance(projection, dict):
        errors.append("projection root must be an object")
    return not errors, tuple(errors)


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
