from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from deltawitness import statement_trace_probe


_SOURCE = """def is_admin(user):
    return user.get(\"role\") == \"admin\"
"""
_TEST = """import sys
import unittest

sys.path.insert(0, \"src\")
from access import is_admin


class AccessTests(unittest.TestCase):
    def test_admin_is_allowed(self):
        self.assertTrue(is_admin({\"role\": \"admin\"}))
"""
_SOURCE_SHA256 = "7bfbd2d0a642c6d7f7da05ece2f4464d31df53a28d1ffed12c5752bc492d8965"
_BINDING = "a" * 64


class EarlyStatementTraceProbeExecutionTests(unittest.TestCase):
    def test_fixed_selector_emits_both_outcome_and_trace_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            (root / "tests").mkdir()
            (root / "src" / "access.py").write_text(_SOURCE, encoding="utf-8")
            (root / "tests" / "test_access.py").write_text(_TEST, encoding="utf-8")
            receipt = root / "outcome-receipt.json"
            trace = root / statement_trace_probe.TRACE_OUTPUT_BASENAME
            args = statement_trace_probe._parser().parse_args(
                [
                    "--start-directory",
                    "tests",
                    "--verbosity",
                    "0",
                    "--test-name",
                    "test_access.AccessTests.test_admin_is_allowed",
                    "--target-path",
                    "src/access.py",
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
                ):
                    self.assertEqual(statement_trace_probe.run_probe(args), 0)
            finally:
                os.chdir(previous)

            self.assertTrue(receipt.is_file())
            self.assertTrue(trace.is_file())


if __name__ == "__main__":
    unittest.main()
