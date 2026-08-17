"""Exact research-only Coverage.py distribution and artifact contract.

This module has no Coverage.py import and remains usable in the dependency-free
base package. It records the only third-party distribution authorized for the
DW-001 direct baseline and verifies a downloaded artifact before offline
installation.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
from pathlib import Path
import stat
from typing import Any

from .errors import DeltaWitnessError
from .reporting import sha256_document


COVERAGEPY_PACKAGE = "coverage"
COVERAGEPY_VERSION = "7.15.2"
COVERAGEPY_WHEEL_FILENAME = "coverage-7.15.2-py3-none-any.whl"
COVERAGEPY_WHEEL_SHA256 = (
    "eb6bcae8d1a9d305351ecb108232441d11c5cfe9de840a04388ba5d2db8d735c"
)
COVERAGEPY_SDIST_FILENAME = "coverage-7.15.2.tar.gz"
COVERAGEPY_SDIST_SHA256 = (
    "3df60dc267f0a2ca23cb7a9ab1109c62b9335ffbf519fcfe167157c28c09b81d"
)
COVERAGEPY_SOURCE_COMMIT = "50d865908dfeb21a0bf1e6f05db578c11662f8dd"
COVERAGEPY_TAG_OBJECT = "65b67b52df5f060eac5ce1206f2bafc885114da6"
COVERAGEPY_MANIFEST_SHA256 = (
    "28f6430e45fcfda973a1fcd57157e2317f096cc2774e8281244eaf18a9d0dd3f"
)
COVERAGEPY_MANIFEST_SCHEMA = (
    "deltawitness.coveragepy-distribution-artifact.v1"
)
_MAX_ARTIFACT_BYTES = 5_000_000


class CoveragePyContractError(DeltaWitnessError):
    """Raised when the exact optional dependency contract is violated."""


def _strict_equal(expected: object, actual: object) -> bool:
    if type(expected) is not type(actual):
        return False
    if isinstance(expected, dict):
        assert isinstance(actual, dict)
        # JSON object member order is non-semantic. Lists below remain exact
        # and order-sensitive because profile, interpreter, and evidence order
        # is part of the reviewed contract.
        return set(expected) == set(actual) and all(
            _strict_equal(expected[key], actual[key]) for key in expected
        )
    if isinstance(expected, list):
        assert isinstance(actual, list)
        return len(expected) == len(actual) and all(
            _strict_equal(left, right)
            for left, right in zip(expected, actual, strict=True)
        )
    return expected == actual


def _first_difference(
    expected: object,
    actual: object,
    *,
    path: str = "coveragepy manifest",
) -> str:
    if type(expected) is not type(actual):
        return (
            f"{path}: type mismatch; expected {type(expected).__name__}, "
            f"observed {type(actual).__name__}"
        )
    if isinstance(expected, dict):
        assert isinstance(actual, dict)
        expected_keys = set(expected)
        actual_keys = set(actual)
        if expected_keys != actual_keys:
            return (
                f"{path}: key membership mismatch; "
                f"missing={sorted(expected_keys - actual_keys)!r}, "
                f"extra={sorted(actual_keys - expected_keys)!r}"
            )
        for key in sorted(expected_keys):
            if not _strict_equal(expected[key], actual[key]):
                return _first_difference(
                    expected[key],
                    actual[key],
                    path=f"{path}.{key}",
                )
        return f"{path}: mismatch"
    if isinstance(expected, list):
        assert isinstance(actual, list)
        if len(expected) != len(actual):
            return (
                f"{path}: length mismatch; expected {len(expected)}, "
                f"observed {len(actual)}"
            )
        for index, (left, right) in enumerate(
            zip(expected, actual, strict=True)
        ):
            if not _strict_equal(left, right):
                return _first_difference(
                    left,
                    right,
                    path=f"{path}[{index}]",
                )
        return f"{path}: mismatch"
    return f"{path}: expected {expected!r}, observed {actual!r}"


def build_coveragepy_distribution_manifest() -> dict[str, Any]:
    """Return the exact reviewed research-only distribution manifest."""

    manifest: dict[str, Any] = {
        "schema_version": COVERAGEPY_MANIFEST_SCHEMA,
        "decision": "GO",
        "package": COVERAGEPY_PACKAGE,
        "version": COVERAGEPY_VERSION,
        "dependency_scope": "research-extra-only",
        "selected_artifact": {
            "filename": COVERAGEPY_WHEEL_FILENAME,
            "format": "wheel",
            "python_tag": "py3",
            "abi_tag": "none",
            "platform_tag": "any",
            "sha256": COVERAGEPY_WHEEL_SHA256,
            "trusted_publishing": True,
            "sigstore_transparency_entry": 2174723144,
        },
        "candidate_sdist": {
            "filename": COVERAGEPY_SDIST_FILENAME,
            "format": "sdist",
            "sha256": COVERAGEPY_SDIST_SHA256,
            "trusted_publishing": True,
            "sigstore_transparency_entry": 2174713616,
            "selected": False,
        },
        "source": {
            "repository": "coveragepy/coveragepy",
            "commit": COVERAGEPY_SOURCE_COMMIT,
            "tag": COVERAGEPY_VERSION,
            "tag_object": COVERAGEPY_TAG_OBJECT,
            "publication_workflow": ".github/workflows/publish.yml",
            "license": "Apache-2.0",
            "license_file": "LICENSE.txt",
        },
        "runtime_contract": {
            "minimum_python": "3.10",
            "supported_delta_witness_pythons": [
                "3.11",
                "3.12",
                "3.13",
                "3.14",
            ],
            "base_runtime_dependency": False,
            "measurement_network_allowed": False,
            "persistent_data_file_allowed": False,
            "ambient_config_allowed": False,
            "plugins_allowed": False,
            "auto_start_allowed": False,
            "subprocess_measurement_allowed": False,
            "concurrency_modes": [],
            "public_api_only": True,
            "selected_tracer": "timid-python",
        },
        "manifest_sha256": None,
    }
    manifest["manifest_sha256"] = compute_coveragepy_manifest_sha256(
        manifest
    )
    return manifest


def compute_coveragepy_manifest_sha256(document: dict[str, Any]) -> str:
    """Hash the complete manifest with its own digest normalized."""

    if not isinstance(document, dict):
        raise CoveragePyContractError("Coverage.py manifest must be an object")
    normalized = deepcopy(document)
    normalized["manifest_sha256"] = None
    return sha256_document(normalized)


def verify_coveragepy_distribution_manifest_document(
    document: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify exact package, artifact, upstream, policy, and digest identity."""

    if not isinstance(document, dict):
        return False, ("coveragepy manifest: must be an object",)
    expected = build_coveragepy_distribution_manifest()
    errors: list[str] = []
    if not _strict_equal(expected, document):
        errors.append(_first_difference(expected, document))
    try:
        computed = compute_coveragepy_manifest_sha256(document)
    except CoveragePyContractError as exc:
        errors.append(str(exc))
    else:
        if document.get("manifest_sha256") != computed:
            errors.append(
                "coveragepy manifest.manifest_sha256: digest mismatch"
            )
        if computed != COVERAGEPY_MANIFEST_SHA256:
            errors.append(
                "coveragepy manifest.manifest_sha256: does not match the "
                "reviewed manifest"
            )
    return not errors, tuple(dict.fromkeys(errors))


def verify_coveragepy_artifact(path: Path) -> str:
    """Verify the selected universal wheel before offline installation."""

    try:
        metadata = path.lstat()
    except OSError as exc:
        raise CoveragePyContractError(
            "Coverage.py artifact cannot be inspected"
        ) from exc
    if path.is_symlink() or not stat.S_ISREG(metadata.st_mode):
        raise CoveragePyContractError(
            "Coverage.py artifact must be a regular non-link file"
        )
    if path.name != COVERAGEPY_WHEEL_FILENAME:
        raise CoveragePyContractError(
            "Coverage.py artifact filename does not match the reviewed wheel"
        )
    if metadata.st_size <= 0 or metadata.st_size > _MAX_ARTIFACT_BYTES:
        raise CoveragePyContractError(
            "Coverage.py artifact size is outside the reviewed safety bound"
        )

    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            while True:
                chunk = handle.read(65_536)
                if not chunk:
                    break
                digest.update(chunk)
    except OSError as exc:
        raise CoveragePyContractError(
            "Coverage.py artifact cannot be read"
        ) from exc
    observed = digest.hexdigest()
    if observed != COVERAGEPY_WHEEL_SHA256:
        raise CoveragePyContractError(
            "Coverage.py artifact SHA-256 does not match the reviewed wheel"
        )
    return observed


__all__ = [
    "COVERAGEPY_MANIFEST_SCHEMA",
    "COVERAGEPY_MANIFEST_SHA256",
    "COVERAGEPY_PACKAGE",
    "COVERAGEPY_SDIST_FILENAME",
    "COVERAGEPY_SDIST_SHA256",
    "COVERAGEPY_SOURCE_COMMIT",
    "COVERAGEPY_TAG_OBJECT",
    "COVERAGEPY_VERSION",
    "COVERAGEPY_WHEEL_FILENAME",
    "COVERAGEPY_WHEEL_SHA256",
    "CoveragePyContractError",
    "build_coveragepy_distribution_manifest",
    "compute_coveragepy_manifest_sha256",
    "verify_coveragepy_artifact",
    "verify_coveragepy_distribution_manifest_document",
]
