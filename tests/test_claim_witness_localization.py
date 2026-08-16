from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from deltawitness.claim_witness import (
    LOCALIZATION_SCHEMA_VERSION,
    build_claim_witness_declaration,
    compute_claim_witness_localization_report_sha256,
    compute_claim_witness_localization_sha256,
    run_claim_witness_localization,
    verify_claim_witness_localization_document,
)
from claim_witness_support import (
    CLAIM_ID,
    COLLATERAL_SELECTOR,
    IMPORT_SELECTOR,
    MISSING_SELECTOR,
    UNRELATED_SELECTOR,
    VALID_SELECTOR,
    fixture_case,
)


_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "DW-001"
    / "schema"
    / "claim-witness-localization.schema.json"
)


def _declaration(config, selectors):
    return build_claim_witness_declaration(
        spec_sha256=config.digest_sha256,
        claim_id=CLAIM_ID,
        selectors=selectors,
    )


class ClaimWitnessLocalizationTests(unittest.TestCase):
    def test_valid_regression_selector_is_discriminating(self) -> None:
        with fixture_case("valid-discriminating-regression") as (
            repository,
            config,
            source_report,
            _,
        ):
            declaration = _declaration(config, [VALID_SELECTOR])
            localization = run_claim_witness_localization(
                repository,
                config,
                source_report,
                declaration,
            )

        self.assertEqual(localization["schema_version"], LOCALIZATION_SCHEMA_VERSION)
        self.assertEqual(localization["aggregate_status"], "supported")
        result = localization["selectors"][0]
        self.assertEqual(result["classification"], "discriminating")
        self.assertIsNone(result["diagnostic_code"])
        self.assertEqual(
            [(state["state"], state["observed"]) for state in result["states"]],
            [("base_candidate", "fail"), ("candidate_candidate", "pass")],
        )
        self.assertEqual(result["states"][0]["receipt_outcome"], "test_failure")
        self.assertEqual(result["states"][0]["receipt_counts"]["tests_run"], 1)
        self.assertEqual(result["states"][1]["receipt_counts"]["tests_run"], 1)
        valid, errors = verify_claim_witness_localization_document(
            localization,
            declaration,
            source_report,
        )
        self.assertTrue(valid, errors)

    def test_unrelated_claim_selector_is_non_discriminating_despite_supported_suite(self) -> None:
        with fixture_case("wrong-reason-unrelated-assertion") as (
            repository,
            config,
            source_report,
            _,
        ):
            self.assertTrue(source_report["complete"])
            self.assertTrue(source_report["supported"])
            declaration = _declaration(config, [UNRELATED_SELECTOR])
            localization = run_claim_witness_localization(
                repository,
                config,
                source_report,
                declaration,
            )

        result = localization["selectors"][0]
        self.assertEqual(result["classification"], "non_discriminating")
        self.assertEqual(localization["aggregate_status"], "unsupported")
        self.assertEqual(
            [state["observed"] for state in result["states"]],
            ["pass", "pass"],
        )
        self.assertTrue(all(state["receipt_counts"]["tests_run"] == 1 for state in result["states"]))

    def test_collateral_selector_can_discriminate_without_becoming_claim_witness(self) -> None:
        with fixture_case("wrong-reason-unrelated-assertion") as (
            repository,
            config,
            source_report,
            _,
        ):
            claim_declaration = _declaration(config, [UNRELATED_SELECTOR])
            collateral_declaration = _declaration(config, [COLLATERAL_SELECTOR])
            claim_localization = run_claim_witness_localization(
                repository,
                config,
                source_report,
                claim_declaration,
            )
            collateral_localization = run_claim_witness_localization(
                repository,
                config,
                source_report,
                collateral_declaration,
            )

        self.assertEqual(claim_localization["aggregate_status"], "unsupported")
        self.assertEqual(
            collateral_localization["selectors"][0]["classification"],
            "discriminating",
        )
        self.assertEqual(collateral_localization["aggregate_status"], "supported")
        self.assertNotEqual(
            claim_declaration["declaration_sha256"],
            collateral_declaration["declaration_sha256"],
        )

    def test_mixed_selector_set_uses_fixed_aggregate_rule(self) -> None:
        with fixture_case("wrong-reason-unrelated-assertion") as (
            repository,
            config,
            source_report,
            _,
        ):
            declaration = _declaration(config, [UNRELATED_SELECTOR, COLLATERAL_SELECTOR])
            localization = run_claim_witness_localization(
                repository,
                config,
                source_report,
                declaration,
            )

        self.assertEqual(
            [item["classification"] for item in localization["selectors"]],
            ["non_discriminating", "discriminating"],
        )
        self.assertEqual(localization["aggregate_status"], "supported")

    def test_import_error_and_missing_selector_remain_indeterminate(self) -> None:
        for family_id, selector in (
            ("wrong-reason-base-import-failure", IMPORT_SELECTOR),
            ("valid-discriminating-regression", MISSING_SELECTOR),
        ):
            with self.subTest(family=family_id, selector=selector):
                with fixture_case(family_id) as (
                    repository,
                    config,
                    source_report,
                    _,
                ):
                    declaration = _declaration(config, [selector])
                    localization = run_claim_witness_localization(
                        repository,
                        config,
                        source_report,
                        declaration,
                    )
                result = localization["selectors"][0]
                self.assertEqual(result["classification"], "indeterminate")
                self.assertEqual(localization["aggregate_status"], "indeterminate")
                self.assertIsNotNone(result["diagnostic_code"])
                self.assertEqual(result["states"][0]["observed"], "error")

    def test_declaration_claim_or_spec_substitution_fails_closed(self) -> None:
        with fixture_case("valid-discriminating-regression") as (
            repository,
            config,
            source_report,
            _,
        ):
            declaration = _declaration(config, [VALID_SELECTOR])
            localization = run_claim_witness_localization(
                repository,
                config,
                source_report,
                declaration,
            )

        for field, value in (("claim_id", "another-claim"), ("spec_sha256", "b" * 64)):
            with self.subTest(field=field):
                tampered_declaration = deepcopy(declaration)
                tampered_declaration[field] = value
                tampered_declaration["declaration_sha256"] = "a" * 64
                valid, errors = verify_claim_witness_localization_document(
                    localization,
                    tampered_declaration,
                    source_report,
                )
                self.assertFalse(valid)
                self.assertTrue(errors)

    def test_recomputed_localization_digests_cannot_hide_source_relation_mismatch(self) -> None:
        with fixture_case("valid-discriminating-regression") as (
            repository,
            config,
            source_report,
            _,
        ):
            declaration = _declaration(config, [VALID_SELECTOR])
            localization = run_claim_witness_localization(
                repository,
                config,
                source_report,
                declaration,
            )

        tampered = deepcopy(localization)
        tampered["source"]["source_report_sha256"] = "f" * 64
        tampered["localization_sha256"] = compute_claim_witness_localization_sha256(tampered)
        tampered["report_sha256"] = compute_claim_witness_localization_report_sha256(tampered)

        valid, errors = verify_claim_witness_localization_document(
            tampered,
            declaration,
            source_report,
        )
        self.assertFalse(valid)
        self.assertTrue(any("source" in error for error in errors), errors)

    def test_public_artifact_excludes_raw_output_and_schema_is_strict(self) -> None:
        with fixture_case("valid-discriminating-regression") as (
            repository,
            config,
            source_report,
            _,
        ):
            declaration = _declaration(config, [VALID_SELECTOR])
            localization = run_claim_witness_localization(
                repository,
                config,
                source_report,
                declaration,
            )

        for selector in localization["selectors"]:
            for state in selector["states"]:
                self.assertIsNone(state["stdout"])
                self.assertIsNone(state["stderr"])
        encoded = json.dumps(localization, sort_keys=True)
        self.assertNotIn("Traceback (most recent call last)", encoded)
        self.assertNotIn("/tmp/", encoded)
        self.assertNotIn("\\Temp\\", encoded)

        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertIs(schema["additionalProperties"], False)
        self.assertEqual(set(schema["required"]), set(localization))
        self.assertEqual(set(schema["properties"]), set(localization))


if __name__ == "__main__":
    unittest.main()
