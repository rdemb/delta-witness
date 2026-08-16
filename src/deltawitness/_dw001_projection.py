"""Deterministic baseline projection for the DW-001 preregistration study.

This module never executes repository code. It projects nested method decisions
from one already-produced, integrity-verified four-state matrix report.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import re
from typing import Any

from .errors import DeltaWitnessError, ReportError
from .reporting import sha256_document, verify_report_document


STUDY_ID = "DW-001"
PROJECTION_SCHEMA_VERSION = "deltawitness.dw001-projection.v1"
SUPPORTED_REPORT_SCHEMA_VERSION = "0.3"

STATE_ORDER = (
    "base_base",
    "base_candidate",
    "candidate_base",
    "candidate_candidate",
)
CANONICAL_EXPECTATIONS = {
    "base_base": "pass",
    "base_candidate": "fail",
    "candidate_base": "pass",
    "candidate_candidate": "pass",
}
METHOD_STATE_SETS = (
    ("M0_FINAL", ("candidate_candidate",)),
    ("M1_F2P", ("base_candidate", "candidate_candidate")),
    (
        "M2_F2P_P2P",
        ("base_candidate", "candidate_base", "candidate_candidate"),
    ),
    ("M3_FOUR_STATE", STATE_ORDER),
)
OBSERVER_IDENTIFIERS = {
    "exit-code-v1": "O0_EXIT_CODE",
    "outcome-receipt-v1": "O1_TYPED_RECEIPT",
}

_ROOT_FIELDS = {
    "schema_version",
    "tool_version",
    "created_at",
    "repository",
    "base_sha",
    "head_sha",
    "spec_path",
    "spec_external",
    "spec_sha256",
    "execution",
    "classification",
    "state_trees",
    "state_commits",
    "claims",
    "complete",
    "supported",
    "witness_sha256",
    "report_sha256",
}
_EXECUTION_FIELDS = {
    "environment_mode",
    "pass_env",
    "output_included",
    "sandboxed",
    "observer_protocols",
}
_CLASSIFICATION_FIELDS = {"code", "tests", "documentation"}
_CLAIM_FIELDS = {"claim_id", "description", "observer", "supported", "command", "states"}
_STATE_FIELDS = {
    "state",
    "commit_sha",
    "tree_sha",
    "observed",
    "expected",
    "matched",
    "return_code",
    "duration_seconds",
    "timed_out",
    "stdout_sha256",
    "stderr_sha256",
    "stdout",
    "stderr",
    "observer",
    "invocation_binding",
    "receipt_sha256",
    "receipt_outcome",
    "receipt_producer",
    "receipt_counts",
    "observation_error",
}
_PROJECTION_FIELDS = {
    "schema_version",
    "study_id",
    "scenario_id",
    "source",
    "applicability",
    "methods",
    "projection_sha256",
}
_SCENARIO_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
_HEX_PATTERN = re.compile(r"[0-9a-f]+\Z")


class DW001ProjectionError(DeltaWitnessError):
    """Raised when a source report cannot be projected under the DW-001 contract."""


def _error(context: str, message: str) -> DW001ProjectionError:
    return DW001ProjectionError(f"{context}: {message}")


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
        raise _error(context, "must be a non-empty string" if not allow_empty else "must be a string")
    return value


def _boolean(value: object, *, context: str) -> bool:
    if not isinstance(value, bool):
        raise _error(context, "must be a boolean")
    return value


def _hex(value: object, *, context: str, lengths: Sequence[int]) -> str:
    text = _string(value, context=context)
    if len(text) not in lengths or _HEX_PATTERN.fullmatch(text) is None:
        raise _error(context, f"must be lowercase hexadecimal with length in {tuple(lengths)}")
    return text


def _string_list(value: object, *, context: str, allow_empty: bool = True) -> list[str]:
    if not isinstance(value, list) or (not allow_empty and not value):
        qualifier = "a non-empty list" if not allow_empty else "a list"
        raise _error(context, f"must be {qualifier} of strings")
    result: list[str] = []
    for index, item in enumerate(value):
        result.append(_string(item, context=f"{context}[{index}]"))
    return result


def _optional_string(value: object, *, context: str) -> str | None:
    if value is None:
        return None
    return _string(value, context=context, allow_empty=True)


def _validate_state(
    value: object,
    *,
    claim_context: str,
    expected_name: str,
    observer: str,
    state_trees: Mapping[str, str],
    state_commits: Mapping[str, str],
) -> dict[str, Any]:
    context = f"{claim_context}.states[{expected_name}]"
    state = _object(value, context=context)
    _exact_keys(state, _STATE_FIELDS, context=context)

    if state["state"] != expected_name:
        raise _error(context, f"state must be {expected_name!r}")
    if state["expected"] != CANONICAL_EXPECTATIONS[expected_name]:
        raise _error(
            context,
            f"expected must be {CANONICAL_EXPECTATIONS[expected_name]!r} for DW-001",
        )
    if state["observer"] != observer:
        raise _error(context, "state observer must match claim observer")

    observed = state["observed"]
    if observed not in {"pass", "fail", "error", "timeout"}:
        raise _error(context, "observed must be pass, fail, error, or timeout")
    matched = _boolean(state["matched"], context=f"{context}.matched")
    if matched != (observed == state["expected"]):
        raise _error(context, "matched is inconsistent with observed and expected")

    timed_out = _boolean(state["timed_out"], context=f"{context}.timed_out")
    if timed_out != (observed == "timeout"):
        raise _error(context, "timed_out is inconsistent with observed")

    return_code = state["return_code"]
    if return_code is not None and (not isinstance(return_code, int) or isinstance(return_code, bool)):
        raise _error(context, "return_code must be an integer or null")
    duration = state["duration_seconds"]
    if (
        not isinstance(duration, (int, float))
        or isinstance(duration, bool)
        or duration < 0
    ):
        raise _error(context, "duration_seconds must be a nonnegative number")

    commit_sha = _hex(state["commit_sha"], context=f"{context}.commit_sha", lengths=(40, 64))
    tree_sha = _hex(state["tree_sha"], context=f"{context}.tree_sha", lengths=(40, 64))
    if commit_sha != state_commits[expected_name]:
        raise _error(context, "commit_sha does not match root state_commits")
    if tree_sha != state_trees[expected_name]:
        raise _error(context, "tree_sha does not match root state_trees")

    _hex(state["stdout_sha256"], context=f"{context}.stdout_sha256", lengths=(64,))
    _hex(state["stderr_sha256"], context=f"{context}.stderr_sha256", lengths=(64,))
    _hex(state["invocation_binding"], context=f"{context}.invocation_binding", lengths=(64,))
    _optional_string(state["stdout"], context=f"{context}.stdout")
    _optional_string(state["stderr"], context=f"{context}.stderr")
    _optional_string(state["receipt_outcome"], context=f"{context}.receipt_outcome")
    _optional_string(state["observation_error"], context=f"{context}.observation_error")

    receipt_sha = state["receipt_sha256"]
    if receipt_sha is not None:
        _hex(receipt_sha, context=f"{context}.receipt_sha256", lengths=(64,))
    if state["receipt_producer"] is not None and not isinstance(state["receipt_producer"], dict):
        raise _error(context, "receipt_producer must be an object or null")
    if state["receipt_counts"] is not None and not isinstance(state["receipt_counts"], dict):
        raise _error(context, "receipt_counts must be an object or null")

    if observed in {"pass", "fail"} and state["observation_error"] is not None:
        raise _error(context, "complete observations must not carry observation_error")
    if observed == "error" and not state["observation_error"]:
        raise _error(context, "error observations require a stable observation_error code")

    return state


def _validate_source_report(document: object) -> tuple[dict[str, Any], str]:
    report = _object(document, context="source report")
    _exact_keys(report, _ROOT_FIELDS, context="source report")

    if report["schema_version"] != SUPPORTED_REPORT_SCHEMA_VERSION:
        raise _error(
            "source report.schema_version",
            f"must be {SUPPORTED_REPORT_SCHEMA_VERSION!r}",
        )
    _string(report["tool_version"], context="source report.tool_version")
    _string(report["created_at"], context="source report.created_at")
    _string(report["repository"], context="source report.repository", allow_empty=True)
    base_sha = _hex(report["base_sha"], context="source report.base_sha", lengths=(40, 64))
    head_sha = _hex(report["head_sha"], context="source report.head_sha", lengths=(40, 64))
    _string(report["spec_path"], context="source report.spec_path")
    _boolean(report["spec_external"], context="source report.spec_external")
    _hex(report["spec_sha256"], context="source report.spec_sha256", lengths=(64,))
    _hex(report["witness_sha256"], context="source report.witness_sha256", lengths=(64,))
    _hex(report["report_sha256"], context="source report.report_sha256", lengths=(64,))

    execution = _object(report["execution"], context="source report.execution")
    _exact_keys(execution, _EXECUTION_FIELDS, context="source report.execution")
    _string(execution["environment_mode"], context="source report.execution.environment_mode")
    _string_list(execution["pass_env"], context="source report.execution.pass_env")
    _boolean(execution["output_included"], context="source report.execution.output_included")
    _boolean(execution["sandboxed"], context="source report.execution.sandboxed")
    observer_protocols = _string_list(
        execution["observer_protocols"],
        context="source report.execution.observer_protocols",
        allow_empty=False,
    )

    classification = _object(report["classification"], context="source report.classification")
    _exact_keys(classification, _CLASSIFICATION_FIELDS, context="source report.classification")
    for category in sorted(_CLASSIFICATION_FIELDS):
        if not isinstance(classification[category], list):
            raise _error(f"source report.classification.{category}", "must be a list")

    state_trees = _object(report["state_trees"], context="source report.state_trees")
    state_commits = _object(report["state_commits"], context="source report.state_commits")
    if set(state_trees) != set(STATE_ORDER) or set(state_commits) != set(STATE_ORDER):
        raise _error("source report", "state_trees and state_commits must contain exactly four states")
    normalized_trees = {
        state: _hex(
            state_trees[state],
            context=f"source report.state_trees.{state}",
            lengths=(40, 64),
        )
        for state in STATE_ORDER
    }
    normalized_commits = {
        state: _hex(
            state_commits[state],
            context=f"source report.state_commits.{state}",
            lengths=(40, 64),
        )
        for state in STATE_ORDER
    }
    if normalized_commits["base_base"] != base_sha:
        raise _error("source report.state_commits.base_base", "must equal base_sha")
    if normalized_commits["candidate_candidate"] != head_sha:
        raise _error("source report.state_commits.candidate_candidate", "must equal head_sha")

    claims_value = report["claims"]
    if not isinstance(claims_value, list) or not claims_value:
        raise _error("source report.claims", "must be a non-empty list")

    claim_ids: set[str] = set()
    observers: set[str] = set()
    all_states: list[dict[str, Any]] = []
    for claim_index, claim_value in enumerate(claims_value):
        context = f"source report.claims[{claim_index}]"
        claim = _object(claim_value, context=context)
        _exact_keys(claim, _CLAIM_FIELDS, context=context)
        claim_id = _string(claim["claim_id"], context=f"{context}.claim_id")
        if claim_id in claim_ids:
            raise _error(f"{context}.claim_id", "must be unique")
        claim_ids.add(claim_id)
        _string(claim["description"], context=f"{context}.description", allow_empty=True)
        observer = _string(claim["observer"], context=f"{context}.observer")
        if observer not in OBSERVER_IDENTIFIERS:
            raise _error(f"{context}.observer", "is not supported by DW-001 projection v1")
        observers.add(observer)
        _string_list(claim["command"], context=f"{context}.command", allow_empty=False)
        claim_supported = _boolean(claim["supported"], context=f"{context}.supported")

        states_value = claim["states"]
        if not isinstance(states_value, list) or len(states_value) != len(STATE_ORDER):
            raise _error(f"{context}.states", "must contain exactly four ordered observations")
        states = [
            _validate_state(
                states_value[index],
                claim_context=context,
                expected_name=state_name,
                observer=observer,
                state_trees=normalized_trees,
                state_commits=normalized_commits,
            )
            for index, state_name in enumerate(STATE_ORDER)
        ]
        if claim_supported != all(state["matched"] for state in states):
            raise _error(f"{context}.supported", "is inconsistent with claim observations")
        all_states.extend(states)

    if len(observers) != 1:
        raise _error("source report.claims", "all claims must use one observer arm")
    observer = next(iter(observers))
    if observer_protocols != [observer]:
        raise _error(
            "source report.execution.observer_protocols",
            "must contain exactly the homogeneous claim observer",
        )

    complete = _boolean(report["complete"], context="source report.complete")
    supported = _boolean(report["supported"], context="source report.supported")
    computed_complete = all(state["observed"] in {"pass", "fail"} for state in all_states)
    if complete != computed_complete:
        raise _error("source report.complete", "is inconsistent with state observations")
    computed_supported = complete and all(claim["supported"] for claim in claims_value)
    if supported != computed_supported:
        raise _error("source report.supported", "is inconsistent with claim results")

    try:
        valid, errors = verify_report_document(report)
    except ReportError as exc:
        raise _error("source report", f"integrity verification could not complete: {exc}") from exc
    if not valid:
        raise _error("source report", f"integrity verification failed: {'; '.join(errors)}")

    return report, observer


def _validate_scenario_id(scenario_id: object) -> str:
    value = _string(scenario_id, context="scenario_id")
    if _SCENARIO_ID_PATTERN.fullmatch(value) is None:
        raise _error(
            "scenario_id",
            "must match [A-Za-z0-9][A-Za-z0-9._-]{0,127}",
        )
    return value


def _validate_non_applicable_states(
    value: Mapping[str, str] | None,
) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise _error("non_applicable_states", "must be a mapping")
    result: dict[str, str] = {}
    for state, reason in value.items():
        if state not in STATE_ORDER:
            raise _error("non_applicable_states", f"unknown state: {state!r}")
        result[state] = _string(
            reason,
            context=f"non_applicable_states.{state}",
        )
    return result


def _project_claim(claim: dict[str, Any], required_states: Sequence[str]) -> dict[str, Any]:
    states_by_name = {state["state"]: state for state in claim["states"]}
    selected = [states_by_name[state_name] for state_name in required_states]
    indeterminate = [
        state["state"] for state in selected if state["observed"] not in {"pass", "fail"}
    ]
    contradicted = [state["state"] for state in selected if not state["matched"]]

    if indeterminate:
        decision = "indeterminate"
        reason_code = "required_state_indeterminate"
    elif contradicted:
        decision = "reject"
        reason_code = "predicate_contradicted"
    else:
        decision = "accept"
        reason_code = "predicate_satisfied"

    return {
        "claim_id": claim["claim_id"],
        "decision": decision,
        "reason_code": reason_code,
        "indeterminate_states": indeterminate,
        "contradicted_states": contradicted,
        "states": [
            {
                "state": state["state"],
                "expected": state["expected"],
                "observed": state["observed"],
                "matched": state["matched"],
            }
            for state in selected
        ],
    }


def _project_method(
    report: dict[str, Any],
    *,
    method_id: str,
    required_states: Sequence[str],
    observer_id: str,
    non_applicable_states: Mapping[str, str],
) -> dict[str, Any]:
    unavailable = [state for state in required_states if state in non_applicable_states]
    if unavailable:
        return {
            "method_id": method_id,
            "observer_id": observer_id,
            "combined_method_id": f"{method_id}__{observer_id}",
            "required_states": list(required_states),
            "decision": "not_applicable",
            "reason_code": "required_state_not_applicable",
            "not_applicable_states": [
                {"state": state, "reason": non_applicable_states[state]}
                for state in unavailable
            ],
            "claims": [],
        }

    claims = [_project_claim(claim, required_states) for claim in report["claims"]]
    if any(claim["decision"] == "indeterminate" for claim in claims):
        decision = "indeterminate"
        reason_code = "required_state_indeterminate"
    elif any(claim["decision"] == "reject" for claim in claims):
        decision = "reject"
        reason_code = "predicate_contradicted"
    else:
        decision = "accept"
        reason_code = "predicate_satisfied"

    return {
        "method_id": method_id,
        "observer_id": observer_id,
        "combined_method_id": f"{method_id}__{observer_id}",
        "required_states": list(required_states),
        "decision": decision,
        "reason_code": reason_code,
        "not_applicable_states": [],
        "claims": claims,
    }


def compute_projection_sha256(document: dict[str, Any]) -> str:
    normalized = dict(document)
    normalized["projection_sha256"] = None
    return sha256_document(normalized)


def verify_projection_document(document: object) -> tuple[bool, tuple[str, ...]]:
    if not isinstance(document, dict):
        raise DW001ProjectionError("Projection root must be a JSON object")
    errors: list[str] = []
    actual_fields = set(document)
    if actual_fields != _PROJECTION_FIELDS:
        errors.append(
            "projection field mismatch: "
            f"missing={sorted(_PROJECTION_FIELDS - actual_fields)}, "
            f"extra={sorted(actual_fields - _PROJECTION_FIELDS)}"
        )
    if document.get("schema_version") != PROJECTION_SCHEMA_VERSION:
        errors.append("projection schema_version is missing or unsupported")
    if document.get("study_id") != STUDY_ID:
        errors.append("projection study_id is missing or invalid")
    expected = document.get("projection_sha256")
    if not isinstance(expected, str):
        errors.append("projection_sha256 is missing or invalid")
    else:
        observed = compute_projection_sha256(document)
        if observed != expected:
            errors.append(
                f"projection digest mismatch: expected {expected}, computed {observed}"
            )
    return not errors, tuple(errors)


def project_baselines(
    document: object,
    *,
    scenario_id: str,
    non_applicable_states: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Project all nested DW-001 baseline decisions from one matrix report.

    `non_applicable_states` must come from independently frozen scenario ground
    truth. It is never inferred from command outcomes.
    """

    report, observer = _validate_source_report(document)
    normalized_scenario_id = _validate_scenario_id(scenario_id)
    normalized_non_applicable = _validate_non_applicable_states(non_applicable_states)
    observer_id = OBSERVER_IDENTIFIERS[observer]

    projection: dict[str, Any] = {
        "schema_version": PROJECTION_SCHEMA_VERSION,
        "study_id": STUDY_ID,
        "scenario_id": normalized_scenario_id,
        "source": {
            "report_schema_version": report["schema_version"],
            "tool_version": report["tool_version"],
            "report_sha256": report["report_sha256"],
            "witness_sha256": report["witness_sha256"],
            "base_sha": report["base_sha"],
            "head_sha": report["head_sha"],
            "spec_sha256": report["spec_sha256"],
            "observer": observer,
            "observer_id": observer_id,
        },
        "applicability": {
            "applicable_states": [
                state for state in STATE_ORDER if state not in normalized_non_applicable
            ],
            "non_applicable_states": [
                {"state": state, "reason": normalized_non_applicable[state]}
                for state in STATE_ORDER
                if state in normalized_non_applicable
            ],
        },
        "methods": [
            _project_method(
                report,
                method_id=method_id,
                required_states=required_states,
                observer_id=observer_id,
                non_applicable_states=normalized_non_applicable,
            )
            for method_id, required_states in METHOD_STATE_SETS
        ],
        "projection_sha256": None,
    }
    projection["projection_sha256"] = compute_projection_sha256(projection)
    return projection
