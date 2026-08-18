from __future__ import annotations

from pathlib import Path
import unittest

from deltawitness.reporting import load_report


_ROOT = Path(__file__).resolve().parents[1]
_SCHEMA_PATH = (
    _ROOT
    / "research"
    / "DW-001"
    / "schema"
    / "interaction-witness-lattice-result.schema.json"
)


class DW001InteractionLatticeResultSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = load_report(_SCHEMA_PATH)

    def test_root_is_closed_and_covers_the_runtime_result_contract(self) -> None:
        self.assertEqual(
            self.schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )
        self.assertEqual(self.schema["type"], "object")
        self.assertFalse(self.schema["additionalProperties"])
        self.assertEqual(
            set(self.schema["required"]),
            set(self.schema["properties"]),
        )
        self.assertEqual(
            self.schema["properties"]["schema_version"]["const"],
            "deltawitness.dw001-interaction-witness-lattice-result.v1",
        )
        self.assertEqual(
            self.schema["properties"]["result_id"]["const"],
            "DW-001-INTERACTION-WITNESS-LATTICE-RESULT-V1",
        )

    def test_normative_objects_are_closed(self) -> None:
        for name in (
            "runtime",
            "configuration",
            "source",
            "typedCounts",
            "producer",
            "pathShape",
            "candidateCost",
            "candidateSelector",
            "pathRecord",
            "pathMultisetRecord",
            "pathMultiset",
            "profileCost",
            "profile",
            "mutantSelectorCost",
            "mutantSelector",
            "mutantProfileOutcome",
            "mutantCost",
            "mutant",
            "summary",
            "comparison",
            "analysis",
            "policy",
            "rootCost",
        ):
            with self.subTest(definition=name):
                definition = self.schema["$defs"][name]
                self.assertEqual(definition["type"], "object")
                self.assertFalse(definition["additionalProperties"])
                self.assertTrue(definition["required"])

    def test_complete_table_cardinalities_and_command_count_are_fixed(self) -> None:
        properties = self.schema["properties"]
        self.assertEqual(
            (
                properties["candidate_selectors"]["minItems"],
                properties["candidate_selectors"]["maxItems"],
            ),
            (4, 4),
        )
        self.assertEqual(
            (
                properties["profiles"]["minItems"],
                properties["profiles"]["maxItems"],
            ),
            (5, 5),
        )
        self.assertEqual(
            (
                properties["mutants"]["minItems"],
                properties["mutants"]["maxItems"],
            ),
            (5, 5),
        )
        mutant = self.schema["$defs"]["mutant"]["properties"]
        self.assertEqual(
            (
                mutant["selectors"]["minItems"],
                mutant["selectors"]["maxItems"],
            ),
            (4, 4),
        )
        self.assertEqual(
            (
                mutant["profile_outcomes"]["minItems"],
                mutant["profile_outcomes"]["maxItems"],
            ),
            (5, 5),
        )
        summary = self.schema["$defs"]["summary"]["properties"]
        self.assertEqual(summary["selector_command_count"], {"const": 24})
        self.assertEqual(summary["mutation_score"], {"const": None})

    def test_expected_unexpected_indeterminate_and_non_policy_boundaries_are_typed(self) -> None:
        analysis = self.schema["$defs"]["analysis"]["properties"]
        self.assertEqual(
            analysis["status"]["enum"],
            ["expected", "unexpected", "indeterminate"],
        )
        candidate = self.schema["$defs"]["candidateSelector"]["properties"]
        self.assertEqual(
            candidate["coverage_status"]["enum"],
            ["complete", "indeterminate"],
        )
        mutant_selector = self.schema["$defs"]["mutantSelector"][
            "properties"
        ]
        self.assertEqual(
            mutant_selector["status"]["enum"],
            ["complete", "indeterminate"],
        )
        policy = self.schema["$defs"]["policy"]["properties"]
        self.assertEqual(policy["quality_score"], {"const": None})
        self.assertEqual(policy["universal_threshold"], {"const": None})
        self.assertEqual(
            policy["merge_blocker_authorized"],
            {"const": False},
        )
        self.assertEqual(
            policy["scientific_novelty_claim_allowed"],
            {"const": False},
        )

    def test_coverage_receipt_and_distribution_reference_the_reviewed_baseline_schema(self) -> None:
        self.assertEqual(
            self.schema["properties"]["distribution"]["$ref"],
            "coveragepy-baseline-result.schema.json#/$defs/distributionManifest",
        )
        candidate = self.schema["$defs"]["candidateSelector"]["properties"]
        self.assertEqual(
            candidate["coverage_receipt"]["oneOf"][0]["$ref"],
            "coveragepy-baseline-result.schema.json#/$defs/coverageReceipt",
        )


if __name__ == "__main__":
    unittest.main()
