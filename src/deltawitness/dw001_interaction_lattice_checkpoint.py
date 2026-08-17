"""Public-safe semantic checkpoint for the DW-001 interaction lattice.

The complete runtime report remains reproducible and independently verifiable.
This projection retains the exact preregistration identities, candidate path
records, profile invariants, complete mutant incidence table, comparisons,
analysis, policy, and stable result semantic digest. One hosted-run report and
cost record is retained explicitly as diagnostic-only evidence.

The module imports no Coverage.py runtime and keeps the dependency-free base
path usable.
"""

from __future__ import annotations

from copy import deepcopy
import math
from pathlib import Path
import stat
from typing import Any, Mapping, Sequence

from .dw001_interaction_lattice_execution import (
    EXECUTION_PROTOCOL_SHA256,
    PREREGISTRATION_MERGE_COMMIT,
    verify_interaction_lattice_execution_protocol_document,
)
from .dw001_interaction_lattice_plan import (
    build_anonymous_path_multiset,
)
from .dw001_interaction_lattice_result import (
    verify_interaction_witness_lattice_result_document,
)
from .errors import DeltaWitnessError
from .reporting import load_report, sha256_document


CHECKPOINT_SCHEMA_VERSION = (
    "deltawitness.dw001-interaction-witness-lattice-result-checkpoint.v1"
)
CHECKPOINT_ID = (
    "DW-001-INTERACTION-WITNESS-LATTICE-RESULT-CHECKPOINT-V1"
)
CHECKPOINT_SHA256 = (
    "40cf297679c83809368e53f35796d817761c25746302530f29fa4dda603277fc"
)
RESULT_SEMANTIC_SHA256 = (
    "bc2ab879595da61815a17dcc33a09c6334b93dea3fd464f2fe4a5437944ebb77"
)
PLAN_SHA256 = (
    "a79a500feb94c8ad78fe4633f9ca176465113de6297db2d07b2d005f5318e1f1"
)
CATALOG_SHA256 = (
    "2b06a86180a45fcd495c0bcf39365dde0cb590507e9a3528714f9ef58526308e"
)
PRIOR_ART_LOG_SHA256 = (
    "af6cb9782ea01a0e58baed8cfc1a4895dc1a53ed934498b307c6b05e8634c44f"
)
COVERAGEPY_MANIFEST_SHA256 = (
    "28f6430e45fcfda973a1fcd57157e2317f096cc2774e8281244eaf18a9d0dd3f"
)
PR46_RESULT_SEMANTIC_SHA256 = (
    "ec0c2fdd5ac24ba53eb895d9014aab623d2631125b8512ba0e0cbf5105f21ee8"
)
PR46_RESULT_REPORT_SHA256 = (
    "8b248757374ebff4195bad181ad02bc5b0bfc61fa2e21ebf45549686c33d2c41"
)
_MAX_CHECKPOINT_BYTES = 1_000_000

_ROOT_FIELDS = {
    "schema_version",
    "study_id",
    "checkpoint_id",
    "status",
    "partition",
    "preregistration",
    "source",
    "candidate_selectors",
    "profile_invariants",
    "profiles",
    "mutants",
    "summary",
    "comparison",
    "analysis",
    "policy",
    "semantic_sha256",
    "reference_report",
    "checkpoint_sha256",
}
_PREREGISTRATION_FIELDS = {
    "merge_commit",
    "execution_protocol_sha256",
    "plan_sha256",
    "catalog_sha256",
    "prior_art_log_sha256",
    "coveragepy_distribution_manifest_sha256",
    "pr46_result_semantic_sha256",
    "pr46_result_report_sha256",
}
_SOURCE_FIELDS = {
    "source_id",
    "path",
    "symbol",
    "source_sha256",
    "ast_sha256",
    "test_id",
    "test_path",
    "test_sha256",
    "target_id",
    "target_lines",
}
_CANDIDATE_FIELDS = {
    "order",
    "quadrant_id",
    "selector_id",
    "selector",
    "observed",
    "context_partition_valid",
    "executed_statements",
    "executed_arcs",
    "path_shape_sha256",
}
_PROFILE_INVARIANT_FIELDS = {
    "statement_union",
    "statement_intersection",
    "arc_union",
    "arc_intersection",
}
_PROFILE_FIELDS = {
    "order",
    "profile_id",
    "selector_count",
    "quadrants",
    "anonymous_path_multiset_sha256",
    "mfa_independence_witness",
    "role_independence_witness",
}
_MUTANT_FIELDS = {
    "order",
    "operator_id",
    "mutant_id",
    "source_sha256",
    "source_ast_sha256",
    "selector_outcomes",
    "profile_outcomes",
}
_SELECTOR_OUTCOME_FIELDS = {"quadrant_id", "observed"}
_PROFILE_OUTCOME_FIELDS = {"profile_id", "outcome"}
_SUMMARY_FIELDS = {
    "candidate_selector_count",
    "candidate_selector_complete_count",
    "mutant_count",
    "mutant_selector_count",
    "mutant_selector_complete_count",
    "selector_command_count",
    "generated_mutant_count",
    "duplicate_record_count",
    "invalid_record_count",
    "not_applicable_record_count",
    "mutation_score",
}
_COMPARISON_FIELDS = {
    "expected_statement_aggregate_discriminates_profiles",
    "statement_aggregate_discriminates_profiles",
    "expected_arc_aggregate_discriminates_profiles",
    "arc_aggregate_discriminates_profiles",
    "expected_anonymous_path_multiset_discriminates_profiles",
    "anonymous_path_multiset_discriminates_profiles",
    "expected_equal_cardinality_path_multisets_distinct",
    "equal_cardinality_path_multisets_distinct",
    "expected_mfa_independence_agrees_with_drop_mfa",
    "mfa_independence_agrees_with_drop_mfa",
    "expected_role_independence_agrees_with_drop_role",
    "role_independence_agrees_with_drop_role",
    "expected_any_independence_agrees_with_or_gates",
    "any_independence_agrees_with_or_gates",
    "concordant",
}
_ANALYSIS_FIELDS = {
    "status",
    "unexpected_candidate_selector_count",
    "indeterminate_candidate_selector_count",
    "unexpected_profile_count",
    "indeterminate_profile_count",
    "unexpected_mutant_selector_count",
    "indeterminate_mutant_selector_count",
    "unexpected_mutant_count",
    "indeterminate_mutant_count",
    "unexpected_candidate_selector_ids",
    "unexpected_profile_ids",
    "unexpected_mutant_ids",
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
    "mcdc_certification_claim_allowed",
    "coverage_superiority_claim_allowed",
    "mutation_superiority_claim_allowed",
    "method_superiority_claim_allowed",
    "scientific_novelty_claim_allowed",
    "award_level_significance_claim_allowed",
    "production_readiness_claim_allowed",
}
_REFERENCE_FIELDS = {
    "workflow_run_id",
    "workflow_job_id",
    "head_sha",
    "python_version",
    "python_implementation",
    "platform_system",
    "created_at",
    "report_sha256",
    "process_wall_seconds",
    "coverage_wall_seconds",
    "coverage_cpu_seconds",
    "diagnostic_only",
}

_REFERENCE_REPORT = {
    "workflow_run_id": 32063085079,
    "workflow_job_id": 95488644926,
    "head_sha": "050b11760c2c42da274ca20f86ce21d91f6d5b9e",
    "python_version": "3.11.15",
    "python_implementation": "CPython",
    "platform_system": "Linux",
    "created_at": "2026-08-17T17:57:56.265244Z",
    "report_sha256": (
        "f67aa03c024852297db256a70f270f1600f347a7d81e95a0a2337ec4efb79632"
    ),
    "process_wall_seconds": 1.993077,
    "coverage_wall_seconds": 0.229917,
    "coverage_cpu_seconds": 0.229885,
    "diagnostic_only": True,
}


class DW001InteractionLatticeCheckpointError(DeltaWitnessError):
    """Raised when the public-safe result checkpoint is inconsistent."""


def _error(
    context: str,
    message: str,
) -> DW001InteractionLatticeCheckpointError:
    return DW001InteractionLatticeCheckpointError(f"{context}: {message}")


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


def compute_interaction_lattice_checkpoint_sha256(
    document: dict[str, Any],
) -> str:
    """Hash the complete checkpoint with its own digest normalized."""

    if not isinstance(document, dict):
        raise _error("interaction checkpoint", "must be an object")
    normalized = deepcopy(document)
    normalized["checkpoint_sha256"] = None
    return sha256_document(normalized)


def _expected_preregistration() -> dict[str, object]:
    return {
        "merge_commit": PREREGISTRATION_MERGE_COMMIT,
        "execution_protocol_sha256": EXECUTION_PROTOCOL_SHA256,
        "plan_sha256": PLAN_SHA256,
        "catalog_sha256": CATALOG_SHA256,
        "prior_art_log_sha256": PRIOR_ART_LOG_SHA256,
        "coveragepy_distribution_manifest_sha256": (
            COVERAGEPY_MANIFEST_SHA256
        ),
        "pr46_result_semantic_sha256": PR46_RESULT_SEMANTIC_SHA256,
        "pr46_result_report_sha256": PR46_RESULT_REPORT_SHA256,
    }


def _expected_source(plan: Mapping[str, object]) -> dict[str, object]:
    source = plan["source_scope"]
    test = plan["test_scope"]
    target = plan["target_scope"]
    if not all(isinstance(value, dict) for value in (source, test, target)):
        raise _error("interaction checkpoint source", "inputs are malformed")
    assert isinstance(source, dict)
    assert isinstance(test, dict)
    assert isinstance(target, dict)
    return {
        "source_id": source["source_id"],
        "path": source["path"],
        "symbol": source["symbol"],
        "source_sha256": source["source_sha256"],
        "ast_sha256": source["ast_sha256"],
        "test_id": test["test_id"],
        "test_path": test["path"],
        "test_sha256": test["test_sha256"],
        "target_id": target["target_id"],
        "target_lines": target["coverage_target_lines"],
    }


def _path_shape_sha256(
    statements: Sequence[int],
    arcs: Sequence[Sequence[int]],
) -> str:
    return sha256_document(
        {
            "schema_version": (
                "deltawitness.dw001-interaction-path-shape.v1"
            ),
            "statements": list(statements),
            "arcs": [list(arc) for arc in arcs],
        }
    )


def _candidate_records(
    plan: Mapping[str, object],
) -> list[dict[str, object]]:
    path_by_quadrant = {
        str(item["quadrant_id"]): item
        for item in plan["structural_hypotheses"]["quadrant_paths"]
    }
    records: list[dict[str, object]] = []
    for quadrant in plan["truth_table"]:
        quadrant_id = str(quadrant["quadrant_id"])
        path = path_by_quadrant[quadrant_id]
        statements = list(path["expected_executed_statements"])
        arcs = [list(arc) for arc in path["expected_arcs"]]
        digest = _path_shape_sha256(statements, arcs)
        if digest != path["expected_path_shape_sha256"]:
            raise _error(
                f"interaction checkpoint candidate {quadrant_id}",
                "path-shape digest does not match the merged plan",
            )
        records.append(
            {
                "order": quadrant["order"],
                "quadrant_id": quadrant_id,
                "selector_id": quadrant["selector_id"],
                "selector": quadrant["selector"],
                "observed": "pass",
                "context_partition_valid": True,
                "executed_statements": statements,
                "executed_arcs": arcs,
                "path_shape_sha256": digest,
            }
        )
    return records


def _profile_invariants(
    candidates: Sequence[Mapping[str, object]],
    plan: Mapping[str, object],
) -> dict[str, object]:
    by_quadrant = {
        str(item["quadrant_id"]): item for item in candidates
    }
    signatures: list[dict[str, object]] = []
    for profile in plan["profiles"]:
        selected = [
            by_quadrant[str(quadrant)]
            for quadrant in profile["quadrants"]
        ]
        statement_sets = [
            set(item["executed_statements"]) for item in selected
        ]
        arc_sets = [
            {tuple(arc) for arc in item["executed_arcs"]}
            for item in selected
        ]
        signatures.append(
            {
                "statement_union": sorted(set().union(*statement_sets)),
                "statement_intersection": sorted(
                    set.intersection(*statement_sets)
                ),
                "arc_union": [
                    list(arc) for arc in sorted(set().union(*arc_sets))
                ],
                "arc_intersection": [
                    list(arc)
                    for arc in sorted(set.intersection(*arc_sets))
                ],
            }
        )
    first = signatures[0]
    if any(not _strict_equal(first, item) for item in signatures[1:]):
        raise _error(
            "interaction checkpoint profile invariants",
            "profile aggregate signatures are not equal",
        )
    return first


def _profile_records(
    candidates: Sequence[Mapping[str, object]],
    plan: Mapping[str, object],
) -> list[dict[str, object]]:
    by_quadrant = {
        str(item["quadrant_id"]): item for item in candidates
    }
    result: list[dict[str, object]] = []
    for profile in plan["profiles"]:
        quadrants = list(profile["quadrants"])
        path_digests = [
            str(by_quadrant[str(quadrant)]["path_shape_sha256"])
            for quadrant in quadrants
        ]
        multiset = build_anonymous_path_multiset(path_digests)
        if not _strict_equal(
            multiset,
            profile["expected_anonymous_path_multiset"],
        ):
            raise _error(
                f"interaction checkpoint profile {profile['profile_id']}",
                "anonymous path multiset does not match preregistration",
            )
        quadrant_set = set(quadrants)
        result.append(
            {
                "order": profile["order"],
                "profile_id": profile["profile_id"],
                "selector_count": len(quadrants),
                "quadrants": quadrants,
                "anonymous_path_multiset_sha256": multiset[
                    "anonymous_path_multiset_sha256"
                ],
                "mfa_independence_witness": {"TT", "TF"}.issubset(
                    quadrant_set
                ),
                "role_independence_witness": {"TT", "FT"}.issubset(
                    quadrant_set
                ),
            }
        )
    return result


def _mutant_decision(
    operator_id: str,
    quadrant: Mapping[str, object],
) -> bool:
    role_ok = bool(quadrant["role_ok"])
    mfa_ok = bool(quadrant["mfa_ok"])
    if operator_id == "drop-mfa-conjunct-v1":
        return role_ok
    if operator_id == "drop-role-conjunct-v1":
        return mfa_ok
    if operator_id == "or-gates-v1":
        return role_ok or mfa_ok
    if operator_id == "constant-false-v1":
        return False
    if operator_id == "constant-true-v1":
        return True
    raise _error(
        "interaction checkpoint mutant",
        f"unsupported operator {operator_id!r}",
    )


def _mutant_records(
    plan: Mapping[str, object],
    catalog: Mapping[str, object],
) -> list[dict[str, object]]:
    expected_matrix = {
        str(row["operator_id"]): {
            str(item["profile_id"]): item["expected_outcome"]
            for item in row["profile_outcomes"]
        }
        for row in plan["future_execution_contract"][
            "expected_mutation_matrix"
        ]
    }
    generic = [
        item
        for item in catalog["mutants"]
        if item["catalog_role"] == "generic_operator"
    ]
    records: list[dict[str, object]] = []
    for mutant in generic:
        operator_id = str(mutant["operator_id"])
        selector_outcomes: list[dict[str, object]] = []
        observed_by_quadrant: dict[str, str] = {}
        for quadrant in plan["truth_table"]:
            observed = (
                "pass"
                if _mutant_decision(operator_id, quadrant)
                == bool(quadrant["expected_decision"])
                else "fail"
            )
            quadrant_id = str(quadrant["quadrant_id"])
            observed_by_quadrant[quadrant_id] = observed
            selector_outcomes.append(
                {"quadrant_id": quadrant_id, "observed": observed}
            )
        profile_outcomes: list[dict[str, object]] = []
        for profile in plan["profiles"]:
            outcome = (
                "survived"
                if all(
                    observed_by_quadrant[str(quadrant)] == "pass"
                    for quadrant in profile["quadrants"]
                )
                else "killed"
            )
            profile_id = str(profile["profile_id"])
            if outcome != expected_matrix[operator_id][profile_id]:
                raise _error(
                    f"interaction checkpoint mutant {operator_id}",
                    "truth-table incidence differs from preregistration",
                )
            profile_outcomes.append(
                {"profile_id": profile_id, "outcome": outcome}
            )
        records.append(
            {
                "order": mutant["order"],
                "operator_id": operator_id,
                "mutant_id": mutant["mutant_id"],
                "source_sha256": mutant["mutated_source_sha256"],
                "source_ast_sha256": mutant["mutated_ast_sha256"],
                "selector_outcomes": selector_outcomes,
                "profile_outcomes": profile_outcomes,
            }
        )
    return records


def _summary(catalog: Mapping[str, object]) -> dict[str, object]:
    summary = catalog["summary"]
    if not isinstance(summary, dict):
        raise _error("interaction checkpoint summary", "catalog is malformed")
    return {
        "candidate_selector_count": 4,
        "candidate_selector_complete_count": 4,
        "mutant_count": 5,
        "mutant_selector_count": 20,
        "mutant_selector_complete_count": 20,
        "selector_command_count": 24,
        "generated_mutant_count": summary["generated"],
        "duplicate_record_count": summary["duplicate"],
        "invalid_record_count": summary["invalid"],
        "not_applicable_record_count": summary["not_applicable"],
        "mutation_score": None,
    }


def _comparison() -> dict[str, object]:
    return {
        "expected_statement_aggregate_discriminates_profiles": False,
        "statement_aggregate_discriminates_profiles": False,
        "expected_arc_aggregate_discriminates_profiles": False,
        "arc_aggregate_discriminates_profiles": False,
        "expected_anonymous_path_multiset_discriminates_profiles": True,
        "anonymous_path_multiset_discriminates_profiles": True,
        "expected_equal_cardinality_path_multisets_distinct": True,
        "equal_cardinality_path_multisets_distinct": True,
        "expected_mfa_independence_agrees_with_drop_mfa": True,
        "mfa_independence_agrees_with_drop_mfa": True,
        "expected_role_independence_agrees_with_drop_role": True,
        "role_independence_agrees_with_drop_role": True,
        "expected_any_independence_agrees_with_or_gates": True,
        "any_independence_agrees_with_or_gates": True,
        "concordant": True,
    }


def _analysis() -> dict[str, object]:
    return {
        "status": "expected",
        "unexpected_candidate_selector_count": 0,
        "indeterminate_candidate_selector_count": 0,
        "unexpected_profile_count": 0,
        "indeterminate_profile_count": 0,
        "unexpected_mutant_selector_count": 0,
        "indeterminate_mutant_selector_count": 0,
        "unexpected_mutant_count": 0,
        "indeterminate_mutant_count": 0,
        "unexpected_candidate_selector_ids": [],
        "unexpected_profile_ids": [],
        "unexpected_mutant_ids": [],
        "comparison_concordant": True,
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
        "mcdc_certification_claim_allowed": False,
        "coverage_superiority_claim_allowed": False,
        "mutation_superiority_claim_allowed": False,
        "method_superiority_claim_allowed": False,
        "scientific_novelty_claim_allowed": False,
        "award_level_significance_claim_allowed": False,
        "production_readiness_claim_allowed": False,
    }


def build_interaction_lattice_result_checkpoint(
    plan: Mapping[str, object],
    catalog: Mapping[str, object],
) -> dict[str, Any]:
    """Reconstruct the exact stable checkpoint from merged inputs."""

    candidates = _candidate_records(plan)
    document: dict[str, Any] = {
        "schema_version": CHECKPOINT_SCHEMA_VERSION,
        "study_id": "DW-001",
        "checkpoint_id": CHECKPOINT_ID,
        "status": "expected",
        "partition": "development",
        "preregistration": _expected_preregistration(),
        "source": _expected_source(plan),
        "candidate_selectors": candidates,
        "profile_invariants": _profile_invariants(candidates, plan),
        "profiles": _profile_records(candidates, plan),
        "mutants": _mutant_records(plan, catalog),
        "summary": _summary(catalog),
        "comparison": _comparison(),
        "analysis": _analysis(),
        "policy": _policy(),
        "semantic_sha256": RESULT_SEMANTIC_SHA256,
        "reference_report": deepcopy(_REFERENCE_REPORT),
        "checkpoint_sha256": None,
    }
    document["checkpoint_sha256"] = (
        compute_interaction_lattice_checkpoint_sha256(document)
    )
    return document


def project_interaction_lattice_result_checkpoint(
    result: object,
    execution_protocol: object,
    plan: object,
    catalog: object,
    prior_art: object,
    coveragepy_manifest: object,
    pr46_result: object,
) -> dict[str, Any]:
    """Project one verified full result to the stable checkpoint shape."""

    valid, errors = verify_interaction_witness_lattice_result_document(
        result,
        execution_protocol,
        plan,
        catalog,
        prior_art,
        coveragepy_manifest,
        pr46_result,
    )
    if not valid:
        raise _error(
            "interaction checkpoint source result",
            "; ".join(errors),
        )
    if not isinstance(result, dict):
        raise _error("interaction checkpoint source result", "must be an object")
    if not isinstance(plan, dict) or not isinstance(catalog, dict):
        raise _error("interaction checkpoint sources", "must be objects")
    projected = build_interaction_lattice_result_checkpoint(plan, catalog)
    projected["candidate_selectors"] = [
        {
            "order": selector["order"],
            "quadrant_id": selector["quadrant_id"],
            "selector_id": selector["selector_id"],
            "selector": selector["selector"],
            "observed": selector["observed"],
            "context_partition_valid": selector[
                "context_partition_valid"
            ],
            "executed_statements": selector["coverage_receipt"][
                "statement_evidence"
            ]["executed"],
            "executed_arcs": selector["coverage_receipt"][
                "branch_evidence"
            ]["context_arcs"],
            "path_shape_sha256": selector["path_shape"][
                "path_shape_sha256"
            ],
        }
        for selector in result["candidate_selectors"]
    ]
    projected["profile_invariants"] = {
        "statement_union": result["profiles"][0]["statement_union"],
        "statement_intersection": result["profiles"][0][
            "statement_intersection"
        ],
        "arc_union": result["profiles"][0]["arc_union"],
        "arc_intersection": result["profiles"][0]["arc_intersection"],
    }
    projected["profiles"] = [
        {
            "order": profile["order"],
            "profile_id": profile["profile_id"],
            "selector_count": profile["selector_count"],
            "quadrants": profile["quadrants"],
            "anonymous_path_multiset_sha256": profile[
                "anonymous_path_multiset"
            ]["anonymous_path_multiset_sha256"],
            "mfa_independence_witness": profile[
                "mfa_independence_witness"
            ],
            "role_independence_witness": profile[
                "role_independence_witness"
            ],
        }
        for profile in result["profiles"]
    ]
    projected["mutants"] = [
        {
            "order": mutant["order"],
            "operator_id": mutant["operator_id"],
            "mutant_id": mutant["mutant_id"],
            "source_sha256": mutant["source_sha256"],
            "source_ast_sha256": mutant["source_ast_sha256"],
            "selector_outcomes": [
                {
                    "quadrant_id": selector["quadrant_id"],
                    "observed": selector["observed"],
                }
                for selector in mutant["selectors"]
            ],
            "profile_outcomes": [
                {
                    "profile_id": profile["profile_id"],
                    "outcome": profile["outcome"],
                }
                for profile in mutant["profile_outcomes"]
            ],
        }
        for mutant in result["mutants"]
    ]
    projected["summary"] = deepcopy(result["summary"])
    projected["comparison"] = deepcopy(result["comparison"])
    projected["analysis"] = deepcopy(result["analysis"])
    projected["policy"] = deepcopy(result["policy"])
    projected["semantic_sha256"] = result["semantic_sha256"]
    projected["checkpoint_sha256"] = (
        compute_interaction_lattice_checkpoint_sha256(projected)
    )
    return projected


def verify_interaction_lattice_result_checkpoint_document(
    document: object,
    execution_protocol: object,
    plan: object,
    catalog: object,
    prior_art: object,
    coveragepy_manifest: object,
    pr46_result: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify exact checkpoint semantics and source-artifact bindings."""

    errors: list[str] = []
    protocol_valid, protocol_errors = (
        verify_interaction_lattice_execution_protocol_document(
            execution_protocol,
            plan,
            catalog,
            prior_art,
            coveragepy_manifest,
            pr46_result,
        )
    )
    if not protocol_valid:
        errors.extend(
            f"interaction checkpoint protocol: {error}"
            for error in protocol_errors
        )
    if not isinstance(plan, dict) or not isinstance(catalog, dict):
        errors.append("interaction checkpoint sources must be objects")
        return False, tuple(dict.fromkeys(errors))
    try:
        checkpoint = _exact_keys(
            document,
            _ROOT_FIELDS,
            context="interaction checkpoint",
        )
        _exact_keys(
            checkpoint["preregistration"],
            _PREREGISTRATION_FIELDS,
            context="interaction checkpoint.preregistration",
        )
        _exact_keys(
            checkpoint["source"],
            _SOURCE_FIELDS,
            context="interaction checkpoint.source",
        )
        candidate_records = checkpoint["candidate_selectors"]
        if not isinstance(candidate_records, list) or len(candidate_records) != 4:
            raise _error(
                "interaction checkpoint.candidate_selectors",
                "must contain four records",
            )
        for index, item in enumerate(candidate_records):
            record = _exact_keys(
                item,
                _CANDIDATE_FIELDS,
                context=f"interaction checkpoint.candidate_selectors[{index}]",
            )
            if record["observed"] != "pass":
                raise _error(
                    f"interaction checkpoint.candidate_selectors[{index}]",
                    "must retain the complete observed pass",
                )
            if record["context_partition_valid"] is not True:
                raise _error(
                    f"interaction checkpoint.candidate_selectors[{index}]",
                    "context partition must be true",
                )
            if record["path_shape_sha256"] != _path_shape_sha256(
                record["executed_statements"],
                record["executed_arcs"],
            ):
                raise _error(
                    f"interaction checkpoint.candidate_selectors[{index}]",
                    "path-shape digest mismatch",
                )
        _exact_keys(
            checkpoint["profile_invariants"],
            _PROFILE_INVARIANT_FIELDS,
            context="interaction checkpoint.profile_invariants",
        )
        profiles = checkpoint["profiles"]
        if not isinstance(profiles, list) or len(profiles) != 5:
            raise _error(
                "interaction checkpoint.profiles",
                "must contain five records",
            )
        for index, item in enumerate(profiles):
            _exact_keys(
                item,
                _PROFILE_FIELDS,
                context=f"interaction checkpoint.profiles[{index}]",
            )
        mutants = checkpoint["mutants"]
        if not isinstance(mutants, list) or len(mutants) != 5:
            raise _error(
                "interaction checkpoint.mutants",
                "must contain five records",
            )
        for index, item in enumerate(mutants):
            mutant = _exact_keys(
                item,
                _MUTANT_FIELDS,
                context=f"interaction checkpoint.mutants[{index}]",
            )
            selector_outcomes = mutant["selector_outcomes"]
            profile_outcomes = mutant["profile_outcomes"]
            if (
                not isinstance(selector_outcomes, list)
                or len(selector_outcomes) != 4
            ):
                raise _error(
                    f"interaction checkpoint.mutants[{index}].selector_outcomes",
                    "must contain four records",
                )
            if (
                not isinstance(profile_outcomes, list)
                or len(profile_outcomes) != 5
            ):
                raise _error(
                    f"interaction checkpoint.mutants[{index}].profile_outcomes",
                    "must contain five records",
                )
            for selector_index, selector in enumerate(selector_outcomes):
                _exact_keys(
                    selector,
                    _SELECTOR_OUTCOME_FIELDS,
                    context=(
                        f"interaction checkpoint.mutants[{index}]."
                        f"selector_outcomes[{selector_index}]"
                    ),
                )
            for profile_index, profile in enumerate(profile_outcomes):
                _exact_keys(
                    profile,
                    _PROFILE_OUTCOME_FIELDS,
                    context=(
                        f"interaction checkpoint.mutants[{index}]."
                        f"profile_outcomes[{profile_index}]"
                    ),
                )
        _exact_keys(
            checkpoint["summary"],
            _SUMMARY_FIELDS,
            context="interaction checkpoint.summary",
        )
        _exact_keys(
            checkpoint["comparison"],
            _COMPARISON_FIELDS,
            context="interaction checkpoint.comparison",
        )
        _exact_keys(
            checkpoint["analysis"],
            _ANALYSIS_FIELDS,
            context="interaction checkpoint.analysis",
        )
        _exact_keys(
            checkpoint["policy"],
            _POLICY_FIELDS,
            context="interaction checkpoint.policy",
        )
        reference = _exact_keys(
            checkpoint["reference_report"],
            _REFERENCE_FIELDS,
            context="interaction checkpoint.reference_report",
        )
        for field in (
            "process_wall_seconds",
            "coverage_wall_seconds",
            "coverage_cpu_seconds",
        ):
            _finite_nonnegative(
                reference[field],
                context=f"interaction checkpoint.reference_report.{field}",
            )
        if reference["diagnostic_only"] is not True:
            raise _error(
                "interaction checkpoint.reference_report.diagnostic_only",
                "must be true",
            )
        if not _is_sha256(reference["report_sha256"]):
            raise _error(
                "interaction checkpoint.reference_report.report_sha256",
                "must be a SHA-256 digest",
            )
        if not _is_sha256(checkpoint["semantic_sha256"]):
            raise _error(
                "interaction checkpoint.semantic_sha256",
                "must be a SHA-256 digest",
            )
        if not _is_sha256(checkpoint["checkpoint_sha256"]):
            raise _error(
                "interaction checkpoint.checkpoint_sha256",
                "must be a SHA-256 digest",
            )
        expected = build_interaction_lattice_result_checkpoint(plan, catalog)
        if not _strict_equal(expected, checkpoint):
            errors.append(
                "interaction checkpoint: does not match independently "
                "reconstructed semantics"
            )
        computed = compute_interaction_lattice_checkpoint_sha256(checkpoint)
        if checkpoint["checkpoint_sha256"] != computed:
            errors.append(
                "interaction checkpoint.checkpoint_sha256: digest mismatch"
            )
        if computed != CHECKPOINT_SHA256:
            errors.append(
                "interaction checkpoint.checkpoint_sha256: does not match "
                "the reviewed checkpoint"
            )
    except (
        DW001InteractionLatticeCheckpointError,
        DeltaWitnessError,
        KeyError,
        TypeError,
        IndexError,
        ValueError,
        OverflowError,
        MemoryError,
        RecursionError,
    ) as exc:
        errors.append(str(exc))
    unique = tuple(dict.fromkeys(errors))
    return not unique, unique


def load_interaction_lattice_result_checkpoint(
    path: Path,
    execution_protocol: object,
    plan: object,
    catalog: object,
    prior_art: object,
    coveragepy_manifest: object,
    pr46_result: object,
) -> dict[str, Any]:
    """Strict-load one bounded regular non-link checkpoint and verify it."""

    try:
        metadata = path.lstat()
    except OSError as exc:
        raise _error("interaction checkpoint path", "cannot be inspected") from exc
    if path.is_symlink() or not stat.S_ISREG(metadata.st_mode):
        raise _error(
            "interaction checkpoint path",
            "must be a regular non-link file",
        )
    if metadata.st_size <= 0 or metadata.st_size > _MAX_CHECKPOINT_BYTES:
        raise _error(
            "interaction checkpoint path",
            "is outside the size limit",
        )
    document = load_report(path)
    valid, errors = verify_interaction_lattice_result_checkpoint_document(
        document,
        execution_protocol,
        plan,
        catalog,
        prior_art,
        coveragepy_manifest,
        pr46_result,
    )
    if not valid:
        raise _error("interaction checkpoint", "; ".join(errors))
    return document


__all__ = [
    "CHECKPOINT_ID",
    "CHECKPOINT_SCHEMA_VERSION",
    "CHECKPOINT_SHA256",
    "DW001InteractionLatticeCheckpointError",
    "RESULT_SEMANTIC_SHA256",
    "build_interaction_lattice_result_checkpoint",
    "compute_interaction_lattice_checkpoint_sha256",
    "load_interaction_lattice_result_checkpoint",
    "project_interaction_lattice_result_checkpoint",
    "verify_interaction_lattice_result_checkpoint_document",
]
