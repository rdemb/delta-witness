from __future__ import annotations

from pathlib import Path
import unittest

from deltawitness.reporting import load_report


_ROOT = Path(__file__).resolve().parents[2]
_SCHEMA_PATH = (
    _ROOT
    / "research"
    / "DW-001"
    / "schema"
    / "coveragepy-baseline-result.schema.json"
)
_RESULT_PATH = (
    _ROOT
    / "research"
    / "DW-001"
    / "coveragepy-baseline-result.v1.json"
)


class CoveragePyResultSchemaTests(unittest.TestCase):
    def test_schema_root_exactly_covers_the_frozen_result(self) -> None:
        schema = load_report(_SCHEMA_PATH)
        result = load_report(_RESULT_PATH)

        self.assertEqual(
            schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )
        self.assertEqual(schema["type"], "object")
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["required"]), set(result))
        self.assertEqual(set(schema["properties"]), set(result))
        self.assertEqual(
            schema["properties"]["schema_version"]["const"],
            result["schema_version"],
        )
        self.assertEqual(
            schema["properties"]["result_id"]["const"],
            result["result_id"],
        )
        self.assertEqual(
            schema["$defs"]["policy"]["properties"],
            {
                "quality_score": {"const": None},
                "headline_score": {"const": None},
                "universal_threshold": {"const": None},
                "merge_blocker_authorized": {"const": False},
                "ecological_inference_allowed": {"const": False},
                "holdout_selected": {"const": False},
                "primary_denominator_eligible": {"const": False},
                "coverage_superiority_claim_allowed": {"const": False},
                "mutation_superiority_claim_allowed": {"const": False},
            },
        )

    def test_schema_requires_exact_nested_objects_and_typed_statuses(self) -> None:
        schema = load_report(_SCHEMA_PATH)
        definitions = schema["$defs"]

        for name in (
            "adapter",
            "distributionManifest",
            "rootConfiguration",
            "source",
            "coverageReceipt",
            "selector",
            "profile",
            "comparison",
            "analysis",
            "policy",
        ):
            with self.subTest(definition=name):
                self.assertFalse(definitions[name]["additionalProperties"])
                self.assertTrue(definitions[name]["required"])

        self.assertEqual(
            definitions["coverageReceipt"]["properties"][
                "measurement_status"
            ]["enum"],
            ["complete", "indeterminate"],
        )
        self.assertEqual(
            definitions["analysis"]["properties"]["status"]["enum"],
            ["expected", "unexpected", "indeterminate"],
        )
        self.assertEqual(
            definitions["selector"]["properties"]["coverage_status"][
                "enum"
            ],
            ["complete", "candidate_invalid", "indeterminate"],
        )


if __name__ == "__main__":
    unittest.main()
