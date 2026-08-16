from __future__ import annotations

from copy import deepcopy
import json
import unittest

from deltawitness.dw001_contracts import SCENARIO_SCHEMA_VERSION
from deltawitness.dw001_fixture_binding import (
    BINDING_SCHEMA_VERSION,
    build_fixture_manifest_binding,
    verify_fixture_manifest_binding_document,
)
from deltawitness.dw001_scenarios import (
    FIXTURE_DESCRIPTOR_SCHEMA_VERSION,
    FIXTURE_IDENTITY_SCHEMA_VERSION,
    SUPPORTED_FAMILIES,
)
from deltawitness.reporting import canonical_json
from dw001_binding_support import SCHEMA_PATH, artifacts


class DW001FixtureManifestBindingCoreTests(unittest.TestCase):
    def test_repeated_construction_is_byte_identical(self) -> None:
        descriptor, identity, manifest = artifacts()

        first = build_fixture_manifest_binding(descriptor, identity, manifest)
        second = build_fixture_manifest_binding(descriptor, identity, manifest)

        self.assertEqual(first, second)
        self.assertEqual(canonical_json(first), canonical_json(second))
        self.assertEqual(first["schema_version"], BINDING_SCHEMA_VERSION)
        valid, errors = verify_fixture_manifest_binding_document(
            first,
            descriptor,
            identity,
            manifest,
        )
        self.assertTrue(valid, errors)

    def test_all_supported_families_and_observer_arms_bind(self) -> None:
        for family_id in SUPPORTED_FAMILIES:
            for observer in ("exit-code-v1", "outcome-receipt-v1"):
                with self.subTest(family=family_id, observer=observer):
                    descriptor, identity, manifest = artifacts(
                        scenario_id=f"fixture-binding-{family_id}-{observer}",
                        family_id=family_id,
                        observer=observer,
                    )
                    binding = build_fixture_manifest_binding(
                        descriptor,
                        identity,
                        manifest,
                    )
                    valid, errors = verify_fixture_manifest_binding_document(
                        binding,
                        descriptor,
                        identity,
                        manifest,
                    )
                    self.assertTrue(valid, errors)

    def test_development_manifest_remains_denominator_ineligible(self) -> None:
        descriptor, identity, manifest = artifacts(partition="development")
        before = deepcopy(manifest)

        binding = build_fixture_manifest_binding(descriptor, identity, manifest)
        valid, errors = verify_fixture_manifest_binding_document(
            binding,
            descriptor,
            identity,
            manifest,
        )

        self.assertTrue(valid, errors)
        self.assertEqual(manifest, before)
        self.assertTrue(
            all(
                method["primary_denominator_eligible"] is False
                for method in manifest["ground_truth"]["methods"]
            )
        )
        self.assertIn("partition", binding["relation_scope"]["manifest_owned_fields"])
        self.assertIn("review", binding["relation_scope"]["manifest_owned_fields"])

    def test_binding_schema_is_strict_and_matches_emitted_root(self) -> None:
        descriptor, identity, manifest = artifacts()
        binding = build_fixture_manifest_binding(descriptor, identity, manifest)
        document = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

        self.assertEqual(
            document["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )
        self.assertFalse(document["additionalProperties"])
        self.assertEqual(set(binding), set(document["required"]))
        self.assertEqual(set(binding), set(document["properties"]))
        self.assertEqual(
            document["properties"]["schema_version"]["const"],
            BINDING_SCHEMA_VERSION,
        )
        self.assertEqual(
            document["properties"]["sources"]["properties"]["descriptor"]
            ["properties"]["schema_version"]["const"],
            FIXTURE_DESCRIPTOR_SCHEMA_VERSION,
        )
        self.assertEqual(
            document["properties"]["sources"]["properties"]["fixture_identity"]
            ["properties"]["schema_version"]["const"],
            FIXTURE_IDENTITY_SCHEMA_VERSION,
        )
        self.assertEqual(
            document["properties"]["sources"]["properties"]["scenario_manifest"]
            ["properties"]["schema_version"]["const"],
            SCENARIO_SCHEMA_VERSION,
        )


if __name__ == "__main__":
    unittest.main()
