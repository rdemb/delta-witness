from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from deltawitness.dw001_scenarios import (
    SUPPORTED_FAMILIES,
    build_fixture_descriptor,
    materialize_synthetic_fixture,
)


_SCHEMA_DIR = Path(__file__).resolve().parents[1] / "research" / "DW-001" / "schema"
_SCHEMA_NAMES = (
    "fixture-descriptor.schema.json",
    "fixture-identity.schema.json",
)


def _walk(value: object):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _resolve_pointer(document: object, reference: str) -> object:
    if not reference.startswith("#/"):
        raise AssertionError(f"Only local JSON pointers are allowed: {reference}")
    current = document
    for raw_part in reference[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or part not in current:
            raise AssertionError(f"Unresolved local JSON pointer: {reference}")
        current = current[part]
    return current


class DW001ScenarioSchemaTests(unittest.TestCase):
    def _schemas(self) -> dict[str, dict[str, object]]:
        documents: dict[str, dict[str, object]] = {}
        for name in _SCHEMA_NAMES:
            path = _SCHEMA_DIR / name
            document = json.loads(path.read_text(encoding="utf-8"))
            self.assertIsInstance(document, dict)
            documents[name] = document
        return documents

    def test_schemas_use_strict_local_object_boundaries(self) -> None:
        for name, document in self._schemas().items():
            with self.subTest(schema=name):
                self.assertEqual(
                    document["$schema"],
                    "https://json-schema.org/draft/2020-12/schema",
                )
                self.assertFalse(document["additionalProperties"])
                for node in _walk(document):
                    if isinstance(node, dict) and node.get("type") == "object":
                        self.assertIs(
                            node.get("additionalProperties"),
                            False,
                            f"{name} contains an open object boundary: {node}",
                        )
                    if isinstance(node, dict) and "$ref" in node:
                        reference = node["$ref"]
                        self.assertIsInstance(reference, str)
                        _resolve_pointer(document, reference)

    def test_schema_family_enums_match_generator_contract(self) -> None:
        expected = list(SUPPORTED_FAMILIES)
        for name, document in self._schemas().items():
            with self.subTest(schema=name):
                actual = document["properties"]["family_id"]["enum"]
                self.assertEqual(actual, expected)

    def test_schema_root_fields_match_emitted_artifacts(self) -> None:
        schemas = self._schemas()
        descriptor = build_fixture_descriptor(
            scenario_id="generator-schema-001",
            family_id="valid-discriminating-regression",
        )
        with tempfile.TemporaryDirectory() as directory:
            identity = materialize_synthetic_fixture(descriptor, Path(directory))

        self.assertEqual(
            set(descriptor),
            set(schemas["fixture-descriptor.schema.json"]["required"]),
        )
        self.assertEqual(
            set(descriptor),
            set(schemas["fixture-descriptor.schema.json"]["properties"]),
        )
        self.assertEqual(
            set(identity),
            set(schemas["fixture-identity.schema.json"]["required"]),
        )
        self.assertEqual(
            set(identity),
            set(schemas["fixture-identity.schema.json"]["properties"]),
        )


if __name__ == "__main__":
    unittest.main()
