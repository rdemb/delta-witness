from __future__ import annotations

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
