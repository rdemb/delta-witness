from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from deltawitness.receipt import load_outcome_receipt

_BINDING = "c" * 64


def invoke_probe(project: Path) -> tuple[subprocess.CompletedProcess[str], object]:
    receipt_path = project.parent / "receipt.json"
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


class UnittestProbeTests(unittest.TestCase):
    def _project(self, directory: str, test_source: str | None) -> Path:
        project = Path(directory) / "project"
        tests = project / "tests"
        tests.mkdir(parents=True)
        if test_source is not None:
            (tests / "test_example.py").write_text(test_source, encoding="utf-8")
        return project

    def test_passing_test_emits_passed_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(
                directory,
                "import unittest\n\n"
                "class Example(unittest.TestCase):\n"
                "    def test_ok(self):\n"
                "        self.assertEqual(2 + 2, 4)\n",
            )
            completed, receipt = invoke_probe(project)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(receipt.outcome, "passed")
        self.assertEqual(receipt.counts["passed"], 1)

    def test_assertion_failure_is_typed_as_test_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(
                directory,
                "import unittest\n\n"
                "class Example(unittest.TestCase):\n"
                "    def test_regression(self):\n"
                "        self.assertEqual('old', 'new')\n",
            )
            completed, receipt = invoke_probe(project)

        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertEqual(receipt.outcome, "test_failure")
        self.assertEqual(receipt.counts["failures"], 1)
        self.assertEqual(receipt.counts["errors"], 0)

    def test_multiple_failing_subtests_count_as_one_logical_test_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(
                directory,
                "import unittest\n\n"
                "class Example(unittest.TestCase):\n"
                "    def test_many_cases(self):\n"
                "        for value in (1, 2, 3):\n"
                "            with self.subTest(value=value):\n"
                "                self.assertEqual(value, 0)\n",
            )
            completed, receipt = invoke_probe(project)

        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertEqual(receipt.outcome, "test_failure")
        self.assertEqual(receipt.counts["tests_run"], 1)
        self.assertEqual(receipt.counts["failures"], 1)

    def test_import_error_is_not_typed_as_regression_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(
                directory,
                "import module_that_does_not_exist_for_deltawitness_test\n",
            )
            completed, receipt = invoke_probe(project)

        self.assertEqual(completed.returncode, 2, completed.stderr)
        self.assertEqual(receipt.outcome, "test_error")
        self.assertGreater(receipt.counts["errors"], 0)
        self.assertEqual(receipt.counts["failures"], 0)

    def test_empty_discovery_is_typed_as_no_tests(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory, None)
            completed, receipt = invoke_probe(project)

        self.assertEqual(completed.returncode, 2, completed.stderr)
        self.assertEqual(receipt.outcome, "no_tests")
        self.assertEqual(receipt.counts["tests_run"], 0)

    def test_all_skipped_suite_is_not_typed_as_passed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(
                directory,
                "import unittest\n\n"
                "class Example(unittest.TestCase):\n"
                "    @unittest.skip('synthetic')\n"
                "    def test_skipped(self):\n"
                "        self.fail('must not execute')\n",
            )
            completed, receipt = invoke_probe(project)

        self.assertEqual(completed.returncode, 2, completed.stderr)
        self.assertEqual(receipt.outcome, "no_effective_tests")
        self.assertEqual(receipt.counts["skipped"], 1)
        self.assertEqual(receipt.counts["passed"], 0)


if __name__ == "__main__":
    unittest.main()
