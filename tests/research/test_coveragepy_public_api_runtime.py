from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import deltawitness.coveragepy_probe as coveragepy_probe
from deltawitness.coveragepy_contract import COVERAGEPY_MANIFEST_SHA256
from deltawitness.execution import run_command


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
_SOURCE_SHA256 = (
    "7bfbd2d0a642c6d7f7da05ece2f4464d31df53a28d1ffed12c5752bc492d8965"
)
_CONTEXT_ID = (
    "dw001-coveragepy-v1:strong-authorization-oracle-v1:"
    "test_access.AccessTests.test_admin_is_allowed"
)
_BINDING = "a" * 64
_SYNTHETIC_MODULES = ("access", "test_access", "tests.test_access")
_DIAGNOSTIC_CHILD = r'''
import os
import sys
import deltawitness.coveragepy_probe as probe


def expose_internal_failure(**kwargs):
    error = sys.exc_info()[1]
    if error is None:
        raise RuntimeError("indeterminate receipt without active exception")
    message = str(error).replace(os.getcwd(), "${ROOT}")
    raise RuntimeError(f"{type(error).__name__}: {message}")


probe._indeterminate_receipt = expose_internal_failure
try:
    result = probe.main(sys.argv[1:])
except Exception as error:
    print(
        f"COVERAGEPY_DIAGNOSTIC:{type(error).__name__}:{error}",
        file=sys.stderr,
    )
    result = 9
raise SystemExit(result)
'''


class CoveragePyPublicApiRuntimeTests(unittest.TestCase):
    def _materialize(self, root: Path) -> None:
        (root / "src").mkdir()
        (root / "tests").mkdir()
        (root / "src" / "access.py").write_text(
            _SOURCE,
            encoding="utf-8",
        )
        (root / "tests" / "test_access.py").write_text(
            _TESTS,
            encoding="utf-8",
        )

    @staticmethod
    def _clear_synthetic_modules() -> None:
        for name in _SYNTHETIC_MODULES:
            sys.modules.pop(name, None)

    def test_fixed_public_api_measurement_is_complete(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="deltawitness-coveragepy-api-smoke-"
        ) as directory:
            root = Path(directory)
            self._materialize(root)
            args = argparse.Namespace(
                start_directory="tests",
                pattern="test*.py",
                top_level_directory=None,
                test_name=[
                    "test_access.AccessTests.test_admin_is_allowed"
                ],
                verbosity=0,
            )
            previous = Path.cwd()
            previous_sys_path = list(sys.path)
            self._clear_synthetic_modules()
            try:
                os.chdir(root)
                suite = coveragepy_probe._load_suite(args)
                target_path = (root / "src" / "access.py").resolve()
                target = {
                    "path": "src/access.py",
                    "symbol": "is_admin",
                    "source_sha256": _SOURCE_SHA256,
                    "target_lines": [2],
                }
                configuration = coveragepy_probe._configuration(_CONTEXT_ID)

                def expose_internal_failure(**kwargs):
                    error = sys.exc_info()[1]
                    if error is None:
                        self.fail(
                            "Coverage.py indeterminate receipt was built "
                            "without an active internal exception"
                        )
                    message = str(error).replace(str(root), "${ROOT}")
                    self.fail(
                        "Coverage.py public API measurement failed: "
                        f"{type(error).__name__}: {message}"
                    )

                with patch.object(
                    coveragepy_probe,
                    "_indeterminate_receipt",
                    side_effect=expose_internal_failure,
                ):
                    result, receipt = coveragepy_probe._measure(
                        suite=suite,
                        args=args,
                        target_path=target_path,
                        target_path_text="src/access.py",
                        target=target,
                        context_id=_CONTEXT_ID,
                        configuration=configuration,
                        binding=_BINDING,
                    )
            finally:
                self._clear_synthetic_modules()
                sys.path[:] = previous_sys_path
                os.chdir(previous)

        self.assertTrue(result.wasSuccessful())
        self.assertEqual(receipt["measurement_status"], "complete")
        self.assertIsNone(receipt["measurement_error"])
        self.assertEqual(
            receipt["distribution"]["manifest_sha256"],
            COVERAGEPY_MANIFEST_SHA256,
        )
        self.assertEqual(
            receipt["statement_evidence"]["target_executed"],
            [2],
        )
        self.assertEqual(
            receipt["context_evidence"]["measured_contexts"],
            [_CONTEXT_ID],
        )
        self.assertTrue(receipt["context_evidence"]["partition_valid"])

    def test_fixed_public_api_measurement_is_complete_in_isolated_child(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="deltawitness-coveragepy-child-smoke-"
        ) as directory:
            root = Path(directory)
            self._materialize(root)
            receipt_path = root / "outcome-receipt.json"
            previous_path = os.environ.get("DELTAWITNESS_RECEIPT_PATH")
            previous_binding = os.environ.get(
                "DELTAWITNESS_RECEIPT_BINDING"
            )
            os.environ["DELTAWITNESS_RECEIPT_PATH"] = str(receipt_path)
            os.environ["DELTAWITNESS_RECEIPT_BINDING"] = _BINDING
            try:
                process = run_command(
                    [
                        "python",
                        "-c",
                        _DIAGNOSTIC_CHILD,
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
                        "--context-id",
                        _CONTEXT_ID,
                        "--coverage-output",
                        coveragepy_probe.COVERAGE_OUTPUT_BASENAME,
                    ],
                    state="coveragepy-public-api-child-smoke",
                    cwd=root,
                    timeout_seconds=30,
                    pass_env=(
                        "DELTAWITNESS_RECEIPT_PATH",
                        "DELTAWITNESS_RECEIPT_BINDING",
                    ),
                    include_output=True,
                    observer="exit-code-v1",
                    receipt_binding=None,
                )
            finally:
                if previous_path is None:
                    os.environ.pop("DELTAWITNESS_RECEIPT_PATH", None)
                else:
                    os.environ["DELTAWITNESS_RECEIPT_PATH"] = previous_path
                if previous_binding is None:
                    os.environ.pop("DELTAWITNESS_RECEIPT_BINDING", None)
                else:
                    os.environ[
                        "DELTAWITNESS_RECEIPT_BINDING"
                    ] = previous_binding

            self.assertFalse(process.timed_out)
            self.assertEqual(
                process.return_code,
                0,
                process.stderr or "isolated child failed without diagnostics",
            )
            receipt = coveragepy_probe.load_coverage_receipt(
                root / coveragepy_probe.COVERAGE_OUTPUT_BASENAME,
                expected_binding=_BINDING,
                expected_target={
                    "path": "src/access.py",
                    "symbol": "is_admin",
                    "source_sha256": _SOURCE_SHA256,
                    "target_lines": [2],
                },
                expected_context_id=_CONTEXT_ID,
                expected_configuration=coveragepy_probe._configuration(
                    _CONTEXT_ID
                ),
                expected_manifest_sha256=COVERAGEPY_MANIFEST_SHA256,
            )
        self.assertEqual(receipt["measurement_status"], "complete")


if __name__ == "__main__":
    unittest.main()
