"""Frozen Gate 1 mutation-plan and deterministic mutant catalog.

This module defines a pre-execution, development-only contract for one fixed
owned-synthetic authorization predicate. It freezes a minimal generic stdlib-AST
operator set, paired strong/weak selector profiles, exact target and mutant
identities, and generation controls for duplicate, invalid, and not-applicable
outcomes before any mutation test result is observed.

The catalog parses and compiles fixed project-owned bytes only. It does not run
mutants or tests, authorize external repositories, produce a mutation score, or
establish oracle strength.
"""

from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import re
from typing import Any, Mapping

from . import _dw001_weak_proxy as _weak_proxy
from .errors import DeltaWitnessError
from .reporting import sha256_document


PLAN_SCHEMA_VERSION = "deltawitness.dw001-claim-scoped-mutation-plan.v1"
CATALOG_SCHEMA_VERSION = "deltawitness.dw001-claim-scoped-mutant-catalog.v1"
PLAN_ID = "DW-001-CLAIM-SCOPED-MUTATION-PLAN-V1"
OPERATOR_SET_ID = "python-boolean-predicate-minimal-v1"
ADAPTER_ID = "python-stdlib-ast-return-v1"

_TARGET_SCHEMA_VERSION = "deltawitness.dw001-python-ast-target.v1"
_MUTANT_SCHEMA_VERSION = "deltawitness.dw001-python-mutant.v1"
_AST_SCHEMA_VERSION = "deltawitness.python-semantic-ast.v1"
_SOURCE_ID = "authorization-predicate-candidate-v1"
_SOURCE_PATH = "src/access.py"
_SOURCE_SYMBOL = "is_admin"
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")

_PLAN_FIELDS = {
    "schema_version",
    "study_id",
    "plan_id",
    "status",
    "partition",
    "adapter",
    "source_scope",
    "operator_set",
    "generation_controls",
    "known_challenge_control",
    "calibration_profiles",
    "reference_claim_checks",
    "generation_contract",
    "future_execution_contract",
    "execution_authorized",
    "holdout_selected",
    "primary_denominator_eligible",
    "plan_sha256",
}
_CATALOG_FIELDS = {
    "schema_version",
    "study_id",
    "plan_id",
    "plan_sha256",
    "partition",
    "source",
    "target",
    "mutants",
    "known_challenge_control",
    "summary",
    "catalog_sha256",
}

_GENERIC_OPERATORS: tuple[dict[str, object], ...] = (
    {
        "order": 1,
        "operator_id": "return-constant-false-v1",
        "operator_class": "boolean_constant_replacement",
        "target_kind": "return_expression",
        "outcome_blind_selection": True,
    },
    {
        "order": 2,
        "operator_id": "return-constant-true-v1",
        "operator_class": "boolean_constant_replacement",
        "target_kind": "return_expression",
        "outcome_blind_selection": True,
    },
    {
        "order": 3,
        "operator_id": "comparison-eq-to-ne-v1",
        "operator_class": "relational_operator_replacement",
        "target_kind": "single_eq_comparison",
        "outcome_blind_selection": True,
    },
)

_GENERATION_CONTROLS: tuple[dict[str, object], ...] = (
    {
        "order": 4,
        "operator_id": "duplicate-false-control-v1",
        "control_purpose": "duplicate_retention",
        "included_in_generic_operator_set": False,
    },
    {
        "order": 5,
        "operator_id": "not-applicable-addition-control-v1",
        "control_purpose": "not_applicable_retention",
        "included_in_generic_operator_set": False,
    },
    {
        "order": 6,
        "operator_id": "invalid-render-control-v1",
        "control_purpose": "invalid_retention",
        "included_in_generic_operator_set": False,
    },
)


class DW001MutationPlanError(DeltaWitnessError):
    """Raised when the mutation plan or catalog is unsafe or inconsistent."""


def _error(context: str, message: str) -> DW001MutationPlanError:
    return DW001MutationPlanError(f"{context}: {message}")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256(value: object, *, context: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise _error(context, "must be exactly 64 lowercase hexadecimal characters")
    return value


def _semantic_ast_value(value: object) -> object:
    """Build a version-stable AST payload by omitting empty optional fields."""

    if isinstance(value, ast.AST):
        fields: dict[str, object] = {}
        for field in value._fields:
            child = getattr(value, field, None)
            if child is None or child == []:
                continue
            fields[field] = _semantic_ast_value(child)
        return {"node": type(value).__name__, "fields": fields}
    if isinstance(value, list):
        return [_semantic_ast_value(item) for item in value]
    return value


def _ast_sha256_from_tree(tree: ast.AST) -> str:
    return sha256_document(
        {
            "schema_version": _AST_SCHEMA_VERSION,
            "tree": _semantic_ast_value(tree),
        }
    )


def _ast_sha256(source: str) -> str:
    try:
        tree = ast.parse(source, filename=_SOURCE_PATH, mode="exec")
    except (SyntaxError, MemoryError, RecursionError) as exc:
        raise _error("claim-scoped mutation source", "cannot be parsed") from exc
    return _ast_sha256_from_tree(tree)


def _known_challenge_control(source_sha256: str) -> dict[str, object]:
    return {
        "mutant_id": "nonempty-role-boolean-v1",
        "origin": "PR-34-fixed-control",
        "source_sha256": source_sha256,
        "mutated_source_sha256": _sha256_bytes(
            _weak_proxy.MUTANT_CODE.encode("utf-8")
        ),
        "mutated_ast_sha256": _ast_sha256(_weak_proxy.MUTANT_CODE),
        "included_in_generic_operator_set": False,
        "counts_toward_operator_generalization": False,
        "source_body_published": False,
    }


def compute_mutation_plan_sha256(document: dict[str, Any]) -> str:
    """Hash canonical plan bytes with the plan digest normalized to null."""

    if not isinstance(document, dict):
        raise _error("claim-scoped mutation plan", "must be an object")
    normalized = deepcopy(document)
    normalized["plan_sha256"] = None
    return sha256_document(normalized)


def compute_mutant_catalog_sha256(document: dict[str, Any]) -> str:
    """Hash canonical catalog bytes with the catalog digest normalized to null."""

    if not isinstance(document, dict):
        raise _error("claim-scoped mutant catalog", "must be an object")
    normalized = deepcopy(document)
    normalized["catalog_sha256"] = None
    return sha256_document(normalized)


def build_claim_scoped_mutation_plan() -> dict[str, Any]:
    """Build the exact pre-execution mutation calibration plan."""

    source_sha256 = _sha256_bytes(_weak_proxy.CANDIDATE_CODE.encode("utf-8"))
    plan: dict[str, Any] = {
        "schema_version": PLAN_SCHEMA_VERSION,
        "study_id": "DW-001",
        "plan_id": PLAN_ID,
        "status": "pre_execution_frozen_design",
        "partition": "development",
        "adapter": {
            "id": ADAPTER_ID,
            "version": "1",
            "parser": "stdlib-ast",
            "round_trip": "ast-unparse-v1",
            "runtime_dependency": False,
        },
        "source_scope": {
            "source_id": _SOURCE_ID,
            "path": _SOURCE_PATH,
            "symbol": _SOURCE_SYMBOL,
            "language": "python",
            "parser": "stdlib-ast",
            "source_sha256": source_sha256,
            "ast_sha256": _ast_sha256(_weak_proxy.CANDIDATE_CODE),
            "target_cardinality": 1,
            "source_body_published": False,
        },
        "operator_set": {
            "id": OPERATOR_SET_ID,
            "selection_status": "frozen_before_calibration_execution",
            "selection_basis": (
                "minimal_boolean_constant_and_relational_replacement"
            ),
            "operators": deepcopy(list(_GENERIC_OPERATORS)),
        },
        "generation_controls": deepcopy(list(_GENERATION_CONTROLS)),
        "known_challenge_control": _known_challenge_control(source_sha256),
        "calibration_profiles": [
            {
                "order": 1,
                "profile_id": "strong-authorization-oracle-v1",
                "profile_role": "positive_control",
                "source_id": _SOURCE_ID,
                "operator_set_id": OPERATOR_SET_ID,
                "selectors": [
                    "test_access.AccessTests.test_admin_is_allowed",
                    "test_access.AccessTests.test_viewer_is_denied",
                ],
                "primary_denominator_eligible": False,
            },
            {
                "order": 2,
                "profile_id": "weak-boolean-proxy-v1",
                "profile_role": "negative_control",
                "source_id": _SOURCE_ID,
                "operator_set_id": OPERATOR_SET_ID,
                "selectors": [
                    "test_access.AccessTests.test_viewer_result_is_boolean"
                ],
                "primary_denominator_eligible": False,
            },
        ],
        "reference_claim_checks": [
            "test_hidden_claim.HiddenClaimTests.test_admin_is_allowed",
            "test_hidden_claim.HiddenClaimTests.test_viewer_is_denied",
        ],
        "generation_contract": {
            "target_identity_schema": _TARGET_SCHEMA_VERSION,
            "mutant_identity_schema": _MUTANT_SCHEMA_VERSION,
            "generation_statuses": [
                "generated",
                "duplicate",
                "invalid",
                "not_applicable",
            ],
            "compile_required_for_generated": True,
            "duplicate_key": "mutated_source_sha256",
            "retain_all_records": True,
            "source_body_published": False,
        },
        "future_execution_contract": {
            "outcome_taxonomy": [
                "killed",
                "survived",
                "invalid",
                "equivalent_review_required",
                "indeterminate",
            ],
            "retain_complete_mutant_table": True,
            "headline_score": None,
            "universal_threshold": None,
            "merge_blocker_authorized": False,
            "execution_status": "not_implemented",
        },
        "execution_authorized": False,
        "holdout_selected": False,
        "primary_denominator_eligible": False,
        "plan_sha256": None,
    }
    plan["plan_sha256"] = compute_mutation_plan_sha256(plan)
    return plan


def _differences(
    expected: object,
    observed: object,
    *,
    context: str,
) -> list[str]:
    errors: list[str] = []
    if isinstance(expected, dict):
        if not isinstance(observed, dict):
            return [f"{context}: must be an object matching the canonical contract"]
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
            return [f"{context}: must be a list matching the canonical contract"]
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
            f"{context}: does not match canonical contract; "
            f"expected={expected!r}, observed={observed!r}"
        )
    return errors


def verify_claim_scoped_mutation_plan_document(
    document: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify exact plan structure, digest, and fixed semantic reconstruction."""

    try:
        if not isinstance(document, dict):
            raise _error("claim-scoped mutation plan", "must be an object")
        actual_fields = set(document)
        if actual_fields != _PLAN_FIELDS:
            raise _error(
                "claim-scoped mutation plan",
                f"field mismatch; missing={sorted(_PLAN_FIELDS - actual_fields)}, "
                f"extra={sorted(actual_fields - _PLAN_FIELDS)}",
            )
        recorded = _sha256(
            document["plan_sha256"],
            context="claim-scoped mutation plan.plan_sha256",
        )
        computed = compute_mutation_plan_sha256(document)
        expected = build_claim_scoped_mutation_plan()
    except (
        DW001MutationPlanError,
        DeltaWitnessError,
        KeyError,
        TypeError,
        IndexError,
        ValueError,
        OverflowError,
        MemoryError,
        RecursionError,
    ) as exc:
        if isinstance(exc, DW001MutationPlanError):
            return False, (str(exc),)
        return False, (
            "claim-scoped mutation plan: verification failed closed: "
            f"{type(exc).__name__}: {exc}",
        )

    errors: list[str] = []
    if recorded != computed:
        errors.append(
            "claim-scoped mutation plan.plan_sha256: digest mismatch; "
            f"expected {recorded}, computed {computed}"
        )
    errors.extend(
        _differences(
            expected,
            document,
            context="claim-scoped mutation plan",
        )
    )
    unique = tuple(dict.fromkeys(errors))
    return not unique, unique


def _find_target(source: str) -> tuple[ast.Module, ast.Return, dict[str, object]]:
    try:
        tree = ast.parse(source, filename=_SOURCE_PATH, mode="exec")
    except (SyntaxError, MemoryError, RecursionError) as exc:
        raise _error("claim-scoped mutation source", "cannot be parsed") from exc
    functions = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == _SOURCE_SYMBOL
    ]
    if len(functions) != 1:
        raise _error(
            "claim-scoped mutation target.symbol",
            f"expected exactly one {_SOURCE_SYMBOL!r} definition, found {len(functions)}",
        )
    function = functions[0]
    returns = [node for node in function.body if isinstance(node, ast.Return)]
    if len(function.body) != 1 or len(returns) != 1 or returns[0].value is None:
        raise _error(
            "claim-scoped mutation target",
            "requires one function body statement containing one return expression",
        )
    return_node = returns[0]
    value = return_node.value
    target: dict[str, object] = {
        "target_cardinality": 1,
        "target_id": None,
        "path": _SOURCE_PATH,
        "symbol": _SOURCE_SYMBOL,
        "node_kind": "Return.value",
        "lineno": value.lineno,
        "col_offset": value.col_offset,
        "end_lineno": value.end_lineno,
        "end_col_offset": value.end_col_offset,
    }
    target_payload = {
        "schema_version": _TARGET_SCHEMA_VERSION,
        "source_sha256": _sha256_bytes(source.encode("utf-8")),
        **{key: item for key, item in target.items() if key != "target_id"},
    }
    target["target_id"] = sha256_document(target_payload)
    return tree, return_node, target


def _compile_valid(source: str) -> bool:
    try:
        compile(source, "<deltawitness-mutant>", "exec")
    except (SyntaxError, ValueError, TypeError, MemoryError, RecursionError):
        return False
    return True


def _mutated_source(operator_id: str) -> tuple[str, str | None, str | None, bool | None, str]:
    tree, return_node, _ = _find_target(_weak_proxy.CANDIDATE_CODE)

    if operator_id in {
        "return-constant-false-v1",
        "duplicate-false-control-v1",
    }:
        return_node.value = ast.Constant(value=False)
    elif operator_id == "return-constant-true-v1":
        return_node.value = ast.Constant(value=True)
    elif operator_id == "comparison-eq-to-ne-v1":
        if (
            not isinstance(return_node.value, ast.Compare)
            or len(return_node.value.ops) != 1
            or not isinstance(return_node.value.ops[0], ast.Eq)
        ):
            return "not_applicable", None, None, None, "target_not_found"
        return_node.value.ops = [ast.NotEq()]
    elif operator_id == "not-applicable-addition-control-v1":
        if not any(
            isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add)
            for node in ast.walk(return_node.value)
        ):
            return "not_applicable", None, None, None, "target_not_found"
        raise _error(
            "claim-scoped mutation generation control",
            "unexpected addition target appeared in the fixed source",
        )
    elif operator_id == "invalid-render-control-v1":
        invalid_source = "def is_admin(user):\n    return (\n"
        if _compile_valid(invalid_source):
            raise _error(
                "claim-scoped mutation generation control",
                "invalid-render control unexpectedly compiled",
            )
        return "invalid", invalid_source, None, False, "compile_error"
    else:
        raise _error(
            "claim-scoped mutation operator",
            f"unsupported operator {operator_id!r}",
        )

    ast.fix_missing_locations(tree)
    mutated_source = ast.unparse(tree) + "\n"
    if not _compile_valid(mutated_source):
        return "invalid", mutated_source, None, False, "compile_error"
    reparsed = ast.parse(
        mutated_source,
        filename=_SOURCE_PATH,
        mode="exec",
    )
    return (
        "generated",
        mutated_source,
        _ast_sha256_from_tree(reparsed),
        True,
        "generated",
    )


def _mutant_id(
    *,
    plan_sha256: str,
    operator_id: str,
    status: str,
    target_id: str,
    mutated_source_sha256: str | None,
    mutated_ast_sha256: str | None,
) -> str:
    return sha256_document(
        {
            "schema_version": _MUTANT_SCHEMA_VERSION,
            "plan_sha256": plan_sha256,
            "operator_id": operator_id,
            "status": status,
            "target_id": target_id,
            "mutated_source_sha256": mutated_source_sha256,
            "mutated_ast_sha256": mutated_ast_sha256,
        }
    )


def build_claim_scoped_mutant_catalog(
    plan: object,
) -> dict[str, Any]:
    """Generate the exact outcome-blind catalog for the verified fixed plan."""

    valid, errors = verify_claim_scoped_mutation_plan_document(plan)
    if not valid:
        raise _error(
            "claim-scoped mutant catalog plan",
            "; ".join(errors),
        )
    assert isinstance(plan, dict)
    source = _weak_proxy.CANDIDATE_CODE
    _, _, target = _find_target(source)
    target_id = str(target["target_id"])

    operator_records: list[tuple[str, str, str]] = [
        (
            "generic_operator",
            str(operator["operator_id"]),
            str(operator["operator_class"]),
        )
        for operator in plan["operator_set"]["operators"]
    ]
    operator_records.extend(
        (
            "generation_control",
            str(control["operator_id"]),
            str(control["control_purpose"]),
        )
        for control in plan["generation_controls"]
    )

    seen_source_digests: dict[str, str] = {}
    records: list[dict[str, object]] = []
    for order, (catalog_role, operator_id, operator_class) in enumerate(
        operator_records,
        start=1,
    ):
        (
            status,
            mutated_source,
            mutated_ast_sha256,
            compile_valid,
            diagnostic_code,
        ) = _mutated_source(operator_id)
        mutated_source_sha256 = (
            _sha256_bytes(mutated_source.encode("utf-8"))
            if mutated_source is not None
            else None
        )
        duplicate_of: str | None = None
        if (
            status == "generated"
            and mutated_source_sha256 is not None
            and mutated_source_sha256 in seen_source_digests
        ):
            status = "duplicate"
            duplicate_of = seen_source_digests[mutated_source_sha256]
            diagnostic_code = "duplicate_source"

        mutant_id = _mutant_id(
            plan_sha256=str(plan["plan_sha256"]),
            operator_id=operator_id,
            status=status,
            target_id=target_id,
            mutated_source_sha256=mutated_source_sha256,
            mutated_ast_sha256=mutated_ast_sha256,
        )
        if status == "generated" and mutated_source_sha256 is not None:
            seen_source_digests[mutated_source_sha256] = mutant_id

        records.append(
            {
                "order": order,
                "catalog_role": catalog_role,
                "operator_id": operator_id,
                "operator_class": operator_class,
                "target_id": target_id,
                "status": status,
                "mutant_id": mutant_id,
                "duplicate_of": duplicate_of,
                "mutated_source_sha256": mutated_source_sha256,
                "mutated_ast_sha256": mutated_ast_sha256,
                "compile_valid": compile_valid,
                "diagnostic_code": diagnostic_code,
                "source_body_published": False,
            }
        )

    catalog: dict[str, Any] = {
        "schema_version": CATALOG_SCHEMA_VERSION,
        "study_id": "DW-001",
        "plan_id": PLAN_ID,
        "plan_sha256": plan["plan_sha256"],
        "partition": "development",
        "source": {
            "source_id": plan["source_scope"]["source_id"],
            "source_sha256": plan["source_scope"]["source_sha256"],
            "ast_sha256": plan["source_scope"]["ast_sha256"],
            "path": plan["source_scope"]["path"],
            "symbol": plan["source_scope"]["symbol"],
            "source_body_published": False,
        },
        "target": target,
        "mutants": records,
        "known_challenge_control": deepcopy(plan["known_challenge_control"]),
        "summary": {
            "total_records": len(records),
            "generic_operator_records": sum(
                record["catalog_role"] == "generic_operator"
                for record in records
            ),
            "generation_control_records": sum(
                record["catalog_role"] == "generation_control"
                for record in records
            ),
            "generated": sum(record["status"] == "generated" for record in records),
            "duplicate": sum(record["status"] == "duplicate" for record in records),
            "invalid": sum(record["status"] == "invalid" for record in records),
            "not_applicable": sum(
                record["status"] == "not_applicable" for record in records
            ),
            "score": None,
        },
        "catalog_sha256": None,
    }
    catalog["catalog_sha256"] = compute_mutant_catalog_sha256(catalog)
    return catalog


def verify_claim_scoped_mutant_catalog_document(
    document: object,
    plan: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify exact catalog structure, digest, and deterministic regeneration."""

    plan_valid, plan_errors = verify_claim_scoped_mutation_plan_document(plan)
    if not plan_valid:
        return False, tuple(
            f"claim-scoped mutant catalog plan: {error}"
            for error in plan_errors
        )
    try:
        if not isinstance(document, dict):
            raise _error("claim-scoped mutant catalog", "must be an object")
        if not isinstance(plan, dict):
            raise _error("claim-scoped mutant catalog plan", "must be an object")
        actual_fields = set(document)
        if actual_fields != _CATALOG_FIELDS:
            raise _error(
                "claim-scoped mutant catalog",
                f"field mismatch; missing={sorted(_CATALOG_FIELDS - actual_fields)}, "
                f"extra={sorted(actual_fields - _CATALOG_FIELDS)}",
            )
        recorded = _sha256(
            document["catalog_sha256"],
            context="claim-scoped mutant catalog.catalog_sha256",
        )
        computed = compute_mutant_catalog_sha256(document)
        expected = build_claim_scoped_mutant_catalog(plan)
    except (
        DW001MutationPlanError,
        DeltaWitnessError,
        KeyError,
        TypeError,
        IndexError,
        ValueError,
        OverflowError,
        SyntaxError,
        MemoryError,
        RecursionError,
    ) as exc:
        if isinstance(exc, DW001MutationPlanError):
            return False, (str(exc),)
        return False, (
            "claim-scoped mutant catalog: verification failed closed: "
            f"{type(exc).__name__}: {exc}",
        )

    errors: list[str] = []
    if recorded != computed:
        errors.append(
            "claim-scoped mutant catalog.catalog_sha256: digest mismatch; "
            f"expected {recorded}, computed {computed}"
        )
    errors.extend(
        _differences(
            expected,
            document,
            context="claim-scoped mutant catalog",
        )
    )
    unique = tuple(dict.fromkeys(errors))
    return not unique, unique


__all__ = [
    "ADAPTER_ID",
    "CATALOG_SCHEMA_VERSION",
    "DW001MutationPlanError",
    "OPERATOR_SET_ID",
    "PLAN_ID",
    "PLAN_SCHEMA_VERSION",
    "build_claim_scoped_mutant_catalog",
    "build_claim_scoped_mutation_plan",
    "compute_mutant_catalog_sha256",
    "compute_mutation_plan_sha256",
    "verify_claim_scoped_mutant_catalog_document",
    "verify_claim_scoped_mutation_plan_document",
]
