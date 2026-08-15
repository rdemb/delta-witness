"""Strict machine-readable outcome receipts for cooperating test adapters."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile
from typing import Any, Mapping

from .errors import ReceiptError

SCHEMA_VERSION = "deltawitness.outcome-receipt.v1"
MAX_RECEIPT_BYTES = 65_536

_COUNT_FIELDS = (
    "tests_run",
    "passed",
    "failures",
    "errors",
    "skipped",
    "expected_failures",
    "unexpected_successes",
)
_ALLOWED_OUTCOMES = {
    "passed",
    "test_failure",
    "test_error",
    "no_tests",
    "no_effective_tests",
    "unexpected_success",
    "producer_error",
}
_HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_PRODUCER_TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/+:-]{0,127}$")


@dataclass(frozen=True)
class OutcomeReceipt:
    """A validated receipt whose semantics are safe to place in a witness report."""

    schema_version: str
    binding: str
    producer_name: str
    producer_version: str
    outcome: str
    counts: dict[str, int]
    sha256: str


def canonical_receipt_bytes(document: object) -> bytes:
    """Return one portable JSON representation for hashing and atomic storage."""

    return json.dumps(
        document,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def classify_counts(counts: Mapping[str, int]) -> str:
    """Classify aggregate unittest-like counts without reading narrative output."""

    if counts["tests_run"] == 0:
        return "no_tests"
    if counts["errors"] > 0:
        return "test_error"
    if counts["unexpected_successes"] > 0:
        return "unexpected_success"
    if counts["failures"] > 0:
        return "test_failure"
    if counts["passed"] == 0:
        return "no_effective_tests"
    return "passed"


def _decode_json_strict(raw: bytes) -> object:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        document: dict[str, Any] = {}
        for key, value in pairs:
            if key in document:
                raise ValueError(f"duplicate key: {key}")
            document[key] = value
        return document

    try:
        text = raw.decode("utf-8")
        return json.loads(text, object_pairs_hook=reject_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ReceiptError("invalid_json", "Outcome receipt is not strict UTF-8 JSON") from exc


def _validate_counts(value: object) -> dict[str, int]:
    if not isinstance(value, dict) or set(value) != set(_COUNT_FIELDS):
        raise ReceiptError(
            "invalid_counts",
            f"Outcome receipt counts must contain exactly {list(_COUNT_FIELDS)!r}",
        )

    counts: dict[str, int] = {}
    for field in _COUNT_FIELDS:
        item = value[field]
        if not isinstance(item, int) or isinstance(item, bool) or not 0 <= item <= 100_000_000:
            raise ReceiptError(
                "invalid_counts",
                f"Outcome receipt count {field!r} must be an integer between 0 and 100000000",
            )
        counts[field] = item

    classified_total = sum(counts[field] for field in _COUNT_FIELDS if field != "tests_run")
    if classified_total != counts["tests_run"]:
        raise ReceiptError(
            "inconsistent_counts",
            "Outcome receipt category counts do not sum to tests_run",
        )
    return counts


def validate_receipt_document(
    document: object,
    *,
    expected_binding: str,
) -> OutcomeReceipt:
    """Validate a decoded receipt with strict fields and invocation binding."""

    if not _HEX_SHA256.fullmatch(expected_binding):
        raise ReceiptError("invalid_expected_binding", "Expected receipt binding is not SHA-256")
    if not isinstance(document, dict):
        raise ReceiptError("invalid_schema", "Outcome receipt root must be a JSON object")
    required = {"schema_version", "binding", "producer", "outcome", "counts"}
    if set(document) != required:
        raise ReceiptError(
            "invalid_schema",
            f"Outcome receipt fields must be exactly {sorted(required)!r}",
        )
    if document["schema_version"] != SCHEMA_VERSION:
        raise ReceiptError("unsupported_schema", "Unsupported outcome receipt schema")

    binding = document["binding"]
    if not isinstance(binding, str) or not _HEX_SHA256.fullmatch(binding):
        raise ReceiptError("invalid_binding", "Outcome receipt binding is not SHA-256")
    if binding != expected_binding:
        raise ReceiptError("binding_mismatch", "Outcome receipt does not match this invocation")

    producer = document["producer"]
    if not isinstance(producer, dict) or set(producer) != {"name", "version"}:
        raise ReceiptError(
            "invalid_producer",
            "Outcome receipt producer must contain exactly name and version",
        )
    producer_name = producer["name"]
    producer_version = producer["version"]
    if not isinstance(producer_name, str) or not _PRODUCER_TOKEN.fullmatch(producer_name):
        raise ReceiptError("invalid_producer", "Outcome receipt producer name is invalid")
    if not isinstance(producer_version, str) or not _PRODUCER_TOKEN.fullmatch(producer_version):
        raise ReceiptError("invalid_producer", "Outcome receipt producer version is invalid")

    outcome = document["outcome"]
    if not isinstance(outcome, str) or outcome not in _ALLOWED_OUTCOMES:
        raise ReceiptError("invalid_outcome", "Outcome receipt has an unsupported outcome")
    counts = _validate_counts(document["counts"])

    if outcome == "producer_error":
        if any(counts.values()):
            raise ReceiptError(
                "inconsistent_outcome",
                "producer_error receipts must use zero counts",
            )
    elif outcome != classify_counts(counts):
        raise ReceiptError(
            "inconsistent_outcome",
            "Outcome receipt outcome is inconsistent with aggregate counts",
        )

    digest = hashlib.sha256(canonical_receipt_bytes(document)).hexdigest()
    return OutcomeReceipt(
        schema_version=SCHEMA_VERSION,
        binding=binding,
        producer_name=producer_name,
        producer_version=producer_version,
        outcome=outcome,
        counts=counts,
        sha256=digest,
    )


def build_receipt_document(
    *,
    binding: str,
    producer_name: str,
    producer_version: str,
    outcome: str,
    counts: Mapping[str, int],
) -> dict[str, object]:
    """Build and self-validate a receipt document for a trusted adapter."""

    document: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "binding": binding,
        "producer": {"name": producer_name, "version": producer_version},
        "outcome": outcome,
        "counts": dict(counts),
    }
    validate_receipt_document(document, expected_binding=binding)
    return document


def _read_bounded_regular_file(path: Path) -> bytes:
    try:
        metadata = path.lstat()
    except FileNotFoundError as exc:
        raise ReceiptError("missing", "Outcome receipt was not produced") from exc
    except OSError as exc:
        raise ReceiptError("unreadable", "Outcome receipt metadata cannot be read") from exc

    if not stat.S_ISREG(metadata.st_mode):
        raise ReceiptError("not_regular", "Outcome receipt must be a regular file")
    if metadata.st_size > MAX_RECEIPT_BYTES:
        raise ReceiptError("too_large", "Outcome receipt exceeds the size limit")

    flags = os.O_RDONLY
    flags |= getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except FileNotFoundError as exc:
        raise ReceiptError("missing", "Outcome receipt disappeared before validation") from exc
    except OSError as exc:
        raise ReceiptError("unreadable", "Outcome receipt cannot be opened safely") from exc

    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            raise ReceiptError("not_regular", "Outcome receipt must remain a regular file")
        if opened.st_size > MAX_RECEIPT_BYTES:
            raise ReceiptError("too_large", "Outcome receipt exceeds the size limit")
        chunks: list[bytes] = []
        remaining = MAX_RECEIPT_BYTES + 1
        while remaining > 0:
            chunk = os.read(descriptor, min(65_536, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(chunks)
    finally:
        os.close(descriptor)

    if len(raw) > MAX_RECEIPT_BYTES:
        raise ReceiptError("too_large", "Outcome receipt exceeds the size limit")
    return raw


def load_outcome_receipt(path: Path, *, expected_binding: str) -> OutcomeReceipt:
    """Load a bounded regular file and validate its full receipt semantics."""

    raw = _read_bounded_regular_file(path)
    document = _decode_json_strict(raw)
    return validate_receipt_document(document, expected_binding=expected_binding)


def write_outcome_receipt(path: Path, document: object, *, expected_binding: str) -> None:
    """Atomically write a self-validated receipt with owner-only permissions."""

    validate_receipt_document(document, expected_binding=expected_binding)
    payload = canonical_receipt_bytes(document) + b"\n"
    if len(payload) > MAX_RECEIPT_BYTES:
        raise ReceiptError("too_large", "Outcome receipt exceeds the size limit")

    parent = path.parent
    if not parent.is_dir():
        raise ReceiptError("unwritable", "Outcome receipt parent directory does not exist")

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=parent,
    )
    temporary = Path(temporary_name)
    try:
        if os.name == "posix":
            os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        if os.name == "posix":
            path.chmod(0o600)
    except Exception:
        try:
            os.close(descriptor)
        except OSError:
            pass
        temporary.unlink(missing_ok=True)
        raise
