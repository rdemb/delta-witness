from __future__ import annotations

from pathlib import Path
import unittest

from deltawitness.dw001_coveragepy_baseline import (
    compute_coveragepy_baseline_report_sha256,
    compute_coveragepy_baseline_semantic_sha256,
    load_claim_scoped_coveragepy_baseline,
)
from deltawitness.dw001_mutation_results import run_claim_scoped_mutation_result
from deltawitness.dw001_statement_coverage import run_claim_scoped_statement_coverage
from deltawitness.reporting import load_report


_ROOT = Path(__file__).resolve().parents[2]
_PLAN_PATH = _ROOT / "research" / "DW-001" / "claim-scoped-mutation-plan.v1.json"
_CATALOG_PATH = _ROOT / "research" / "DW-001" / "claim-scoped-mutant-catalog.v1.json"
_RESULT_PATH = _ROOT / "research" / "DW-001" / "coveragepy-baseline-result.v1.json"
_SEMANTIC_SHA256 = (
    "ec0c2fdd5ac24ba53eb895d9014aab623d2631125b8512ba0e0cbf5105f21ee8"
)
_REPORT_SHA256 = (
    "8b248757374ebff4195bad181ad02bc5b0bfc61fa2e21ebf45549686c33d2c41"
)


class CoveragePyFrozenResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = load_report(_PLAN_PATH)
        cls.catalog = load_report(_CATALOG_PATH)
        cls.mutation_result = run_claim_scoped_mutation_result(
            cls.plan,
            cls.catalog,
        )
        cls.stdlib_result = run_claim_scoped_statement_coverage(
            cls.plan,
            cls.catalog,
            cls.mutation_result,
        )

    def test_frozen_result_reconstructs_and_verifies(self) -> None:
        result = load_claim_scoped_coveragepy_baseline(
            _RESULT_PATH,
            self.plan,
            self.catalog,
            self.mutation_result,
            self.stdlib_result,
        )
        self.assertEqual(result["semantic_sha256"], _SEMANTIC_SHA256)
        self.assertEqual(result["report_sha256"], _REPORT_SHA256)
        self.assertEqual(
            compute_coveragepy_baseline_semantic_sha256(result),
            _SEMANTIC_SHA256,
        )
        self.assertEqual(
            compute_coveragepy_baseline_report_sha256(result),
            _REPORT_SHA256,
        )
        self.assertEqual(result["analysis"]["status"], "expected")
        self.assertFalse(
            result["comparison"][
                "coveragepy_branch_discriminates_profiles"
            ]
        )
        self.assertTrue(
            result["comparison"][
                "incremental_mutation_signal_beyond_coveragepy_observed"
            ]
        )


if __name__ == "__main__":
    unittest.main()
