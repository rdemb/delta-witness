"""DW-001 scenario-manifest and result-record contracts.

These contracts keep pre-execution ground truth separate from post-execution
evidence. Builders validate semantic invariants before sealing an artifact.
Verifiers recompute those invariants before accepting unkeyed integrity
digests. Cross-artifact verification additionally binds a result to the
supplied scenario manifest and DW-001 projection.

No function in this module executes repository code.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from copy import deepcopy
import math
from pathlib import PurePosixPath
import re
from typing import Any

from .dw001 import (
    METHOD_STATE_SETS,
    OBSERVER_IDENTIFIERS,
    STATE_ORDER,
    verify_projection_document,
)
from .errors import DeltaWitnessError
from .reporting import sha256_document


STUDY_ID = "DW-001"
SCENARIO_SCHEMA_VERSION = "deltawitness.dw001-scenario-manifest.v1"
RESULT_SCHEMA_VERSION = "deltawitness.dw001-result-record.v1"

_PARTITIONS = {"development", "holdout"}
_PARTITION_LOCK_STATUS = {"development_uncommitted", "holdout_committed"}
_SOURCE_TYPES = {"synthetic", "owned", "licensed", "authorized"}
_REVIEW_STATUS = {"pending", "approved", "rejected"}
_REVIEW_DECISIONS = {"approve", "reject"}
_STATE_OBSERVATIONS = {"pass", "fail", "error", "timeout"}
_METHOD_DECISIONS = {"accept", "reject", "indeterminate", "not_applicable"}
_DECISION_REASONS = {
    "accept": "predicate_satisfied",
    "reject": "predicate_contradicted",
    "indeterminate": "required_state_indeterminate",
    "not_applicable": "required_state_not_applicable",
}
_FAILURE_CAUSES = {
    "none",
    "assertion_failure",
    "test_failure_untyped",
    "collection_error",
    "import_error",
    "setup_error",
    "teardown_error",
    "no_tests",
    "no_effective_tests",
    "unexpected_success",
    "producer_error",
    "infrastructure_error",
    "unknown_error",
    "timeout",
}
_EXCLUSION_STATUS = {"included", "excluded"}
_DEVIATION_STATUS = {"applied", "rejected"}
_CONFIRMATORY_IMPACT = {"none", "exploratory_only", "excluded"}
_COST_STATUS = {"measured", "not_run", "unavailable"}
_OBSERVER_BY_ID = {observer_id: observer for observer, observer_id in OBSERVER_IDENTIFIERS.items()}

_SCENARIO_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/+:-]{0,127}\Z")
_ENV_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
_HEX_PATTERN = re.compile(r"[0-9a-f]+\Z")

_SCENARIO_FIELDS = {
    "schema_version",
    "study_id",
    "scenario_id",
    "partition",
    "partition_lock",
    "provenance",
    "git",
    "paths",
    "execution",
    "ground_truth",
    "review",
    "manifest_sha256",
}
_PARTITION_LOCK_FIELDS = {"status", "commitment_sha256", "commitment_scope"}
_PROVENANCE_FIELDS = {
    "source_type",
    "source_id",
    "license_expression",
    "authorization_basis",
    "authorization_reference",
    "public_release_allowed",
}
_GIT_FIELDS = {"repository_id", "base_sha", "head_sha"}
_PATHS_FIELDS = {"code", "tests", "documentation"}
_EXECUTION_FIELDS = {
    "command",
    "observer",
    "observer_id",
    "timeout_seconds",
    "pass_exit_codes",
    "fail_exit_codes",
    "pass_env",
    "environment_requirements",
}
_GROUND_TRUTH_FIELDS = {
    "states",
    "methods",
    "false_assurance_mechanism",
    "environment_assumptions",
}
_GROUND_TRUTH_STATE_FIELDS = {
    "state",
    "applicable",
    "applicability_reason",
    "expected_observed",
    "failure_cause",
}
_GROUND_TRUTH_METHOD_FIELDS = {
    "method_id",
    "observer_id",
    "combined_method_id",
    "expected_decision",
    "reason_code",
    "primary_denominator_eligible",
}
_REVIEW_FIELDS = {"status", "reviewers"}
_REVIEWER_FIELDS = {
    "reviewer_id",
    "role",
    "independent_of_scenario_author",
    "independent_of_implementation",
    "decision",
    "rationale",
}

_RESULT_FIELDS = {
    "schema_version",
    "study_id",
    "scenario_id",
    "partition",
    "scenario_manifest_sha256",
    "source",
    "exclusion",
    "deviations",
    "methods",
    "result_sha256",
}
_RESULT_SOURCE_FIELDS = {
    "protocol_commit",
    "implementation_commit",
    "generator_commit",
    "baseline_contract_sha256",
    "matrix_report_sha256",
    "witness_sha256",
    "projection_sha256",
    "observer_id",
}
_EXCLUSION_FIELDS = {"status", "code", "reason", "decision_reference"}
_DEVIATION_FIELDS = {
    "deviation_id",
    "status",
    "rule_id",
    "observed_problem",
    "action",
    "results_visible",
    "confirmatory_impact",
    "approval_reference",
}
_RESULT_METHOD_FIELDS = {
    "method_id",
    "observer_id",
    "combined_method_id",
    "expected_decision",
    "observed_decision",
    "observed_reason_code",
    "concordant",
    "primary_denominator_eligible",
    "denominator_reason_code",
    "cost",
}
_COST_FIELDS = {
    "status",
    "wall_clock_seconds",
    "cpu_seconds",
    "state_count",
    "command_count",
    "review_seconds",
    "missing_reason",
}


class DW001ContractError(DeltaWitnessError):
    """Raised when a DW-001 study contract cannot be constructed safely."""


def _error(context: str, message: str) -> DW001ContractError:
    return DW001ContractError(f"{context}: {message}")


def _object(value: object, *, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _error(context, "must be an object")
    return value


def _exact_keys(value: dict[str, Any], expected: set[str], *, context: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise _error(context, f"field mismatch; missing={missing}, extra={extra}")


def _string(value: object, *, context: str, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value):
        qualifier = "a string" if allow_empty else "a non-empty string"
        raise _error(context, f"must be {qualifier}")
    return value


def _optional_string(value: object, *, context: str) -> str | None:
    if value is None:
        return None
    return _string(value, context=context)


def _boolean(value: object, *, context: str) -> bool:
    if not isinstance(value, bool):
        raise _error(context, "must be a boolean")
    return value


def _integer(
    value: object,
    *,
    context: str,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise _error(context, "must be an integer")
    if minimum is not None and value < minimum:
        raise _error(context, f"must be at least {minimum}")
    if maximum is not None and value > maximum:
        raise _error(context, f"must be at most {maximum}")
    return value


def _number_or_none(value: object, *, context: str) -> float | int | None:
    if value is None:
        return None
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise _error(context, "must be a finite nonnegative number or null")
    if not math.isfinite(float(value)) or value < 0:
        raise _error(context, "must be a finite nonnegative number or null")
    return value


def _integer_or_none(value: object, *, context: str) -> int | None:
    if value is None:
        return None
    return _integer(value, context=context, minimum=0)


def _hex(value: object, *, context: str, lengths: Sequence[int]) -> str:
    text = _string(value, context=context)
    if len(text) not in lengths or _HEX_PATTERN.fullmatch(text) is None:
        raise _error(context, f"must be lowercase hexadecimal with length in {tuple(lengths)}")
    return text


def _optional_hex(value: object, *, context: str, lengths: Sequence[int]) -> str | None:
    if value is None:
        return None
    return _hex(value, context=context, lengths=lengths)


def _string_list(
    value: object,
    *,
    context: str,
    allow_empty: bool = True,
    unique: bool = True,
) -> list[str]:
    if not isinstance(value, list) or (not allow_empty and not value):
        qualifier = "a list" if allow_empty else "a non-empty list"
        raise _error(context, f"must be {qualifier} of strings")
    result = [_string(item, context=f"{context}[{index}]") for index, item in enumerate(value)]
    if unique and len(set(result)) != len(result):
        raise _error(context, "must not contain duplicates")
    return result


def _integer_list(
    value: object,
    *,
    context: str,
    allow_empty: bool = False,
) -> list[int]:
    if not isinstance(value, list) or (not allow_empty and not value):
        qualifier = "a list" if allow_empty else "a non-empty list"
        raise _error(context, f"must be {qualifier} of integers")
    result = [
        _integer(item, context=f"{context}[{index}]", minimum=-255, maximum=255)
        for index, item in enumerate(value)
    ]
    if len(set(result)) != len(result):
        raise _error(context, "must not contain duplicates")
    return result


def _token(value: object, *, context: str) -> str:
    text = _string(value, context=context)
    if _TOKEN_PATTERN.fullmatch(text) is None:
        raise _error(context, "contains unsupported characters")
    return text


def _scenario_id(value: object, *, context: str = "scenario_id") -> str:
    text = _string(value, context=context)
    if _SCENARIO_ID_PATTERN.fullmatch(text) is None:
        raise _error(context, "must match [A-Za-z0-9][A-Za-z0-9._-]{0,127}")
    return text


def _safe_path(value: object, *, context: str) -> str:
    path = _string(value, context=context)
    if path.startswith("/") or "\\" in path or "\x00" in path:
        raise _error(context, "must be a safe repository-relative POSIX path")
    parts = PurePosixPath(path).parts
    if not parts or any(part in {".", ".."} or part.casefold() == ".git" for part in parts):
        raise _error(context, "must be a safe repository-relative POSIX path")
    return path


def _prefix_free(paths: Sequence[str], *, context: str) -> None:
    ordered = sorted(paths)
    for index, path in enumerate(ordered):
        prefix = f"{path}/"
        for other in ordered[index + 1 :]:
            if other.startswith(prefix):
                raise _error(context, f"contains ancestor/descendant paths: {path!r}, {other!r}")


def _collect_errors(validator: Callable[[], None]) -> list[str]:
    try:
        validator()
    except DW001ContractError as exc:
        return [str(exc)]
    return []


def _decision_from_ground_truth(
    states_by_name: Mapping[str, dict[str, Any]],
    required_states: Sequence[str],
) -> tuple[str, str]:
    selected = [states_by_name[state] for state in required_states]
    if any(not state["applicable"] for state in selected):
        return "not_applicable", "required_state_not_applicable"
    if any(state["expected_observed"] in {"error", "timeout"} for state in selected):
        return "indeterminate", "required_state_indeterminate"
    if any(
        state["expected_observed"]
        != {
            "base_base": "pass",
            "base_candidate": "fail",
            "candidate_base": "pass",
            "candidate_candidate": "pass",
        }[state["state"]]
        for state in selected
    ):
        return "reject", "predicate_contradicted"
    return "accept", "predicate_satisfied"


def _validate_partition_lock(partition: str, value: object) -> None:
    lock = _object(value, context="scenario manifest.partition_lock")
    _exact_keys(lock, _PARTITION_LOCK_FIELDS, context="scenario manifest.partition_lock")
    status = _string(lock["status"], context="scenario manifest.partition_lock.status")
    if status not in _PARTITION_LOCK_STATUS:
        raise _error("scenario manifest.partition_lock.status", "is unsupported")
    commitment = lock["commitment_sha256"]
    scope = lock["commitment_scope"]
    if partition == "development":
        if status != "development_uncommitted" or commitment is not None or scope is not None:
            raise _error(
                "scenario manifest.partition_lock",
                "partition_lock is inconsistent with development partition",
            )
    else:
        if status != "holdout_committed":
            raise _error(
                "scenario manifest.partition_lock",
                "partition_lock is inconsistent with holdout partition",
            )
        _hex(
            commitment,
            context="scenario manifest.partition_lock.commitment_sha256",
            lengths=(64,),
        )
        if scope != "dw001-holdout-index-v1":
            raise _error(
                "scenario manifest.partition_lock.commitment_scope",
                "must be 'dw001-holdout-index-v1' for a holdout partition",
            )


def _validate_provenance(value: object) -> None:
    provenance = _object(value, context="scenario manifest.provenance")
    _exact_keys(provenance, _PROVENANCE_FIELDS, context="scenario manifest.provenance")
    source_type = _string(provenance["source_type"], context="scenario manifest.provenance.source_type")
    if source_type not in _SOURCE_TYPES:
        raise _error("scenario manifest.provenance.source_type", "is unsupported")
    _string(provenance["source_id"], context="scenario manifest.provenance.source_id")
    license_expression = _optional_string(
        provenance["license_expression"],
        context="scenario manifest.provenance.license_expression",
    )
    basis = _string(
        provenance["authorization_basis"],
        context="scenario manifest.provenance.authorization_basis",
    )
    authorization_reference = _optional_string(
        provenance["authorization_reference"],
        context="scenario manifest.provenance.authorization_reference",
    )
    _boolean(
        provenance["public_release_allowed"],
        context="scenario manifest.provenance.public_release_allowed",
    )

    if source_type == "synthetic":
        if basis != "owned_synthetic_fixture" or license_expression is not None or authorization_reference is not None:
            raise _error(
                "scenario manifest.provenance",
                "synthetic provenance requires owned_synthetic_fixture and no external license or authorization reference",
            )
    elif source_type == "owned":
        if basis != "owned_repository" or authorization_reference is not None:
            raise _error(
                "scenario manifest.provenance",
                "owned provenance requires owned_repository and no external authorization reference",
            )
    elif source_type == "licensed":
        if basis != "license" or license_expression is None:
            raise _error(
                "scenario manifest.provenance",
                "licensed provenance requires authorization_basis='license' and license_expression",
            )
    else:
        if basis not in {"written_authorization", "public_security_policy"}:
            raise _error(
                "scenario manifest.provenance.authorization_basis",
                "authorized provenance requires written_authorization or public_security_policy",
            )
        if authorization_reference is None:
            raise _error(
                "scenario manifest.provenance.authorization_reference",
                "authorized provenance requires a public-safe authorization reference",
            )


def _validate_git(value: object) -> None:
    git = _object(value, context="scenario manifest.git")
    _exact_keys(git, _GIT_FIELDS, context="scenario manifest.git")
    _string(git["repository_id"], context="scenario manifest.git.repository_id")
    base = _hex(git["base_sha"], context="scenario manifest.git.base_sha", lengths=(40, 64))
    head = _hex(git["head_sha"], context="scenario manifest.git.head_sha", lengths=(40, 64))
    if base == head:
        raise _error("scenario manifest.git", "base_sha and head_sha must differ")


def _validate_paths(value: object) -> None:
    paths = _object(value, context="scenario manifest.paths")
    _exact_keys(paths, _PATHS_FIELDS, context="scenario manifest.paths")
    normalized: list[str] = []
    for category in ("code", "tests", "documentation"):
        raw = paths[category]
        if not isinstance(raw, list) or (category in {"code", "tests"} and not raw):
            qualifier = "a non-empty list" if category in {"code", "tests"} else "a list"
            raise _error(f"scenario manifest.paths.{category}", f"must be {qualifier}")
        category_paths = [
            _safe_path(item, context=f"scenario manifest.paths.{category}[{index}]")
            for index, item in enumerate(raw)
        ]
        if len(set(category_paths)) != len(category_paths):
            raise _error(f"scenario manifest.paths.{category}", "must not contain duplicates")
        normalized.extend(category_paths)
    if len(set(normalized)) != len(normalized):
        raise _error("scenario manifest.paths", "path categories must be disjoint")
    _prefix_free(normalized, context="scenario manifest.paths")


def _validate_execution(value: object) -> tuple[str, str]:
    execution = _object(value, context="scenario manifest.execution")
    _exact_keys(execution, _EXECUTION_FIELDS, context="scenario manifest.execution")
    _string_list(
        execution["command"],
        context="scenario manifest.execution.command",
        allow_empty=False,
        unique=False,
    )
    observer = _string(execution["observer"], context="scenario manifest.execution.observer")
    if observer not in OBSERVER_IDENTIFIERS:
        raise _error("scenario manifest.execution.observer", "is unsupported")
    observer_id = _string(
        execution["observer_id"],
        context="scenario manifest.execution.observer_id",
    )
    if observer_id != OBSERVER_IDENTIFIERS[observer]:
        raise _error(
            "scenario manifest.execution.observer_id",
            "is inconsistent with observer",
        )
    _integer(
        execution["timeout_seconds"],
        context="scenario manifest.execution.timeout_seconds",
        minimum=1,
        maximum=86_400,
    )
    pass_codes = _integer_list(
        execution["pass_exit_codes"],
        context="scenario manifest.execution.pass_exit_codes",
    )
    fail_codes = _integer_list(
        execution["fail_exit_codes"],
        context="scenario manifest.execution.fail_exit_codes",
    )
    if set(pass_codes) & set(fail_codes):
        raise _error(
            "scenario manifest.execution",
            "pass_exit_codes and fail_exit_codes must be disjoint",
        )
    pass_env = _string_list(
        execution["pass_env"],
        context="scenario manifest.execution.pass_env",
    )
    for index, name in enumerate(pass_env):
        if _ENV_PATTERN.fullmatch(name) is None:
            raise _error(
                f"scenario manifest.execution.pass_env[{index}]",
                "is not a valid environment variable name",
            )
    _string_list(
        execution["environment_requirements"],
        context="scenario manifest.execution.environment_requirements",
    )
    return observer, observer_id


def _validate_state_failure_cause(
    *,
    state: str,
    observer: str,
    observed: str,
    cause: str,
) -> None:
    context = f"scenario manifest.ground_truth.states[{state}].failure_cause"
    if cause not in _FAILURE_CAUSES:
        raise _error(context, "is unsupported")
    if observed == "pass" and cause != "none":
        raise _error(context, "pass observations require failure_cause='none'")
    if observed == "timeout" and cause != "timeout":
        raise _error(context, "timeout observations require failure_cause='timeout'")
    if observed == "fail" and cause not in {"assertion_failure", "test_failure_untyped"}:
        raise _error(
            context,
            "fail observations require assertion_failure or test_failure_untyped",
        )
    if observed == "error" and cause in {"none", "assertion_failure", "test_failure_untyped", "timeout"}:
        raise _error(context, "error observations require a non-test-failure error cause")
    if observer == "outcome-receipt-v1" and observed == "fail" and cause != "assertion_failure":
        raise _error(
            context,
            "typed-receipt failure ground truth must use assertion_failure",
        )


def _validate_ground_truth_states(
    value: object,
    *,
    observer: str,
) -> dict[str, dict[str, Any]]:
    if not isinstance(value, list) or len(value) != len(STATE_ORDER):
        raise _error(
            "scenario manifest.ground_truth.states",
            "must contain exactly four ordered states",
        )
    states: dict[str, dict[str, Any]] = {}
    for index, expected_name in enumerate(STATE_ORDER):
        context = f"scenario manifest.ground_truth.states[{expected_name}]"
        state = _object(value[index], context=context)
        _exact_keys(state, _GROUND_TRUTH_STATE_FIELDS, context=context)
        if state["state"] != expected_name:
            raise _error(context, f"state must be {expected_name!r}")
        applicable = _boolean(state["applicable"], context=f"{context}.applicable")
        reason = _optional_string(
            state["applicability_reason"],
            context=f"{context}.applicability_reason",
        )
        observed = state["expected_observed"]
        cause = state["failure_cause"]
        if applicable:
            if reason is not None:
                raise _error(context, "applicable state must not carry applicability_reason")
            if observed not in _STATE_OBSERVATIONS:
                raise _error(
                    f"{context}.expected_observed",
                    "must be pass, fail, error, or timeout for an applicable state",
                )
            cause_text = _string(cause, context=f"{context}.failure_cause")
            _validate_state_failure_cause(
                state=expected_name,
                observer=observer,
                observed=observed,
                cause=cause_text,
            )
        else:
            if reason is None:
                raise _error(context, "non-applicable state requires applicability_reason")
            if observed is not None or cause is not None:
                raise _error(
                    context,
                    "non-applicable state requires null expected_observed and failure_cause",
                )
        states[expected_name] = state
    return states


def _validate_review(value: object) -> str:
    review = _object(value, context="scenario manifest.review")
    _exact_keys(review, _REVIEW_FIELDS, context="scenario manifest.review")
    status = _string(review["status"], context="scenario manifest.review.status")
    if status not in _REVIEW_STATUS:
        raise _error("scenario manifest.review.status", "is unsupported")
    reviewers = review["reviewers"]
    if not isinstance(reviewers, list) or not reviewers:
        raise _error("scenario manifest.review.reviewers", "must be a non-empty list")
    seen: set[str] = set()
    has_independent_approval = False
    has_rejection = False
    for index, item in enumerate(reviewers):
        context = f"scenario manifest.review.reviewers[{index}]"
        reviewer = _object(item, context=context)
        _exact_keys(reviewer, _REVIEWER_FIELDS, context=context)
        reviewer_id = _token(reviewer["reviewer_id"], context=f"{context}.reviewer_id")
        if reviewer_id in seen:
            raise _error(f"{context}.reviewer_id", "must be unique")
        seen.add(reviewer_id)
        _string(reviewer["role"], context=f"{context}.role")
        author_independent = _boolean(
            reviewer["independent_of_scenario_author"],
            context=f"{context}.independent_of_scenario_author",
        )
        implementation_independent = _boolean(
            reviewer["independent_of_implementation"],
            context=f"{context}.independent_of_implementation",
        )
        decision = _string(reviewer["decision"], context=f"{context}.decision")
        if decision not in _REVIEW_DECISIONS:
            raise _error(f"{context}.decision", "is unsupported")
        _string(reviewer["rationale"], context=f"{context}.rationale")
        if decision == "reject":
            has_rejection = True
        if decision == "approve" and author_independent and implementation_independent:
            has_independent_approval = True

    expected_status = (
        "rejected"
        if has_rejection
        else ("approved" if has_independent_approval else "pending")
    )
    if status != expected_status:
        raise _error(
            "scenario manifest.review.status",
            f"is inconsistent with reviewer decisions; expected {expected_status!r}",
        )
    return status


def _validate_ground_truth_methods(
    value: object,
    *,
    observer_id: str,
    states_by_name: Mapping[str, dict[str, Any]],
    partition: str,
    review_status: str,
) -> None:
    if not isinstance(value, list) or len(value) != len(METHOD_STATE_SETS):
        raise _error(
            "scenario manifest.ground_truth.methods",
            "must contain exactly four ordered methods",
        )
    for index, (expected_method_id, required_states) in enumerate(METHOD_STATE_SETS):
        context = f"scenario manifest.ground_truth.methods[{expected_method_id}]"
        method = _object(value[index], context=context)
        _exact_keys(method, _GROUND_TRUTH_METHOD_FIELDS, context=context)
        if method["method_id"] != expected_method_id:
            raise _error(context, f"method_id must be {expected_method_id!r}")
        if method["observer_id"] != observer_id:
            raise _error(context, "observer_id is inconsistent with execution")
        expected_combined = f"{expected_method_id}__{observer_id}"
        if method["combined_method_id"] != expected_combined:
            raise _error(context, "combined_method_id is inconsistent")
        expected_decision, expected_reason = _decision_from_ground_truth(
            states_by_name,
            required_states,
        )
        if method["expected_decision"] != expected_decision or method["reason_code"] != expected_reason:
            raise _error(
                context,
                "method ground truth is inconsistent with state ground truth",
            )
        eligible = (
            partition == "holdout"
            and review_status == "approved"
            and expected_decision != "not_applicable"
        )
        if _boolean(
            method["primary_denominator_eligible"],
            context=f"{context}.primary_denominator_eligible",
        ) != eligible:
            raise _error(
                context,
                "primary_denominator_eligible is inconsistent with partition, review, and applicability",
            )


def _validate_scenario_semantics(document: dict[str, Any]) -> None:
    _exact_keys(document, _SCENARIO_FIELDS, context="scenario manifest")
    if document["schema_version"] != SCENARIO_SCHEMA_VERSION:
        raise _error(
            "scenario manifest.schema_version",
            f"must be {SCENARIO_SCHEMA_VERSION!r}",
        )
    if document["study_id"] != STUDY_ID:
        raise _error("scenario manifest.study_id", f"must be {STUDY_ID!r}")
    _scenario_id(document["scenario_id"], context="scenario manifest.scenario_id")
    partition = _string(document["partition"], context="scenario manifest.partition")
    if partition not in _PARTITIONS:
        raise _error("scenario manifest.partition", "is unsupported")
    _validate_partition_lock(partition, document["partition_lock"])
    _validate_provenance(document["provenance"])
    _validate_git(document["git"])
    _validate_paths(document["paths"])
    observer, observer_id = _validate_execution(document["execution"])

    ground_truth = _object(document["ground_truth"], context="scenario manifest.ground_truth")
    _exact_keys(ground_truth, _GROUND_TRUTH_FIELDS, context="scenario manifest.ground_truth")
    states = _validate_ground_truth_states(ground_truth["states"], observer=observer)
    _string(
        ground_truth["false_assurance_mechanism"],
        context="scenario manifest.ground_truth.false_assurance_mechanism",
    )
    _string_list(
        ground_truth["environment_assumptions"],
        context="scenario manifest.ground_truth.environment_assumptions",
    )
    review_status = _validate_review(document["review"])
    _validate_ground_truth_methods(
        ground_truth["methods"],
        observer_id=observer_id,
        states_by_name=states,
        partition=partition,
        review_status=review_status,
    )


def compute_scenario_manifest_sha256(document: dict[str, Any]) -> str:
    normalized = dict(document)
    normalized["manifest_sha256"] = None
    return sha256_document(normalized)


def compute_result_sha256(document: dict[str, Any]) -> str:
    normalized = dict(document)
    normalized["result_sha256"] = None
    return sha256_document(normalized)


def seal_scenario_manifest(document: object) -> dict[str, Any]:
    """Validate and seal one deterministic scenario manifest."""

    if not isinstance(document, dict):
        raise DW001ContractError("Scenario manifest root must be an object")
    sealed = deepcopy(document)
    sealed["manifest_sha256"] = None
    _validate_scenario_semantics(sealed)
    sealed["manifest_sha256"] = compute_scenario_manifest_sha256(sealed)
    return sealed


def verify_scenario_manifest_document(document: object) -> tuple[bool, tuple[str, ...]]:
    """Recompute manifest semantics before accepting its unkeyed digest."""

    if not isinstance(document, dict):
        raise DW001ContractError("Scenario manifest root must be an object")
    errors = _collect_errors(lambda: _validate_scenario_semantics(document))
    expected = document.get("manifest_sha256")
    try:
        normalized_expected = _hex(
            expected,
            context="scenario manifest.manifest_sha256",
            lengths=(64,),
        )
    except DW001ContractError as exc:
        errors.append(str(exc))
    else:
        observed = compute_scenario_manifest_sha256(document)
        if observed != normalized_expected:
            errors.append(
                f"scenario manifest digest mismatch: expected {normalized_expected}, computed {observed}"
            )
    return not errors, tuple(errors)


def _validate_result_source(value: object) -> str:
    source = _object(value, context="result record.source")
    _exact_keys(source, _RESULT_SOURCE_FIELDS, context="result record.source")
    _hex(source["protocol_commit"], context="result record.source.protocol_commit", lengths=(40, 64))
    _hex(
        source["implementation_commit"],
        context="result record.source.implementation_commit",
        lengths=(40, 64),
    )
    _optional_hex(
        source["generator_commit"],
        context="result record.source.generator_commit",
        lengths=(40, 64),
    )
    for field in (
        "baseline_contract_sha256",
        "matrix_report_sha256",
        "witness_sha256",
        "projection_sha256",
    ):
        _hex(source[field], context=f"result record.source.{field}", lengths=(64,))
    observer_id = _string(source["observer_id"], context="result record.source.observer_id")
    if observer_id not in _OBSERVER_BY_ID:
        raise _error("result record.source.observer_id", "is unsupported")
    return observer_id


def _validate_exclusion(value: object) -> str:
    exclusion = _object(value, context="result record.exclusion")
    _exact_keys(exclusion, _EXCLUSION_FIELDS, context="result record.exclusion")
    status = _string(exclusion["status"], context="result record.exclusion.status")
    if status not in _EXCLUSION_STATUS:
        raise _error("result record.exclusion.status", "is unsupported")
    code = _optional_string(exclusion["code"], context="result record.exclusion.code")
    reason = _optional_string(exclusion["reason"], context="result record.exclusion.reason")
    reference = _optional_string(
        exclusion["decision_reference"],
        context="result record.exclusion.decision_reference",
    )
    if status == "included":
        if code is not None or reason is not None or reference is not None:
            raise _error(
                "result record.exclusion",
                "included result must not carry exclusion metadata",
            )
    elif code is None or reason is None or reference is None:
        raise _error(
            "result record.exclusion",
            "excluded result requires code, reason, and decision_reference",
        )
    return status


def _validate_deviations(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise _error("result record.deviations", "must be a list")
    deviations: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        context = f"result record.deviations[{index}]"
        deviation = _object(item, context=context)
        _exact_keys(deviation, _DEVIATION_FIELDS, context=context)
        deviation_id = _token(deviation["deviation_id"], context=f"{context}.deviation_id")
        if deviation_id in seen:
            raise _error(f"{context}.deviation_id", "must be unique")
        seen.add(deviation_id)
        status = _string(deviation["status"], context=f"{context}.status")
        if status not in _DEVIATION_STATUS:
            raise _error(f"{context}.status", "is unsupported")
        _string(deviation["rule_id"], context=f"{context}.rule_id")
        _string(deviation["observed_problem"], context=f"{context}.observed_problem")
        _string(deviation["action"], context=f"{context}.action")
        _boolean(deviation["results_visible"], context=f"{context}.results_visible")
        impact = _string(
            deviation["confirmatory_impact"],
            context=f"{context}.confirmatory_impact",
        )
        if impact not in _CONFIRMATORY_IMPACT:
            raise _error(f"{context}.confirmatory_impact", "is unsupported")
        approval = _optional_string(
            deviation["approval_reference"],
            context=f"{context}.approval_reference",
        )
        if status == "applied" and approval is None:
            raise _error(context, "applied deviation requires approval_reference")
        if status == "rejected" and (impact != "none" or approval is not None):
            raise _error(
                context,
                "rejected deviation must use confirmatory_impact='none' and no approval_reference",
            )
        deviations.append(deviation)
    return deviations


def _validate_cost(value: object, *, context: str) -> None:
    cost = _object(value, context=context)
    _exact_keys(cost, _COST_FIELDS, context=context)
    status = _string(cost["status"], context=f"{context}.status")
    if status not in _COST_STATUS:
        raise _error(f"{context}.status", "is unsupported")
    wall = _number_or_none(cost["wall_clock_seconds"], context=f"{context}.wall_clock_seconds")
    cpu = _number_or_none(cost["cpu_seconds"], context=f"{context}.cpu_seconds")
    state_count = _integer_or_none(cost["state_count"], context=f"{context}.state_count")
    command_count = _integer_or_none(cost["command_count"], context=f"{context}.command_count")
    review = _number_or_none(cost["review_seconds"], context=f"{context}.review_seconds")
    missing = _optional_string(cost["missing_reason"], context=f"{context}.missing_reason")
    values = (wall, cpu, state_count, command_count, review)
    if status == "measured":
        if any(item is None for item in values) or missing is not None:
            raise _error(
                context,
                "measured cost requires every numeric field and no missing_reason",
            )
    elif any(item is not None for item in values) or missing is None:
        raise _error(
            context,
            f"{status} cost requires null numeric fields and a missing_reason",
        )


def _deviation_denominator_reason(deviations: Sequence[dict[str, Any]]) -> str | None:
    applied = [item for item in deviations if item["status"] == "applied"]
    if any(item["confirmatory_impact"] == "excluded" for item in applied):
        return "deviation_excluded"
    if any(item["confirmatory_impact"] == "exploratory_only" for item in applied):
        return "deviation_exploratory_only"
    return None


def _expected_denominator(
    *,
    partition: str,
    exclusion_status: str,
    deviations: Sequence[dict[str, Any]],
    expected_decision: str,
    observed_decision: str,
) -> tuple[bool, str]:
    if partition == "development":
        return False, "development_partition"
    if expected_decision == "not_applicable":
        return False, "expected_not_applicable"
    if exclusion_status == "excluded":
        return False, "excluded"
    deviation_reason = _deviation_denominator_reason(deviations)
    if deviation_reason is not None:
        return False, deviation_reason
    if observed_decision == "not_applicable":
        return False, "observed_not_applicable"
    return True, "eligible"


def _validate_result_methods(
    value: object,
    *,
    observer_id: str,
    partition: str,
    exclusion_status: str,
    deviations: Sequence[dict[str, Any]],
) -> None:
    if not isinstance(value, list) or len(value) != len(METHOD_STATE_SETS):
        raise _error("result record.methods", "must contain exactly four ordered methods")
    for index, (expected_method_id, _) in enumerate(METHOD_STATE_SETS):
        context = f"result record.methods[{expected_method_id}]"
        method = _object(value[index], context=context)
        _exact_keys(method, _RESULT_METHOD_FIELDS, context=context)
        if method["method_id"] != expected_method_id:
            raise _error(context, f"method_id must be {expected_method_id!r}")
        if method["observer_id"] != observer_id:
            raise _error(context, "observer_id is inconsistent with result source")
        if method["combined_method_id"] != f"{expected_method_id}__{observer_id}":
            raise _error(context, "combined_method_id is inconsistent")
        expected_decision = _string(
            method["expected_decision"],
            context=f"{context}.expected_decision",
        )
        observed_decision = _string(
            method["observed_decision"],
            context=f"{context}.observed_decision",
        )
        if expected_decision not in _METHOD_DECISIONS:
            raise _error(f"{context}.expected_decision", "is unsupported")
        if observed_decision not in _METHOD_DECISIONS:
            raise _error(f"{context}.observed_decision", "is unsupported")
        reason = _string(
            method["observed_reason_code"],
            context=f"{context}.observed_reason_code",
        )
        if reason != _DECISION_REASONS[observed_decision]:
            raise _error(
                f"{context}.observed_reason_code",
                "is inconsistent with observed_decision",
            )
        concordant = _boolean(method["concordant"], context=f"{context}.concordant")
        if concordant != (expected_decision == observed_decision):
            raise _error(context, "concordant is inconsistent with expected and observed decisions")

        eligible, denominator_reason = _expected_denominator(
            partition=partition,
            exclusion_status=exclusion_status,
            deviations=deviations,
            expected_decision=expected_decision,
            observed_decision=observed_decision,
        )
        recorded_eligible = _boolean(
            method["primary_denominator_eligible"],
            context=f"{context}.primary_denominator_eligible",
        )
        recorded_reason = _string(
            method["denominator_reason_code"],
            context=f"{context}.denominator_reason_code",
        )
        if recorded_eligible != eligible or recorded_reason != denominator_reason:
            if exclusion_status == "excluded" and recorded_eligible:
                raise _error(
                    context,
                    "excluded result cannot be primary-denominator eligible",
                )
            if denominator_reason == "deviation_exploratory_only" and recorded_eligible:
                raise _error(
                    context,
                    "exploratory-only result cannot be primary-denominator eligible",
                )
            raise _error(
                context,
                "denominator eligibility is inconsistent with partition, exclusion, deviations, and applicability",
            )
        _validate_cost(method["cost"], context=f"{context}.cost")


def _validate_result_semantics(document: dict[str, Any]) -> None:
    _exact_keys(document, _RESULT_FIELDS, context="result record")
    if document["schema_version"] != RESULT_SCHEMA_VERSION:
        raise _error("result record.schema_version", f"must be {RESULT_SCHEMA_VERSION!r}")
    if document["study_id"] != STUDY_ID:
        raise _error("result record.study_id", f"must be {STUDY_ID!r}")
    _scenario_id(document["scenario_id"], context="result record.scenario_id")
    partition = _string(document["partition"], context="result record.partition")
    if partition not in _PARTITIONS:
        raise _error("result record.partition", "is unsupported")
    _hex(
        document["scenario_manifest_sha256"],
        context="result record.scenario_manifest_sha256",
        lengths=(64,),
    )
    observer_id = _validate_result_source(document["source"])
    exclusion_status = _validate_exclusion(document["exclusion"])
    deviations = _validate_deviations(document["deviations"])
    _validate_result_methods(
        document["methods"],
        observer_id=observer_id,
        partition=partition,
        exclusion_status=exclusion_status,
        deviations=deviations,
    )


def seal_result_record(document: object) -> dict[str, Any]:
    """Validate and seal one deterministic result record."""

    if not isinstance(document, dict):
        raise DW001ContractError("Result record root must be an object")
    sealed = deepcopy(document)
    sealed["result_sha256"] = None
    _validate_result_semantics(sealed)
    sealed["result_sha256"] = compute_result_sha256(sealed)
    return sealed


def _supplemental_result_errors(document: dict[str, Any]) -> list[str]:
    """Collect independent denominator/deviation errors after a primary failure.

    The strict validator stops at the first invariant violation. These checks
    retain multiple load-bearing diagnostics for a single malformed result.
    """

    errors: list[str] = []
    deviations = document.get("deviations")
    methods = document.get("methods")
    exclusion = document.get("exclusion")
    if isinstance(deviations, list):
        for index, item in enumerate(deviations):
            if isinstance(item, dict) and item.get("status") == "applied" and item.get("approval_reference") is None:
                errors.append(
                    f"result record.deviations[{index}]: applied deviation requires approval_reference"
                )
    if isinstance(methods, list):
        exclusion_status = exclusion.get("status") if isinstance(exclusion, dict) else None
        exploratory = any(
            isinstance(item, dict)
            and item.get("status") == "applied"
            and item.get("confirmatory_impact") == "exploratory_only"
            for item in deviations
        ) if isinstance(deviations, list) else False
        for method in methods:
            if not isinstance(method, dict) or not method.get("primary_denominator_eligible"):
                continue
            method_id = method.get("method_id", "<unknown>")
            if exclusion_status == "excluded":
                errors.append(
                    f"result record.methods[{method_id}]: excluded result cannot be primary-denominator eligible"
                )
            if exploratory:
                errors.append(
                    f"result record.methods[{method_id}]: exploratory-only result cannot be primary-denominator eligible"
                )
    return errors


def verify_result_record_document(document: object) -> tuple[bool, tuple[str, ...]]:
    """Recompute result semantics before accepting its unkeyed digest."""

    if not isinstance(document, dict):
        raise DW001ContractError("Result record root must be an object")
    errors = _collect_errors(lambda: _validate_result_semantics(document))
    for error in _supplemental_result_errors(document):
        if error not in errors:
            errors.append(error)
    expected = document.get("result_sha256")
    try:
        normalized_expected = _hex(
            expected,
            context="result record.result_sha256",
            lengths=(64,),
        )
    except DW001ContractError as exc:
        errors.append(str(exc))
    else:
        observed = compute_result_sha256(document)
        if observed != normalized_expected:
            errors.append(
                f"result record digest mismatch: expected {normalized_expected}, computed {observed}"
            )
    return not errors, tuple(errors)


def _method_map(value: object, *, context: str) -> dict[str, dict[str, Any]]:
    if not isinstance(value, list):
        raise _error(context, "must be a list")
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(value):
        method = _object(item, context=f"{context}[{index}]")
        method_id = _string(method.get("method_id"), context=f"{context}[{index}].method_id")
        if method_id in result:
            raise _error(f"{context}[{index}].method_id", "must be unique")
        result[method_id] = method
    return result


def _manifest_state_applicability(manifest: dict[str, Any]) -> tuple[list[str], dict[str, str]]:
    states = manifest["ground_truth"]["states"]
    applicable: list[str] = []
    non_applicable: dict[str, str] = {}
    for state in states:
        if state["applicable"]:
            applicable.append(state["state"])
        else:
            non_applicable[state["state"]] = state["applicability_reason"]
    return applicable, non_applicable


def _cross_validate(
    result: dict[str, Any],
    manifest: dict[str, Any],
    projection: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if result["scenario_manifest_sha256"] != manifest["manifest_sha256"]:
        errors.append("scenario manifest digest mismatch between result and supplied manifest")
    if result["scenario_id"] != manifest["scenario_id"]:
        errors.append("scenario_id mismatch between result and supplied manifest")
    if result["partition"] != manifest["partition"]:
        errors.append("partition mismatch between result and supplied manifest")
    if projection.get("scenario_id") != manifest["scenario_id"]:
        errors.append("scenario_id mismatch between projection and supplied manifest")

    projection_source = projection.get("source")
    result_source = result["source"]
    manifest_git = manifest["git"]
    manifest_execution = manifest["execution"]
    if not isinstance(projection_source, dict):
        errors.append("projection.source must be an object")
        return errors

    source_pairs = (
        ("matrix_report_sha256", "report_sha256"),
        ("witness_sha256", "witness_sha256"),
        ("projection_sha256", None),
        ("observer_id", "observer_id"),
    )
    for result_field, projection_field in source_pairs:
        projection_value = (
            projection.get("projection_sha256")
            if projection_field is None
            else projection_source.get(projection_field)
        )
        if result_source[result_field] != projection_value:
            errors.append(
                f"result source {result_field} does not match supplied projection"
            )
    if manifest_git["base_sha"] != projection_source.get("base_sha"):
        errors.append("manifest base_sha does not match supplied projection")
    if manifest_git["head_sha"] != projection_source.get("head_sha"):
        errors.append("manifest head_sha does not match supplied projection")
    if manifest_execution["observer"] != projection_source.get("observer"):
        errors.append("manifest observer does not match supplied projection")
    if manifest_execution["observer_id"] != projection_source.get("observer_id"):
        errors.append("manifest observer_id does not match supplied projection")

    applicable, non_applicable = _manifest_state_applicability(manifest)
    projection_applicability = projection.get("applicability")
    if isinstance(projection_applicability, dict):
        if projection_applicability.get("applicable_states") != applicable:
            errors.append("projection applicability does not match supplied manifest")
        expected_non_applicable = [
            {"state": state, "reason": non_applicable[state]}
            for state in STATE_ORDER
            if state in non_applicable
        ]
        if projection_applicability.get("non_applicable_states") != expected_non_applicable:
            errors.append("projection non-applicability reasons do not match supplied manifest")
    else:
        errors.append("projection.applicability must be an object")

    try:
        result_methods = _method_map(result["methods"], context="result record.methods")
        manifest_methods = _method_map(
            manifest["ground_truth"]["methods"],
            context="scenario manifest.ground_truth.methods",
        )
        projection_methods = _method_map(
            projection.get("methods"),
            context="projection.methods",
        )
    except DW001ContractError as exc:
        errors.append(str(exc))
        return errors

    review_status = manifest["review"]["status"]
    exclusion_status = result["exclusion"]["status"]
    deviations = result["deviations"]
    for method_id, _ in METHOD_STATE_SETS:
        if method_id not in result_methods or method_id not in manifest_methods or method_id not in projection_methods:
            errors.append(f"method {method_id} is missing from a supplied artifact")
            continue
        result_method = result_methods[method_id]
        manifest_method = manifest_methods[method_id]
        projection_method = projection_methods[method_id]
        if result_method["expected_decision"] != manifest_method["expected_decision"]:
            errors.append(f"{method_id}: expected decision does not match supplied manifest")
        if result_method["observed_decision"] != projection_method["decision"]:
            errors.append(f"{method_id}: observed decision does not match supplied projection")
        if result_method["observed_reason_code"] != projection_method["reason_code"]:
            errors.append(f"{method_id}: observed reason does not match supplied projection")
        expected_concordance = (
            manifest_method["expected_decision"] == projection_method["decision"]
        )
        if result_method["concordant"] != expected_concordance:
            errors.append(f"{method_id}: concordance is inconsistent across supplied artifacts")

        eligible, reason = _expected_denominator(
            partition=manifest["partition"],
            exclusion_status=exclusion_status,
            deviations=deviations,
            expected_decision=manifest_method["expected_decision"],
            observed_decision=projection_method["decision"],
        )
        if review_status != "approved":
            eligible, reason = False, "ground_truth_not_approved"
        if (
            result_method["primary_denominator_eligible"] != eligible
            or result_method["denominator_reason_code"] != reason
        ):
            errors.append(
                f"{method_id}: denominator eligibility is inconsistent across supplied artifacts"
            )
    return errors


def verify_result_against_sources(
    result: object,
    manifest: object,
    projection: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify result, manifest, projection, and their explicit cross-bindings."""

    errors: list[str] = []
    try:
        manifest_valid, manifest_errors = verify_scenario_manifest_document(manifest)
    except DW001ContractError as exc:
        errors.append(str(exc))
        manifest_valid = False
        manifest_errors = ()
    if not manifest_valid:
        errors.extend(manifest_errors)

    try:
        result_valid, result_errors = verify_result_record_document(result)
    except DW001ContractError as exc:
        errors.append(str(exc))
        result_valid = False
        result_errors = ()
    if not result_valid:
        errors.extend(result_errors)

    try:
        projection_valid, projection_errors = verify_projection_document(projection)
    except DeltaWitnessError as exc:
        errors.append(str(exc))
        projection_valid = False
        projection_errors = ()
    if not projection_valid:
        errors.extend(f"projection: {error}" for error in projection_errors)

    if isinstance(result, dict) and isinstance(manifest, dict) and isinstance(projection, dict):
        errors.extend(_cross_validate(result, manifest, projection))
    return not errors, tuple(dict.fromkeys(errors))


__all__ = [
    "DW001ContractError",
    "RESULT_SCHEMA_VERSION",
    "SCENARIO_SCHEMA_VERSION",
    "STUDY_ID",
    "compute_result_sha256",
    "compute_scenario_manifest_sha256",
    "seal_result_record",
    "seal_scenario_manifest",
    "verify_result_against_sources",
    "verify_result_record_document",
    "verify_scenario_manifest_document",
]
