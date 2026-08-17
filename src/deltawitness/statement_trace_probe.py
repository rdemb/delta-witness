"""Hardened public statement-trace probe facade.

The implementation lives in the private sibling module. This facade preserves
its receipt and trace semantics while rejecting symbolic links in every target
path component before resolution. The fixed DW-001 runner creates regular
project-owned files, but the child boundary remains fail-closed independently.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import stat
import sys
from threading import RLock
from typing import Any

from . import _statement_trace_probe as _implementation
from .errors import ReceiptError


StatementTraceError = _implementation.StatementTraceError
TRACE_OUTPUT_BASENAME = _implementation.TRACE_OUTPUT_BASENAME
TRACE_PRODUCER_NAME = _implementation.TRACE_PRODUCER_NAME
TRACE_SCHEMA_VERSION = _implementation.TRACE_SCHEMA_VERSION

build_trace_document = _implementation.build_trace_document
compute_trace_sha256 = _implementation.compute_trace_sha256
_parser = _implementation._parser

# Private regression seam. Product callers do not provide a suite loader; the
# facade forwards this alias only so a fail-closed producer-error test can
# inject one deterministic internal failure without weakening the child API.
_load_suite = _implementation._load_suite

_TARGET_LOCK = RLock()


def _error(context: str, message: str) -> StatementTraceError:
    return StatementTraceError(f"{context}: {message}")


def validate_trace_document(
    document: object,
    *,
    expected_binding: str,
    expected_target_path: str,
    expected_target_symbol: str,
    expected_source_sha256: str,
    expected_target_lines: list[int],
) -> dict[str, Any]:
    """Validate one trace and enforce producer-implied call/line relations."""

    validated = _implementation.validate_trace_document(
        document,
        expected_binding=expected_binding,
        expected_target_path=expected_target_path,
        expected_target_symbol=expected_target_symbol,
        expected_source_sha256=expected_source_sha256,
        expected_target_lines=expected_target_lines,
    )
    if (
        validated["trace_status"] == "complete"
        and validated["function_calls"] == 0
        and (validated["covered_lines"] or validated["line_hits"])
    ):
        raise _error(
            "statement trace function_calls",
            "must be positive when complete line evidence is present",
        )
    return validated


def load_trace_document(
    path: Path,
    *,
    expected_binding: str,
    expected_target_path: str,
    expected_target_symbol: str,
    expected_source_sha256: str,
    expected_target_lines: list[int],
) -> dict[str, Any]:
    """Load a bounded trace file and apply the public relational validator."""

    document = _implementation.load_trace_document(
        path,
        expected_binding=expected_binding,
        expected_target_path=expected_target_path,
        expected_target_symbol=expected_target_symbol,
        expected_source_sha256=expected_source_sha256,
        expected_target_lines=expected_target_lines,
    )
    return validate_trace_document(
        document,
        expected_binding=expected_binding,
        expected_target_path=expected_target_path,
        expected_target_symbol=expected_target_symbol,
        expected_source_sha256=expected_source_sha256,
        expected_target_lines=expected_target_lines,
    )


def _safe_relative_path(raw: str, *, context: str) -> Path:
    return _implementation._safe_relative_path(raw, context=context)


def _target_source(
    raw_path: str,
    expected_sha256: str,
) -> tuple[Path, str]:
    """Resolve one regular target without following any symbolic-link component."""

    relative = _safe_relative_path(
        raw_path,
        context="statement trace target path",
    )
    root = Path.cwd().resolve()
    candidate = root
    final_metadata: object | None = None

    try:
        for index, part in enumerate(relative.parts):
            candidate = candidate / part
            metadata = candidate.lstat()
            if stat.S_ISLNK(metadata.st_mode):
                raise _error(
                    "statement trace target path",
                    "must be a regular non-link path; symbolic-link components are forbidden",
                )
            if index < len(relative.parts) - 1:
                if not stat.S_ISDIR(metadata.st_mode):
                    raise _error(
                        "statement trace target path",
                        "ancestor components must be directories",
                    )
            else:
                final_metadata = metadata
    except StatementTraceError:
        raise
    except OSError as exc:
        raise _error(
            "statement trace target path",
            "cannot be inspected",
        ) from exc

    if final_metadata is None or not stat.S_ISREG(final_metadata.st_mode):
        raise _error(
            "statement trace target path",
            "must be a regular non-link file",
        )

    try:
        path = candidate.resolve(strict=True)
        path.relative_to(root)
        source_bytes = path.read_bytes()
    except (OSError, ValueError) as exc:
        raise _error(
            "statement trace target path",
            "cannot be resolved inside the working directory",
        ) from exc

    digest = hashlib.sha256(source_bytes).hexdigest()
    if digest != expected_sha256:
        raise _error(
            "statement trace target source_sha256",
            "does not match source bytes",
        )
    return path, relative.as_posix()


def run_probe(args: argparse.Namespace) -> int:
    """Run the private producer with hardened and testable internals installed."""

    with _TARGET_LOCK:
        original_target = _implementation._target_source
        original_loader = _implementation._load_suite
        _implementation._target_source = _target_source
        _implementation._load_suite = _load_suite
        try:
            return _implementation.run_probe(args)
        finally:
            _implementation._target_source = original_target
            _implementation._load_suite = original_loader


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        return run_probe(args)
    except (ReceiptError, StatementTraceError) as exc:
        code = getattr(exc, "code", "statement_trace_error")
        print(f"DeltaWitness statement trace error: {code}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "StatementTraceError",
    "TRACE_OUTPUT_BASENAME",
    "TRACE_PRODUCER_NAME",
    "TRACE_SCHEMA_VERSION",
    "build_trace_document",
    "compute_trace_sha256",
    "load_trace_document",
    "validate_trace_document",
]
