from __future__ import annotations

from pathlib import Path
import unittest

from deltawitness.reporting import load_report


_ROOT = Path(__file__).resolve().parents[1]
_DW001 = _ROOT / "research" / "DW-001"
_CHECKPOINT_PATH = (
    _DW001 / "interaction-witness-lattice-result-checkpoint.v1.json"
)
_SCHEMA_PATH = (
    _DW001
    / "schema"
    / "interaction-witness-lattice-result-checkpoint.schema.json"
)


class DW001InteractionLatticeCheckpointSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.checkpoint = load_report(_CHECKPOINT_PATH)
        cls.schema = load_report(_SCHEMA_PATH)

    def test_schema_root_is_closed_and_matches_checkpoint_fields(self) -> None:
        self.assertEqual(
            self.schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )
        self.assertEqual(self.schema["type"], "object")
        self.assertFalse(self.schema["additionalProperties"])
        self.assertEqual(set(self.schema["required"]), set(self.checkpoint))
        self.assertEqual(set(self.schema["properties"]), set(self.checkpoint))
        self.assertEqual(
            self.schema["properties"]["semantic_sha256"]["const"],
            self.checkpoint["semantic_sha256"],
        )
        self.assertEqual(
            self.schema["properties"]["checkpoint_sha256"]["const"],
            self.checkpoint["checkpoint_sha256"],
        )

    def test_normative_object_definitions_are_closed(self) -> None:
        for name in (
            "preregistration",
            "source",
            "candidateSelector",
            "profileInvariants",
            "profile",
            "selectorOutcome",
            "profileOutcome",
            "mutant",
            "summary",
            "comparison",
            "analysis",
            "policy",
            "referenceReport",
        ):
            with self.subTest(definition=name):
                definition = self.schema["$defs"][name]
                self.assertEqual(definition["type"], "object")
                self.assertFalse(definition["additionalProperties"])
                self.assertTrue(definition["required"])

    def test_schema_cardinalities_preserve_complete_tables(self) -> None:
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
                mutant["selector_outcomes"]["minItems"],
                mutant["selector_outcomes"]["maxItems"],
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

    def test_schema_freezes_non_policy_and_diagnostic_boundaries(self) -> None:
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
        reference = self.schema["$defs"]["referenceReport"]["properties"]
        self.assertEqual(reference["diagnostic_only"], {"const": True})
        self.assertEqual(
            self.schema["$defs"]["summary"]["properties"][
                "mutation_score"
            ],
            {"const": None},
        )


if __name__ == "__main__":
    unittest.main()
