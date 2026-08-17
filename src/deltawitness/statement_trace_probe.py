"""Fixed standard-library unittest probe with statement trace evidence.

The probe emits two invocation-bound artifacts for one exact unittest selector:

- the existing `outcome-receipt-v1` typed result;
- a strict `statement-trace-receipt-v1` for one exact source/symbol/line scope.

It is intentionally narrow and currently used only with project-owned DW-001
fixtures. A trace binding is visible to tested code and is not authentication.
"""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import io
import json
import os
from pathlib import Path
import stat
import sys
from typing import Any, Mapping
import unittest

from . import __version__
from .errors import DeltaWitnessError, ReceiptError
from .receipt import classify_counts
from .reporting import canonical_json, sha256_document
from .unittest_probe import (
    _ReceiptTestResult,
    _destination_from_environment,
    _load_suite,
    _write,
    _zero_counts,
)


TRACE_SCHEMA_VERSION = "deltawitness.statement-trace-receipt.v1"
TRACE_PRODUCER_NAME = "deltawitness-statement-trace"
TRACE_OUTPUT_BASENAME = ".deltawitness-statement-trace.json"
_MAX_TRACE_BYTES = 65_536

_TRACE_FIELDS = {
    "schema_version",
    "binding",
    "producer",
    "target",
    "trace_status",
    "function_calls",
    "covered_lines",
    "line_hits",
    "trace_error",
    "trace_sha256",
}
_TARGET_FIELDS = {
    "path",
    "symbol",
    "source_sha256",
    "target_lines",
}
_PRODUCER_FIELDS = {"name", "version"}
_HIT_FIELDS = {"line", "hits"}


class StatementTraceError(DeltaWitnessError):
    """Raised when a statement-trace receipt is unsafe or inconsistent."""


def _error(context: str, message: str) -> StatementTraceError:
    return StatementTraceError(f"{context}: {message}")


def _exact_keys(
    value: object,
    expected: set[str],
    *,
    context: str,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _error(context, "must be an object")
    actual = set(value)
    if actual != expected:
        raise _error(
            context,
            f"field mismatch; missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}",
        )
    return value


def _sha256(value: object, *, context: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise _error(context, "must be a lowercase SHA-256 digest")
    return value


def compute_trace_sha256(document: dict[str, Any]) -> str:
    """Hash the complete trace receipt with its own digest normalized."""

    if not isinstance(document, dict):
        raise _error("statement trace receipt", "must be an object")
    normalized = deepcopy(document)
    normalized["trace_sha256"] = None
    return sha256_document(normalized)


def build_trace_document(
    *,
    binding: str,
    target_path: str,
    target_symbol: str,
    source_sha256: str,
    target_lines: list[int],
    trace_status: str,
    function_calls: int | None,
    line_hits: Mapping[int, int],
    trace_error: str | None,
) -> dict[str, Any]:
    """Build one canonical trace receipt."""

    hits = [
        {"line": line, "hits": line_hits[line]}
        for line in sorted(line_hits)
    ]
    document: dict[str, Any] = {
        "schema_version": TRACE_SCHEMA_VERSION,
        "binding": binding,
        "producer": {
            "name": TRACE_PRODUCER_NAME,
            "version": __version__,
        },
        "target": {
            "path": target_path,
            "symbol": target_symbol,
            "source_sha256": source_sha256,
            "target_lines": sorted(target_lines),
        },
        "trace_status": trace_status,
        "function_calls": function_calls,
        "covered_lines": [item["line"] for item in hits],
        "line_hits": hits,
        "trace_error": trace_error,
        "trace_sha256": None,
    }
    document["trace_sha256"] = compute_trace_sha256(document)
    return document


def validate_trace_document(
    document: object,
    *,
    expected_binding: str,
    expected_target_path: str,
    expected_target_symbol: str,
    expected_source_sha256: str,
    expected_target_lines: list[int],
) -> dict[str, Any]:
    """Validate strict trace structure, relations, consistency, and digest."""

    trace = _exact_keys(
        document,
        _TRACE_FIELDS,
        context="statement trace receipt",
    )
    if trace["schema_version"] != TRACE_SCHEMA_VERSION:
        raise _error("statement trace receipt.schema_version", "is unsupported")
    if trace["binding"] != expected_binding:
        raise _error("statement trace receipt.binding", "does not match invocation")
    producer = _exact_keys(
        trace["producer"],
        _PRODUCER_FIELDS,
        context="statement trace receipt.producer",
    )
    if producer != {
        "name": TRACE_PRODUCER_NAME,
        "version": __version__,
    }:
        raise _error("statement trace receipt.producer", "is unsupported")
    target = _exact_keys(
        trace["target"],
        _TARGET_FIELDS,
        context="statement trace receipt.target",
    )
    expected_target = {
        "path": expected_target_path,
        "symbol": expected_target_symbol,
        "source_sha256": expected_source_sha256,
        "target_lines": sorted(expected_target_lines),
    }
    if target != expected_target:
        raise _error("statement trace receipt.target", "does not match invocation")

    status = trace["trace_status"]
    if status not in {"complete", "indeterminate"}:
        raise _error("statement trace receipt.trace_status", "is unsupported")
    covered_lines = trace["covered_lines"]
    line_hits_value = trace["line_hits"]
    if not isinstance(covered_lines, list) or not isinstance(line_hits_value, list):
        raise _error(
            "statement trace receipt coverage",
            "covered_lines and line_hits must be arrays",
        )
    if any(
        isinstance(line, bool) or not isinstance(line, int) or line <= 0
        for line in covered_lines
    ):
        raise _error(
            "statement trace receipt.covered_lines",
            "must contain positive integers",
        )
    if covered_lines != sorted(set(covered_lines)):
        raise _error(
            "statement trace receipt.covered_lines",
            "must be sorted and unique",
        )
    line_hits: list[dict[str, int]] = []
    for index, item in enumerate(line_hits_value):
        hit = _exact_keys(
            item,
            _HIT_FIELDS,
            context=f"statement trace receipt.line_hits[{index}]",
        )
        line = hit["line"]
        count = hit["hits"]
        if (
            isinstance(line, bool)
            or not isinstance(line, int)
            or line <= 0
            or isinstance(count, bool)
            or not isinstance(count, int)
            or count <= 0
        ):
            raise _error(
                f"statement trace receipt.line_hits[{index}]",
                "line and hits must be positive integers",
            )
        line_hits.append({"line": line, "hits": count})
    if line_hits != sorted(line_hits, key=lambda item: item["line"]):
        raise _error(
            "statement trace receipt.line_hits",
            "must be sorted by line",
        )
    if len({item["line"] for item in line_hits}) != len(line_hits):
        raise _error("statement trace receipt.line_hits", "contains duplicate lines")
    if covered_lines != [item["line"] for item in line_hits]:
        raise _error(
            "statement trace receipt coverage",
            "covered_lines must equal line_hits line identities",
        )
    if not set(covered_lines).issubset(set(expected_target_lines)):
        raise _error(
            "statement trace receipt.covered_lines",
            "contains a line outside the declared target",
        )

    if status == "complete":
        calls = trace["function_calls"]
        if isinstance(calls, bool) or not isinstance(calls, int) or calls < 0:
            raise _error(
                "statement trace receipt.function_calls",
                "must be a nonnegative integer for complete traces",
            )
        if trace["trace_error"] is not None:
            raise _error(
                "statement trace receipt.trace_error",
                "must be null for complete traces",
            )
    else:
        if trace["function_calls"] is not None:
            raise _error(
                "statement trace receipt.function_calls",
                "must be null for indeterminate traces",
            )
        if covered_lines or line_hits:
            raise _error(
                "statement trace receipt coverage",
                "must be empty for indeterminate traces",
            )
        trace_error = trace["trace_error"]
        if not isinstance(trace_error, str) or not trace_error:
            raise _error(
                "statement trace receipt.trace_error",
                "must be a non-empty diagnostic code for indeterminate traces",
            )

    recorded = _sha256(
        trace["trace_sha256"],
        context="statement trace receipt.trace_sha256",
    )
    computed = compute_trace_sha256(trace)
    if recorded != computed:
        raise _error(
            "statement trace receipt.trace_sha256",
            "digest mismatch",
        )
    return deepcopy(trace)


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant is forbidden: {value}")


def _object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_trace_document(
    path: Path,
    *,
    expected_binding: str,
    expected_target_path: str,
    expected_target_symbol: str,
    expected_source_sha256: str,
    expected_target_lines: list[int],
) -> dict[str, Any]:
    """Load one bounded regular strict-JSON trace receipt."""

    try:
        metadata = path.lstat()
    except OSError as exc:
        raise _error("statement trace receipt path", "cannot be inspected") from exc
    if not stat.S_ISREG(metadata.st_mode) or path.is_symlink():
        raise _error("statement trace receipt path", "must be a regular non-link file")
    if metadata.st_size > _MAX_TRACE_BYTES:
        raise _error("statement trace receipt path", "exceeds the size limit")
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        document = json.loads(
            text,
            object_pairs_hook=_object_pairs,
            parse_constant=_reject_constant,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise _error("statement trace receipt", "is not strict UTF-8 JSON") from exc
    return validate_trace_document(
        document,
        expected_binding=expected_binding,
        expected_target_path=expected_target_path,
        expected_target_symbol=expected_target_symbol,
        expected_source_sha256=expected_source_sha256,
        expected_target_lines=expected_target_lines,
    )


def _safe_relative_path(raw: str, *, context: str) -> Path:
    path = Path(raw)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise _error(context, "must be a normalized relative path")
    if "\\" in raw:
        raise _error(context, "must use forward-slash path syntax")
    return path


def _trace_destination(raw: str) -> Path:
    relative = _safe_relative_path(raw, context="statement trace output")
    if relative.as_posix() != TRACE_OUTPUT_BASENAME:
        raise _error(
            "statement trace output",
            f"must equal {TRACE_OUTPUT_BASENAME!r}",
        )
    destination = Path.cwd() / relative
    try:
        destination.lstat()
    except FileNotFoundError:
        return destination
    except OSError as exc:
        raise _error("statement trace output", "cannot be inspected") from exc
    raise _error("statement trace output", "must not already exist")


def _target_source(
    raw_path: str,
    expected_sha256: str,
) -> tuple[Path, str]:
    relative = _safe_relative_path(raw_path, context="statement trace target path")
    root = Path.cwd().resolve()
    try:
        path = (root / relative).resolve(strict=True)
    except OSError as exc:
        raise _error("statement trace target path", "cannot be resolved") from exc
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise _error("statement trace target path", "escapes the working directory") from exc
    if not path.is_file() or path.is_symlink():
        raise _error("statement trace target path", "must be a regular non-link file")
    digest = __import__("hashlib").sha256(path.read_bytes()).hexdigest()
    if digest != expected_sha256:
        raise _error("statement trace target source_sha256", "does not match source bytes")
    return path, relative.as_posix()


def _write_trace(destination: Path, document: dict[str, Any]) -> None:
    data = canonical_json(document) + b"\n"
    if len(data) > _MAX_TRACE_BYTES:
        raise _error("statement trace receipt", "exceeds the size limit")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(destination, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            destination.unlink(missing_ok=True)
        except OSError:
            pass
        raise


class _Collector:
    def __init__(
        self,
        *,
        target_path: Path,
        target_symbol: str,
        target_lines: set[int],
    ) -> None:
        self.target_path = target_path
        self.target_symbol = target_symbol
        self.target_lines = target_lines
        self.function_calls = 0
        self.line_hits: Counter[int] = Counter()

    def _matches(self, frame: object) -> bool:
        code = getattr(frame, "f_code", None)
        if code is None or getattr(code, "co_name", None) != self.target_symbol:
            return False
        filename = getattr(code, "co_filename", None)
        if not isinstance(filename, str):
            return False
        try:
            return Path(filename).resolve() == self.target_path
        except OSError:
            return False

    def global_trace(self, frame: object, event: str, arg: object):
        if event == "call" and self._matches(frame):
            self.function_calls += 1
            return self.local_trace
        return None

    def local_trace(self, frame: object, event: str, arg: object):
        if event == "line":
            line = getattr(frame, "f_lineno", None)
            if isinstance(line, int) and line in self.target_lines:
                self.line_hits[line] += 1
        return self.local_trace


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m deltawitness.statement_trace_probe",
        description=(
            "Run exact unittest selectors and emit typed outcome plus fixed "
            "statement-trace receipts."
        ),
    )
    parser.add_argument("--start-directory", default="tests")
    parser.add_argument("--pattern", default="test*.py")
    parser.add_argument("--top-level-directory", default=None)
    parser.add_argument("--test-name", action="append", default=None)
    parser.add_argument("--verbosity", type=int, choices=(0, 1, 2), default=0)
    parser.add_argument("--target-path", required=True)
    parser.add_argument("--target-symbol", required=True)
    parser.add_argument("--target-line", action="append", type=int, required=True)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--trace-output", required=True)
    return parser


def run_probe(args: argparse.Namespace) -> int:
    receipt_destination, binding = _destination_from_environment()
    trace_destination = _trace_destination(args.trace_output)
    expected_sha256 = _sha256(
        args.source_sha256,
        context="statement trace source_sha256",
    )
    target_lines = sorted(set(args.target_line))
    if any(line <= 0 for line in target_lines):
        raise _error("statement trace target lines", "must be positive integers")

    trace_status = "indeterminate"
    function_calls: int | None = None
    line_hits: Mapping[int, int] = {}
    trace_error: str | None = "trace_not_started"
    outcome = "producer_error"
    counts = _zero_counts()

    try:
        target_path, target_path_text = _target_source(
            args.target_path,
            expected_sha256,
        )
        suite = _load_suite(args)
        collector = _Collector(
            target_path=target_path,
            target_symbol=args.target_symbol,
            target_lines=set(target_lines),
        )
        previous_trace = sys.gettrace()
        if previous_trace is not None:
            trace_error = "preexisting_trace"
            result = unittest.TextTestRunner(
                stream=io.StringIO(),
                verbosity=args.verbosity,
                failfast=False,
                buffer=True,
                resultclass=_ReceiptTestResult,
            ).run(suite)
        else:
            try:
                sys.settrace(collector.global_trace)
                result = unittest.TextTestRunner(
                    stream=io.StringIO(),
                    verbosity=args.verbosity,
                    failfast=False,
                    buffer=True,
                    resultclass=_ReceiptTestResult,
                ).run(suite)
            finally:
                sys.settrace(previous_trace)
            trace_status = "complete"
            function_calls = collector.function_calls
            line_hits = dict(collector.line_hits)
            trace_error = None

        if not isinstance(result, _ReceiptTestResult):
            raise ReceiptError("unexpected_result", "unittest returned an unexpected result type")
        counts = result.receipt_counts()
        outcome = classify_counts(counts)
        _write(receipt_destination, binding, outcome=outcome, counts=counts)
        trace_document = build_trace_document(
            binding=binding,
            target_path=target_path_text,
            target_symbol=args.target_symbol,
            source_sha256=expected_sha256,
            target_lines=target_lines,
            trace_status=trace_status,
            function_calls=function_calls,
            line_hits=line_hits,
            trace_error=trace_error,
        )
        _write_trace(trace_destination, trace_document)
    except (ReceiptError, StatementTraceError):
        raise
    except Exception as exc:
        try:
            _write(
                receipt_destination,
                binding,
                outcome="producer_error",
                counts=_zero_counts(),
            )
        except Exception:
            pass
        try:
            trace_document = build_trace_document(
                binding=binding,
                target_path=args.target_path,
                target_symbol=args.target_symbol,
                source_sha256=expected_sha256,
                target_lines=target_lines,
                trace_status="indeterminate",
                function_calls=None,
                line_hits={},
                trace_error="producer_error",
            )
            _write_trace(trace_destination, trace_document)
        except Exception:
            pass
        raise ReceiptError(
            "producer_error",
            "statement trace receipt production failed",
        ) from exc

    if outcome == "passed":
        return 0
    if outcome == "test_failure":
        return 1
    return 2


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
