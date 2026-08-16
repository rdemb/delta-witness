from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from deltawitness._dw001_pilot_execution import _publish_staging


class DW001DevelopmentPilotAtomicPublishTests(unittest.TestCase):
    def test_existing_empty_destination_is_not_partially_populated_on_publish_failure(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            staging = root / "staging"
            output = root / "output"
            staging.mkdir()
            output.mkdir()
            (staging / "plan.json").write_text("{}\n", encoding="utf-8")
            cases = staging / "cases"
            cases.mkdir()
            (cases / "case.json").write_text("{}\n", encoding="utf-8")

            original_replace = Path.replace

            def fail_only_atomic_publish(
                path: Path,
                target: Path,
            ) -> Path:
                if path == staging:
                    raise OSError("injected final rename failure")
                return original_replace(path, target)

            with patch.object(Path, "replace", new=fail_only_atomic_publish):
                with self.assertRaisesRegex(OSError, "injected final rename failure"):
                    _publish_staging(staging, output, True)

            self.assertFalse(output.exists())
            self.assertTrue((staging / "plan.json").is_file())
            self.assertTrue((staging / "cases" / "case.json").is_file())


if __name__ == "__main__":
    unittest.main()
