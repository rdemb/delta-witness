from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from deltawitness.coveragepy_contract import COVERAGEPY_WHEEL_FILENAME


_ROOT = Path(__file__).resolve().parents[1]
_SCRIPT = _ROOT / "scripts" / "verify_coveragepy_artifact.py"


class CoveragePyArtifactCliTests(unittest.TestCase):
    def _run(self, path: Path) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(
            [sys.executable, str(_SCRIPT), str(path)],
            cwd=_ROOT,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_missing_artifact_is_a_harness_or_configuration_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / COVERAGEPY_WHEEL_FILENAME
            completed = self._run(missing)

        self.assertEqual(
            completed.returncode,
            2,
            completed.stderr.decode("utf-8", errors="replace"),
        )
        self.assertIn(
            b"cannot be inspected",
            completed.stderr,
        )

    def test_present_but_wrong_artifact_remains_an_unsupported_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / COVERAGEPY_WHEEL_FILENAME
            artifact.write_bytes(b"not-the-reviewed-wheel")
            completed = self._run(artifact)

        self.assertEqual(
            completed.returncode,
            1,
            completed.stderr.decode("utf-8", errors="replace"),
        )
        self.assertIn(b"SHA-256", completed.stderr)


if __name__ == "__main__":
    unittest.main()
