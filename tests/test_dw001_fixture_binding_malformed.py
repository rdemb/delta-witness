from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from deltawitness.dw001_fixture_binding import (
    build_fixture_manifest_binding,
    compute_fixture_manifest_binding_sha256,
    verify_fixture_manifest_binding_document,
)
from dw001_binding_support import SCHEMA_PATH, artifacts


def _walk(value: object):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


class DW001FixtureManifestBindingMalformedTests(unittest.TestCase):
    def setUp(self) -> None:
        self.descriptor, self.identity, self.manifest = artifacts(
            scenario_id="fixture-binding-malformed-001"
        )
        self.binding = build_fixture_manifest_binding(
            self.descriptor,
            self.identity,
            self.manifest,
        )

    def _verify_tampered(self, tampered: dict[str, object]) -> tuple[str, ...]:
        tampered["binding_sha256"] = compute_fixture_manifest_binding_sha256(
            tampered
        )
        valid, errors = verify_fixture_manifest_binding_document(
            tampered,
            self.descriptor,
            self.identity,
            self.manifest,
        )
        self.assertFalse(valid)
        self.assertTrue(errors)
        return errors

    def test_unhashable_control_role_fails_closed(self) -> None:
        tampered = deepcopy(self.binding)
        tampered["control_role"] = []

        errors = self._verify_tampered(tampered)

        self.assertTrue(any("control_role" in error for error in errors), errors)

    def test_unhashable_state_observation_fails_closed(self) -> None:
        tampered = deepcopy(self.binding)
        tampered["expected_states"][0]["expected_observed"] = []

        errors = self._verify_tampered(tampered)

        self.assertTrue(any("expected_observed" in error for error in errors), errors)

    def test_unhashable_method_decision_fails_closed(self) -> None:
        tampered = deepcopy(self.binding)
        tampered["expected_methods"][0]["decision"] = []

        errors = self._verify_tampered(tampered)

        self.assertTrue(any("decision" in error for error in errors), errors)

    def test_schema_has_no_open_object_boundary(self) -> None:
        document = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

        for node in _walk(document):
            if isinstance(node, dict) and node.get("type") == "object":
                self.assertIs(
                    node.get("additionalProperties"),
                    False,
                    f"binding schema contains an open object boundary: {node}",
                )

    def test_schema_uses_canonical_tuple_order(self) -> None:
        document = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        state_items = document["properties"]["expected_states"]["prefixItems"]
        method_items = document["properties"]["expected_methods"]["prefixItems"]

        self.assertEqual(
            [item["properties"]["state"]["const"] for item in state_items],
            [
                "base_base",
                "base_candidate",
                "candidate_base",
                "candidate_candidate",
            ],
        )
        self.assertEqual(
            [item["properties"]["method_id"]["const"] for item in method_items],
            ["M0_FINAL", "M1_F2P", "M2_F2P_P2P", "M3_FOUR_STATE"],
        )


if __name__ == "__main__":
    unittest.main()
