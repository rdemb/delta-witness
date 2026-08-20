"""Deterministic pre-execution claim-relevant path preregistration.

This module freezes one exact project-owned 2×2 route control, eight claim
selectors, eight separately labeled collateral-reference selectors, one bounded
assertion-influence graph, four executable fault/neutral controls, four
explicit generation controls, and a complete expected selector matrix before
any authorized result execution.

It parses and compiles fixed project-owned bytes to derive identities.  It does
not execute the candidate, tests, Coverage.py, implementations, or influence
observations.  It authorizes no external repository, holdout, score, threshold,
merge blocker, release, deployment, superiority, production, or novelty claim.
"""

from __future__ import annotations

import ast
import hashlib
import re
import stat
from copy import deepcopy
from pathlib import Path
from typing import Any

from .errors import DeltaWitnessError
from .reporting import load_report, sha256_document

MAIN_COMMIT = "3a363c3bdaa6e8fbbd0d6ab33f2417d76a50a5e9"
INTERACTION_SEMANTIC_SHA256 = (
    "bc2ab879595da61815a17dcc33a09c6334b93dea3fd464f2fe4a5437944ebb77"
)
INTERACTION_CHECKPOINT_SHA256 = (
    "40cf297679c83809368e53f35796d817761c25746302530f29fa4dda603277fc"
)
COVERAGEPY_MANIFEST_SHA256 = (
    "28f6430e45fcfda973a1fcd57157e2317f096cc2774e8281244eaf18a9d0dd3f"
)
PLAN_SCHEMA = "deltawitness.dw001-claim-relevant-path-divergence-plan.v1"
CATALOG_SCHEMA = "deltawitness.dw001-claim-relevant-path-divergence-catalog.v1"
PRIOR_ART_SCHEMA = "deltawitness.dw001-claim-relevant-path-prior-art-log.v1"
PLAN_ID = "DW-001-CLAIM-RELEVANT-PATH-DIVERGENCE-PLAN-V1"
PLAN_SCHEMA_VERSION = PLAN_SCHEMA
CATALOG_SCHEMA_VERSION = CATALOG_SCHEMA
PRIOR_ART_SCHEMA_VERSION = PRIOR_ART_SCHEMA
SOURCE_ID = "claim-relevant-path-authorization-candidate-v1"
TEST_ID = "claim-relevant-path-selectors-v1"
SOURCE_PATH = "src/access.py"
TEST_PATH = "tests/test_access.py"

SOURCE = '''def authorize(user, *, decision_route, collateral_route):
    role_value = user.get("role")
    mfa_ok = user.get("mfa") is True
    if decision_route == "direct":
        role_ok = role_value == "admin"
    else:
        normalized_role = str(role_value).strip().lower()
        role_ok = normalized_role == "admin"
    if collateral_route == "compact":
        trace_code = "compact"
    else:
        trace_label = f"role={role_value}"
        trace_code = "verbose:" + trace_label
    allowed = role_ok and mfa_ok
    if allowed:
        reason_code = "ALLOW"
    else:
        reason_code = "DENY"
    return {
        "allowed": allowed,
        "reason_code": reason_code,
        "trace_code": trace_code,
    }
'''

TESTS = '''import sys
import unittest

sys.path.insert(0, "src")
from access import authorize


class AccessTests(unittest.TestCase):
    def _assert_claim(self, role, decision_route, collateral_route, expected):
        result = authorize(
            {"role": role, "mfa": True},
            decision_route=decision_route,
            collateral_route=collateral_route,
        )
        self.assertIs(result["allowed"], expected)
        self.assertEqual(
            result["reason_code"],
            "ALLOW" if expected else "DENY",
        )

    def test_admin_direct_compact(self):
        self._assert_claim("admin", "direct", "compact", True)

    def test_admin_direct_verbose(self):
        self._assert_claim("admin", "direct", "verbose", True)

    def test_admin_normalized_compact(self):
        self._assert_claim("admin", "normalized", "compact", True)

    def test_admin_normalized_verbose(self):
        self._assert_claim("admin", "normalized", "verbose", True)

    def test_viewer_direct_compact(self):
        self._assert_claim("viewer", "direct", "compact", False)

    def test_viewer_direct_verbose(self):
        self._assert_claim("viewer", "direct", "verbose", False)

    def test_viewer_normalized_compact(self):
        self._assert_claim("viewer", "normalized", "compact", False)

    def test_viewer_normalized_verbose(self):
        self._assert_claim("viewer", "normalized", "verbose", False)


class CollateralReferenceTests(unittest.TestCase):
    def _assert_trace(self, role, decision_route, collateral_route, expected):
        result = authorize(
            {"role": role, "mfa": True},
            decision_route=decision_route,
            collateral_route=collateral_route,
        )
        self.assertEqual(result["trace_code"], expected)

    def test_admin_direct_compact_trace(self):
        self._assert_trace("admin", "direct", "compact", "compact")

    def test_admin_direct_verbose_trace(self):
        self._assert_trace("admin", "direct", "verbose", "verbose:role=admin")

    def test_admin_normalized_compact_trace(self):
        self._assert_trace("admin", "normalized", "compact", "compact")

    def test_admin_normalized_verbose_trace(self):
        self._assert_trace(
            "admin", "normalized", "verbose", "verbose:role=admin"
        )

    def test_viewer_direct_compact_trace(self):
        self._assert_trace("viewer", "direct", "compact", "compact")

    def test_viewer_direct_verbose_trace(self):
        self._assert_trace("viewer", "direct", "verbose", "verbose:role=viewer")

    def test_viewer_normalized_compact_trace(self):
        self._assert_trace("viewer", "normalized", "compact", "compact")

    def test_viewer_normalized_verbose_trace(self):
        self._assert_trace(
            "viewer", "normalized", "verbose", "verbose:role=viewer"
        )
'''


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def semantic_ast_value(value: object) -> object:
    if isinstance(value, ast.AST):
        fields: dict[str, object] = {}
        for field in value._fields:
            child = getattr(value, field, None)
            if child is None or child == []:
                continue
            fields[field] = semantic_ast_value(child)
        return {"node": type(value).__name__, "fields": fields}
    if isinstance(value, list):
        return [semantic_ast_value(item) for item in value]
    return value


def ast_sha256(source: str) -> str:
    tree = ast.parse(source, filename=SOURCE_PATH, mode="exec")
    return sha256_document(
        {
            "schema_version": "deltawitness.python-semantic-ast.v1",
            "tree": semantic_ast_value(tree),
        }
    )


def replace_once(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise ValueError(f"replacement cardinality for {old!r}: {source.count(old)}")
    changed = source.replace(old, new, 1)
    compile(changed, SOURCE_PATH, "exec")
    return changed


def path_shape(
    *, decision_route: str, collateral_route: str, allowed: bool
) -> dict[str, object]:
    statements = [2, 3, 4]
    arcs = [[-1, 2], [2, 3], [3, 4]]
    if decision_route == "direct":
        statements += [5]
        arcs += [[4, 5], [5, 9]]
    else:
        statements += [7, 8]
        arcs += [[4, 7], [7, 8], [8, 9]]
    statements += [9]
    if collateral_route == "compact":
        statements += [10]
        arcs += [[9, 10], [10, 14]]
    else:
        statements += [12, 13]
        arcs += [[9, 12], [12, 13], [13, 14]]
    statements += [14, 15]
    arcs += [[14, 15]]
    if allowed:
        statements += [16, 19]
        arcs += [[15, 16], [16, 19], [19, -1]]
    else:
        statements += [18, 19]
        arcs += [[15, 18], [18, 19], [19, -1]]
    payload = {
        "schema_version": "deltawitness.dw001-claim-path-shape.v1",
        "statements": statements,
        "arcs": arcs,
    }
    return {
        "executed_statements": statements,
        "executed_arcs": arcs,
        "path_shape_sha256": sha256_document(payload),
    }


CELL_DEFINITIONS: list[dict[str, object]] = []
order = 0
for input_class, role, expected_allowed in (
    ("allowed", "admin", True),
    ("denied", "viewer", False),
):
    for decision_route, decision_code in (
        ("direct", "D"),
        ("normalized", "N"),
    ):
        for collateral_route, collateral_code in (
            ("compact", "C"),
            ("verbose", "V"),
        ):
            order += 1
            cell_id = f"{input_class[0].upper()}{decision_code}{collateral_code}"
            expected_trace = (
                "compact"
                if collateral_route == "compact"
                else f"verbose:role={role}"
            )
            CELL_DEFINITIONS.append(
                {
                    "order": order,
                    "cell_id": cell_id,
                    "input_class": input_class,
                    "role": role,
                    "mfa": True,
                    "decision_route": decision_route,
                    "collateral_route": collateral_route,
                    "expected_allowed": expected_allowed,
                    "expected_reason_code": (
                        "ALLOW" if expected_allowed else "DENY"
                    ),
                    "expected_trace_code": expected_trace,
                    "claim_selector": (
                        f"test_access.AccessTests.test_{role}_"
                        f"{decision_route}_{collateral_route}"
                    ),
                    "collateral_reference_selector": (
                        "test_access.CollateralReferenceTests.test_"
                        f"{role}_{decision_route}_{collateral_route}_trace"
                    ),
                }
            )

SOURCE_SHA256 = sha256_bytes(SOURCE.encode("utf-8"))
SOURCE_AST_SHA256 = ast_sha256(SOURCE)
TEST_SHA256 = sha256_bytes(TESTS.encode("utf-8"))

CELLS: list[dict[str, object]] = []
for definition in CELL_DEFINITIONS:
    cell = deepcopy(definition)
    identity_input = {
        "role": cell["role"],
        "mfa": cell["mfa"],
        "decision_route": cell["decision_route"],
        "collateral_route": cell["collateral_route"],
    }
    cell["claim_selector_id"] = sha256_document(
        {
            "schema_version": "deltawitness.dw001-claim-path-selector.v1",
            "selector_role": "claim",
            "test_sha256": TEST_SHA256,
            "cell_id": cell["cell_id"],
            "selector": cell["claim_selector"],
            "input": identity_input,
            "expected_allowed": cell["expected_allowed"],
            "expected_reason_code": cell["expected_reason_code"],
        }
    )
    cell["collateral_reference_selector_id"] = sha256_document(
        {
            "schema_version": "deltawitness.dw001-claim-path-selector.v1",
            "selector_role": "collateral_reference",
            "test_sha256": TEST_SHA256,
            "cell_id": cell["cell_id"],
            "selector": cell["collateral_reference_selector"],
            "input": identity_input,
            "expected_trace_code": cell["expected_trace_code"],
        }
    )
    cell["expected_candidate_path"] = path_shape(
        decision_route=str(cell["decision_route"]),
        collateral_route=str(cell["collateral_route"]),
        allowed=bool(cell["expected_allowed"]),
    )
    CELLS.append(cell)

PROFILES: list[dict[str, object]] = []
for profile_order, (profile_id, axis, value) in enumerate(
    (
        ("decision-direct-v1", "decision_route", "direct"),
        ("decision-normalized-v1", "decision_route", "normalized"),
        ("collateral-compact-v1", "collateral_route", "compact"),
        ("collateral-verbose-v1", "collateral_route", "verbose"),
        ("claim-allowed-v1", "input_class", "allowed"),
        ("claim-denied-v1", "input_class", "denied"),
    ),
    start=1,
):
    members = [cell for cell in CELLS if cell[axis] == value]
    PROFILES.append(
        {
            "order": profile_order,
            "profile_id": profile_id,
            "profile_axis": axis,
            "profile_value": value,
            "cell_ids": [cell["cell_id"] for cell in members],
            "claim_selector_ids": [
                cell["claim_selector_id"] for cell in members
            ],
            "collateral_reference_selector_ids": [
                cell["collateral_reference_selector_id"] for cell in members
            ],
            "primary_denominator_eligible": False,
        }
    )

INFLUENCE_CONTROL: dict[str, Any] = {
    "schema_version": "deltawitness.dw001-claim-path-influence-control.v1",
    "criterion_fields": ["allowed", "reason_code"],
    "collateral_reference_fields": ["trace_code"],
    "nodes": [
        "user.role",
        "user.mfa",
        "decision_route",
        "collateral_route",
        "role_value",
        "mfa_ok",
        "normalized_role",
        "role_ok",
        "trace_label",
        "trace_code",
        "allowed",
        "reason_code",
    ],
    "edges": [
        ["user.role", "role_value"],
        ["user.mfa", "mfa_ok"],
        ["decision_route", "role_ok"],
        ["role_value", "role_ok"],
        ["role_value", "normalized_role"],
        ["normalized_role", "role_ok"],
        ["collateral_route", "trace_code"],
        ["role_value", "trace_label"],
        ["trace_label", "trace_code"],
        ["role_ok", "allowed"],
        ["mfa_ok", "allowed"],
        ["allowed", "reason_code"],
    ],
    "expected_claim_influencing_nodes": [
        "user.role",
        "user.mfa",
        "decision_route",
        "role_value",
        "mfa_ok",
        "normalized_role",
        "role_ok",
        "allowed",
        "reason_code",
    ],
    "expected_collateral_only_nodes": [
        "collateral_route",
        "trace_label",
        "trace_code",
    ],
    "general_dynamic_slicing_claim_allowed": False,
    "checked_coverage_claim_allowed": False,
    "control_sha256": None,
}
INFLUENCE_CONTROL["control_sha256"] = sha256_document(INFLUENCE_CONTROL)

VARIANT_DEFINITIONS = [
    {
        "order": 1,
        "implementation_id": "direct-role-inversion-v1",
        "role": "claim_relevant_route_fault",
        "old": '        role_ok = role_value == "admin"\n',
        "new": '        role_ok = role_value != "admin"\n',
        "status": "generated",
    },
    {
        "order": 2,
        "implementation_id": "verbose-via-compact-collateral-diversion-v1",
        "role": "collateral_route_fault",
        "old": '    if collateral_route == "compact":\n',
        "new": '    if collateral_route in {"compact", "verbose"}:\n',
        "status": "generated",
    },
    {
        "order": 3,
        "implementation_id": "shared-or-gates-v1",
        "role": "shared_claim_fault",
        "old": "    allowed = role_ok and mfa_ok\n",
        "new": "    allowed = role_ok or mfa_ok\n",
        "status": "generated",
    },
    {
        "order": 4,
        "implementation_id": "direct-via-normalized-neutral-diversion-v1",
        "role": "neutral_path_diversion",
        "old": '    if decision_route == "direct":\n',
        "new": '    if decision_route == "unreachable-direct":\n',
        "status": "generated_behavior_preserving_control",
    },
    {
        "order": 5,
        "implementation_id": "duplicate-shared-or-control-v1",
        "role": "duplicate_control",
        "old": "    allowed = role_ok and mfa_ok\n",
        "new": "    allowed = role_ok or mfa_ok\n",
        "status": "duplicate",
    },
]


def expected_row(implementation_id: str, cell: dict[str, object]) -> dict[str, object]:
    role = str(cell["role"])
    decision_route = str(cell["decision_route"])
    collateral_route = str(cell["collateral_route"])
    expected_allowed = bool(cell["expected_allowed"])
    actual_allowed = expected_allowed
    actual_trace = str(cell["expected_trace_code"])
    measured_decision_route = decision_route
    measured_collateral_route = collateral_route

    if implementation_id == "direct-role-inversion-v1" and decision_route == "direct":
        actual_allowed = not expected_allowed
    elif (
        implementation_id
        == "verbose-via-compact-collateral-diversion-v1"
        and collateral_route == "verbose"
    ):
        actual_trace = "compact"
        measured_collateral_route = "compact"
    elif implementation_id == "shared-or-gates-v1":
        actual_allowed = True  # every frozen input has mfa=True
    elif (
        implementation_id == "direct-via-normalized-neutral-diversion-v1"
        and decision_route == "direct"
    ):
        measured_decision_route = "normalized"

    actual_reason = "ALLOW" if actual_allowed else "DENY"
    claim_pass = (
        actual_allowed == expected_allowed
        and actual_reason == cell["expected_reason_code"]
    )
    collateral_reference_pass = actual_trace == cell["expected_trace_code"]
    measured_path = path_shape(
        decision_route=measured_decision_route,
        collateral_route=measured_collateral_route,
        allowed=actual_allowed,
    )
    candidate_path_sha = cell["expected_candidate_path"]["path_shape_sha256"]
    return {
        "cell_id": cell["cell_id"],
        "expected_claim_observed": "pass" if claim_pass else "fail",
        "expected_collateral_reference_observed": (
            "pass" if collateral_reference_pass else "fail"
        ),
        "expected_allowed": actual_allowed,
        "expected_reason_code": actual_reason,
        "expected_trace_code": actual_trace,
        "expected_measured_decision_route": measured_decision_route,
        "expected_measured_collateral_route": measured_collateral_route,
        "expected_path_shape_sha256": measured_path["path_shape_sha256"],
        "expected_candidate_path_conformant": (
            measured_path["path_shape_sha256"] == candidate_path_sha
        ),
    }

EXECUTION_MATRIX = [
    {
        "order": index,
        "implementation_id": definition["implementation_id"],
        "role": definition["role"],
        "selector_outcomes": [
            expected_row(str(definition["implementation_id"]), cell)
            for cell in CELLS
        ],
    }
    for index, definition in enumerate(VARIANT_DEFINITIONS[:4], start=1)
]

PLAN: dict[str, Any] = {
    "schema_version": PLAN_SCHEMA,
    "study_id": "DW-001",
    "plan_id": PLAN_ID,
    "status": "pre_execution_frozen_design",
    "partition": "development",
    "prior_evidence": {
        "main_commit": MAIN_COMMIT,
        "interaction_result_semantic_sha256": INTERACTION_SEMANTIC_SHA256,
        "interaction_checkpoint_sha256": INTERACTION_CHECKPOINT_SHA256,
        "coveragepy_distribution_manifest_sha256": COVERAGEPY_MANIFEST_SHA256,
        "prior_result_modified": False,
    },
    "adapter": {
        "id": "python-fixed-source-claim-path-v1",
        "version": "1",
        "parser": "stdlib-ast",
        "round_trip": "exact-text-substitution-v1",
        "future_coverage_adapter": "coveragepy-public-api-v1",
        "future_outcome_observer": "outcome-receipt-v1",
        "runtime_dependency": False,
    },
    "source_scope": {
        "source_id": SOURCE_ID,
        "path": SOURCE_PATH,
        "symbol": "authorize",
        "source_sha256": SOURCE_SHA256,
        "ast_sha256": SOURCE_AST_SHA256,
        "source_line_count": 23,
        "source_body_in_artifact": False,
    },
    "test_scope": {
        "test_id": TEST_ID,
        "path": TEST_PATH,
        "test_sha256": TEST_SHA256,
        "claim_selector_count": 8,
        "collateral_reference_selector_count": 8,
        "total_selector_count": 16,
        "test_body_in_artifact": False,
    },
    "behavioral_contract": {
        "claim_output_fields": ["allowed", "reason_code"],
        "collateral_reference_fields": ["trace_code"],
        "claim_selectors_read_collateral_fields": False,
        "collateral_reference_selectors_satisfy_claim": False,
        "candidate_decision_routes_behaviorally_equivalent": True,
        "candidate_collateral_routes_claim_output_neutral": True,
    },
    "targets": [
        {
            "order": 1,
            "target_id": sha256_document(
                {
                    "schema_version": "deltawitness.dw001-claim-path-target.v1",
                    "source_sha256": SOURCE_SHA256,
                    "target_role": "claim_decision",
                    "path": SOURCE_PATH,
                    "symbol": "authorize",
                    "lines": [4, 5, 7, 8, 14, 15, 16, 18],
                }
            ),
            "target_role": "claim_decision",
            "path": SOURCE_PATH,
            "symbol": "authorize",
            "lines": [4, 5, 7, 8, 14, 15, 16, 18],
        },
        {
            "order": 2,
            "target_id": sha256_document(
                {
                    "schema_version": "deltawitness.dw001-claim-path-target.v1",
                    "source_sha256": SOURCE_SHA256,
                    "target_role": "collateral_trace",
                    "path": SOURCE_PATH,
                    "symbol": "authorize",
                    "lines": [9, 10, 12, 13],
                }
            ),
            "target_role": "collateral_trace",
            "path": SOURCE_PATH,
            "symbol": "authorize",
            "lines": [9, 10, 12, 13],
        },
    ],
    "cells": deepcopy(CELLS),
    "profiles": deepcopy(PROFILES),
    "influence_control": deepcopy(INFLUENCE_CONTROL),
    "operator_set": {
        "id": "claim-and-collateral-route-controls-v1",
        "selection_status": "frozen_before_result_execution",
        "operators": [
            {
                key: value
                for key, value in definition.items()
                if key not in {"old", "new"}
            }
            for definition in VARIANT_DEFINITIONS[:4]
        ],
    },
    "expected_execution_matrix": deepcopy(EXECUTION_MATRIX),
    "expected_relations": {
        "raw_paths_distinguish_decision_routes": True,
        "raw_paths_distinguish_collateral_routes": True,
        "candidate_claim_outputs_distinguish_decision_routes": False,
        "candidate_claim_outputs_distinguish_collateral_routes": False,
        "decision_route_is_claim_influencing": True,
        "collateral_route_is_claim_influencing": False,
        "collateral_fault_survives_claim_selectors": True,
        "collateral_fault_fails_collateral_references": True,
        "neutral_diversion_preserves_all_declared_outputs": True,
        "reject_all_path_divergence_overrefuses_valid_control": True,
    },
    "future_execution_contract": {
        "execution_status": "not_implemented",
        "candidate_claim_selector_commands": 8,
        "candidate_collateral_reference_commands": 8,
        "generated_implementation_claim_selector_commands": 32,
        "generated_implementation_collateral_reference_commands": 32,
        "maximum_selector_commands": 80,
        "complete_divergence_status": "unexpected",
        "missing_or_ambiguous_status": "indeterminate",
        "claim_outcome_taxonomy": ["pass", "fail", "error", "timeout"],
        "path_conformance_taxonomy": [
            "conformant",
            "divergent",
            "indeterminate",
        ],
        "score": None,
        "universal_threshold": None,
        "merge_blocker_authorized": False,
    },
    "policy": {
        "quality_score": None,
        "headline_score": None,
        "mutation_score": None,
        "universal_threshold": None,
        "merge_blocker_authorized": False,
        "ecological_inference_allowed": False,
        "holdout_selected": False,
        "primary_denominator_eligible": False,
        "external_repository_execution_authorized": False,
        "release_authorized": False,
        "deployment_authorized": False,
        "method_superiority_claim_allowed": False,
        "production_readiness_claim_allowed": False,
        "scientific_novelty_claim_allowed": False,
        "award_level_significance_claim_allowed": False,
    },
    "execution_authorized": False,
    "plan_sha256": None,
}
PLAN["plan_sha256"] = sha256_document(PLAN)

CATALOG_RECORDS: list[dict[str, object]] = []
seen_source: dict[str, str] = {}
for definition in VARIANT_DEFINITIONS:
    source = replace_once(SOURCE, str(definition["old"]), str(definition["new"]))
    source_sha = sha256_bytes(source.encode("utf-8"))
    source_ast_sha = ast_sha256(source)
    status = str(definition["status"])
    duplicate_of = seen_source.get(source_sha) if status == "duplicate" else None
    implementation_sha = sha256_document(
        {
            "schema_version": "deltawitness.dw001-claim-path-implementation.v1",
            "plan_sha256": PLAN["plan_sha256"],
            "implementation_id": definition["implementation_id"],
            "status": status,
            "source_sha256": source_sha,
            "ast_sha256": source_ast_sha,
        }
    )
    if status.startswith("generated"):
        seen_source[source_sha] = implementation_sha
    CATALOG_RECORDS.append(
        {
            "order": definition["order"],
            "implementation_id": definition["implementation_id"],
            "role": definition["role"],
            "status": status,
            "implementation_sha256": implementation_sha,
            "duplicate_of": duplicate_of,
            "source_sha256": source_sha,
            "ast_sha256": source_ast_sha,
            "compile_valid": True,
            "source_body_in_artifact": False,
        }
    )

CATALOG_RECORDS.append(
    {
        "order": 6,
        "implementation_id": "not-applicable-addition-control-v1",
        "role": "not_applicable_control",
        "status": "not_applicable",
        "implementation_sha256": sha256_document(
            {
                "schema_version": "deltawitness.dw001-claim-path-implementation.v1",
                "plan_sha256": PLAN["plan_sha256"],
                "implementation_id": "not-applicable-addition-control-v1",
                "status": "not_applicable",
                "source_sha256": None,
                "ast_sha256": None,
            }
        ),
        "duplicate_of": None,
        "source_sha256": None,
        "ast_sha256": None,
        "compile_valid": None,
        "source_body_in_artifact": False,
    }
)
INVALID_SOURCE = "def authorize(user, *, decision_route, collateral_route):\n    return (\n"
CATALOG_RECORDS.append(
    {
        "order": 7,
        "implementation_id": "invalid-render-control-v1",
        "role": "invalid_control",
        "status": "invalid",
        "implementation_sha256": sha256_document(
            {
                "schema_version": "deltawitness.dw001-claim-path-implementation.v1",
                "plan_sha256": PLAN["plan_sha256"],
                "implementation_id": "invalid-render-control-v1",
                "status": "invalid",
                "source_sha256": sha256_bytes(INVALID_SOURCE.encode("utf-8")),
                "ast_sha256": None,
            }
        ),
        "duplicate_of": None,
        "source_sha256": sha256_bytes(INVALID_SOURCE.encode("utf-8")),
        "ast_sha256": None,
        "compile_valid": False,
        "source_body_in_artifact": False,
    }
)
EQUIVALENT_REVIEW_SOURCE = SOURCE.replace(
    "    return {\n", "    result = {\n", 1
).replace(
    '        "trace_code": trace_code,\n    }\n',
    '        "trace_code": trace_code,\n    }\n    return result\n',
    1,
)
compile(EQUIVALENT_REVIEW_SOURCE, SOURCE_PATH, "exec")
equivalent_source_sha = sha256_bytes(EQUIVALENT_REVIEW_SOURCE.encode("utf-8"))
equivalent_ast_sha = ast_sha256(EQUIVALENT_REVIEW_SOURCE)
CATALOG_RECORDS.append(
    {
        "order": 8,
        "implementation_id": "equivalent-review-copy-return-v1",
        "role": "equivalent_review_control",
        "status": "equivalent_review_required",
        "implementation_sha256": sha256_document(
            {
                "schema_version": "deltawitness.dw001-claim-path-implementation.v1",
                "plan_sha256": PLAN["plan_sha256"],
                "implementation_id": "equivalent-review-copy-return-v1",
                "status": "equivalent_review_required",
                "source_sha256": equivalent_source_sha,
                "ast_sha256": equivalent_ast_sha,
            }
        ),
        "duplicate_of": None,
        "source_sha256": equivalent_source_sha,
        "ast_sha256": equivalent_ast_sha,
        "compile_valid": True,
        "source_body_in_artifact": False,
    }
)

CATALOG: dict[str, Any] = {
    "schema_version": CATALOG_SCHEMA,
    "study_id": "DW-001",
    "plan_id": PLAN_ID,
    "plan_sha256": PLAN["plan_sha256"],
    "partition": "development",
    "source": deepcopy(PLAN["source_scope"]),
    "test": deepcopy(PLAN["test_scope"]),
    "implementations": CATALOG_RECORDS,
    "summary": {
        "total_records": 8,
        "generated": 3,
        "generated_behavior_preserving_control": 1,
        "duplicate": 1,
        "not_applicable": 1,
        "invalid": 1,
        "equivalent_review_required": 1,
        "score": None,
    },
    "catalog_sha256": None,
}
CATALOG["catalog_sha256"] = sha256_document(CATALOG)



PRIOR_ART: dict[str, Any] = {
    "schema_version": PRIOR_ART_SCHEMA,
    "study_id": "DW-001",
    "log_id": "DW-001-CLAIM-RELEVANT-PATH-PRIOR-ART-LOG-V1",
    "status": "pre_execution_literature_boundary",
    "reviewed_at": "2026-08-18",
    "plan_id": PLAN_ID,
    "plan_sha256": PLAN["plan_sha256"],
    "catalog_sha256": CATALOG["catalog_sha256"],
    "sources": [
        {"order": 1, "source_id": "coveragepy-7.15.2-contexts-api", "title": "Coverage.py measurement contexts and public API", "source_type": "official-versioned-tool-documentation", "identifier": "https://coverage.readthedocs.io/en/7.15.2/", "baseline_role": "Exact statement, arc, branch-statistic, and per-selector context evidence.", "boundary": "Execution structure does not establish assertion influence or oracle adequacy."},
        {"order": 2, "source_id": "schuler-zeller-checked-coverage", "title": "Checked coverage: an indicator for oracle quality", "source_type": "peer-reviewed-primary-research", "identifier": "10.1002/stvr.1497", "baseline_role": "Dynamic slice of covered statements influencing an oracle.", "boundary": "This preregistration does not implement or claim general checked coverage."},
        {"order": 3, "source_id": "korel-laski-dynamic-slicing", "title": "Dynamic Program Slicing", "source_type": "peer-reviewed-primary-research", "identifier": "Information Processing Letters 29(3), 1988", "baseline_role": "Execution-specific program dependence and slicing.", "boundary": "The fixed influence graph is one project-owned control, not a dynamic slicer."},
        {"order": 4, "source_id": "weiser-program-slicing", "title": "Program Slicing", "source_type": "peer-reviewed-primary-research", "identifier": "IEEE TSE 10(4), 1984", "baseline_role": "Foundational slicing criterion and dependence abstraction.", "boundary": "No general static slicing claim is made."},
        {"order": 5, "source_id": "barr-oracle-survey", "title": "The Oracle Problem in Software Testing: A Survey", "source_type": "peer-reviewed-survey", "identifier": "10.1109/TSE.2014.2372785", "baseline_role": "Limits of determining expected behavior and oracle adequacy.", "boundary": "The fixed assertions are project-owned controls, not a solution to the oracle problem."},
        {"order": 6, "source_id": "jia-harman-mutation-survey", "title": "An Analysis and Survey of the Development of Mutation Testing", "source_type": "peer-reviewed-survey", "identifier": "10.1109/TSE.2010.62", "baseline_role": "Mutation operators, adequacy, equivalence, and cost.", "boundary": "The fixed catalog is not representative and produces no mutation score."},
    ],
    "closest_baselines": [
        {"order": 1, "baseline_id": "raw-selector-context-paths", "captures": "Exact per-selector executed statement and arc shapes.", "planned_comparison": "Distinguish all decision and collateral routes.", "not_claimed": "No claim relevance or oracle strength."},
        {"order": 2, "baseline_id": "explicit-route-membership", "captures": "Exact declared decision and collateral route labels.", "planned_comparison": "Prefer this simpler baseline if it captures every runtime distinction.", "not_claimed": "No evidence that declared labels match actual execution."},
        {"order": 3, "baseline_id": "fixed-assertion-influence-graph", "captures": "Exact project-owned dependence relation from inputs/routes to returned fields.", "planned_comparison": "Separate decision-route from collateral-only computation.", "not_claimed": "No general static or dynamic slicing."},
        {"order": 4, "baseline_id": "typed-claim-and-collateral-assertions", "captures": "Exact behavior of claim-facing and separately labeled collateral reference checks.", "planned_comparison": "Prevent collateral failures from satisfying the authorization claim.", "not_claimed": "No complete specification."},
        {"order": 5, "baseline_id": "fixed-fault-incidence", "captures": "Exact typed outcomes for route-local, shared, collateral, and neutral-diversion controls.", "planned_comparison": "Test bounded relation between influence and fault detection.", "not_claimed": "No mutation adequacy or method superiority."},
    ],
    "planned_difference": {
        "question": "Whether integrity-bound runtime path evidence can be filtered by one exact assertion-influence control without conflating collateral divergence with claim failure.",
        "simpler_baseline_preferred_if_equivalent": True,
        "negative_control": "Reject-all-path-divergence is expected to over-refuse at least one valid control.",
    },
    "novelty_boundary": {"novelty_status": "not_established", "systematic_review_complete": False, "scientific_novelty_claim_allowed": False, "award_level_significance_claim_allowed": False},
    "policy": deepcopy(PLAN["policy"]),
    "log_sha256": None,
}
PRIOR_ART["log_sha256"] = sha256_document(PRIOR_ART)

_REVIEWED = {
    "source_sha256": "8c1bdd26c2e98cd209f210630bfe4d274a3dcd7bbd042db8b8586c7750814327",
    "source_ast_sha256": "dabb7011748968f8d43d590ff843a91697a3344a2400d7cabaf926b79ca88e2d",
    "test_sha256": "8a26d52fa7fbb4ab7fc6eab466d9051cd329b0da09a667b5e220fbbfd416d1e9",
    "influence_control_sha256": "7b068d2f71003fade4eca77e1aa9cdb3a0f2f526f89dbd4828d4f17fbf2bd4f5",
    "plan_sha256": "ff0403132c3424fc7309a15a05794eed93ac9eb526de172e17326f8409ca0888",
    "catalog_sha256": "f36fbe58c00cfb8ed0fd994f3bb1dcdb45040774f7ae4663563b9f40ac15daa5",
    "prior_art_log_sha256": "5f697631a5ded7a413dd11f4da0606ee8809e2b0f5de257ecab53a7e2d7f790c",
}
PLAN_SHA256 = _REVIEWED["plan_sha256"]
CATALOG_SHA256 = _REVIEWED["catalog_sha256"]
PRIOR_ART_LOG_SHA256 = _REVIEWED["prior_art_log_sha256"]
INFLUENCE_CONTROL_SHA256 = _REVIEWED["influence_control_sha256"]
_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")


class DW001ClaimRelevantPathPlanError(DeltaWitnessError):
    """Raised when the frozen preregistration contract is inconsistent."""


def _error(context: str, detail: str) -> DW001ClaimRelevantPathPlanError:
    return DW001ClaimRelevantPathPlanError(f"{context}: {detail}")


def _assert_reviewed_identities() -> None:
    observed = {
        "source_sha256": SOURCE_SHA256,
        "source_ast_sha256": SOURCE_AST_SHA256,
        "test_sha256": TEST_SHA256,
        "influence_control_sha256": INFLUENCE_CONTROL["control_sha256"],
        "plan_sha256": PLAN["plan_sha256"],
        "catalog_sha256": CATALOG["catalog_sha256"],
        "prior_art_log_sha256": PRIOR_ART["log_sha256"],
    }
    for name, expected in _REVIEWED.items():
        if observed[name] != expected:
            raise _error("claim-relevant path reviewed identity", f"{name} mismatch; expected {expected}, observed {observed[name]}")


def _self_digest(document: dict[str, Any], field: str, context: str) -> str:
    if not isinstance(document, dict):
        raise _error(context, "must be an object")
    normalized = deepcopy(document)
    normalized[field] = None
    return sha256_document(normalized)


def compute_claim_relevant_path_plan_sha256(document: dict[str, Any]) -> str:
    return _self_digest(document, "plan_sha256", "claim-relevant path plan")


def compute_claim_relevant_path_catalog_sha256(document: dict[str, Any]) -> str:
    return _self_digest(document, "catalog_sha256", "claim-relevant path catalog")


def compute_claim_relevant_path_prior_art_sha256(document: dict[str, Any]) -> str:
    return _self_digest(document, "log_sha256", "claim-relevant path prior art")


def _compile_fixed_sources() -> None:
    source_tree = ast.parse(SOURCE, filename=SOURCE_PATH, mode="exec")
    test_tree = ast.parse(TESTS, filename=TEST_PATH, mode="exec")
    compile(source_tree, SOURCE_PATH, "exec")
    compile(test_tree, TEST_PATH, "exec")
    compile(ast.parse(ast.unparse(source_tree) + "\n", filename=SOURCE_PATH, mode="exec"), SOURCE_PATH, "exec")


def build_claim_relevant_path_plan() -> dict[str, Any]:
    _compile_fixed_sources()
    _assert_reviewed_identities()
    return deepcopy(PLAN)


def build_claim_relevant_path_catalog(plan: object) -> dict[str, Any]:
    valid, errors = verify_claim_relevant_path_plan_document(plan)
    if not valid:
        raise _error("claim-relevant path catalog plan", "; ".join(errors))
    _assert_reviewed_identities()
    return deepcopy(CATALOG)


def build_claim_relevant_path_prior_art_log(plan: object, catalog: object) -> dict[str, Any]:
    valid, errors = verify_claim_relevant_path_catalog_document(catalog, plan)
    if not valid:
        raise _error("claim-relevant path prior-art catalog", "; ".join(errors))
    _assert_reviewed_identities()
    return deepcopy(PRIOR_ART)


def _differences(expected: object, observed: object, *, context: str) -> list[str]:
    if type(expected) is not type(observed):
        return [f"{context}: type mismatch; expected {type(expected).__name__}, observed {type(observed).__name__}"]
    if isinstance(expected, dict):
        assert isinstance(observed, dict)
        errors: list[str] = []
        expected_keys, observed_keys = set(expected), set(observed)
        if expected_keys != observed_keys:
            errors.append(f"{context}: field mismatch; missing={sorted(expected_keys-observed_keys)}, extra={sorted(observed_keys-expected_keys)}")
        for key in sorted(expected_keys & observed_keys):
            errors.extend(_differences(expected[key], observed[key], context=f"{context}.{key}"))
        return errors
    if isinstance(expected, list):
        assert isinstance(observed, list)
        errors = []
        if len(expected) != len(observed):
            errors.append(f"{context}: length mismatch; expected {len(expected)}, observed {len(observed)}")
        for index, (left, right) in enumerate(zip(expected, observed, strict=False)):
            errors.extend(_differences(left, right, context=f"{context}[{index}]"))
        return errors
    return [] if expected == observed else [f"{context}: expected={expected!r}, observed={observed!r}"]


def _validated_digest(value: object, expected: str, *, context: str) -> tuple[str, list[str]]:
    if not isinstance(value, str) or _SHA256_PATTERN.fullmatch(value) is None:
        raise _error(context, "expected a lowercase SHA-256 digest")
    return value, ([] if value == expected else [f"{context}: reviewed identity mismatch"])


def _failure(context: str, exc: BaseException) -> tuple[bool, tuple[str, ...]]:
    return False, (f"{context}: verification failed closed: {type(exc).__name__}: {exc}",)


def _verify_exact(document: object, expected: dict[str, Any], *, digest_field: str, reviewed_digest: str, context: str) -> tuple[bool, tuple[str, ...]]:
    try:
        if not isinstance(document, dict):
            raise _error(context, "must be an object")
        _assert_reviewed_identities()
        recorded, errors = _validated_digest(document.get(digest_field), reviewed_digest, context=f"{context}.{digest_field}")
        computed = _self_digest(document, digest_field, context)
        if recorded != computed:
            errors.append(f"{context}.{digest_field}: digest mismatch")
        errors.extend(_differences(expected, document, context=context))
    except (DW001ClaimRelevantPathPlanError, DeltaWitnessError, KeyError, TypeError, IndexError, ValueError, OverflowError, MemoryError, RecursionError) as exc:
        return _failure(context, exc)
    unique = tuple(dict.fromkeys(errors))
    return not unique, unique


def verify_claim_relevant_path_plan_document(document: object) -> tuple[bool, tuple[str, ...]]:
    return _verify_exact(document, PLAN, digest_field="plan_sha256", reviewed_digest=PLAN_SHA256, context="claim-relevant path plan")


def verify_claim_relevant_path_catalog_document(document: object, plan: object) -> tuple[bool, tuple[str, ...]]:
    valid, errors = verify_claim_relevant_path_plan_document(plan)
    if not valid:
        return False, tuple(f"claim-relevant path catalog plan: {error}" for error in errors)
    return _verify_exact(document, CATALOG, digest_field="catalog_sha256", reviewed_digest=CATALOG_SHA256, context="claim-relevant path catalog")


def verify_claim_relevant_path_prior_art_log_document(document: object, plan: object, catalog: object) -> tuple[bool, tuple[str, ...]]:
    valid, errors = verify_claim_relevant_path_catalog_document(catalog, plan)
    if not valid:
        return False, tuple(f"claim-relevant path prior-art catalog: {error}" for error in errors)
    return _verify_exact(document, PRIOR_ART, digest_field="log_sha256", reviewed_digest=PRIOR_ART_LOG_SHA256, context="claim-relevant path prior art")


def _load_regular_document(path: Path, *, context: str) -> dict[str, Any]:
    try:
        status = path.lstat()
    except OSError as exc:
        raise _error(context, f"cannot inspect {path}: {exc}") from exc
    if stat.S_ISLNK(status.st_mode) or not stat.S_ISREG(status.st_mode):
        raise _error(context, f"expected a regular non-symbolic-link file: {path}")
    try:
        document = load_report(path)
    except DeltaWitnessError as exc:
        raise _error(context, str(exc)) from exc
    if not isinstance(document, dict):
        raise _error(context, "document root must be an object")
    return document


def load_claim_relevant_path_plan(path: Path) -> dict[str, Any]:
    document = _load_regular_document(path, context="claim-relevant path plan")
    valid, errors = verify_claim_relevant_path_plan_document(document)
    if not valid:
        raise _error("claim-relevant path plan", "; ".join(errors))
    return document


def load_claim_relevant_path_catalog(path: Path, plan: object) -> dict[str, Any]:
    document = _load_regular_document(path, context="claim-relevant path catalog")
    valid, errors = verify_claim_relevant_path_catalog_document(document, plan)
    if not valid:
        raise _error("claim-relevant path catalog", "; ".join(errors))
    return document


def load_claim_relevant_path_prior_art_log(path: Path, plan: object, catalog: object) -> dict[str, Any]:
    document = _load_regular_document(path, context="claim-relevant path prior art")
    valid, errors = verify_claim_relevant_path_prior_art_log_document(document, plan, catalog)
    if not valid:
        raise _error("claim-relevant path prior art", "; ".join(errors))
    return document


__all__ = [
    "CATALOG_SCHEMA_VERSION", "CATALOG_SHA256", "CELLS", "COVERAGEPY_MANIFEST_SHA256",
    "DW001ClaimRelevantPathPlanError", "INFLUENCE_CONTROL_SHA256", "INTERACTION_CHECKPOINT_SHA256",
    "INTERACTION_SEMANTIC_SHA256", "MAIN_COMMIT", "PLAN_ID", "PLAN_SCHEMA_VERSION", "PLAN_SHA256",
    "PRIOR_ART_LOG_SHA256", "PRIOR_ART_SCHEMA_VERSION", "PROFILES", "SOURCE", "SOURCE_AST_SHA256",
    "SOURCE_PATH", "SOURCE_SHA256", "TESTS", "TEST_PATH", "TEST_SHA256", "ast_sha256",
    "build_claim_relevant_path_catalog", "build_claim_relevant_path_plan", "build_claim_relevant_path_prior_art_log",
    "compute_claim_relevant_path_catalog_sha256", "compute_claim_relevant_path_plan_sha256",
    "compute_claim_relevant_path_prior_art_sha256", "load_claim_relevant_path_catalog",
    "load_claim_relevant_path_plan", "load_claim_relevant_path_prior_art_log", "path_shape", "sha256_bytes",
    "verify_claim_relevant_path_catalog_document", "verify_claim_relevant_path_plan_document",
    "verify_claim_relevant_path_prior_art_log_document",
]
