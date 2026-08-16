from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from deltawitness.dw001_pilot import (
    DW001PilotError,
    build_development_pilot_plan,
    run_development_pilot,
)


class DW001DevelopmentPilotPrepublicationExactSetTests(unittest.TestCase):
    def test_unexpected_staged_file_prevents_final_publication(self) -> None:
        plan = build_development_pilot_plan(
            protocol_commit_sha="a" * 40,
            implementation_commit_sha="b" * 40,
        )

        def injected_runner(
            _plan: object,
            output_directory: Path,
        ) -> dict[str, object]:
            destination = Path(output_directory)
            destination.mkdir()
            (destination / "unexpected.json").write_text("{}\n", encoding="utf-8")
            return {"injected": True}

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "published"
            with patch(
                "deltawitness.dw001_pilot.run_pilot",
                new=injected_runner,
            ):
                with self.assertRaisesRegex(
                    DW001PilotError,
                    "unexpected.json",
                ):
                    run_development_pilot(plan, output)

            self.assertFalse(output.exists())
            self.assertEqual(list(Path(directory).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
