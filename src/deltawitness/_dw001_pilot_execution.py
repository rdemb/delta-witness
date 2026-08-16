"""Execution and verification for the DW-001 development mechanism pilot.

The runner executes only the exact ten-arm sealed development plan. It stages
all public artifacts outside the requested destination, independently verifies
the complete bundle, and publishes it only after every case and controlled
contrast agrees with the plan. The runner accepts no free-form fixture bytes,
commands, selectors, expectations, exclusions, or denominator decisions.

This module is development-only research infrastructure. It does not create a
holdout, establish ecological effectiveness, authenticate producers, or provide
containment.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path, PurePosixPath
import shutil
import tempfile
import time
from typing import Any, Mapping, Sequence

from .claim_witness import (
    build_claim_witness_declaration,
    run_claim_witness_localization,
    verify_claim_witness_declaration_document,
    verify_claim_witness_localization_document,
)
from .config import load_config
from .dw001 import METHOD_STATE_SETS, project_baselines, verify_projection_document
from .dw001_contracts import (
    RESULT_SCHEMA_VERSION,
    SCENARIO_SCHEMA_VERSION,
    STUDY_ID,
    seal_result_record,
    seal_scenario_manifest,
    verify_result_against_sources,
    verify_result_record_document,
    verify_scenario_manifest_document,
)
from .dw001_fixture_binding import (
    build_fixture_manifest_binding,
    verify_fixture_manifest_binding_document,
)
from .dw001_scenarios import (
    build_fixture_descriptor,
    materialize_synthetic_fixture,
    verify_fixture_descriptor_document,
    verify_fixture_identity_document,
    verify_materialized_fixture,
)
from .errors import DeltaWitnessError
from .matrix import report_to_dict, verify_repository
from .reporting import (
    canonical_json,
    load_report,
    sha256_document,
    verify_report_document,
)


INDEX_SCHEMA_VERSION = "deltawitness.dw001-development-pilot-index.v1"
PILOT_ID = "DW-001-DEV-PILOT-V1"

_INDEX_FIELDS = {
    "schema_version",
    "study_id",
    "pilot_id",
    "partition",
    "plan_sha256",
    "protocol_commit_sha",
    "implementation_commit_sha",
    "created_at",
    "complete",
    "cases",
    "analysis",
    "semantic_sha256",
    "index_sha256",
}
_CASE_FIELDS = {
    "order",
    "case_id",
    "scenario_id",
    "family_id",
    "observer_id",
    "control_role",
    "partition",
    "status",
    "artifacts",
    "stable_evidence",
    "report_evidence",
    "methods",
    "localization",
    "cost",
}
_ARTIFACT_FIELDS = {
    "descriptor",
    "identity",
    "manifest",
    "binding",
    "matrix_report",
    "projection",
    "declaration",
    "localization",
    "result",
}
_STABLE_EVIDENCE_FIELDS = {
    "descriptor_sha256",
    "identity_sha256",
    "manifest_sha256",
    "binding_sha256",
    "witness_sha256",
}
_REPORT_EVIDENCE_FIELDS = {
    "matrix_report_sha256",
    "projection_sha256",
    "declaration_sha256",
    "localization_sha256",
    "localization_report_sha256",
    "result_sha256",
}
_METHOD_FIELDS = {
    "method_id",
    "decision",
    "reason_code",
    "concordant",
    "primary_denominator_eligible",
}
_LOCALIZATION_FIELDS = {
    "required",
    "expected_status",
    "observed_status",
    "concordant",
}
_COST_FIELDS = {
    "status",
    "wall_clock_seconds",
    "cpu_seconds",
    "executed_matrix_states",
    "executed_selector_states",
    "command_count",
    "artifact_count",
    "public_bundle_bytes",
    "review_time_minutes",
    "review_status",
    "missing_reason",
}
_ANALYSIS_FIELDS = {
    "contrasts",
    "headline_score",
    "ecological_inference_allowed",
    "retain_case_tables",
}
_CONTRAST_FIELDS = {"contrast_id", "status", "case_ids", "evidence"}
_EVIDENCE_FIELDS = {"case_id", "metric", "observed"}

_HEX40 = set("0123456789abcdef")
_HEX64 = _HEX40


class PilotExecutionError(DeltaWitnessError):
    """Raised when pilot execution or bundle verification fails closed."""


def _error(context: str, message: str) -> PilotExecutionError:
    return PilotExecutionError(f"{context}: {message}")


def _object(value: object, *, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _error(context, "must be an object")
    return value


def _exact_keys(
    value: Mapping[str, object],
    expected: set[str],
    *,
    context: str,
) -> None:
    actual = set(value)
    if actual != expected:
        raise _error(
            context,
            f"field mismatch; missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}",
        )


def _string(value: object, *, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise _error(context, "must be a non-empty string")
    return value


def _hex(value: object, *, context: str, length: int) -> str:
    text = _string(value, context=context)
    alphabet = _HEX40 if length == 40 else _HEX64
    if len(text) != length or any(character not in alphabet for character in text):
        raise _error(
            context,
            f"must be exactly {length} lowercase hexadecimal characters",
        )
    return text


def _safe_relative_path(value: object, *, context: str) -> str:
    text = _string(value, context=context)
    if text.startswith("/") or "\\" in text or "\x00" in text:
        raise _error(context, "must be a safe repository-relative POSIX path")
    parts = PurePosixPath(text).parts
    if not parts or any(part in {".", ".."} for part in parts):
        raise _error(context, "must be a safe repository-relative POSIX path")
    return text


def _finite_nonnegative(value: object, *, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _error(context, "must be a finite nonnegative number")
    numeric = float(value)
    if not math.isfinite(numeric) or numeric < 0.0:
        raise _error(context, "must be a finite nonnegative number")
    return numeric


def _nonnegative_int(value: object, *, context: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise _error(context, "must be a nonnegative integer")
    return value


def _write_json(path: Path, document: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        json.dumps(
            document,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
        ).encode("utf-8")
        + b"\n"
    )
    if os.name == "posix":
        path.chmod(0o600)


def _load_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        return load_report(path)
    except DeltaWitnessError as exc:
        raise _error(label, str(exc)) from exc


def _prepare_destination(destination: Path) -> tuple[Path, bool]:
    output = Path(destination)
    if output.is_symlink():
        raise _error(
            "development pilot output directory",
            "symbolic-link destinations are not allowed",
        )
    existed = output.exists()
    if existed:
        if not output.is_dir():
            raise _error(
                "development pilot output directory",
                "must be absent or an empty directory",
            )
        if any(output.iterdir()):
            raise _error(
                "development pilot output directory",
                "must be empty",
            )
    parent = output.parent
    if parent.is_symlink() or not parent.is_dir():
        raise _error(
            "development pilot output directory parent",
            "must be a trusted literal directory",
        )
    return output, existed


def _publish_staging(staging: Path, output: Path, output_existed: bool) -> None:
    if output_existed:
        for child in sorted(staging.iterdir(), key=lambda item: item.name):
            child.replace(output / child.name)
        staging.rmdir()
    else:
        staging.replace(output)


def _manifest(
    descriptor: Mapping[str, object],
    identity: Mapping[str, object],
) -> dict[str, Any]:
    observer_id = descriptor["observer_id"]
    states = [
        {
            "state": state["state"],
            "applicable": state["applicable"],
            "applicability_reason": None,
            "expected_observed": state["expected_observed"],
            "failure_cause": state["failure_cause"],
        }
        for state in descriptor["expected_states"]
    ]
    methods = [
        {
            "method_id": method["method_id"],
            "observer_id": observer_id,
            "combined_method_id": f"{method['method_id']}__{observer_id}",
            "expected_decision": method["decision"],
            "reason_code": method["reason_code"],
            "primary_denominator_eligible": False,
        }
        for method in descriptor["expected_methods"]
    ]
    git_identity = identity["git"]
    return seal_scenario_manifest(
        {
            "schema_version": SCENARIO_SCHEMA_VERSION,
            "study_id": STUDY_ID,
            "scenario_id": descriptor["scenario_id"],
            "partition": "development",
            "partition_lock": {
                "status": "development_uncommitted",
                "commitment_sha256": None,
                "commitment_scope": None,
            },
            "provenance": {
                "source_type": "synthetic",
                "source_id": f"synthetic/{descriptor['family_id']}",
                "license_expression": None,
                "authorization_basis": "owned_synthetic_fixture",
                "authorization_reference": None,
                "public_release_allowed": True,
            },
            "git": {
                "repository_id": "synthetic-dw001-fixture",
                "base_sha": git_identity["base_commit_sha"],
                "head_sha": git_identity["head_commit_sha"],
            },
            "paths": deepcopy(identity["paths"]),
            "execution": {
                "command": deepcopy(descriptor["command"]),
                "observer": descriptor["observer"],
                "observer_id": observer_id,
                "timeout_seconds": descriptor["timeout_seconds"],
                "pass_exit_codes": [0],
                "fail_exit_codes": [1],
                "pass_env": [],
                "environment_requirements": [
                    "CPython 3.11 or later",
                    "Git with SHA-1 object-format support",
                    "Disposable non-sensitive execution environment",
                ],
            },
            "ground_truth": {
                "states": states,
                "methods": methods,
                "false_assurance_mechanism": descriptor["family_id"],
                "environment_assumptions": [
                    "The owned synthetic fixture is deterministic.",
                    "No external service is required.",
                    "The runner is not a sandbox.",
                ],
            },
            "review": {
                "status": "approved",
                "reviewers": [
                    {
                        "reviewer_id": "owned-synthetic-contract-review-v1",
                        "role": "ground_truth_reviewer",
                        "independent_of_scenario_author": True,
                        "independent_of_implementation": True,
                        "decision": "approve",
                        "rationale": (
                            "Expected states are fixed by the reviewed owned-"
                            "synthetic family contract and direct controls."
                        ),
                    }
                ],
            },
            "manifest_sha256": None,
        }
    )


def _method_cost_not_run() -> dict[str, object]:
    return {
        "status": "not_run",
        "wall_clock_seconds": None,
        "cpu_seconds": None,
        "state_count": None,
        "command_count": None,
        "review_seconds": None,
        "missing_reason": (
            "Native method-specific cost execution is outside the full-matrix "
            "development mechanism pilot."
        ),
    }


def _baseline_contract_sha256() -> str:
    return sha256_document(
        {
            "schema_version": "deltawitness.dw001-nested-methods.v1",
            "methods": [
                {"method_id": method_id, "required_states": list(states)}
                for method_id, states in METHOD_STATE_SETS
            ],
        }
    )


def _result_record(
    *,
    plan: Mapping[str, object],
    manifest: Mapping[str, object],
    projection: Mapping[str, object],
) -> dict[str, Any]:
    manifest_methods = {
        method["method_id"]: method
        for method in manifest["ground_truth"]["methods"]
    }
    result = seal_result_record(
        {
            "schema_version": RESULT_SCHEMA_VERSION,
            "study_id": STUDY_ID,
            "scenario_id": manifest["scenario_id"],
            "partition": "development",
            "scenario_manifest_sha256": manifest["manifest_sha256"],
            "source": {
                "protocol_commit": plan["protocol_commit_sha"],
                "implementation_commit": plan["implementation_commit_sha"],
                "generator_commit": plan["implementation_commit_sha"],
                "baseline_contract_sha256": _baseline_contract_sha256(),
                "matrix_report_sha256": projection["source"]["report_sha256"],
                "witness_sha256": projection["source"]["witness_sha256"],
                "projection_sha256": projection["projection_sha256"],
                "observer_id": projection["source"]["observer_id"],
            },
            "exclusion": {
                "status": "included",
                "code": None,
                "reason": None,
                "decision_reference": None,
            },
            "deviations": [],
            "methods": [
                {
                    "method_id": method["method_id"],
                    "observer_id": method["observer_id"],
                    "combined_method_id": method["combined_method_id"],
                    "expected_decision": manifest_methods[method["method_id"]][
                        "expected_decision"
                    ],
                    "observed_decision": method["decision"],
                    "observed_reason_code": method["reason_code"],
                    "concordant": (
                        manifest_methods[method["method_id"]]["expected_decision"]
                        == method["decision"]
                    ),
                    "primary_denominator_eligible": False,
                    "denominator_reason_code": "development_partition",
                    "cost": _method_cost_not_run(),
                }
                for method in projection["methods"]
            ],
            "result_sha256": None,
        }
    )
    valid, errors = verify_result_record_document(result)
    if not valid:
        raise _error("development pilot result record", "; ".join(errors))
    cross_valid, cross_errors = verify_result_against_sources(
        result,
        manifest,
        projection,
    )
    if not cross_valid:
        raise _error(
            "development pilot result cross-artifact verification",
            "; ".join(cross_errors),
        )
    return result


def _artifact_paths(case_id: str, localization_required: bool) -> dict[str, str | None]:
    prefix = f"cases/{case_id}"
    return {
        "descriptor": f"{prefix}/descriptor.json",
        "identity": f"{prefix}/identity.json",
        "manifest": f"{prefix}/manifest.json",
        "binding": f"{prefix}/binding.json",
        "matrix_report": f"{prefix}/matrix-report.json",
        "projection": f"{prefix}/projection.json",
        "declaration": (
            f"{prefix}/claim-witness-declaration.json"
            if localization_required
            else None
        ),
        "localization": (
            f"{prefix}/claim-witness-localization.json"
            if localization_required
            else None
        ),
        "result": f"{prefix}/result.json",
    }


def _methods(result: Mapping[str, object]) -> list[dict[str, object]]:
    return [
        {
            "method_id": method["method_id"],
            "decision": method["observed_decision"],
            "reason_code": method["observed_reason_code"],
            "concordant": method["concordant"],
            "primary_denominator_eligible": method[
                "primary_denominator_eligible"
            ],
        }
        for method in result["methods"]
    ]


def _case_semantic_payload(case: Mapping[str, object]) -> dict[str, object]:
    return {
        "order": case["order"],
        "case_id": case["case_id"],
        "scenario_id": case["scenario_id"],
        "family_id": case["family_id"],
        "observer_id": case["observer_id"],
        "control_role": case["control_role"],
        "partition": case["partition"],
        "status": case["status"],
        "stable_evidence": case["stable_evidence"],
        "methods": case["methods"],
        "localization": case["localization"],
    }


def _semantic_payload(index: Mapping[str, object]) -> dict[str, object]:
    cases = index["cases"]
    if not isinstance(cases, list):
        raise _error("development pilot index.cases", "must be a list")
    return {
        "schema_version": index["schema_version"],
        "study_id": index["study_id"],
        "pilot_id": index["pilot_id"],
        "partition": index["partition"],
        "plan_sha256": index["plan_sha256"],
        "protocol_commit_sha": index["protocol_commit_sha"],
        "implementation_commit_sha": index["implementation_commit_sha"],
        "complete": index["complete"],
        "cases": [_case_semantic_payload(case) for case in cases],
        "analysis": index["analysis"],
    }


def compute_semantic_sha256(document: dict[str, Any]) -> str:
    return sha256_document(_semantic_payload(document))


def compute_index_sha256(document: dict[str, Any]) -> str:
    if not isinstance(document, dict):
        raise _error("development pilot index", "must be an object")
    normalized = deepcopy(document)
    normalized["index_sha256"] = None
    return sha256_document(normalized)


def _case_lookup(cases: Sequence[Mapping[str, object]]) -> dict[str, Mapping[str, object]]:
    return {str(case["case_id"]): case for case in cases}


def _method_decision(case: Mapping[str, object], method_id: str) -> str:
    matches = [
        method["decision"]
        for method in case["methods"]
        if method["method_id"] == method_id
    ]
    if len(matches) != 1:
        raise _error(
            f"development pilot analysis.{case['case_id']}",
            f"does not contain exactly one {method_id} decision",
        )
    return str(matches[0])


def _evidence(case_id: str, metric: str, observed: object) -> dict[str, str]:
    return {
        "case_id": case_id,
        "metric": metric,
        "observed": str(observed),
    }


def _analysis(cases: Sequence[Mapping[str, object]]) -> dict[str, object]:
    lookup = _case_lookup(cases)

    valid_ids = ("dev-v1-valid-o0", "dev-v1-valid-o1")
    nondiscriminating_ids = (
        "dev-v1-nondiscriminating-o0",
        "dev-v1-nondiscriminating-o1",
    )
    regression_ids = (
        "dev-v1-candidate-regression-o0",
        "dev-v1-candidate-regression-o1",
    )
    import_ids = ("dev-v1-import-error-o0", "dev-v1-import-error-o1")
    unrelated_ids = (
        "dev-v1-unrelated-assertion-o0",
        "dev-v1-unrelated-assertion-o1",
    )

    contrasts: list[dict[str, object]] = []

    valid_ok = all(
        all(_method_decision(lookup[case_id], method_id) == "accept" for method_id, _ in METHOD_STATE_SETS)
        and lookup[case_id]["localization"]["observed_status"] == "supported"
        for case_id in valid_ids
    )
    contrasts.append(
        {
            "contrast_id": "valid-positive-control",
            "status": "observed_as_expected" if valid_ok else "unexpected",
            "case_ids": list(valid_ids),
            "evidence": [
                _evidence(case_id, "localization", lookup[case_id]["localization"]["observed_status"])
                for case_id in valid_ids
            ],
        }
    )

    discrimination_ok = all(
        _method_decision(lookup[case_id], "M0_FINAL") == "accept"
        and _method_decision(lookup[case_id], "M1_F2P") == "reject"
        for case_id in nondiscriminating_ids
    )
    contrasts.append(
        {
            "contrast_id": "candidate-test-discrimination",
            "status": "observed_as_expected" if discrimination_ok else "unexpected",
            "case_ids": list(nondiscriminating_ids),
            "evidence": [
                _evidence(
                    case_id,
                    "M0_FINAL->M1_F2P",
                    f"{_method_decision(lookup[case_id], 'M0_FINAL')}->{_method_decision(lookup[case_id], 'M1_F2P')}",
                )
                for case_id in nondiscriminating_ids
            ],
        }
    )

    preservation_ok = all(
        _method_decision(lookup[case_id], "M1_F2P") == "accept"
        and _method_decision(lookup[case_id], "M2_F2P_P2P") == "reject"
        for case_id in regression_ids
    )
    contrasts.append(
        {
            "contrast_id": "original-test-preservation",
            "status": "observed_as_expected" if preservation_ok else "unexpected",
            "case_ids": list(regression_ids),
            "evidence": [
                _evidence(
                    case_id,
                    "M1_F2P->M2_F2P_P2P",
                    f"{_method_decision(lookup[case_id], 'M1_F2P')}->{_method_decision(lookup[case_id], 'M2_F2P_P2P')}",
                )
                for case_id in regression_ids
            ],
        }
    )

    import_o0 = lookup[import_ids[0]]
    import_o1 = lookup[import_ids[1]]
    import_ok = (
        _method_decision(import_o0, "M1_F2P") == "accept"
        and _method_decision(import_o1, "M1_F2P") == "indeterminate"
        and import_o0["localization"]["observed_status"] == "indeterminate"
        and import_o1["localization"]["observed_status"] == "indeterminate"
    )
    contrasts.append(
        {
            "contrast_id": "typed-import-error",
            "status": "observed_as_expected" if import_ok else "unexpected",
            "case_ids": list(import_ids),
            "evidence": [
                _evidence(import_ids[0], "M1_F2P", _method_decision(import_o0, "M1_F2P")),
                _evidence(import_ids[1], "M1_F2P", _method_decision(import_o1, "M1_F2P")),
            ],
        }
    )

    mismatch_ok = all(
        _method_decision(lookup[case_id], "M3_FOUR_STATE") == "accept"
        and lookup[case_id]["localization"]["observed_status"] == "unsupported"
        for case_id in unrelated_ids
    )
    contrasts.append(
        {
            "contrast_id": "declared-witness-mismatch",
            "status": "observed_as_expected" if mismatch_ok else "unexpected",
            "case_ids": list(unrelated_ids),
            "evidence": [
                _evidence(
                    case_id,
                    "M3/localization",
                    f"{_method_decision(lookup[case_id], 'M3_FOUR_STATE')}/{lookup[case_id]['localization']['observed_status']}",
                )
                for case_id in unrelated_ids
            ],
        }
    )

    # Preserve the fixed plan order, not the construction order above.
    order = {
        "candidate-test-discrimination": 0,
        "original-test-preservation": 1,
        "typed-import-error": 2,
        "declared-witness-mismatch": 3,
        "valid-positive-control": 4,
    }
    contrasts.sort(key=lambda item: order[str(item["contrast_id"])])
    return {
        "contrasts": contrasts,
        "headline_score": None,
        "ecological_inference_allowed": False,
        "retain_case_tables": True,
    }


def _assert_expected_case(
    plan_case: Mapping[str, object],
    case: Mapping[str, object],
) -> None:
    expected_decisions = [
        (method["method_id"], method["decision"], method["reason_code"])
        for method in plan_case["expected_methods"]
    ]
    observed_decisions = [
        (method["method_id"], method["decision"], method["reason_code"])
        for method in case["methods"]
    ]
    if observed_decisions != expected_decisions:
        raise _error(
            f"development pilot case {case['case_id']}.methods",
            f"does not match sealed plan; expected={expected_decisions!r}, "
            f"observed={observed_decisions!r}",
        )
    if not all(method["concordant"] for method in case["methods"]):
        raise _error(
            f"development pilot case {case['case_id']}.methods",
            "contains a non-concordant method",
        )
    if any(method["primary_denominator_eligible"] for method in case["methods"]):
        raise _error(
            f"development pilot case {case['case_id']}.denominator",
            "development methods cannot be primary-denominator eligible",
        )
    expected_status = plan_case["localization"]["expected_status"]
    if case["localization"]["observed_status"] != expected_status:
        raise _error(
            f"development pilot case {case['case_id']}.localization",
            f"expected {expected_status!r}, observed "
            f"{case['localization']['observed_status']!r}",
        )


def _execute_case(
    *,
    plan: Mapping[str, object],
    plan_case: Mapping[str, object],
    staging: Path,
) -> dict[str, Any]:
    started_wall = time.perf_counter()
    started_cpu = time.process_time()

    case_id = str(plan_case["case_id"])
    descriptor = build_fixture_descriptor(
        scenario_id=case_id,
        family_id=str(plan_case["family_id"]),
        observer=str(plan_case["observer"]),
    )
    descriptor_valid, descriptor_errors = verify_fixture_descriptor_document(descriptor)
    if not descriptor_valid:
        raise _error(
            f"development pilot case {case_id}.descriptor",
            "; ".join(descriptor_errors),
        )

    with tempfile.TemporaryDirectory(
        prefix=f"deltawitness-pilot-{case_id}-"
    ) as working_directory:
        repository = Path(working_directory)
        identity = materialize_synthetic_fixture(descriptor, repository)
        identity_valid, identity_errors = verify_fixture_identity_document(
            identity,
            descriptor,
        )
        materialized_valid, materialized_errors = verify_materialized_fixture(
            identity,
            descriptor,
            repository,
        )
        if not identity_valid or not materialized_valid:
            raise _error(
                f"development pilot case {case_id}.identity",
                "; ".join([*identity_errors, *materialized_errors]),
            )

        manifest = _manifest(descriptor, identity)
        manifest_valid, manifest_errors = verify_scenario_manifest_document(manifest)
        if not manifest_valid:
            raise _error(
                f"development pilot case {case_id}.manifest",
                "; ".join(manifest_errors),
            )

        binding = build_fixture_manifest_binding(descriptor, identity, manifest)
        binding_valid, binding_errors = verify_fixture_manifest_binding_document(
            binding,
            descriptor,
            identity,
            manifest,
        )
        if not binding_valid:
            raise _error(
                f"development pilot case {case_id}.binding",
                "; ".join(binding_errors),
            )

        spec_path = repository / str(identity["specification"]["path"])
        config = load_config(spec_path)
        report_object = verify_repository(
            repository,
            str(identity["git"]["base_commit_sha"]),
            str(identity["git"]["head_commit_sha"]),
            config,
            include_output=False,
        )
        report = report_to_dict(report_object)
        report_valid, report_errors = verify_report_document(report)
        if not report_valid:
            raise _error(
                f"development pilot case {case_id}.matrix_report",
                "; ".join(report_errors),
            )

        projection = project_baselines(report, scenario_id=case_id)
        projection_valid, projection_errors = verify_projection_document(projection)
        if not projection_valid:
            raise _error(
                f"development pilot case {case_id}.projection",
                "; ".join(projection_errors),
            )

        declaration: dict[str, Any] | None = None
        localization: dict[str, Any] | None = None
        localization_plan = plan_case["localization"]
        if localization_plan["required"]:
            declaration = build_claim_witness_declaration(
                spec_sha256=str(plan_case["spec_sha256"]),
                claim_id=str(plan["claim_id"]),
                selectors=list(localization_plan["selectors"]),
            )
            if declaration["declaration_sha256"] != localization_plan[
                "declaration_sha256"
            ]:
                raise _error(
                    f"development pilot case {case_id}.declaration",
                    "digest does not match sealed plan",
                )
            declaration_valid, declaration_errors = (
                verify_claim_witness_declaration_document(declaration)
            )
            if not declaration_valid:
                raise _error(
                    f"development pilot case {case_id}.declaration",
                    "; ".join(declaration_errors),
                )
            localization = run_claim_witness_localization(
                repository,
                config,
                report,
                declaration,
            )
            localization_valid, localization_errors = (
                verify_claim_witness_localization_document(
                    localization,
                    declaration,
                    report,
                )
            )
            if not localization_valid:
                raise _error(
                    f"development pilot case {case_id}.localization",
                    "; ".join(localization_errors),
                )
            observed_localization_status = localization["aggregate_status"]
        else:
            observed_localization_status = "not_applicable"

        result = _result_record(
            plan=plan,
            manifest=manifest,
            projection=projection,
        )

    artifacts = _artifact_paths(
        case_id,
        bool(localization_plan["required"]),
    )
    documents: dict[str, object | None] = {
        "descriptor": descriptor,
        "identity": identity,
        "manifest": manifest,
        "binding": binding,
        "matrix_report": report,
        "projection": projection,
        "declaration": declaration,
        "localization": localization,
        "result": result,
    }
    for name, relative in artifacts.items():
        if relative is not None:
            document = documents[name]
            if document is None:
                raise _error(
                    f"development pilot case {case_id}.{name}",
                    "required artifact is missing",
                )
            _write_json(staging / relative, document)

    artifact_files = [
        staging / relative
        for relative in artifacts.values()
        if relative is not None
    ]
    public_bytes = sum(path.stat().st_size for path in artifact_files)
    finished_wall = time.perf_counter()
    finished_cpu = time.process_time()

    case = {
        "order": plan_case["order"],
        "case_id": case_id,
        "scenario_id": plan_case["scenario_id"],
        "family_id": plan_case["family_id"],
        "observer_id": plan_case["observer_id"],
        "control_role": plan_case["control_role"],
        "partition": "development",
        "status": "valid",
        "artifacts": artifacts,
        "stable_evidence": {
            "descriptor_sha256": descriptor["descriptor_sha256"],
            "identity_sha256": identity["identity_sha256"],
            "manifest_sha256": manifest["manifest_sha256"],
            "binding_sha256": binding["binding_sha256"],
            "witness_sha256": report["witness_sha256"],
        },
        "report_evidence": {
            "matrix_report_sha256": report["report_sha256"],
            "projection_sha256": projection["projection_sha256"],
            "declaration_sha256": (
                declaration["declaration_sha256"]
                if declaration is not None
                else None
            ),
            "localization_sha256": (
                localization["localization_sha256"]
                if localization is not None
                else None
            ),
            "localization_report_sha256": (
                localization["report_sha256"]
                if localization is not None
                else None
            ),
            "result_sha256": result["result_sha256"],
        },
        "methods": _methods(result),
        "localization": {
            "required": localization_plan["required"],
            "expected_status": localization_plan["expected_status"],
            "observed_status": observed_localization_status,
            "concordant": (
                observed_localization_status
                == localization_plan["expected_status"]
            ),
        },
        "cost": {
            "status": "measured_review_unavailable",
            "wall_clock_seconds": float(finished_wall - started_wall),
            "cpu_seconds": float(finished_cpu - started_cpu),
            "executed_matrix_states": 4,
            "executed_selector_states": (
                2 * len(localization_plan["selectors"])
                if localization_plan["required"]
                else 0
            ),
            "command_count": (
                4
                + (
                    2 * len(localization_plan["selectors"])
                    if localization_plan["required"]
                    else 0
                )
            ),
            "artifact_count": len(artifact_files),
            "public_bundle_bytes": public_bytes,
            "review_time_minutes": None,
            "review_status": "unmeasured",
            "missing_reason": (
                "Human review time was not measured during automated "
                "development mechanism execution."
            ),
        },
    }
    _assert_expected_case(plan_case, case)
    return case


def run_pilot(plan: object, output_directory: Path) -> dict[str, Any]:
    from .dw001_pilot import verify_development_pilot_plan_document

    plan_valid, plan_errors = verify_development_pilot_plan_document(plan)
    if not plan_valid:
        raise _error(
            "development pilot plan verification",
            "; ".join(plan_errors),
        )
    assert isinstance(plan, dict)

    output, output_existed = _prepare_destination(Path(output_directory))
    staging = Path(
        tempfile.mkdtemp(
            prefix=".deltawitness-pilot-staging-",
            dir=output.parent,
        )
    )
    try:
        _write_json(staging / "plan.json", plan)
        cases = [
            _execute_case(
                plan=plan,
                plan_case=plan_case,
                staging=staging,
            )
            for plan_case in plan["case_arms"]
        ]
        analysis = _analysis(cases)
        unexpected = [
            contrast["contrast_id"]
            for contrast in analysis["contrasts"]
            if contrast["status"] != "observed_as_expected"
        ]
        if unexpected:
            raise _error(
                "development pilot analysis",
                f"unexpected controlled contrasts: {unexpected}",
            )

        index: dict[str, Any] = {
            "schema_version": INDEX_SCHEMA_VERSION,
            "study_id": STUDY_ID,
            "pilot_id": PILOT_ID,
            "partition": "development",
            "plan_sha256": plan["plan_sha256"],
            "protocol_commit_sha": plan["protocol_commit_sha"],
            "implementation_commit_sha": plan["implementation_commit_sha"],
            "created_at": datetime.now(timezone.utc).isoformat().replace(
                "+00:00", "Z"
            ),
            "complete": True,
            "cases": cases,
            "analysis": analysis,
            "semantic_sha256": None,
            "index_sha256": None,
        }
        index["semantic_sha256"] = compute_semantic_sha256(index)
        index["index_sha256"] = compute_index_sha256(index)
        _write_json(staging / "index.json", index)

        index_valid, index_errors = verify_index(index, plan)
        if not index_valid:
            raise _error(
                "development pilot index self-verification",
                "; ".join(index_errors),
            )
        bundle_valid, bundle_errors = verify_bundle(staging, plan)
        if not bundle_valid:
            raise _error(
                "development pilot bundle self-verification",
                "; ".join(bundle_errors),
            )
        _publish_staging(staging, output, output_existed)
        return index
    except BaseException:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        raise


def _validate_artifacts(
    value: object,
    *,
    case_id: str,
    localization_required: bool,
) -> dict[str, str | None]:
    artifacts = _object(value, context=f"development pilot index case {case_id}.artifacts")
    _exact_keys(
        artifacts,
        _ARTIFACT_FIELDS,
        context=f"development pilot index case {case_id}.artifacts",
    )
    expected = _artifact_paths(case_id, localization_required)
    if artifacts != expected:
        raise _error(
            f"development pilot index case {case_id}.artifacts",
            f"does not match canonical paths; expected={expected!r}, "
            f"observed={artifacts!r}",
        )
    for name, path in artifacts.items():
        if path is not None:
            _safe_relative_path(
                path,
                context=f"development pilot index case {case_id}.artifacts.{name}",
            )
    return artifacts


def _validate_case(
    case: object,
    plan_case: Mapping[str, object],
) -> dict[str, Any]:
    case_id = str(plan_case["case_id"])
    document = _object(case, context=f"development pilot index case {case_id}")
    _exact_keys(
        document,
        _CASE_FIELDS,
        context=f"development pilot index case {case_id}",
    )
    for field in (
        "order",
        "case_id",
        "scenario_id",
        "family_id",
        "observer_id",
        "control_role",
    ):
        if document[field] != plan_case[field]:
            raise _error(
                f"development pilot index case {case_id}.{field}",
                "does not match sealed plan",
            )
    if document["partition"] != "development" or document["status"] != "valid":
        raise _error(
            f"development pilot index case {case_id}.partition/status",
            "must remain valid development evidence",
        )

    localization_plan = plan_case["localization"]
    _validate_artifacts(
        document["artifacts"],
        case_id=case_id,
        localization_required=bool(localization_plan["required"]),
    )

    stable = _object(
        document["stable_evidence"],
        context=f"development pilot index case {case_id}.stable_evidence",
    )
    _exact_keys(
        stable,
        _STABLE_EVIDENCE_FIELDS,
        context=f"development pilot index case {case_id}.stable_evidence",
    )
    for field in _STABLE_EVIDENCE_FIELDS:
        _hex(
            stable[field],
            context=f"development pilot index case {case_id}.stable_evidence.{field}",
            length=64,
        )
    if stable["descriptor_sha256"] != plan_case["descriptor_sha256"]:
        raise _error(
            f"development pilot index case {case_id}.stable_evidence.descriptor_sha256",
            "does not match sealed plan",
        )

    reports = _object(
        document["report_evidence"],
        context=f"development pilot index case {case_id}.report_evidence",
    )
    _exact_keys(
        reports,
        _REPORT_EVIDENCE_FIELDS,
        context=f"development pilot index case {case_id}.report_evidence",
    )
    for field, value in reports.items():
        if value is not None:
            _hex(
                value,
                context=f"development pilot index case {case_id}.report_evidence.{field}",
                length=64,
            )
    if bool(localization_plan["required"]) != (
        reports["declaration_sha256"] is not None
        and reports["localization_sha256"] is not None
        and reports["localization_report_sha256"] is not None
    ):
        raise _error(
            f"development pilot index case {case_id}.report_evidence",
            "localization digest presence is inconsistent with sealed plan",
        )

    methods_value = document["methods"]
    if not isinstance(methods_value, list) or len(methods_value) != 4:
        raise _error(
            f"development pilot index case {case_id}.methods",
            "must contain exactly four methods",
        )
    expected_methods = plan_case["expected_methods"]
    for index, (method, expected) in enumerate(
        zip(methods_value, expected_methods, strict=True)
    ):
        context = f"development pilot index case {case_id}.methods[{index}]"
        method_doc = _object(method, context=context)
        _exact_keys(method_doc, _METHOD_FIELDS, context=context)
        for field in ("method_id", "decision", "reason_code"):
            if method_doc[field] != expected[field]:
                raise _error(
                    f"{context}.{field}",
                    "does not match sealed plan",
                )
        if method_doc["concordant"] is not True:
            raise _error(f"{context}.concordant", "must be true")
        if method_doc["primary_denominator_eligible"] is not False:
            raise _error(
                f"{context}.denominator",
                "development evidence cannot be primary-denominator eligible",
            )

    localization = _object(
        document["localization"],
        context=f"development pilot index case {case_id}.localization",
    )
    _exact_keys(
        localization,
        _LOCALIZATION_FIELDS,
        context=f"development pilot index case {case_id}.localization",
    )
    if localization["required"] is not localization_plan["required"]:
        raise _error(
            f"development pilot index case {case_id}.localization.required",
            "does not match sealed plan",
        )
    if localization["expected_status"] != localization_plan["expected_status"]:
        raise _error(
            f"development pilot index case {case_id}.localization.expected_status",
            "does not match sealed plan",
        )
    if localization["observed_status"] != localization_plan["expected_status"]:
        raise _error(
            f"development pilot index case {case_id}.localization.observed_status",
            "does not match sealed expected status",
        )
    if localization["concordant"] is not True:
        raise _error(
            f"development pilot index case {case_id}.localization.concordant",
            "must be true",
        )

    cost = _object(
        document["cost"],
        context=f"development pilot index case {case_id}.cost",
    )
    _exact_keys(
        cost,
        _COST_FIELDS,
        context=f"development pilot index case {case_id}.cost",
    )
    if cost["status"] != "measured_review_unavailable":
        raise _error(
            f"development pilot index case {case_id}.cost.status",
            "is unsupported",
        )
    _finite_nonnegative(
        cost["wall_clock_seconds"],
        context=f"development pilot index case {case_id}.cost.wall_clock_seconds",
    )
    _finite_nonnegative(
        cost["cpu_seconds"],
        context=f"development pilot index case {case_id}.cost.cpu_seconds",
    )
    for field in (
        "executed_matrix_states",
        "executed_selector_states",
        "command_count",
        "artifact_count",
        "public_bundle_bytes",
    ):
        _nonnegative_int(
            cost[field],
            context=f"development pilot index case {case_id}.cost.{field}",
        )
    expected_selector_states = (
        2 * len(localization_plan["selectors"])
        if localization_plan["required"]
        else 0
    )
    if cost["executed_matrix_states"] != 4:
        raise _error(
            f"development pilot index case {case_id}.cost.executed_matrix_states",
            "must be 4",
        )
    if cost["executed_selector_states"] != expected_selector_states:
        raise _error(
            f"development pilot index case {case_id}.cost.executed_selector_states",
            "does not match sealed localization plan",
        )
    if cost["command_count"] != 4 + expected_selector_states:
        raise _error(
            f"development pilot index case {case_id}.cost.command_count",
            "does not match executed state contract",
        )
    if cost["review_time_minutes"] is not None:
        raise _error(
            f"development pilot index case {case_id}.cost.review_time_minutes",
            "must be null when review is unmeasured",
        )
    if cost["review_status"] != "unmeasured" or not isinstance(
        cost["missing_reason"], str
    ) or not cost["missing_reason"]:
        raise _error(
            f"development pilot index case {case_id}.cost.review",
            "requires explicit unmeasured status and missing reason",
        )
    return document


def _validate_analysis(
    analysis: object,
    cases: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    document = _object(analysis, context="development pilot index.analysis")
    _exact_keys(document, _ANALYSIS_FIELDS, context="development pilot index.analysis")
    expected = _analysis(cases)
    if document != expected:
        raise _error(
            "development pilot index.analysis",
            "does not match machine-derived controlled contrasts",
        )
    contrasts = document["contrasts"]
    if not isinstance(contrasts, list):
        raise _error("development pilot index.analysis.contrasts", "must be a list")
    for index, item in enumerate(contrasts):
        context = f"development pilot index.analysis.contrasts[{index}]"
        contrast = _object(item, context=context)
        _exact_keys(contrast, _CONTRAST_FIELDS, context=context)
        if contrast["status"] != "observed_as_expected":
            raise _error(f"{context}.status", "must be observed_as_expected")
        case_ids = contrast["case_ids"]
        if not isinstance(case_ids, list) or not case_ids:
            raise _error(f"{context}.case_ids", "must be a non-empty list")
        evidence = contrast["evidence"]
        if not isinstance(evidence, list) or not evidence:
            raise _error(f"{context}.evidence", "must be a non-empty list")
        for evidence_index, evidence_item in enumerate(evidence):
            evidence_context = f"{context}.evidence[{evidence_index}]"
            evidence_doc = _object(evidence_item, context=evidence_context)
            _exact_keys(evidence_doc, _EVIDENCE_FIELDS, context=evidence_context)
    return document


def verify_index(
    document: object,
    plan: object,
) -> tuple[bool, tuple[str, ...]]:
    from .dw001_pilot import verify_development_pilot_plan_document

    plan_valid, plan_errors = verify_development_pilot_plan_document(plan)
    if not plan_valid:
        return False, tuple(
            f"development pilot index plan: {error}" for error in plan_errors
        )
    if not isinstance(plan, dict):
        return False, ("development pilot index plan must be an object",)

    try:
        index = _object(document, context="development pilot index")
        _exact_keys(index, _INDEX_FIELDS, context="development pilot index")
        if index["schema_version"] != INDEX_SCHEMA_VERSION:
            raise _error("development pilot index.schema_version", "is unsupported")
        for field, expected in (
            ("study_id", STUDY_ID),
            ("pilot_id", PILOT_ID),
            ("partition", "development"),
            ("plan_sha256", plan["plan_sha256"]),
            ("protocol_commit_sha", plan["protocol_commit_sha"]),
            ("implementation_commit_sha", plan["implementation_commit_sha"]),
            ("complete", True),
        ):
            if index[field] != expected:
                raise _error(
                    f"development pilot index.{field}",
                    "does not match sealed plan or development boundary",
                )
        _string(index["created_at"], context="development pilot index.created_at")
        cases_value = index["cases"]
        if not isinstance(cases_value, list) or len(cases_value) != 10:
            raise _error(
                "development pilot index.cases",
                "must contain exactly ten ordered cases",
            )
        cases = [
            _validate_case(case, plan_case)
            for case, plan_case in zip(
                cases_value,
                plan["case_arms"],
                strict=True,
            )
        ]
        if len({case["case_id"] for case in cases}) != 10:
            raise _error("development pilot index.cases.case_id", "must be unique")
        _validate_analysis(index["analysis"], cases)
        recorded_semantic = _hex(
            index["semantic_sha256"],
            context="development pilot index.semantic_sha256",
            length=64,
        )
        computed_semantic = compute_semantic_sha256(index)
        if recorded_semantic != computed_semantic:
            raise _error(
                "development pilot index.semantic_sha256",
                f"digest mismatch: expected {recorded_semantic}, "
                f"computed {computed_semantic}",
            )
        recorded_index = _hex(
            index["index_sha256"],
            context="development pilot index.index_sha256",
            length=64,
        )
        computed_index = compute_index_sha256(index)
        if recorded_index != computed_index:
            raise _error(
                "development pilot index.index_sha256",
                f"digest mismatch: expected {recorded_index}, computed {computed_index}",
            )
    except (
        PilotExecutionError,
        DeltaWitnessError,
        KeyError,
        TypeError,
        IndexError,
        ValueError,
        OverflowError,
    ) as exc:
        if isinstance(exc, PilotExecutionError):
            return False, (str(exc),)
        return False, (
            "development pilot index: verification failed closed: "
            f"{type(exc).__name__}: {exc}",
        )
    return True, ()


def _verify_case_artifacts(
    *,
    root: Path,
    plan: Mapping[str, object],
    plan_case: Mapping[str, object],
    index_case: Mapping[str, object],
) -> list[str]:
    errors: list[str] = []
    case_id = str(plan_case["case_id"])
    artifacts = index_case["artifacts"]
    documents: dict[str, dict[str, Any] | None] = {}
    for name, relative in artifacts.items():
        if relative is None:
            documents[name] = None
            continue
        try:
            path = root / _safe_relative_path(
                relative,
                context=f"development pilot bundle case {case_id}.{name}",
            )
            if not path.is_file():
                errors.append(
                    f"development pilot bundle case {case_id}.{name}: "
                    f"artifact is missing: {relative}"
                )
                documents[name] = None
                continue
            documents[name] = _load_json(
                path,
                label=f"development pilot bundle case {case_id}.{name}",
            )
        except (PilotExecutionError, DeltaWitnessError) as exc:
            errors.append(str(exc))
            documents[name] = None
    if errors:
        return errors

    descriptor = documents["descriptor"]
    identity = documents["identity"]
    manifest = documents["manifest"]
    binding = documents["binding"]
    report = documents["matrix_report"]
    projection = documents["projection"]
    declaration = documents["declaration"]
    localization = documents["localization"]
    result = documents["result"]
    assert all(
        document is not None
        for document in (
            descriptor,
            identity,
            manifest,
            binding,
            report,
            projection,
            result,
        )
    )

    checks: list[tuple[str, tuple[bool, tuple[str, ...]]]] = [
        (
            "descriptor",
            verify_fixture_descriptor_document(descriptor),
        ),
        (
            "identity",
            verify_fixture_identity_document(identity, descriptor),
        ),
        (
            "manifest",
            verify_scenario_manifest_document(manifest),
        ),
        (
            "binding",
            verify_fixture_manifest_binding_document(
                binding,
                descriptor,
                identity,
                manifest,
            ),
        ),
        (
            "matrix_report",
            verify_report_document(report),
        ),
        (
            "projection",
            verify_projection_document(projection),
        ),
        (
            "result",
            verify_result_record_document(result),
        ),
        (
            "result_sources",
            verify_result_against_sources(result, manifest, projection),
        ),
    ]
    for label, (valid, check_errors) in checks:
        if not valid:
            errors.extend(
                f"development pilot bundle case {case_id}.{label}: {error}"
                for error in check_errors
            )

    if report["spec_sha256"] != plan_case["spec_sha256"]:
        errors.append(
            f"development pilot bundle case {case_id}.matrix_report: "
            "spec digest does not match sealed plan"
        )
    if report["witness_sha256"] != index_case["stable_evidence"]["witness_sha256"]:
        errors.append(
            f"development pilot bundle case {case_id}.matrix_report: "
            "witness digest does not match index"
        )
    if report["report_sha256"] != index_case["report_evidence"]["matrix_report_sha256"]:
        errors.append(
            f"development pilot bundle case {case_id}.matrix_report: "
            "report digest does not match index"
        )
    if projection["projection_sha256"] != index_case["report_evidence"]["projection_sha256"]:
        errors.append(
            f"development pilot bundle case {case_id}.projection: "
            "digest does not match index"
        )
    if result["result_sha256"] != index_case["report_evidence"]["result_sha256"]:
        errors.append(
            f"development pilot bundle case {case_id}.result: "
            "digest does not match index"
        )

    localization_required = bool(plan_case["localization"]["required"])
    if localization_required:
        if declaration is None or localization is None:
            errors.append(
                f"development pilot bundle case {case_id}.localization: "
                "required declaration or localization is missing"
            )
        else:
            declaration_valid, declaration_errors = (
                verify_claim_witness_declaration_document(declaration)
            )
            localization_valid, localization_errors = (
                verify_claim_witness_localization_document(
                    localization,
                    declaration,
                    report,
                )
            )
            if not declaration_valid:
                errors.extend(
                    f"development pilot bundle case {case_id}.declaration: {error}"
                    for error in declaration_errors
                )
            if not localization_valid:
                errors.extend(
                    f"development pilot bundle case {case_id}.localization: {error}"
                    for error in localization_errors
                )
            if declaration["declaration_sha256"] != index_case["report_evidence"]["declaration_sha256"]:
                errors.append(
                    f"development pilot bundle case {case_id}.declaration: "
                    "digest does not match index"
                )
            if localization["localization_sha256"] != index_case["report_evidence"]["localization_sha256"]:
                errors.append(
                    f"development pilot bundle case {case_id}.localization: "
                    "semantic digest does not match index"
                )
            if localization["report_sha256"] != index_case["report_evidence"]["localization_report_sha256"]:
                errors.append(
                    f"development pilot bundle case {case_id}.localization: "
                    "report digest does not match index"
                )
    elif declaration is not None or localization is not None:
        errors.append(
            f"development pilot bundle case {case_id}.localization: "
            "unexpected localization artifacts"
        )

    # Re-materialize the fixed fixture to verify exact identity without retaining
    # an execution worktree in the public bundle.
    try:
        with tempfile.TemporaryDirectory(
            prefix=f"deltawitness-pilot-reverify-{case_id}-"
        ) as directory:
            regenerated = materialize_synthetic_fixture(
                descriptor,
                Path(directory),
            )
            regenerated_valid, regenerated_errors = verify_materialized_fixture(
                regenerated,
                descriptor,
                Path(directory),
            )
            if not regenerated_valid:
                errors.extend(
                    f"development pilot bundle case {case_id}.identity: {error}"
                    for error in regenerated_errors
                )
            if regenerated != identity:
                errors.append(
                    f"development pilot bundle case {case_id}.identity: "
                    "does not reproduce from the retained descriptor"
                )
    except DeltaWitnessError as exc:
        errors.append(
            f"development pilot bundle case {case_id}.identity: "
            f"re-materialization failed: {exc}"
        )
    return errors


def verify_bundle(
    output_directory: Path,
    plan: object,
) -> tuple[bool, tuple[str, ...]]:
    root = Path(output_directory)
    if root.is_symlink() or not root.is_dir():
        return False, (
            "development pilot bundle: output directory must be a literal directory",
        )
    try:
        retained_plan = _load_json(
            root / "plan.json",
            label="development pilot bundle.plan",
        )
        index = _load_json(
            root / "index.json",
            label="development pilot bundle.index",
        )
    except (PilotExecutionError, DeltaWitnessError) as exc:
        return False, (str(exc),)

    from .dw001_pilot import verify_development_pilot_plan_document

    plan_valid, plan_errors = verify_development_pilot_plan_document(plan)
    retained_valid, retained_errors = verify_development_pilot_plan_document(
        retained_plan
    )
    index_valid, index_errors = verify_index(index, plan)
    errors: list[str] = []
    if not plan_valid:
        errors.extend(f"development pilot bundle.plan: {error}" for error in plan_errors)
    if not retained_valid:
        errors.extend(
            f"development pilot bundle.retained_plan: {error}"
            for error in retained_errors
        )
    if retained_plan != plan:
        errors.append(
            "development pilot bundle.plan: retained plan does not match supplied plan"
        )
    if not index_valid:
        errors.extend(f"development pilot bundle.index: {error}" for error in index_errors)
    if errors or not isinstance(plan, dict) or not isinstance(index, dict):
        return False, tuple(dict.fromkeys(errors))

    cases = index["cases"]
    for plan_case, index_case in zip(
        plan["case_arms"],
        cases,
        strict=True,
    ):
        errors.extend(
            _verify_case_artifacts(
                root=root,
                plan=plan,
                plan_case=plan_case,
                index_case=index_case,
            )
        )
    return not errors, tuple(dict.fromkeys(errors))
