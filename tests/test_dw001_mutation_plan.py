from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from deltawitness.dw001_mutation_plan import (
    ADAPTER_ID,
    CATALOG_SCHEMA_VERSION,
    OPERATOR_SET_ID,
    PLAN_ID,
    PLAN_SCHEMA_VERSION,
    build_claim_scoped_mutant_catalog,
    build_claim_scoped_mutation_plan,
    compute_mutant_catalog_sha256,
    compute_mutation_plan_sha256,
    verify_claim_scoped_mutant_catalog_document,
    verify_claim_scoped_mutation_plan_document,
)
from deltawitness.reporting import canonical_json


_ROOT = Path(__file__).resolve().parents[1]
_SCHEMA_DIR = _ROOT / "research" / "DW-001" / "schema"
_PLAN_PATH = _ROOT / "research" / "DW-001" / "claim-scoped-mutation-plan.v1.json"

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
_GENERIC_OPERATOR_IDS = [
    "return-constant-false-v1",
    "return-constant-true-v1",
    "comparison-eq-to-ne-v1",
]
_CONTROL_OPERATOR_IDS = [
    "duplicate-false-control-v1",
    "not-applicable-addition-control-v1",
    "invalid-render-control-v1",
]
_EXPECTED_STATUSES = [
    "generated",
    "generated",
    "generated",
    "duplicate",
    "not_applicable",
    "invalid",
]


def _walk(value: object):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


class DW001MutationPlanTests(unittest.TestCase):
    def test_plan_is_exact_deterministic_and_pre_execution_only(self) -> None:
        first = build_claim_scoped_mutation_plan()
        second = build_claim_scoped_mutation_plan()

        self.assertEqual(first, second)
        self.assertEqual(canonical_json(first), canonical_json(second))
        self.assertEqual(set(first), _PLAN_FIELDS)
        self.assertEqual(first["schema_version"], PLAN_SCHEMA_VERSION)
        self.assertEqual(first["study_id"], "DW-001")
        self.assertEqual(first["plan_id"], PLAN_ID)
        self.assertEqual(first["status"], "pre_execution_frozen_design")
        self.assertEqual(first["partition"], "development")
        self.assertEqual(first["adapter"]["id"], ADAPTER_ID)
        self.assertEqual(first["operator_set"]["id"], OPERATOR_SET_ID)
        self.assertEqual(
            [operator["operator_id"] for operator in first["operator_set"]["operators"]],
            _GENERIC_OPERATOR_IDS,
        )
        self.assertEqual(
            [control["operator_id"] for control in first["generation_controls"]],
            _CONTROL_OPERATOR_IDS,
        )
        self.assertFalse(first["execution_authorized"])
        self.assertFalse(first["holdout_selected"])
        self.assertFalse(first["primary_denominator_eligible"])
        self.assertIsNone(first["future_execution_contract"]["headline_score"])
        self.assertFalse(
            first["future_execution_contract"]["merge_blocker_authorized"]
        )
        self.assertTrue(
            first["future_execution_contract"]["retain_complete_mutant_table"]
        )

        valid, errors = verify_claim_scoped_mutation_plan_document(first)
        self.assertTrue(valid, errors)

    def test_plan_pairs_strong_and_weak_profiles_on_identical_source_scope(self) -> None:
        plan = build_claim_scoped_mutation_plan()
        self.assertEqual(
            plan["source_scope"],
            {
                "source_id": "authorization-predicate-candidate-v1",
                "path": "src/access.py",
                "symbol": "is_admin",
                "language": "python",
                "parser": "stdlib-ast",
                "source_sha256": plan["source_scope"]["source_sha256"],
                "ast_sha256": plan["source_scope"]["ast_sha256"],
                "target_cardinality": 1,
                "source_body_published": False,
            },
        )
        self.assertEqual(
            [profile["profile_id"] for profile in plan["calibration_profiles"]],
            ["strong-authorization-oracle-v1", "weak-boolean-proxy-v1"],
        )
        self.assertEqual(
            plan["calibration_profiles"][0]["selectors"],
            [
                "test_access.AccessTests.test_admin_is_allowed",
                "test_access.AccessTests.test_viewer_is_denied",
            ],
        )
        self.assertEqual(
            plan["calibration_profiles"][1]["selectors"],
            ["test_access.AccessTests.test_viewer_result_is_boolean"],
        )
        self.assertEqual(
            plan["reference_claim_checks"],
            [
                "test_hidden_claim.HiddenClaimTests.test_admin_is_allowed",
                "test_hidden_claim.HiddenClaimTests.test_viewer_is_denied",
            ],
        )
        self.assertTrue(
            all(
                profile["source_id"] == plan["source_scope"]["source_id"]
                and profile["operator_set_id"] == OPERATOR_SET_ID
                and profile["primary_denominator_eligible"] is False
                for profile in plan["calibration_profiles"]
            )
        )

    def test_known_challenge_mutant_is_not_generic_operator_evidence(self) -> None:
        plan = build_claim_scoped_mutation_plan()
        known = plan["known_challenge_control"]

        self.assertEqual(known["mutant_id"], "nonempty-role-boolean-v1")
        self.assertEqual(known["origin"], "PR-34-fixed-control")
        self.assertFalse(known["included_in_generic_operator_set"])
        self.assertFalse(known["counts_toward_operator_generalization"])
        self.assertNotIn(
            known["mutant_id"],
            [item["operator_id"] for item in plan["operator_set"]["operators"]],
        )

    def test_catalog_retains_generated_duplicate_not_applicable_and_invalid_records(self) -> None:
        plan = build_claim_scoped_mutation_plan()
        catalog = build_claim_scoped_mutant_catalog(plan)

        self.assertEqual(set(catalog), _CATALOG_FIELDS)
        self.assertEqual(catalog["schema_version"], CATALOG_SCHEMA_VERSION)
        self.assertEqual(catalog["plan_id"], PLAN_ID)
        self.assertEqual(catalog["plan_sha256"], plan["plan_sha256"])
        self.assertEqual(catalog["partition"], "development")
        self.assertEqual(catalog["target"]["target_cardinality"], 1)
        self.assertEqual(
            [record["operator_id"] for record in catalog["mutants"]],
            [*_GENERIC_OPERATOR_IDS, *_CONTROL_OPERATOR_IDS],
        )
        self.assertEqual(
            [record["status"] for record in catalog["mutants"]],
            _EXPECTED_STATUSES,
        )
        self.assertEqual(
            catalog["summary"],
            {
                "total_records": 6,
                "generic_operator_records": 3,
                "generation_control_records": 3,
                "generated": 3,
                "duplicate": 1,
                "invalid": 1,
                "not_applicable": 1,
                "score": None,
            },
        )

        generated = catalog["mutants"][:3]
        self.assertEqual(len({item["mutant_id"] for item in generated}), 3)
        self.assertEqual(
            len({item["mutated_source_sha256"] for item in generated}),
            3,
        )
        self.assertTrue(all(item["compile_valid"] for item in generated))
        self.assertTrue(all(item["source_body_published"] is False for item in generated))

        duplicate = catalog["mutants"][3]
        self.assertEqual(duplicate["duplicate_of"], generated[0]["mutant_id"])
        self.assertEqual(
            duplicate["mutated_source_sha256"],
            generated[0]["mutated_source_sha256"],
        )
        self.assertIs(duplicate["compile_valid"], True)

        not_applicable = catalog["mutants"][4]
        self.assertIsNone(not_applicable["mutated_source_sha256"])
        self.assertIsNone(not_applicable["mutated_ast_sha256"])
        self.assertIsNone(not_applicable["compile_valid"])
        self.assertIsNone(not_applicable["duplicate_of"])

        invalid = catalog["mutants"][5]
        self.assertIsNotNone(invalid["mutated_source_sha256"])
        self.assertIsNone(invalid["mutated_ast_sha256"])
        self.assertIs(invalid["compile_valid"], False)
        self.assertEqual(invalid["diagnostic_code"], "compile_error")

        self.assertEqual(
            catalog["known_challenge_control"]["mutant_id"],
            "nonempty-role-boolean-v1",
        )
        self.assertFalse(
            catalog["known_challenge_control"][
                "included_in_generic_operator_set"
            ]
        )

        valid, errors = verify_claim_scoped_mutant_catalog_document(catalog, plan)
        self.assertTrue(valid, errors)

    def test_catalog_is_reproducible_across_repeated_generation(self) -> None:
        plan = build_claim_scoped_mutation_plan()
        first = build_claim_scoped_mutant_catalog(plan)
        second = build_claim_scoped_mutant_catalog(plan)
        self.assertEqual(first, second)
        self.assertEqual(canonical_json(first), canonical_json(second))

    def test_recomputed_digests_cannot_hide_plan_or_catalog_drift(self) -> None:
        plan = build_claim_scoped_mutation_plan()
        for mutator, expected in (
            (
                lambda document: document["source_scope"].__setitem__(
                    "symbol", "is_owner"
                ),
                "symbol",
            ),
            (
                lambda document: document["operator_set"]["operators"][0].__setitem__(
                    "operator_id", "replacement"
                ),
                "operator_id",
            ),
            (
                lambda document: document["calibration_profiles"][0][
                    "selectors"
                ].append("test_access.AccessTests.test_missing_role_is_denied"),
                "selectors",
            ),
            (
                lambda document: document.__setitem__("execution_authorized", True),
                "execution_authorized",
            ),
            (
                lambda document: document.__setitem__(
                    "primary_denominator_eligible", True
                ),
                "primary_denominator_eligible",
            ),
        ):
            with self.subTest(expected=expected):
                tampered = deepcopy(plan)
                mutator(tampered)
                tampered["plan_sha256"] = compute_mutation_plan_sha256(tampered)
                valid, errors = verify_claim_scoped_mutation_plan_document(tampered)
                self.assertFalse(valid)
                self.assertTrue(any(expected in error for error in errors), errors)

        catalog = build_claim_scoped_mutant_catalog(plan)
        for mutator, expected in (
            (
                lambda document: document["mutants"][0].__setitem__(
                    "operator_id", "substituted"
                ),
                "operator_id",
            ),
            (
                lambda document: document["mutants"][3].__setitem__(
                    "duplicate_of", "f" * 64
                ),
                "duplicate_of",
            ),
            (
                lambda document: document["mutants"][4].__setitem__(
                    "status", "generated"
                ),
                "status",
            ),
            (
                lambda document: document["summary"].__setitem__("score", 1.0),
                "score",
            ),
        ):
            with self.subTest(expected=expected):
                tampered = deepcopy(catalog)
                mutator(tampered)
                tampered["catalog_sha256"] = compute_mutant_catalog_sha256(
                    tampered
                )
                valid, errors = verify_claim_scoped_mutant_catalog_document(
                    tampered,
                    plan,
                )
                self.assertFalse(valid)
                self.assertTrue(any(expected in error for error in errors), errors)

    def test_committed_plan_and_schemas_match_public_contract(self) -> None:
        plan = build_claim_scoped_mutation_plan()
        committed = json.loads(_PLAN_PATH.read_text(encoding="utf-8"))
        self.assertEqual(committed, plan)

        for name, fields, version in (
            (
                "claim-scoped-mutation-plan.schema.json",
                _PLAN_FIELDS,
                PLAN_SCHEMA_VERSION,
            ),
            (
                "claim-scoped-mutant-catalog.schema.json",
                _CATALOG_FIELDS,
                CATALOG_SCHEMA_VERSION,
            ),
        ):
            schema = json.loads((_SCHEMA_DIR / name).read_text(encoding="utf-8"))
            self.assertEqual(
                schema["$schema"],
                "https://json-schema.org/draft/2020-12/schema",
            )
            self.assertIs(schema["additionalProperties"], False)
            self.assertEqual(set(schema["required"]), fields)
            self.assertEqual(set(schema["properties"]), fields)
            self.assertEqual(schema["properties"]["schema_version"]["const"], version)
            for node in _walk(schema):
                if isinstance(node, dict) and node.get("type") == "object":
                    self.assertIs(node.get("additionalProperties"), False, node)

    def test_public_artifacts_exclude_source_bodies_and_private_material(self) -> None:
        plan = build_claim_scoped_mutation_plan()
        catalog = build_claim_scoped_mutant_catalog(plan)
        encoded = json.dumps({"plan": plan, "catalog": catalog}, sort_keys=True)
        for prohibited in (
            "def is_admin",
            "return user.get",
            "/tmp/",
            "\\Temp\\",
            "Traceback (most recent call last)",
            '"stdout"',
            '"stderr"',
            "credential",
            "environment_values",
            "private_endpoint",
        ):
            self.assertNotIn(prohibited, encoded)


if __name__ == "__main__":
    unittest.main()
