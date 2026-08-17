from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch

from deltawitness import __version__
import deltawitness.dw001_statement_coverage as statement_coverage
from deltawitness.dw001_mutation_results import run_claim_scoped_mutation_result
from deltawitness.dw001_statement_coverage import (
    compute_statement_coverage_report_sha256,
    compute_statement_coverage_semantic_sha256,
    run_claim_scoped_statement_coverage,
    verify_claim_scoped_statement_coverage_document,
)
from deltawitness.receipt import build_receipt_document, validate_receipt_document
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

    def test_error_observation_cannot_retain_a_resealed_passed_receipt(self) -> None:
        original = statement_coverage._execute_selector
        injected = False

        def contradictory_selector(**kwargs):
            nonlocal injected
            observation = original(**kwargs)
            if not injected:
                injected = True
                observation = deepcopy(observation)
                observation["observed"] = "error"
                observation["return_code"] = 2
                observation["timed_out"] = False
                observation["observation_error"] = "receipt_exit_mismatch"
                # Retain the valid, invocation-bound `passed` receipt and its
                # one-passing-test counts. Current main incorrectly accepts
                # this process/receipt contradiction after result resealing.
            return observation

        with patch.object(
            statement_coverage,
            "_execute_selector",
            side_effect=contradictory_selector,
            create=True,
        ):
            with self.assertRaisesRegex(
                statement_coverage.DW001StatementCoverageError,
                "receipt",
            ):
                run_claim_scoped_statement_coverage(
                    self.plan,
                    self.catalog,
                    self.mutation_result,
                )

        self.assertTrue(injected)

    def test_error_observation_rejects_process_inconsistent_typed_error_receipt(
        self,
    ) -> None:
        original = statement_coverage._execute_selector
        injected = False

        def contradictory_selector(**kwargs):
            nonlocal injected
            observation = original(**kwargs)
            if not injected:
                injected = True
                observation = deepcopy(observation)
                counts = {
                    "tests_run": 1,
                    "passed": 0,
                    "failures": 0,
                    "errors": 1,
                    "skipped": 0,
                    "expected_failures": 0,
                    "unexpected_successes": 0,
                }
                receipt = build_receipt_document(
                    binding=observation["invocation_binding"],
                    producer_name="deltawitness-unittest",
                    producer_version=__version__,
                    outcome="test_error",
                    counts=counts,
                )
                canonical = validate_receipt_document(
                    receipt,
                    expected_binding=observation["invocation_binding"],
                )
                observation["observed"] = "error"
                observation["return_code"] = 0
                observation["timed_out"] = False
                observation["receipt_sha256"] = canonical.sha256
                observation["receipt_outcome"] = canonical.outcome
                observation["receipt_producer"] = {
                    "name": canonical.producer_name,
                    "version": canonical.producer_version,
                }
                observation["receipt_counts"] = canonical.counts
                observation["observation_error"] = "receipt_exit_mismatch"
            return observation

        with patch.object(
            statement_coverage,
            "_execute_selector",
            side_effect=contradictory_selector,
            create=True,
        ):
            with self.assertRaisesRegex(
                statement_coverage.DW001StatementCoverageError,
                "return_code",
            ):
                run_claim_scoped_statement_coverage(
                    self.plan,
                    self.catalog,
                    self.mutation_result,
                )

        self.assertTrue(injected)

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
