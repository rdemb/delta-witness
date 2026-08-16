"""Public DW-001 synthetic-fixture API with fail-closed safety checks.

The original deterministic generator core remains responsible for the first
three owned-synthetic families. Fixed adapters add controlled observer,
oracle-relevance, and oracle-strength probes without accepting free-form source
or test bytes. This public boundary dispatches by verified family identifier,
rejects symbolic-link destinations, and binds specification digests to
descriptor-derived bytes.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from . import _dw001_scenarios as _core
from . import _dw001_weak_proxy as _weak_proxy
from . import _dw001_wrong_reason as _wrong_reason

DW001ScenarioError = _core.DW001ScenarioError
FIXTURE_DESCRIPTOR_SCHEMA_VERSION = _core.FIXTURE_DESCRIPTOR_SCHEMA_VERSION
FIXTURE_IDENTITY_SCHEMA_VERSION = _core.FIXTURE_IDENTITY_SCHEMA_VERSION
GENERATOR_ID = _core.GENERATOR_ID
GENERATOR_VERSION = _core.GENERATOR_VERSION
SUPPORTED_FAMILIES = (
    *_core.SUPPORTED_FAMILIES,
    *_wrong_reason.SUPPORTED_FAMILIES,
    _weak_proxy.FAMILY_ID,
)
compute_fixture_descriptor_sha256 = _core.compute_fixture_descriptor_sha256
compute_fixture_identity_sha256 = _core.compute_fixture_identity_sha256


def _family(document: object) -> object:
    return document.get("family_id") if isinstance(document, dict) else None


def _adapter(document: object):
    family = _family(document)
    if family in _wrong_reason.SUPPORTED_FAMILIES:
        return _wrong_reason
    if family == _weak_proxy.FAMILY_ID:
        return _weak_proxy
    return None


def build_fixture_descriptor(
    *,
    scenario_id: str,
    family_id: str,
    observer: str = "outcome-receipt-v1",
) -> dict[str, Any]:
    """Build one canonical descriptor for a supported fixed family."""

    if family_id in _wrong_reason.SUPPORTED_FAMILIES:
        return _wrong_reason.build_descriptor(
            scenario_id=scenario_id,
            family_id=family_id,
            observer=observer,
        )
    if family_id == _weak_proxy.FAMILY_ID:
        return _weak_proxy.build_descriptor(
            scenario_id=scenario_id,
            observer=observer,
        )
    return _core.build_fixture_descriptor(
        scenario_id=scenario_id,
        family_id=family_id,
        observer=observer,
    )


def verify_fixture_descriptor_document(
    document: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify a descriptor using the exact family implementation."""

    adapter = _adapter(document)
    if adapter is not None:
        return adapter.verify_descriptor(document)
    return _core.verify_fixture_descriptor_document(document)


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

    adapter = _adapter(descriptor)
    if adapter is not None:
        return adapter.verify_identity(identity, descriptor)

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
    """Materialize a verified fixed family into a literal destination."""

    normalized_destination = _destination(destination)
    adapter = _adapter(document)
    if adapter is not None:
        identity = adapter.materialize(document, normalized_destination)
    else:
        identity = _core.materialize_synthetic_fixture(
            document,
            normalized_destination,
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
    adapter = _adapter(descriptor)
    if adapter is not None:
        return adapter.verify_materialized(
            identity,
            descriptor,
            normalized,
        )
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
