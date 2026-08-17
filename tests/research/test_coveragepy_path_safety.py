from __future__ import annotations

import hashlib
import os
from pathlib import Path
import tempfile
import unittest

import deltawitness.coveragepy_probe as coveragepy_probe
from deltawitness.coveragepy_probe import CoveragePyProbeError


_SOURCE = "def is_admin(user):\n    return True\n"


class CoveragePyPathSafetyTests(unittest.TestCase):
    def test_target_rejects_final_symbolic_link_before_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            source = root / "src" / "real_access.py"
            source.write_text(_SOURCE, encoding="utf-8")
            linked = root / "src" / "access.py"
            linked.symlink_to(source.name)
            source_sha256 = hashlib.sha256(source.read_bytes()).hexdigest()
            previous = Path.cwd()
            try:
                os.chdir(root)
                with self.assertRaisesRegex(
                    CoveragePyProbeError,
                    "symbolic-link",
                ):
                    coveragepy_probe._target_source(
                        "src/access.py",
                        source_sha256,
                    )
            finally:
                os.chdir(previous)

    def test_target_rejects_symbolic_link_ancestor_before_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            real_src = root / "real-src"
            real_src.mkdir()
            source = real_src / "access.py"
            source.write_text(_SOURCE, encoding="utf-8")
            (root / "src").symlink_to(real_src.name, target_is_directory=True)
            source_sha256 = hashlib.sha256(source.read_bytes()).hexdigest()
            previous = Path.cwd()
            try:
                os.chdir(root)
                with self.assertRaisesRegex(
                    CoveragePyProbeError,
                    "symbolic-link",
                ):
                    coveragepy_probe._target_source(
                        "src/access.py",
                        source_sha256,
                    )
            finally:
                os.chdir(previous)

    def test_output_rejects_absolute_traversal_and_preexisting_link_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            previous = Path.cwd()
            try:
                os.chdir(root)
                for raw in (
                    str(root / coveragepy_probe.COVERAGE_OUTPUT_BASENAME),
                    f"../{coveragepy_probe.COVERAGE_OUTPUT_BASENAME}",
                    "nested/.deltawitness-coveragepy.json",
                ):
                    with self.subTest(raw=raw):
                        with self.assertRaises(CoveragePyProbeError):
                            coveragepy_probe._output_destination(raw)

                target = root / "real.json"
                target.write_text("{}", encoding="utf-8")
                output = root / coveragepy_probe.COVERAGE_OUTPUT_BASENAME
                output.symlink_to(target.name)
                with self.assertRaisesRegex(
                    CoveragePyProbeError,
                    "must not already exist",
                ):
                    coveragepy_probe._output_destination(
                        coveragepy_probe.COVERAGE_OUTPUT_BASENAME
                    )
            finally:
                os.chdir(previous)


if __name__ == "__main__":
    unittest.main()
