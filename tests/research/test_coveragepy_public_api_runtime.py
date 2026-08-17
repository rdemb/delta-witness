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


class CoveragePyPublicApiRuntimeTests(unittest.TestCase):
    def test_fixed_public_api_measurement_is_complete(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="deltawitness-coveragepy-api-smoke-"
        ) as directory:
            root = Path(directory)
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
                        binding="a" * 64,
                    )
            finally:
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


if __name__ == "__main__":
    unittest.main()
