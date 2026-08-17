"""Public contract scaffold for the DW-001 Coverage.py direct baseline.

The dependency and artifact boundary is implemented first. The execution and
verification path remains deliberately unavailable until the red-first
research contract has been retained in CI.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from .errors import DeltaWitnessError
from .reporting import load_report, sha256_document


RESULT_SCHEMA_VERSION = "deltawitness.dw001-coveragepy-baseline-result.v1"
RESULT_ID = "DW-001-COVERAGEPY-BASELINE-RESULT-V1"
ADAPTER_ID = "coveragepy-public-api-v1"
MUTATION_RESULT_SEMANTIC_SHA256 = (
    "9e101bca85fd630bf5bdb2a6030d9fdab93eb3eac54b03f4aab99012c28086b6"
)
STDLIB_STATEMENT_RESULT_SEMANTIC_SHA256 = (
    "353e887ccb43561f1a0749e7948dd40bd7019534e93b5dca5b11ea16d49f68c6"
)


class DW001CoveragePyBaselineError(DeltaWitnessError):
    """Raised when the fixed Coverage.py baseline contract cannot be met."""


def _semantic_view(document: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(document)
    normalized["created_at"] = None
    normalized["runtime"] = None
    normalized["semantic_sha256"] = None
    normalized["report_sha256"] = None
    return normalized


def compute_coveragepy_baseline_semantic_sha256(
    document: dict[str, Any],
) -> str:
    """Hash stable baseline semantics."""

    if not isinstance(document, dict):
        raise DW001CoveragePyBaselineError(
            "Coverage.py baseline result must be an object"
        )
    return sha256_document(_semantic_view(document))


def compute_coveragepy_baseline_report_sha256(
    document: dict[str, Any],
) -> str:
    """Hash the complete result with only its report digest normalized."""

    if not isinstance(document, dict):
        raise DW001CoveragePyBaselineError(
            "Coverage.py baseline result must be an object"
        )
    normalized = deepcopy(document)
    normalized["report_sha256"] = None
    return sha256_document(normalized)


def run_claim_scoped_coveragepy_baseline(
    plan: object,
    catalog: object,
    mutation_result: object,
    stdlib_statement_result: object,
) -> dict[str, Any]:
    """Execute the fixed direct baseline after the red contract is retained."""

    raise DW001CoveragePyBaselineError(
        "Coverage.py baseline implementation is intentionally not implemented"
    )


def verify_claim_scoped_coveragepy_baseline_document(
    document: object,
    plan: object,
    catalog: object,
    mutation_result: object,
    stdlib_statement_result: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify one result after the red contract is retained."""

    return False, ("Coverage.py baseline implementation is not implemented",)


def load_claim_scoped_coveragepy_baseline(
    path: Path,
    plan: object,
    catalog: object,
    mutation_result: object,
    stdlib_statement_result: object,
) -> dict[str, Any]:
    """Strict-load and verify one result document."""

    document = load_report(path)
    valid, errors = verify_claim_scoped_coveragepy_baseline_document(
        document,
        plan,
        catalog,
        mutation_result,
        stdlib_statement_result,
    )
    if not valid:
        raise DW001CoveragePyBaselineError("; ".join(errors))
    return document


__all__ = [
    "ADAPTER_ID",
    "DW001CoveragePyBaselineError",
    "MUTATION_RESULT_SEMANTIC_SHA256",
    "RESULT_ID",
    "RESULT_SCHEMA_VERSION",
    "STDLIB_STATEMENT_RESULT_SEMANTIC_SHA256",
    "compute_coveragepy_baseline_report_sha256",
    "compute_coveragepy_baseline_semantic_sha256",
    "load_claim_scoped_coveragepy_baseline",
    "run_claim_scoped_coveragepy_baseline",
    "verify_claim_scoped_coveragepy_baseline_document",
]
