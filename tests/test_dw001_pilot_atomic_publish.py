from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from deltawitness.dw001_pilot import (
    DW001PilotError,
    build_development_pilot_plan,
    run_development_pilot,
)


class DW001DevelopmentPilotAtomicPublishTests(unittest.TestCase):
    def test_existing_empty_destination_is_rejected_before_execution(self) -> None:
        plan = build_development_pilot_plan(
            protocol_commit_sha="a" * 40,
            implementation_commit_sha="b" * 40,
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "output"
            output.mkdir()

            with self.assertRaisesRegex(
                DW001PilotError,
                "must be absent for atomic publication",
            ):
                run_development_pilot(plan, output)

            self.assertTrue(output.is_dir())
            self.assertEqual(list(output.iterdir()), [])
            self.assertEqual(list(root.iterdir()), [output])


if __name__ == "__main__":
    unittest.main()
