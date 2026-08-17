from __future__ import annotations

from pathlib import Path
import unittest

from deltawitness.reporting import load_report


_ROOT = Path(__file__).resolve().parents[1]
_PLAN_PATH = (
    _ROOT
    / "research"
    / "DW-001"
    / "interaction-witness-lattice-plan.v1.json"
)
_CATALOG_PATH = (
    _ROOT
    / "research"
    / "DW-001"
    / "interaction-witness-lattice-mutant-catalog.v1.json"
)
_PLAN_SCHEMA_PATH = (
    _ROOT
    / "research"
    / "DW-001"
    / "schema"
    / "interaction-witness-lattice-plan.schema.json"
)
_CATALOG_SCHEMA_PATH = (
    _ROOT
    / "research"
    / "DW-001"
    / "schema"
    / "interaction-witness-lattice-mutant-catalog.schema.json"
)


class DW001InteractionLatticeSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = load_report(_PLAN_PATH)
        cls.catalog = load_report(_CATALOG_PATH)
        cls.plan_schema = load_report(_PLAN_SCHEMA_PATH)
        cls.catalog_schema = load_report(_CATALOG_SCHEMA_PATH)

    def test_schema_roots_are_closed_and_cover_every_artifact_field(self) -> None:
        for artifact, schema in (
            (self.plan, self.plan_schema),
            (self.catalog, self.catalog_schema),
        ):
            with self.subTest(schema=schema["$id"]):
                self.assertEqual(
                    schema["$schema"],
                    "https://json-schema.org/draft/2020-12/schema",
                )
                self.assertEqual(schema["type"], "object")
                self.assertFalse(schema["additionalProperties"])
                self.assertEqual(set(schema["required"]), set(artifact))
                self.assertEqual(set(schema["properties"]), set(artifact))

    def test_every_normative_object_definition_is_closed(self) -> None:
        for schema, names in (
            (
                self.plan_schema,
                (
                    "adapter",
                    "priorEvidence",
                    "sourceScope",
                    "testScope",
                    "truthEntry",
                    "target",
                    "pathHypothesis",
                    "branchStat",
                    "structuralHypotheses",
                    "pathPartitionContract",
                    "pathMultisetRecord",
                    "pathMultiset",
                    "profile",
                    "operator",
                    "operatorSet",
                    "generationControl",
                    "profileOutcome",
                    "mutationMatrixRow",
                    "futureExecutionContract",
                    "policy",
                ),
            ),
            (
                self.catalog_schema,
                ("source", "test", "target", "mutant", "summary"),
            ),
        ):
            for name in names:
                with self.subTest(schema=schema["$id"], definition=name):
                    definition = schema["$defs"][name]
                    self.assertEqual(definition["type"], "object")
                    self.assertFalse(definition["additionalProperties"])
                    self.assertTrue(definition["required"])

    def test_plan_schema_freezes_design_only_and_non_policy_fields(self) -> None:
        properties = self.plan_schema["properties"]
        self.assertEqual(properties["execution_authorized"], {"const": False})
        self.assertEqual(properties["holdout_selected"], {"const": False})
        self.assertEqual(
            properties["primary_denominator_eligible"],
            {"const": False},
        )
        future = self.plan_schema["$defs"]["futureExecutionContract"][
            "properties"
        ]
        self.assertEqual(
            future["execution_status"],
            {"const": "not_implemented"},
        )
        self.assertEqual(future["score"], {"const": None})
        self.assertEqual(future["universal_threshold"], {"const": None})
        self.assertEqual(
            future["merge_blocker_authorized"],
            {"const": False},
        )
        policy = self.plan_schema["$defs"]["policy"]["properties"]
        self.assertEqual(policy["quality_score"], {"const": None})
        self.assertEqual(
            policy["scientific_novelty_claim_allowed"],
            {"const": False},
        )

    def test_schema_cardinalities_match_the_preregistration(self) -> None:
        plan_properties = self.plan_schema["properties"]
        self.assertEqual(
            (
                plan_properties["truth_table"]["minItems"],
                plan_properties["truth_table"]["maxItems"],
            ),
            (4, 4),
        )
        self.assertEqual(
            (
                plan_properties["profiles"]["minItems"],
                plan_properties["profiles"]["maxItems"],
            ),
            (5, 5),
        )
        self.assertEqual(
            (
                plan_properties["generation_controls"]["minItems"],
                plan_properties["generation_controls"]["maxItems"],
            ),
            (3, 3),
        )
        catalog_mutants = self.catalog_schema["properties"]["mutants"]
        self.assertEqual(
            (catalog_mutants["minItems"], catalog_mutants["maxItems"]),
            (8, 8),
        )

    def test_catalog_schema_retains_non_executed_generation_statuses(self) -> None:
        mutant = self.catalog_schema["$defs"]["mutant"]["properties"]
        self.assertEqual(
            mutant["status"]["enum"],
            ["generated", "duplicate", "not_applicable", "invalid"],
        )
        self.assertNotIn("outcome", mutant)
        self.assertNotIn("killed", mutant)
        summary = self.catalog_schema["$defs"]["summary"]["properties"]
        self.assertEqual(summary["generated"], {"const": 5})
        self.assertEqual(summary["duplicate"], {"const": 1})
        self.assertEqual(summary["invalid"], {"const": 1})
        self.assertEqual(summary["not_applicable"], {"const": 1})
        self.assertEqual(summary["score"], {"const": None})


if __name__ == "__main__":
    unittest.main()
