from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from deltawitness import statement_trace_probe
from deltawitness.errors import ReceiptError
from deltawitness.receipt import load_outcome_receipt


_SOURCE = """def is_admin(user):
    return user.get(\"role\") == \"admin\"
"""
_TEST = """import sys
import unittest

sys.path.insert(0, \"src\")
from trace_access import is_admin


class TraceAccessTests(unittest.TestCase):
    def test_admin_is_allowed(self):
        self.assertTrue(is_admin({\"role\": \"admin\"}))
"""
_SOURCE_SHA256 = "7bfbd2d0a642c6d7f7da05ece2f4464d31df53a28d1ffed12c5752bc492d8965"
_BINDING = "a" * 64
_TARGET_PATH = "src/trace_access.py"
_SELECTOR = (
    "test_statement_trace_fixture."
    "TraceAccessTests.test_admin_is_allowed"
)


class StatementTraceProbeExecutionTests(unittest.TestCase):
    def _fixture(self, root: Path) -> tuple[Path, Path, object]:
        (root / "src").mkdir()
        (root / "tests").mkdir()
        (root / _TARGET_PATH).write_text(_SOURCE, encoding="utf-8")
        (root / "tests" / "test_statement_trace_fixture.py").write_text(
            _TEST,
            encoding="utf-8",
        )
        receipt = root / "outcome-receipt.json"
        trace = root / statement_trace_probe.TRACE_OUTPUT_BASENAME
        args = statement_trace_probe._parser().parse_args(
            [
                "--start-directory",
                "tests",
                "--verbosity",
                "0",
                "--test-name",
                _SELECTOR,
                "--target-path",
                _TARGET_PATH,
                "--target-symbol",
                "is_admin",
                "--target-line",
                "2",
                "--source-sha256",
                _SOURCE_SHA256,
                "--trace-output",
                statement_trace_probe.TRACE_OUTPUT_BASENAME,
            ]
        )
        return receipt, trace, args

    def _run_in(self, root: Path, args: object) -> int:
        previous = Path.cwd()
        try:
            os.chdir(root)
            with patch.dict(
                os.environ,
                {
                    "DELTAWITNESS_RECEIPT_PATH": str(
                        root / "outcome-receipt.json"
                    ),
                    "DELTAWITNESS_RECEIPT_BINDING": _BINDING,
                },
                clear=False,
            ):
                return statement_trace_probe.run_probe(args)
        finally:
            os.chdir(previous)

    def _load_trace(self, trace: Path) -> dict[str, object]:
        return statement_trace_probe.load_trace_document(
            trace,
            expected_binding=_BINDING,
            expected_target_path=_TARGET_PATH,
            expected_target_symbol="is_admin",
            expected_source_sha256=_SOURCE_SHA256,
            expected_target_lines=[2],
        )

    def test_fixed_selector_emits_both_outcome_and_trace_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            receipt, trace, args = self._fixture(root)
            self.assertEqual(self._run_in(root, args), 0)

            outcome = load_outcome_receipt(
                receipt,
                expected_binding=_BINDING,
            )
            document = self._load_trace(trace)
            self.assertEqual(outcome.outcome, "passed")
            self.assertEqual(outcome.counts["tests_run"], 1)
            self.assertEqual(document["trace_status"], "complete")
            self.assertEqual(document["function_calls"], 1)
            self.assertEqual(document["covered_lines"], [2])
            self.assertEqual(document["line_hits"], [{"line": 2, "hits": 1}])

    def test_internal_probe_failure_retains_bound_indeterminate_trace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            receipt, trace, args = self._fixture(root)
            previous = Path.cwd()
            try:
                os.chdir(root)
                with patch.dict(
                    os.environ,
                    {
                        "DELTAWITNESS_RECEIPT_PATH": str(receipt),
                        "DELTAWITNESS_RECEIPT_BINDING": _BINDING,
                    },
                    clear=False,
                ), patch.object(
                    statement_trace_probe,
                    "_load_suite",
                    side_effect=RuntimeError("synthetic producer failure"),
                ):
                    with self.assertRaises(ReceiptError):
                        statement_trace_probe.run_probe(args)
            finally:
                os.chdir(previous)

            outcome = load_outcome_receipt(
                receipt,
                expected_binding=_BINDING,
            )
            document = self._load_trace(trace)
            self.assertEqual(outcome.outcome, "producer_error")
            self.assertEqual(outcome.counts["tests_run"], 0)
            self.assertEqual(document["trace_status"], "indeterminate")
            self.assertIsNone(document["function_calls"])
            self.assertEqual(document["covered_lines"], [])
            self.assertEqual(document["line_hits"], [])
            self.assertEqual(document["trace_error"], "producer_error")


if __name__ == "__main__":
    unittest.main()
