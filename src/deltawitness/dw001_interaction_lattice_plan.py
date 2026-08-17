"""Pre-execution interaction-witness lattice plan for DW-001.

This module freezes one fixed project-owned two-condition authorization source,
four exact unittest selectors, five selector profiles, five claim-violating
mutation operators, three generation controls, expected structural signatures,
and a complete expected mutant/profile incidence table before the new source is
executed under Coverage.py or mutation testing.

It parses, transforms, unparses, reparses, and compiles fixed project-owned
bytes only. It does not run the source, tests, Coverage.py, or mutants. It
authorizes no external repository, holdout, score, threshold, merge blocker, or
method-superiority claim.
"""

from __future__ import annotations

import ast
from collections import Counter
from copy import deepcopy
import hashlib
import re
from typing import Any, Mapping, Sequence

from .errors import DeltaWitnessError
from .reporting import sha256_document


PLAN_SCHEMA_VERSION = (
    "deltawitness.dw001-interaction-witness-lattice-plan.v1"
)
CATALOG_SCHEMA_VERSION = (
    "deltawitness.dw001-interaction-witness-lattice-mutant-catalog.v1"
)
PLAN_ID = "DW-001-INTERACTION-WITNESS-LATTICE-PLAN-V1"
ADAPTER_ID = "python-stdlib-ast-interaction-lattice-v1"
OPERATOR_SET_ID = "two-condition-conjunction-faults-v1"

_SOURCE_ID = "two-condition-authorization-candidate-v1"
_SOURCE_PATH = "src/access.py"
_SOURCE_SYMBOL = "is_authorized"
_TEST_ID = "two-condition-authorization-selectors-v1"
_TEST_PATH = "tests/test_access.py"

_AST_SCHEMA_VERSION = "deltawitness.python-semantic-ast.v1"
_TARGET_SCHEMA_VERSION = (
    "deltawitness.dw001-interaction-witness-target.v1"
)
_SELECTOR_SCHEMA_VERSION = (
    "deltawitness.dw001-interaction-witness-selector.v1"
)
_MUTANT_SCHEMA_VERSION = (
    "deltawitness.dw001-interaction-witness-mutant.v1"
)
_PATH_SHAPE_SCHEMA_VERSION = (
    "deltawitness.dw001-interaction-path-shape.v1"
)
_PATH_MULTISET_SCHEMA_VERSION = (
    "deltawitness.dw001-interaction-path-multiset.v1"
)
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")

PR46_MERGE_COMMIT = "1e7f1c627d23bb54df0753ef7e3452a746c2f520"
PR46_COVERAGEPY_RESULT_SEMANTIC_SHA256 = (
    "ec0c2fdd5ac24ba53eb895d9014aab623d2631125b8512ba0e0cbf5105f21ee8"
)
PR46_COVERAGEPY_RESULT_REPORT_SHA256 = (
    "8b248757374ebff4195bad181ad02bc5b0bfc61fa2e21ebf45549686c33d2c41"
)
PR46_MUTATION_RESULT_SEMANTIC_SHA256 = (
    "9e101bca85fd630bf5bdb2a6030d9fdab93eb3eac54b03f4aab99012c28086b6"
)
PR46_STDLIB_STATEMENT_RESULT_SEMANTIC_SHA256 = (
    "353e887ccb43561f1a0749e7948dd40bd7019534e93b5dca5b11ea16d49f68c6"
)
PR46_COVERAGEPY_DISTRIBUTION_MANIFEST_SHA256 = (
    "28f6430e45fcfda973a1fcd57157e2317f096cc2774e8281244eaf18a9d0dd3f"
)

CANDIDATE_SOURCE = """def is_authorized(user):
    role_ok = user.get(\"role\") == \"admin\"
    mfa_ok = user.get(\"mfa\") is True
    if role_ok:
        role_gate = True
    else:
        role_gate = False
    if mfa_ok:
        mfa_gate = True
    else:
        mfa_gate = False
    return role_gate and mfa_gate
"""

SELECTOR_TEST_SOURCE = """import sys
import unittest

sys.path.insert(0, \"src\")
from access import is_authorized


class AccessTests(unittest.TestCase):
    def test_admin_with_mfa_is_allowed(self):
        self.assertTrue(
            is_authorized({\"role\": \"admin\", \"mfa\": True})
        )

    def test_admin_without_mfa_is_denied(self):
        self.assertFalse(
            is_authorized({\"role\": \"admin\", \"mfa\": False})
        )

    def test_viewer_with_mfa_is_denied(self):
        self.assertFalse(
            is_authorized({\"role\": \"viewer\", \"mfa\": True})
        )

    def test_viewer_without_mfa_is_denied(self):
        self.assertFalse(
            is_authorized({\"role\": \"viewer\", \"mfa\": False})
        )
"""

_TRUTH_TABLE: tuple[dict[str, object], ...] = (
    {
        "order": 1,
        "quadrant_id": "TT",
        "role_ok": True,
        "mfa_ok": True,
        "input": {"role": "admin", "mfa": True},
        "expected_decision": True,
        "selector": (
            "test_access.AccessTests.test_admin_with_mfa_is_allowed"
        ),
    },
    {
        "order": 2,
        "quadrant_id": "TF",
        "role_ok": True,
        "mfa_ok": False,
        "input": {"role": "admin", "mfa": False},
        "expected_decision": False,
        "selector": (
            "test_access.AccessTests.test_admin_without_mfa_is_denied"
        ),
    },
    {
        "order": 3,
        "quadrant_id": "FT",
        "role_ok": False,
        "mfa_ok": True,
        "input": {"role": "viewer", "mfa": True},
        "expected_decision": False,
        "selector": (
            "test_access.AccessTests.test_viewer_with_mfa_is_denied"
        ),
    },
    {
        "order": 4,
        "quadrant_id": "FF",
        "role_ok": False,
        "mfa_ok": False,
        "input": {"role": "viewer", "mfa": False},
        "expected_decision": False,
        "selector": (
            "test_access.AccessTests.test_viewer_without_mfa_is_denied"
        ),
    },
)

_QUADRANT_PATH_HYPOTHESES: tuple[dict[str, object], ...] = (
    {
        "quadrant_id": "TT",
        "expected_executed_statements": [2, 3, 4, 5, 8, 9, 12],
        "expected_missing_statements": [1, 7, 11],
        "expected_arcs": [
            [-1, 2], [2, 3], [3, 4], [4, 5],
            [5, 8], [8, 9], [9, 12], [12, -1],
        ],
    },
    {
        "quadrant_id": "TF",
        "expected_executed_statements": [2, 3, 4, 5, 8, 11, 12],
        "expected_missing_statements": [1, 7, 9],
        "expected_arcs": [
            [-1, 2], [2, 3], [3, 4], [4, 5],
            [5, 8], [8, 11], [11, 12], [12, -1],
        ],
    },
    {
        "quadrant_id": "FT",
        "expected_executed_statements": [2, 3, 4, 7, 8, 9, 12],
        "expected_missing_statements": [1, 5, 11],
        "expected_arcs": [
            [-1, 2], [2, 3], [3, 4], [4, 7],
            [7, 8], [8, 9], [9, 12], [12, -1],
        ],
    },
    {
        "quadrant_id": "FF",
        "expected_executed_statements": [2, 3, 4, 7, 8, 11, 12],
        "expected_missing_statements": [1, 5, 9],
        "expected_arcs": [
            [-1, 2], [2, 3], [3, 4], [4, 7],
            [7, 8], [8, 11], [11, 12], [12, -1],
        ],
    },
)

_PROFILE_DEFINITIONS: tuple[dict[str, object], ...] = (
    {
        "order": 1,
        "profile_id": "diagonal-only-v1",
        "profile_role": "diagonal_negative_control",
        "quadrants": ["TT", "FF"],
        "expected_mfa_independence_witness": False,
        "expected_role_independence_witness": False,
    },
    {
        "order": 2,
        "profile_id": "mfa-independence-v1",
        "profile_role": "single_condition_independence_control",
        "quadrants": ["TT", "TF", "FF"],
        "expected_mfa_independence_witness": True,
        "expected_role_independence_witness": False,
    },
    {
        "order": 3,
        "profile_id": "role-independence-v1",
        "profile_role": "single_condition_independence_control",
        "quadrants": ["TT", "FT", "FF"],
        "expected_mfa_independence_witness": False,
        "expected_role_independence_witness": True,
    },
    {
        "order": 4,
        "profile_id": "mcdc-basis-v1",
        "profile_role": "two_condition_independence_control",
        "quadrants": ["TT", "TF", "FT"],
        "expected_mfa_independence_witness": True,
        "expected_role_independence_witness": True,
    },
    {
        "order": 5,
        "profile_id": "full-truth-table-v1",
        "profile_role": "full_truth_table_control",
        "quadrants": ["TT", "TF", "FT", "FF"],
        "expected_mfa_independence_witness": True,
        "expected_role_independence_witness": True,
    },
)

_GENERIC_OPERATORS: tuple[dict[str, object], ...] = (
    {
        "order": 1,
        "operator_id": "drop-mfa-conjunct-v1",
        "operator_class": "boolean_operand_deletion",
        "target_kind": "two_operand_and",
        "retained_operand": "role_gate",
        "outcome_blind_selection": True,
    },
    {
        "order": 2,
        "operator_id": "drop-role-conjunct-v1",
        "operator_class": "boolean_operand_deletion",
        "target_kind": "two_operand_and",
        "retained_operand": "mfa_gate",
        "outcome_blind_selection": True,
    },
    {
        "order": 3,
        "operator_id": "or-gates-v1",
        "operator_class": "boolean_connector_replacement",
        "target_kind": "two_operand_and",
        "replacement_connector": "or",
        "outcome_blind_selection": True,
    },
    {
        "order": 4,
        "operator_id": "constant-false-v1",
        "operator_class": "boolean_constant_replacement",
        "target_kind": "return_expression",
        "replacement_value": False,
        "outcome_blind_selection": True,
    },
    {
        "order": 5,
        "operator_id": "constant-true-v1",
        "operator_class": "boolean_constant_replacement",
        "target_kind": "return_expression",
        "replacement_value": True,
        "outcome_blind_selection": True,
    },
)

_GENERATION_CONTROLS: tuple[dict[str, object], ...] = (
    {
        "order": 6,
        "operator_id": "duplicate-false-control-v1",
        "control_purpose": "duplicate_retention",
        "included_in_generic_operator_set": False,
    },
    {
        "order": 7,
        "operator_id": "not-applicable-addition-control-v1",
        "control_purpose": "not_applicable_retention",
        "included_in_generic_operator_set": False,
    },
    {
        "order": 8,
        "operator_id": "invalid-render-control-v1",
        "control_purpose": "invalid_retention",
        "included_in_generic_operator_set": False,
    },
)

_EXPECTED_MUTATION_MATRIX: tuple[dict[str, object], ...] = (
    {
        "operator_id": "drop-mfa-conjunct-v1",
        "profile_outcomes": [
            {"profile_id": "diagonal-only-v1", "expected_outcome": "survived"},
            {"profile_id": "mfa-independence-v1", "expected_outcome": "killed"},
            {"profile_id": "role-independence-v1", "expected_outcome": "survived"},
            {"profile_id": "mcdc-basis-v1", "expected_outcome": "killed"},
            {"profile_id": "full-truth-table-v1", "expected_outcome": "killed"},
        ],
    },
    {
        "operator_id": "drop-role-conjunct-v1",
        "profile_outcomes": [
            {"profile_id": "diagonal-only-v1", "expected_outcome": "survived"},
            {"profile_id": "mfa-independence-v1", "expected_outcome": "survived"},
            {"profile_id": "role-independence-v1", "expected_outcome": "killed"},
            {"profile_id": "mcdc-basis-v1", "expected_outcome": "killed"},
            {"profile_id": "full-truth-table-v1", "expected_outcome": "killed"},
        ],
    },
    {
        "operator_id": "or-gates-v1",
        "profile_outcomes": [
            {"profile_id": "diagonal-only-v1", "expected_outcome": "survived"},
            {"profile_id": "mfa-independence-v1", "expected_outcome": "killed"},
            {"profile_id": "role-independence-v1", "expected_outcome": "killed"},
            {"profile_id": "mcdc-basis-v1", "expected_outcome": "killed"},
            {"profile_id": "full-truth-table-v1", "expected_outcome": "killed"},
        ],
    },
    {
        "operator_id": "constant-false-v1",
        "profile_outcomes": [
            {"profile_id": profile_id, "expected_outcome": "killed"}
            for profile_id in (
                "diagonal-only-v1", "mfa-independence-v1",
                "role-independence-v1", "mcdc-basis-v1",
                "full-truth-table-v1",
            )
        ],
    },
    {
        "operator_id": "constant-true-v1",
        "profile_outcomes": [
            {"profile_id": profile_id, "expected_outcome": "killed"}
            for profile_id in (
                "diagonal-only-v1", "mfa-independence-v1",
                "role-independence-v1", "mcdc-basis-v1",
                "full-truth-table-v1",
            )
        ],
    },
)

_PLAN_FIELDS = {
    "schema_version", "study_id", "plan_id", "status", "partition",
    "prior_evidence", "adapter", "source_scope", "test_scope",
    "truth_table", "target_scope", "structural_hypotheses",
    "path_partition_contract", "profiles", "operator_set",
    "generation_controls", "future_execution_contract", "policy",
    "execution_authorized", "holdout_selected",
    "primary_denominator_eligible", "plan_sha256",
}
_CATALOG_FIELDS = {
    "schema_version", "study_id", "plan_id", "plan_sha256", "partition",
    "source", "test", "target", "mutants", "summary", "catalog_sha256",
}


class DW001InteractionLatticePlanError(DeltaWitnessError):
    """Raised when the frozen interaction-lattice design is inconsistent."""


def _error(context: str, message: str) -> DW001InteractionLatticePlanError:
    return DW001InteractionLatticePlanError(f"{context}: {message}")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256(value: object, *, context: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise _error(context, "must be 64 lowercase hexadecimal characters")
    return value


def _semantic_ast_value(value: object) -> object:
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
    return sha256_document({
        "schema_version": _AST_SCHEMA_VERSION,
        "tree": _semantic_ast_value(tree),
    })


def _ast_sha256(source: str) -> str:
    try:
        tree = ast.parse(source, filename=_SOURCE_PATH, mode="exec")
    except (SyntaxError, MemoryError, RecursionError) as exc:
        raise _error("interaction-lattice source", "cannot be parsed") from exc
    return _ast_sha256_from_tree(tree)


def _selector_id(*, test_sha256: str, quadrant: Mapping[str, object]) -> str:
    return sha256_document({
        "schema_version": _SELECTOR_SCHEMA_VERSION,
        "test_sha256": test_sha256,
        "quadrant_id": quadrant["quadrant_id"],
        "selector": quadrant["selector"],
        "input": quadrant["input"],
        "expected_decision": quadrant["expected_decision"],
    })


def _path_shape_sha256(
    statements: Sequence[int], arcs: Sequence[Sequence[int]],
) -> str:
    return sha256_document({
        "schema_version": _PATH_SHAPE_SCHEMA_VERSION,
        "statements": list(statements),
        "arcs": [list(arc) for arc in arcs],
    })


def build_anonymous_path_multiset(
    path_shape_sha256s: Sequence[str],
) -> dict[str, object]:
    """Build an order-independent multiset while preserving multiplicity."""

    for index, digest in enumerate(path_shape_sha256s):
        _sha256(digest, context=f"interaction path multiset[{index}]")
    counts = Counter(path_shape_sha256s)
    records = [
        {"path_shape_sha256": digest, "count": counts[digest]}
        for digest in sorted(counts)
    ]
    return {
        "multiplicity_semantics": "multiset",
        "records": records,
        "anonymous_path_multiset_sha256": sha256_document({
            "schema_version": _PATH_MULTISET_SCHEMA_VERSION,
            "records": records,
        }),
    }


def compute_interaction_lattice_plan_sha256(document: dict[str, Any]) -> str:
    if not isinstance(document, dict):
        raise _error("interaction-lattice plan", "must be an object")
    normalized = deepcopy(document)
    normalized["plan_sha256"] = None
    return sha256_document(normalized)


def compute_interaction_lattice_catalog_sha256(document: dict[str, Any]) -> str:
    if not isinstance(document, dict):
        raise _error("interaction-lattice catalog", "must be an object")
    normalized = deepcopy(document)
    normalized["catalog_sha256"] = None
    return sha256_document(normalized)


def _find_target(source: str) -> tuple[ast.Module, ast.Return, dict[str, object]]:
    try:
        tree = ast.parse(source, filename=_SOURCE_PATH, mode="exec")
    except (SyntaxError, MemoryError, RecursionError) as exc:
        raise _error("interaction-lattice source", "cannot be parsed") from exc
    functions = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == _SOURCE_SYMBOL
    ]
    if len(functions) != 1:
        raise _error(
            "interaction-lattice target.symbol",
            f"expected one {_SOURCE_SYMBOL!r}, found {len(functions)}",
        )
    function = functions[0]
    returns = [node for node in function.body if isinstance(node, ast.Return)]
    if len(returns) != 1 or function.body[-1] is not returns[0]:
        raise _error(
            "interaction-lattice target",
            "requires one final top-level return statement",
        )
    return_node = returns[0]
    value = return_node.value
    if (
        not isinstance(value, ast.BoolOp)
        or not isinstance(value.op, ast.And)
        or len(value.values) != 2
        or not all(isinstance(item, ast.Name) for item in value.values)
        or [item.id for item in value.values] != ["role_gate", "mfa_gate"]
    ):
        raise _error(
            "interaction-lattice target",
            "requires `role_gate and mfa_gate` as the final expression",
        )
    target: dict[str, object] = {
        "target_cardinality": 1,
        "target_id": None,
        "path": _SOURCE_PATH,
        "symbol": _SOURCE_SYMBOL,
        "node_kind": "Return.value/BoolOp.And",
        "lineno": value.lineno,
        "col_offset": value.col_offset,
        "end_lineno": value.end_lineno,
        "end_col_offset": value.end_col_offset,
        "operand_count": 2,
        "operand_identifiers": ["role_gate", "mfa_gate"],
        "coverage_target_lines": [2, 3, 4, 5, 7, 8, 9, 11, 12],
    }
    target["target_id"] = sha256_document({
        "schema_version": _TARGET_SCHEMA_VERSION,
        "source_sha256": _sha256_bytes(source.encode("utf-8")),
        **{key: item for key, item in target.items() if key != "target_id"},
    })
    return tree, return_node, target


def _quadrants() -> list[dict[str, object]]:
    test_sha256 = _sha256_bytes(SELECTOR_TEST_SOURCE.encode("utf-8"))
    return [
        {
            **deepcopy(quadrant),
            "selector_id": _selector_id(
                test_sha256=test_sha256, quadrant=quadrant,
            ),
        }
        for quadrant in _TRUTH_TABLE
    ]


def _path_hypotheses() -> list[dict[str, object]]:
    return [
        {
            **deepcopy(item),
            "expected_path_shape_sha256": _path_shape_sha256(
                item["expected_executed_statements"], item["expected_arcs"],
            ),
        }
        for item in _QUADRANT_PATH_HYPOTHESES
    ]


def _profiles(
    quadrants: Sequence[Mapping[str, object]],
    paths: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    quadrant_by_id = {str(item["quadrant_id"]): item for item in quadrants}
    path_by_id = {str(item["quadrant_id"]): item for item in paths}
    profiles: list[dict[str, object]] = []
    for definition in _PROFILE_DEFINITIONS:
        quadrant_ids = list(definition["quadrants"])
        selectors = [quadrant_by_id[item]["selector"] for item in quadrant_ids]
        selector_ids = [
            quadrant_by_id[item]["selector_id"] for item in quadrant_ids
        ]
        path_digests = [
            str(path_by_id[item]["expected_path_shape_sha256"])
            for item in quadrant_ids
        ]
        profiles.append({
            **deepcopy(definition),
            "selectors": selectors,
            "selector_ids": selector_ids,
            "expected_statement_union": [2, 3, 4, 5, 7, 8, 9, 11, 12],
            "expected_statement_intersection": [2, 3, 4, 8, 12],
            "expected_arc_union": [
                [-1, 2], [2, 3], [3, 4], [4, 5], [4, 7], [5, 8],
                [7, 8], [8, 9], [8, 11], [9, 12], [11, 12], [12, -1],
            ],
            "expected_arc_intersection": [
                [-1, 2], [2, 3], [3, 4], [12, -1],
            ],
            "expected_anonymous_path_multiset": (
                build_anonymous_path_multiset(path_digests)
            ),
            "primary_denominator_eligible": False,
        })
    return profiles


def build_interaction_witness_lattice_plan() -> dict[str, Any]:
    """Build the exact design-only preregistration."""

    source_sha256 = _sha256_bytes(CANDIDATE_SOURCE.encode("utf-8"))
    test_sha256 = _sha256_bytes(SELECTOR_TEST_SOURCE.encode("utf-8"))
    _, _, target = _find_target(CANDIDATE_SOURCE)
    quadrants = _quadrants()
    paths = _path_hypotheses()
    profiles = _profiles(quadrants, paths)
    plan: dict[str, Any] = {
        "schema_version": PLAN_SCHEMA_VERSION,
        "study_id": "DW-001",
        "plan_id": PLAN_ID,
        "status": "pre_execution_frozen_design",
        "partition": "development",
        "prior_evidence": {
            "merge_commit": PR46_MERGE_COMMIT,
            "coveragepy_result_path": (
                "research/DW-001/coveragepy-baseline-result.v1.json"
            ),
            "coveragepy_result_semantic_sha256": (
                PR46_COVERAGEPY_RESULT_SEMANTIC_SHA256
            ),
            "coveragepy_result_report_sha256": (
                PR46_COVERAGEPY_RESULT_REPORT_SHA256
            ),
            "mutation_result_semantic_sha256": (
                PR46_MUTATION_RESULT_SEMANTIC_SHA256
            ),
            "stdlib_statement_result_semantic_sha256": (
                PR46_STDLIB_STATEMENT_RESULT_SEMANTIC_SHA256
            ),
            "coveragepy_distribution_manifest_sha256": (
                PR46_COVERAGEPY_DISTRIBUTION_MANIFEST_SHA256
            ),
            "prior_source_reused": False,
            "prior_selectors_reused": False,
            "prior_result_modified": False,
        },
        "adapter": {
            "id": ADAPTER_ID,
            "version": "1",
            "parser": "stdlib-ast",
            "round_trip": "ast-unparse-v1",
            "future_coverage_adapter": "coveragepy-public-api-v1",
            "future_outcome_observer": "outcome-receipt-v1",
            "runtime_dependency": False,
        },
        "source_scope": {
            "source_id": _SOURCE_ID,
            "path": _SOURCE_PATH,
            "symbol": _SOURCE_SYMBOL,
            "language": "python",
            "source_sha256": source_sha256,
            "ast_sha256": _ast_sha256(CANDIDATE_SOURCE),
            "source_line_count": 12,
            "source_body_in_artifact": False,
        },
        "test_scope": {
            "test_id": _TEST_ID,
            "path": _TEST_PATH,
            "test_sha256": test_sha256,
            "selector_count": 4,
            "test_body_in_artifact": False,
        },
        "truth_table": quadrants,
        "target_scope": target,
        "structural_hypotheses": {
            "expected_executable_statements": [1, 2, 3, 4, 5, 7, 8, 9, 11, 12],
            "quadrant_paths": paths,
            "expected_branch_stats_per_selector": [
                {"line": 4, "total_exits": 2, "taken_exits": 1},
                {"line": 8, "total_exits": 2, "taken_exits": 1},
            ],
            "expected_missing_branch_count_per_selector": 2,
            "all_profile_statement_union_intersection_equal": True,
            "all_profile_arc_union_intersection_equal": True,
            "statement_union_intersection_discriminates_profiles": False,
            "arc_union_intersection_discriminates_profiles": False,
            "path_partition_discriminates_profiles": True,
        },
        "path_partition_contract": {
            "path_shape_schema_version": _PATH_SHAPE_SCHEMA_VERSION,
            "path_multiset_schema_version": _PATH_MULTISET_SCHEMA_VERSION,
            "primary_path_components": [
                "executed_statement_set", "executed_arc_set",
            ],
            "anonymous_path_key_excludes": [
                "selector", "selector_id", "quadrant_id", "context_id",
                "invocation_binding", "hit_count_magnitude",
            ],
            "selector_context_binding_retained_separately": True,
            "selector_input_order_semantic": False,
            "multiplicity_semantics": "multiset",
            "hit_count_magnitude_used": False,
        },
        "profiles": profiles,
        "operator_set": {
            "id": OPERATOR_SET_ID,
            "selection_status": "frozen_before_result_execution",
            "selection_basis": "two_condition_conjunction_fault_controls",
            "operators": deepcopy(list(_GENERIC_OPERATORS)),
        },
        "generation_controls": deepcopy(list(_GENERATION_CONTROLS)),
        "future_execution_contract": {
            "unique_candidate_selector_commands": 4,
            "unique_mutant_selector_commands": 20,
            "candidate_selector_expected_outcome": "pass",
            "profile_outcome_taxonomy": [
                "killed", "survived", "candidate_invalid", "indeterminate",
            ],
            "expected_mutation_matrix": deepcopy(list(_EXPECTED_MUTATION_MATRIX)),
            "retain_complete_selector_table": True,
            "retain_complete_mutant_table": True,
            "retain_expected_observed_concordance": True,
            "complete_divergence_status": "unexpected",
            "missing_or_ambiguous_status": "indeterminate",
            "missing_branch_arc_identity_status": "unavailable-public-api",
            "score": None,
            "universal_threshold": None,
            "merge_blocker_authorized": False,
            "execution_status": "not_implemented",
        },
        "policy": {
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
            "scientific_novelty_claim_allowed": False,
        },
        "execution_authorized": False,
        "holdout_selected": False,
        "primary_denominator_eligible": False,
        "plan_sha256": None,
    }
    plan["plan_sha256"] = compute_interaction_lattice_plan_sha256(plan)
    return plan


def _differences(expected: object, observed: object, *, context: str) -> list[str]:
    errors: list[str] = []
    if type(expected) is not type(observed):
        return [f"{context}: type mismatch"]
    if isinstance(expected, dict):
        assert isinstance(observed, dict)
        expected_keys, observed_keys = set(expected), set(observed)
        if expected_keys != observed_keys:
            errors.append(
                f"{context}: field mismatch; "
                f"missing={sorted(expected_keys - observed_keys)}, "
                f"extra={sorted(observed_keys - expected_keys)}"
            )
        for key in sorted(expected_keys & observed_keys):
            errors.extend(_differences(
                expected[key], observed[key], context=f"{context}.{key}",
            ))
        return errors
    if isinstance(expected, list):
        assert isinstance(observed, list)
        if len(expected) != len(observed):
            errors.append(
                f"{context}: length mismatch; expected {len(expected)}, "
                f"observed {len(observed)}"
            )
        for index, (left, right) in enumerate(zip(expected, observed, strict=False)):
            errors.extend(_differences(
                left, right, context=f"{context}[{index}]",
            ))
        return errors
    if expected != observed:
        errors.append(f"{context}: expected={expected!r}, observed={observed!r}")
    return errors


def verify_interaction_witness_lattice_plan_document(
    document: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify exact plan structure, digest, and semantic reconstruction."""

    try:
        if not isinstance(document, dict):
            raise _error("interaction-lattice plan", "must be an object")
        actual_fields = set(document)
        if actual_fields != _PLAN_FIELDS:
            raise _error(
                "interaction-lattice plan",
                f"field mismatch; missing={sorted(_PLAN_FIELDS - actual_fields)}, "
                f"extra={sorted(actual_fields - _PLAN_FIELDS)}",
            )
        recorded = _sha256(
            document["plan_sha256"],
            context="interaction-lattice plan.plan_sha256",
        )
        computed = compute_interaction_lattice_plan_sha256(document)
        expected = build_interaction_witness_lattice_plan()
    except (
        DW001InteractionLatticePlanError, DeltaWitnessError, KeyError,
        TypeError, IndexError, ValueError, OverflowError, MemoryError,
        RecursionError,
    ) as exc:
        if isinstance(exc, DW001InteractionLatticePlanError):
            return False, (str(exc),)
        return False, (
            "interaction-lattice plan: verification failed closed: "
            f"{type(exc).__name__}: {exc}",
        )
    errors: list[str] = []
    if recorded != computed:
        errors.append("interaction-lattice plan.plan_sha256: digest mismatch")
    errors.extend(_differences(
        expected, document, context="interaction-lattice plan",
    ))
    unique = tuple(dict.fromkeys(errors))
    return not unique, unique


def _compile_valid(source: str) -> bool:
    try:
        compile(source, "<deltawitness-interaction-mutant>", "exec")
    except (SyntaxError, ValueError, TypeError, MemoryError, RecursionError):
        return False
    return True


def _mutated_source(
    operator_id: str,
) -> tuple[str, str | None, str | None, bool | None, str]:
    tree, return_node, _ = _find_target(CANDIDATE_SOURCE)
    value = return_node.value
    assert isinstance(value, ast.BoolOp)

    if operator_id == "drop-mfa-conjunct-v1":
        return_node.value = deepcopy(value.values[0])
    elif operator_id == "drop-role-conjunct-v1":
        return_node.value = deepcopy(value.values[1])
    elif operator_id == "or-gates-v1":
        value.op = ast.Or()
    elif operator_id in {"constant-false-v1", "duplicate-false-control-v1"}:
        return_node.value = ast.Constant(value=False)
    elif operator_id == "constant-true-v1":
        return_node.value = ast.Constant(value=True)
    elif operator_id == "not-applicable-addition-control-v1":
        if not any(
            isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add)
            for node in ast.walk(value)
        ):
            return "not_applicable", None, None, None, "target_not_found"
        raise _error(
            "interaction-lattice generation control",
            "unexpected addition target appeared",
        )
    elif operator_id == "invalid-render-control-v1":
        invalid_source = "def is_authorized(user):\n    return (\n"
        if _compile_valid(invalid_source):
            raise _error(
                "interaction-lattice generation control",
                "invalid-render control unexpectedly compiled",
            )
        return "invalid", invalid_source, None, False, "compile_error"
    else:
        raise _error(
            "interaction-lattice operator",
            f"unsupported operator {operator_id!r}",
        )

    ast.fix_missing_locations(tree)
    mutated_source = ast.unparse(tree) + "\n"
    if not _compile_valid(mutated_source):
        return "invalid", mutated_source, None, False, "compile_error"
    reparsed = ast.parse(mutated_source, filename=_SOURCE_PATH, mode="exec")
    return (
        "generated", mutated_source, _ast_sha256_from_tree(reparsed),
        True, "generated",
    )


def _mutant_id(
    *, plan_sha256: str, operator_id: str, status: str,
    target_id: str, mutated_source_sha256: str | None,
    mutated_ast_sha256: str | None,
) -> str:
    return sha256_document({
        "schema_version": _MUTANT_SCHEMA_VERSION,
        "plan_sha256": plan_sha256,
        "operator_id": operator_id,
        "status": status,
        "target_id": target_id,
        "mutated_source_sha256": mutated_source_sha256,
        "mutated_ast_sha256": mutated_ast_sha256,
    })


def build_interaction_witness_lattice_mutant_catalog(
    plan: object,
) -> dict[str, Any]:
    """Generate identities only; do not execute mutants or tests."""

    valid, errors = verify_interaction_witness_lattice_plan_document(plan)
    if not valid:
        raise _error("interaction-lattice catalog plan", "; ".join(errors))
    assert isinstance(plan, dict)
    _, _, target = _find_target(CANDIDATE_SOURCE)
    target_id = str(target["target_id"])

    operator_records: list[tuple[str, str, str]] = [
        (
            "generic_operator", str(operator["operator_id"]),
            str(operator["operator_class"]),
        )
        for operator in plan["operator_set"]["operators"]
    ]
    operator_records.extend(
        (
            "generation_control", str(control["operator_id"]),
            str(control["control_purpose"]),
        )
        for control in plan["generation_controls"]
    )

    seen_source_digests: dict[str, str] = {}
    records: list[dict[str, object]] = []
    for order, (role, operator_id, operator_class) in enumerate(
        operator_records, start=1,
    ):
        status, mutated_source, mutated_ast_sha256, compile_valid, diagnostic = (
            _mutated_source(operator_id)
        )
        mutated_source_sha256 = (
            _sha256_bytes(mutated_source.encode("utf-8"))
            if mutated_source is not None else None
        )
        duplicate_of: str | None = None
        if (
            status == "generated"
            and mutated_source_sha256 is not None
            and mutated_source_sha256 in seen_source_digests
        ):
            status = "duplicate"
            duplicate_of = seen_source_digests[mutated_source_sha256]
            diagnostic = "duplicate_source"
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
        records.append({
            "order": order,
            "catalog_role": role,
            "operator_id": operator_id,
            "operator_class": operator_class,
            "target_id": target_id,
            "status": status,
            "mutant_id": mutant_id,
            "duplicate_of": duplicate_of,
            "mutated_source_sha256": mutated_source_sha256,
            "mutated_ast_sha256": mutated_ast_sha256,
            "compile_valid": compile_valid,
            "diagnostic_code": diagnostic,
            "source_body_in_artifact": False,
        })

    catalog: dict[str, Any] = {
        "schema_version": CATALOG_SCHEMA_VERSION,
        "study_id": "DW-001",
        "plan_id": PLAN_ID,
        "plan_sha256": plan["plan_sha256"],
        "partition": "development",
        "source": {
            "source_id": plan["source_scope"]["source_id"],
            "path": plan["source_scope"]["path"],
            "symbol": plan["source_scope"]["symbol"],
            "source_sha256": plan["source_scope"]["source_sha256"],
            "ast_sha256": plan["source_scope"]["ast_sha256"],
            "source_body_in_artifact": False,
        },
        "test": {
            "test_id": plan["test_scope"]["test_id"],
            "path": plan["test_scope"]["path"],
            "test_sha256": plan["test_scope"]["test_sha256"],
            "test_body_in_artifact": False,
        },
        "target": target,
        "mutants": records,
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
    catalog["catalog_sha256"] = compute_interaction_lattice_catalog_sha256(catalog)
    return catalog


def verify_interaction_witness_lattice_mutant_catalog_document(
    document: object, plan: object,
) -> tuple[bool, tuple[str, ...]]:
    plan_valid, plan_errors = verify_interaction_witness_lattice_plan_document(plan)
    if not plan_valid:
        return False, tuple(
            f"interaction-lattice catalog plan: {error}" for error in plan_errors
        )
    try:
        if not isinstance(document, dict):
            raise _error("interaction-lattice catalog", "must be an object")
        if not isinstance(plan, dict):
            raise _error("interaction-lattice catalog plan", "must be an object")
        actual_fields = set(document)
        if actual_fields != _CATALOG_FIELDS:
            raise _error(
                "interaction-lattice catalog",
                f"field mismatch; missing={sorted(_CATALOG_FIELDS - actual_fields)}, "
                f"extra={sorted(actual_fields - _CATALOG_FIELDS)}",
            )
        recorded = _sha256(
            document["catalog_sha256"],
            context="interaction-lattice catalog.catalog_sha256",
        )
        computed = compute_interaction_lattice_catalog_sha256(document)
        expected = build_interaction_witness_lattice_mutant_catalog(plan)
    except (
        DW001InteractionLatticePlanError, DeltaWitnessError, KeyError,
        TypeError, IndexError, ValueError, OverflowError, MemoryError,
        RecursionError,
    ) as exc:
        if isinstance(exc, DW001InteractionLatticePlanError):
            return False, (str(exc),)
        return False, (
            "interaction-lattice catalog: verification failed closed: "
            f"{type(exc).__name__}: {exc}",
        )
    errors: list[str] = []
    if recorded != computed:
        errors.append("interaction-lattice catalog.catalog_sha256: digest mismatch")
    errors.extend(_differences(
        expected, document, context="interaction-lattice catalog",
    ))
    unique = tuple(dict.fromkeys(errors))
    return not unique, unique


__all__ = [
    "ADAPTER_ID",
    "CATALOG_SCHEMA_VERSION",
    "CANDIDATE_SOURCE",
    "DW001InteractionLatticePlanError",
    "OPERATOR_SET_ID",
    "PLAN_ID",
    "PLAN_SCHEMA_VERSION",
    "SELECTOR_TEST_SOURCE",
    "build_anonymous_path_multiset",
    "build_interaction_witness_lattice_mutant_catalog",
    "build_interaction_witness_lattice_plan",
    "compute_interaction_lattice_catalog_sha256",
    "compute_interaction_lattice_plan_sha256",
    "verify_interaction_witness_lattice_mutant_catalog_document",
    "verify_interaction_witness_lattice_plan_document",
]
