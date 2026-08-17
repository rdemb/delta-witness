"""Claim-scoped statement-coverage baseline for DW-001.

The runner executes only the exact project-owned candidate source and selector
profiles frozen by the claim-scoped mutation plan, collects invocation-bound
statement traces for the exact `is_admin` target, and compares those signatures
with the already verified frozen mutation-result table.

Complete but preregistration-divergent coverage signatures remain valid negative
results. Malformed, substituted, contradictory, aggregate-inconsistent, or
non-finite evidence still fails closed.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import math
from pathlib import Path
import platform
import tempfile
import time
from typing import Any, Mapping, Sequence

from . import __version__
from . import _dw001_weak_proxy as _weak_proxy
from . import dw001_mutation_results as _mutation_results
from .dw001_mutation_plan import (
    verify_claim_scoped_mutant_catalog_document,
    verify_claim_scoped_mutation_plan_document,
)
from .errors import DeltaWitnessError
from .execution import run_command
from .reporting import sha256_document
from .statement_trace_probe import (
    StatementTraceError,
    TRACE_OUTPUT_BASENAME,
    TRACE_PRODUCER_NAME,
    TRACE_SCHEMA_VERSION,
    build_trace_document,
    compute_trace_sha256,
    load_trace_document,
    validate_trace_document,
)


RESULT_SCHEMA_VERSION = "deltawitness.dw001-statement-coverage-result.v1"
RESULT_ID = "DW-001-STATEMENT-COVERAGE-RESULT-V1"
ADAPTER_ID = "stdlib-statement-trace-v1"
MUTATION_RESULT_SEMANTIC_SHA256 = (
    "9e101bca85fd630bf5bdb2a6030d9fdab93eb3eac54b03f4aab99012c28086b6"
)

_BINDING_SCHEMA_VERSION = (
    "deltawitness.dw001-statement-coverage-invocation.v1"
)
_STRONG_PROFILE_ID = "strong-authorization-oracle-v1"
_WEAK_PROFILE_ID = "weak-boolean-proxy-v1"
_TARGET_PATH = "src/access.py"
_TARGET_SYMBOL = "is_admin"

_ROOT_FIELDS = {
    "schema_version",
    "study_id",
    "result_id",
    "partition",
    "plan_sha256",
    "catalog_sha256",
    "mutation_result_semantic_sha256",
    "created_at",
    "runtime",
    "adapter",
    "source",
    "profiles",
    "comparison",
    "analysis",
    "policy",
    "cost",
    "semantic_sha256",
    "report_sha256",
}
_SELECTOR_FIELDS = {
    "selector",
    "source_sha256",
    "test_sha256",
    "command",
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
    "expected_covered_lines",
    "coverage_status",
    "coverage_concordant",
    "trace",
    "concordant",
}
_PROFILE_FIELDS = {
    "order",
    "profile_id",
    "profile_role",
    "selectors",
    "expected_union_lines",
    "union_lines",
    "expected_intersection_lines",
    "intersection_lines",
    "line_hits",
    "expected_all_selectors_passed",
    "all_selectors_passed",
    "coverage_status",
    "concordant",
    "cost",
}
_PROFILE_COST_FIELDS = {
    "status",
    "command_count",
    "selector_count",
    "wall_clock_seconds",
    "cpu_seconds",
    "missing_reason",
}
_ROOT_COST_FIELDS = {
    "status",
    "profile_count",
    "command_count",
    "selector_count",
    "wall_clock_seconds",
    "cpu_seconds",
    "missing_reason",
}


class DW001StatementCoverageError(DeltaWitnessError):
    """Raised when statement-coverage evidence fails closed."""


def _error(context: str, message: str) -> DW001StatementCoverageError:
    return DW001StatementCoverageError(f"{context}: {message}")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


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
        return (
            set(expected) == set(observed)
            and all(_strict_equal(expected[key], observed[key]) for key in expected)
        )
    if isinstance(expected, list):
        return (
            len(expected) == len(observed)
            and all(
                _strict_equal(expected_item, observed_item)
                for expected_item, observed_item in zip(
                    expected, observed, strict=True
                )
            )
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
        errors = []
        if len(expected) != len(observed):
            errors.append(
                f"{path}: length mismatch; expected {len(expected)}, "
                f"observed {len(observed)}"
            )
        for index, (expected_item, observed_item) in enumerate(
            zip(expected, observed, strict=False)
        ):
            errors.extend(
                _difference_paths(
                    expected_item,
                    observed_item,
                    path=f"{path}[{index}]",
                )
            )
        return errors
    if expected != observed:
        return [f"{path}: value mismatch"]
    return []


def _compute_trace_sha256(document: dict[str, Any]) -> str:
    """Test-visible alias for recomputing one complete trace receipt digest."""

    return compute_trace_sha256(document)


def _test_bytes(selector: str) -> bytes:
    if selector.startswith("test_access.AccessTests."):
        return _mutation_results._CALIBRATION_TESTS.encode("utf-8")
    raise _error("statement coverage selector", f"unsupported selector {selector!r}")


def _target_lines(catalog: Mapping[str, object]) -> list[int]:
    target = catalog.get("target")
    if not isinstance(target, dict):
        raise _error("statement coverage catalog.target", "must be an object")
    line = target.get("lineno")
    if isinstance(line, bool) or not isinstance(line, int) or line <= 0:
        raise _error("statement coverage catalog.target.lineno", "must be positive")
    return [line]


def _trace_command(
    *,
    selector: str,
    source_sha256: str,
    target_lines: Sequence[int],
) -> list[str]:
    command = [
        "python",
        "-m",
        "deltawitness.statement_trace_probe",
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
            "--trace-output",
            TRACE_OUTPUT_BASENAME,
        ]
    )
    return command


def _invocation_binding(
    *,
    plan_sha256: str,
    catalog_sha256: str,
    mutation_result_semantic_sha256: str,
    profile_id: str,
    selector: str,
    source_sha256: str,
    test_sha256: str,
    target_id: str,
    target_lines: Sequence[int],
    command: Sequence[str],
) -> str:
    return sha256_document(
        {
            "schema_version": _BINDING_SCHEMA_VERSION,
            "result_id": RESULT_ID,
            "adapter_id": ADAPTER_ID,
            "plan_sha256": plan_sha256,
            "catalog_sha256": catalog_sha256,
            "mutation_result_semantic_sha256": (
                mutation_result_semantic_sha256
            ),
            "profile_id": profile_id,
            "selector": selector,
            "source_sha256": source_sha256,
            "test_sha256": test_sha256,
            "target_id": target_id,
            "target_lines": list(target_lines),
            "command": list(command),
            "observer": "outcome-receipt-v1",
            "trace_schema_version": TRACE_SCHEMA_VERSION,
            "trace_producer": {
                "name": TRACE_PRODUCER_NAME,
                "version": __version__,
            },
        }
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


def _indeterminate_trace(
    *,
    binding: str,
    source_sha256: str,
    target_lines: list[int],
    code: str,
) -> dict[str, Any]:
    return build_trace_document(
        binding=binding,
        target_path=_TARGET_PATH,
        target_symbol=_TARGET_SYMBOL,
        source_sha256=source_sha256,
        target_lines=target_lines,
        trace_status="indeterminate",
        function_calls=None,
        line_hits={},
        trace_error=code,
    )


def _execute_selector(
    *,
    plan: Mapping[str, object],
    catalog: Mapping[str, object],
    mutation_result: Mapping[str, object],
    profile_id: str,
    selector: str,
) -> dict[str, Any]:
    """Execute one fixed candidate selector and load both bound receipts."""

    source = _weak_proxy.CANDIDATE_CODE
    source_sha256 = _sha256_bytes(source.encode("utf-8"))
    expected_source = plan["source_scope"]
    if not isinstance(expected_source, dict):
        raise _error("statement coverage source scope", "must be an object")
    if source_sha256 != expected_source["source_sha256"]:
        raise _error(
            "statement coverage source_sha256",
            "does not match frozen plan",
        )
    target = catalog["target"]
    if not isinstance(target, dict):
        raise _error("statement coverage catalog.target", "must be an object")
    target_id = str(target["target_id"])
    target_lines = _target_lines(catalog)
    tests = _test_bytes(selector)
    test_sha256 = _sha256_bytes(tests)
    command = _trace_command(
        selector=selector,
        source_sha256=source_sha256,
        target_lines=target_lines,
    )
    binding = _invocation_binding(
        plan_sha256=str(plan["plan_sha256"]),
        catalog_sha256=str(catalog["catalog_sha256"]),
        mutation_result_semantic_sha256=str(
            mutation_result["semantic_sha256"]
        ),
        profile_id=profile_id,
        selector=selector,
        source_sha256=source_sha256,
        test_sha256=test_sha256,
        target_id=target_id,
        target_lines=target_lines,
        command=command,
    )

    with tempfile.TemporaryDirectory(
        prefix="deltawitness-statement-coverage-"
    ) as directory:
        root = Path(directory)
        (root / "src").mkdir()
        (root / "tests").mkdir()
        (root / "src" / "access.py").write_text(source, encoding="utf-8")
        (root / "tests" / "test_access.py").write_bytes(tests)
        process = run_command(
            command,
            state=f"statement-coverage:{profile_id}:{selector}",
            cwd=root,
            timeout_seconds=30,
            pass_env=(),
            include_output=False,
            observer="outcome-receipt-v1",
            receipt_binding=binding,
        )
        trace_path = root / TRACE_OUTPUT_BASENAME
        if trace_path.exists():
            try:
                trace = load_trace_document(
                    trace_path,
                    expected_binding=binding,
                    expected_target_path=_TARGET_PATH,
                    expected_target_symbol=_TARGET_SYMBOL,
                    expected_source_sha256=source_sha256,
                    expected_target_lines=target_lines,
                )
            except StatementTraceError:
                trace = _indeterminate_trace(
                    binding=binding,
                    source_sha256=source_sha256,
                    target_lines=target_lines,
                    code="invalid_trace_receipt",
                )
        else:
            trace = _indeterminate_trace(
                binding=binding,
                source_sha256=source_sha256,
                target_lines=target_lines,
                code=(
                    "trace_timeout"
                    if process.timed_out
                    else "missing_trace_receipt"
                ),
            )

    observed, observation_error = _classify_process(process)
    return {
        "selector": selector,
        "source_sha256": source_sha256,
        "test_sha256": test_sha256,
        "command": command,
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
        "trace": trace,
    }


def _selector_status(raw: Mapping[str, object]) -> str:
    trace = raw.get("trace")
    if not isinstance(trace, dict) or trace.get("trace_status") != "complete":
        return "indeterminate"
    observed = raw.get("observed")
    if observed == "pass":
        return "complete"
    if observed == "fail":
        return "candidate_invalid"
    return "indeterminate"


def _enrich_selector(
    raw: Mapping[str, object],
    *,
    expected_covered_lines: list[int],
) -> dict[str, Any]:
    trace = raw.get("trace")
    if not isinstance(trace, dict):
        raise _error("statement coverage selector.trace", "must be an object")
    status = _selector_status(raw)
    observed = raw.get("observed")
    outcome_concordant = observed == "pass"
    coverage_concordant = (
        status == "complete"
        and trace.get("covered_lines") == expected_covered_lines
    )
    return {
        **deepcopy(dict(raw)),
        "expected_observed": "pass",
        "outcome_concordant": outcome_concordant,
        "expected_covered_lines": list(expected_covered_lines),
        "coverage_status": status,
        "coverage_concordant": coverage_concordant,
        "concordant": outcome_concordant and coverage_concordant,
    }


def _profile_lines(
    selectors: Sequence[Mapping[str, object]],
) -> tuple[list[int], list[int], list[dict[str, int]]]:
    line_sets = [
        set(selector["trace"]["covered_lines"])
        for selector in selectors
    ]
    union = sorted(set().union(*line_sets))
    intersection = sorted(set.intersection(*line_sets))
    hits: Counter[int] = Counter()
    for selector in selectors:
        for item in selector["trace"]["line_hits"]:
            hits[item["line"]] += item["hits"]
    return (
        union,
        intersection,
        [{"line": line, "hits": hits[line]} for line in sorted(hits)],
    )


def _build_profile(
    *,
    order: int,
    profile: Mapping[str, object],
    selectors: list[dict[str, Any]],
    expected_lines: list[int],
    wall_clock_seconds: float,
    cpu_seconds: float,
) -> dict[str, Any]:
    statuses = [selector["coverage_status"] for selector in selectors]
    all_passed = all(selector["observed"] == "pass" for selector in selectors)
    if any(status == "indeterminate" for status in statuses):
        coverage_status = "indeterminate"
        union_lines = None
        intersection_lines = None
        line_hits = None
    elif any(status == "candidate_invalid" for status in statuses):
        coverage_status = "candidate_invalid"
        union_lines = None
        intersection_lines = None
        line_hits = None
    else:
        coverage_status = "complete"
        union_lines, intersection_lines, line_hits = _profile_lines(selectors)
    concordant = (
        coverage_status == "complete"
        and union_lines == expected_lines
        and intersection_lines == expected_lines
        and all_passed
        and all(selector["concordant"] for selector in selectors)
    )
    return {
        "order": order,
        "profile_id": profile["profile_id"],
        "profile_role": profile["profile_role"],
        "selectors": selectors,
        "expected_union_lines": list(expected_lines),
        "union_lines": union_lines,
        "expected_intersection_lines": list(expected_lines),
        "intersection_lines": intersection_lines,
        "line_hits": line_hits,
        "expected_all_selectors_passed": True,
        "all_selectors_passed": all_passed,
        "coverage_status": coverage_status,
        "concordant": concordant,
        "cost": {
            "status": "measured",
            "command_count": len(selectors),
            "selector_count": len(selectors),
            "wall_clock_seconds": round(wall_clock_seconds, 6),
            "cpu_seconds": round(cpu_seconds, 6),
            "missing_reason": None,
        },
    }


def _profile_by_id(
    profiles: Sequence[Mapping[str, object]],
    profile_id: str,
) -> Mapping[str, object]:
    matches = [profile for profile in profiles if profile.get("profile_id") == profile_id]
    if len(matches) != 1:
        raise _error(
            "statement coverage profiles",
            f"expected exactly one {profile_id!r} profile",
        )
    return matches[0]


def _mutation_discrimination(mutation_result: Mapping[str, object]) -> bool | None:
    records = mutation_result.get("records")
    if not isinstance(records, list):
        raise _error("statement coverage mutation result.records", "must be a list")
    generic = [
        record
        for record in records
        if isinstance(record, dict)
        and record.get("record_role") == "generic_operator"
    ]
    if not generic:
        raise _error("statement coverage mutation result", "has no generic records")
    differences: list[bool] = []
    for record in generic:
        profiles = record.get("profiles")
        if not isinstance(profiles, list):
            raise _error(
                "statement coverage mutation result profile",
                "must be a list",
            )
        strong = _profile_by_id(profiles, _STRONG_PROFILE_ID).get("outcome")
        weak = _profile_by_id(profiles, _WEAK_PROFILE_ID).get("outcome")
        if strong == "indeterminate" or weak == "indeterminate":
            return None
        differences.append(strong != weak)
    return any(differences)


def _derive_comparison(
    profiles: Sequence[Mapping[str, object]],
    mutation_result: Mapping[str, object],
) -> dict[str, Any]:
    strong = _profile_by_id(profiles, _STRONG_PROFILE_ID)
    weak = _profile_by_id(profiles, _WEAK_PROFILE_ID)
    if (
        strong.get("coverage_status") != "complete"
        or weak.get("coverage_status") != "complete"
    ):
        coverage_discriminates = None
    else:
        coverage_discriminates = (
            strong.get("union_lines") != weak.get("union_lines")
            or strong.get("intersection_lines")
            != weak.get("intersection_lines")
        )
    mutation_discriminates = _mutation_discrimination(mutation_result)
    if coverage_discriminates is None or mutation_discriminates is None:
        agree = None
        incremental = None
    else:
        agree = coverage_discriminates == mutation_discriminates
        incremental = mutation_discriminates and not coverage_discriminates
    expected = {
        "expected_statement_coverage_discriminates_profiles": False,
        "expected_mutation_discriminates_profiles": True,
        "expected_coverage_and_mutation_agree": False,
        "expected_incremental_mutation_signal_observed": True,
    }
    observed = {
        "statement_coverage_discriminates_profiles": coverage_discriminates,
        "mutation_discriminates_profiles": mutation_discriminates,
        "coverage_and_mutation_agree": agree,
        "incremental_mutation_signal_observed": incremental,
    }
    concordant = (
        coverage_discriminates
        == expected["expected_statement_coverage_discriminates_profiles"]
        and mutation_discriminates
        == expected["expected_mutation_discriminates_profiles"]
        and agree == expected["expected_coverage_and_mutation_agree"]
        and incremental
        == expected["expected_incremental_mutation_signal_observed"]
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
    if indeterminate:
        status = "indeterminate"
    elif unexpected_selectors or unexpected_profiles or comparison.get("concordant") is not True:
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


def _preflight(
    plan: object,
    catalog: object,
    mutation_result: object,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    plan_valid, plan_errors = verify_claim_scoped_mutation_plan_document(plan)
    catalog_valid, catalog_errors = verify_claim_scoped_mutant_catalog_document(
        catalog,
        plan,
    )
    mutation_valid, mutation_errors = (
        _mutation_results.verify_claim_scoped_mutation_result_document(
            mutation_result,
            plan,
            catalog,
        )
    )
    errors = [
        *[f"plan: {error}" for error in plan_errors if not plan_valid],
        *[f"catalog: {error}" for error in catalog_errors if not catalog_valid],
        *[
            f"mutation_result: {error}"
            for error in mutation_errors
            if not mutation_valid
        ],
    ]
    if errors:
        raise _error("statement coverage preflight", "; ".join(errors))
    if not isinstance(plan, dict) or not isinstance(catalog, dict) or not isinstance(mutation_result, dict):
        raise _error("statement coverage preflight", "all sources must be objects")
    if mutation_result.get("semantic_sha256") != MUTATION_RESULT_SEMANTIC_SHA256:
        raise _error(
            "statement coverage mutation_result_semantic_sha256",
            "does not match the frozen result",
        )
    source = plan.get("source_scope")
    target = catalog.get("target")
    if not isinstance(source, dict) or not isinstance(target, dict):
        raise _error("statement coverage source relation", "is malformed")
    if source.get("path") != _TARGET_PATH or source.get("symbol") != _TARGET_SYMBOL:
        raise _error("statement coverage source relation", "is unsupported")
    if target.get("path") != _TARGET_PATH or target.get("symbol") != _TARGET_SYMBOL:
        raise _error("statement coverage target relation", "is unsupported")
    return plan, catalog, mutation_result


def _semantic_view(document: Mapping[str, object]) -> dict[str, Any]:
    normalized = deepcopy(dict(document))
    normalized["created_at"] = None
    normalized["runtime"] = None
    normalized["semantic_sha256"] = None
    normalized["report_sha256"] = None
    root_cost = normalized.get("cost")
    if isinstance(root_cost, dict):
        root_cost["wall_clock_seconds"] = None
        root_cost["cpu_seconds"] = None
    profiles = normalized.get("profiles")
    if isinstance(profiles, list):
        for profile in profiles:
            if not isinstance(profile, dict):
                continue
            cost = profile.get("cost")
            if isinstance(cost, dict):
                cost["wall_clock_seconds"] = None
                cost["cpu_seconds"] = None
            selectors = profile.get("selectors")
            if isinstance(selectors, list):
                for selector in selectors:
                    if isinstance(selector, dict):
                        selector["duration_seconds"] = None
                        selector["stdout_sha256"] = None
                        selector["stderr_sha256"] = None
    return normalized


def compute_statement_coverage_semantic_sha256(document: dict[str, Any]) -> str:
    """Hash stable coverage and comparison semantics."""

    if not isinstance(document, dict):
        raise _error("statement coverage result", "must be an object")
    return sha256_document(_semantic_view(document))


def compute_statement_coverage_report_sha256(document: dict[str, Any]) -> str:
    """Hash the complete result with only its report digest normalized."""

    if not isinstance(document, dict):
        raise _error("statement coverage result", "must be an object")
    normalized = deepcopy(document)
    normalized["report_sha256"] = None
    return sha256_document(normalized)


def run_claim_scoped_statement_coverage(
    plan: object,
    catalog: object,
    mutation_result: object,
) -> dict[str, Any]:
    """Execute the two frozen candidate selector profiles and compare evidence."""

    normalized_plan, normalized_catalog, normalized_mutation = _preflight(
        plan,
        catalog,
        mutation_result,
    )
    profiles_value = normalized_plan["calibration_profiles"]
    if not isinstance(profiles_value, list) or len(profiles_value) != 2:
        raise _error("statement coverage profiles", "must contain exactly two profiles")
    target_lines = _target_lines(normalized_catalog)
    started_wall = time.perf_counter()
    started_cpu = time.process_time()
    profiles: list[dict[str, Any]] = []
    for order, profile in enumerate(profiles_value, start=1):
        if not isinstance(profile, dict):
            raise _error("statement coverage profile", "must be an object")
        profile_wall = time.perf_counter()
        profile_cpu = time.process_time()
        raw_selectors = [
            _execute_selector(
                plan=normalized_plan,
                catalog=normalized_catalog,
                mutation_result=normalized_mutation,
                profile_id=str(profile["profile_id"]),
                selector=str(selector),
            )
            for selector in profile["selectors"]
        ]
        selectors = [
            _enrich_selector(
                selector,
                expected_covered_lines=target_lines,
            )
            for selector in raw_selectors
        ]
        profiles.append(
            _build_profile(
                order=order,
                profile=profile,
                selectors=selectors,
                expected_lines=target_lines,
                wall_clock_seconds=time.perf_counter() - profile_wall,
                cpu_seconds=time.process_time() - profile_cpu,
            )
        )
    comparison = _derive_comparison(profiles, normalized_mutation)
    analysis = _derive_analysis(profiles, comparison)
    source = normalized_plan["source_scope"]
    target = normalized_catalog["target"]
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
        "created_at": datetime.now(timezone.utc).isoformat().replace(
            "+00:00", "Z"
        ),
        "runtime": {
            "tool_version": __version__,
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
            "platform_system": platform.system(),
            "trace_api": "sys.settrace",
            "trace_thread_scope": "current-thread",
        },
        "adapter": {
            "id": ADAPTER_ID,
            "version": "1",
            "trace_schema_version": TRACE_SCHEMA_VERSION,
            "trace_producer": TRACE_PRODUCER_NAME,
        },
        "source": {
            "source_id": source["source_id"],
            "source_sha256": source["source_sha256"],
            "source_ast_sha256": source["ast_sha256"],
            "target_id": target["target_id"],
            "path": source["path"],
            "symbol": source["symbol"],
            "target_lines": target_lines,
            "source_body_published": False,
        },
        "profiles": profiles,
        "comparison": comparison,
        "analysis": analysis,
        "policy": _policy(),
        "cost": {
            "status": "measured",
            "profile_count": 2,
            "command_count": sum(
                profile["cost"]["command_count"] for profile in profiles
            ),
            "selector_count": sum(
                profile["cost"]["selector_count"] for profile in profiles
            ),
            "wall_clock_seconds": round(time.perf_counter() - started_wall, 6),
            "cpu_seconds": round(time.process_time() - started_cpu, 6),
            "missing_reason": None,
        },
        "semantic_sha256": None,
        "report_sha256": None,
    }
    result["semantic_sha256"] = compute_statement_coverage_semantic_sha256(
        result
    )
    result["report_sha256"] = compute_statement_coverage_report_sha256(result)
    valid, errors = verify_claim_scoped_statement_coverage_document(
        result,
        normalized_plan,
        normalized_catalog,
        normalized_mutation,
    )
    if not valid:
        raise _error(
            "statement coverage self-verification",
            "; ".join(errors),
        )
    return result


def _canonical_selector(
    actual: object,
    *,
    plan: Mapping[str, object],
    catalog: Mapping[str, object],
    mutation_result: Mapping[str, object],
    profile_id: str,
    selector: str,
) -> dict[str, Any]:
    record = _exact_keys(
        actual,
        _SELECTOR_FIELDS,
        context=f"statement coverage selector {profile_id}/{selector}",
    )
    source = plan["source_scope"]
    target = catalog["target"]
    assert isinstance(source, dict) and isinstance(target, dict)
    target_lines = _target_lines(catalog)
    source_sha256 = str(source["source_sha256"])
    test_sha256 = _sha256_bytes(_test_bytes(selector))
    command = _trace_command(
        selector=selector,
        source_sha256=source_sha256,
        target_lines=target_lines,
    )
    binding = _invocation_binding(
        plan_sha256=str(plan["plan_sha256"]),
        catalog_sha256=str(catalog["catalog_sha256"]),
        mutation_result_semantic_sha256=str(mutation_result["semantic_sha256"]),
        profile_id=profile_id,
        selector=selector,
        source_sha256=source_sha256,
        test_sha256=test_sha256,
        target_id=str(target["target_id"]),
        target_lines=target_lines,
        command=command,
    )
    expected_static = {
        "selector": selector,
        "source_sha256": source_sha256,
        "test_sha256": test_sha256,
        "command": command,
        "expected_observed": "pass",
        "expected_covered_lines": target_lines,
        "invocation_binding": binding,
    }
    for field, expected in expected_static.items():
        if not _strict_equal(expected, record[field]):
            raise _error(
                f"statement coverage selector.{field}",
                "does not match frozen relation",
            )
    _finite_nonnegative(
        record["duration_seconds"],
        context="statement coverage selector.duration_seconds",
    )
    for field in ("stdout_sha256", "stderr_sha256"):
        if not _is_sha256(record[field]):
            raise _error(
                f"statement coverage selector.{field}",
                "must be a lowercase SHA-256 digest",
            )
    observed = record["observed"]
    if observed not in {"pass", "fail", "error", "timeout"}:
        raise _error("statement coverage selector.observed", "is unsupported")
    if observed in {"pass", "fail"}:
        expected_return = 0 if observed == "pass" else 1
        expected_receipt = "passed" if observed == "pass" else "test_failure"
        if (
            record["return_code"] != expected_return
            or record["timed_out"] is not False
            or record["receipt_outcome"] != expected_receipt
            or record["observation_error"] is not None
            or not _is_sha256(record["receipt_sha256"])
            or not isinstance(record["receipt_producer"], dict)
            or not isinstance(record["receipt_counts"], dict)
        ):
            raise _error(
                "statement coverage selector receipt",
                f"is inconsistent with observed={observed!r}",
            )
        counts = record["receipt_counts"]
        expected_failures = 0 if observed == "pass" else 1
        if (
            counts.get("tests_run") != 1
            or counts.get("failures") != expected_failures
            or counts.get("errors") != 0
        ):
            raise _error(
                "statement coverage selector.receipt_counts",
                "is inconsistent with one logical test",
            )
    elif observed == "timeout":
        if record["timed_out"] is not True:
            raise _error(
                "statement coverage selector.timed_out",
                "must be true for timeout",
            )
    elif record["observation_error"] is None:
        raise _error(
            "statement coverage selector.observation_error",
            "must explain an error",
        )

    trace = validate_trace_document(
        record["trace"],
        expected_binding=binding,
        expected_target_path=_TARGET_PATH,
        expected_target_symbol=_TARGET_SYMBOL,
        expected_source_sha256=source_sha256,
        expected_target_lines=target_lines,
    )
    raw = {
        "selector": selector,
        "source_sha256": source_sha256,
        "test_sha256": test_sha256,
        "command": command,
        "observed": observed,
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
        "trace": trace,
    }
    canonical = _enrich_selector(raw, expected_covered_lines=target_lines)
    for field in (
        "outcome_concordant",
        "coverage_status",
        "coverage_concordant",
        "concordant",
    ):
        if record[field] is not canonical[field]:
            raise _error(
                f"statement coverage selector.{field}",
                "does not match observed evidence",
            )
    return canonical


def _canonical_profile(
    actual: object,
    *,
    plan: Mapping[str, object],
    catalog: Mapping[str, object],
    mutation_result: Mapping[str, object],
    profile: Mapping[str, object],
    order: int,
) -> dict[str, Any]:
    record = _exact_keys(
        actual,
        _PROFILE_FIELDS,
        context=f"statement coverage profile {profile['profile_id']}",
    )
    for field, expected in (
        ("order", order),
        ("profile_id", profile["profile_id"]),
        ("profile_role", profile["profile_role"]),
    ):
        if record[field] != expected:
            raise _error(
                f"statement coverage profile.{field}",
                "does not match frozen profile",
            )
    selectors_value = profile["selectors"]
    actual_selectors = record["selectors"]
    if (
        not isinstance(selectors_value, list)
        or not isinstance(actual_selectors, list)
        or len(selectors_value) != len(actual_selectors)
    ):
        raise _error(
            "statement coverage profile.selectors",
            "cardinality does not match frozen profile",
        )
    selectors = [
        _canonical_selector(
            actual_selector,
            plan=plan,
            catalog=catalog,
            mutation_result=mutation_result,
            profile_id=str(profile["profile_id"]),
            selector=str(selector),
        )
        for actual_selector, selector in zip(
            actual_selectors,
            selectors_value,
            strict=True,
        )
    ]
    cost = _exact_keys(
        record["cost"],
        _PROFILE_COST_FIELDS,
        context="statement coverage profile.cost",
    )
    if (
        cost["status"] != "measured"
        or cost["command_count"] != len(selectors)
        or cost["selector_count"] != len(selectors)
        or cost["missing_reason"] is not None
    ):
        raise _error(
            "statement coverage profile.cost",
            "does not match fixed execution contract",
        )
    _finite_nonnegative(
        cost["wall_clock_seconds"],
        context="statement coverage profile.cost.wall_clock_seconds",
    )
    _finite_nonnegative(
        cost["cpu_seconds"],
        context="statement coverage profile.cost.cpu_seconds",
    )
    canonical = _build_profile(
        order=order,
        profile=profile,
        selectors=selectors,
        expected_lines=_target_lines(catalog),
        wall_clock_seconds=float(cost["wall_clock_seconds"]),
        cpu_seconds=float(cost["cpu_seconds"]),
    )
    for field in (
        "expected_union_lines",
        "union_lines",
        "expected_intersection_lines",
        "intersection_lines",
        "line_hits",
        "expected_all_selectors_passed",
        "all_selectors_passed",
        "coverage_status",
        "concordant",
    ):
        if not _strict_equal(canonical[field], record[field]):
            raise _error(
                f"statement coverage profile.{field}",
                "does not match selector-derived evidence",
            )
    canonical["cost"] = deepcopy(cost)
    return canonical


def _canonical_result(
    document: object,
    plan: Mapping[str, object],
    catalog: Mapping[str, object],
    mutation_result: Mapping[str, object],
) -> dict[str, Any]:
    result = _exact_keys(
        document,
        _ROOT_FIELDS,
        context="statement coverage result",
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
            "statement coverage result.profiles",
            "must contain the two frozen profiles",
        )
    profiles = [
        _canonical_profile(
            actual,
            plan=plan,
            catalog=catalog,
            mutation_result=mutation_result,
            profile=profile,
            order=order,
        )
        for order, (actual, profile) in enumerate(
            zip(actual_profiles, profiles_source, strict=True),
            start=1,
        )
    ]
    comparison = _derive_comparison(profiles, mutation_result)
    analysis = _derive_analysis(profiles, comparison)
    source = plan["source_scope"]
    target = catalog["target"]
    assert isinstance(source, dict) and isinstance(target, dict)
    base = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "study_id": "DW-001",
        "result_id": RESULT_ID,
        "partition": "development",
        "plan_sha256": plan["plan_sha256"],
        "catalog_sha256": catalog["catalog_sha256"],
        "mutation_result_semantic_sha256": mutation_result["semantic_sha256"],
        "created_at": result["created_at"],
        "runtime": deepcopy(result["runtime"]),
        "adapter": {
            "id": ADAPTER_ID,
            "version": "1",
            "trace_schema_version": TRACE_SCHEMA_VERSION,
            "trace_producer": TRACE_PRODUCER_NAME,
        },
        "source": {
            "source_id": source["source_id"],
            "source_sha256": source["source_sha256"],
            "source_ast_sha256": source["ast_sha256"],
            "target_id": target["target_id"],
            "path": source["path"],
            "symbol": source["symbol"],
            "target_lines": _target_lines(catalog),
            "source_body_published": False,
        },
        "profiles": profiles,
        "comparison": comparison,
        "analysis": analysis,
        "policy": _policy(),
        "cost": deepcopy(result["cost"]),
        "semantic_sha256": result["semantic_sha256"],
        "report_sha256": result["report_sha256"],
    }
    if not isinstance(result["created_at"], str) or not result["created_at"]:
        raise _error("statement coverage result.created_at", "must be non-empty")
    runtime = result["runtime"]
    if not isinstance(runtime, dict) or set(runtime) != {
        "tool_version",
        "python_implementation",
        "python_version",
        "platform_system",
        "trace_api",
        "trace_thread_scope",
    }:
        raise _error("statement coverage result.runtime", "has invalid fields")
    if runtime.get("trace_api") != "sys.settrace" or runtime.get(
        "trace_thread_scope"
    ) != "current-thread":
        raise _error("statement coverage result.runtime", "has invalid trace semantics")
    if any(not isinstance(value, str) or not value for value in runtime.values()):
        raise _error("statement coverage result.runtime", "values must be non-empty strings")
    cost = _exact_keys(
        result["cost"],
        _ROOT_COST_FIELDS,
        context="statement coverage result.cost",
    )
    if (
        cost["status"] != "measured"
        or cost["profile_count"] != 2
        or cost["command_count"] != 3
        or cost["selector_count"] != 3
        or cost["missing_reason"] is not None
    ):
        raise _error(
            "statement coverage result.cost",
            "does not match fixed execution contract",
        )
    _finite_nonnegative(
        cost["wall_clock_seconds"],
        context="statement coverage result.cost.wall_clock_seconds",
    )
    _finite_nonnegative(
        cost["cpu_seconds"],
        context="statement coverage result.cost.cpu_seconds",
    )
    return base


def verify_claim_scoped_statement_coverage_document(
    document: object,
    plan: object,
    catalog: object,
    mutation_result: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify complete coverage evidence and preserve valid unexpected results."""

    try:
        normalized_plan, normalized_catalog, normalized_mutation = _preflight(
            plan,
            catalog,
            mutation_result,
        )
        canonical = _canonical_result(
            document,
            normalized_plan,
            normalized_catalog,
            normalized_mutation,
        )
        assert isinstance(document, dict)
        errors: list[str] = []
        for field in (
            "schema_version",
            "study_id",
            "result_id",
            "partition",
            "plan_sha256",
            "catalog_sha256",
            "mutation_result_semantic_sha256",
            "adapter",
            "source",
            "profiles",
            "comparison",
            "analysis",
            "policy",
            "cost",
        ):
            errors.extend(
                _difference_paths(
                    canonical[field],
                    document[field],
                    path=f"statement coverage result.{field}",
                )
            )
        if document.get("semantic_sha256") != compute_statement_coverage_semantic_sha256(
            document
        ):
            errors.append("statement coverage result.semantic_sha256: digest mismatch")
        if document.get("report_sha256") != compute_statement_coverage_report_sha256(
            document
        ):
            errors.append("statement coverage result.report_sha256: digest mismatch")
    except (
        DW001StatementCoverageError,
        StatementTraceError,
        DeltaWitnessError,
        KeyError,
        TypeError,
        IndexError,
        ValueError,
        OverflowError,
        MemoryError,
        RecursionError,
        AssertionError,
    ) as exc:
        if isinstance(exc, (DW001StatementCoverageError, StatementTraceError)):
            return False, (str(exc),)
        return False, (
            "statement coverage result: verification failed closed: "
            f"{type(exc).__name__}: {exc}",
        )
    unique = tuple(dict.fromkeys(errors))
    return not unique, unique


__all__ = [
    "ADAPTER_ID",
    "DW001StatementCoverageError",
    "MUTATION_RESULT_SEMANTIC_SHA256",
    "RESULT_ID",
    "RESULT_SCHEMA_VERSION",
    "compute_statement_coverage_report_sha256",
    "compute_statement_coverage_semantic_sha256",
    "run_claim_scoped_statement_coverage",
    "verify_claim_scoped_statement_coverage_document",
]
