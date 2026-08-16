"""Typed result boundary for the frozen DW-001 mutation catalog.

The completed implementation will execute only the exact project-owned source,
mutants, selectors, and reference checks frozen by PR #38. This red-first stub
fails closed until result semantics and verification are implemented.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .errors import DeltaWitnessError
from .reporting import sha256_document


RESULT_SCHEMA_VERSION = "deltawitness.dw001-claim-scoped-mutation-result.v1"
RESULT_ID = "DW-001-CLAIM-SCOPED-MUTATION-RESULT-V1"


class DW001MutationResultError(DeltaWitnessError):
    """Raised when mutation-result execution or verification fails closed."""


def compute_mutation_result_semantic_sha256(document: dict[str, Any]) -> str:
    normalized = deepcopy(document)
    normalized["semantic_sha256"] = None
    normalized["report_sha256"] = None
    normalized.pop("created_at", None)
    normalized.pop("runtime", None)
    for implementation in [document.get("candidate_baseline"), *document.get("records", [])]:
        if isinstance(implementation, dict):
            cost = implementation.get("cost")
            if isinstance(cost, dict):
                cost["wall_clock_seconds"] = None
                cost["cpu_seconds"] = None
            for profile in implementation.get("profiles", []):
                for selector in profile.get("selectors", []):
                    selector["duration_seconds"] = None
            reference = implementation.get("reference")
            if isinstance(reference, dict):
                for selector in reference.get("selectors", []):
                    selector["duration_seconds"] = None
    return sha256_document(normalized)


def compute_mutation_result_report_sha256(document: dict[str, Any]) -> str:
    normalized = deepcopy(document)
    normalized["report_sha256"] = None
    return sha256_document(normalized)


def _unimplemented() -> DW001MutationResultError:
    return DW001MutationResultError(
        "claim-scoped mutation result execution is not implemented"
    )


def run_claim_scoped_mutation_result(
    plan: object,
    catalog: object,
) -> dict[str, Any]:
    raise _unimplemented()


def verify_claim_scoped_mutation_result_document(
    document: object,
    plan: object,
    catalog: object,
) -> tuple[bool, tuple[str, ...]]:
    return False, (str(_unimplemented()),)


__all__ = [
    "DW001MutationResultError",
    "RESULT_ID",
    "RESULT_SCHEMA_VERSION",
    "compute_mutation_result_report_sha256",
    "compute_mutation_result_semantic_sha256",
    "run_claim_scoped_mutation_result",
    "verify_claim_scoped_mutation_result_document",
]
