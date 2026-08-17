"""Public scaffold for the frozen DW-001 interaction-lattice result.

The separately authorized execution protocol exists and is verifiable. The
result runner and verifier remain deliberately unavailable until the normative
red-first contract has been retained in CI.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from .errors import DeltaWitnessError
from .reporting import load_report, sha256_document


RESULT_SCHEMA_VERSION = (
    "deltawitness.dw001-interaction-witness-lattice-result.v1"
)
RESULT_ID = "DW-001-INTERACTION-WITNESS-LATTICE-RESULT-V1"
EXECUTION_PROTOCOL_SHA256 = (
    "e10a9e287555ee8a1b8c0a9b7768d2f949c04a70081a778d51fefb78c1276912"
)
PLAN_SHA256 = (
    "a79a500feb94c8ad78fe4633f9ca176465113de6297db2d07b2d005f5318e1f1"
)
CATALOG_SHA256 = (
    "2b06a86180a45fcd495c0bcf39365dde0cb590507e9a3528714f9ef58526308e"
)
PRIOR_ART_LOG_SHA256 = (
    "af6cb9782ea01a0e58baed8cfc1a4895dc1a53ed934498b307c6b05e8634c44f"
)


class DW001InteractionLatticeResultError(DeltaWitnessError):
    """Raised when the frozen interaction-lattice result cannot be produced."""


def _semantic_view(document: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(document)
    normalized["created_at"] = None
    normalized["runtime"] = None
    normalized["semantic_sha256"] = None
    normalized["report_sha256"] = None
    return normalized


def compute_interaction_lattice_result_semantic_sha256(
    document: dict[str, Any],
) -> str:
    """Hash stable result semantics once the runner is implemented."""

    if not isinstance(document, dict):
        raise DW001InteractionLatticeResultError(
            "interaction-lattice result must be an object"
        )
    return sha256_document(_semantic_view(document))


def compute_interaction_lattice_result_report_sha256(
    document: dict[str, Any],
) -> str:
    """Hash the complete result with only its report digest normalized."""

    if not isinstance(document, dict):
        raise DW001InteractionLatticeResultError(
            "interaction-lattice result must be an object"
        )
    normalized = deepcopy(document)
    normalized["report_sha256"] = None
    return sha256_document(normalized)


def run_interaction_witness_lattice_result(
    execution_protocol: object,
    plan: object,
    catalog: object,
    prior_art: object,
    coveragepy_manifest: object,
    pr46_result: object,
) -> dict[str, Any]:
    """Execute the exact fixed experiment after red evidence is retained."""

    raise DW001InteractionLatticeResultError(
        "interaction-witness lattice result is intentionally not implemented"
    )


def verify_interaction_witness_lattice_result_document(
    document: object,
    execution_protocol: object,
    plan: object,
    catalog: object,
    prior_art: object,
    coveragepy_manifest: object,
    pr46_result: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify one result after the red-first contract is retained."""

    return False, (
        "interaction-witness lattice result is intentionally not implemented",
    )


def load_interaction_witness_lattice_result(
    path: Path,
    execution_protocol: object,
    plan: object,
    catalog: object,
    prior_art: object,
    coveragepy_manifest: object,
    pr46_result: object,
) -> dict[str, Any]:
    """Strict-load and verify one result document."""

    document = load_report(path)
    valid, errors = verify_interaction_witness_lattice_result_document(
        document,
        execution_protocol,
        plan,
        catalog,
        prior_art,
        coveragepy_manifest,
        pr46_result,
    )
    if not valid:
        raise DW001InteractionLatticeResultError("; ".join(errors))
    return document


__all__ = [
    "CATALOG_SHA256",
    "DW001InteractionLatticeResultError",
    "EXECUTION_PROTOCOL_SHA256",
    "PLAN_SHA256",
    "PRIOR_ART_LOG_SHA256",
    "RESULT_ID",
    "RESULT_SCHEMA_VERSION",
    "compute_interaction_lattice_result_report_sha256",
    "compute_interaction_lattice_result_semantic_sha256",
    "load_interaction_witness_lattice_result",
    "run_interaction_witness_lattice_result",
    "verify_interaction_witness_lattice_result_document",
]
