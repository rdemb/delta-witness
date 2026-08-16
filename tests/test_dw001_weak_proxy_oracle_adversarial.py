from __future__ import annotations

from copy import deepcopy
import math
import unittest

from deltawitness.dw001_oracle_challenge import (
    compute_weak_oracle_challenge_sha256,
    compute_weak_oracle_report_sha256,
    verify_weak_oracle_challenge_document,
)
from test_dw001_weak_proxy_oracle import _run_arm


class DW001WeakProxyOracleAdversarialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.artifacts = _run_arm("outcome-receipt-v1")

    def _verify(self, document: object) -> tuple[bool, tuple[str, ...]]:
        return verify_weak_oracle_challenge_document(
            document,
            self.artifacts["descriptor"],
            self.artifacts["identity"],
            self.artifacts["report"],
            self.artifacts["projection"],
            self.artifacts["declaration"],
            self.artifacts["localization"],
        )

    @staticmethod
    def _resign(document: dict[str, object]) -> None:
        document["challenge_sha256"] = compute_weak_oracle_challenge_sha256(
            document
        )
        document["report_sha256"] = compute_weak_oracle_report_sha256(document)

    def test_non_object_and_incomplete_roots_fail_closed(self) -> None:
        for document in (None, [], "challenge", 7, {}):
            with self.subTest(document=type(document).__name__):
                valid, errors = self._verify(document)
                self.assertFalse(valid)
                self.assertTrue(errors)

        missing = deepcopy(self.artifacts["challenge"])
        del missing["finding"]
        self._resign(missing)
        valid, errors = self._verify(missing)
        self.assertFalse(valid)
        self.assertTrue(any("finding" in error for error in errors), errors)

        extra = deepcopy(self.artifacts["challenge"])
        extra["unexpected"] = "field"
        self._resign(extra)
        valid, errors = self._verify(extra)
        self.assertFalse(valid)
        self.assertTrue(any("unexpected" in error for error in errors), errors)

    def test_duplicate_or_reordered_controls_fail_after_resigning(self) -> None:
        duplicate = deepcopy(self.artifacts["challenge"])
        duplicate["controlled_executions"][1] = deepcopy(
            duplicate["controlled_executions"][0]
        )
        self._resign(duplicate)
        valid, errors = self._verify(duplicate)
        self.assertFalse(valid)
        self.assertTrue(
            any("controlled_executions[1]" in error for error in errors),
            errors,
        )

        reordered = deepcopy(self.artifacts["challenge"])
        reordered["controlled_executions"][0], reordered[
            "controlled_executions"
        ][1] = (
            reordered["controlled_executions"][1],
            reordered["controlled_executions"][0],
        )
        self._resign(reordered)
        valid, errors = self._verify(reordered)
        self.assertFalse(valid)
        self.assertTrue(any("controlled_executions" in error for error in errors), errors)

    def test_nonfinite_or_wrong_type_control_evidence_fails_closed(self) -> None:
        nonfinite = deepcopy(self.artifacts["challenge"])
        nonfinite["controlled_executions"][0]["receipt_counts"]["failures"] = (
            math.nan
        )
        valid, errors = self._verify(nonfinite)
        self.assertFalse(valid)
        self.assertTrue(errors)

        wrong_type = deepcopy(self.artifacts["challenge"])
        wrong_type["controlled_executions"] = {
            "base": wrong_type["controlled_executions"][0]
        }
        valid, errors = self._verify(wrong_type)
        self.assertFalse(valid)
        self.assertTrue(errors)

    def test_missing_source_relation_is_not_recoverable_by_resigning(self) -> None:
        tampered = deepcopy(self.artifacts["challenge"])
        tampered["source"]["declaration_sha256"] = "0" * 64
        self._resign(tampered)

        valid, errors = self._verify(tampered)

        self.assertFalse(valid)
        self.assertTrue(
            any("declaration_sha256" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
