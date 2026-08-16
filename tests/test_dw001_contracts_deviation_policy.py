from __future__ import annotations

from copy import deepcopy
import unittest

from deltawitness.dw001 import project_baselines
from deltawitness.dw001_contracts import (
    compute_result_sha256,
    verify_result_record_document,
)
from test_dw001 import _report
from test_dw001_contracts_verification import _manifest, _result


class DW001DeviationPolicyRegressionTests(unittest.TestCase):
    def test_results_visible_applied_deviation_cannot_remain_confirmatory(self) -> None:
        projection = project_baselines(
            _report(),
            scenario_id="study-contract-visible-deviation-001",
        )
        manifest = _manifest(projection, partition="holdout")
        result = _result(manifest, projection)
        tampered = deepcopy(result)
        tampered["deviations"] = [
            {
                "deviation_id": "deviation-visible-001",
                "status": "applied",
                "rule_id": "execution.timeout",
                "observed_problem": "The frozen timeout was changed after method results were visible.",
                "action": "Use a longer timeout.",
                "results_visible": True,
                "confirmatory_impact": "none",
                "approval_reference": "review/deviation-visible-001",
            }
        ]
        tampered["result_sha256"] = compute_result_sha256(tampered)

        valid, errors = verify_result_record_document(tampered)

        self.assertFalse(valid)
        self.assertTrue(
            any(
                "results-visible applied deviation cannot retain confirmatory eligibility"
                in error
                for error in errors
            ),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
