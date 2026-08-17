"""Claim-scoped Coverage.py statement and branch baseline for DW-001.

The runner executes only the exact project-owned candidate source and selector
profiles frozen by the claim-scoped mutation plan. Each child emits a typed
unittest outcome receipt and a strict Coverage.py public-API measurement
receipt bound to one exact static selector context.

Complete but preregistration-divergent evidence remains a valid negative
result. Missing, ambiguous, malformed, substituted, contradictory, or
aggregate-inconsistent evidence fails closed or remains explicitly
indeterminate according to the frozen contract.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import math
from pathlib import Path
import platform
import stat
import tempfile
from typing import Any, Mapping, Sequence

from . import __version__
from . import _dw001_statement_coverage as _statement
from . import _dw001_weak_proxy as _weak_proxy
from .coveragepy_contract import (
    COVERAGEPY_MANIFEST_SHA256,
    COVERAGEPY_PACKAGE,
    COVERAGEPY_VERSION,
    build_coveragepy_distribution_manifest,
    verify_coveragepy_distribution_manifest_document,
)
from .coveragepy_probe import (
    COVERAGE_OUTPUT_BASENAME,
    COVERAGE_PRODUCER_NAME,
    COVERAGE_RECEIPT_SCHEMA_VERSION,
    CoveragePyProbeError,
    build_coverage_receipt,
    load_coverage_receipt,
    validate_coverage_receipt,
)
from .dw001_statement_coverage import (
    verify_claim_scoped_statement_coverage_document,
)
from .errors import DeltaWitnessError, ReportError
from .execution import run_command
from .receipt import build_receipt_document, validate_receipt_document
from .reporting import load_report, sha256_document


RESULT_SCHEMA_VERSION = "deltawitness.dw001-coveragepy-baseline-result.v1"
RESULT_ID = "DW-001-COVERAGEPY-BASELINE-RESULT-V1"
ADAPTER_ID = "coveragepy-public-api-v1"
MUTATION_RESULT_SEMANTIC_SHA256 = (
    "9e101bca85fd630bf5bdb2a6030d9fdab93eb3eac54b03f4aab99012c28086b6"
)
STDLIB_STATEMENT_RESULT_SEMANTIC_SHA256 = (
    "353e887ccb43561f1a0749e7948dd40bd7019534e93b5dca5b11ea16d49f68c6"
)

_BINDING_SCHEMA_VERSION = (
    "deltawitness.dw001-coveragepy-baseline-invocation.v1"
)
_STRONG_PROFILE_ID = "strong-authorization-oracle-v1"
_WEAK_PROFILE_ID = "weak-boolean-proxy-v1"
_TARGET_PATH = "src/access.py"
_TARGET_SYMBOL = "is_admin"
_MAX_RESULT_BYTES = 2_000_000

_ROOT_FIELDS = {
    "schema_version",
    "study_id",
    "result_id",
    "partition",
    "plan_sha256",
    "catalog_sha256",
    "mutation_result_semantic_sha256",
    "stdlib_statement_result_semantic_sha256",
    "distribution_manifest_sha256",
    "created_at",
    "runtime",
    "adapter",
    "distribution",
    "configuration",
    "source",
    "profiles",
    "comparison",
    "analysis",
    "policy",
    "cost",
    "semantic_sha256",
    "report_sha256",
}
_RUNTIME_FIELDS = {
    "tool_version",
    "python_implementation",
    "python_version",
    "platform_system",
}
_ADAPTER_FIELDS = {
    "id",
    "version",
    "coverage_receipt_schema_version",
    "coverage_producer",
    "public_api_only",
    "context_strategy",
}
_SOURCE_FIELDS = {
    "source_id",
    "path",
    "symbol",
    "source_sha256",
    "ast_sha256",
    "target_id",
    "target_lines",
}
_SELECTOR_FIELDS = {
    "selector",
    "source_sha256",
    "test_sha256",
    "command",
    "context_id",
    "expected_observed",
    "observed",
    "outcome_concordant",
    "return_code",
    "timed_out",
    "duration_seconds",
    "stdout_sha256",
    "stderr_sha256",
    "invocation_binding",
    "receipt_sha256",
    "receipt_outcome",
    "receipt_producer",
    "receipt_counts",
    "observation_error",
    "coverage_status",
    "coverage_error",
    "coverage_receipt",
    "expected_target_executed",
    "statement_concordant",
    "branch_evidence_complete",
    "context_partition_valid",
    "concordant",
    "cost",
}
_SELECTOR_COST_FIELDS = {
    "status",
    "process_wall_seconds",
    "coverage_wall_seconds",
    "coverage_cpu_seconds",
    "missing_reason",
}
_PROFILE_FIELDS = {
    "order",
    "profile_id",
    "profile_role",
    "selectors",
    "expected_statement_union",
    "statement_union",
    "expected_statement_intersection",
    "statement_intersection",
    "arc_union",
    "arc_intersection",
    "all_selectors_passed",
    "context_partition_valid",
    "coverage_status",
    "concordant",
    "cost",
}
_PROFILE_COST_FIELDS = {
    "status",
    "command_count",
    "selector_count",
    "process_wall_seconds",
    "coverage_wall_seconds",
    "coverage_cpu_seconds",
    "missing_reason",
}
_ROOT_COST_FIELDS = {
    "status",
    "profile_count",
    "command_count",
    "selector_count",
    "process_wall_seconds",
    "coverage_wall_seconds",
    "coverage_cpu_seconds",
    "missing_reason",
}
_COMPARISON_FIELDS = {
    "expected_stdlib_statement_discriminates_profiles",
    "stdlib_statement_discriminates_profiles",
    "expected_coveragepy_statement_discriminates_profiles",
    "coveragepy_statement_discriminates_profiles",
    "expected_coveragepy_branch_discriminates_profiles",
    "coveragepy_branch_discriminates_profiles",
    "expected_mutation_discriminates_profiles",
    "mutation_discriminates_profiles",
    "expected_stdlib_and_coveragepy_statement_agree",
    "stdlib_and_coveragepy_statement_agree",
    "expected_coveragepy_branch_and_mutation_agree",
    "coveragepy_branch_and_mutation_agree",
    "expected_incremental_branch_signal_observed",
    "incremental_branch_signal_observed",
    "expected_incremental_mutation_signal_beyond_coveragepy_observed",
    "incremental_mutation_signal_beyond_coveragepy_observed",
    "concordant",
}
_ANALYSIS_FIELDS = {
    "status",
    "unexpected_selector_count",
    "unexpected_profile_count",
    "indeterminate_selector_count",
    "unexpected_profile_ids",
    "comparison_concordant",
}
_POLICY_FIELDS = {
    "quality_score",
    "headline_score",
    "universal_threshold",
    "merge_blocker_authorized",
    "ecological_inference_allowed",
    "holdout_selected",
    "primary_denominator_eligible",
    "coverage_superiority_claim_allowed",
    "mutation_superiority_claim_allowed",
}


class DW001CoveragePyBaselineError(DeltaWitnessError):
    """Raised when the fixed Coverage.py baseline contract cannot be met."""


def _error(context: str, message: str) -> DW001CoveragePyBaselineError:
    return DW001CoveragePyBaselineError(f"{context}: {message}")


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


def _difference_paths(
    expected: object,
    observed: object,
    *,
    path: str,
) -> list[str]:
    if type(expected) is not type(observed):
        return [f"{path}: type or value mismatch"]
    if isinstance(expected, dict):
        assert isinstance(observed, dict)
        errors: list[str] = []
        expected_keys = set(expected)
        observed_keys = set(observed)
        for key in sorted(expected_keys - observed_keys):
            errors.append(f"{path}.{key}: missing")
        for key in sorted(observed_keys - expected_keys):
            errors.append(f"{path}.{key}: unexpected")
        for key in sorted(expected_keys & observed_keys):
            errors.extend(
                _difference_paths(
                    expected[key],
                    observed[key],
                    path=f"{path}.{key}",
                )
            )
        return errors
    if isinstance(expected, list):
        assert isinstance(observed, list)
        errors = []
        if len(expected) != len(observed):
            errors.append(
                f"{path}: length mismatch; expected {len(expected)}, "
                f"observed {len(observed)}"
            )
        for index, (left, right) in enumerate(
            zip(expected, observed, strict=False)
        ):
            errors.extend(
                _difference_paths(
                    left,
                    right,
                    path=f"{path}[{index}]",
                )
            )
        return errors
    if expected != observed:
        return [f"{path}: value mismatch"]
    return []


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _finite_nonnegative(value: object, *, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _error(context, "must be a finite nonnegative number")
    numeric = float(value)
    if not math.isfinite(numeric) or numeric < 0.0:
        raise _error(context, "must be a finite nonnegative number")
    return numeric


def _round_cost(value: float) -> float:
    return round(value, 6)


def _configuration() -> dict[str, object]:
    return {
        "data_file": None,
        "auto_data": False,
        "timid": True,
        "branch": True,
        "config_file": False,
        "source_dirs": ["src"],
        "concurrency": None,
        "check_preimported": False,
        "context_strategy": "static-selector-context-v1",
        "messages": False,
        "plugins": [],
        "auto_start": False,
        "subprocess_measurement": False,
        "network_during_measurement": False,
    }


def _selector_configuration(context_id: str) -> dict[str, object]:
    base = _configuration()
    strategy = base.pop("context_strategy")
    assert strategy == "static-selector-context-v1"
    base["context"] = context_id
    return base


def _adapter() -> dict[str, object]:
    return {
        "id": ADAPTER_ID,
        "version": "1",
        "coverage_receipt_schema_version": COVERAGE_RECEIPT_SCHEMA_VERSION,
        "coverage_producer": COVERAGE_PRODUCER_NAME,
        "public_api_only": True,
        "context_strategy": "static-selector-context-v1",
    }


def _policy() -> dict[str, object]:
    return {
        "quality_score": None,
        "headline_score": None,
        "universal_threshold": None,
        "merge_blocker_authorized": False,
        "ecological_inference_allowed": False,
        "holdout_selected": False,
        "primary_denominator_eligible": False,
        "coverage_superiority_claim_allowed": False,
        "mutation_superiority_claim_allowed": False,
    }


def _context_id(profile_id: str, selector: str) -> str:
    return f"dw001-coveragepy-v1:{profile_id}:{selector}"


def _coverage_command(
    *,
    selector: str,
    source_sha256: str,
    target_lines: Sequence[int],
    context_id: str,
) -> list[str]:
    command = [
        "python",
        "-m",
        "deltawitness.coveragepy_probe",
        "--start-directory",
        "tests",
        "--verbosity",
        "0",
        "--test-name",
        selector,
        "--target-path",
        _TARGET_PATH,
        "--target-symbol",
        _TARGET_SYMBOL,
    ]
    for line in target_lines:
        command.extend(["--target-line", str(line)])
    command.extend(
        [
            "--source-sha256",
            source_sha256,
            "--context-id",
            context_id,
            "--coverage-output",
            COVERAGE_OUTPUT_BASENAME,
        ]
    )
    return command


def _invocation_binding(
    *,
    plan_sha256: str,
    catalog_sha256: str,
    mutation_result_semantic_sha256: str,
    stdlib_statement_result_semantic_sha256: str,
    profile_id: str,
    selector: str,
    source_sha256: str,
    test_sha256: str,
    target_id: str,
    target_lines: Sequence[int],
    context_id: str,
    command: Sequence[str],
) -> str:
    return sha256_document(
        {
            "schema_version": _BINDING_SCHEMA_VERSION,
            "result_id": RESULT_ID,
            "adapter_id": ADAPTER_ID,
            "distribution_manifest_sha256": COVERAGEPY_MANIFEST_SHA256,
            "plan_sha256": plan_sha256,
            "catalog_sha256": catalog_sha256,
            "mutation_result_semantic_sha256": (
                mutation_result_semantic_sha256
            ),
            "stdlib_statement_result_semantic_sha256": (
                stdlib_statement_result_semantic_sha256
            ),
            "profile_id": profile_id,
            "selector": selector,
            "source_sha256": source_sha256,
            "test_sha256": test_sha256,
            "target_id": target_id,
            "target_lines": list(target_lines),
            "context_id": context_id,
            "command": list(command),
            "observer": "outcome-receipt-v1",
            "coverage_receipt_schema_version": (
                COVERAGE_RECEIPT_SCHEMA_VERSION
            ),
            "coverage_producer": {
                "name": COVERAGE_PRODUCER_NAME,
                "version": __version__,
            },
        }
    )


def _source_view(
    plan: Mapping[str, object],
    catalog: Mapping[str, object],
) -> dict[str, object]:
    source = plan["source_scope"]
    target = catalog["target"]
    if not isinstance(source, dict) or not isinstance(target, dict):
        raise _error("Coverage.py source relation", "is malformed")
    return {
        "source_id": source["source_id"],
        "path": source["path"],
        "symbol": source["symbol"],
        "source_sha256": source["source_sha256"],
        "ast_sha256": source["ast_sha256"],
        "target_id": target["target_id"],
        "target_lines": _statement._target_lines(catalog),
    }


def _preflight(
    plan: object,
    catalog: object,
    mutation_result: object,
    stdlib_statement_result: object,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    normalized_plan, normalized_catalog, normalized_mutation = (
        _statement._preflight(plan, catalog, mutation_result)
    )
    valid, errors = verify_claim_scoped_statement_coverage_document(
        stdlib_statement_result,
        normalized_plan,
        normalized_catalog,
        normalized_mutation,
    )
    if not valid:
        raise _error(
            "Coverage.py stdlib statement preflight",
            "; ".join(errors),
        )
    if not isinstance(stdlib_statement_result, dict):
        raise _error(
            "Coverage.py stdlib statement preflight",
            "must be an object",
        )
    if (
        stdlib_statement_result.get("semantic_sha256")
        != STDLIB_STATEMENT_RESULT_SEMANTIC_SHA256
    ):
        raise _error(
            "Coverage.py stdlib statement semantic identity",
            "does not match the frozen result",
        )
    manifest = build_coveragepy_distribution_manifest()
    manifest_valid, manifest_errors = (
        verify_coveragepy_distribution_manifest_document(manifest)
    )
    if not manifest_valid:
        raise _error(
            "Coverage.py distribution manifest",
            "; ".join(manifest_errors),
        )
    if manifest.get("manifest_sha256") != COVERAGEPY_MANIFEST_SHA256:
        raise _error(
            "Coverage.py distribution manifest",
            "does not match the reviewed identity",
        )
    return (
        normalized_plan,
        normalized_catalog,
        normalized_mutation,
        stdlib_statement_result,
    )


def _classify_process(process: object) -> tuple[str, str | None]:
    if bool(getattr(process, "timed_out")):
        return "timeout", None
    receipt_error = getattr(process, "receipt_error")
    if receipt_error is not None:
        return "error", str(receipt_error)
    receipt_outcome = getattr(process, "receipt_outcome")
    return_code = getattr(process, "return_code")
    if receipt_outcome == "passed" and return_code == 0:
        return "pass", None
    if receipt_outcome == "test_failure" and return_code == 1:
        return "fail", None
    return "error", "receipt_exit_mismatch"


def _execute_selector(
    *,
    plan: Mapping[str, object],
    catalog: Mapping[str, object],
    mutation_result: Mapping[str, object],
    stdlib_statement_result: Mapping[str, object],
    profile_id: str,
    selector: str,
) -> dict[str, Any]:
    """Execute one exact candidate selector and load both typed receipts."""

    source_text = _weak_proxy.CANDIDATE_CODE
    source_sha256 = _statement._sha256_bytes(source_text.encode("utf-8"))
    source = plan["source_scope"]
    target = catalog["target"]
    if not isinstance(source, dict) or not isinstance(target, dict):
        raise _error("Coverage.py selector source relation", "is malformed")
    if source_sha256 != source["source_sha256"]:
        raise _error(
            "Coverage.py selector source_sha256",
            "does not match the frozen source",
        )
    target_lines = _statement._target_lines(catalog)
    test_bytes = _statement._test_bytes(selector)
    test_sha256 = _statement._sha256_bytes(test_bytes)
    context_id = _context_id(profile_id, selector)
    command = _coverage_command(
        selector=selector,
        source_sha256=source_sha256,
        target_lines=target_lines,
        context_id=context_id,
    )
    binding = _invocation_binding(
        plan_sha256=str(plan["plan_sha256"]),
        catalog_sha256=str(catalog["catalog_sha256"]),
        mutation_result_semantic_sha256=str(
            mutation_result["semantic_sha256"]
        ),
        stdlib_statement_result_semantic_sha256=str(
            stdlib_statement_result["semantic_sha256"]
        ),
        profile_id=profile_id,
        selector=selector,
        source_sha256=source_sha256,
        test_sha256=test_sha256,
        target_id=str(target["target_id"]),
        target_lines=target_lines,
        context_id=context_id,
        command=command,
    )
    expected_target = {
        "path": _TARGET_PATH,
        "symbol": _TARGET_SYMBOL,
        "source_sha256": source_sha256,
        "target_lines": target_lines,
    }
    expected_configuration = _selector_configuration(context_id)

    with tempfile.TemporaryDirectory(
        prefix="deltawitness-coveragepy-baseline-"
    ) as directory:
        root = Path(directory)
        (root / "src").mkdir()
        (root / "tests").mkdir()
        (root / "src" / "access.py").write_text(
            source_text,
            encoding="utf-8",
        )
        (root / "tests" / "test_access.py").write_bytes(test_bytes)
        process = run_command(
            command,
            state=f"coveragepy:{profile_id}:{selector}",
            cwd=root,
            timeout_seconds=30,
            pass_env=(),
            include_output=False,
            observer="outcome-receipt-v1",
            receipt_binding=binding,
        )
        coverage_path = root / COVERAGE_OUTPUT_BASENAME
        coverage_receipt: dict[str, Any] | None = None
        coverage_error: str | None = None
        if coverage_path.exists():
            try:
                coverage_receipt = load_coverage_receipt(
                    coverage_path,
                    expected_binding=binding,
                    expected_target=expected_target,
                    expected_context_id=context_id,
                    expected_configuration=expected_configuration,
                    expected_manifest_sha256=COVERAGEPY_MANIFEST_SHA256,
                )
            except (CoveragePyProbeError, ReportError, DeltaWitnessError):
                coverage_error = "invalid_coverage_receipt"
        else:
            coverage_error = (
                "timeout"
                if process.timed_out
                else "missing_coverage_receipt"
            )
        data_files = sorted(
            path.name for path in root.glob(".coverage*") if path.exists()
        )
        if data_files:
            coverage_receipt = None
            coverage_error = "unexpected_coverage_data_file"

    observed, observation_error = _classify_process(process)
    if coverage_receipt is not None:
        measurement_status = coverage_receipt["measurement_status"]
        measurement_error = coverage_receipt["measurement_error"]
        if measurement_status == "complete":
            coverage_error = None
        else:
            coverage_error = str(measurement_error)
    return {
        "selector": selector,
        "source_sha256": source_sha256,
        "test_sha256": test_sha256,
        "command": command,
        "context_id": context_id,
        "observed": observed,
        "return_code": process.return_code,
        "timed_out": process.timed_out,
        "duration_seconds": process.duration_seconds,
        "stdout_sha256": process.stdout_sha256,
        "stderr_sha256": process.stderr_sha256,
        "invocation_binding": binding,
        "receipt_sha256": process.receipt_sha256,
        "receipt_outcome": process.receipt_outcome,
        "receipt_producer": process.receipt_producer,
        "receipt_counts": process.receipt_counts,
        "observation_error": observation_error,
        "coverage_receipt": coverage_receipt,
        "coverage_error": coverage_error,
    }


def _selector_status(raw: Mapping[str, object]) -> str:
    observed = raw.get("observed")
    if observed == "fail":
        return "candidate_invalid"
    if observed != "pass":
        return "indeterminate"
    receipt = raw.get("coverage_receipt")
    if not isinstance(receipt, dict):
        return "indeterminate"
    if receipt.get("measurement_status") != "complete":
        return "indeterminate"
    return "complete"


def _selector_cost(raw: Mapping[str, object]) -> dict[str, object]:
    process_wall = _finite_nonnegative(
        raw.get("duration_seconds"),
        context="Coverage.py selector.duration_seconds",
    )
    receipt = raw.get("coverage_receipt")
    if isinstance(receipt, dict):
        cost = receipt.get("cost")
        if not isinstance(cost, dict):
            raise _error("Coverage.py selector receipt.cost", "must be an object")
        coverage_wall = _finite_nonnegative(
            cost.get("wall_clock_seconds"),
            context="Coverage.py selector coverage wall cost",
        )
        coverage_cpu = _finite_nonnegative(
            cost.get("cpu_seconds"),
            context="Coverage.py selector coverage CPU cost",
        )
        return {
            "status": "measured",
            "process_wall_seconds": _round_cost(process_wall),
            "coverage_wall_seconds": _round_cost(coverage_wall),
            "coverage_cpu_seconds": _round_cost(coverage_cpu),
            "missing_reason": None,
        }
    return {
        "status": "partial",
        "process_wall_seconds": _round_cost(process_wall),
        "coverage_wall_seconds": None,
        "coverage_cpu_seconds": None,
        "missing_reason": "coverage_receipt_unavailable",
    }


def _enrich_selector(
    raw: Mapping[str, object],
    *,
    expected_target_executed: list[int],
) -> dict[str, Any]:
    status = _selector_status(raw)
    observed = raw.get("observed")
    outcome_concordant = observed == "pass"
    receipt = raw.get("coverage_receipt")
    statement_concordant = False
    branch_complete = False
    context_valid = False
    if status == "complete" and isinstance(receipt, dict):
        statement = receipt.get("statement_evidence")
        branch = receipt.get("branch_evidence")
        context = receipt.get("context_evidence")
        if (
            isinstance(statement, dict)
            and isinstance(branch, dict)
            and isinstance(context, dict)
        ):
            statement_concordant = (
                statement.get("target_executed")
                == expected_target_executed
            )
            branch_complete = branch.get("has_arcs") is True
            context_valid = context.get("partition_valid") is True
    coverage_error = raw.get("coverage_error")
    if status == "complete" and coverage_error is not None:
        raise _error(
            "Coverage.py selector.coverage_error",
            "must be null for complete evidence",
        )
    if status != "complete" and (
        not isinstance(coverage_error, str) or not coverage_error
    ):
        raise _error(
            "Coverage.py selector.coverage_error",
            "must identify indeterminate or invalid evidence",
        )
    return {
        **deepcopy(dict(raw)),
        "expected_observed": "pass",
        "outcome_concordant": outcome_concordant,
        "coverage_status": status,
        "expected_target_executed": list(expected_target_executed),
        "statement_concordant": statement_concordant,
        "branch_evidence_complete": branch_complete,
        "context_partition_valid": context_valid,
        "concordant": (
            outcome_concordant
            and statement_concordant
            and branch_complete
            and context_valid
        ),
        "cost": _selector_cost(raw),
    }


def _sets_for_profile(
    selectors: Sequence[Mapping[str, object]],
    *,
    field: str,
) -> tuple[list[Any], list[Any]]:
    values: list[set[Any]] = []
    for selector in selectors:
        receipt = selector["coverage_receipt"]
        assert isinstance(receipt, dict)
        if field == "target_executed":
            evidence = receipt["statement_evidence"]
            assert isinstance(evidence, dict)
            values.append(set(evidence[field]))
        else:
            evidence = receipt["branch_evidence"]
            assert isinstance(evidence, dict)
            values.append({tuple(arc) for arc in evidence[field]})
    union = set().union(*values)
    intersection = set.intersection(*values)
    if field == "target_executed":
        return sorted(union), sorted(intersection)
    return (
        [list(arc) for arc in sorted(union)],
        [list(arc) for arc in sorted(intersection)],
    )


def _aggregate_cost(
    selectors: Sequence[Mapping[str, object]],
    *,
    profile_count: int | None,
) -> dict[str, object]:
    costs = [selector["cost"] for selector in selectors]
    assert all(isinstance(cost, dict) for cost in costs)
    complete = all(cost["status"] == "measured" for cost in costs)
    process_wall = sum(float(cost["process_wall_seconds"]) for cost in costs)
    coverage_wall_values = [cost["coverage_wall_seconds"] for cost in costs]
    coverage_cpu_values = [cost["coverage_cpu_seconds"] for cost in costs]
    coverage_wall = (
        sum(float(value) for value in coverage_wall_values)
        if all(value is not None for value in coverage_wall_values)
        else None
    )
    coverage_cpu = (
        sum(float(value) for value in coverage_cpu_values)
        if all(value is not None for value in coverage_cpu_values)
        else None
    )
    result: dict[str, object] = {
        "status": "measured" if complete else "partial",
        "command_count": len(selectors),
        "selector_count": len(selectors),
        "process_wall_seconds": _round_cost(process_wall),
        "coverage_wall_seconds": (
            None if coverage_wall is None else _round_cost(coverage_wall)
        ),
        "coverage_cpu_seconds": (
            None if coverage_cpu is None else _round_cost(coverage_cpu)
        ),
        "missing_reason": (
            None if complete else "selector_cost_unavailable"
        ),
    }
    if profile_count is not None:
        result = {
            "status": result["status"],
            "profile_count": profile_count,
            "command_count": result["command_count"],
            "selector_count": result["selector_count"],
            "process_wall_seconds": result["process_wall_seconds"],
            "coverage_wall_seconds": result["coverage_wall_seconds"],
            "coverage_cpu_seconds": result["coverage_cpu_seconds"],
            "missing_reason": result["missing_reason"],
        }
    return result


def _build_profile(
    *,
    order: int,
    profile: Mapping[str, object],
    selectors: list[dict[str, Any]],
    expected_lines: list[int],
) -> dict[str, Any]:
    statuses = [selector["coverage_status"] for selector in selectors]
    all_passed = all(selector["observed"] == "pass" for selector in selectors)
    if any(status == "indeterminate" for status in statuses):
        coverage_status = "indeterminate"
    elif any(status == "candidate_invalid" for status in statuses):
        coverage_status = "candidate_invalid"
    else:
        coverage_status = "complete"
    if coverage_status == "complete":
        statement_union, statement_intersection = _sets_for_profile(
            selectors,
            field="target_executed",
        )
        arc_union, arc_intersection = _sets_for_profile(
            selectors,
            field="target_arcs",
        )
        context_partition_valid = all(
            selector["context_partition_valid"] is True
            for selector in selectors
        )
    else:
        statement_union = None
        statement_intersection = None
        arc_union = None
        arc_intersection = None
        context_partition_valid = False
    concordant = (
        coverage_status == "complete"
        and statement_union == expected_lines
        and statement_intersection == expected_lines
        and all_passed
        and context_partition_valid
        and all(selector["concordant"] is True for selector in selectors)
    )
    return {
        "order": order,
        "profile_id": profile["profile_id"],
        "profile_role": profile["profile_role"],
        "selectors": selectors,
        "expected_statement_union": list(expected_lines),
        "statement_union": statement_union,
        "expected_statement_intersection": list(expected_lines),
        "statement_intersection": statement_intersection,
        "arc_union": arc_union,
        "arc_intersection": arc_intersection,
        "all_selectors_passed": all_passed,
        "context_partition_valid": context_partition_valid,
        "coverage_status": coverage_status,
        "concordant": concordant,
        "cost": _aggregate_cost(selectors, profile_count=None),
    }


def _profile_by_id(
    profiles: Sequence[Mapping[str, object]],
    profile_id: str,
) -> Mapping[str, object]:
    matches = [
        profile
        for profile in profiles
        if profile.get("profile_id") == profile_id
    ]
    if len(matches) != 1:
        raise _error(
            "Coverage.py profiles",
            f"expected exactly one {profile_id!r} profile",
        )
    return matches[0]


def _stdlib_statement_discrimination(
    stdlib_statement_result: Mapping[str, object],
) -> bool | None:
    profiles = stdlib_statement_result.get("profiles")
    if not isinstance(profiles, list):
        raise _error(
            "Coverage.py stdlib statement profiles",
            "must be a list",
        )
    strong = _profile_by_id(profiles, _STRONG_PROFILE_ID)
    weak = _profile_by_id(profiles, _WEAK_PROFILE_ID)
    if (
        strong.get("coverage_status") != "complete"
        or weak.get("coverage_status") != "complete"
    ):
        return None
    return (
        strong.get("union_lines") != weak.get("union_lines")
        or strong.get("intersection_lines")
        != weak.get("intersection_lines")
    )


def _coveragepy_discrimination(
    profiles: Sequence[Mapping[str, object]],
    *,
    union_field: str,
    intersection_field: str,
) -> bool | None:
    strong = _profile_by_id(profiles, _STRONG_PROFILE_ID)
    weak = _profile_by_id(profiles, _WEAK_PROFILE_ID)
    if (
        strong.get("coverage_status") != "complete"
        or weak.get("coverage_status") != "complete"
    ):
        return None
    return (
        strong.get(union_field) != weak.get(union_field)
        or strong.get(intersection_field) != weak.get(intersection_field)
    )


def _derive_comparison(
    profiles: Sequence[Mapping[str, object]],
    mutation_result: Mapping[str, object],
    stdlib_statement_result: Mapping[str, object],
) -> dict[str, Any]:
    stdlib_statement = _stdlib_statement_discrimination(
        stdlib_statement_result
    )
    coveragepy_statement = _coveragepy_discrimination(
        profiles,
        union_field="statement_union",
        intersection_field="statement_intersection",
    )
    coveragepy_branch = _coveragepy_discrimination(
        profiles,
        union_field="arc_union",
        intersection_field="arc_intersection",
    )
    mutation = _statement._mutation_discrimination(mutation_result)
    stdlib_statement_agree = (
        None
        if stdlib_statement is None or coveragepy_statement is None
        else stdlib_statement == coveragepy_statement
    )
    branch_mutation_agree = (
        None
        if coveragepy_branch is None or mutation is None
        else coveragepy_branch == mutation
    )
    incremental_branch = (
        None
        if coveragepy_statement is None or coveragepy_branch is None
        else coveragepy_branch and not coveragepy_statement
    )
    incremental_mutation = (
        None
        if (
            coveragepy_statement is None
            or coveragepy_branch is None
            or mutation is None
        )
        else (
            mutation
            and not coveragepy_statement
            and not coveragepy_branch
        )
    )
    expected = {
        "expected_stdlib_statement_discriminates_profiles": False,
        "expected_coveragepy_statement_discriminates_profiles": False,
        "expected_coveragepy_branch_discriminates_profiles": False,
        "expected_mutation_discriminates_profiles": True,
        "expected_stdlib_and_coveragepy_statement_agree": True,
        "expected_coveragepy_branch_and_mutation_agree": False,
        "expected_incremental_branch_signal_observed": False,
        "expected_incremental_mutation_signal_beyond_coveragepy_observed": (
            True
        ),
    }
    observed = {
        "stdlib_statement_discriminates_profiles": stdlib_statement,
        "coveragepy_statement_discriminates_profiles": (
            coveragepy_statement
        ),
        "coveragepy_branch_discriminates_profiles": coveragepy_branch,
        "mutation_discriminates_profiles": mutation,
        "stdlib_and_coveragepy_statement_agree": stdlib_statement_agree,
        "coveragepy_branch_and_mutation_agree": branch_mutation_agree,
        "incremental_branch_signal_observed": incremental_branch,
        "incremental_mutation_signal_beyond_coveragepy_observed": (
            incremental_mutation
        ),
    }
    concordant = all(
        observed[key.removeprefix("expected_")] == value
        for key, value in expected.items()
    )
    return {**expected, **observed, "concordant": concordant}


def _derive_analysis(
    profiles: Sequence[Mapping[str, object]],
    comparison: Mapping[str, object],
) -> dict[str, Any]:
    selectors = [
        selector
        for profile in profiles
        for selector in profile.get("selectors", [])
    ]
    indeterminate = sum(
        selector.get("coverage_status") == "indeterminate"
        for selector in selectors
    )
    unexpected_selectors = sum(
        selector.get("coverage_status") != "indeterminate"
        and selector.get("concordant") is not True
        for selector in selectors
    )
    unexpected_profiles = [
        str(profile.get("profile_id"))
        for profile in profiles
        if profile.get("coverage_status") != "indeterminate"
        and profile.get("concordant") is not True
    ]
    comparison_indeterminate = any(
        comparison.get(field) is None
        for field in (
            "stdlib_statement_discriminates_profiles",
            "coveragepy_statement_discriminates_profiles",
            "coveragepy_branch_discriminates_profiles",
            "mutation_discriminates_profiles",
            "stdlib_and_coveragepy_statement_agree",
            "coveragepy_branch_and_mutation_agree",
            "incremental_branch_signal_observed",
            "incremental_mutation_signal_beyond_coveragepy_observed",
        )
    )
    if indeterminate or comparison_indeterminate:
        status = "indeterminate"
    elif (
        unexpected_selectors
        or unexpected_profiles
        or comparison.get("concordant") is not True
    ):
        status = "unexpected"
    else:
        status = "expected"
    return {
        "status": status,
        "unexpected_selector_count": unexpected_selectors,
        "unexpected_profile_count": len(unexpected_profiles),
        "indeterminate_selector_count": indeterminate,
        "unexpected_profile_ids": unexpected_profiles,
        "comparison_concordant": comparison.get("concordant") is True,
    }


def _semantic_view(document: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(document)
    normalized["created_at"] = None
    normalized["runtime"] = None
    normalized["semantic_sha256"] = None
    normalized["report_sha256"] = None
    root_cost = normalized.get("cost")
    if isinstance(root_cost, dict):
        for field in (
            "process_wall_seconds",
            "coverage_wall_seconds",
            "coverage_cpu_seconds",
        ):
            root_cost[field] = None
    profiles = normalized.get("profiles")
    if isinstance(profiles, list):
        for profile in profiles:
            if not isinstance(profile, dict):
                continue
            profile_cost = profile.get("cost")
            if isinstance(profile_cost, dict):
                for field in (
                    "process_wall_seconds",
                    "coverage_wall_seconds",
                    "coverage_cpu_seconds",
                ):
                    profile_cost[field] = None
            selectors = profile.get("selectors")
            if not isinstance(selectors, list):
                continue
            for selector in selectors:
                if not isinstance(selector, dict):
                    continue
                selector["duration_seconds"] = None
                selector["stdout_sha256"] = None
                selector["stderr_sha256"] = None
                selector_cost = selector.get("cost")
                if isinstance(selector_cost, dict):
                    for field in (
                        "process_wall_seconds",
                        "coverage_wall_seconds",
                        "coverage_cpu_seconds",
                    ):
                        selector_cost[field] = None
                receipt = selector.get("coverage_receipt")
                if isinstance(receipt, dict):
                    receipt_cost = receipt.get("cost")
                    if isinstance(receipt_cost, dict):
                        receipt_cost["wall_clock_seconds"] = None
                        receipt_cost["cpu_seconds"] = None
                    receipt["coverage_sha256"] = None
    return normalized


def compute_coveragepy_baseline_semantic_sha256(
    document: dict[str, Any],
) -> str:
    """Hash stable source, receipt, profile, comparison, and policy semantics."""

    if not isinstance(document, dict):
        raise _error("Coverage.py baseline result", "must be an object")
    return sha256_document(_semantic_view(document))


def compute_coveragepy_baseline_report_sha256(
    document: dict[str, Any],
) -> str:
    """Hash the complete result with only its report digest normalized."""

    if not isinstance(document, dict):
        raise _error("Coverage.py baseline result", "must be an object")
    normalized = deepcopy(document)
    normalized["report_sha256"] = None
    return sha256_document(normalized)


def run_claim_scoped_coveragepy_baseline(
    plan: object,
    catalog: object,
    mutation_result: object,
    stdlib_statement_result: object,
) -> dict[str, Any]:
    """Execute the exact frozen selector profiles and compare all four signals."""

    (
        normalized_plan,
        normalized_catalog,
        normalized_mutation,
        normalized_stdlib,
    ) = _preflight(
        plan,
        catalog,
        mutation_result,
        stdlib_statement_result,
    )
    profiles_source = normalized_plan["calibration_profiles"]
    if not isinstance(profiles_source, list) or len(profiles_source) != 2:
        raise _error(
            "Coverage.py profiles",
            "must contain exactly the two frozen profiles",
        )
    target_lines = _statement._target_lines(normalized_catalog)
    profiles: list[dict[str, Any]] = []
    for order, profile in enumerate(profiles_source, start=1):
        if not isinstance(profile, dict):
            raise _error("Coverage.py profile", "must be an object")
        raw_selectors = [
            _execute_selector(
                plan=normalized_plan,
                catalog=normalized_catalog,
                mutation_result=normalized_mutation,
                stdlib_statement_result=normalized_stdlib,
                profile_id=str(profile["profile_id"]),
                selector=str(selector),
            )
            for selector in profile["selectors"]
        ]
        selectors = [
            _enrich_selector(
                raw,
                expected_target_executed=target_lines,
            )
            for raw in raw_selectors
        ]
        profiles.append(
            _build_profile(
                order=order,
                profile=profile,
                selectors=selectors,
                expected_lines=target_lines,
            )
        )
    comparison = _derive_comparison(
        profiles,
        normalized_mutation,
        normalized_stdlib,
    )
    analysis = _derive_analysis(profiles, comparison)
    selectors = [
        selector
        for profile in profiles
        for selector in profile["selectors"]
    ]
    result: dict[str, Any] = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "study_id": "DW-001",
        "result_id": RESULT_ID,
        "partition": "development",
        "plan_sha256": normalized_plan["plan_sha256"],
        "catalog_sha256": normalized_catalog["catalog_sha256"],
        "mutation_result_semantic_sha256": normalized_mutation[
            "semantic_sha256"
        ],
        "stdlib_statement_result_semantic_sha256": normalized_stdlib[
            "semantic_sha256"
        ],
        "distribution_manifest_sha256": COVERAGEPY_MANIFEST_SHA256,
        "created_at": datetime.now(timezone.utc).isoformat().replace(
            "+00:00", "Z"
        ),
        "runtime": {
            "tool_version": __version__,
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
            "platform_system": platform.system(),
        },
        "adapter": _adapter(),
        "distribution": build_coveragepy_distribution_manifest(),
        "configuration": _configuration(),
        "source": _source_view(normalized_plan, normalized_catalog),
        "profiles": profiles,
        "comparison": comparison,
        "analysis": analysis,
        "policy": _policy(),
        "cost": _aggregate_cost(selectors, profile_count=2),
        "semantic_sha256": None,
        "report_sha256": None,
    }
    result["semantic_sha256"] = (
        compute_coveragepy_baseline_semantic_sha256(result)
    )
    result["report_sha256"] = compute_coveragepy_baseline_report_sha256(
        result
    )
    valid, errors = verify_claim_scoped_coveragepy_baseline_document(
        result,
        normalized_plan,
        normalized_catalog,
        normalized_mutation,
        normalized_stdlib,
    )
    if not valid:
        raise _error(
            "Coverage.py baseline self-verification",
            "; ".join(errors),
        )
    return result


def _expected_process_from_receipt(
    outcome: str,
) -> tuple[str, int, str | None]:
    if outcome == "passed":
        return "pass", 0, None
    if outcome == "test_failure":
        return "fail", 1, None
    return "error", 2, "receipt_exit_mismatch"


def _validate_process_receipt(
    record: Mapping[str, object],
    *,
    binding: str,
    context: str,
) -> None:
    receipt_sha256 = record["receipt_sha256"]
    receipt_outcome = record["receipt_outcome"]
    receipt_producer = record["receipt_producer"]
    receipt_counts = record["receipt_counts"]
    observed = record["observed"]
    return_code = record["return_code"]
    timed_out = record["timed_out"]
    observation_error = record["observation_error"]

    if receipt_sha256 is None:
        if any(
            value is not None
            for value in (
                receipt_outcome,
                receipt_producer,
                receipt_counts,
            )
        ):
            raise _error(
                f"{context}.receipt_sha256",
                "is missing while receipt fields are present",
            )
        if observed == "timeout":
            if (
                timed_out is not True
                or return_code is not None
                or observation_error is not None
            ):
                raise _error(
                    context,
                    "timeout process fields are inconsistent",
                )
            return
        if observed == "error":
            if timed_out is not False:
                raise _error(
                    f"{context}.timed_out",
                    "must be false for error",
                )
            if not isinstance(observation_error, str) or not observation_error:
                raise _error(
                    f"{context}.observation_error",
                    "must identify the missing or invalid receipt",
                )
            return
        raise _error(
            f"{context}.receipt_sha256",
            f"is required for observed={observed!r}",
        )

    if timed_out is not False:
        raise _error(
            f"{context}.timed_out",
            "a retained receipt requires completed execution",
        )
    expected_producer = {
        "name": "deltawitness-unittest",
        "version": __version__,
    }
    if receipt_producer != expected_producer:
        raise _error(
            f"{context}.receipt_producer",
            "does not match the fixed typed producer",
        )
    if not isinstance(receipt_outcome, str) or not isinstance(
        receipt_counts, dict
    ):
        raise _error(
            f"{context}.receipt",
            "outcome and counts are required",
        )
    try:
        receipt_document = build_receipt_document(
            binding=binding,
            producer_name=expected_producer["name"],
            producer_version=expected_producer["version"],
            outcome=receipt_outcome,
            counts=receipt_counts,
        )
        canonical = validate_receipt_document(
            receipt_document,
            expected_binding=binding,
        )
    except DeltaWitnessError as exc:
        raise _error(
            f"{context}.receipt",
            f"has invalid typed semantics ({exc})",
        ) from exc
    if receipt_sha256 != canonical.sha256:
        raise _error(
            f"{context}.receipt_sha256",
            "does not match the reconstructed receipt",
        )
    expected_observed, expected_return, expected_error = (
        _expected_process_from_receipt(receipt_outcome)
    )
    if observed != expected_observed:
        raise _error(
            f"{context}.receipt_outcome",
            "is inconsistent with observed classification",
        )
    if return_code != expected_return:
        raise _error(
            f"{context}.return_code",
            "is inconsistent with the retained receipt",
        )
    if observation_error != expected_error:
        raise _error(
            f"{context}.observation_error",
            "is inconsistent with the retained receipt",
        )
    if expected_observed in {"pass", "fail"}:
        expected_counts = {
            "tests_run": 1,
            "passed": 1 if expected_observed == "pass" else 0,
            "failures": 1 if expected_observed == "fail" else 0,
            "errors": 0,
            "skipped": 0,
            "expected_failures": 0,
            "unexpected_successes": 0,
        }
        if receipt_counts != expected_counts:
            raise _error(
                f"{context}.receipt_counts",
                "must represent exactly one logical selector test",
            )


def _canonical_selector(
    actual: object,
    *,
    plan: Mapping[str, object],
    catalog: Mapping[str, object],
    mutation_result: Mapping[str, object],
    stdlib_statement_result: Mapping[str, object],
    profile_id: str,
    selector: str,
) -> dict[str, Any]:
    context = f"Coverage.py selector {profile_id}/{selector}"
    record = _exact_keys(actual, _SELECTOR_FIELDS, context=context)
    source = plan["source_scope"]
    target = catalog["target"]
    assert isinstance(source, dict) and isinstance(target, dict)
    source_sha256 = str(source["source_sha256"])
    target_lines = _statement._target_lines(catalog)
    test_sha256 = _statement._sha256_bytes(
        _statement._test_bytes(selector)
    )
    context_id = _context_id(profile_id, selector)
    command = _coverage_command(
        selector=selector,
        source_sha256=source_sha256,
        target_lines=target_lines,
        context_id=context_id,
    )
    binding = _invocation_binding(
        plan_sha256=str(plan["plan_sha256"]),
        catalog_sha256=str(catalog["catalog_sha256"]),
        mutation_result_semantic_sha256=str(
            mutation_result["semantic_sha256"]
        ),
        stdlib_statement_result_semantic_sha256=str(
            stdlib_statement_result["semantic_sha256"]
        ),
        profile_id=profile_id,
        selector=selector,
        source_sha256=source_sha256,
        test_sha256=test_sha256,
        target_id=str(target["target_id"]),
        target_lines=target_lines,
        context_id=context_id,
        command=command,
    )
    expected_static = {
        "selector": selector,
        "source_sha256": source_sha256,
        "test_sha256": test_sha256,
        "command": command,
        "context_id": context_id,
        "expected_observed": "pass",
        "expected_target_executed": target_lines,
        "invocation_binding": binding,
    }
    for field, expected in expected_static.items():
        if not _strict_equal(expected, record[field]):
            raise _error(
                f"{context}.{field}",
                "does not match the frozen relation",
            )
    if record["observed"] not in {"pass", "fail", "error", "timeout"}:
        raise _error(f"{context}.observed", "is unsupported")
    _finite_nonnegative(
        record["duration_seconds"],
        context=f"{context}.duration_seconds",
    )
    for field in ("stdout_sha256", "stderr_sha256"):
        if not _is_sha256(record[field]):
            raise _error(
                f"{context}.{field}",
                "must be a lowercase SHA-256 digest",
            )
    _validate_process_receipt(record, binding=binding, context=context)

    coverage_receipt = record["coverage_receipt"]
    if coverage_receipt is None:
        if record["coverage_status"] != "indeterminate":
            raise _error(
                f"{context}.coverage_status",
                "must be indeterminate without a receipt",
            )
        if not isinstance(record["coverage_error"], str) or not record[
            "coverage_error"
        ]:
            raise _error(
                f"{context}.coverage_error",
                "must identify missing coverage evidence",
            )
        canonical_receipt = None
    else:
        canonical_receipt = validate_coverage_receipt(
            coverage_receipt,
            expected_binding=binding,
            expected_target={
                "path": _TARGET_PATH,
                "symbol": _TARGET_SYMBOL,
                "source_sha256": source_sha256,
                "target_lines": target_lines,
            },
            expected_context_id=context_id,
            expected_configuration=_selector_configuration(context_id),
            expected_manifest_sha256=COVERAGEPY_MANIFEST_SHA256,
        )
        measurement_status = canonical_receipt["measurement_status"]
        expected_error = canonical_receipt["measurement_error"]
        if measurement_status == "complete":
            if record["coverage_error"] is not None:
                raise _error(
                    f"{context}.coverage_error",
                    "must be null for complete evidence",
                )
        elif record["coverage_error"] != expected_error:
            raise _error(
                f"{context}.coverage_error",
                "must match the indeterminate receipt",
            )

    raw = {
        "selector": selector,
        "source_sha256": source_sha256,
        "test_sha256": test_sha256,
        "command": command,
        "context_id": context_id,
        "observed": record["observed"],
        "return_code": record["return_code"],
        "timed_out": record["timed_out"],
        "duration_seconds": record["duration_seconds"],
        "stdout_sha256": record["stdout_sha256"],
        "stderr_sha256": record["stderr_sha256"],
        "invocation_binding": binding,
        "receipt_sha256": record["receipt_sha256"],
        "receipt_outcome": record["receipt_outcome"],
        "receipt_producer": deepcopy(record["receipt_producer"]),
        "receipt_counts": deepcopy(record["receipt_counts"]),
        "observation_error": record["observation_error"],
        "coverage_receipt": canonical_receipt,
        "coverage_error": record["coverage_error"],
    }
    canonical = _enrich_selector(
        raw,
        expected_target_executed=target_lines,
    )
    for field in (
        "outcome_concordant",
        "coverage_status",
        "statement_concordant",
        "branch_evidence_complete",
        "context_partition_valid",
        "concordant",
        "cost",
    ):
        if not _strict_equal(canonical[field], record[field]):
            raise _error(
                f"{context}.{field}",
                "does not match reconstructed evidence",
            )
    return canonical


def _canonical_profile(
    actual: object,
    *,
    plan: Mapping[str, object],
    catalog: Mapping[str, object],
    mutation_result: Mapping[str, object],
    stdlib_statement_result: Mapping[str, object],
    profile: Mapping[str, object],
    order: int,
) -> dict[str, Any]:
    context = f"Coverage.py profile {profile['profile_id']}"
    record = _exact_keys(actual, _PROFILE_FIELDS, context=context)
    for field, expected in (
        ("order", order),
        ("profile_id", profile["profile_id"]),
        ("profile_role", profile["profile_role"]),
    ):
        if record[field] != expected:
            raise _error(
                f"{context}.{field}",
                "does not match the frozen profile",
            )
    expected_selectors = profile["selectors"]
    actual_selectors = record["selectors"]
    if (
        not isinstance(expected_selectors, list)
        or not isinstance(actual_selectors, list)
        or len(expected_selectors) != len(actual_selectors)
    ):
        raise _error(
            f"{context}.selectors",
            "cardinality does not match the frozen profile",
        )
    selectors = [
        _canonical_selector(
            actual_selector,
            plan=plan,
            catalog=catalog,
            mutation_result=mutation_result,
            stdlib_statement_result=stdlib_statement_result,
            profile_id=str(profile["profile_id"]),
            selector=str(selector),
        )
        for actual_selector, selector in zip(
            actual_selectors,
            expected_selectors,
            strict=True,
        )
    ]
    canonical = _build_profile(
        order=order,
        profile=profile,
        selectors=selectors,
        expected_lines=_statement._target_lines(catalog),
    )
    for field in _PROFILE_FIELDS - {"selectors"}:
        if not _strict_equal(canonical[field], record[field]):
            raise _error(
                f"{context}.{field}",
                "does not match selector-derived evidence",
            )
    return canonical


def _canonical_result(
    document: object,
    plan: Mapping[str, object],
    catalog: Mapping[str, object],
    mutation_result: Mapping[str, object],
    stdlib_statement_result: Mapping[str, object],
) -> dict[str, Any]:
    result = _exact_keys(
        document,
        _ROOT_FIELDS,
        context="Coverage.py baseline result",
    )
    profiles_source = plan["calibration_profiles"]
    actual_profiles = result["profiles"]
    if (
        not isinstance(profiles_source, list)
        or not isinstance(actual_profiles, list)
        or len(profiles_source) != 2
        or len(actual_profiles) != 2
    ):
        raise _error(
            "Coverage.py baseline result.profiles",
            "must contain the two frozen profiles",
        )
    profiles = [
        _canonical_profile(
            actual,
            plan=plan,
            catalog=catalog,
            mutation_result=mutation_result,
            stdlib_statement_result=stdlib_statement_result,
            profile=profile,
            order=order,
        )
        for order, (actual, profile) in enumerate(
            zip(actual_profiles, profiles_source, strict=True),
            start=1,
        )
    ]
    comparison = _derive_comparison(
        profiles,
        mutation_result,
        stdlib_statement_result,
    )
    analysis = _derive_analysis(profiles, comparison)
    distribution = build_coveragepy_distribution_manifest()
    valid_distribution, distribution_errors = (
        verify_coveragepy_distribution_manifest_document(
            result["distribution"]
        )
    )
    if not valid_distribution:
        raise _error(
            "Coverage.py baseline result.distribution",
            "; ".join(distribution_errors),
        )
    if not _strict_equal(distribution, result["distribution"]):
        raise _error(
            "Coverage.py baseline result.distribution",
            "does not match the reviewed manifest",
        )
    if not isinstance(result["created_at"], str) or not result["created_at"]:
        raise _error(
            "Coverage.py baseline result.created_at",
            "must be a non-empty string",
        )
    runtime = _exact_keys(
        result["runtime"],
        _RUNTIME_FIELDS,
        context="Coverage.py baseline result.runtime",
    )
    if any(not isinstance(value, str) or not value for value in runtime.values()):
        raise _error(
            "Coverage.py baseline result.runtime",
            "values must be non-empty strings",
        )
    adapter = _exact_keys(
        result["adapter"],
        _ADAPTER_FIELDS,
        context="Coverage.py baseline result.adapter",
    )
    if not _strict_equal(_adapter(), adapter):
        raise _error(
            "Coverage.py baseline result.adapter",
            "does not match the fixed adapter",
        )
    configuration = result["configuration"]
    if not _strict_equal(_configuration(), configuration):
        raise _error(
            "Coverage.py baseline result.configuration",
            "does not match the fixed configuration",
        )
    source = _exact_keys(
        result["source"],
        _SOURCE_FIELDS,
        context="Coverage.py baseline result.source",
    )
    if not _strict_equal(_source_view(plan, catalog), source):
        raise _error(
            "Coverage.py baseline result.source",
            "does not match the frozen source and target",
        )
    comparison_record = _exact_keys(
        result["comparison"],
        _COMPARISON_FIELDS,
        context="Coverage.py baseline result.comparison",
    )
    if not _strict_equal(comparison, comparison_record):
        raise _error(
            "Coverage.py baseline result.comparison",
            "does not match reconstructed profile relations",
        )
    analysis_record = _exact_keys(
        result["analysis"],
        _ANALYSIS_FIELDS,
        context="Coverage.py baseline result.analysis",
    )
    if not _strict_equal(analysis, analysis_record):
        raise _error(
            "Coverage.py baseline result.analysis",
            "does not match reconstructed evidence",
        )
    policy = _exact_keys(
        result["policy"],
        _POLICY_FIELDS,
        context="Coverage.py baseline result.policy",
    )
    if not _strict_equal(_policy(), policy):
        raise _error(
            "Coverage.py baseline result.policy",
            "does not match the fixed non-policy boundary",
        )
    selectors = [
        selector
        for profile in profiles
        for selector in profile["selectors"]
    ]
    expected_cost = _aggregate_cost(selectors, profile_count=2)
    cost = _exact_keys(
        result["cost"],
        _ROOT_COST_FIELDS,
        context="Coverage.py baseline result.cost",
    )
    if not _strict_equal(expected_cost, cost):
        raise _error(
            "Coverage.py baseline result.cost",
            "does not match selector-derived costs",
        )
    expected_static = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "study_id": "DW-001",
        "result_id": RESULT_ID,
        "partition": "development",
        "plan_sha256": plan["plan_sha256"],
        "catalog_sha256": catalog["catalog_sha256"],
        "mutation_result_semantic_sha256": mutation_result[
            "semantic_sha256"
        ],
        "stdlib_statement_result_semantic_sha256": (
            stdlib_statement_result["semantic_sha256"]
        ),
        "distribution_manifest_sha256": COVERAGEPY_MANIFEST_SHA256,
    }
    for field, expected in expected_static.items():
        if result[field] != expected:
            raise _error(
                f"Coverage.py baseline result.{field}",
                "does not match the frozen relation",
            )
    return {
        **expected_static,
        "created_at": result["created_at"],
        "runtime": deepcopy(runtime),
        "adapter": _adapter(),
        "distribution": distribution,
        "configuration": _configuration(),
        "source": _source_view(plan, catalog),
        "profiles": profiles,
        "comparison": comparison,
        "analysis": analysis,
        "policy": _policy(),
        "cost": expected_cost,
        "semantic_sha256": result["semantic_sha256"],
        "report_sha256": result["report_sha256"],
    }


def verify_claim_scoped_coveragepy_baseline_document(
    document: object,
    plan: object,
    catalog: object,
    mutation_result: object,
    stdlib_statement_result: object,
) -> tuple[bool, tuple[str, ...]]:
    """Independently reconstruct source, receipts, aggregates, and digests."""

    try:
        (
            normalized_plan,
            normalized_catalog,
            normalized_mutation,
            normalized_stdlib,
        ) = _preflight(
            plan,
            catalog,
            mutation_result,
            stdlib_statement_result,
        )
        canonical = _canonical_result(
            document,
            normalized_plan,
            normalized_catalog,
            normalized_mutation,
            normalized_stdlib,
        )
        assert isinstance(document, dict)
        errors: list[str] = []
        for field in _ROOT_FIELDS - {
            "created_at",
            "runtime",
            "semantic_sha256",
            "report_sha256",
        }:
            errors.extend(
                _difference_paths(
                    canonical[field],
                    document[field],
                    path=f"Coverage.py baseline result.{field}",
                )
            )
        if document.get("semantic_sha256") != (
            compute_coveragepy_baseline_semantic_sha256(document)
        ):
            errors.append(
                "Coverage.py baseline result.semantic_sha256: digest mismatch"
            )
        if document.get("report_sha256") != (
            compute_coveragepy_baseline_report_sha256(document)
        ):
            errors.append(
                "Coverage.py baseline result.report_sha256: digest mismatch"
            )
    except (
        DW001CoveragePyBaselineError,
        CoveragePyProbeError,
        DeltaWitnessError,
        ReportError,
        KeyError,
        TypeError,
        IndexError,
        ValueError,
        OverflowError,
        MemoryError,
        RecursionError,
        AssertionError,
    ) as exc:
        if isinstance(
            exc,
            (
                DW001CoveragePyBaselineError,
                CoveragePyProbeError,
                ReportError,
            ),
        ):
            return False, (str(exc),)
        return False, (
            "Coverage.py baseline result: verification failed closed: "
            f"{type(exc).__name__}: {exc}",
        )
    unique = tuple(dict.fromkeys(errors))
    return not unique, unique


def load_claim_scoped_coveragepy_baseline(
    path: Path,
    plan: object,
    catalog: object,
    mutation_result: object,
    stdlib_statement_result: object,
) -> dict[str, Any]:
    """Strict-load one bounded regular non-link result and verify it."""

    try:
        metadata = path.lstat()
    except OSError as exc:
        raise _error("Coverage.py baseline result path", "cannot be inspected") from exc
    if path.is_symlink() or not stat.S_ISREG(metadata.st_mode):
        raise _error(
            "Coverage.py baseline result path",
            "must be a regular non-link file",
        )
    if metadata.st_size <= 0 or metadata.st_size > _MAX_RESULT_BYTES:
        raise _error(
            "Coverage.py baseline result path",
            "is outside the size limit",
        )
    document = load_report(path)
    valid, errors = verify_claim_scoped_coveragepy_baseline_document(
        document,
        plan,
        catalog,
        mutation_result,
        stdlib_statement_result,
    )
    if not valid:
        raise _error(
            "Coverage.py baseline result",
            "; ".join(errors),
        )
    return document


__all__ = [
    "ADAPTER_ID",
    "DW001CoveragePyBaselineError",
    "MUTATION_RESULT_SEMANTIC_SHA256",
    "RESULT_ID",
    "RESULT_SCHEMA_VERSION",
    "STDLIB_STATEMENT_RESULT_SEMANTIC_SHA256",
    "compute_coveragepy_baseline_report_sha256",
    "compute_coveragepy_baseline_semantic_sha256",
    "load_claim_scoped_coveragepy_baseline",
    "run_claim_scoped_coveragepy_baseline",
    "verify_claim_scoped_coveragepy_baseline_document",
]
