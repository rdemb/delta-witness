from __future__ import annotations

import argparse
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import coverage

import deltawitness.coveragepy_probe as coveragepy_probe


_CONTEXT_ID = (
    "dw001-coveragepy-v1:strong-authorization-oracle-v1:"
    "test_access.AccessTests.test_admin_is_allowed"
)
_BINDING = "a" * 64


class CoveragePyAmbientStateTests(unittest.TestCase):
    def _measure_unavailable_boundary(self, root: Path):
        """Run a passing logical test without importing synthetic modules.

        These tests isolate Coverage.py ambient-state classification itself.
        Source loading, contexts, and exact selector execution are exercised by
        the separate public-API child and complete baseline tests.
        """

        (root / "src").mkdir()
        source = root / "src" / "access.py"
        source.write_text(
            "def is_admin(user):\n    return True\n",
            encoding="utf-8",
        )
        target = {
            "path": "src/access.py",
            "symbol": "is_admin",
            "source_sha256": __import__("hashlib").sha256(
                source.read_bytes()
            ).hexdigest(),
            "target_lines": [2],
        }
        suite = unittest.TestSuite(
            [unittest.FunctionTestCase(lambda: None)]
        )
        args = argparse.Namespace(verbosity=0)
        previous = Path.cwd()
        try:
            os.chdir(root)
            return coveragepy_probe._measure(
                suite=suite,
                args=args,
                target_path=source.resolve(),
                target_path_text="src/access.py",
                target=target,
                context_id=_CONTEXT_ID,
                configuration=coveragepy_probe._configuration(_CONTEXT_ID),
                binding=_BINDING,
            )
        finally:
            os.chdir(previous)

    def _assert_indeterminate(
        self,
        result: unittest.TestResult,
        receipt: dict[str, object],
        expected_error: str,
    ) -> None:
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(receipt["measurement_status"], "indeterminate")
        self.assertEqual(receipt["measurement_error"], expected_error)
        self.assertIsNone(receipt["measured_files"])
        self.assertIsNone(receipt["statement_evidence"])
        self.assertIsNone(receipt["branch_evidence"])
        self.assertIsNone(receipt["context_evidence"])

    def test_coverage_environment_variable_forces_indeterminate_measurement(self) -> None:
        previous = os.environ.get("COVERAGE_RCFILE")
        os.environ["COVERAGE_RCFILE"] = "/tmp/ambient-coveragerc"
        try:
            with tempfile.TemporaryDirectory() as directory:
                result, receipt = self._measure_unavailable_boundary(
                    Path(directory)
                )
        finally:
            if previous is None:
                os.environ.pop("COVERAGE_RCFILE", None)
            else:
                os.environ["COVERAGE_RCFILE"] = previous

        self._assert_indeterminate(
            result,
            receipt,
            "ambient_coverage_environment",
        )

    def test_preexisting_active_collector_forces_indeterminate_measurement(self) -> None:
        # Test the documented public active-collector signal without installing
        # a process-global trace function that could contaminate later tests.
        with patch.object(
            coverage.Coverage,
            "current",
            return_value=object(),
        ):
            with tempfile.TemporaryDirectory() as directory:
                result, receipt = self._measure_unavailable_boundary(
                    Path(directory)
                )

        self._assert_indeterminate(
            result,
            receipt,
            "coveragepy_already_active",
        )


if __name__ == "__main__":
    unittest.main()
