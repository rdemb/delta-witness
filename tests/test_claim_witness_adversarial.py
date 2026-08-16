from __future__ import annotations

from copy import deepcopy
import math
import unittest

from deltawitness.claim_witness import (
    build_claim_witness_declaration,
    compute_claim_witness_localization_report_sha256,
    compute_claim_witness_localization_sha256,
    run_claim_witness_localization,
    verify_claim_witness_localization_document,
)
from deltawitness.receipt import (
    build_receipt_document,
    validate_receipt_document,
)
from claim_witness_support import CLAIM_ID, VALID_SELECTOR, fixture_case


def _resign(localization: dict[str, object]) -> None:
    localization["localization_sha256"] = (
        compute_claim_witness_localization_sha256(localization)
    )
    localization["report_sha256"] = (
        compute_claim_witness_localization_report_sha256(localization)
    )


def _replace_receipt(
    state: dict[str, object],
    *,
    producer_name: str,
    producer_version: str,
    counts: dict[str, int],
) -> None:
    binding = state["invocation_binding"]
    outcome = state["receipt_outcome"]
    assert isinstance(binding, str)
    assert isinstance(outcome, str)
    document = build_receipt_document(
        binding=binding,
        producer_name=producer_name,
        producer_version=producer_version,
        outcome=outcome,
        counts=counts,
    )
    receipt = validate_receipt_document(
        document,
        expected_binding=binding,
    )
    state["receipt_sha256"] = receipt.sha256
    state["receipt_producer"] = {
        "name": producer_name,
        "version": producer_version,
    }
    state["receipt_counts"] = counts


class ClaimWitnessAdversarialTests(unittest.TestCase):
    def _artifacts(self):
        context = fixture_case("valid-discriminating-regression")
        repository, config, source_report, _ = context.__enter__()
        self.addCleanup(context.__exit__, None, None, None)
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
        return declaration, source_report, localization

    def test_exact_selector_receipt_must_cover_one_logical_test(self) -> None:
        declaration, source_report, localization = self._artifacts()
        tampered = deepcopy(localization)
        state = tampered["selectors"][0]["states"][0]
        assert isinstance(state, dict)
        _replace_receipt(
            state,
            producer_name="deltawitness-unittest",
            producer_version="0.0.3",
            counts={
                "tests_run": 2,
                "passed": 0,
                "failures": 2,
                "errors": 0,
                "skipped": 0,
                "expected_failures": 0,
                "unexpected_successes": 0,
            },
        )
        _resign(tampered)

        valid, errors = verify_claim_witness_localization_document(
            tampered,
            declaration,
            source_report,
        )

        self.assertFalse(valid)
        self.assertTrue(any("exactly one logical test" in error for error in errors), errors)

    def test_adapter_rejects_substituted_receipt_producer_after_resigning(self) -> None:
        declaration, source_report, localization = self._artifacts()
        tampered = deepcopy(localization)
        state = tampered["selectors"][0]["states"][0]
        assert isinstance(state, dict)
        counts = state["receipt_counts"]
        assert isinstance(counts, dict)
        _replace_receipt(
            state,
            producer_name="another-producer",
            producer_version="1",
            counts=counts,
        )
        _resign(tampered)

        valid, errors = verify_claim_witness_localization_document(
            tampered,
            declaration,
            source_report,
        )

        self.assertFalse(valid)
        self.assertTrue(any("receipt producer" in error for error in errors), errors)

    def test_invocation_binding_tampering_fails_after_digest_recomputation(self) -> None:
        declaration, source_report, localization = self._artifacts()
        tampered = deepcopy(localization)
        tampered["selectors"][0]["states"][0]["invocation_binding"] = "f" * 64
        _resign(tampered)

        valid, errors = verify_claim_witness_localization_document(
            tampered,
            declaration,
            source_report,
        )

        self.assertFalse(valid)
        self.assertTrue(any("invocation_binding" in error for error in errors), errors)

    def test_git_state_substitution_fails_after_digest_recomputation(self) -> None:
        declaration, source_report, localization = self._artifacts()
        tampered = deepcopy(localization)
        base_candidate = tampered["selectors"][0]["states"][0]
        candidate_candidate = tampered["selectors"][0]["states"][1]
        base_candidate["commit_sha"] = candidate_candidate["commit_sha"]
        base_candidate["tree_sha"] = candidate_candidate["tree_sha"]
        _resign(tampered)

        valid, errors = verify_claim_witness_localization_document(
            tampered,
            declaration,
            source_report,
        )

        self.assertFalse(valid)
        self.assertTrue(any("source report" in error for error in errors), errors)

    def test_nonfinite_duration_fails_closed(self) -> None:
        declaration, source_report, localization = self._artifacts()
        tampered = deepcopy(localization)
        tampered["selectors"][0]["states"][0]["duration_seconds"] = math.nan

        valid, errors = verify_claim_witness_localization_document(
            tampered,
            declaration,
            source_report,
        )

        self.assertFalse(valid)
        self.assertTrue(any("duration_seconds" in error for error in errors), errors)

    def test_unhashable_observed_value_fails_closed(self) -> None:
        declaration, source_report, localization = self._artifacts()
        tampered = deepcopy(localization)
        tampered["selectors"][0]["states"][0]["observed"] = []
        _resign(tampered)

        valid, errors = verify_claim_witness_localization_document(
            tampered,
            declaration,
            source_report,
        )

        self.assertFalse(valid)
        self.assertTrue(any("observed" in error for error in errors), errors)

    def test_unhashable_aggregate_status_fails_closed(self) -> None:
        declaration, source_report, localization = self._artifacts()
        tampered = deepcopy(localization)
        tampered["aggregate_status"] = []
        _resign(tampered)

        valid, errors = verify_claim_witness_localization_document(
            tampered,
            declaration,
            source_report,
        )

        self.assertFalse(valid)
        self.assertTrue(any("aggregate_status" in error for error in errors), errors)

    def test_malformed_roots_return_typed_invalid_diagnostics(self) -> None:
        declaration, source_report, localization = self._artifacts()

        for label, bad_localization, bad_declaration, bad_report in (
            ("localization", [], declaration, source_report),
            ("declaration", localization, [], source_report),
            ("source report", localization, declaration, []),
        ):
            with self.subTest(label=label):
                valid, errors = verify_claim_witness_localization_document(
                    bad_localization,
                    bad_declaration,
                    bad_report,
                )
                self.assertFalse(valid)
                self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
