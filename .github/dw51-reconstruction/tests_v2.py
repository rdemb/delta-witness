from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FILES: dict[str, str] = {
    "tests/test_dw001_claim_relevant_path_preregistration.py": r'''from __future__ import annotations

import ast
from pathlib import Path
import sys
import unittest

from deltawitness.dw001_claim_relevant_path_plan import (
    CATALOG_SHA256,
    CELLS,
    COVERAGEPY_MANIFEST_SHA256,
    INFLUENCE_CONTROL_SHA256,
    INTERACTION_CHECKPOINT_SHA256,
    INTERACTION_SEMANTIC_SHA256,
    MAIN_COMMIT,
    PLAN_SHA256,
    PRIOR_ART_LOG_SHA256,
    PROFILES,
    SOURCE,
    SOURCE_AST_SHA256,
    SOURCE_PATH,
    SOURCE_SHA256,
    TESTS,
    TEST_PATH,
    TEST_SHA256,
    ast_sha256,
    build_claim_relevant_path_catalog,
    build_claim_relevant_path_plan,
    build_claim_relevant_path_prior_art_log,
    load_claim_relevant_path_catalog,
    load_claim_relevant_path_plan,
    load_claim_relevant_path_prior_art_log,
    path_shape,
    sha256_bytes,
    verify_claim_relevant_path_catalog_document,
    verify_claim_relevant_path_plan_document,
    verify_claim_relevant_path_prior_art_log_document,
)
from deltawitness.reporting import load_report

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research" / "DW-001"

EXPECTED = {
    "main_commit": "3a363c3bdaa6e8fbbd0d6ab33f2417d76a50a5e9",
    "interaction_semantic_sha256": "bc2ab879595da61815aa7dcc33a09c6334b93dea3fd464f2fe4a5437944ebb77",
    "interaction_checkpoint_sha256": "40cf297679c83809368e53f35796d817761c25746302530f29fa4dda603277fc",
    "coveragepy_manifest_sha256": "28f6430e45fcfda973a1fcd57157e2317f096cc2774e8281244eaf18a9d0dd3f",
    "source_sha256": "8c1bdd26c2e98cd209f210630bfe4d274a3dcd7bbd042db8b8586c7750814327",
    "source_ast_sha256": "dabb7011748968f8d43d590ff843a91697a3344a2400d7cabaf926b79ca88e2d",
    "test_sha256": "8a26d52fa7fbb4ab7fc6eab466d9051cd329b0da09a667b5e220fbbfd416d1e9",
    "influence_control_sha256": "7b068d2f71003fade4eca77e1aa9cdb3a0f2f526f89dbd4828d4f17fbf2bd4f5",
    "plan_sha256": "ff0403132c3424fc7309a15a05794eed93ac9eb526de172e17326f8409ca0888",
    "catalog_sha256": "f36fbe58c00cfb8ed0fd994f3bb1dcdb45040774f7ae4663563b9f40ac15daa5",
    "prior_art_log_sha256": "5f697631a5ded7a413dd11f4da0606ee8809e2b0f5de257ecab53a7e2d7f790c",
}


class DW001ClaimRelevantPathPreregistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan_path = RESEARCH / "claim-relevant-path-divergence-plan.v1.json"
        cls.catalog_path = RESEARCH / "claim-relevant-path-divergence-catalog.v1.json"
        cls.prior_path = RESEARCH / "claim-relevant-path-prior-art-log.v1.json"
        cls.plan = load_report(cls.plan_path)
        cls.catalog = load_report(cls.catalog_path)
        cls.prior = load_report(cls.prior_path)

    def test_reviewed_identity_constants_remain_exact(self) -> None:
        self.assertEqual(MAIN_COMMIT, EXPECTED["main_commit"])
        self.assertEqual(INTERACTION_SEMANTIC_SHA256, EXPECTED["interaction_semantic_sha256"])
        self.assertEqual(INTERACTION_CHECKPOINT_SHA256, EXPECTED["interaction_checkpoint_sha256"])
        self.assertEqual(COVERAGEPY_MANIFEST_SHA256, EXPECTED["coveragepy_manifest_sha256"])
        self.assertEqual(SOURCE_SHA256, EXPECTED["source_sha256"])
        self.assertEqual(SOURCE_AST_SHA256, EXPECTED["source_ast_sha256"])
        self.assertEqual(TEST_SHA256, EXPECTED["test_sha256"])
        self.assertEqual(INFLUENCE_CONTROL_SHA256, EXPECTED["influence_control_sha256"])
        self.assertEqual(PLAN_SHA256, EXPECTED["plan_sha256"])
        self.assertEqual(CATALOG_SHA256, EXPECTED["catalog_sha256"])
        self.assertEqual(PRIOR_ART_LOG_SHA256, EXPECTED["prior_art_log_sha256"])

    def test_fixed_source_and_test_bytes_reproduce_reviewed_hashes(self) -> None:
        self.assertEqual(sha256_bytes(SOURCE.encode("utf-8")), SOURCE_SHA256)
        self.assertEqual(ast_sha256(SOURCE), SOURCE_AST_SHA256)
        self.assertEqual(sha256_bytes(TESTS.encode("utf-8")), TEST_SHA256)
        compile(ast.parse(SOURCE, filename=SOURCE_PATH, mode="exec"), SOURCE_PATH, "exec")
        compile(ast.parse(TESTS, filename=TEST_PATH, mode="exec"), TEST_PATH, "exec")

    def test_builders_reproduce_committed_canonical_documents(self) -> None:
        plan = build_claim_relevant_path_plan()
        catalog = build_claim_relevant_path_catalog(plan)
        prior = build_claim_relevant_path_prior_art_log(plan, catalog)
        self.assertEqual(plan, self.plan)
        self.assertEqual(catalog, self.catalog)
        self.assertEqual(prior, self.prior)

    def test_regular_file_loaders_recheck_the_complete_chain(self) -> None:
        plan = load_claim_relevant_path_plan(self.plan_path)
        catalog = load_claim_relevant_path_catalog(self.catalog_path, plan)
        prior = load_claim_relevant_path_prior_art_log(self.prior_path, plan, catalog)
        self.assertEqual(plan, self.plan)
        self.assertEqual(catalog, self.catalog)
        self.assertEqual(prior, self.prior)

    def test_verifiers_accept_only_the_frozen_documents(self) -> None:
        self.assertEqual(verify_claim_relevant_path_plan_document(self.plan), (True, ()))
        self.assertEqual(
            verify_claim_relevant_path_catalog_document(self.catalog, self.plan),
            (True, ()),
        )
        self.assertEqual(
            verify_claim_relevant_path_prior_art_log_document(
                self.prior,
                self.plan,
                self.catalog,
            ),
            (True, ()),
        )

    def test_design_only_execution_and_decision_fields_fail_closed(self) -> None:
        self.assertIs(self.plan["execution_authorized"], False)
        future = self.plan["future_execution_contract"]
        self.assertEqual(future["execution_status"], "not_implemented")
        self.assertEqual(future["complete_divergence_status"], "unexpected")
        self.assertEqual(future["missing_or_ambiguous_status"], "indeterminate")
        self.assertIsNone(future["score"])
        self.assertIsNone(future["universal_threshold"])
        self.assertIs(future["merge_blocker_authorized"], False)
        for key in (
            "quality_score",
            "headline_score",
            "mutation_score",
            "universal_threshold",
        ):
            self.assertIsNone(self.plan["policy"][key])
        for key, value in self.plan["policy"].items():
            if key not in {
                "quality_score",
                "headline_score",
                "mutation_score",
                "universal_threshold",
            }:
                self.assertIs(value, False, key)

    def test_owned_two_by_two_cells_are_complete_and_selector_ids_unique(self) -> None:
        self.assertEqual(len(CELLS), 8)
        observed = {
            (
                cell["input_class"],
                cell["decision_route"],
                cell["collateral_route"],
            )
            for cell in CELLS
        }
        expected = {
            (input_class, decision_route, collateral_route)
            for input_class in ("allowed", "denied")
            for decision_route in ("direct", "normalized")
            for collateral_route in ("compact", "verbose")
        }
        self.assertEqual(observed, expected)
        self.assertEqual(len({cell["cell_id"] for cell in CELLS}), 8)
        self.assertEqual(len({cell["claim_selector_id"] for cell in CELLS}), 8)
        self.assertEqual(
            len({cell["collateral_reference_selector_id"] for cell in CELLS}),
            8,
        )

    def test_overlapping_profiles_are_explicit_and_not_primary_denominators(self) -> None:
        self.assertEqual(len(PROFILES), 6)
        self.assertEqual(
            [profile["profile_id"] for profile in PROFILES],
            [
                "decision-direct-v1",
                "decision-normalized-v1",
                "collateral-compact-v1",
                "collateral-verbose-v1",
                "claim-allowed-v1",
                "claim-denied-v1",
            ],
        )
        memberships = [set(profile["cell_ids"]) for profile in PROFILES]
        self.assertTrue(any(left & right for left in memberships for right in memberships if left is not right))
        for profile in PROFILES:
            self.assertEqual(len(profile["cell_ids"]), 4)
            self.assertEqual(len(profile["claim_selector_ids"]), 4)
            self.assertEqual(len(profile["collateral_reference_selector_ids"]), 4)
            self.assertIs(profile["primary_denominator_eligible"], False)

    def test_fixed_influence_control_separates_claim_and_collateral_nodes(self) -> None:
        control = self.plan["influence_control"]
        self.assertEqual(control["control_sha256"], INFLUENCE_CONTROL_SHA256)
        reverse: dict[str, set[str]] = {}
        for source, target in control["edges"]:
            reverse.setdefault(target, set()).add(source)

        def ancestors(targets: set[str]) -> set[str]:
            seen = set(targets)
            pending = list(targets)
            while pending:
                target = pending.pop()
                for source in reverse.get(target, set()):
                    if source not in seen:
                        seen.add(source)
                        pending.append(source)
            return seen

        claim_ancestors = ancestors(set(control["criterion_fields"]))
        self.assertEqual(
            claim_ancestors,
            set(control["expected_claim_influencing_nodes"]),
        )
        self.assertTrue(
            set(control["expected_collateral_only_nodes"]).isdisjoint(claim_ancestors)
        )
        self.assertIs(control["general_dynamic_slicing_claim_allowed"], False)
        self.assertIs(control["checked_coverage_claim_allowed"], False)

    def test_candidate_path_shapes_are_independently_derived(self) -> None:
        for cell in self.plan["cells"]:
            expected = path_shape(
                decision_route=cell["decision_route"],
                collateral_route=cell["collateral_route"],
                allowed=cell["expected_allowed"],
            )
            self.assertEqual(cell["expected_candidate_path"], expected)
            self.assertEqual(
                len(expected["executed_arcs"]),
                len(expected["executed_statements"]) + 1,
            )

    def test_fault_and_neutral_control_matrix_is_complete(self) -> None:
        matrix = {
            row["implementation_id"]: row
            for row in self.plan["expected_execution_matrix"]
        }
        self.assertEqual(len(matrix), 4)
        expected_counts = {
            "direct-role-inversion-v1": (4, 0, 4),
            "verbose-via-compact-collateral-diversion-v1": (0, 4, 4),
            "shared-or-gates-v1": (4, 0, 4),
            "direct-via-normalized-neutral-diversion-v1": (0, 0, 4),
        }
        for implementation_id, (claim_fail, collateral_fail, path_divergent) in expected_counts.items():
            outcomes = matrix[implementation_id]["selector_outcomes"]
            self.assertEqual(len(outcomes), 8)
            self.assertEqual(
                sum(item["expected_claim_observed"] == "fail" for item in outcomes),
                claim_fail,
            )
            self.assertEqual(
                sum(
                    item["expected_collateral_reference_observed"] == "fail"
                    for item in outcomes
                ),
                collateral_fail,
            )
            self.assertEqual(
                sum(item["expected_candidate_path_conformant"] is False for item in outcomes),
                path_divergent,
            )
        self.assertIs(
            self.plan["expected_relations"][
                "reject_all_path_divergence_overrefuses_valid_control"
            ],
            True,
        )

    def test_catalog_retains_generation_controls_without_execution_outcomes(self) -> None:
        statuses = [record["status"] for record in self.catalog["implementations"]]
        self.assertEqual(
            statuses,
            [
                "generated",
                "generated",
                "generated",
                "generated_behavior_preserving_control",
                "duplicate",
                "not_applicable",
                "invalid",
                "equivalent_review_required",
            ],
        )
        self.assertEqual(self.catalog["summary"]["total_records"], 8)
        self.assertIsNone(self.catalog["summary"]["score"])
        for record in self.catalog["implementations"]:
            self.assertNotIn("outcome", record)
            self.assertNotIn("killed", record)
            self.assertIs(record["source_body_in_artifact"], False)

    def test_prior_art_and_public_claim_boundary_remain_narrow(self) -> None:
        self.assertEqual(len(self.prior["sources"]), 6)
        self.assertEqual(len(self.prior["closest_baselines"]), 5)
        novelty = self.prior["novelty_boundary"]
        self.assertEqual(novelty["novelty_status"], "not_established")
        self.assertIs(novelty["systematic_review_complete"], False)
        self.assertIs(novelty["scientific_novelty_claim_allowed"], False)
        self.assertIs(novelty["award_level_significance_claim_allowed"], False)
        self.assertIs(
            self.prior["planned_difference"][
                "simpler_baseline_preferred_if_equivalent"
            ],
            True,
        )

    def test_import_is_dependency_free_and_does_not_load_coveragepy(self) -> None:
        self.assertNotIn("coverage", sys.modules)

    def test_module_contains_no_candidate_execution_primitive(self) -> None:
        module_path = (
            ROOT
            / "src"
            / "deltawitness"
            / "dw001_claim_relevant_path_plan.py"
        )
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        forbidden = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in {"exec", "eval"}
        ]
        self.assertEqual(forbidden, [])


if __name__ == "__main__":
    unittest.main()
''',
    "tests/test_dw001_claim_relevant_path_adversarial.py": r'''from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from deltawitness.dw001_claim_relevant_path_plan import (
    DW001ClaimRelevantPathPlanError,
    build_claim_relevant_path_catalog,
    build_claim_relevant_path_plan,
    build_claim_relevant_path_prior_art_log,
    compute_claim_relevant_path_catalog_sha256,
    compute_claim_relevant_path_plan_sha256,
    compute_claim_relevant_path_prior_art_sha256,
    load_claim_relevant_path_plan,
    verify_claim_relevant_path_catalog_document,
    verify_claim_relevant_path_plan_document,
    verify_claim_relevant_path_prior_art_log_document,
)


class DW001ClaimRelevantPathAdversarialTests(unittest.TestCase):
    def setUp(self) -> None:
        self.plan = build_claim_relevant_path_plan()
        self.catalog = build_claim_relevant_path_catalog(self.plan)
        self.prior = build_claim_relevant_path_prior_art_log(self.plan, self.catalog)

    @staticmethod
    def reseal_plan(document: dict[str, object]) -> None:
        document["plan_sha256"] = compute_claim_relevant_path_plan_sha256(document)

    @staticmethod
    def reseal_catalog(document: dict[str, object]) -> None:
        document["catalog_sha256"] = compute_claim_relevant_path_catalog_sha256(document)

    @staticmethod
    def reseal_prior(document: dict[str, object]) -> None:
        document["log_sha256"] = compute_claim_relevant_path_prior_art_sha256(document)

    def assert_plan_rejected(self, document: object) -> None:
        valid, errors = verify_claim_relevant_path_plan_document(document)
        self.assertIs(valid, False)
        self.assertTrue(errors)

    def test_digest_valid_route_membership_substitution_is_rejected(self) -> None:
        changed = deepcopy(self.plan)
        changed["cells"][0]["decision_route"] = "normalized"
        self.reseal_plan(changed)
        self.assert_plan_rejected(changed)

    def test_digest_valid_selector_role_substitution_is_rejected(self) -> None:
        changed = deepcopy(self.plan)
        changed["cells"][0]["claim_selector"] = changed["cells"][0][
            "collateral_reference_selector"
        ]
        self.reseal_plan(changed)
        self.assert_plan_rejected(changed)

    def test_digest_valid_cell_reordering_is_rejected(self) -> None:
        changed = deepcopy(self.plan)
        changed["cells"][0], changed["cells"][1] = (
            changed["cells"][1],
            changed["cells"][0],
        )
        self.reseal_plan(changed)
        self.assert_plan_rejected(changed)

    def test_digest_valid_influence_edge_substitution_is_rejected(self) -> None:
        changed = deepcopy(self.plan)
        changed["influence_control"]["edges"][0] = [
            "collateral_route",
            "allowed",
        ]
        self.reseal_plan(changed)
        self.assert_plan_rejected(changed)

    def test_digest_valid_expected_matrix_substitution_is_rejected(self) -> None:
        changed = deepcopy(self.plan)
        changed["expected_execution_matrix"][0]["selector_outcomes"][0][
            "expected_claim_observed"
        ] = "pass"
        self.reseal_plan(changed)
        self.assert_plan_rejected(changed)

    def test_extra_missing_and_wrong_type_fields_fail_closed(self) -> None:
        extra = deepcopy(self.plan)
        extra["escape_hatch"] = True
        self.assert_plan_rejected(extra)

        missing = deepcopy(self.plan)
        del missing["policy"]
        self.assert_plan_rejected(missing)

        wrong_type = deepcopy(self.plan)
        wrong_type["execution_authorized"] = 0
        self.reseal_plan(wrong_type)
        self.assert_plan_rejected(wrong_type)

    def test_catalog_status_and_outcome_injection_are_rejected_when_resealed(self) -> None:
        changed = deepcopy(self.catalog)
        changed["implementations"][5]["status"] = "generated"
        self.reseal_catalog(changed)
        valid, errors = verify_claim_relevant_path_catalog_document(
            changed,
            self.plan,
        )
        self.assertIs(valid, False)
        self.assertTrue(errors)

        injected = deepcopy(self.catalog)
        injected["implementations"][0]["outcome"] = "killed"
        self.reseal_catalog(injected)
        valid, errors = verify_claim_relevant_path_catalog_document(
            injected,
            self.plan,
        )
        self.assertIs(valid, False)
        self.assertTrue(errors)

    def test_catalog_duplicate_binding_substitution_is_rejected(self) -> None:
        changed = deepcopy(self.catalog)
        changed["implementations"][4]["duplicate_of"] = "0" * 64
        self.reseal_catalog(changed)
        valid, errors = verify_claim_relevant_path_catalog_document(
            changed,
            self.plan,
        )
        self.assertIs(valid, False)
        self.assertTrue(errors)

    def test_prior_art_novelty_promotion_is_rejected_when_resealed(self) -> None:
        changed = deepcopy(self.prior)
        changed["novelty_boundary"]["novelty_status"] = "established"
        changed["novelty_boundary"]["scientific_novelty_claim_allowed"] = True
        self.reseal_prior(changed)
        valid, errors = verify_claim_relevant_path_prior_art_log_document(
            changed,
            self.plan,
            self.catalog,
        )
        self.assertIs(valid, False)
        self.assertTrue(errors)

    def test_prior_art_source_reordering_is_rejected_when_resealed(self) -> None:
        changed = deepcopy(self.prior)
        changed["sources"].reverse()
        self.reseal_prior(changed)
        valid, errors = verify_claim_relevant_path_prior_art_log_document(
            changed,
            self.plan,
            self.catalog,
        )
        self.assertIs(valid, False)
        self.assertTrue(errors)

    def test_substituted_plan_cannot_generate_a_catalog(self) -> None:
        changed = deepcopy(self.plan)
        changed["source_scope"]["source_sha256"] = "0" * 64
        self.reseal_plan(changed)
        with self.assertRaises(DW001ClaimRelevantPathPlanError):
            build_claim_relevant_path_catalog(changed)

    def test_loader_rejects_symlink_directory_duplicate_keys_and_malformed_utf8(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            valid_path = root / "plan.json"
            valid_path.write_text(
                json.dumps(self.plan, separators=(",", ":")),
                encoding="utf-8",
            )
            link = root / "link.json"
            try:
                link.symlink_to(valid_path)
            except (OSError, NotImplementedError):
                link = None
            if link is not None:
                with self.assertRaises(DW001ClaimRelevantPathPlanError):
                    load_claim_relevant_path_plan(link)

            with self.assertRaises(DW001ClaimRelevantPathPlanError):
                load_claim_relevant_path_plan(root)

            duplicate = root / "duplicate.json"
            duplicate.write_text(
                '{"schema_version":"x","schema_version":"y"}',
                encoding="utf-8",
            )
            with self.assertRaises(DW001ClaimRelevantPathPlanError):
                load_claim_relevant_path_plan(duplicate)

            malformed = root / "malformed.json"
            malformed.write_bytes(b"{\xff}")
            with self.assertRaises(DW001ClaimRelevantPathPlanError):
                load_claim_relevant_path_plan(malformed)

    def test_verifiers_return_typed_fail_closed_results_for_non_objects(self) -> None:
        for value in (None, [], "x", 0, True):
            valid, errors = verify_claim_relevant_path_plan_document(value)
            self.assertIs(valid, False)
            self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
''',
    "tests/test_dw001_claim_relevant_path_schemas.py": r'''from __future__ import annotations

from pathlib import Path
import unittest

from deltawitness.reporting import load_report

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research" / "DW-001"
SCHEMA = RESEARCH / "schema"
CASES = (
    (
        "claim-relevant-path-divergence-plan.v1.json",
        "claim-relevant-path-divergence-plan.schema.json",
    ),
    (
        "claim-relevant-path-divergence-catalog.v1.json",
        "claim-relevant-path-divergence-catalog.schema.json",
    ),
    (
        "claim-relevant-path-prior-art-log.v1.json",
        "claim-relevant-path-prior-art-log.schema.json",
    ),
)


def walk(value: object):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def assert_exact_schema(
    test: unittest.TestCase,
    value: object,
    schema: object,
) -> None:
    test.assertIsInstance(schema, dict)
    assert isinstance(schema, dict)
    if "const" in schema:
        test.assertEqual(value, schema["const"])
        return
    if schema.get("type") == "object":
        test.assertIsInstance(value, dict)
        assert isinstance(value, dict)
        test.assertIs(schema.get("additionalProperties"), False)
        test.assertEqual(set(value), set(schema["required"]))
        test.assertEqual(set(value), set(schema["properties"]))
        for key, child in value.items():
            assert_exact_schema(test, child, schema["properties"][key])
        return
    if schema.get("type") == "array":
        test.assertIsInstance(value, list)
        assert isinstance(value, list)
        test.assertEqual(len(value), schema["minItems"])
        test.assertEqual(len(value), schema["maxItems"])
        test.assertEqual(len(value), len(schema["prefixItems"]))
        test.assertIs(schema["items"], False)
        for child, child_schema in zip(value, schema["prefixItems"], strict=True):
            assert_exact_schema(test, child, child_schema)
        return
    test.fail(f"unsupported exact schema node: {schema!r}")


class DW001ClaimRelevantPathSchemaTests(unittest.TestCase):
    def test_exact_schemas_accept_only_the_committed_documents(self) -> None:
        for artifact_name, schema_name in CASES:
            with self.subTest(artifact=artifact_name):
                artifact = load_report(RESEARCH / artifact_name)
                schema = load_report(SCHEMA / schema_name)
                self.assertEqual(
                    schema["$schema"],
                    "https://json-schema.org/draft/2020-12/schema",
                )
                assert_exact_schema(self, artifact, schema)

    def test_every_object_boundary_is_closed_and_every_array_is_bounded(self) -> None:
        for _, schema_name in CASES:
            schema = load_report(SCHEMA / schema_name)
            for node in walk(schema):
                if isinstance(node, dict) and node.get("type") == "object":
                    self.assertIs(node.get("additionalProperties"), False)
                    self.assertEqual(set(node["required"]), set(node["properties"]))
                if isinstance(node, dict) and node.get("type") == "array":
                    self.assertEqual(node["minItems"], node["maxItems"])
                    self.assertEqual(node["minItems"], len(node["prefixItems"]))
                    self.assertIs(node["items"], False)

    def test_plan_schema_freezes_design_only_boundary(self) -> None:
        schema = load_report(
            SCHEMA / "claim-relevant-path-divergence-plan.schema.json"
        )
        properties = schema["properties"]
        self.assertEqual(properties["execution_authorized"], {"const": False})
        future = properties["future_execution_contract"]["properties"]
        self.assertEqual(future["execution_status"], {"const": "not_implemented"})
        self.assertEqual(future["score"], {"const": None})
        self.assertEqual(future["universal_threshold"], {"const": None})
        self.assertEqual(future["merge_blocker_authorized"], {"const": False})

    def test_catalog_schema_retains_all_non_execution_statuses(self) -> None:
        schema = load_report(
            SCHEMA / "claim-relevant-path-divergence-catalog.schema.json"
        )
        records = schema["properties"]["implementations"]["prefixItems"]
        self.assertEqual(
            [record["properties"]["status"]["const"] for record in records],
            [
                "generated",
                "generated",
                "generated",
                "generated_behavior_preserving_control",
                "duplicate",
                "not_applicable",
                "invalid",
                "equivalent_review_required",
            ],
        )


if __name__ == "__main__":
    unittest.main()
''',
    "scripts/smoke_dw001_claim_relevant_path_plan.py": r'''#!/usr/bin/env python3
"""Rebuild and verify the design-only DW-001 claim-path preregistration."""

from __future__ import annotations

from pathlib import Path
import sys

from deltawitness.dw001_claim_relevant_path_plan import (
    CATALOG_SHA256,
    INFLUENCE_CONTROL_SHA256,
    PLAN_SHA256,
    PRIOR_ART_LOG_SHA256,
    SOURCE_AST_SHA256,
    SOURCE_SHA256,
    TEST_SHA256,
    build_claim_relevant_path_catalog,
    build_claim_relevant_path_plan,
    build_claim_relevant_path_prior_art_log,
    load_claim_relevant_path_catalog,
    load_claim_relevant_path_plan,
    load_claim_relevant_path_prior_art_log,
)

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research" / "DW-001"


def main() -> int:
    if "coverage" in sys.modules:
        raise AssertionError("Coverage.py was imported before preregistration smoke")

    committed_plan = load_claim_relevant_path_plan(
        RESEARCH / "claim-relevant-path-divergence-plan.v1.json"
    )
    committed_catalog = load_claim_relevant_path_catalog(
        RESEARCH / "claim-relevant-path-divergence-catalog.v1.json",
        committed_plan,
    )
    committed_prior = load_claim_relevant_path_prior_art_log(
        RESEARCH / "claim-relevant-path-prior-art-log.v1.json",
        committed_plan,
        committed_catalog,
    )

    rebuilt_plan = build_claim_relevant_path_plan()
    rebuilt_catalog = build_claim_relevant_path_catalog(rebuilt_plan)
    rebuilt_prior = build_claim_relevant_path_prior_art_log(
        rebuilt_plan,
        rebuilt_catalog,
    )
    if (
        committed_plan != rebuilt_plan
        or committed_catalog != rebuilt_catalog
        or committed_prior != rebuilt_prior
    ):
        raise AssertionError("committed preregistration artifacts changed")
    if committed_plan["execution_authorized"] is not False:
        raise AssertionError("candidate execution was authorized")
    if committed_plan["future_execution_contract"]["execution_status"] != "not_implemented":
        raise AssertionError("execution status changed")
    if "coverage" in sys.modules:
        raise AssertionError("preregistration smoke imported Coverage.py")

    print(
        "DW-001 claim-path preregistration smoke passed: "
        f"source_sha256={SOURCE_SHA256} "
        f"source_ast_sha256={SOURCE_AST_SHA256} "
        f"test_sha256={TEST_SHA256} "
        f"influence_sha256={INFLUENCE_CONTROL_SHA256} "
        f"plan_sha256={PLAN_SHA256} "
        f"catalog_sha256={CATALOG_SHA256} "
        f"prior_art_sha256={PRIOR_ART_LOG_SHA256} "
        "execution=not_implemented novelty=not_established"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''',
}

for relative, content in FILES.items():
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")

print(f"wrote {len(FILES)} deterministic regression files")
