"""Placeholder API for declared logical-test witness localization.

The red-first tests define the intended declaration, exact selector command,
BC/CC execution, classification, and cross-artifact verification semantics.
Implementation is intentionally absent in this commit.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import WitnessConfig
from .errors import DeltaWitnessError


DECLARATION_SCHEMA_VERSION = "deltawitness.claim-witness-declaration.v1"
LOCALIZATION_SCHEMA_VERSION = "deltawitness.claim-witness-localization.v1"
ADAPTER_ID = "unittest-test-id-v1"
ADAPTER_VERSION = "1"
AGGREGATE_RULE = "at_least_one_discriminating_and_none_indeterminate"


class ClaimWitnessError(DeltaWitnessError):
    """Raised when declared logical-test witness evidence is unsafe or invalid."""


def _unimplemented() -> ClaimWitnessError:
    return ClaimWitnessError("claim witness localization is not implemented")


def canonical_unittest_selector_command(selector: str) -> list[str]:
    raise _unimplemented()


def compute_claim_witness_declaration_sha256(document: dict[str, Any]) -> str:
    raise _unimplemented()


def build_claim_witness_declaration(
    *,
    spec_sha256: str,
    claim_id: str,
    selectors: list[str] | tuple[str, ...],
) -> dict[str, Any]:
    raise _unimplemented()


def verify_claim_witness_declaration_document(
    document: object,
) -> tuple[bool, tuple[str, ...]]:
    raise _unimplemented()


def compute_claim_witness_localization_sha256(document: dict[str, Any]) -> str:
    raise _unimplemented()


def compute_claim_witness_localization_report_sha256(
    document: dict[str, Any],
) -> str:
    raise _unimplemented()


def run_claim_witness_localization(
    repo: Path,
    config: WitnessConfig,
    source_report: object,
    declaration: object,
) -> dict[str, Any]:
    raise _unimplemented()


def verify_claim_witness_localization_document(
    document: object,
    declaration: object,
    source_report: object,
) -> tuple[bool, tuple[str, ...]]:
    raise _unimplemented()


__all__ = [
    "ADAPTER_ID",
    "ADAPTER_VERSION",
    "AGGREGATE_RULE",
    "DECLARATION_SCHEMA_VERSION",
    "LOCALIZATION_SCHEMA_VERSION",
    "ClaimWitnessError",
    "build_claim_witness_declaration",
    "canonical_unittest_selector_command",
    "compute_claim_witness_declaration_sha256",
    "compute_claim_witness_localization_report_sha256",
    "compute_claim_witness_localization_sha256",
    "run_claim_witness_localization",
    "verify_claim_witness_declaration_document",
    "verify_claim_witness_localization_document",
]
