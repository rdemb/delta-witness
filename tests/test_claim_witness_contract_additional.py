from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from deltawitness.claim_witness import (
    build_claim_witness_declaration,
    compute_claim_witness_localization_report_sha256,
    compute_claim_witness_localization_sha256,
    run_claim_witness_localization,
    verify_claim_witness_localization_document,
)
from deltawitness.receipt import build_receipt_document, validate_receipt_document
from claim_witness_support import CLAIM_ID, VALID_SELECTOR, fixture_case


_SCHEMA_DIR = Path(__file__).resolve().parents[1] / "research" / "DW-001" / "schema"


def _walk(value: object):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _resign(localization: dict[str, object]) -> None:
    localization["localization_sha256"] = (
        compute_claim_witness_localization_sha256(localization)
    )
    localization["report_sha256"] = (
        compute_claim_witness_localization_report_sha256(localization)
    )


class ClaimWitnessContractAdditionalTests(unittest.TestCase):
    def test_every_schema_object_boundary_is_closed(self) -> None:
        for name in (
            "claim-witness-declaration.schema.json",
            "claim-witness-localization.schema.json",
        ):
            with self.subTest(schema=name):
                document = json.loads((_SCHEMA_DIR / name).read_text(encoding="utf-8"))
                for node in _walk(document):
                    if isinstance(node, dict) and node.get("type") == "object":
                        self.assertIs(
                            node.get("additionalProperties"),
                            False,
                            f"open object boundary in {name}: {node}",
                        )

    def test_localization_schema_fixes_bc_cc_tuple_order(self) -> None:
        document = json.loads(
            (_SCHEMA_DIR / "claim-witness-localization.schema.json").read_text(
                encoding="utf-8"
            )
        )
        states = document["$defs"]["selector_result"]["properties"]["states"]
        self.assertEqual(
            [
                item["properties"]["state"]["const"]
                for item in states["prefixItems"]
            ],
            ["base_candidate", "candidate_candidate"],
        )
        self.assertIs(states["items"], False)

    def test_candidate_failure_is_not_collapsed_into_unsupported(self) -> None:
        with fixture_case("valid-discriminating-regression") as (
            repository,
            config,
            source_report,
            _,
        ):
            declaration = build_claim_witness_declaration(
                spec_sha256=config.digest_sha256,
                claim_id=CLAIM_ID,
                selectors=[VALID_SELECTOR],
            )
            localization = run_claim_witness_localization(
                repository,
                config,
                source_report,
                declaration,
            )

        tampered = deepcopy(localization)
        selector_result = tampered["selectors"][0]
        candidate_state = selector_result["states"][1]
        binding = candidate_state["invocation_binding"]
        producer = candidate_state["receipt_producer"]
        assert isinstance(binding, str)
        assert isinstance(producer, dict)
        counts = {
            "tests_run": 1,
            "passed": 0,
            "failures": 1,
            "errors": 0,
            "skipped": 0,
            "expected_failures": 0,
            "unexpected_successes": 0,
        }
        receipt_document = build_receipt_document(
            binding=binding,
            producer_name=producer["name"],
            producer_version=producer["version"],
            outcome="test_failure",
            counts=counts,
        )
        receipt = validate_receipt_document(
            receipt_document,
            expected_binding=binding,
        )
        candidate_state["observed"] = "fail"
        candidate_state["return_code"] = 1
        candidate_state["receipt_sha256"] = receipt.sha256
        candidate_state["receipt_outcome"] = "test_failure"
        candidate_state["receipt_counts"] = counts
        candidate_state["observation_error"] = None
        selector_result["classification"] = "candidate_invalid"
        selector_result["diagnostic_code"] = "candidate_candidate_failed"
        tampered["aggregate_status"] = "candidate_invalid"
        _resign(tampered)

        valid, errors = verify_claim_witness_localization_document(
            tampered,
            declaration,
            source_report,
        )

        self.assertTrue(valid, errors)


if __name__ == "__main__":
    unittest.main()
