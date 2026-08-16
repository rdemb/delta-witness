from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest

from deltawitness.dw001_scenarios import (
    DW001ScenarioError,
    build_fixture_descriptor,
    materialize_synthetic_fixture,
)


class DW001ScenarioDestinationSafetyTests(unittest.TestCase):
    @unittest.skipIf(os.name != "posix", "symbolic-link destination semantics are POSIX-specific")
    def test_symbolic_link_destination_is_rejected_without_touching_target(self) -> None:
        descriptor = build_fixture_descriptor(
            scenario_id="generator-symlink-destination-001",
            family_id="valid-discriminating-regression",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target"
            target.mkdir()
            destination = root / "destination"
            destination.symlink_to(target, target_is_directory=True)

            with self.assertRaisesRegex(DW001ScenarioError, "symbolic link"):
                materialize_synthetic_fixture(descriptor, destination)

            self.assertEqual(list(target.iterdir()), [])
            self.assertTrue(destination.is_symlink())


if __name__ == "__main__":
    unittest.main()
