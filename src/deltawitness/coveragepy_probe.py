"""Public contract scaffold for the fixed Coverage.py measurement child."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from .errors import DeltaWitnessError
from .reporting import load_report, sha256_document


COVERAGE_RECEIPT_SCHEMA_VERSION = (
    "deltawitness.coveragepy-measurement-receipt.v1"
)
COVERAGE_PRODUCER_NAME = "deltawitness-coveragepy"
COVERAGE_OUTPUT_BASENAME = ".deltawitness-coveragepy.json"


class CoveragePyProbeError(DeltaWitnessError):
    """Raised when the exact Coverage.py measurement receipt is invalid."""


def compute_coverage_receipt_sha256(document: dict[str, Any]) -> str:
    if not isinstance(document, dict):
        raise CoveragePyProbeError("Coverage.py receipt must be an object")
    normalized = deepcopy(document)
    normalized["coverage_sha256"] = None
    return sha256_document(normalized)


def build_coverage_receipt(**kwargs: object) -> dict[str, Any]:
    raise CoveragePyProbeError(
        "Coverage.py receipt implementation is intentionally not implemented"
    )


def validate_coverage_receipt(
    document: object,
    **expected: object,
) -> dict[str, Any]:
    raise CoveragePyProbeError(
        "Coverage.py receipt implementation is intentionally not implemented"
    )


def load_coverage_receipt(
    path: Path,
    **expected: object,
) -> dict[str, Any]:
    document = load_report(path)
    return validate_coverage_receipt(document, **expected)


def main(argv: list[str] | None = None) -> int:
    return 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "COVERAGE_OUTPUT_BASENAME",
    "COVERAGE_PRODUCER_NAME",
    "COVERAGE_RECEIPT_SCHEMA_VERSION",
    "CoveragePyProbeError",
    "build_coverage_receipt",
    "compute_coverage_receipt_sha256",
    "load_coverage_receipt",
    "validate_coverage_receipt",
]
