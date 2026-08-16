from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from deltawitness.receipt import load_outcome_receipt


_BINDING = "d" * 64


def _invoke(project: Path, selector: str):
    receipt_path = project.parent / "selector-receipt.json"
    env = os.environ.copy()
    env["DELTAWITNESS_RECEIPT_PATH"] = str(receipt_path.resolve())
    env["DELTAWITNESS_RECEIPT_BINDING"] = _BINDING
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "deltawitness.unittest_probe",
            "--start-directory",
            "tests",
            "--verbosity",
            "0",
            "--test-name",
            selector,
        ],
        cwd=project,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    receipt = load_outcome_receipt(receipt_path, expected_binding=_BINDING)
    return completed, receipt


class UnittestProbeSelectorTests(unittest.TestCase):
    def _project(self, directory: str) -> Path:
        project = Path(directory) / "project"
        tests = project / "tests"
        tests.mkdir(parents=True)
        (tests / "test_example.py").write_text(
            "import unittest\n\n"
            "class Example(unittest.TestCase):\n"
            "    def test_passes(self):\n"
            "        self.assertTrue(True)\n\n"
            "    def test_fails(self):\n"
            "        self.assertEqual('old', 'new')\n",
            encoding="utf-8",
        )
        return project

    def test_exact_selector_executes_one_logical_test(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            completed, receipt = _invoke(
                project,
                "test_example.Example.test_passes",
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(receipt.outcome, "passed")
        self.assertEqual(receipt.counts["tests_run"], 1)
        self.assertEqual(receipt.counts["passed"], 1)
        self.assertEqual(receipt.counts["failures"], 0)

    def test_exact_failing_selector_emits_one_typed_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            completed, receipt = _invoke(
                project,
                "test_example.Example.test_fails",
            )

        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertEqual(receipt.outcome, "test_failure")
        self.assertEqual(receipt.counts["tests_run"], 1)
        self.assertEqual(receipt.counts["failures"], 1)
        self.assertEqual(receipt.counts["errors"], 0)

    def test_missing_selector_is_typed_as_error_not_no_tests(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            completed, receipt = _invoke(
                project,
                "test_example.Example.test_missing",
            )

        self.assertEqual(completed.returncode, 2, completed.stderr)
        self.assertEqual(receipt.outcome, "test_error")
        self.assertEqual(receipt.counts["tests_run"], 1)
        self.assertEqual(receipt.counts["errors"], 1)
        self.assertEqual(receipt.counts["failures"], 0)


if __name__ == "__main__":
    unittest.main()
