"""DW-001 development mechanism-pilot plan and execution boundary.

The sealed plan is a deterministic, development-only contract over the five
fixed owned-synthetic families and both supported observer arms. Every semantic
field is derived from existing fixture and claim-witness contracts; callers may
supply only exact protocol and implementation commit identities.

The execution runner and public pilot index remain deliberately unavailable in
this revision. A valid plan authorizes no command by itself and cannot create a
holdout or confirmatory denominator.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any, Mapping, Sequence

from .claim_witness import (
    AGGREGATE_RULE,
    DECLARATION_SCHEMA_VERSION,
    LOCALIZATION_SCHEMA_VERSION,
    build_claim_witness_declaration,
)
from .dw001 import PROJECTION_SCHEMA_VERSION, STUDY_ID
from .dw001_contracts import RESULT_SCHEMA_VERSION, SCENARIO_SCHEMA_VERSION
from .dw001_fixture_binding import BINDING_SCHEMA_VERSION
from .dw001_scenarios import (
    FIXTURE_DESCRIPTOR_SCHEMA_VERSION,
    FIXTURE_IDENTITY_SCHEMA_VERSION,
    GENERATOR_ID,
    GENERATOR_VERSION,
    build_fixture_descriptor,
    compute_fixture_specification_sha256,
)
from .errors import DeltaWitnessError
from .reporting import sha256_document


PLAN_SCHEMA_VERSION = "deltawitness.dw001-development-pilot-plan.v1"
INDEX_SCHEMA_VERSION = "deltawitness.dw001-development-pilot-index.v1"
PILOT_ID = "DW-001-DEV-PILOT-V1"

_CLAIM_ID = "role-check-regression"
_GIT_SHA_PATTERN = re.compile(r"[0-9a-f]{40}\Z")
_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")

_ROOT_FIELDS = {
    "schema_version",
    "study_id",
    "pilot_id",
    "partition",
    "protocol_commit_sha",
    "implementation_commit_sha",
    "contracts",
    "generator",
    "claim_id",
    "case_arms",
    "analysis_contract",
    "cost_contract",
    "plan_sha256",
}

_CONTRACTS = {
    "matrix_report": "0.3",
    "projection": PROJECTION_SCHEMA_VERSION,
    "fixture_descriptor": FIXTURE_DESCRIPTOR_SCHEMA_VERSION,
    "fixture_identity": FIXTURE_IDENTITY_SCHEMA_VERSION,
    "fixture_manifest_binding": BINDING_SCHEMA_VERSION,
    "scenario_manifest": SCENARIO_SCHEMA_VERSION,
    "result_record": RESULT_SCHEMA_VERSION,
    "claim_witness_declaration": DECLARATION_SCHEMA_VERSION,
    "claim_witness_localization": LOCALIZATION_SCHEMA_VERSION,
}

_ANALYSIS_CONTRACT = {
    "contrast_ids": [
        "candidate-test-discrimination",
        "original-test-preservation",
        "typed-import-error",
        "declared-witness-mismatch",
        "valid-positive-control",
    ],
    "retain_case_tables": True,
    "headline_score_allowed": False,
    "ecological_inference_allowed": False,
    "aggregate_release_requires_all_cases_valid": True,
}

_COST_CONTRACT = {
    "measured_fields": [
        "wall_clock_seconds",
        "cpu_seconds",
        "executed_matrix_states",
        "executed_selector_states",
        "command_count",
        "artifact_count",
        "public_bundle_bytes",
        "review_time_minutes",
    ],
    "missing_numeric_value": None,
    "missing_reason_required": True,
    "nonfinite_allowed": False,
    "negative_allowed": False,
    "projected_method_native_cost_allowed": False,
}

# order, case ID, family, observer, localization required, selectors, expected
# localization status. These values are part of the sealed development-only
# population contract, not runtime inputs.
_CASE_DEFINITIONS: tuple[
    tuple[str, str, str, bool, tuple[str, ...], str], ...
] = (
    (
        "dev-v1-valid-o0",
        "valid-discriminating-regression",
        "exit-code-v1",
        True,
        ("test_access.AccessTests.test_viewer_is_denied",),
        "supported",
    ),
    (
        "dev-v1-valid-o1",
        "valid-discriminating-regression",
        "outcome-receipt-v1",
        True,
        ("test_access.AccessTests.test_viewer_is_denied",),
        "supported",
    ),
    (
        "dev-v1-nondiscriminating-o0",
        "non-discriminating-candidate-test",
        "exit-code-v1",
        False,
        (),
        "not_applicable",
    ),
    (
        "dev-v1-nondiscriminating-o1",
        "non-discriminating-candidate-test",
        "outcome-receipt-v1",
        False,
        (),
        "not_applicable",
    ),
    (
        "dev-v1-candidate-regression-o0",
        "candidate-regression-against-base-tests",
        "exit-code-v1",
        False,
        (),
        "not_applicable",
    ),
    (
        "dev-v1-candidate-regression-o1",
        "candidate-regression-against-base-tests",
        "outcome-receipt-v1",
        False,
        (),
        "not_applicable",
    ),
    (
        "dev-v1-import-error-o0",
        "wrong-reason-base-import-failure",
        "exit-code-v1",
        True,
        ("test_access.AccessTests.test_role_is_normalized",),
        "indeterminate",
    ),
    (
        "dev-v1-import-error-o1",
        "wrong-reason-base-import-failure",
        "outcome-receipt-v1",
        True,
        ("test_access.AccessTests.test_role_is_normalized",),
        "indeterminate",
    ),
    (
        "dev-v1-unrelated-assertion-o0",
        "wrong-reason-unrelated-assertion",
        "exit-code-v1",
        True,
        ("test_access.AccessTests.test_viewer_result_is_boolean",),
        "unsupported",
    ),
    (
        "dev-v1-unrelated-assertion-o1",
        "wrong-reason-unrelated-assertion",
        "outcome-receipt-v1",
        True,
        ("test_access.AccessTests.test_viewer_result_is_boolean",),
        "unsupported",
    ),
)


class DW001PilotError(DeltaWitnessError):
    """Raised when a development-pilot plan or bundle is unsafe or invalid."""


def _error(context: str, message: str) -> DW001PilotError:
    return DW001PilotError(f"{context}: {message}")


def _git_sha(value: object, *, context: str) -> str:
    if not isinstance(value, str) or _GIT_SHA_PATTERN.fullmatch(value) is None:
        raise _error(context, "must be exactly 40 lowercase hexadecimal characters")
    return value


def _sha256(value: object, *, context: str) -> str:
    if not isinstance(value, str) or _SHA256_PATTERN.fullmatch(value) is None:
        raise _error(context, "must be exactly 64 lowercase hexadecimal characters")
    return value


def _exact_root(document: object) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise _error("development pilot plan", "must be an object")
    actual = set(document)
    if actual != _ROOT_FIELDS:
        raise _error(
            "development pilot plan",
            f"field mismatch; missing={sorted(_ROOT_FIELDS - actual)}, "
            f"extra={sorted(actual - _ROOT_FIELDS)}",
        )
    return document


def _case_arm(
    *,
    order: int,
    case_id: str,
    family_id: str,
    observer: str,
    localization_required: bool,
    selectors: tuple[str, ...],
    expected_localization_status: str,
) -> dict[str, Any]:
    descriptor = build_fixture_descriptor(
        scenario_id=case_id,
        family_id=family_id,
        observer=observer,
    )
    spec_sha256 = compute_fixture_specification_sha256(descriptor)

    declaration_sha256: str | None = None
    aggregate_rule: str | None = None
    selector_list = list(selectors)
    if localization_required:
        declaration = build_claim_witness_declaration(
            spec_sha256=spec_sha256,
            claim_id=_CLAIM_ID,
            selectors=selector_list,
        )
        declaration_sha256 = declaration["declaration_sha256"]
        aggregate_rule = AGGREGATE_RULE

    return {
        "order": order,
        "case_id": case_id,
        "scenario_id": case_id,
        "family_id": family_id,
        "observer": observer,
        "observer_id": descriptor["observer_id"],
        "control_role": descriptor["control_role"],
        "partition": "development",
        "primary_denominator_eligible": False,
        "descriptor_sha256": descriptor["descriptor_sha256"],
        "spec_sha256": spec_sha256,
        "expected_states": deepcopy(descriptor["expected_states"]),
        "expected_methods": deepcopy(descriptor["expected_methods"]),
        "localization": {
            "required": localization_required,
            "selectors": selector_list,
            "aggregate_rule": aggregate_rule,
            "expected_status": expected_localization_status,
            "declaration_sha256": declaration_sha256,
        },
    }


def compute_development_pilot_plan_sha256(document: dict[str, Any]) -> str:
    """Hash canonical plan bytes with ``plan_sha256`` normalized to null."""

    if not isinstance(document, dict):
        raise _error("development pilot plan", "must be an object")
    normalized = deepcopy(document)
    normalized["plan_sha256"] = None
    return sha256_document(normalized)


def build_development_pilot_plan(
    *,
    protocol_commit_sha: str,
    implementation_commit_sha: str,
) -> dict[str, Any]:
    """Build the exact sealed ten-arm development-only pilot plan."""

    protocol_sha = _git_sha(
        protocol_commit_sha,
        context="development pilot plan.protocol_commit_sha",
    )
    implementation_sha = _git_sha(
        implementation_commit_sha,
        context="development pilot plan.implementation_commit_sha",
    )

    case_arms = [
        _case_arm(
            order=order,
            case_id=case_id,
            family_id=family_id,
            observer=observer,
            localization_required=localization_required,
            selectors=selectors,
            expected_localization_status=expected_status,
        )
        for order, (
            case_id,
            family_id,
            observer,
            localization_required,
            selectors,
            expected_status,
        ) in enumerate(_CASE_DEFINITIONS, start=1)
    ]

    plan: dict[str, Any] = {
        "schema_version": PLAN_SCHEMA_VERSION,
        "study_id": STUDY_ID,
        "pilot_id": PILOT_ID,
        "partition": "development",
        "protocol_commit_sha": protocol_sha,
        "implementation_commit_sha": implementation_sha,
        "contracts": deepcopy(_CONTRACTS),
        "generator": {
            "id": GENERATOR_ID,
            "version": GENERATOR_VERSION,
        },
        "claim_id": _CLAIM_ID,
        "case_arms": case_arms,
        "analysis_contract": deepcopy(_ANALYSIS_CONTRACT),
        "cost_contract": deepcopy(_COST_CONTRACT),
        "plan_sha256": None,
    }
    plan["plan_sha256"] = compute_development_pilot_plan_sha256(plan)
    return plan


def _differences(
    expected: object,
    observed: object,
    *,
    context: str,
) -> list[str]:
    """Return deterministic structural/semantic differences without dereference risk."""

    errors: list[str] = []
    if isinstance(expected, dict):
        if not isinstance(observed, dict):
            return [f"{context}: must be an object matching the canonical sealed plan"]
        expected_keys = set(expected)
        observed_keys = set(observed)
        if expected_keys != observed_keys:
            errors.append(
                f"{context}: field mismatch; "
                f"missing={sorted(expected_keys - observed_keys)}, "
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
            return [f"{context}: must be a list matching the canonical sealed plan"]
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
            f"{context}: does not match canonical sealed plan; "
            f"expected={expected!r}, observed={observed!r}"
        )
    return errors


def verify_development_pilot_plan_document(
    document: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify plan structure, digest, and exact derivation from fixed contracts."""

    try:
        plan = _exact_root(document)
        protocol_sha = _git_sha(
            plan["protocol_commit_sha"],
            context="development pilot plan.protocol_commit_sha",
        )
        implementation_sha = _git_sha(
            plan["implementation_commit_sha"],
            context="development pilot plan.implementation_commit_sha",
        )
        recorded_digest = _sha256(
            plan["plan_sha256"],
            context="development pilot plan.plan_sha256",
        )
        computed_digest = compute_development_pilot_plan_sha256(plan)
        expected = build_development_pilot_plan(
            protocol_commit_sha=protocol_sha,
            implementation_commit_sha=implementation_sha,
        )
    except (
        DW001PilotError,
        DeltaWitnessError,
        KeyError,
        TypeError,
        IndexError,
        ValueError,
        OverflowError,
    ) as exc:
        if isinstance(exc, DW001PilotError):
            return False, (str(exc),)
        return False, (
            "development pilot plan: verification failed closed: "
            f"{type(exc).__name__}: {exc}",
        )

    errors: list[str] = []
    if recorded_digest != computed_digest:
        errors.append(
            "development pilot plan.plan_sha256: digest mismatch; "
            f"expected {recorded_digest}, computed {computed_digest}"
        )
    errors.extend(
        _differences(
            expected,
            plan,
            context="development pilot plan",
        )
    )
    unique = tuple(dict.fromkeys(errors))
    return not unique, unique


def _unimplemented() -> DW001PilotError:
    return DW001PilotError(
        "DW-001 development pilot execution is not implemented or authorized"
    )


def compute_development_pilot_index_sha256(document: dict[str, Any]) -> str:
    raise _unimplemented()


def run_development_pilot(
    plan: object,
    output_directory: Path,
) -> dict[str, Any]:
    raise _unimplemented()


def verify_development_pilot_index_document(
    document: object,
    plan: object,
) -> tuple[bool, tuple[str, ...]]:
    raise _unimplemented()


__all__ = [
    "INDEX_SCHEMA_VERSION",
    "PILOT_ID",
    "PLAN_SCHEMA_VERSION",
    "DW001PilotError",
    "build_development_pilot_plan",
    "compute_development_pilot_index_sha256",
    "compute_development_pilot_plan_sha256",
    "run_development_pilot",
    "verify_development_pilot_index_document",
    "verify_development_pilot_plan_document",
]
