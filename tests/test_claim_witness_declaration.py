from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from deltawitness.claim_witness import (
    ADAPTER_ID,
    ADAPTER_VERSION,
    AGGREGATE_RULE,
    DECLARATION_SCHEMA_VERSION,
    build_claim_witness_declaration,
    canonical_unittest_selector_command,
    compute_claim_witness_declaration_sha256,
    verify_claim_witness_declaration_document,
)
from deltawitness.reporting import canonical_json
from claim_witness_support import CLAIM_ID, COLLATERAL_SELECTOR, UNRELATED_SELECTOR


_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "DW-001"
    / "schema"
    / "claim-witness-declaration.schema.json"
)


class ClaimWitnessDeclarationTests(unittest.TestCase):
    def test_builder_is_deterministic_and_derives_commands(self) -> None:
        selectors = [UNRELATED_SELECTOR, COLLATERAL_SELECTOR]

        first = build_claim_witness_declaration(
            spec_sha256="a" * 64,
            claim_id=CLAIM_ID,
            selectors=selectors,
        )
        second = build_claim_witness_declaration(
            spec_sha256="a" * 64,
            claim_id=CLAIM_ID,
            selectors=tuple(selectors),
        )

        self.assertEqual(first, second)
        self.assertEqual(canonical_json(first), canonical_json(second))
        self.assertEqual(first["schema_version"], DECLARATION_SCHEMA_VERSION)
        self.assertEqual(first["adapter"], {"id": ADAPTER_ID, "version": ADAPTER_VERSION})
        self.assertEqual(first["aggregate_rule"], AGGREGATE_RULE)
        self.assertEqual(first["selectors"], selectors)
        self.assertEqual(
            first["selector_commands"],
            [
                {
                    "selector": selector,
                    "command": canonical_unittest_selector_command(selector),
                }
                for selector in selectors
            ],
        )
        valid, errors = verify_claim_witness_declaration_document(first)
        self.assertTrue(valid, errors)

    def test_duplicate_or_reordered_selector_command_relation_is_rejected(self) -> None:
        with self.assertRaises(Exception):
            build_claim_witness_declaration(
                spec_sha256="a" * 64,
                claim_id=CLAIM_ID,
                selectors=[UNRELATED_SELECTOR, UNRELATED_SELECTOR],
            )

        declaration = build_claim_witness_declaration(
            spec_sha256="a" * 64,
            claim_id=CLAIM_ID,
            selectors=[UNRELATED_SELECTOR, COLLATERAL_SELECTOR],
        )
        tampered = deepcopy(declaration)
        tampered["selector_commands"].reverse()
        tampered["declaration_sha256"] = compute_claim_witness_declaration_sha256(tampered)

        valid, errors = verify_claim_witness_declaration_document(tampered)
        self.assertFalse(valid)
        self.assertTrue(any("selector_commands" in error for error in errors), errors)

    def test_free_form_command_drift_is_rejected_after_digest_recomputation(self) -> None:
        declaration = build_claim_witness_declaration(
            spec_sha256="a" * 64,
            claim_id=CLAIM_ID,
            selectors=[UNRELATED_SELECTOR],
        )
        tampered = deepcopy(declaration)
        tampered["selector_commands"][0]["command"] = ["python", "-m", "unittest"]
        tampered["declaration_sha256"] = compute_claim_witness_declaration_sha256(tampered)

        valid, errors = verify_claim_witness_declaration_document(tampered)
        self.assertFalse(valid)
        self.assertTrue(any("command" in error for error in errors), errors)

    def test_unsafe_or_ambiguous_selectors_are_rejected(self) -> None:
        for selector in (
            "test_access.AccessTests",
            "../test_access.AccessTests.test_viewer",
            "test_access/AccessTests/test_viewer",
            "test_access.AccessTests.test-viewer",
            "test_access.AccessTests.test_viewer\x00extra",
        ):
            with self.subTest(selector=selector):
                with self.assertRaises(Exception):
                    build_claim_witness_declaration(
                        spec_sha256="a" * 64,
                        claim_id=CLAIM_ID,
                        selectors=[selector],
                    )

    def test_schema_is_strict_and_matches_emitted_root(self) -> None:
        declaration = build_claim_witness_declaration(
            spec_sha256="a" * 64,
            claim_id=CLAIM_ID,
            selectors=[UNRELATED_SELECTOR],
        )
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))

        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertIs(schema["additionalProperties"], False)
        self.assertEqual(set(schema["required"]), set(declaration))
        self.assertEqual(set(schema["properties"]), set(declaration))
        self.assertEqual(
            schema["properties"]["schema_version"]["const"],
            DECLARATION_SCHEMA_VERSION,
        )


if __name__ == "__main__":
    unittest.main()
