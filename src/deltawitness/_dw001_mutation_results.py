"""Typed execution results for the frozen DW-001 mutation catalog.

The runner executes only the exact project-owned candidate, three generic
mutants, historical challenge control, selector profiles, and reference checks
frozen by PR #38 and issue #39. Duplicate, not-applicable, and invalid catalog
records remain visible but are never executed.

Complete but unexpected observations are retained as negative results. Frozen
expectations remain explicit and separate from observed evidence; concordance
is derived rather than used as a validity condition. Malformed, contradictory,
or relationally inconsistent evidence still fails closed.
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
    "analysis",
    "policy",
    "cost",
    "semantic_sha256",
    "report_sha256",
}
_OBSERVATION_FIELDS = {
    "implementation_id",
    "profile_id",
    "selector",
    "source_sha256",
    "test_sha256",
    "command",
    "expected_observed",
    "observed",
    "concordant",
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
}
_PROFILE_FIELDS = {
    "profile_id",
    "profile_role",
    "selectors",
    "expected_outcome",
    "outcome",
    "concordant",
}
_REFERENCE_FIELDS = {
    "profile_id",
    "selectors",
    "expected_outcome",
    "outcome",
    "concordant",
}
_RECORD_FIELDS = {
    "record_id",
    "implementation_id",
    "record_role",
    "operator_id",
    "mutant_id",
    "catalog_status",
    "source_sha256",
    "source_ast_sha256",
    "execution_status",
    "counts_toward_generic_generalization",
    "profiles",
    "reference",
    "concordant",
    "cost",
}
_RECORD_COST_FIELDS = {
    "status",
    "command_count",
    "selector_count",
    "wall_clock_seconds",
    "cpu_seconds",
    "missing_reason",
}
_ROOT_COST_FIELDS = {
    "status",
    "implementation_count",
    "command_count",
    "selector_count",
    "wall_clock_seconds",
    "cpu_seconds",
    "missing_reason",
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


def _test_bytes(selector: str) -> tuple[str, bytes]:
    if selector.startswith("test_access.AccessTests."):
        return "test_access.py", _CALIBRATION_TESTS.encode("utf-8")
    if selector.startswith("test_hidden_claim.HiddenClaimTests."):
        return "test_hidden_claim.py", _REFERENCE_TESTS.encode("utf-8")
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
    """Build canonical complete pass/fail evidence for one selector."""

    _, tests = _test_bytes(selector)
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
    receipt = validate_receipt_document(
        build_receipt_document(
            binding=binding,
            producer_name=_PRODUCER_NAME,
            producer_version=__version__,
            outcome=receipt_outcome,
            counts=counts,
        ),
        expected_binding=binding,
    )
    return {
        "implementation_id": implementation_id,
        "profile_id": profile_id,
        "selector": selector,
        "source_sha256": source_sha256,
        "test_sha256": test_sha256,
        "command": command,
        "expected_observed": observed,
        "observed": observed,
        "concordant": True,
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
    if bool(getattr(observation, "timed_out")):
        return "timeout", None
    receipt_error = getattr(observation, "receipt_error")
    if receipt_error is not None:
        return "error", str(receipt_error)
    receipt_outcome = getattr(observation, "receipt_outcome")
    return_code = getattr(observation, "return_code")
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
    """Execute one exact selector through the existing typed receipt adapter."""

    _, tests = _test_bytes(selector)
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
        return (
            "baseline_passed"
            if all(item == "pass" for item in observations)
            else "baseline_failed"
        )
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
    expected_outcome = _profile_outcome(expected, baseline=baseline)
    return {
        "profile_id": profile["profile_id"],
        "profile_role": profile["profile_role"],
        "selectors": observations,
        "expected_outcome": expected_outcome,
        "outcome": expected_outcome,
        "concordant": True,
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
    expected_outcome = _reference_outcome(expected)
    return {
        "profile_id": _REFERENCE_PROFILE_ID,
        "selectors": observations,
        "expected_outcome": expected_outcome,
        "outcome": expected_outcome,
        "concordant": True,
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
        "concordant": True,
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
        "concordant": True,
        "cost": {
            "status": "not_executed",
            "command_count": 0,
            "selector_count": 0,
            "wall_clock_seconds": 0.0,
            "cpu_seconds": 0.0,
            "missing_reason": execution_status,
        },
    }


def _expected_templates(
    plan: Mapping[str, object],
    catalog: Mapping[str, object],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
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
        if record["status"] == "generated":
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
    return candidate, records


def _profile_for(record: Mapping[str, object], profile_id: str) -> Mapping[str, object]:
    profiles = record.get("profiles")
    if not isinstance(profiles, list):
        raise _error("mutation result summary profiles", "must be a list")
    matches = [profile for profile in profiles if profile.get("profile_id") == profile_id]
    if len(matches) != 1 or not isinstance(matches[0], dict):
        raise _error(
            "mutation result summary profile",
            f"expected one {profile_id!r} profile",
        )
    return matches[0]


def _derive_summary(
    candidate: Mapping[str, object],
    records: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    generic = [record for record in records if record.get("record_role") == "generic_operator"]
    historical = [
        record
        for record in records
        if record.get("record_role") == "historical_challenge_control"
    ]
    generation = [
        record for record in records if record.get("record_role") == "generation_control"
    ]
    candidate_reference = candidate.get("reference")
    candidate_profiles = candidate.get("profiles")
    candidate_valid = (
        isinstance(candidate_profiles, list)
        and all(
            isinstance(profile, dict) and profile.get("outcome") == "baseline_passed"
            for profile in candidate_profiles
        )
        and isinstance(candidate_reference, dict)
        and candidate_reference.get("outcome") == "reference_passed"
    )
    return {
        "candidate_baseline_valid": candidate_valid,
        "catalog_records": 6,
        "generic_mutants_executed": len(generic),
        "historical_controls_executed": len(historical),
        "generation_records_not_executed": len(generation),
        "generic_strong_killed": sum(
            _profile_for(record, _STRONG_PROFILE_ID).get("outcome") == "killed"
            for record in generic
        ),
        "generic_strong_survived": sum(
            _profile_for(record, _STRONG_PROFILE_ID).get("outcome") == "survived"
            for record in generic
        ),
        "generic_strong_indeterminate": sum(
            _profile_for(record, _STRONG_PROFILE_ID).get("outcome") == "indeterminate"
            for record in generic
        ),
        "generic_weak_killed": sum(
            _profile_for(record, _WEAK_PROFILE_ID).get("outcome") == "killed"
            for record in generic
        ),
        "generic_weak_survived": sum(
            _profile_for(record, _WEAK_PROFILE_ID).get("outcome") == "survived"
            for record in generic
        ),
        "generic_weak_indeterminate": sum(
            _profile_for(record, _WEAK_PROFILE_ID).get("outcome") == "indeterminate"
            for record in generic
        ),
        "generic_claim_violations_observed": sum(
            isinstance(record.get("reference"), dict)
            and record["reference"].get("outcome") == "claim_violation_observed"
            for record in generic
        ),
        "mutation_score": None,
    }


def _derive_analysis(
    candidate: Mapping[str, object],
    records: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    unexpected_observations = 0
    unexpected_profiles = 0
    unexpected_references = 0
    unexpected_record_ids: list[str] = []
    for record in [candidate, *records]:
        profiles = record.get("profiles")
        if isinstance(profiles, list):
            for profile in profiles:
                if not isinstance(profile, dict):
                    continue
                if profile.get("concordant") is not True:
                    unexpected_profiles += 1
                selectors = profile.get("selectors")
                if isinstance(selectors, list):
                    unexpected_observations += sum(
                        isinstance(selector, dict)
                        and selector.get("concordant") is not True
                        for selector in selectors
                    )
        reference = record.get("reference")
        if isinstance(reference, dict):
            if reference.get("concordant") is not True:
                unexpected_references += 1
            selectors = reference.get("selectors")
            if isinstance(selectors, list):
                unexpected_observations += sum(
                    isinstance(selector, dict)
                    and selector.get("concordant") is not True
                    for selector in selectors
                )
        if record.get("concordant") is not True:
            unexpected_record_ids.append(str(record.get("record_id")))
    return {
        "status": "expected" if not unexpected_record_ids else "unexpected",
        "candidate_baseline_concordant": candidate.get("concordant") is True,
        "unexpected_observation_count": unexpected_observations,
        "unexpected_profile_count": unexpected_profiles,
        "unexpected_reference_count": unexpected_references,
        "unexpected_record_ids": unexpected_record_ids,
    }


def _policy() -> dict[str, object]:
    return {
        "retain_complete_mutant_table": True,
        "headline_score": None,
        "universal_threshold": None,
        "merge_blocker_authorized": False,
        "ecological_inference_allowed": False,
        "holdout_selected": False,
        "primary_denominator_eligible": False,
        "generic_operator_generalization_allowed": False,
    }


def _base_result(
    plan: Mapping[str, object],
    catalog: Mapping[str, object],
    candidate: Mapping[str, object],
    records: Sequence[Mapping[str, object]],
) -> dict[str, Any]:
    source = plan["source_scope"]
    if not isinstance(source, dict):
        raise _error("mutation result source", "must be an object")
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
        "candidate_baseline": deepcopy(candidate),
        "records": deepcopy(list(records)),
        "summary": _derive_summary(candidate, records),
        "analysis": _derive_analysis(candidate, records),
        "policy": _policy(),
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


def _enrich_observation(
    raw: Mapping[str, object],
    expected: Mapping[str, object],
) -> dict[str, Any]:
    observation = deepcopy(dict(raw))
    observation["expected_observed"] = expected["expected_observed"]
    observation["concordant"] = (
        observation.get("observed") == expected["expected_observed"]
    )
    return observation


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
                _enrich_observation(
                    _execute_observation(
                        root=root,
                        plan_sha256=str(plan["plan_sha256"]),
                        catalog_sha256=str(catalog["catalog_sha256"]),
                        implementation_id=implementation_id,
                        profile_id=str(expected_profile["profile_id"]),
                        selector=str(expected_selector["selector"]),
                        source_sha256=source_sha256,
                    ),
                    expected_selector,
                )
                for expected_selector in expected_profile["selectors"]
            ]
            outcome = _profile_outcome(
                [item["observed"] for item in actual_selectors],
                baseline=(expected_record["record_role"] == "candidate_baseline"),
            )
            actual_profiles.append(
                {
                    "profile_id": expected_profile["profile_id"],
                    "profile_role": expected_profile["profile_role"],
                    "selectors": actual_selectors,
                    "expected_outcome": expected_profile["expected_outcome"],
                    "outcome": outcome,
                    "concordant": outcome == expected_profile["expected_outcome"],
                }
            )

        expected_reference = expected_record["reference"]
        if not isinstance(expected_reference, dict):
            raise _error(
                f"mutation result {implementation_id}.reference",
                "must be an object for executed records",
            )
        actual_reference_selectors = [
            _enrich_observation(
                _execute_observation(
                    root=root,
                    plan_sha256=str(plan["plan_sha256"]),
                    catalog_sha256=str(catalog["catalog_sha256"]),
                    implementation_id=implementation_id,
                    profile_id=_REFERENCE_PROFILE_ID,
                    selector=str(expected_selector["selector"]),
                    source_sha256=source_sha256,
                ),
                expected_selector,
            )
            for expected_selector in expected_reference["selectors"]
        ]
        reference_outcome = _reference_outcome(
            [item["observed"] for item in actual_reference_selectors]
        )
        actual_reference = {
            "profile_id": _REFERENCE_PROFILE_ID,
            "selectors": actual_reference_selectors,
            "expected_outcome": expected_reference["expected_outcome"],
            "outcome": reference_outcome,
            "concordant": reference_outcome == expected_reference["expected_outcome"],
        }

    wall = time.perf_counter() - started_wall
    cpu = time.process_time() - started_cpu
    return {
        **{
            key: deepcopy(value)
            for key, value in expected_record.items()
            if key not in {"profiles", "reference", "concordant", "cost"}
        },
        "profiles": actual_profiles,
        "reference": actual_reference,
        "concordant": (
            all(profile["concordant"] for profile in actual_profiles)
            and actual_reference["concordant"]
        ),
        "cost": {
            "status": "measured",
            "command_count": 5,
            "selector_count": 5,
            "wall_clock_seconds": round(wall, 6),
            "cpu_seconds": round(cpu, 6),
            "missing_reason": None,
        },
    }


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
    """Execute the exact frozen catalog and retain expected or unexpected evidence."""

    normalized_plan, normalized_catalog = _preflight(plan, catalog)
    candidate_template, record_templates = _expected_templates(
        normalized_plan,
        normalized_catalog,
    )
    started_wall = time.perf_counter()
    started_cpu = time.process_time()

    candidate = _execute_record(
        plan=normalized_plan,
        catalog=normalized_catalog,
        expected_record=candidate_template,
        source=_weak_proxy.CANDIDATE_CODE,
    )

    catalog_records = normalized_catalog["mutants"]
    if not isinstance(catalog_records, list):
        raise _error("mutation result catalog records", "must be a list")
    catalog_by_id = {
        str(record["mutant_id"]): record
        for record in catalog_records
    }
    actual_records: list[dict[str, Any]] = []
    for template in record_templates:
        if template["execution_status"] != "executed":
            actual_records.append(deepcopy(template))
            continue
        if template["record_role"] == "historical_challenge_control":
            source = _weak_proxy.MUTANT_CODE
        else:
            source = _materialize_source_for_record(
                catalog_by_id[str(template["mutant_id"])]
            )
        actual_records.append(
            _execute_record(
                plan=normalized_plan,
                catalog=normalized_catalog,
                expected_record=template,
                source=source,
            )
        )

    wall = time.perf_counter() - started_wall
    cpu = time.process_time() - started_cpu
    result = _base_result(
        normalized_plan,
        normalized_catalog,
        candidate,
        actual_records,
    )
    result["created_at"] = datetime.now(timezone.utc).isoformat().replace(
        "+00:00", "Z"
    )
    result["runtime"] = {
        "tool_version": __version__,
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "platform_system": platform.system(),
    }
    result["cost"] = {
        "status": "measured",
        "implementation_count": 5,
        "command_count": 25,
        "selector_count": 25,
        "wall_clock_seconds": round(wall, 6),
        "cpu_seconds": round(cpu, 6),
        "missing_reason": None,
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


def _validate_runtime_and_costs(document: Mapping[str, object]) -> None:
    created_at = document.get("created_at")
    if not isinstance(created_at, str) or not created_at:
        raise _error("claim-scoped mutation result.created_at", "must be a non-empty string")
    runtime = _exact_keys(
        document.get("runtime"),
        {
            "tool_version",
            "python_implementation",
            "python_version",
            "platform_system",
        },
        context="claim-scoped mutation result.runtime",
    )
    if any(not isinstance(value, str) or not value for value in runtime.values()):
        raise _error("claim-scoped mutation result.runtime", "values must be non-empty strings")
    root_cost = _exact_keys(
        document.get("cost"),
        _ROOT_COST_FIELDS,
        context="claim-scoped mutation result.cost",
    )
    if (
        root_cost["status"] != "measured"
        or root_cost["implementation_count"] != 5
        or root_cost["command_count"] != 25
        or root_cost["selector_count"] != 25
        or root_cost["missing_reason"] is not None
    ):
        raise _error(
            "claim-scoped mutation result.cost",
            "does not match fixed execution contract",
        )
    _finite_nonnegative(
        root_cost["wall_clock_seconds"],
        context="claim-scoped mutation result.cost.wall_clock_seconds",
    )
    _finite_nonnegative(
        root_cost["cpu_seconds"],
        context="claim-scoped mutation result.cost.cpu_seconds",
    )


def _canonical_observation(
    actual: object,
    expected: Mapping[str, object],
    *,
    plan: Mapping[str, object],
    catalog: Mapping[str, object],
) -> dict[str, Any]:
    observation = _exact_keys(
        actual,
        _OBSERVATION_FIELDS,
        context=(
            "claim-scoped mutation result observation "
            f"{expected['implementation_id']}/{expected['selector']}"
        ),
    )
    for field in (
        "implementation_id",
        "profile_id",
        "selector",
        "source_sha256",
        "test_sha256",
        "command",
        "invocation_binding",
        "expected_observed",
    ):
        if observation[field] != expected[field]:
            raise _error(
                f"claim-scoped mutation result observation.{field}",
                "does not match frozen relation",
            )
    _finite_nonnegative(
        observation["duration_seconds"],
        context="claim-scoped mutation result observation.duration_seconds",
    )
    for field in ("stdout_sha256", "stderr_sha256"):
        if not _is_sha256(observation[field]):
            raise _error(
                f"claim-scoped mutation result observation.{field}",
                "must be a lowercase SHA-256 digest",
            )

    observed = observation["observed"]
    if observed not in {"pass", "fail", "error", "timeout"}:
        raise _error(
            "claim-scoped mutation result observation.observed",
            "is unsupported",
        )
    if observed in {"pass", "fail"}:
        complete = _expected_observation(
            plan_sha256=str(plan["plan_sha256"]),
            catalog_sha256=str(catalog["catalog_sha256"]),
            implementation_id=str(expected["implementation_id"]),
            profile_id=str(expected["profile_id"]),
            selector=str(expected["selector"]),
            source_sha256=str(expected["source_sha256"]),
            observed=str(observed),
        )
        for field in (
            "return_code",
            "timed_out",
            "receipt_sha256",
            "receipt_outcome",
            "receipt_producer",
            "receipt_counts",
            "observation_error",
        ):
            if not _strict_equal(complete[field], observation[field]):
                raise _error(
                    f"claim-scoped mutation result observation.{field}",
                    f"is inconsistent with observed={observed!r}",
                )
    elif observed == "timeout":
        if observation["timed_out"] is not True:
            raise _error(
                "claim-scoped mutation result observation.timed_out",
                "must be true when observed='timeout'",
            )
    else:
        if observation["timed_out"] is True:
            raise _error(
                "claim-scoped mutation result observation.observed",
                "error cannot also be timeout",
            )
        if observation["observation_error"] is None:
            raise _error(
                "claim-scoped mutation result observation.observation_error",
                "must explain observed='error'",
            )

    canonical = deepcopy(observation)
    canonical["concordant"] = observed == expected["expected_observed"]
    return canonical


def _canonical_profile(
    actual: object,
    expected: Mapping[str, object],
    *,
    plan: Mapping[str, object],
    catalog: Mapping[str, object],
    baseline: bool,
) -> dict[str, Any]:
    profile = _exact_keys(
        actual,
        _PROFILE_FIELDS,
        context=f"claim-scoped mutation result profile {expected['profile_id']}",
    )
    for field in ("profile_id", "profile_role", "expected_outcome"):
        if profile[field] != expected[field]:
            raise _error(
                f"claim-scoped mutation result profile.{field}",
                "does not match frozen profile",
            )
    actual_selectors = profile["selectors"]
    expected_selectors = expected["selectors"]
    if (
        not isinstance(actual_selectors, list)
        or not isinstance(expected_selectors, list)
        or len(actual_selectors) != len(expected_selectors)
    ):
        raise _error(
            "claim-scoped mutation result profile.selectors",
            "cardinality does not match frozen profile",
        )
    selectors = [
        _canonical_observation(
            actual_selector,
            expected_selector,
            plan=plan,
            catalog=catalog,
        )
        for actual_selector, expected_selector in zip(
            actual_selectors,
            expected_selectors,
            strict=True,
        )
    ]
    outcome = _profile_outcome(
        [str(selector["observed"]) for selector in selectors],
        baseline=baseline,
    )
    canonical = {
        "profile_id": expected["profile_id"],
        "profile_role": expected["profile_role"],
        "selectors": selectors,
        "expected_outcome": expected["expected_outcome"],
        "outcome": outcome,
        "concordant": outcome == expected["expected_outcome"],
    }
    if profile["outcome"] != canonical["outcome"]:
        raise _error(
            "claim-scoped mutation result profile.outcome",
            "does not match observed selector evidence",
        )
    if profile["concordant"] is not canonical["concordant"]:
        raise _error(
            "claim-scoped mutation result profile.concordant",
            "does not match expected and observed outcomes",
        )
    return canonical


def _canonical_reference(
    actual: object,
    expected: Mapping[str, object],
    *,
    plan: Mapping[str, object],
    catalog: Mapping[str, object],
) -> dict[str, Any]:
    reference = _exact_keys(
        actual,
        _REFERENCE_FIELDS,
        context="claim-scoped mutation result reference",
    )
    for field in ("profile_id", "expected_outcome"):
        if reference[field] != expected[field]:
            raise _error(
                f"claim-scoped mutation result reference.{field}",
                "does not match frozen reference contract",
            )
    actual_selectors = reference["selectors"]
    expected_selectors = expected["selectors"]
    if (
        not isinstance(actual_selectors, list)
        or not isinstance(expected_selectors, list)
        or len(actual_selectors) != len(expected_selectors)
    ):
        raise _error(
            "claim-scoped mutation result reference.selectors",
            "cardinality does not match frozen reference checks",
        )
    selectors = [
        _canonical_observation(
            actual_selector,
            expected_selector,
            plan=plan,
            catalog=catalog,
        )
        for actual_selector, expected_selector in zip(
            actual_selectors,
            expected_selectors,
            strict=True,
        )
    ]
    outcome = _reference_outcome([str(selector["observed"]) for selector in selectors])
    canonical = {
        "profile_id": expected["profile_id"],
        "selectors": selectors,
        "expected_outcome": expected["expected_outcome"],
        "outcome": outcome,
        "concordant": outcome == expected["expected_outcome"],
    }
    if reference["outcome"] != canonical["outcome"]:
        raise _error(
            "claim-scoped mutation result reference.outcome",
            "does not match observed selector evidence",
        )
    if reference["concordant"] is not canonical["concordant"]:
        raise _error(
            "claim-scoped mutation result reference.concordant",
            "does not match expected and observed outcomes",
        )
    return canonical


def _canonical_executed_record(
    actual: object,
    expected: Mapping[str, object],
    *,
    plan: Mapping[str, object],
    catalog: Mapping[str, object],
) -> dict[str, Any]:
    record = _exact_keys(
        actual,
        _RECORD_FIELDS,
        context=f"claim-scoped mutation result record {expected['record_id']}",
    )
    for field in (
        "record_id",
        "implementation_id",
        "record_role",
        "operator_id",
        "mutant_id",
        "catalog_status",
        "source_sha256",
        "source_ast_sha256",
        "execution_status",
        "counts_toward_generic_generalization",
    ):
        if record[field] != expected[field]:
            raise _error(
                f"claim-scoped mutation result record.{field}",
                "does not match frozen plan/catalog relation",
            )
    actual_profiles = record["profiles"]
    expected_profiles = expected["profiles"]
    if (
        not isinstance(actual_profiles, list)
        or not isinstance(expected_profiles, list)
        or len(actual_profiles) != len(expected_profiles)
    ):
        raise _error(
            "claim-scoped mutation result record.profiles",
            "cardinality does not match frozen profiles",
        )
    profiles = [
        _canonical_profile(
            actual_profile,
            expected_profile,
            plan=plan,
            catalog=catalog,
            baseline=(expected["record_role"] == "candidate_baseline"),
        )
        for actual_profile, expected_profile in zip(
            actual_profiles,
            expected_profiles,
            strict=True,
        )
    ]
    expected_reference = expected["reference"]
    if not isinstance(expected_reference, dict):
        raise _error(
            "claim-scoped mutation result expected reference",
            "must be an object for executed records",
        )
    reference = _canonical_reference(
        record["reference"],
        expected_reference,
        plan=plan,
        catalog=catalog,
    )
    cost = _exact_keys(
        record["cost"],
        _RECORD_COST_FIELDS,
        context="claim-scoped mutation result record.cost",
    )
    if (
        cost["status"] != "measured"
        or cost["command_count"] != 5
        or cost["selector_count"] != 5
        or cost["missing_reason"] is not None
    ):
        raise _error(
            "claim-scoped mutation result record.cost",
            "does not match fixed execution contract",
        )
    _finite_nonnegative(
        cost["wall_clock_seconds"],
        context="claim-scoped mutation result record.cost.wall_clock_seconds",
    )
    _finite_nonnegative(
        cost["cpu_seconds"],
        context="claim-scoped mutation result record.cost.cpu_seconds",
    )
    concordant = all(profile["concordant"] for profile in profiles) and reference[
        "concordant"
    ]
    if record["concordant"] is not concordant:
        raise _error(
            "claim-scoped mutation result record.concordant",
            "does not match profile/reference concordance",
        )
    return {
        **{
            key: deepcopy(expected[key])
            for key in (
                "record_id",
                "implementation_id",
                "record_role",
                "operator_id",
                "mutant_id",
                "catalog_status",
                "source_sha256",
                "source_ast_sha256",
                "execution_status",
                "counts_toward_generic_generalization",
            )
        },
        "profiles": profiles,
        "reference": reference,
        "concordant": concordant,
        "cost": deepcopy(cost),
    }


def _canonical_generation_record(
    actual: object,
    expected: Mapping[str, object],
) -> dict[str, Any]:
    record = _exact_keys(
        actual,
        _RECORD_FIELDS,
        context=f"claim-scoped mutation result record {expected['record_id']}",
    )
    if not _strict_equal(dict(expected), record):
        raise _error(
            f"claim-scoped mutation result record {expected['record_id']}",
            "does not match frozen non-execution record",
        )
    return deepcopy(dict(expected))


def _canonical_result(
    document: object,
    plan: Mapping[str, object],
    catalog: Mapping[str, object],
) -> dict[str, Any]:
    result = _exact_keys(
        document,
        _ROOT_FIELDS,
        context="claim-scoped mutation result",
    )
    _validate_runtime_and_costs(result)
    candidate_template, record_templates = _expected_templates(plan, catalog)
    candidate = _canonical_executed_record(
        result["candidate_baseline"],
        candidate_template,
        plan=plan,
        catalog=catalog,
    )
    actual_records = result["records"]
    if not isinstance(actual_records, list) or len(actual_records) != len(record_templates):
        raise _error(
            "claim-scoped mutation result.records",
            "cardinality does not match frozen catalog plus historical control",
        )
    records = [
        (
            _canonical_executed_record(
                actual,
                expected,
                plan=plan,
                catalog=catalog,
            )
            if expected["execution_status"] == "executed"
            else _canonical_generation_record(actual, expected)
        )
        for actual, expected in zip(
            actual_records,
            record_templates,
            strict=True,
        )
    ]
    canonical = _base_result(plan, catalog, candidate, records)
    canonical["created_at"] = result["created_at"]
    canonical["runtime"] = deepcopy(result["runtime"])
    canonical["cost"] = deepcopy(result["cost"])
    canonical["semantic_sha256"] = result["semantic_sha256"]
    canonical["report_sha256"] = result["report_sha256"]
    return canonical


def verify_claim_scoped_mutation_result_document(
    document: object,
    plan: object,
    catalog: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify complete evidence while retaining valid unexpected observations."""

    try:
        normalized_plan, normalized_catalog = _preflight(plan, catalog)
        canonical = _canonical_result(
            document,
            normalized_plan,
            normalized_catalog,
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
            "source",
            "candidate_baseline",
            "records",
            "summary",
            "analysis",
            "policy",
            "cost",
        ):
            if not _strict_equal(canonical[field], document[field]):
                errors.append(
                    f"claim-scoped mutation result.{field}: does not match "
                    "source-derived or observation-derived semantics"
                )
        if document.get("semantic_sha256") != compute_mutation_result_semantic_sha256(
            document
        ):
            errors.append(
                "claim-scoped mutation result.semantic_sha256: digest mismatch"
            )
        if document.get("report_sha256") != compute_mutation_result_report_sha256(
            document
        ):
            errors.append(
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
    unique = tuple(dict.fromkeys(errors))
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
