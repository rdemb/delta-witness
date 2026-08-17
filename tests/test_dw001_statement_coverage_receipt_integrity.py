from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import unittest

from deltawitness.dw001_mutation_results import run_claim_scoped_mutation_result
from deltawitness.dw001_statement_coverage import (
    compute_statement_coverage_report_sha256,
    compute_statement_coverage_semantic_sha256,
    run_claim_scoped_statement_coverage,
    verify_claim_scoped_statement_coverage_document,
)
from deltawitness.reporting import load_report


_ROOT = Path(__file__).resolve().parents[1]
_PLAN_PATH = _ROOT / "research" / "DW-001" / "claim-scoped-mutation-plan.v1.json"
_CATALOG_PATH = _ROOT / "research" / "DW-001" / "claim-scoped-mutant-catalog.v1.json"


class DW001StatementCoverageReceiptIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = load_report(_PLAN_PATH)
        cls.catalog = load_report(_CATALOG_PATH)
        cls.mutation_result = run_claim_scoped_mutation_result(
            cls.plan,
            cls.catalog,
        )
        cls.result = run_claim_scoped_statement_coverage(
            cls.plan,
            cls.catalog,
            cls.mutation_result,
        )

    def _reseal(self, document: dict[str, object]) -> None:
        document["semantic_sha256"] = compute_statement_coverage_semantic_sha256(
            document
        )
        document["report_sha256"] = compute_statement_coverage_report_sha256(
            document
        )

    def _verify(self, document: object) -> tuple[bool, tuple[str, ...]]:
        return verify_claim_scoped_statement_coverage_document(
            document,
            self.plan,
            self.catalog,
            self.mutation_result,
        )

    def test_recomputed_result_digests_cannot_hide_receipt_producer_substitution(self) -> None:
        tampered = deepcopy(self.result)
        selector = tampered["profiles"][0]["selectors"][0]
        selector["receipt_producer"] = {
            "name": "substituted-producer",
            "version": selector["receipt_producer"]["version"],
        }
        self._reseal(tampered)

        valid, errors = self._verify(tampered)
        self.assertFalse(valid)
        self.assertTrue(
            any("receipt_producer" in error for error in errors),
            errors,
        )

    def test_recomputed_result_digests_cannot_hide_receipt_digest_substitution(self) -> None:
        tampered = deepcopy(self.result)
        tampered["profiles"][0]["selectors"][0]["receipt_sha256"] = "f" * 64
        self._reseal(tampered)

        valid, errors = self._verify(tampered)
        self.assertFalse(valid)
        self.assertTrue(
            any("receipt_sha256" in error for error in errors),
            errors,
        )

    def test_recomputed_result_digests_cannot_hide_receipt_count_substitution(self) -> None:
        tampered = deepcopy(self.result)
        counts = tampered["profiles"][0]["selectors"][0]["receipt_counts"]
        counts["passed"] = 0
        counts["skipped"] = 1
        self._reseal(tampered)

        valid, errors = self._verify(tampered)
        self.assertFalse(valid)
        self.assertTrue(
            any("receipt_counts" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
