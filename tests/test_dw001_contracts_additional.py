from __future__ import annotations

from copy import deepcopy
import json
import math
from pathlib import Path
import unittest

from deltawitness.dw001 import project_baselines
from deltawitness.dw001_contracts import (
    compute_result_sha256,
    verify_result_against_sources,
    verify_result_record_document,
    verify_scenario_manifest_document,
)
from test_dw001 import _report
from test_dw001_contracts_verification import _manifest, _result


class DW001StudyContractAdditionalTests(unittest.TestCase):
    def test_typed_receipt_arm_round_trips_through_all_contracts(self) -> None:
        projection = project_baselines(
            _report(observers=("outcome-receipt-v1",)),
            scenario_id="study-contract-typed-001",
        )
        manifest = _manifest(projection)
        result = _result(manifest, projection)

        manifest_valid, manifest_errors = verify_scenario_manifest_document(manifest)
        result_valid, result_errors = verify_result_record_document(result)
        cross_valid, cross_errors = verify_result_against_sources(
            result,
            manifest,
            projection,
        )

        self.assertTrue(manifest_valid, manifest_errors)
        self.assertTrue(result_valid, result_errors)
        self.assertTrue(cross_valid, cross_errors)
        self.assertEqual(manifest["execution"]["observer_id"], "O1_TYPED_RECEIPT")

    def test_approved_exploratory_deviation_is_retained_but_not_confirmatory(self) -> None:
        projection = project_baselines(
            _report(),
            scenario_id="study-contract-deviation-001",
        )
        manifest = _manifest(projection, partition="holdout")
        result = _result(manifest, projection)
        result["deviations"] = [
            {
                "deviation_id": "deviation-001",
                "status": "applied",
                "rule_id": "execution.timeout",
                "observed_problem": "Synthetic timeout policy deviation.",
                "action": "Use the pre-approved alternative timeout.",
                "results_visible": False,
                "confirmatory_impact": "exploratory_only",
                "approval_reference": "review/deviation-001",
            }
        ]
        for method in result["methods"]:
            method["primary_denominator_eligible"] = False
            method["denominator_reason_code"] = "deviation_exploratory_only"
        result["result_sha256"] = compute_result_sha256(result)

        result_valid, result_errors = verify_result_record_document(result)
        cross_valid, cross_errors = verify_result_against_sources(
            result,
            manifest,
            projection,
        )

        self.assertTrue(result_valid, result_errors)
        self.assertTrue(cross_valid, cross_errors)
        self.assertTrue(
            all(
                not method["primary_denominator_eligible"]
                for method in result["methods"]
            )
        )

    def test_nonfinite_cost_is_rejected_after_digest_recomputation(self) -> None:
        projection = project_baselines(
            _report(),
            scenario_id="study-contract-cost-001",
        )
        manifest = _manifest(projection)
        result = _result(manifest, projection)
        tampered = deepcopy(result)
        cost = tampered["methods"][0]["cost"]
        cost.update(
            {
                "status": "measured",
                "wall_clock_seconds": math.inf,
                "cpu_seconds": 1.0,
                "state_count": 1,
                "command_count": 1,
                "review_seconds": 0.0,
                "missing_reason": None,
            }
        )
        tampered["result_sha256"] = compute_result_sha256(tampered)

        valid, errors = verify_result_record_document(tampered)

        self.assertFalse(valid)
        self.assertTrue(
            any("finite nonnegative number" in error for error in errors),
            errors,
        )

    def test_schema_documents_are_strict_and_local_references_resolve(self) -> None:
        root = Path(__file__).resolve().parents[1]
        schema_paths = (
            root / "research" / "DW-001" / "schema" / "scenario-manifest.schema.json",
            root / "research" / "DW-001" / "schema" / "result-record.schema.json",
        )

        for path in schema_paths:
            with self.subTest(schema=path.name):
                document = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(
                    document["$schema"],
                    "https://json-schema.org/draft/2020-12/schema",
                )
                self.assertFalse(document["additionalProperties"])
                self.assertTrue(document["required"])
                definitions = document.get("$defs", {})
                self.assertIsInstance(definitions, dict)
                for reference in self._local_references(document):
                    prefix = "#/$defs/"
                    self.assertTrue(reference.startswith(prefix), reference)
                    self.assertIn(reference[len(prefix) :], definitions)

    def _local_references(self, value: object) -> list[str]:
        references: list[str] = []
        if isinstance(value, dict):
            reference = value.get("$ref")
            if isinstance(reference, str) and reference.startswith("#"):
                references.append(reference)
            for item in value.values():
                references.extend(self._local_references(item))
        elif isinstance(value, list):
            for item in value:
                references.extend(self._local_references(item))
        return references


if __name__ == "__main__":
    unittest.main()
