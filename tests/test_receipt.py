from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest

from deltawitness.errors import ReceiptError
from deltawitness.receipt import (
    MAX_RECEIPT_BYTES,
    build_receipt_document,
    load_outcome_receipt,
    validate_receipt_document,
    write_outcome_receipt,
)

_BINDING = "a" * 64


def counts(**overrides: int) -> dict[str, int]:
    result = {
        "tests_run": 1,
        "passed": 1,
        "failures": 0,
        "errors": 0,
        "skipped": 0,
        "expected_failures": 0,
        "unexpected_successes": 0,
    }
    result.update(overrides)
    return result


class OutcomeReceiptTests(unittest.TestCase):
    def test_round_trip_preserves_typed_semantics(self) -> None:
        document = build_receipt_document(
            binding=_BINDING,
            producer_name="test-producer",
            producer_version="1.0.0",
            outcome="test_failure",
            counts=counts(passed=0, failures=1),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            write_outcome_receipt(path, document, expected_binding=_BINDING)
            receipt = load_outcome_receipt(path, expected_binding=_BINDING)

        self.assertEqual(receipt.outcome, "test_failure")
        self.assertEqual(receipt.counts["failures"], 1)
        self.assertEqual(receipt.producer_name, "test-producer")
        self.assertEqual(len(receipt.sha256), 64)

    def test_binding_mismatch_fails_closed(self) -> None:
        document = build_receipt_document(
            binding=_BINDING,
            producer_name="test-producer",
            producer_version="1.0.0",
            outcome="passed",
            counts=counts(),
        )
        with self.assertRaisesRegex(ReceiptError, "invocation") as captured:
            validate_receipt_document(document, expected_binding="b" * 64)
        self.assertEqual(captured.exception.code, "binding_mismatch")

    def test_duplicate_json_keys_are_rejected(self) -> None:
        raw = (
            '{"schema_version":"deltawitness.outcome-receipt.v1",'
            f'"binding":"{_BINDING}",'
            '"producer":{"name":"x","version":"1"},'
            '"outcome":"passed","outcome":"test_failure",'
            '"counts":{"tests_run":1,"passed":1,"failures":0,"errors":0,'
            '"skipped":0,"expected_failures":0,"unexpected_successes":0}}'
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            path.write_text(raw, encoding="utf-8")
            with self.assertRaises(ReceiptError) as captured:
                load_outcome_receipt(path, expected_binding=_BINDING)
        self.assertEqual(captured.exception.code, "invalid_json")

    def test_inconsistent_counts_are_rejected(self) -> None:
        document = {
            "schema_version": "deltawitness.outcome-receipt.v1",
            "binding": _BINDING,
            "producer": {"name": "x", "version": "1"},
            "outcome": "passed",
            "counts": counts(tests_run=2),
        }
        with self.assertRaises(ReceiptError) as captured:
            validate_receipt_document(document, expected_binding=_BINDING)
        self.assertEqual(captured.exception.code, "inconsistent_counts")

    def test_semantically_inconsistent_outcome_is_rejected(self) -> None:
        document = {
            "schema_version": "deltawitness.outcome-receipt.v1",
            "binding": _BINDING,
            "producer": {"name": "x", "version": "1"},
            "outcome": "passed",
            "counts": counts(passed=0, failures=1),
        }
        with self.assertRaises(ReceiptError) as captured:
            validate_receipt_document(document, expected_binding=_BINDING)
        self.assertEqual(captured.exception.code, "inconsistent_outcome")

    def test_oversized_receipt_is_rejected_before_json_parsing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            path.write_bytes(b"{" + b"x" * MAX_RECEIPT_BYTES)
            with self.assertRaises(ReceiptError) as captured:
                load_outcome_receipt(path, expected_binding=_BINDING)
        self.assertEqual(captured.exception.code, "too_large")

    @unittest.skipIf(os.name != "posix", "symbolic-link semantics required")
    def test_symbolic_link_receipt_is_not_followed(self) -> None:
        document = build_receipt_document(
            binding=_BINDING,
            producer_name="test-producer",
            producer_version="1.0.0",
            outcome="passed",
            counts=counts(),
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.json"
            target.write_text(json.dumps(document), encoding="utf-8")
            link = root / "receipt.json"
            os.symlink(target.name, link)
            with self.assertRaises(ReceiptError) as captured:
                load_outcome_receipt(link, expected_binding=_BINDING)
        self.assertEqual(captured.exception.code, "not_regular")


if __name__ == "__main__":
    unittest.main()
