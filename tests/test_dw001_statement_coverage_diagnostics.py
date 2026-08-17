from __future__ import annotations

from pathlib import Path
import unittest

from deltawitness.dw001_mutation_results import run_claim_scoped_mutation_result
from deltawitness.dw001_statement_coverage import run_claim_scoped_statement_coverage
from deltawitness.reporting import load_report


_ROOT = Path(__file__).resolve().parents[1]
_PLAN_PATH = _ROOT / "research" / "DW-001" / "claim-scoped-mutation-plan.v1.json"
_CATALOG_PATH = _ROOT / "research" / "DW-001" / "claim-scoped-mutant-catalog.v1.json"


class DW001StatementCoverageDiagnosticTests(unittest.TestCase):
    def test_fixed_candidate_selectors_emit_complete_trace_receipts(self) -> None:
        plan = load_report(_PLAN_PATH)
        catalog = load_report(_CATALOG_PATH)
        mutation_result = run_claim_scoped_mutation_result(plan, catalog)
        result = run_claim_scoped_statement_coverage(
            plan,
            catalog,
            mutation_result,
        )

        for profile in result["profiles"]:
            for selector in profile["selectors"]:
                self.assertEqual(
                    selector["observed"],
                    "pass",
                    selector,
                )
                self.assertEqual(
                    selector["return_code"],
                    0,
                    selector,
                )
                self.assertIsNone(
                    selector["observation_error"],
                    selector,
                )
                self.assertEqual(
                    selector["receipt_outcome"],
                    "passed",
                    selector,
                )
                self.assertEqual(
                    selector["trace"]["trace_status"],
                    "complete",
                    selector,
                )


if __name__ == "__main__":
    unittest.main()
