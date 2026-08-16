"""Canonical JSON archive for one verified DW-001 development pilot bundle.

The archive is a text-only transport and retention format over the already
verified directory bundle. It embeds every retained JSON object with its exact
relative path and a canonical document digest, then re-materializes the full
bundle through the ordinary bundle verifier before acceptance.

The archive adds no producer authentication, timestamp guarantee, containment,
confirmatory eligibility, ecological inference, or external upload channel.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path, PurePosixPath
import shutil
import tempfile
from typing import Any, Mapping

from ._dw001_pilot_execution import PILOT_ID, verify_bundle
from ._dw001_pilot_plan import verify_development_pilot_plan_document
from .dw001 import STUDY_ID
from .errors import DeltaWitnessError
from .reporting import load_report, sha256_document


ARCHIVE_SCHEMA_VERSION = "deltawitness.dw001-development-pilot-archive.v1"
FILE_SCHEMA_VERSION = "deltawitness.dw001-development-pilot-file.v1"

_ARCHIVE_FIELDS = {
    "schema_version",
    "study_id",
    "pilot_id",
    "partition",
    "plan_sha256",
    "index_semantic_sha256",
    "files",
    "archive_sha256",
}
_FILE_FIELDS = {
    "schema_version",
    "path",
    "document",
    "document_sha256",
}


class PilotArchiveError(DeltaWitnessError):
    """Raised when a pilot archive is malformed, unsafe, or inconsistent."""


def _error(context: str, message: str) -> PilotArchiveError:
    return PilotArchiveError(f"{context}: {message}")


def _object(value: object, *, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _error(context, "must be an object")
    return value


def _exact_keys(
    value: Mapping[str, object],
    expected: set[str],
    *,
    context: str,
) -> None:
    actual = set(value)
    if actual != expected:
        raise _error(
            context,
            f"field mismatch; missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}",
        )


def _safe_relative_path(value: object, *, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise _error(context, "must be a non-empty string")
    if value.startswith("/") or "\\" in value or "\x00" in value:
        raise _error(context, "must be a safe repository-relative POSIX path")
    parts = PurePosixPath(value).parts
    if not parts or any(part in {".", ".."} for part in parts):
        raise _error(context, "must be a safe repository-relative POSIX path")
    if PurePosixPath(value).suffix != ".json":
        raise _error(context, "must identify a JSON document")
    return value


def _write_document(path: Path, document: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        json.dumps(
            document,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
        ).encode("utf-8")
        + b"\n"
    )


def compute_archive_sha256(document: dict[str, Any]) -> str:
    """Hash an archive or file record with its own digest field normalized."""

    if not isinstance(document, dict):
        raise _error("development pilot archive digest", "document must be an object")
    normalized = deepcopy(document)
    if "archive_sha256" in normalized:
        normalized["archive_sha256"] = None
    elif "document_sha256" in normalized:
        normalized["document_sha256"] = None
    else:
        raise _error(
            "development pilot archive digest",
            "document has no recognized digest field",
        )
    return sha256_document(normalized)


def _file_record(path: str, document: dict[str, Any]) -> dict[str, Any]:
    record: dict[str, Any] = {
        "schema_version": FILE_SCHEMA_VERSION,
        "path": path,
        "document": document,
        "document_sha256": None,
    }
    record["document_sha256"] = compute_archive_sha256(record)
    return record


def build_archive(
    bundle_directory: Path,
    plan: object,
) -> dict[str, Any]:
    """Pack one independently verified directory bundle into canonical JSON."""

    valid, errors = verify_bundle(Path(bundle_directory), plan)
    if not valid:
        raise _error(
            "development pilot archive source bundle",
            "; ".join(errors),
        )
    if not isinstance(plan, dict):
        raise _error("development pilot archive plan", "must be an object")

    root = Path(bundle_directory)
    files: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.json"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        _safe_relative_path(
            relative,
            context="development pilot archive file path",
        )
        document = load_report(path)
        files.append(_file_record(relative, document))

    index_matches = [
        item["document"] for item in files if item["path"] == "index.json"
    ]
    if len(index_matches) != 1:
        raise _error(
            "development pilot archive index",
            "source bundle must contain exactly one index.json",
        )
    archive: dict[str, Any] = {
        "schema_version": ARCHIVE_SCHEMA_VERSION,
        "study_id": STUDY_ID,
        "pilot_id": PILOT_ID,
        "partition": "development",
        "plan_sha256": plan["plan_sha256"],
        "index_semantic_sha256": index_matches[0]["semantic_sha256"],
        "files": files,
        "archive_sha256": None,
    }
    archive["archive_sha256"] = compute_archive_sha256(archive)
    verified, verify_errors = verify_archive(archive, plan)
    if not verified:
        raise _error(
            "development pilot archive self-verification",
            "; ".join(verify_errors),
        )
    return archive


def _validate_structure(
    document: object,
    plan: Mapping[str, object],
) -> tuple[dict[str, Any], list[str]]:
    archive = _object(document, context="development pilot archive")
    _exact_keys(
        archive,
        _ARCHIVE_FIELDS,
        context="development pilot archive",
    )
    errors: list[str] = []
    for field, expected in (
        ("schema_version", ARCHIVE_SCHEMA_VERSION),
        ("study_id", STUDY_ID),
        ("pilot_id", PILOT_ID),
        ("partition", "development"),
        ("plan_sha256", plan["plan_sha256"]),
    ):
        if archive[field] != expected:
            errors.append(
                f"development pilot archive.{field}: does not match sealed plan"
            )
    if not isinstance(archive["index_semantic_sha256"], str):
        errors.append(
            "development pilot archive.index_semantic_sha256: must be a string"
        )

    files = archive["files"]
    if not isinstance(files, list) or not files:
        raise _error("development pilot archive.files", "must be a non-empty list")
    paths: list[str] = []
    for index, item in enumerate(files):
        context = f"development pilot archive.files[{index}]"
        record = _object(item, context=context)
        _exact_keys(record, _FILE_FIELDS, context=context)
        if record["schema_version"] != FILE_SCHEMA_VERSION:
            errors.append(f"{context}.schema_version: is unsupported")
        path = _safe_relative_path(record["path"], context=f"{context}.path")
        paths.append(path)
        if not isinstance(record["document"], dict):
            errors.append(f"{context}.document: must be an object")
        recorded_digest = record["document_sha256"]
        if not isinstance(recorded_digest, str):
            errors.append(f"{context}.document_sha256: must be a string")
        else:
            computed_digest = compute_archive_sha256(record)
            if recorded_digest != computed_digest:
                errors.append(
                    f"{context}.document_sha256: digest mismatch; "
                    f"expected {recorded_digest}, computed {computed_digest}"
                )
    if len(paths) != len(set(paths)):
        errors.append("development pilot archive.files.path: duplicate paths are forbidden")
    if paths != sorted(paths):
        errors.append("development pilot archive.files.path: paths must be sorted")
    for required in ("plan.json", "index.json"):
        if required not in paths:
            errors.append(
                f"development pilot archive.files: missing required {required}"
            )

    recorded_archive_digest = archive["archive_sha256"]
    if not isinstance(recorded_archive_digest, str):
        errors.append("development pilot archive.archive_sha256: must be a string")
    else:
        computed_archive_digest = compute_archive_sha256(archive)
        if recorded_archive_digest != computed_archive_digest:
            errors.append(
                "development pilot archive.archive_sha256: digest mismatch; "
                f"expected {recorded_archive_digest}, "
                f"computed {computed_archive_digest}"
            )
    return archive, errors


def _materialize_unchecked(
    archive: Mapping[str, object],
    destination: Path,
) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    files = archive["files"]
    assert isinstance(files, list)
    for item in files:
        assert isinstance(item, dict)
        relative = _safe_relative_path(
            item["path"],
            context="development pilot archive materialization path",
        )
        _write_document(destination / relative, item["document"])


def verify_archive(
    document: object,
    plan: object,
) -> tuple[bool, tuple[str, ...]]:
    plan_valid, plan_errors = verify_development_pilot_plan_document(plan)
    if not plan_valid:
        return False, tuple(
            f"development pilot archive plan: {error}" for error in plan_errors
        )
    if not isinstance(plan, dict):
        return False, ("development pilot archive plan must be an object",)
    try:
        archive, errors = _validate_structure(document, plan)
    except (
        PilotArchiveError,
        DeltaWitnessError,
        KeyError,
        TypeError,
        IndexError,
        ValueError,
        OverflowError,
    ) as exc:
        if isinstance(exc, PilotArchiveError):
            return False, (str(exc),)
        return False, (
            "development pilot archive: verification failed closed: "
            f"{type(exc).__name__}: {exc}",
        )
    if errors:
        return False, tuple(dict.fromkeys(errors))

    try:
        with tempfile.TemporaryDirectory(
            prefix="deltawitness-pilot-archive-verify-"
        ) as parent:
            restored = Path(parent) / "bundle"
            _materialize_unchecked(archive, restored)
            bundle_valid, bundle_errors = verify_bundle(restored, plan)
            if not bundle_valid:
                errors.extend(
                    "development pilot archive document/path relation: " + error
                    for error in bundle_errors
                )
            index = load_report(restored / "index.json")
            if index.get("semantic_sha256") != archive["index_semantic_sha256"]:
                errors.append(
                    "development pilot archive.index_semantic_sha256: "
                    "does not match embedded index document"
                )
    except (
        PilotArchiveError,
        DeltaWitnessError,
        OSError,
        KeyError,
        TypeError,
    ) as exc:
        errors.append(
            "development pilot archive document materialization: "
            f"{type(exc).__name__}: {exc}"
        )
    unique = tuple(dict.fromkeys(errors))
    return not unique, unique


def _prepare_destination(destination: Path) -> tuple[Path, bool]:
    output = Path(destination)
    if output.is_symlink():
        raise _error(
            "development pilot archive output directory",
            "symbolic-link destinations are not allowed",
        )
    existed = output.exists()
    if existed:
        if not output.is_dir() or any(output.iterdir()):
            raise _error(
                "development pilot archive output directory",
                "must be absent or an empty literal directory",
            )
    elif output.parent.is_symlink() or not output.parent.is_dir():
        raise _error(
            "development pilot archive output parent",
            "must be a trusted literal directory",
        )
    return output, existed


def materialize_archive(
    document: object,
    destination: Path,
    plan: object,
) -> None:
    """Materialize an already verified archive without partial final output."""

    valid, errors = verify_archive(document, plan)
    if not valid:
        raise _error(
            "development pilot archive verification",
            "; ".join(errors),
        )
    assert isinstance(document, dict)
    output, existed = _prepare_destination(Path(destination))
    staging = Path(
        tempfile.mkdtemp(
            prefix=".deltawitness-pilot-archive-staging-",
            dir=output.parent,
        )
    )
    try:
        for item in document["files"]:
            relative = _safe_relative_path(
                item["path"],
                context="development pilot archive materialization path",
            )
            _write_document(staging / relative, item["document"])
        bundle_valid, bundle_errors = verify_bundle(staging, plan)
        if not bundle_valid:
            raise _error(
                "development pilot archive materialized bundle",
                "; ".join(bundle_errors),
            )
        if existed:
            for child in sorted(staging.iterdir(), key=lambda item: item.name):
                child.replace(output / child.name)
            staging.rmdir()
        else:
            staging.replace(output)
    except BaseException:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        raise


__all__ = [
    "ARCHIVE_SCHEMA_VERSION",
    "FILE_SCHEMA_VERSION",
    "PilotArchiveError",
    "build_archive",
    "compute_archive_sha256",
    "materialize_archive",
    "verify_archive",
]
