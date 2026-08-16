"""DW-001 synthetic scenario generator contract (red-first placeholder)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .errors import DeltaWitnessError

FIXTURE_DESCRIPTOR_SCHEMA_VERSION = "deltawitness.dw001-fixture-descriptor.v1"
FIXTURE_IDENTITY_SCHEMA_VERSION = "deltawitness.dw001-fixture-identity.v1"
GENERATOR_ID = "deltawitness-synthetic-python"
GENERATOR_VERSION = "1"
SUPPORTED_FAMILIES = (
    "valid-discriminating-regression",
    "non-discriminating-candidate-test",
    "candidate-regression-against-base-tests",
)


class DW001ScenarioError(DeltaWitnessError):
    """Raised when a DW-001 synthetic fixture cannot be constructed safely."""


def _missing() -> DW001ScenarioError:
    return DW001ScenarioError("DW-001 deterministic scenario generator is not implemented")


def build_fixture_descriptor(
    *,
    scenario_id: str,
    family_id: str,
    observer: str = "outcome-receipt-v1",
) -> dict[str, Any]:
    raise _missing()


def compute_fixture_descriptor_sha256(document: dict[str, Any]) -> str:
    raise _missing()


def verify_fixture_descriptor_document(document: object) -> tuple[bool, tuple[str, ...]]:
    raise _missing()


def materialize_synthetic_fixture(
    document: object,
    destination: Path,
) -> dict[str, Any]:
    raise _missing()


def compute_fixture_identity_sha256(document: dict[str, Any]) -> str:
    raise _missing()


def verify_fixture_identity_document(
    identity: object,
    descriptor: object,
) -> tuple[bool, tuple[str, ...]]:
    raise _missing()


def verify_materialized_fixture(
    identity: object,
    descriptor: object,
    destination: Path,
) -> tuple[bool, tuple[str, ...]]:
    raise _missing()
