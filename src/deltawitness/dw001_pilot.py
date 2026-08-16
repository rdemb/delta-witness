"""Public DW-001 development mechanism-pilot API.

The plan contract is deterministic and development-only. The runner stages and
self-verifies the exact ten-arm bundle before publication. A canonical text
archive can retain every verified JSON artifact without adding an external
upload mechanism. None of these contracts authorizes a holdout, creates a
confirmatory denominator, authenticates producers, or provides containment.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ._dw001_pilot_archive import (
    ARCHIVE_SCHEMA_VERSION,
    build_archive,
    compute_archive_sha256,
    materialize_archive,
    verify_archive,
)
from ._dw001_pilot_execution import (
    INDEX_SCHEMA_VERSION,
    compute_index_sha256,
    run_pilot,
    verify_bundle,
    verify_index,
)
from ._dw001_pilot_plan import (
    DW001PilotError,
    PILOT_ID,
    PLAN_SCHEMA_VERSION,
    build_development_pilot_plan,
    compute_development_pilot_plan_sha256,
    verify_development_pilot_plan_document,
)


def compute_development_pilot_index_sha256(document: dict[str, Any]) -> str:
    """Compute the complete index digest with its own field normalized."""

    return compute_index_sha256(document)


def compute_development_pilot_archive_sha256(document: dict[str, Any]) -> str:
    """Compute an archive or embedded-file digest with its own field normalized."""

    return compute_archive_sha256(document)


def run_development_pilot(
    plan: object,
    output_directory: Path,
) -> dict[str, Any]:
    """Execute only the exact verified development plan into a safe bundle."""

    return run_pilot(plan, output_directory)


def verify_development_pilot_index_document(
    document: object,
    plan: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify index structure, plan relation, controlled contrasts, and digests."""

    return verify_index(document, plan)


def verify_development_pilot_bundle(
    output_directory: Path,
    plan: object,
) -> tuple[bool, tuple[str, ...]]:
    """Strict-decode and independently verify every retained pilot artifact."""

    return verify_bundle(output_directory, plan)


def build_development_pilot_archive(
    output_directory: Path,
    plan: object,
) -> dict[str, Any]:
    """Pack one verified directory bundle into a canonical JSON archive."""

    return build_archive(output_directory, plan)


def verify_development_pilot_archive_document(
    document: object,
    plan: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify every embedded document by reconstructing the directory bundle."""

    return verify_archive(document, plan)


def materialize_development_pilot_archive(
    document: object,
    output_directory: Path,
    plan: object,
) -> None:
    """Reconstruct a verified archive without leaving partial final output."""

    materialize_archive(document, output_directory, plan)


__all__ = [
    "ARCHIVE_SCHEMA_VERSION",
    "INDEX_SCHEMA_VERSION",
    "PILOT_ID",
    "PLAN_SCHEMA_VERSION",
    "DW001PilotError",
    "build_development_pilot_archive",
    "build_development_pilot_plan",
    "compute_development_pilot_archive_sha256",
    "compute_development_pilot_index_sha256",
    "compute_development_pilot_plan_sha256",
    "materialize_development_pilot_archive",
    "run_development_pilot",
    "verify_development_pilot_archive_document",
    "verify_development_pilot_bundle",
    "verify_development_pilot_index_document",
    "verify_development_pilot_plan_document",
]
