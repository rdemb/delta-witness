"""Placeholder API for the DW-001 development mechanism pilot.

The red-first tests define the sealed ten-arm plan, derivation, verification,
execution-bundle, analysis, and cost semantics. No pilot execution capability
is implemented in this commit.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .errors import DeltaWitnessError


PLAN_SCHEMA_VERSION = "deltawitness.dw001-development-pilot-plan.v1"
INDEX_SCHEMA_VERSION = "deltawitness.dw001-development-pilot-index.v1"
PILOT_ID = "DW-001-DEV-PILOT-V1"


class DW001PilotError(DeltaWitnessError):
    """Raised when a development-pilot plan or bundle is unsafe or invalid."""


def _unimplemented() -> DW001PilotError:
    return DW001PilotError("DW-001 development pilot is not implemented")


def compute_development_pilot_plan_sha256(document: dict[str, Any]) -> str:
    raise _unimplemented()


def build_development_pilot_plan(
    *,
    protocol_commit_sha: str,
    implementation_commit_sha: str,
) -> dict[str, Any]:
    raise _unimplemented()


def verify_development_pilot_plan_document(
    document: object,
) -> tuple[bool, tuple[str, ...]]:
    raise _unimplemented()


def compute_development_pilot_index_sha256(document: dict[str, Any]) -> str:
    raise _unimplemented()


def run_development_pilot(
    plan: object,
    output_directory: Path,
) -> dict[str, Any]:
    raise _unimplemented()


def verify_development_pilot_index_document(
    document: object,
    plan: object,
) -> tuple[bool, tuple[str, ...]]:
    raise _unimplemented()


__all__ = [
    "INDEX_SCHEMA_VERSION",
    "PILOT_ID",
    "PLAN_SCHEMA_VERSION",
    "DW001PilotError",
    "build_development_pilot_plan",
    "compute_development_pilot_index_sha256",
    "compute_development_pilot_plan_sha256",
    "run_development_pilot",
    "verify_development_pilot_index_document",
    "verify_development_pilot_plan_document",
]
