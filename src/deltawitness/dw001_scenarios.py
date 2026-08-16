"""Public DW-001 synthetic-fixture API with fail-closed destination checks.

The internal module defines deterministic descriptor, identity, and materializer
semantics. This public boundary rejects a symbolic-link destination before any
Git or file operation can follow it.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import _dw001_scenarios as _core

DW001ScenarioError = _core.DW001ScenarioError
FIXTURE_DESCRIPTOR_SCHEMA_VERSION = _core.FIXTURE_DESCRIPTOR_SCHEMA_VERSION
FIXTURE_IDENTITY_SCHEMA_VERSION = _core.FIXTURE_IDENTITY_SCHEMA_VERSION
GENERATOR_ID = _core.GENERATOR_ID
GENERATOR_VERSION = _core.GENERATOR_VERSION
SUPPORTED_FAMILIES = _core.SUPPORTED_FAMILIES
build_fixture_descriptor = _core.build_fixture_descriptor
compute_fixture_descriptor_sha256 = _core.compute_fixture_descriptor_sha256
compute_fixture_identity_sha256 = _core.compute_fixture_identity_sha256
verify_fixture_descriptor_document = _core.verify_fixture_descriptor_document
verify_fixture_identity_document = _core.verify_fixture_identity_document


def _destination(path: Path) -> Path:
    destination = Path(path)
    if destination.is_symlink():
        raise DW001ScenarioError(
            "synthetic fixture destination: symbolic link destinations are not allowed"
        )
    return destination


def materialize_synthetic_fixture(
    document: object,
    destination: Path,
) -> dict[str, Any]:
    """Materialize only into a literal non-symlink destination path."""

    return _core.materialize_synthetic_fixture(document, _destination(destination))


def verify_materialized_fixture(
    identity: object,
    descriptor: object,
    destination: Path,
) -> tuple[bool, tuple[str, ...]]:
    """Reject symlink destinations before checking repository identities."""

    try:
        normalized = _destination(destination)
    except DW001ScenarioError as exc:
        return False, (str(exc),)
    return _core.verify_materialized_fixture(identity, descriptor, normalized)


__all__ = [
    "DW001ScenarioError",
    "FIXTURE_DESCRIPTOR_SCHEMA_VERSION",
    "FIXTURE_IDENTITY_SCHEMA_VERSION",
    "GENERATOR_ID",
    "GENERATOR_VERSION",
    "SUPPORTED_FAMILIES",
    "build_fixture_descriptor",
    "compute_fixture_descriptor_sha256",
    "compute_fixture_identity_sha256",
    "materialize_synthetic_fixture",
    "verify_fixture_descriptor_document",
    "verify_fixture_identity_document",
    "verify_materialized_fixture",
]
