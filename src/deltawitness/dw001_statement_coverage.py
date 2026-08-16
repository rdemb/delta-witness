"""Predeclared DW-001 statement-coverage baseline boundary.

The completed implementation will execute only the exact project-owned
candidate source and selector profiles frozen by the claim-scoped mutation
plan, then compare their target-statement coverage signatures with the already
verified mutation-result evidence. This red-first stub deliberately fails
closed until the result and verifier contracts are implemented.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .errors import DeltaWitnessError
from .reporting import sha256_document


RESULT_SCHEMA_VERSION = "deltawitness.dw001-statement-coverage-result.v1"
RESULT_ID = "DW-001-STATEMENT-COVERAGE-RESULT-V1"
ADAPTER_ID = "stdlib-statement-trace-v1"
MUTATION_RESULT_SEMANTIC_SHA256 = (
    "9e101bca85fd630bf5bdb2a6030d9fdab93eb3eac54b03f4aab99012c28086b6"
)


class DW001StatementCoverageError(DeltaWitnessError):
    """Raised when statement-coverage evidence fails closed."""


def compute_statement_coverage_semantic_sha256(document: dict[str, Any]) -> str:
    normalized = deepcopy(document)
    normalized["semantic_sha256"] = None
    normalized["report_sha256"] = None
    normalized.pop("created_at", None)
    normalized.pop("runtime", None)
    return sha256_document(normalized)


def compute_statement_coverage_report_sha256(document: dict[str, Any]) -> str:
    normalized = deepcopy(document)
    normalized["report_sha256"] = None
    return sha256_document(normalized)


def _unimplemented() -> DW001StatementCoverageError:
    return DW001StatementCoverageError(
        "claim-scoped statement-coverage baseline is not implemented"
    )


def run_claim_scoped_statement_coverage(
    plan: object,
    catalog: object,
    mutation_result: object,
) -> dict[str, Any]:
    raise _unimplemented()


def verify_claim_scoped_statement_coverage_document(
    document: object,
    plan: object,
    catalog: object,
    mutation_result: object,
) -> tuple[bool, tuple[str, ...]]:
    return False, (str(_unimplemented()),)


__all__ = [
    "ADAPTER_ID",
    "DW001StatementCoverageError",
    "MUTATION_RESULT_SEMANTIC_SHA256",
    "RESULT_ID",
    "RESULT_SCHEMA_VERSION",
    "compute_statement_coverage_report_sha256",
    "compute_statement_coverage_semantic_sha256",
    "run_claim_scoped_statement_coverage",
    "verify_claim_scoped_statement_coverage_document",
]
