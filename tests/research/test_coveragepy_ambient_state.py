from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import sys
import tempfile
import unittest

import coverage

import deltawitness.coveragepy_probe as coveragepy_probe


_SOURCE = """def is_admin(user):
    return user.get(\"role\") == \"admin\"
"""
_TESTS = """import sys
import unittest

sys.path.insert(0, \"src\")
from access import is_admin


class AccessTests(unittest.TestCase):
    def test_admin_is_allowed(self):
        self.assertTrue(is_admin({\"role\": \"admin\"}))
"""
_SELECTOR = "test_access.AccessTests.test_admin_is_allowed"
_CONTEXT_ID = (
    "dw001-coveragepy-v1:strong-authorization-oracle-v1:"
    f"{_SELECTOR}"
)
_BINDING = "a" * 64
_SYNTHETIC_MODULES = ("access", "test_access", "tests.test_access")


class CoveragePyAmbientStateTests(unittest.TestCase):
    @staticmethod
    def _clear_synthetic_modules() -> None:
        for name in _SYNTHETIC_MODULES:
            sys.modules.pop(name, None)

    def _measure(self, root: Path):
        (root / "src").mkdir()
        (root / "tests").mkdir()
        source = root / "src" / "access.py"
        source.write_text(_SOURCE, encoding="utf-8")
        (root / "tests" / "test_access.py").write_text(
            _TESTS,
            encoding="utf-8",
        )
        source_sha256 = hashlib.sha256(source.read_bytes()).hexdigest()
        args = argparse.Namespace(
            start_directory="tests",
            pattern="test*.py",
            top_level_directory=None,
            test_name=[_SELECTOR],
            verbosity=0,
        )
        previous = Path.cwd()
        previous_sys_path = list(sys.path)
        self._clear_synthetic_modules()
        try:
            os.chdir(root)
            suite = coveragepy_probe._load_suite(args)
            target = {
                "path": "src/access.py",
                "symbol": "is_admin",
                "source_sha256": source_sha256,
                "target_lines": [2],
            }
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
            self._clear_synthetic_modules()
            sys.path[:] = previous_sys_path
            os.chdir(previous)

    @staticmethod
    def _coverage_environment() -> dict[str, str]:
        return {
            key: value
            for key, value in os.environ.items()
            if key.startswith("COVERAGE_")
        }

    @staticmethod
    def _clear_coverage_environment() -> None:
        for key in tuple(os.environ):
            if key.startswith("COVERAGE_"):
                os.environ.pop(key, None)

    def test_coverage_environment_variable_forces_indeterminate_measurement(self) -> None:
        previous = os.environ.get("COVERAGE_RCFILE")
        os.environ["COVERAGE_RCFILE"] = "/tmp/ambient-coveragerc"
        try:
            with tempfile.TemporaryDirectory() as directory:
                result, receipt = self._measure(Path(directory))
        finally:
            if previous is None:
                os.environ.pop("COVERAGE_RCFILE", None)
            else:
                os.environ["COVERAGE_RCFILE"] = previous

        self.assertTrue(result.wasSuccessful())
        self.assertEqual(receipt["measurement_status"], "indeterminate")
        self.assertEqual(
            receipt["measurement_error"],
            "ambient_coverage_environment",
        )
        self.assertIsNone(receipt["measured_files"])
        self.assertIsNone(receipt["statement_evidence"])
        self.assertIsNone(receipt["branch_evidence"])
        self.assertIsNone(receipt["context_evidence"])

    def test_preexisting_active_collector_forces_indeterminate_measurement(self) -> None:
        # Starting Coverage.py may itself create implementation-selection
        # COVERAGE_* variables. This test isolates only the active-collector
        # boundary so the ambient-environment boundary remains a separate test.
        previous_environment = self._coverage_environment()
        self._clear_coverage_environment()
        ambient = coverage.Coverage(data_file=None, config_file=False)
        ambient.start()
        self._clear_coverage_environment()
        try:
            with tempfile.TemporaryDirectory() as directory:
                result, receipt = self._measure(Path(directory))
        finally:
            ambient.stop()
            self._clear_coverage_environment()
            os.environ.update(previous_environment)

        self.assertTrue(result.wasSuccessful())
        self.assertEqual(receipt["measurement_status"], "indeterminate")
        self.assertEqual(
            receipt["measurement_error"],
            "coveragepy_already_active",
        )
        self.assertIsNone(receipt["measured_files"])
        self.assertIsNone(receipt["statement_evidence"])
        self.assertIsNone(receipt["branch_evidence"])
        self.assertIsNone(receipt["context_evidence"])


if __name__ == "__main__":
    unittest.main()
