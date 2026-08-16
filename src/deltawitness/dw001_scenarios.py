"""Public DW-001 synthetic-fixture API with fail-closed safety checks.

The internal module defines deterministic descriptor, identity, and materializer
semantics. This public boundary rejects symbolic-link destinations and
independently binds the emitted specification digest to descriptor-derived
bytes before accepting an identity.
"""

from __future__ import annotations

import hashlib
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


def compute_fixture_specification_sha256(document: object) -> str:
    """Compute the exact specification digest derived from one descriptor."""

    valid, errors = verify_fixture_descriptor_document(document)
    if not valid:
        detail = errors[0] if errors else "descriptor verification failed"
        raise DW001ScenarioError(
            f"fixture descriptor specification: {detail}"
        )
    if not isinstance(document, dict):
        raise DW001ScenarioError(
            "fixture descriptor specification: descriptor must be an object"
        )
    return hashlib.sha256(_core._specification_bytes(document)).hexdigest()


def verify_fixture_identity_document(
    identity: object,
    descriptor: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify identity semantics plus descriptor-derived specification bytes."""

    valid, errors = _core.verify_fixture_identity_document(
        identity,
        descriptor,
    )
    if not valid:
        return valid, errors
    if not isinstance(identity, dict):
        return False, ("fixture identity must be an object",)
    specification = identity.get("specification")
    if not isinstance(specification, dict):
        return False, ("fixture identity.specification must be an object",)
    recorded = specification.get("sha256")
    try:
        expected = compute_fixture_specification_sha256(descriptor)
    except DW001ScenarioError as exc:
        return False, (str(exc),)
    if recorded != expected:
        return False, (
            "fixture identity.specification.sha256 does not match "
            "descriptor-derived specification bytes",
        )
    return True, ()


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

    identity = _core.materialize_synthetic_fixture(
        document,
        _destination(destination),
    )
    valid, errors = verify_fixture_identity_document(identity, document)
    if not valid:
        detail = errors[0] if errors else "identity verification failed"
        raise DW001ScenarioError(
            f"synthetic fixture identity: {detail}"
        )
    return identity


def verify_materialized_fixture(
    identity: object,
    descriptor: object,
    destination: Path,
) -> tuple[bool, tuple[str, ...]]:
    """Verify public identity semantics before repository identity checks."""

    try:
        normalized = _destination(destination)
    except DW001ScenarioError as exc:
        return False, (str(exc),)
    identity_valid, identity_errors = verify_fixture_identity_document(
        identity,
        descriptor,
    )
    if not identity_valid:
        return False, identity_errors
    return _core.verify_materialized_fixture(
        identity,
        descriptor,
        normalized,
    )


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
    "compute_fixture_specification_sha256",
    "materialize_synthetic_fixture",
    "verify_fixture_descriptor_document",
    "verify_fixture_identity_document",
    "verify_materialized_fixture",
]
