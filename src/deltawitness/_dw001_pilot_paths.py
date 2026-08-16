"""Exact file-set boundary for DW-001 development pilot bundles.

A valid evidence directory or archive contains only the files derived from the
sealed ten-arm plan. Required artifacts are not merely a lower bound: extra
JSON, text, symbolic-link, directory, or special entries are rejected so that
publication review covers the complete retained object.
"""

from __future__ import annotations

import os
from pathlib import Path, PurePosixPath
from typing import Mapping

from .errors import DeltaWitnessError


class PilotPathError(DeltaWitnessError):
    """Raised when a pilot bundle or archive has an unsafe file set."""


def _error(context: str, message: str) -> PilotPathError:
    return PilotPathError(f"{context}: {message}")


def _safe_component(value: object, *, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise _error(context, "must be a non-empty string")
    if value.startswith("/") or "\\" in value or "\x00" in value:
        raise _error(context, "must be a safe POSIX path component")
    parts = PurePosixPath(value).parts
    if len(parts) != 1 or parts[0] in {".", ".."}:
        raise _error(context, "must be a single safe POSIX path component")
    return value


def _safe_relative_path(value: object, *, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise _error(context, "must be a non-empty string")
    if value.startswith("/") or "\\" in value or "\x00" in value:
        raise _error(context, "must be a safe repository-relative POSIX path")
    parts = PurePosixPath(value).parts
    if not parts or any(part in {".", ".."} for part in parts):
        raise _error(context, "must be a safe repository-relative POSIX path")
    return value


def expected_bundle_file_paths(plan: object) -> tuple[str, ...]:
    """Derive the exact retained file set from one sealed-plan-shaped object."""

    if not isinstance(plan, dict):
        raise _error("development pilot exact file set plan", "must be an object")
    case_arms = plan.get("case_arms")
    if not isinstance(case_arms, list) or not case_arms:
        raise _error(
            "development pilot exact file set plan.case_arms",
            "must be a non-empty list",
        )

    paths = {"plan.json", "index.json"}
    case_ids: set[str] = set()
    for index, case in enumerate(case_arms):
        context = f"development pilot exact file set plan.case_arms[{index}]"
        if not isinstance(case, Mapping):
            raise _error(context, "must be an object")
        case_id = _safe_component(case.get("case_id"), context=f"{context}.case_id")
        if case_id in case_ids:
            raise _error(f"{context}.case_id", "must be unique")
        case_ids.add(case_id)
        localization = case.get("localization")
        if not isinstance(localization, Mapping):
            raise _error(f"{context}.localization", "must be an object")
        required = localization.get("required")
        if not isinstance(required, bool):
            raise _error(f"{context}.localization.required", "must be a boolean")

        prefix = f"cases/{case_id}"
        paths.update(
            {
                f"{prefix}/descriptor.json",
                f"{prefix}/identity.json",
                f"{prefix}/manifest.json",
                f"{prefix}/binding.json",
                f"{prefix}/matrix-report.json",
                f"{prefix}/projection.json",
                f"{prefix}/result.json",
            }
        )
        if required:
            paths.add(f"{prefix}/claim-witness-declaration.json")
            paths.add(f"{prefix}/claim-witness-localization.json")
    return tuple(sorted(paths))


def expected_bundle_directory_paths(plan: object) -> tuple[str, ...]:
    """Derive the exact non-root directory set for one evidence bundle."""

    files = expected_bundle_file_paths(plan)
    directories: set[str] = set()
    for file_path in files:
        parent = PurePosixPath(file_path).parent
        while parent != PurePosixPath("."):
            directories.add(parent.as_posix())
            parent = parent.parent
    return tuple(sorted(directories))


_ARTIFACT_LABELS = {
    "plan.json": "plan",
    "index.json": "index",
    "descriptor.json": "descriptor",
    "identity.json": "identity",
    "manifest.json": "manifest",
    "binding.json": "binding",
    "matrix-report.json": "matrix_report",
    "projection.json": "projection",
    "claim-witness-declaration.json": "declaration",
    "claim-witness-localization.json": "localization",
    "result.json": "result",
}


def _artifact_labels(paths: list[str]) -> list[str]:
    return sorted(
        {
            _ARTIFACT_LABELS.get(PurePosixPath(path).name, "unknown")
            for path in paths
        }
    )


def _compare_paths(
    *,
    expected: set[str],
    observed: set[str],
    context: str,
) -> list[str]:
    errors: list[str] = []
    missing = sorted(expected - observed)
    unexpected = sorted(observed - expected)
    if missing:
        errors.append(
            f"{context}: missing paths={missing}; "
            f"missing artifacts={_artifact_labels(missing)}"
        )
    if unexpected:
        errors.append(f"{context}: unexpected paths={unexpected}")
    return errors


def verify_exact_bundle_tree(
    root: Path,
    plan: object,
) -> tuple[bool, tuple[str, ...]]:
    """Require the complete directory tree to equal the sealed expected set."""

    bundle = Path(root)
    try:
        expected_files = set(expected_bundle_file_paths(plan))
        expected_directories = set(expected_bundle_directory_paths(plan))
        if bundle.is_symlink() or not bundle.is_dir():
            raise _error(
                "development pilot bundle exact file set",
                "root must be a literal directory",
            )

        observed_files: set[str] = set()
        observed_directories: set[str] = set()
        unsafe_entries: list[str] = []
        for current, directory_names, file_names in os.walk(
            bundle,
            topdown=True,
            followlinks=False,
        ):
            current_path = Path(current)
            retained_directories: list[str] = []
            for name in sorted(directory_names):
                path = current_path / name
                relative = path.relative_to(bundle).as_posix()
                if path.is_symlink():
                    unsafe_entries.append(relative)
                    continue
                retained_directories.append(name)
                observed_directories.add(relative)
            directory_names[:] = retained_directories

            for name in sorted(file_names):
                path = current_path / name
                relative = path.relative_to(bundle).as_posix()
                if path.is_symlink() or not path.is_file():
                    unsafe_entries.append(relative)
                    continue
                observed_files.add(relative)

        errors = _compare_paths(
            expected=expected_files,
            observed=observed_files,
            context="development pilot bundle files",
        )
        errors.extend(
            _compare_paths(
                expected=expected_directories,
                observed=observed_directories,
                context="development pilot bundle directories",
            )
        )
        if unsafe_entries:
            errors.append(
                "development pilot bundle exact file set: unsafe entries="
                f"{sorted(unsafe_entries)}"
            )
    except (PilotPathError, OSError, ValueError, TypeError, KeyError) as exc:
        if isinstance(exc, PilotPathError):
            return False, (str(exc),)
        return False, (
            "development pilot bundle exact file set: verification failed "
            f"closed: {type(exc).__name__}: {exc}",
        )
    unique = tuple(dict.fromkeys(errors))
    return not unique, unique


def verify_exact_archive_paths(
    document: object,
    plan: object,
) -> tuple[bool, tuple[str, ...]]:
    """Require an archive record list to equal the sealed expected file set."""

    try:
        expected = set(expected_bundle_file_paths(plan))
        if not isinstance(document, dict):
            raise _error("development pilot archive exact file set", "must be an object")
        files = document.get("files")
        if not isinstance(files, list):
            raise _error(
                "development pilot archive exact file set.files",
                "must be a list",
            )
        observed: list[str] = []
        for index, item in enumerate(files):
            context = f"development pilot archive exact file set.files[{index}]"
            if not isinstance(item, Mapping):
                raise _error(context, "must be an object")
            path = _safe_relative_path(item.get("path"), context=f"{context}.path")
            observed.append(path)

        errors: list[str] = []
        if len(observed) != len(set(observed)):
            duplicates = sorted(
                {path for path in observed if observed.count(path) > 1}
            )
            errors.append(
                "development pilot archive exact file set: duplicate paths="
                f"{duplicates}"
            )
        errors.extend(
            _compare_paths(
                expected=expected,
                observed=set(observed),
                context="development pilot archive files",
            )
        )
    except (PilotPathError, TypeError, KeyError, ValueError) as exc:
        if isinstance(exc, PilotPathError):
            return False, (str(exc),)
        return False, (
            "development pilot archive exact file set: verification failed "
            f"closed: {type(exc).__name__}: {exc}",
        )
    unique = tuple(dict.fromkeys(errors))
    return not unique, unique


__all__ = [
    "PilotPathError",
    "expected_bundle_directory_paths",
    "expected_bundle_file_paths",
    "verify_exact_archive_paths",
    "verify_exact_bundle_tree",
]
