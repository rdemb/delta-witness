from __future__ import annotations

import unittest

import deltawitness.dw001_coveragepy_baseline as coveragepy_baseline


class CoveragePyStatusPrecedenceTests(unittest.TestCase):
    def test_missing_or_indeterminate_measurement_precedes_typed_failure(self) -> None:
        self.assertEqual(
            coveragepy_baseline._selector_status(
                {
                    "observed": "fail",
                    "coverage_receipt": None,
                }
            ),
            "indeterminate",
        )
        self.assertEqual(
            coveragepy_baseline._selector_status(
                {
                    "observed": "fail",
                    "coverage_receipt": {
                        "measurement_status": "indeterminate",
                        "measurement_error": "coveragepy_tool_error",
                    },
                }
            ),
            "indeterminate",
        )

    def test_complete_measurement_can_classify_candidate_failure(self) -> None:
        self.assertEqual(
            coveragepy_baseline._selector_status(
                {
                    "observed": "fail",
                    "coverage_receipt": {
                        "measurement_status": "complete",
                        "measurement_error": None,
                    },
                }
            ),
            "candidate_invalid",
        )

    def test_non_pass_fail_process_outcomes_remain_indeterminate(self) -> None:
        for observed in ("error", "timeout", None):
            with self.subTest(observed=observed):
                self.assertEqual(
                    coveragepy_baseline._selector_status(
                        {
                            "observed": observed,
                            "coverage_receipt": {
                                "measurement_status": "complete",
                            },
                        }
                    ),
                    "indeterminate",
                )


if __name__ == "__main__":
    unittest.main()
