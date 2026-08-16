from __future__ import annotations

from copy import deepcopy
import unittest

from deltawitness.dw001 import project_baselines
from deltawitness.dw001_contracts import (
    DW001ContractError,
    compute_result_sha256,
    seal_result_record,
    verify_result_against_sources,
)
from test_dw001 import _report
from test_dw001_contracts_verification import _manifest, _result


def _results_visible_deviation_result(
    manifest: dict[str, object],
    projection: dict[str, object],
) -> dict[str, object]:
    result = _result(manifest, projection)
    tampered = deepcopy(result)
    tampered["deviations"] = [
        {
            "deviation_id": "deviation-visible-guard-001",
            "status": "applied",
            "rule_id": "execution.timeout",
            "observed_problem": "The frozen timeout was changed after method results were visible.",
            "action": "Use a longer timeout.",
            "results_visible": True,
            "confirmatory_impact": "none",
            "approval_reference": "review/deviation-visible-guard-001",
        }
    ]
    return tampered


class DW001PostUnblindingGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.projection = project_baselines(
            _report(),
            scenario_id="study-contract-post-unblinding-guard-001",
        )
        self.manifest = _manifest(self.projection, partition="holdout")

    def test_builder_refuses_results_visible_applied_confirmatory_deviation(self) -> None:
        document = _results_visible_deviation_result(self.manifest, self.projection)

        with self.assertRaisesRegex(
            DW001ContractError,
            "results-visible applied deviation cannot retain confirmatory eligibility",
        ):
            seal_result_record(document)

    def test_cross_artifact_verifier_refuses_recomputed_digest(self) -> None:
        document = _results_visible_deviation_result(self.manifest, self.projection)
        document["result_sha256"] = compute_result_sha256(document)

        valid, errors = verify_result_against_sources(
            document,
            self.manifest,
            self.projection,
        )

        self.assertFalse(valid)
        self.assertTrue(
            any(
                "results-visible applied deviation cannot retain confirmatory eligibility"
                in error
                for error in errors
            ),
            errors,
        )

    def test_approved_pre_unblinding_deviation_can_retain_confirmatory_status(self) -> None:
        document = _result(self.manifest, self.projection)
        document["deviations"] = [
            {
                "deviation_id": "deviation-pre-unblinding-001",
                "status": "applied",
                "rule_id": "execution.timeout",
                "observed_problem": "The frozen timeout was infeasible before any result was visible.",
                "action": "Use the approved replacement timeout.",
                "results_visible": False,
                "confirmatory_impact": "none",
                "approval_reference": "review/deviation-pre-unblinding-001",
            }
        ]

        sealed = seal_result_record(document)
        valid, errors = verify_result_against_sources(
            sealed,
            self.manifest,
            self.projection,
        )

        self.assertTrue(valid, errors)
        self.assertTrue(
            all(method["primary_denominator_eligible"] for method in sealed["methods"])
        )


if __name__ == "__main__":
    unittest.main()
