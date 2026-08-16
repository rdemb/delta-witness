"""Placeholder for the DW-001 fixture-to-manifest binding contract.

The red-first tests define the intended public API and relation semantics. The
implementation is intentionally absent in this commit.
"""

from __future__ import annotations

from typing import Any

from .errors import DeltaWitnessError


BINDING_SCHEMA_VERSION = "deltawitness.dw001-fixture-manifest-binding.v1"


class DW001FixtureBindingError(DeltaWitnessError):
    """Raised when fixture and manifest evidence cannot be bound safely."""


def _unimplemented() -> DW001FixtureBindingError:
    return DW001FixtureBindingError(
        "DW-001 fixture-manifest binding is not implemented"
    )


def compute_fixture_manifest_binding_sha256(document: dict[str, Any]) -> str:
    raise _unimplemented()


def build_fixture_manifest_binding(
    descriptor: object,
    identity: object,
    manifest: object,
) -> dict[str, Any]:
    raise _unimplemented()


def verify_fixture_manifest_binding_document(
    binding: object,
    descriptor: object,
    identity: object,
    manifest: object,
) -> tuple[bool, tuple[str, ...]]:
    raise _unimplemented()


__all__ = [
    "BINDING_SCHEMA_VERSION",
    "DW001FixtureBindingError",
    "build_fixture_manifest_binding",
    "compute_fixture_manifest_binding_sha256",
    "verify_fixture_manifest_binding_document",
]
