"""Typed execution results for the frozen DW-001 mutation catalog.

The runner executes only the exact project-owned candidate, three generic
mutants, historical challenge control, selector profiles, and reference checks
frozen by PR #38 and issue #39. Duplicate, not-applicable, and invalid catalog
records remain visible but are never executed.

The result retains every typed selector observation and explicitly withholds a
mutation score, universal threshold, merge blocker, holdout, and primary
research denominator. It is an owned-synthetic calibration result, not a
mutation-adequacy or ecological-effectiveness claim.
"""

from __future__ import annotations

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
from .claim_witness import canonical_unittest_selector_command
from .dw001_mutation_plan import (
    _mutated_source,
    verify_claim_scoped_mutant_catalog_document,
    verify_claim_scoped_mutation_plan_document,
)
from .errors import DeltaWitnessError
from .execution import run_command
from .receipt import build_receipt_document, validate_receipt_document
from .reporting import sha256_document


RESULT_SCHEMA_VERSION = "deltawitness.dw001-claim-scoped-mutation-result.v1"
RESULT_ID = "DW-001-CLAIM-SCOPED-MUTATION-RESULT-V1"

_RESULT_BINDING_SCHEMA_VERSION = (
    "deltawitness.dw001-claim-scoped-mutation-invocation.v1"
)
_PRODUCER_NAME = "deltawitness-unittest"
_STRONG_PROFILE_ID = "strong-authorization-oracle-v1"
_WEAK_PROFILE_ID = "weak-boolean-proxy-v1"
_REFERENCE_PROFILE_ID = "reference-claim-checks-v1"
_CANDIDATE_ID = "candidate-baseline-v1"

_ROOT_FIELDS = {
    "schema_version",
    "study_id",
    "result_id",
    "partition",
    "plan_sha256",
    "catalog_sha256",
    "created_at",
    "runtime",
    "source",
    "candidate_baseline",
    "records",
    "summary",
    "policy",
    "cost",
    "semantic_sha256",
    "report_sha256",
}

_CALIBRATION_TESTS = """import sys
import unittest

sys.path.insert(0, "src")
from access import is_admin


class AccessTests(unittest.TestCase):
    def test_admin_is_allowed(self):
        self.assertTrue(is_admin({"role": "admin"}))

    def test_viewer_is_denied(self):
        self.assertFalse(is_admin({"role": "viewer"}))

    def test_viewer_result_is_boolean(self):
        self.assertIsInstance(is_admin({"role": "viewer"}), bool)
"""

_REFERENCE_TESTS = """import sys
import unittest

sys.path.insert(0, "src")
from access import is_admin


class HiddenClaimTests(unittest.TestCase):
    def test_admin_is_allowed(self):
        self.assertTrue(is_admin({"role": "admin"}))

    def test_viewer_is_denied(self):
        self.assertFalse(is_admin({"role": "viewer"}))
"""

_EXPECTED_BY_OPERATOR: dict[str, dict[str, tuple[str, ...]]] = {
    "return-constant-false-v1": {
        "strong": ("fail", "pass"),
        "weak": ("pass",),
        "reference": ("fail", "pass"),
    },
    "return-constant-true-v1": {
        "strong": ("pass", "fail"),
        "weak": ("pass",),
        "reference": ("pass", "fail"),
    },
    "comparison-eq-to-ne-v1": {
        "strong": ("fail", "fail"),
        "weak": ("pass",),
        "reference": ("fail", "fail"),
    },
}
_EXPECTED_KNOWN_CONTROL = {
    "strong": ("pass", "fail"),
    "weak": ("pass",),
    "reference": ("pass", "fail"),
}
_EXPECTED_CANDIDATE = {
    "strong": ("pass", "pass"),
    "weak": ("pass",),
    "reference": ("pass", "pass"),
}


class DW001MutationResultError(DeltaWitnessError):
    """Raised when mutation-result execution or verification fails closed."""


def _error(context: str, message: str) -> DW001MutationResultError:
    return DW001MutationResultError(f"{context}: {message}")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _counts(observed: str) -> dict[str, int]:
    if observed == "pass":
        return {
            "tests_run": 1,
            "passed": 1,
            "failures": 0,
            "errors": 0,
            "skipped": 0,
            "expected_failures": 0,
            "unexpected_successes": 0,
        }
    if observed == "fail":
        return {
            "tests_run": 1,
            "passed": 0,
            "failures": 1,
            "errors": 0,
            "skipped": 0,
            "expected_failures": 0,
            "unexpected_successes": 0,
        }
    raise _error("mutation result expected counts", f"unsupported outcome {observed!r}")


def _receipt_outcome(observed: str) -> str:
    if observed == "pass":
        return "passed"
    if observed == "fail":
        return "test_failure"
    raise _error(
        "mutation result expected receipt",
        f"unsupported outcome {observed!r}",
    )


def _test_bytes(selector: str) -> tuple[str, bytes, str]:
    if selector.startswith("test_access.AccessTests."):
        return (
            "test_access.py",
            _CALIBRATION_TESTS.encode("utf-8"),
            "calibration_profile",
        )
    if selector.startswith("test_hidden_claim.HiddenClaimTests."):
        return (
            "test_hidden_claim.py",
            _REFERENCE_TESTS.encode("utf-8"),
            "reference_claim",
        )
    raise _error("mutation result selector", f"unsupported selector {selector!r}")


def _invocation_binding(
    *,
    plan_sha256: str,
    catalog_sha256: str,
    implementation_id: str,
    profile_id: str,
    selector: str,
    source_sha256: str,
    test_sha256: str,
    command: Sequence[str],
) -> str:
    return sha256_document(
        {
            "schema_version": _RESULT_BINDING_SCHEMA_VERSION,
            "result_id": RESULT_ID,
            "plan_sha256": plan_sha256,
            "catalog_sha256": catalog_sha256,
            "implementation_id": implementation_id,
            "profile_id": profile_id,
            "selector": selector,
            "source_sha256": source_sha256,
            "test_sha256": test_sha256,
            "command": list(command),
            "observer": "outcome-receipt-v1",
            "producer": {
                "name": _PRODUCER_NAME,
                "version": __version__,
            },
        }
    )


def _expected_observation(
    *,
    plan_sha256: str,
    catalog_sha256: str,
    implementation_id: str,
    profile_id: str,
    selector: str,
    source_sha256: str,
    observed: str,
) -> dict[str, Any]:
    _, tests, _ = _test_bytes(selector)
    test_sha256 = _sha256_bytes(tests)
    command = canonical_unittest_selector_command(selector)
    binding = _invocation_binding(
        plan_sha256=plan_sha256,
        catalog_sha256=catalog_sha256,
        implementation_id=implementation_id,
        profile_id=profile_id,
        selector=selector,
        source_sha256=source_sha256,
        test_sha256=test_sha256,
        command=command,
    )
    receipt_outcome = _receipt_outcome(observed)
    counts = _counts(observed)
    receipt_document = build_receipt_document(
        binding=binding,
        producer_name=_PRODUCER_NAME,
        producer_version=__version__,
        outcome=receipt_outcome,
        counts=counts,
    )
    receipt = validate_receipt_document(
        receipt_document,
        expected_binding=binding,
    )
    return {
        "implementation_id": implementation_id,
        "profile_id": profile_id,
        "selector": selector,
        "source_sha256": source_sha256,
        "test_sha256": test_sha256,
        "command": command,
        "observed": observed,
        "return_code": 0 if observed == "pass" else 1,
        "timed_out": False,
        "duration_seconds": None,
        "stdout_sha256": None,
        "stderr_sha256": None,
        "invocation_binding": binding,
        "receipt_sha256": receipt.sha256,
        "receipt_outcome": receipt_outcome,
        "receipt_producer": {
            "name": _PRODUCER_NAME,
            "version": __version__,
        },
        "receipt_counts": counts,
        "observation_error": None,
    }


def _classify_observation(observation: object) -> tuple[str, str | None]:
    timed_out = observation.timed_out  # type: ignore[attr-defined]
    if timed_out:
        return "timeout", None
    receipt_error = observation.receipt_error  # type: ignore[attr-defined]
    if receipt_error is not None:
        return "error", str(receipt_error)
    receipt_outcome = observation.receipt_outcome  # type: ignore[attr-defined]
    return_code = observation.return_code  # type: ignore[attr-defined]
    if receipt_outcome == "passed" and return_code == 0:
        return "pass", None
    if receipt_outcome == "test_failure" and return_code == 1:
        return "fail", None
    return "error", "receipt_exit_mismatch"


def _execute_observation(
    *,
    root: Path,
    plan_sha256: str,
    catalog_sha256: str,
    implementation_id: str,
    profile_id: str,
    selector: str,
    source_sha256: str,
) -> dict[str, Any]:
    _, tests, _ = _test_bytes(selector)
    test_sha256 = _sha256_bytes(tests)
    command = canonical_unittest_selector_command(selector)
    binding = _invocation_binding(
        plan_sha256=plan_sha256,
        catalog_sha256=catalog_sha256,
        implementation_id=implementation_id,
        profile_id=profile_id,
        selector=selector,
        source_sha256=source_sha256,
        test_sha256=test_sha256,
        command=command,
    )
    process = run_command(
        command,
        state=f"mutation-result:{implementation_id}:{profile_id}:{selector}",
        cwd=root,
        timeout_seconds=30,
        pass_env=(),
        include_output=False,
        observer="outcome-receipt-v1",
        receipt_binding=binding,
    )
    observed, observation_error = _classify_observation(process)
    return {
        "implementation_id": implementation_id,
        "profile_id": profile_id,
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
    }


def _profile_outcome(observations: Sequence[str], *, baseline: bool) -> str:
    if any(item in {"error", "timeout"} for item in observations):
        return "indeterminate"
    if baseline:
        return "baseline_passed" if all(item == "pass" for item in observations) else "baseline_failed"
    return "survived" if all(item == "pass" for item in observations) else "killed"


def _reference_outcome(observations: Sequence[str]) -> str:
    if any(item in {"error", "timeout"} for item in observations):
        return "indeterminate"
    return (
        "reference_passed"
        if all(item == "pass" for item in observations)
        else "claim_violation_observed"
    )


def _expected_profile(
    *,
    plan: Mapping[str, object],
    catalog: Mapping[str, object],
    implementation_id: str,
    source_sha256: str,
    profile: Mapping[str, object],
    expected: Sequence[str],
    baseline: bool,
) -> dict[str, Any]:
    selectors = profile["selectors"]
    if not isinstance(selectors, list) or len(selectors) != len(expected):
        raise _error(
            f"mutation result profile {profile.get('profile_id')}",
            "selector cardinality does not match preregistered outcomes",
        )
    observations = [
        _expected_observation(
            plan_sha256=str(plan["plan_sha256"]),
            catalog_sha256=str(catalog["catalog_sha256"]),
            implementation_id=implementation_id,
            profile_id=str(profile["profile_id"]),
            selector=str(selector),
            source_sha256=source_sha256,
            observed=str(observed),
        )
        for selector, observed in zip(selectors, expected, strict=True)
    ]
    return {
        "profile_id": profile["profile_id"],
        "profile_role": profile["profile_role"],
        "selectors": observations,
        "outcome": _profile_outcome(expected, baseline=baseline),
    }


def _expected_reference(
    *,
    plan: Mapping[str, object],
    catalog: Mapping[str, object],
    implementation_id: str,
    source_sha256: str,
    expected: Sequence[str],
) -> dict[str, Any]:
    selectors = plan["reference_claim_checks"]
    if not isinstance(selectors, list) or len(selectors) != len(expected):
        raise _error(
            "mutation result reference selectors",
            "selector cardinality does not match preregistered outcomes",
        )
    observations = [
        _expected_observation(
            plan_sha256=str(plan["plan_sha256"]),
            catalog_sha256=str(catalog["catalog_sha256"]),
            implementation_id=implementation_id,
            profile_id=_REFERENCE_PROFILE_ID,
            selector=str(selector),
            source_sha256=source_sha256,
            observed=str(observed),
        )
        for selector, observed in zip(selectors, expected, strict=True)
    ]
    return {
        "profile_id": _REFERENCE_PROFILE_ID,
        "selectors": observations,
        "outcome": _reference_outcome(expected),
    }


def _expected_executed_record(
    *,
    plan: Mapping[str, object],
    catalog: Mapping[str, object],
    record_id: str,
    record_role: str,
    operator_id: str | None,
    mutant_id: str | None,
    catalog_status: str,
    source_sha256: str,
    source_ast_sha256: str | None,
    counts_toward_generic_generalization: bool,
    expected: Mapping[str, Sequence[str]],
    baseline: bool,
) -> dict[str, Any]:
    profiles_value = plan["calibration_profiles"]
    if not isinstance(profiles_value, list) or len(profiles_value) != 2:
        raise _error("mutation result plan profiles", "must contain exactly two profiles")
    profiles = [
        _expected_profile(
            plan=plan,
            catalog=catalog,
            implementation_id=record_id,
            source_sha256=source_sha256,
            profile=profile,
            expected=expected[key],
            baseline=baseline,
        )
        for profile, key in zip(
            profiles_value,
            ("strong", "weak"),
            strict=True,
        )
    ]
    reference = _expected_reference(
        plan=plan,
        catalog=catalog,
        implementation_id=record_id,
        source_sha256=source_sha256,
        expected=expected["reference"],
    )
    return {
        "record_id": record_id,
        "implementation_id": record_id,
        "record_role": record_role,
        "operator_id": operator_id,
        "mutant_id": mutant_id,
        "catalog_status": catalog_status,
        "source_sha256": source_sha256,
        "source_ast_sha256": source_ast_sha256,
        "execution_status": "executed",
        "counts_toward_generic_generalization": (
            counts_toward_generic_generalization
        ),
        "profiles": profiles,
        "reference": reference,
        "cost": {
            "status": "measured",
            "command_count": 5,
            "selector_count": 5,
            "wall_clock_seconds": None,
            "cpu_seconds": None,
            "missing_reason": None,
        },
    }


def _expected_generation_record(record: Mapping[str, object]) -> dict[str, Any]:
    catalog_status = str(record["status"])
    execution_status = {
        "duplicate": "not_executed_duplicate",
        "not_applicable": "not_executed_not_applicable",
        "invalid": "not_executed_invalid",
    }.get(catalog_status)
    if execution_status is None:
        raise _error(
            "mutation result generation record",
            f"unsupported non-executed status {catalog_status!r}",
        )
    return {
        "record_id": record["mutant_id"],
        "implementation_id": None,
        "record_role": "generation_control",
        "operator_id": record["operator_id"],
        "mutant_id": record["mutant_id"],
        "catalog_status": catalog_status,
        "source_sha256": record["mutated_source_sha256"],
        "source_ast_sha256": record["mutated_ast_sha256"],
        "execution_status": execution_status,
        "counts_toward_generic_generalization": False,
        "profiles": [],
        "reference": None,
        "cost": {
            "status": "not_executed",
            "command_count": 0,
            "selector_count": 0,
            "wall_clock_seconds": 0.0,
            "cpu_seconds": 0.0,
            "missing_reason": execution_status,
        },
    }


def _expected_semantic_result(
    plan: Mapping[str, object],
    catalog: Mapping[str, object],
) -> dict[str, Any]:
    source = plan["source_scope"]
    if not isinstance(source, dict):
        raise _error("mutation result source scope", "must be an object")
    candidate = _expected_executed_record(
        plan=plan,
        catalog=catalog,
        record_id=_CANDIDATE_ID,
        record_role="candidate_baseline",
        operator_id=None,
        mutant_id=None,
        catalog_status="candidate",
        source_sha256=str(source["source_sha256"]),
        source_ast_sha256=str(source["ast_sha256"]),
        counts_toward_generic_generalization=False,
        expected=_EXPECTED_CANDIDATE,
        baseline=True,
    )

    records: list[dict[str, Any]] = []
    catalog_records = catalog["mutants"]
    if not isinstance(catalog_records, list) or len(catalog_records) != 6:
        raise _error("mutation result catalog mutants", "must contain six records")
    for record in catalog_records:
        status = record["status"]
        if status == "generated":
            operator_id = str(record["operator_id"])
            expected = _EXPECTED_BY_OPERATOR.get(operator_id)
            if expected is None:
                raise _error(
                    "mutation result operator",
                    f"missing preregistered outcomes for {operator_id!r}",
                )
            records.append(
                _expected_executed_record(
                    plan=plan,
                    catalog=catalog,
                    record_id=str(record["mutant_id"]),
                    record_role="generic_operator",
                    operator_id=operator_id,
                    mutant_id=str(record["mutant_id"]),
                    catalog_status="generated",
                    source_sha256=str(record["mutated_source_sha256"]),
                    source_ast_sha256=str(record["mutated_ast_sha256"]),
                    counts_toward_generic_generalization=True,
                    expected=expected,
                    baseline=False,
                )
            )
        else:
            records.append(_expected_generation_record(record))

    known = catalog["known_challenge_control"]
    if not isinstance(known, dict):
        raise _error("mutation result known control", "must be an object")
    records.append(
        _expected_executed_record(
            plan=plan,
            catalog=catalog,
            record_id=str(known["mutant_id"]),
            record_role="historical_challenge_control",
            operator_id=None,
            mutant_id=str(known["mutant_id"]),
            catalog_status="historical_control",
            source_sha256=str(known["mutated_source_sha256"]),
            source_ast_sha256=str(known["mutated_ast_sha256"]),
            counts_toward_generic_generalization=False,
            expected=_EXPECTED_KNOWN_CONTROL,
            baseline=False,
        )
    )

    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "study_id": "DW-001",
        "result_id": RESULT_ID,
        "partition": "development",
        "plan_sha256": plan["plan_sha256"],
        "catalog_sha256": catalog["catalog_sha256"],
        "created_at": None,
        "runtime": None,
        "source": {
            "source_id": source["source_id"],
            "source_sha256": source["source_sha256"],
            "source_ast_sha256": source["ast_sha256"],
            "target_id": catalog["target"]["target_id"],
        },
        "candidate_baseline": candidate,
        "records": records,
        "summary": {
            "candidate_baseline_valid": True,
            "catalog_records": 6,
            "generic_mutants_executed": 3,
            "historical_controls_executed": 1,
            "generation_records_not_executed": 3,
            "generic_strong_killed": 3,
            "generic_strong_survived": 0,
            "generic_strong_indeterminate": 0,
            "generic_weak_killed": 0,
            "generic_weak_survived": 3,
            "generic_weak_indeterminate": 0,
            "generic_claim_violations_observed": 3,
            "mutation_score": None,
        },
        "policy": {
            "retain_complete_mutant_table": True,
            "headline_score": None,
            "universal_threshold": None,
            "merge_blocker_authorized": False,
            "ecological_inference_allowed": False,
            "holdout_selected": False,
            "primary_denominator_eligible": False,
            "generic_operator_generalization_allowed": False,
        },
        "cost": {
            "status": "measured",
            "implementation_count": 5,
            "command_count": 25,
            "selector_count": 25,
            "wall_clock_seconds": None,
            "cpu_seconds": None,
            "missing_reason": None,
        },
        "semantic_sha256": None,
        "report_sha256": None,
    }


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
    implementations: list[object] = [normalized.get("candidate_baseline")]
    records = normalized.get("records")
    if isinstance(records, list):
        implementations.extend(records)
    for implementation in implementations:
        if not isinstance(implementation, dict):
            continue
        cost = implementation.get("cost")
        if isinstance(cost, dict) and cost.get("status") == "measured":
            cost["wall_clock_seconds"] = None
            cost["cpu_seconds"] = None
        profiles = implementation.get("profiles")
        if isinstance(profiles, list):
            for profile in profiles:
                if not isinstance(profile, dict):
                    continue
                selectors = profile.get("selectors")
                if isinstance(selectors, list):
                    for selector in selectors:
                        if isinstance(selector, dict):
                            selector["duration_seconds"] = None
                            selector["stdout_sha256"] = None
                            selector["stderr_sha256"] = None
        reference = implementation.get("reference")
        if isinstance(reference, dict):
            selectors = reference.get("selectors")
            if isinstance(selectors, list):
                for selector in selectors:
                    if isinstance(selector, dict):
                        selector["duration_seconds"] = None
                        selector["stdout_sha256"] = None
                        selector["stderr_sha256"] = None
    return normalized


def compute_mutation_result_semantic_sha256(document: dict[str, Any]) -> str:
    """Hash stable result semantics while excluding runtime and timing fields."""

    if not isinstance(document, dict):
        raise _error("claim-scoped mutation result", "must be an object")
    return sha256_document(_semantic_view(document))


def compute_mutation_result_report_sha256(document: dict[str, Any]) -> str:
    """Hash the complete result with only its report digest normalized."""

    if not isinstance(document, dict):
        raise _error("claim-scoped mutation result", "must be an object")
    normalized = deepcopy(document)
    normalized["report_sha256"] = None
    return sha256_document(normalized)


def _differences(
    expected: object,
    observed: object,
    *,
    context: str,
) -> list[str]:
    errors: list[str] = []
    if isinstance(expected, dict):
        if not isinstance(observed, dict):
            return [f"{context}: must be an object"]
        expected_keys = set(expected)
        observed_keys = set(observed)
        if expected_keys != observed_keys:
            errors.append(
                f"{context}: field mismatch; missing={sorted(expected_keys - observed_keys)}, "
                f"extra={sorted(observed_keys - expected_keys)}"
            )
        for key in sorted(expected_keys & observed_keys):
            errors.extend(
                _differences(
                    expected[key],
                    observed[key],
                    context=f"{context}.{key}",
                )
            )
        return errors
    if isinstance(expected, list):
        if not isinstance(observed, list):
            return [f"{context}: must be a list"]
        if len(expected) != len(observed):
            errors.append(
                f"{context}: length mismatch; expected {len(expected)}, "
                f"observed {len(observed)}"
            )
        for index, (expected_item, observed_item) in enumerate(
            zip(expected, observed, strict=False)
        ):
            errors.extend(
                _differences(
                    expected_item,
                    observed_item,
                    context=f"{context}[{index}]",
                )
            )
        return errors
    if observed != expected:
        errors.append(
            f"{context}: expected={expected!r}, observed={observed!r}"
        )
    return errors


def _materialize_source_for_record(record: Mapping[str, object]) -> str:
    operator_id = str(record["operator_id"])
    status, source, ast_sha256, compile_valid, _ = _mutated_source(operator_id)
    if status != "generated" or source is None or compile_valid is not True:
        raise _error(
            f"mutation result operator {operator_id}",
            "did not regenerate a compile-valid source",
        )
    source_sha256 = _sha256_bytes(source.encode("utf-8"))
    if source_sha256 != record["mutated_source_sha256"]:
        raise _error(
            f"mutation result operator {operator_id}.source_sha256",
            "does not match frozen catalog",
        )
    if ast_sha256 != record["mutated_ast_sha256"]:
        raise _error(
            f"mutation result operator {operator_id}.ast_sha256",
            "does not match frozen catalog",
        )
    return source


def _execute_record(
    *,
    plan: Mapping[str, object],
    catalog: Mapping[str, object],
    expected_record: Mapping[str, object],
    source: str,
) -> dict[str, Any]:
    implementation_id = str(expected_record["implementation_id"])
    source_sha256 = _sha256_bytes(source.encode("utf-8"))
    if source_sha256 != expected_record["source_sha256"]:
        raise _error(
            f"mutation result {implementation_id}.source_sha256",
            "does not match frozen expected source identity",
        )
    started_wall = time.perf_counter()
    started_cpu = time.process_time()
    with tempfile.TemporaryDirectory(
        prefix=f"deltawitness-mutation-result-{implementation_id[:12]}-"
    ) as directory:
        root = Path(directory)
        (root / "src").mkdir()
        (root / "tests").mkdir()
        (root / "src" / "access.py").write_text(source, encoding="utf-8")
        (root / "tests" / "test_access.py").write_text(
            _CALIBRATION_TESTS,
            encoding="utf-8",
        )
        (root / "tests" / "test_hidden_claim.py").write_text(
            _REFERENCE_TESTS,
            encoding="utf-8",
        )

        actual_profiles: list[dict[str, Any]] = []
        for expected_profile in expected_record["profiles"]:
            actual_selectors = [
                _execute_observation(
                    root=root,
                    plan_sha256=str(plan["plan_sha256"]),
                    catalog_sha256=str(catalog["catalog_sha256"]),
                    implementation_id=implementation_id,
                    profile_id=str(expected_profile["profile_id"]),
                    selector=str(expected_selector["selector"]),
                    source_sha256=source_sha256,
                )
                for expected_selector in expected_profile["selectors"]
            ]
            observed = [item["observed"] for item in actual_selectors]
            outcome = _profile_outcome(
                observed,
                baseline=(expected_record["record_role"] == "candidate_baseline"),
            )
            actual_profiles.append(
                {
                    "profile_id": expected_profile["profile_id"],
                    "profile_role": expected_profile["profile_role"],
                    "selectors": actual_selectors,
                    "outcome": outcome,
                }
            )

        expected_reference = expected_record["reference"]
        assert isinstance(expected_reference, dict)
        actual_reference_selectors = [
            _execute_observation(
                root=root,
                plan_sha256=str(plan["plan_sha256"]),
                catalog_sha256=str(catalog["catalog_sha256"]),
                implementation_id=implementation_id,
                profile_id=_REFERENCE_PROFILE_ID,
                selector=str(expected_selector["selector"]),
                source_sha256=source_sha256,
            )
            for expected_selector in expected_reference["selectors"]
        ]
        actual_reference = {
            "profile_id": _REFERENCE_PROFILE_ID,
            "selectors": actual_reference_selectors,
            "outcome": _reference_outcome(
                [item["observed"] for item in actual_reference_selectors]
            ),
        }

    wall = time.perf_counter() - started_wall
    cpu = time.process_time() - started_cpu
    actual = {
        **{
            key: deepcopy(value)
            for key, value in expected_record.items()
            if key not in {"profiles", "reference", "cost"}
        },
        "profiles": actual_profiles,
        "reference": actual_reference,
        "cost": {
            "status": "measured",
            "command_count": 5,
            "selector_count": 5,
            "wall_clock_seconds": round(wall, 6),
            "cpu_seconds": round(cpu, 6),
            "missing_reason": None,
        },
    }
    differences = _differences(
        _semantic_view({
            **_expected_semantic_result(plan, catalog),
            "candidate_baseline": expected_record,
            "records": [],
        })["candidate_baseline"],
        _semantic_view({
            **_expected_semantic_result(plan, catalog),
            "candidate_baseline": actual,
            "records": [],
        })["candidate_baseline"],
        context=f"claim-scoped mutation execution {implementation_id}",
    )
    if differences:
        raise _error(
            f"claim-scoped mutation execution {implementation_id}",
            "; ".join(differences),
        )
    return actual


def _preflight(
    plan: object,
    catalog: object,
) -> tuple[dict[str, Any], dict[str, Any]]:
    plan_valid, plan_errors = verify_claim_scoped_mutation_plan_document(plan)
    catalog_valid, catalog_errors = verify_claim_scoped_mutant_catalog_document(
        catalog,
        plan,
    )
    errors = [
        *[f"plan: {error}" for error in plan_errors if not plan_valid],
        *[f"catalog: {error}" for error in catalog_errors if not catalog_valid],
    ]
    if errors:
        raise _error("claim-scoped mutation result preflight", "; ".join(errors))
    if not isinstance(plan, dict) or not isinstance(catalog, dict):
        raise _error("claim-scoped mutation result preflight", "sources must be objects")
    if plan["execution_authorized"] is not False:
        raise _error(
            "claim-scoped mutation result plan.execution_authorized",
            "must remain false; this runner is a separately reviewed fixed development execution",
        )
    return plan, catalog


def run_claim_scoped_mutation_result(
    plan: object,
    catalog: object,
) -> dict[str, Any]:
    """Execute the exact frozen owned-synthetic catalog and paired profiles."""

    normalized_plan, normalized_catalog = _preflight(plan, catalog)
    expected = _expected_semantic_result(normalized_plan, normalized_catalog)
    started_wall = time.perf_counter()
    started_cpu = time.process_time()

    candidate = _execute_record(
        plan=normalized_plan,
        catalog=normalized_catalog,
        expected_record=expected["candidate_baseline"],
        source=_weak_proxy.CANDIDATE_CODE,
    )

    catalog_records = normalized_catalog["mutants"]
    assert isinstance(catalog_records, list)
    expected_records = expected["records"]
    actual_records: list[dict[str, Any]] = []
    catalog_by_id = {
        str(record["mutant_id"]): record
        for record in catalog_records
    }
    for expected_record in expected_records:
        if expected_record["execution_status"] != "executed":
            actual_records.append(deepcopy(expected_record))
            continue
        if expected_record["record_role"] == "historical_challenge_control":
            source = _weak_proxy.MUTANT_CODE
        else:
            frozen_record = catalog_by_id[str(expected_record["mutant_id"])]
            source = _materialize_source_for_record(frozen_record)
        actual_records.append(
            _execute_record(
                plan=normalized_plan,
                catalog=normalized_catalog,
                expected_record=expected_record,
                source=source,
            )
        )

    wall = time.perf_counter() - started_wall
    cpu = time.process_time() - started_cpu
    result: dict[str, Any] = {
        **{
            key: deepcopy(value)
            for key, value in expected.items()
            if key not in {
                "created_at",
                "runtime",
                "candidate_baseline",
                "records",
                "cost",
                "semantic_sha256",
                "report_sha256",
            }
        },
        "created_at": datetime.now(timezone.utc).isoformat().replace(
            "+00:00", "Z"
        ),
        "runtime": {
            "tool_version": __version__,
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
            "platform_system": platform.system(),
        },
        "candidate_baseline": candidate,
        "records": actual_records,
        "cost": {
            "status": "measured",
            "implementation_count": 5,
            "command_count": 25,
            "selector_count": 25,
            "wall_clock_seconds": round(wall, 6),
            "cpu_seconds": round(cpu, 6),
            "missing_reason": None,
        },
        "semantic_sha256": None,
        "report_sha256": None,
    }
    result["semantic_sha256"] = compute_mutation_result_semantic_sha256(result)
    result["report_sha256"] = compute_mutation_result_report_sha256(result)
    valid, errors = verify_claim_scoped_mutation_result_document(
        result,
        normalized_plan,
        normalized_catalog,
    )
    if not valid:
        raise _error(
            "claim-scoped mutation result self-verification",
            "; ".join(errors),
        )
    return result


def _finite_nonnegative(value: object, *, context: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _error(context, "must be a finite nonnegative number")
    numeric = float(value)
    if not math.isfinite(numeric) or numeric < 0.0:
        raise _error(context, "must be a finite nonnegative number")


def _validate_volatiles(document: Mapping[str, object]) -> None:
    created_at = document.get("created_at")
    if not isinstance(created_at, str) or not created_at:
        raise _error("claim-scoped mutation result.created_at", "must be a non-empty string")
    runtime = document.get("runtime")
    if not isinstance(runtime, dict) or set(runtime) != {
        "tool_version",
        "python_implementation",
        "python_version",
        "platform_system",
    }:
        raise _error("claim-scoped mutation result.runtime", "has invalid fields")
    if any(not isinstance(value, str) or not value for value in runtime.values()):
        raise _error("claim-scoped mutation result.runtime", "values must be non-empty strings")

    root_cost = document.get("cost")
    if not isinstance(root_cost, dict):
        raise _error("claim-scoped mutation result.cost", "must be an object")
    _finite_nonnegative(
        root_cost.get("wall_clock_seconds"),
        context="claim-scoped mutation result.cost.wall_clock_seconds",
    )
    _finite_nonnegative(
        root_cost.get("cpu_seconds"),
        context="claim-scoped mutation result.cost.cpu_seconds",
    )

    implementations: list[object] = [document.get("candidate_baseline")]
    records = document.get("records")
    if not isinstance(records, list):
        raise _error("claim-scoped mutation result.records", "must be a list")
    implementations.extend(records)
    for implementation in implementations:
        if not isinstance(implementation, dict):
            raise _error("claim-scoped mutation result implementation", "must be an object")
        cost = implementation.get("cost")
        if not isinstance(cost, dict):
            raise _error("claim-scoped mutation result implementation.cost", "must be an object")
        _finite_nonnegative(
            cost.get("wall_clock_seconds"),
            context="claim-scoped mutation result implementation.cost.wall_clock_seconds",
        )
        _finite_nonnegative(
            cost.get("cpu_seconds"),
            context="claim-scoped mutation result implementation.cost.cpu_seconds",
        )
        for profile in implementation.get("profiles", []):
            if not isinstance(profile, dict):
                raise _error("claim-scoped mutation result profile", "must be an object")
            for selector in profile.get("selectors", []):
                _validate_observation_volatiles(selector)
        reference = implementation.get("reference")
        if isinstance(reference, dict):
            for selector in reference.get("selectors", []):
                _validate_observation_volatiles(selector)


def _validate_observation_volatiles(selector: object) -> None:
    if not isinstance(selector, dict):
        raise _error("claim-scoped mutation result selector", "must be an object")
    _finite_nonnegative(
        selector.get("duration_seconds"),
        context="claim-scoped mutation result selector.duration_seconds",
    )
    for field in ("stdout_sha256", "stderr_sha256"):
        value = selector.get(field)
        if (
            not isinstance(value, str)
            or len(value) != 64
            or any(character not in "0123456789abcdef" for character in value)
        ):
            raise _error(
                f"claim-scoped mutation result selector.{field}",
                "must be a lowercase SHA-256 digest",
            )


def verify_claim_scoped_mutation_result_document(
    document: object,
    plan: object,
    catalog: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify source relations, stable semantics, volatile fields, and digests."""

    try:
        normalized_plan, normalized_catalog = _preflight(plan, catalog)
        if not isinstance(document, dict):
            raise _error("claim-scoped mutation result", "must be an object")
        if set(document) != _ROOT_FIELDS:
            raise _error(
                "claim-scoped mutation result",
                f"field mismatch; missing={sorted(_ROOT_FIELDS - set(document))}, "
                f"extra={sorted(set(document) - _ROOT_FIELDS)}",
            )
        _validate_volatiles(document)
        expected = _expected_semantic_result(normalized_plan, normalized_catalog)
        actual_semantic = _semantic_view(document)
        differences = _differences(
            expected,
            actual_semantic,
            context="claim-scoped mutation result",
        )
        recorded_semantic = document.get("semantic_sha256")
        computed_semantic = compute_mutation_result_semantic_sha256(document)
        if recorded_semantic != computed_semantic:
            differences.append(
                "claim-scoped mutation result.semantic_sha256: digest mismatch"
            )
        recorded_report = document.get("report_sha256")
        computed_report = compute_mutation_result_report_sha256(document)
        if recorded_report != computed_report:
            differences.append(
                "claim-scoped mutation result.report_sha256: digest mismatch"
            )
    except (
        DW001MutationResultError,
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
        if isinstance(exc, DW001MutationResultError):
            return False, (str(exc),)
        return False, (
            "claim-scoped mutation result: verification failed closed: "
            f"{type(exc).__name__}: {exc}",
        )
    unique = tuple(dict.fromkeys(differences))
    return not unique, unique


__all__ = [
    "DW001MutationResultError",
    "RESULT_ID",
    "RESULT_SCHEMA_VERSION",
    "compute_mutation_result_report_sha256",
    "compute_mutation_result_semantic_sha256",
    "run_claim_scoped_mutation_result",
    "verify_claim_scoped_mutation_result_document",
]
