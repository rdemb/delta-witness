"""Public DW-001 projection API with fail-closed semantic verification.

Projection construction and source-report validation live in the internal
``_dw001_projection`` module. This module independently rechecks every
serialized nested-method decision before accepting the projection digest.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from . import _dw001_projection as _core

CANONICAL_EXPECTATIONS = _core.CANONICAL_EXPECTATIONS
METHOD_STATE_SETS = _core.METHOD_STATE_SETS
OBSERVER_IDENTIFIERS = _core.OBSERVER_IDENTIFIERS
PROJECTION_SCHEMA_VERSION = _core.PROJECTION_SCHEMA_VERSION
STATE_ORDER = _core.STATE_ORDER
STUDY_ID = _core.STUDY_ID
DW001ProjectionError = _core.DW001ProjectionError
compute_projection_sha256 = _core.compute_projection_sha256
project_baselines = _core.project_baselines

_PROJECTION_FIELDS = {
    "schema_version",
    "study_id",
    "scenario_id",
    "source",
    "applicability",
    "methods",
    "projection_sha256",
}
_SOURCE_FIELDS = {
    "report_schema_version",
    "tool_version",
    "report_sha256",
    "witness_sha256",
    "base_sha",
    "head_sha",
    "spec_sha256",
    "observer",
    "observer_id",
}
_APPLICABILITY_FIELDS = {"applicable_states", "non_applicable_states"}
_STATE_REASON_FIELDS = {"state", "reason"}
_METHOD_FIELDS = {
    "method_id",
    "observer_id",
    "combined_method_id",
    "required_states",
    "decision",
    "reason_code",
    "not_applicable_states",
    "claims",
}
_CLAIM_FIELDS = {
    "claim_id",
    "decision",
    "reason_code",
    "indeterminate_states",
    "contradicted_states",
    "states",
}
_STATE_FIELDS = {"state", "expected", "observed", "matched"}


def _state_reasons(value: object, *, context: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise _core._error(context, "must be a list")
    entries: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        item_context = f"{context}[{index}]"
        entry = _core._object(item, context=item_context)
        _core._exact_keys(entry, _STATE_REASON_FIELDS, context=item_context)
        state = _core._string(entry["state"], context=f"{item_context}.state")
        if state not in STATE_ORDER:
            raise _core._error(f"{item_context}.state", f"unknown state: {state!r}")
        if state in seen:
            raise _core._error(f"{item_context}.state", "must be unique")
        seen.add(state)
        reason = _core._string(entry["reason"], context=f"{item_context}.reason")
        entries.append({"state": state, "reason": reason})
    return entries


def _source_observer_id(value: object) -> str:
    source = _core._object(value, context="projection.source")
    _core._exact_keys(source, _SOURCE_FIELDS, context="projection.source")
    if source["report_schema_version"] != _core.SUPPORTED_REPORT_SCHEMA_VERSION:
        raise _core._error(
            "projection.source.report_schema_version",
            f"must be {_core.SUPPORTED_REPORT_SCHEMA_VERSION!r}",
        )
    _core._string(source["tool_version"], context="projection.source.tool_version")
    _core._hex(source["report_sha256"], context="projection.source.report_sha256", lengths=(64,))
    _core._hex(source["witness_sha256"], context="projection.source.witness_sha256", lengths=(64,))
    _core._hex(source["base_sha"], context="projection.source.base_sha", lengths=(40, 64))
    _core._hex(source["head_sha"], context="projection.source.head_sha", lengths=(40, 64))
    _core._hex(source["spec_sha256"], context="projection.source.spec_sha256", lengths=(64,))
    observer = _core._string(source["observer"], context="projection.source.observer")
    if observer not in OBSERVER_IDENTIFIERS:
        raise _core._error("projection.source.observer", "is not supported")
    observer_id = _core._string(source["observer_id"], context="projection.source.observer_id")
    if observer_id != OBSERVER_IDENTIFIERS[observer]:
        raise _core._error("projection.source.observer_id", "is inconsistent with observer")
    return observer_id


def _applicability(value: object) -> dict[str, str]:
    applicability = _core._object(value, context="projection.applicability")
    _core._exact_keys(applicability, _APPLICABILITY_FIELDS, context="projection.applicability")
    applicable = _core._string_list(
        applicability["applicable_states"],
        context="projection.applicability.applicable_states",
    )
    if len(set(applicable)) != len(applicable):
        raise _core._error(
            "projection.applicability.applicable_states",
            "must not contain duplicates",
        )
    if any(state not in STATE_ORDER for state in applicable):
        raise _core._error(
            "projection.applicability.applicable_states",
            "contains an unknown state",
        )
    entries = _state_reasons(
        applicability["non_applicable_states"],
        context="projection.applicability.non_applicable_states",
    )
    non_applicable = {entry["state"]: entry["reason"] for entry in entries}
    expected_applicable = [state for state in STATE_ORDER if state not in non_applicable]
    expected_entries = [
        {"state": state, "reason": non_applicable[state]}
        for state in STATE_ORDER
        if state in non_applicable
    ]
    if applicable != expected_applicable:
        raise _core._error(
            "projection.applicability.applicable_states",
            "must be the canonical complement of non_applicable_states",
        )
    if entries != expected_entries:
        raise _core._error(
            "projection.applicability.non_applicable_states",
            "must use canonical matrix-state order",
        )
    return non_applicable


def _projected_state(value: object, *, context: str, expected_name: str) -> dict[str, Any]:
    state = _core._object(value, context=context)
    _core._exact_keys(state, _STATE_FIELDS, context=context)
    if state["state"] != expected_name:
        raise _core._error(context, f"state must be {expected_name!r}")
    expected = CANONICAL_EXPECTATIONS[expected_name]
    if state["expected"] != expected:
        raise _core._error(context, f"expected must be {expected!r}")
    observed = state["observed"]
    if observed not in {"pass", "fail", "error", "timeout"}:
        raise _core._error(context, "observed must be pass, fail, error, or timeout")
    matched = _core._boolean(state["matched"], context=f"{context}.matched")
    if matched != (observed == expected):
        raise _core._error(context, "matched is inconsistent with observed and expected")
    return state


def _projected_claim(
    value: object,
    *,
    context: str,
    required_states: Sequence[str],
) -> dict[str, Any]:
    claim = _core._object(value, context=context)
    _core._exact_keys(claim, _CLAIM_FIELDS, context=context)
    _core._string(claim["claim_id"], context=f"{context}.claim_id")
    states_value = claim["states"]
    if not isinstance(states_value, list) or len(states_value) != len(required_states):
        raise _core._error(
            f"{context}.states",
            "must contain exactly the method's ordered required states",
        )
    states = [
        _projected_state(
            states_value[index],
            context=f"{context}.states[{state_name}]",
            expected_name=state_name,
        )
        for index, state_name in enumerate(required_states)
    ]
    expected_indeterminate = [
        state["state"] for state in states if state["observed"] not in {"pass", "fail"}
    ]
    expected_contradicted = [state["state"] for state in states if not state["matched"]]
    indeterminate = _core._string_list(
        claim["indeterminate_states"],
        context=f"{context}.indeterminate_states",
    )
    contradicted = _core._string_list(
        claim["contradicted_states"],
        context=f"{context}.contradicted_states",
    )
    if indeterminate != expected_indeterminate:
        raise _core._error(
            f"{context}.indeterminate_states",
            "is inconsistent with projected state observations",
        )
    if contradicted != expected_contradicted:
        raise _core._error(
            f"{context}.contradicted_states",
            "is inconsistent with projected state observations",
        )
    if expected_indeterminate:
        expected_decision = "indeterminate"
        expected_reason = "required_state_indeterminate"
    elif expected_contradicted:
        expected_decision = "reject"
        expected_reason = "predicate_contradicted"
    else:
        expected_decision = "accept"
        expected_reason = "predicate_satisfied"
    if claim["decision"] != expected_decision:
        raise _core._error(context, "claim decision is inconsistent with projected states")
    if claim["reason_code"] != expected_reason:
        raise _core._error(context, "claim reason_code is inconsistent with projected states")
    return claim


def _verify_semantics(document: dict[str, Any]) -> None:
    _core._exact_keys(document, _PROJECTION_FIELDS, context="projection")
    if document["schema_version"] != PROJECTION_SCHEMA_VERSION:
        raise _core._error("projection.schema_version", "is missing or unsupported")
    if document["study_id"] != STUDY_ID:
        raise _core._error("projection.study_id", "is missing or invalid")
    _core._validate_scenario_id(document["scenario_id"])
    observer_id = _source_observer_id(document["source"])
    non_applicable = _applicability(document["applicability"])

    methods_value = document["methods"]
    if not isinstance(methods_value, list) or len(methods_value) != len(METHOD_STATE_SETS):
        raise _core._error("projection.methods", "must contain exactly four ordered methods")

    reference_claim_ids: tuple[str, ...] | None = None
    shared_states: dict[tuple[str, str], dict[str, Any]] = {}
    for index, (method_id, required_states) in enumerate(METHOD_STATE_SETS):
        context = f"projection.methods[{method_id}]"
        method = _core._object(methods_value[index], context=context)
        _core._exact_keys(method, _METHOD_FIELDS, context=context)
        if method["method_id"] != method_id:
            raise _core._error(context, f"method_id must be {method_id!r}")
        if method["observer_id"] != observer_id:
            raise _core._error(context, "observer_id is inconsistent with projection.source")
        if method["combined_method_id"] != f"{method_id}__{observer_id}":
            raise _core._error(context, "combined_method_id is inconsistent")
        required = _core._string_list(
            method["required_states"],
            context=f"{context}.required_states",
            allow_empty=False,
        )
        if required != list(required_states):
            raise _core._error(context, "required_states are inconsistent with method_id")

        unavailable = [state for state in required_states if state in non_applicable]
        entries = _state_reasons(
            method["not_applicable_states"],
            context=f"{context}.not_applicable_states",
        )
        expected_entries = [
            {"state": state, "reason": non_applicable[state]} for state in unavailable
        ]
        if entries != expected_entries:
            raise _core._error(
                context,
                "not_applicable_states are inconsistent with applicability and required_states",
            )

        claims_value = method["claims"]
        if not isinstance(claims_value, list):
            raise _core._error(f"{context}.claims", "must be a list")
        if unavailable:
            if method["decision"] != "not_applicable":
                raise _core._error(context, "method decision is inconsistent with applicability")
            if method["reason_code"] != "required_state_not_applicable":
                raise _core._error(context, "method reason_code is inconsistent with applicability")
            if claims_value:
                raise _core._error(
                    f"{context}.claims",
                    "must be empty when method is not_applicable",
                )
            continue

        if not claims_value:
            raise _core._error(f"{context}.claims", "must be non-empty for an applicable method")
        claims = [
            _projected_claim(
                value,
                context=f"{context}.claims[{claim_index}]",
                required_states=required_states,
            )
            for claim_index, value in enumerate(claims_value)
        ]
        claim_ids = tuple(claim["claim_id"] for claim in claims)
        if len(set(claim_ids)) != len(claim_ids):
            raise _core._error(f"{context}.claims", "claim_id values must be unique")
        if reference_claim_ids is None:
            reference_claim_ids = claim_ids
        elif claim_ids != reference_claim_ids:
            raise _core._error(f"{context}.claims", "claim identities differ across methods")

        for claim in claims:
            for state in claim["states"]:
                key = (claim["claim_id"], state["state"])
                previous = shared_states.get(key)
                if previous is not None and previous != state:
                    raise _core._error(
                        context,
                        "shared state observation differs across projected methods",
                    )
                shared_states[key] = state

        if any(claim["decision"] == "indeterminate" for claim in claims):
            expected_decision = "indeterminate"
            expected_reason = "required_state_indeterminate"
        elif any(claim["decision"] == "reject" for claim in claims):
            expected_decision = "reject"
            expected_reason = "predicate_contradicted"
        else:
            expected_decision = "accept"
            expected_reason = "predicate_satisfied"
        if method["decision"] != expected_decision:
            raise _core._error(context, "method decision is inconsistent with projected claims")
        if method["reason_code"] != expected_reason:
            raise _core._error(context, "method reason_code is inconsistent with projected claims")


def verify_projection_document(document: object) -> tuple[bool, tuple[str, ...]]:
    """Verify the projection digest and all deterministic semantic invariants."""

    if not isinstance(document, dict):
        raise DW001ProjectionError("Projection root must be a JSON object")
    errors: list[str] = []
    try:
        _verify_semantics(document)
    except DW001ProjectionError as exc:
        errors.append(str(exc))

    expected = document.get("projection_sha256")
    try:
        normalized_expected = _core._hex(
            expected,
            context="projection_sha256",
            lengths=(64,),
        )
    except DW001ProjectionError:
        errors.append("projection_sha256 is missing or invalid")
    else:
        observed = compute_projection_sha256(document)
        if observed != normalized_expected:
            errors.append(
                f"projection digest mismatch: expected {normalized_expected}, computed {observed}"
            )
    return not errors, tuple(errors)


__all__ = [
    "CANONICAL_EXPECTATIONS",
    "METHOD_STATE_SETS",
    "STATE_ORDER",
    "DW001ProjectionError",
    "compute_projection_sha256",
    "project_baselines",
    "verify_projection_document",
]
