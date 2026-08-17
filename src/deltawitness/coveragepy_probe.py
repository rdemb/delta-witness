"""Fixed Coverage.py measurement child for the DW-001 direct baseline.

The child executes one exact project-owned unittest selector, emits the existing
invocation-bound typed outcome receipt, and emits one strict public-safe
Coverage.py measurement receipt. Coverage.py is imported lazily so the base
DeltaWitness package remains dependency-free.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import importlib.metadata
import math
import os
from pathlib import Path
import re
import stat
import sys
import time
from typing import Any, Mapping, Sequence
import unittest

from . import __version__
from .coveragepy_contract import (
    COVERAGEPY_MANIFEST_SHA256,
    COVERAGEPY_PACKAGE,
    COVERAGEPY_VERSION,
)
from .errors import DeltaWitnessError, ReceiptError, ReportError
from .receipt import classify_counts
from .reporting import canonical_json, load_report, sha256_document
from .unittest_probe import (
    _ReceiptTestResult,
    _destination_from_environment,
    _load_suite,
    _write,
)


COVERAGE_RECEIPT_SCHEMA_VERSION = (
    "deltawitness.coveragepy-measurement-receipt.v1"
)
COVERAGE_PRODUCER_NAME = "deltawitness-coveragepy"
COVERAGE_OUTPUT_BASENAME = ".deltawitness-coveragepy.json"
_MAX_RECEIPT_BYTES = 262_144
_STABLE_ERROR = re.compile(r"^[a-z][a-z0-9_]{0,95}$")

_ROOT_FIELDS = {
    "schema_version",
    "binding",
    "producer",
    "distribution",
    "configuration",
    "target",
    "context",
    "measurement_status",
    "measurement_error",
    "measured_files",
    "statement_evidence",
    "branch_evidence",
    "context_evidence",
    "cost",
    "coverage_sha256",
}
_PRODUCER_FIELDS = {"name", "version"}
_DISTRIBUTION_FIELDS = {
    "manifest_sha256",
    "package",
    "expected_version",
    "observed_distribution_name",
    "observed_distribution_version",
    "observed_module_version",
}
_CONFIGURATION_FIELDS = {
    "data_file",
    "auto_data",
    "timid",
    "branch",
    "config_file",
    "source_dirs",
    "concurrency",
    "check_preimported",
    "context",
    "messages",
    "plugins",
    "auto_start",
    "subprocess_measurement",
    "network_during_measurement",
}
_TARGET_FIELDS = {"path", "symbol", "source_sha256", "target_lines"}
_CONTEXT_FIELDS = {"id", "strategy"}
_STATEMENT_FIELDS = {
    "executable",
    "executed",
    "missing",
    "measured_lines",
    "target_executable",
    "target_executed",
    "target_missing",
}
_BRANCH_FIELDS = {
    "has_arcs",
    "all_arcs",
    "context_arcs",
    "target_arcs",
    "branch_stats",
    "target_branch_stats",
    "missing_branch_count",
    "target_missing_branch_count",
    "missing_branch_arcs",
    "missing_branch_arc_identity_status",
}
_BRANCH_STAT_FIELDS = {"line", "total_exits", "taken_exits"}
_CONTEXT_EVIDENCE_FIELDS = {
    "measured_contexts",
    "contexts_by_lineno",
    "query_context",
    "lines",
    "arcs",
    "partition_valid",
}
_CONTEXT_LINE_FIELDS = {"line", "contexts"}
_COST_FIELDS = {
    "status",
    "wall_clock_seconds",
    "cpu_seconds",
    "missing_reason",
}


class CoveragePyProbeError(DeltaWitnessError):
    """Raised when the exact Coverage.py measurement receipt is invalid."""


def _error(context: str, message: str) -> CoveragePyProbeError:
    return CoveragePyProbeError(f"{context}: {message}")


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


def _strict_equal(expected: object, observed: object) -> bool:
    if type(expected) is not type(observed):
        return False
    if isinstance(expected, dict):
        assert isinstance(observed, dict)
        # JSON object member order is non-semantic. Canonical serialization
        # sorts keys, so round-tripped receipts must be compared by exact key
        # membership and values rather than insertion order.
        return set(expected) == set(observed) and all(
            _strict_equal(expected[key], observed[key]) for key in expected
        )
    if isinstance(expected, list):
        assert isinstance(observed, list)
        return len(expected) == len(observed) and all(
            _strict_equal(left, right)
            for left, right in zip(expected, observed, strict=True)
        )
    return expected == observed


def _sha256(value: object, *, context: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise _error(context, "must be a lowercase SHA-256 digest")
    return value


def _finite_nonnegative(value: object, *, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _error(context, "must be a finite nonnegative number")
    numeric = float(value)
    if not math.isfinite(numeric) or numeric < 0.0:
        raise _error(context, "must be a finite nonnegative number")
    return numeric


def _positive_lines(
    value: object,
    *,
    context: str,
    allow_empty: bool = True,
) -> list[int]:
    if not isinstance(value, list):
        raise _error(context, "must be an array")
    if not allow_empty and not value:
        raise _error(context, "must not be empty")
    if any(
        isinstance(line, bool) or not isinstance(line, int) or line <= 0
        for line in value
    ):
        raise _error(context, "must contain positive integers")
    if value != sorted(set(value)):
        raise _error(context, "must be sorted and unique")
    return value


def _arcs(value: object, *, context: str) -> list[list[int]]:
    if not isinstance(value, list):
        raise _error(context, "must be an array")
    normalized: list[list[int]] = []
    for index, arc in enumerate(value):
        if (
            not isinstance(arc, list)
            or len(arc) != 2
            or any(
                isinstance(item, bool) or not isinstance(item, int)
                for item in arc
            )
        ):
            raise _error(f"{context}[{index}]", "must be an integer pair")
        normalized.append([arc[0], arc[1]])
    if (
        normalized != sorted(normalized)
        or len({tuple(arc) for arc in normalized}) != len(normalized)
    ):
        raise _error(context, "must be sorted and unique")
    return normalized


def _relative_path(value: object, *, context: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise _error(context, "must be a normalized relative path")
    path = Path(value)
    if path.is_absolute() or any(
        part in {"", ".", ".."} for part in path.parts
    ):
        raise _error(context, "must be a normalized relative path")
    if path.as_posix() != value:
        raise _error(context, "must use normalized forward-slash syntax")
    return value


def compute_coverage_receipt_sha256(document: dict[str, Any]) -> str:
    """Hash the complete receipt with its own digest normalized."""

    if not isinstance(document, dict):
        raise CoveragePyProbeError("Coverage.py receipt must be an object")
    normalized = deepcopy(document)
    normalized["coverage_sha256"] = None
    return sha256_document(normalized)


def build_coverage_receipt(
    *,
    binding: str,
    distribution: Mapping[str, object],
    configuration: Mapping[str, object],
    target: Mapping[str, object],
    context: Mapping[str, object],
    measurement_status: str,
    measurement_error: str | None,
    measured_files: Sequence[str] | None,
    statement_evidence: Mapping[str, object] | None,
    branch_evidence: Mapping[str, object] | None,
    context_evidence: Mapping[str, object] | None,
    cost: Mapping[str, object],
) -> dict[str, Any]:
    """Build one canonical measurement receipt without hiding negative evidence."""

    document: dict[str, Any] = {
        "schema_version": COVERAGE_RECEIPT_SCHEMA_VERSION,
        "binding": binding,
        "producer": {
            "name": COVERAGE_PRODUCER_NAME,
            "version": __version__,
        },
        "distribution": deepcopy(dict(distribution)),
        "configuration": deepcopy(dict(configuration)),
        "target": deepcopy(dict(target)),
        "context": deepcopy(dict(context)),
        "measurement_status": measurement_status,
        "measurement_error": measurement_error,
        "measured_files": (
            None if measured_files is None else list(measured_files)
        ),
        "statement_evidence": (
            None
            if statement_evidence is None
            else deepcopy(dict(statement_evidence))
        ),
        "branch_evidence": (
            None
            if branch_evidence is None
            else deepcopy(dict(branch_evidence))
        ),
        "context_evidence": (
            None
            if context_evidence is None
            else deepcopy(dict(context_evidence))
        ),
        "cost": deepcopy(dict(cost)),
        "coverage_sha256": None,
    }
    document["coverage_sha256"] = compute_coverage_receipt_sha256(document)
    return document


def _validate_distribution(
    value: object,
    *,
    expected_manifest_sha256: str,
    status: str,
) -> dict[str, Any]:
    distribution = _exact_keys(
        value,
        _DISTRIBUTION_FIELDS,
        context="Coverage.py receipt.distribution",
    )
    if distribution["manifest_sha256"] != expected_manifest_sha256:
        raise _error(
            "Coverage.py receipt.distribution.manifest_sha256",
            "does not match invocation",
        )
    if distribution["package"] != COVERAGEPY_PACKAGE:
        raise _error(
            "Coverage.py receipt.distribution.package",
            "is unsupported",
        )
    if distribution["expected_version"] != COVERAGEPY_VERSION:
        raise _error(
            "Coverage.py receipt.distribution.expected_version",
            "is unsupported",
        )
    observed = (
        distribution["observed_distribution_name"],
        distribution["observed_distribution_version"],
        distribution["observed_module_version"],
    )
    exact = (COVERAGEPY_PACKAGE, COVERAGEPY_VERSION, COVERAGEPY_VERSION)
    if status == "complete" and observed != exact:
        raise _error(
            "Coverage.py receipt.distribution",
            "complete measurement requires exact runtime identity",
        )
    if status == "indeterminate" and not (
        observed == (None, None, None)
        or all(isinstance(item, str) for item in observed)
    ):
        raise _error(
            "Coverage.py receipt.distribution",
            "indeterminate identity must be all null or all strings",
        )
    return distribution


def _validate_configuration(
    value: object,
    *,
    expected: Mapping[str, object],
) -> dict[str, Any]:
    configuration = _exact_keys(
        value,
        _CONFIGURATION_FIELDS,
        context="Coverage.py receipt.configuration",
    )
    if not _strict_equal(dict(expected), configuration):
        raise _error(
            "Coverage.py receipt.configuration",
            "does not match the fixed invocation",
        )
    return configuration


def _validate_target(
    value: object,
    *,
    expected: Mapping[str, object],
) -> dict[str, Any]:
    target = _exact_keys(
        value,
        _TARGET_FIELDS,
        context="Coverage.py receipt.target",
    )
    _relative_path(target["path"], context="Coverage.py receipt.target.path")
    if not isinstance(target["symbol"], str) or not target["symbol"]:
        raise _error(
            "Coverage.py receipt.target.symbol",
            "must be a non-empty string",
        )
    _sha256(
        target["source_sha256"],
        context="Coverage.py receipt.target.source_sha256",
    )
    _positive_lines(
        target["target_lines"],
        context="Coverage.py receipt.target.target_lines",
        allow_empty=False,
    )
    if not _strict_equal(dict(expected), target):
        raise _error(
            "Coverage.py receipt.target",
            "does not match invocation",
        )
    return target


def _validate_cost(value: object) -> dict[str, Any]:
    cost = _exact_keys(
        value,
        _COST_FIELDS,
        context="Coverage.py receipt.cost",
    )
    if cost["status"] != "measured" or cost["missing_reason"] is not None:
        raise _error(
            "Coverage.py receipt.cost",
            "must retain measured finite costs",
        )
    _finite_nonnegative(
        cost["wall_clock_seconds"],
        context="Coverage.py receipt.cost.wall_clock_seconds",
    )
    _finite_nonnegative(
        cost["cpu_seconds"],
        context="Coverage.py receipt.cost.cpu_seconds",
    )
    return cost


def _validate_statement_evidence(
    value: object,
    *,
    target_lines: list[int],
) -> dict[str, Any]:
    evidence = _exact_keys(
        value,
        _STATEMENT_FIELDS,
        context="Coverage.py receipt.statement_evidence",
    )
    executable = _positive_lines(
        evidence["executable"],
        context="Coverage.py receipt.statement_evidence.executable",
    )
    executed = _positive_lines(
        evidence["executed"],
        context="Coverage.py receipt.statement_evidence.executed",
    )
    missing = _positive_lines(
        evidence["missing"],
        context="Coverage.py receipt.statement_evidence.missing",
    )
    measured = _positive_lines(
        evidence["measured_lines"],
        context="Coverage.py receipt.statement_evidence.measured_lines",
    )
    target_executable = _positive_lines(
        evidence["target_executable"],
        context="Coverage.py receipt.statement_evidence.target_executable",
    )
    target_executed = _positive_lines(
        evidence["target_executed"],
        context="Coverage.py receipt.statement_evidence.target_executed",
    )
    target_missing = _positive_lines(
        evidence["target_missing"],
        context="Coverage.py receipt.statement_evidence.target_missing",
    )
    if not set(executed).issubset(executable):
        raise _error(
            "Coverage.py receipt.statement_evidence.executed",
            "must be a subset of executable",
        )
    if missing != sorted(set(executable) - set(executed)):
        raise _error(
            "Coverage.py receipt.statement_evidence.missing",
            "must equal executable minus executed",
        )
    if measured != executed:
        raise _error(
            "Coverage.py receipt.statement_evidence.measured_lines",
            "must equal executed lines",
        )
    expected_target_executable = sorted(
        set(executable) & set(target_lines)
    )
    expected_target_executed = sorted(set(executed) & set(target_lines))
    if target_executable != expected_target_executable:
        raise _error(
            "Coverage.py receipt.statement_evidence.target_executable",
            "is inconsistent with target",
        )
    if target_executed != expected_target_executed:
        raise _error(
            "Coverage.py receipt.statement_evidence.target_executed",
            "is inconsistent with target",
        )
    if target_missing != sorted(
        set(target_executable) - set(target_executed)
    ):
        raise _error(
            "Coverage.py receipt.statement_evidence.target_missing",
            "is inconsistent with target",
        )
    return evidence


def _validate_branch_stats(
    value: object,
    *,
    context: str,
) -> list[dict[str, int]]:
    if not isinstance(value, list):
        raise _error(context, "must be an array")
    normalized: list[dict[str, int]] = []
    for index, raw in enumerate(value):
        item = _exact_keys(
            raw,
            _BRANCH_STAT_FIELDS,
            context=f"{context}[{index}]",
        )
        line = item["line"]
        total = item["total_exits"]
        taken = item["taken_exits"]
        if (
            isinstance(line, bool)
            or not isinstance(line, int)
            or line <= 0
            or isinstance(total, bool)
            or not isinstance(total, int)
            or total < 0
            or isinstance(taken, bool)
            or not isinstance(taken, int)
            or taken < 0
            or taken > total
        ):
            raise _error(
                f"{context}[{index}]",
                "contains invalid branch statistics",
            )
        normalized.append(
            {
                "line": line,
                "total_exits": total,
                "taken_exits": taken,
            }
        )
    if normalized != sorted(normalized, key=lambda item: item["line"]):
        raise _error(context, "must be sorted by line")
    if len({item["line"] for item in normalized}) != len(normalized):
        raise _error(context, "contains duplicate lines")
    return normalized


def _validate_branch_evidence(
    value: object,
    *,
    target_lines: list[int],
) -> dict[str, Any]:
    evidence = _exact_keys(
        value,
        _BRANCH_FIELDS,
        context="Coverage.py receipt.branch_evidence",
    )
    if evidence["has_arcs"] is not True:
        raise _error(
            "Coverage.py receipt.branch_evidence.has_arcs",
            "must be true",
        )
    all_arcs = _arcs(
        evidence["all_arcs"],
        context="Coverage.py receipt.branch_evidence.all_arcs",
    )
    context_arcs = _arcs(
        evidence["context_arcs"],
        context="Coverage.py receipt.branch_evidence.context_arcs",
    )
    target_arcs = _arcs(
        evidence["target_arcs"],
        context="Coverage.py receipt.branch_evidence.target_arcs",
    )
    if not set(map(tuple, context_arcs)).issubset(
        set(map(tuple, all_arcs))
    ):
        raise _error(
            "Coverage.py receipt.branch_evidence.context_arcs",
            "must be a subset of all_arcs",
        )
    expected_target_arcs = [
        arc
        for arc in context_arcs
        if arc[0] in target_lines or arc[1] in target_lines
    ]
    if target_arcs != expected_target_arcs:
        raise _error(
            "Coverage.py receipt.branch_evidence.target_arcs",
            "is inconsistent with target",
        )
    stats = _validate_branch_stats(
        evidence["branch_stats"],
        context="Coverage.py receipt.branch_evidence.branch_stats",
    )
    target_stats = _validate_branch_stats(
        evidence["target_branch_stats"],
        context="Coverage.py receipt.branch_evidence.target_branch_stats",
    )
    if target_stats != [
        item for item in stats if item["line"] in target_lines
    ]:
        raise _error(
            "Coverage.py receipt.branch_evidence.target_branch_stats",
            "is inconsistent with target",
        )
    expected_missing = sum(
        item["total_exits"] - item["taken_exits"] for item in stats
    )
    expected_target_missing = sum(
        item["total_exits"] - item["taken_exits"]
        for item in target_stats
    )
    if evidence["missing_branch_count"] != expected_missing:
        raise _error(
            "Coverage.py receipt.branch_evidence.missing_branch_count",
            "is inconsistent with branch_stats",
        )
    if evidence["target_missing_branch_count"] != expected_target_missing:
        raise _error(
            "Coverage.py receipt.branch_evidence.target_missing_branch_count",
            "is inconsistent with target_branch_stats",
        )
    if evidence["missing_branch_arcs"] is not None:
        raise _error(
            "Coverage.py receipt.branch_evidence.missing_branch_arcs",
            "must remain unavailable",
        )
    if (
        evidence["missing_branch_arc_identity_status"]
        != "unavailable-public-api"
    ):
        raise _error(
            "Coverage.py receipt.branch_evidence."
            "missing_branch_arc_identity_status",
            "is unsupported",
        )
    return evidence


def _validate_context_evidence(
    value: object,
    *,
    context_id: str,
    statement: Mapping[str, object],
    branch: Mapping[str, object],
) -> dict[str, Any]:
    evidence = _exact_keys(
        value,
        _CONTEXT_EVIDENCE_FIELDS,
        context="Coverage.py receipt.context_evidence",
    )
    measured_contexts = evidence["measured_contexts"]
    if (
        not isinstance(measured_contexts, list)
        or measured_contexts != [context_id]
    ):
        raise _error(
            "Coverage.py receipt.context_evidence.measured_contexts",
            "must contain only the exact selector context",
        )
    contexts_by_lineno = evidence["contexts_by_lineno"]
    if not isinstance(contexts_by_lineno, list):
        raise _error(
            "Coverage.py receipt.context_evidence.contexts_by_lineno",
            "must be an array",
        )
    normalized: list[dict[str, object]] = []
    for index, raw in enumerate(contexts_by_lineno):
        item = _exact_keys(
            raw,
            _CONTEXT_LINE_FIELDS,
            context=(
                "Coverage.py receipt.context_evidence."
                f"contexts_by_lineno[{index}]"
            ),
        )
        line = item["line"]
        contexts = item["contexts"]
        if (
            isinstance(line, bool)
            or not isinstance(line, int)
            or line <= 0
        ):
            raise _error(
                "Coverage.py receipt.context_evidence."
                f"contexts_by_lineno[{index}].line",
                "must be positive",
            )
        if contexts != [context_id]:
            raise _error(
                "Coverage.py receipt.context_evidence."
                f"contexts_by_lineno[{index}].contexts",
                "contains cross-contamination",
            )
        normalized.append({"line": line, "contexts": contexts})
    if normalized != sorted(normalized, key=lambda item: item["line"]):
        raise _error(
            "Coverage.py receipt.context_evidence.contexts_by_lineno",
            "must be sorted by line",
        )
    if len({item["line"] for item in normalized}) != len(normalized):
        raise _error(
            "Coverage.py receipt.context_evidence.contexts_by_lineno",
            "contains duplicate lines",
        )
    lines = _positive_lines(
        evidence["lines"],
        context="Coverage.py receipt.context_evidence.lines",
    )
    arcs = _arcs(
        evidence["arcs"],
        context="Coverage.py receipt.context_evidence.arcs",
    )
    if evidence["query_context"] != context_id:
        raise _error(
            "Coverage.py receipt.context_evidence.query_context",
            "does not match invocation",
        )
    if lines != statement["measured_lines"]:
        raise _error(
            "Coverage.py receipt.context_evidence.lines",
            "must equal measured statement lines",
        )
    if [item["line"] for item in normalized] != lines:
        raise _error(
            "Coverage.py receipt.context_evidence.contexts_by_lineno",
            "must bind every measured line exactly once",
        )
    if arcs != branch["context_arcs"]:
        raise _error(
            "Coverage.py receipt.context_evidence.arcs",
            "must equal context arcs",
        )
    if evidence["partition_valid"] is not True:
        raise _error(
            "Coverage.py receipt.context_evidence.partition_valid",
            "must be true",
        )
    return evidence


def validate_coverage_receipt(
    document: object,
    *,
    expected_binding: str,
    expected_target: Mapping[str, object],
    expected_context_id: str,
    expected_configuration: Mapping[str, object],
    expected_manifest_sha256: str,
) -> dict[str, Any]:
    """Validate exact structure, public-safe evidence, relations, and digest."""

    receipt = _exact_keys(
        document,
        _ROOT_FIELDS,
        context="Coverage.py receipt",
    )
    if receipt["schema_version"] != COVERAGE_RECEIPT_SCHEMA_VERSION:
        raise _error(
            "Coverage.py receipt.schema_version",
            "is unsupported",
        )
    if receipt["binding"] != expected_binding:
        raise _error(
            "Coverage.py receipt.binding",
            "does not match invocation",
        )
    producer = _exact_keys(
        receipt["producer"],
        _PRODUCER_FIELDS,
        context="Coverage.py receipt.producer",
    )
    if producer != {
        "name": COVERAGE_PRODUCER_NAME,
        "version": __version__,
    }:
        raise _error("Coverage.py receipt.producer", "is unsupported")
    status = receipt["measurement_status"]
    if status not in {"complete", "indeterminate"}:
        raise _error(
            "Coverage.py receipt.measurement_status",
            "is unsupported",
        )
    _validate_distribution(
        receipt["distribution"],
        expected_manifest_sha256=expected_manifest_sha256,
        status=status,
    )
    _validate_configuration(
        receipt["configuration"],
        expected=expected_configuration,
    )
    target = _validate_target(
        receipt["target"],
        expected=expected_target,
    )
    context = _exact_keys(
        receipt["context"],
        _CONTEXT_FIELDS,
        context="Coverage.py receipt.context",
    )
    if context != {
        "id": expected_context_id,
        "strategy": "static-selector-context-v1",
    }:
        raise _error(
            "Coverage.py receipt.context",
            "does not match invocation",
        )
    _validate_cost(receipt["cost"])

    if status == "indeterminate":
        measurement_error = receipt["measurement_error"]
        if (
            not isinstance(measurement_error, str)
            or not _STABLE_ERROR.fullmatch(measurement_error)
        ):
            raise _error(
                "Coverage.py receipt.measurement_error",
                "must be a stable non-empty diagnostic code",
            )
        for field in (
            "measured_files",
            "statement_evidence",
            "branch_evidence",
            "context_evidence",
        ):
            if receipt[field] is not None:
                raise _error(
                    f"Coverage.py receipt.{field}",
                    "must be null for indeterminate measurement",
                )
    else:
        if receipt["measurement_error"] is not None:
            raise _error(
                "Coverage.py receipt.measurement_error",
                "must be null for complete measurement",
            )
        measured_files = receipt["measured_files"]
        if not isinstance(measured_files, list) or not measured_files:
            raise _error(
                "Coverage.py receipt.measured_files",
                "must be a non-empty array",
            )
        for index, path in enumerate(measured_files):
            _relative_path(
                path,
                context=f"Coverage.py receipt.measured_files[{index}]",
            )
        if measured_files != sorted(set(measured_files)):
            raise _error(
                "Coverage.py receipt.measured_files",
                "must be sorted and unique",
            )
        if measured_files != [target["path"]]:
            raise _error(
                "Coverage.py receipt.measured_files",
                "must contain only the exact target path",
            )
        statement = _validate_statement_evidence(
            receipt["statement_evidence"],
            target_lines=target["target_lines"],
        )
        branch = _validate_branch_evidence(
            receipt["branch_evidence"],
            target_lines=target["target_lines"],
        )
        _validate_context_evidence(
            receipt["context_evidence"],
            context_id=expected_context_id,
            statement=statement,
            branch=branch,
        )

    recorded = _sha256(
        receipt["coverage_sha256"],
        context="Coverage.py receipt.coverage_sha256",
    )
    computed = compute_coverage_receipt_sha256(receipt)
    if recorded != computed:
        raise _error(
            "Coverage.py receipt.coverage_sha256",
            "digest mismatch",
        )
    return deepcopy(receipt)


def load_coverage_receipt(
    path: Path,
    **expected: object,
) -> dict[str, Any]:
    """Load one bounded regular non-link strict-JSON measurement receipt."""

    try:
        metadata = path.lstat()
    except OSError as exc:
        raise _error(
            "Coverage.py receipt path",
            "cannot be inspected",
        ) from exc
    if path.is_symlink() or not stat.S_ISREG(metadata.st_mode):
        raise _error(
            "Coverage.py receipt path",
            "must be a regular non-link file",
        )
    if metadata.st_size <= 0 or metadata.st_size > _MAX_RECEIPT_BYTES:
        raise _error(
            "Coverage.py receipt path",
            "is outside the size limit",
        )
    try:
        document = load_report(path)
    except ReportError:
        raise
    return validate_coverage_receipt(document, **expected)


def _safe_relative_path(raw: str, *, context: str) -> Path:
    value = _relative_path(raw, context=context)
    return Path(value)


def _target_source(
    raw_path: str,
    expected_sha256: str,
) -> tuple[Path, str]:
    relative = _safe_relative_path(
        raw_path,
        context="Coverage.py target path",
    )
    root = Path.cwd().resolve()
    candidate = root
    final_metadata: os.stat_result | None = None
    try:
        for index, part in enumerate(relative.parts):
            candidate = candidate / part
            metadata = candidate.lstat()
            if stat.S_ISLNK(metadata.st_mode):
                raise _error(
                    "Coverage.py target path",
                    "symbolic-link components are forbidden",
                )
            if index < len(relative.parts) - 1:
                if not stat.S_ISDIR(metadata.st_mode):
                    raise _error(
                        "Coverage.py target path",
                        "ancestor components must be directories",
                    )
            else:
                final_metadata = metadata
    except CoveragePyProbeError:
        raise
    except OSError as exc:
        raise _error(
            "Coverage.py target path",
            "cannot be inspected",
        ) from exc
    if final_metadata is None or not stat.S_ISREG(final_metadata.st_mode):
        raise _error(
            "Coverage.py target path",
            "must be a regular non-link file",
        )
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
        source_bytes = resolved.read_bytes()
    except (OSError, ValueError) as exc:
        raise _error(
            "Coverage.py target path",
            "cannot be resolved inside the working directory",
        ) from exc
    import hashlib

    if hashlib.sha256(source_bytes).hexdigest() != expected_sha256:
        raise _error(
            "Coverage.py target source_sha256",
            "does not match source bytes",
        )
    return resolved, relative.as_posix()


def _output_destination(raw: str) -> Path:
    relative = _safe_relative_path(raw, context="Coverage.py output")
    if relative.as_posix() != COVERAGE_OUTPUT_BASENAME:
        raise _error(
            "Coverage.py output",
            f"must equal {COVERAGE_OUTPUT_BASENAME!r}",
        )
    destination = Path.cwd() / relative
    try:
        destination.lstat()
    except FileNotFoundError:
        return destination
    except OSError as exc:
        raise _error(
            "Coverage.py output",
            "cannot be inspected",
        ) from exc
    raise _error("Coverage.py output", "must not already exist")


def _write_coverage(destination: Path, document: dict[str, Any]) -> None:
    data = canonical_json(document) + b"\n"
    if len(data) > _MAX_RECEIPT_BYTES:
        raise _error("Coverage.py receipt", "exceeds the size limit")
    descriptor = os.open(
        destination,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o600,
    )
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


def _configuration(context_id: str) -> dict[str, object]:
    return {
        "data_file": None,
        "auto_data": False,
        "timid": True,
        "branch": True,
        "config_file": False,
        "source_dirs": ["src"],
        "concurrency": None,
        "check_preimported": False,
        "context": context_id,
        "messages": False,
        "plugins": [],
        "auto_start": False,
        "subprocess_measurement": False,
        "network_during_measurement": False,
    }


def _distribution(
    *,
    distribution_name: str | None,
    distribution_version: str | None,
    module_version: str | None,
) -> dict[str, object]:
    return {
        "manifest_sha256": COVERAGEPY_MANIFEST_SHA256,
        "package": COVERAGEPY_PACKAGE,
        "expected_version": COVERAGEPY_VERSION,
        "observed_distribution_name": distribution_name,
        "observed_distribution_version": distribution_version,
        "observed_module_version": module_version,
    }


def _indeterminate_receipt(
    *,
    binding: str,
    distribution: Mapping[str, object],
    configuration: Mapping[str, object],
    target: Mapping[str, object],
    context_id: str,
    code: str,
    wall_seconds: float,
    cpu_seconds: float,
) -> dict[str, Any]:
    return build_coverage_receipt(
        binding=binding,
        distribution=distribution,
        configuration=configuration,
        target=target,
        context={
            "id": context_id,
            "strategy": "static-selector-context-v1",
        },
        measurement_status="indeterminate",
        measurement_error=code,
        measured_files=None,
        statement_evidence=None,
        branch_evidence=None,
        context_evidence=None,
        cost={
            "status": "measured",
            "wall_clock_seconds": wall_seconds,
            "cpu_seconds": cpu_seconds,
            "missing_reason": None,
        },
    )


def _normalize_arcs(value: object) -> list[list[int]]:
    if value is None:
        return []
    return sorted([[int(left), int(right)] for left, right in value])


def _measure(
    *,
    suite: unittest.TestSuite,
    args: argparse.Namespace,
    target_path: Path,
    target_path_text: str,
    target: Mapping[str, object],
    context_id: str,
    configuration: Mapping[str, object],
    binding: str,
) -> tuple[unittest.TestResult, dict[str, Any]]:
    wall_start = time.perf_counter()
    cpu_start = time.process_time()
    distribution = _distribution(
        distribution_name=None,
        distribution_version=None,
        module_version=None,
    )
    unavailable: str | None = None
    coverage_module: Any | None = None

    if any(key.startswith("COVERAGE_") for key in os.environ):
        unavailable = "ambient_coverage_environment"
    else:
        try:
            import coverage as imported_coverage
        except ImportError:
            unavailable = "missing_optional_dependency"
        else:
            coverage_module = imported_coverage
            try:
                distribution_name = importlib.metadata.metadata(
                    COVERAGEPY_PACKAGE
                )["Name"]
                distribution_version = importlib.metadata.version(
                    COVERAGEPY_PACKAGE
                )
                module_version = str(imported_coverage.__version__)
            except (
                importlib.metadata.PackageNotFoundError,
                KeyError,
                TypeError,
                ValueError,
            ):
                unavailable = "coveragepy_identity_unavailable"
            else:
                distribution = _distribution(
                    distribution_name=distribution_name,
                    distribution_version=distribution_version,
                    module_version=module_version,
                )
                if (
                    distribution_name != COVERAGEPY_PACKAGE
                    or distribution_version != COVERAGEPY_VERSION
                    or module_version != COVERAGEPY_VERSION
                ):
                    unavailable = "coveragepy_identity_mismatch"
                elif imported_coverage.Coverage.current() is not None:
                    unavailable = "coveragepy_already_active"

    runner = unittest.TextTestRunner(
        stream=__import__("io").StringIO(),
        verbosity=args.verbosity,
        failfast=False,
        buffer=True,
        resultclass=_ReceiptTestResult,
    )

    if unavailable is not None or coverage_module is None:
        result = runner.run(suite)
        receipt = _indeterminate_receipt(
            binding=binding,
            distribution=distribution,
            configuration=configuration,
            target=target,
            context_id=context_id,
            code=unavailable or "coveragepy_unavailable",
            wall_seconds=time.perf_counter() - wall_start,
            cpu_seconds=time.process_time() - cpu_start,
        )
        return result, receipt

    try:
        cov = coverage_module.Coverage(
            data_file=None,
            auto_data=False,
            timid=True,
            branch=True,
            config_file=False,
            source_dirs=[str(target_path.parent)],
            concurrency=None,
            check_preimported=False,
            context=context_id,
            messages=False,
            plugins=(),
        )
        with cov.collect():
            result = runner.run(suite)
        data = cov.get_data()
        target_filename = str(target_path)
        measured_absolute = sorted(data.measured_files())
        if measured_absolute != [target_filename]:
            raise _error(
                "Coverage.py measured files",
                "do not match the exact target",
            )
        measured_contexts = sorted(data.measured_contexts())
        contexts_by_lineno_raw = data.contexts_by_lineno(target_filename)
        all_lines = sorted(data.lines(target_filename) or [])
        all_arcs = _normalize_arcs(data.arcs(target_filename))
        data.set_query_context(context_id)
        context_lines = sorted(data.lines(target_filename) or [])
        context_arcs = _normalize_arcs(data.arcs(target_filename))
        _, executable, excluded, missing, _ = cov.analysis2(target_filename)
        if excluded:
            raise _error(
                "Coverage.py analysis2",
                "unexpected excluded lines",
            )
        executable_lines = sorted(executable)
        missing_lines = sorted(missing)
        branch_stats_raw = cov.branch_stats(target_filename)
        branch_stats = [
            {
                "line": int(line),
                "total_exits": int(values[0]),
                "taken_exits": int(values[1]),
            }
            for line, values in sorted(branch_stats_raw.items())
        ]
        target_lines = list(target["target_lines"])
        target_arcs = [
            arc
            for arc in context_arcs
            if arc[0] in target_lines or arc[1] in target_lines
        ]
        target_branch_stats = [
            item for item in branch_stats if item["line"] in target_lines
        ]
        contexts_by_lineno = [
            {"line": int(line), "contexts": sorted(contexts)}
            for line, contexts in sorted(contexts_by_lineno_raw.items())
        ]
        partition_valid = (
            measured_contexts == [context_id]
            and all(
                item["contexts"] == [context_id]
                for item in contexts_by_lineno
            )
            and context_lines == all_lines
            and context_arcs == all_arcs
        )
        statement_evidence = {
            "executable": executable_lines,
            "executed": context_lines,
            "missing": missing_lines,
            "measured_lines": context_lines,
            "target_executable": sorted(
                set(executable_lines) & set(target_lines)
            ),
            "target_executed": sorted(
                set(context_lines) & set(target_lines)
            ),
            "target_missing": sorted(
                (set(executable_lines) & set(target_lines))
                - set(context_lines)
            ),
        }
        branch_evidence = {
            "has_arcs": data.has_arcs(),
            "all_arcs": all_arcs,
            "context_arcs": context_arcs,
            "target_arcs": target_arcs,
            "branch_stats": branch_stats,
            "target_branch_stats": target_branch_stats,
            "missing_branch_count": sum(
                item["total_exits"] - item["taken_exits"]
                for item in branch_stats
            ),
            "target_missing_branch_count": sum(
                item["total_exits"] - item["taken_exits"]
                for item in target_branch_stats
            ),
            "missing_branch_arcs": None,
            "missing_branch_arc_identity_status": (
                "unavailable-public-api"
            ),
        }
        context_evidence = {
            "measured_contexts": measured_contexts,
            "contexts_by_lineno": contexts_by_lineno,
            "query_context": context_id,
            "lines": context_lines,
            "arcs": context_arcs,
            "partition_valid": partition_valid,
        }
        receipt = build_coverage_receipt(
            binding=binding,
            distribution=distribution,
            configuration=configuration,
            target=target,
            context={
                "id": context_id,
                "strategy": "static-selector-context-v1",
            },
            measurement_status="complete",
            measurement_error=None,
            measured_files=[target_path_text],
            statement_evidence=statement_evidence,
            branch_evidence=branch_evidence,
            context_evidence=context_evidence,
            cost={
                "status": "measured",
                "wall_clock_seconds": time.perf_counter() - wall_start,
                "cpu_seconds": time.process_time() - cpu_start,
                "missing_reason": None,
            },
        )
        validate_coverage_receipt(
            receipt,
            expected_binding=binding,
            expected_target=target,
            expected_context_id=context_id,
            expected_configuration=configuration,
            expected_manifest_sha256=COVERAGEPY_MANIFEST_SHA256,
        )
        return result, receipt
    except Exception:
        if "result" not in locals():
            result = runner.run(suite)
        receipt = _indeterminate_receipt(
            binding=binding,
            distribution=distribution,
            configuration=configuration,
            target=target,
            context_id=context_id,
            code="coveragepy_tool_error",
            wall_seconds=time.perf_counter() - wall_start,
            cpu_seconds=time.process_time() - cpu_start,
        )
        return result, receipt


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m deltawitness.coveragepy_probe",
        description=(
            "Run one exact unittest selector and emit typed outcome plus "
            "Coverage.py receipts."
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
    parser.add_argument("--context-id", required=True)
    parser.add_argument("--coverage-output", required=True)
    return parser


def run_probe(args: argparse.Namespace) -> int:
    receipt_destination, binding = _destination_from_environment()
    coverage_destination = _output_destination(args.coverage_output)
    source_sha256 = _sha256(
        args.source_sha256,
        context="Coverage.py source_sha256",
    )
    target_lines = sorted(set(args.target_line))
    if not target_lines or any(line <= 0 for line in target_lines):
        raise _error("Coverage.py target lines", "must be positive")
    if not isinstance(args.target_symbol, str) or not args.target_symbol:
        raise _error("Coverage.py target symbol", "must be non-empty")
    if (
        not isinstance(args.context_id, str)
        or not args.context_id
        or len(args.context_id) > 512
    ):
        raise _error("Coverage.py context", "is invalid")
    target_path, target_path_text = _target_source(
        args.target_path,
        source_sha256,
    )
    target = {
        "path": target_path_text,
        "symbol": args.target_symbol,
        "source_sha256": source_sha256,
        "target_lines": target_lines,
    }
    configuration = _configuration(args.context_id)
    suite = _load_suite(args)
    result, coverage_receipt = _measure(
        suite=suite,
        args=args,
        target_path=target_path,
        target_path_text=target_path_text,
        target=target,
        context_id=args.context_id,
        configuration=configuration,
        binding=binding,
    )
    if not isinstance(result, _ReceiptTestResult):
        raise ReceiptError(
            "unexpected_result",
            "unittest returned an unexpected result type",
        )
    counts = result.receipt_counts()
    outcome = classify_counts(counts)
    _write(
        receipt_destination,
        binding,
        outcome=outcome,
        counts=counts,
    )
    _write_coverage(coverage_destination, coverage_receipt)
    if outcome == "passed":
        return 0
    if outcome == "test_failure":
        return 1
    return 2


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        return run_probe(args)
    except (CoveragePyProbeError, ReceiptError) as exc:
        code = getattr(exc, "code", "coveragepy_probe_error")
        print(
            f"DeltaWitness Coverage.py probe error: {code}",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "COVERAGE_OUTPUT_BASENAME",
    "COVERAGE_PRODUCER_NAME",
    "COVERAGE_RECEIPT_SCHEMA_VERSION",
    "CoveragePyProbeError",
    "build_coverage_receipt",
    "compute_coverage_receipt_sha256",
    "load_coverage_receipt",
    "validate_coverage_receipt",
]
