from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from deltawitness.config import load_config
from deltawitness.errors import VerificationError
from deltawitness.influence import analyze_patch_influence


def run(cwd: Path, *args: str) -> str:
    completed = subprocess.run(
        list(args),
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"Command failed: {args}\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )
    return completed.stdout.strip()


def commit_all(repo: Path, message: str) -> str:
    run(repo, "git", "add", ".")
    run(repo, "git", "commit", "-m", message)
    return run(repo, "git", "rev-parse", "HEAD")


def initialize(repo: Path) -> None:
    run(repo, "git", "init", "-b", "main")
    run(repo, "git", "config", "user.email", "test@example.invalid")
    run(repo, "git", "config", "user.name", "DeltaWitness Test")
    (repo / "src").mkdir()
    (repo / "tests").mkdir()


def write_spec(
    repo: Path,
    marker: Path,
    *,
    canonical: bool,
) -> Path:
    base_candidate = "fail" if canonical else "pass"
    command = (
        "from pathlib import Path; "
        f"Path({str(marker)!r}).write_text('executed', encoding='utf-8')"
    )
    spec = repo / "deltawitness.toml"
    spec.write_text(
        "[paths]\n"
        "code = ['src/**']\n"
        "tests = ['tests/**']\n"
        "documentation = ['deltawitness.toml']\n\n"
        "[[claim]]\n"
        "id = 'must-not-run'\n"
        "description = 'Preflight must reject this analysis before command execution.'\n"
        f"command = [{sys.executable!r}, '-c', {command!r}]\n"
        "timeout_seconds = 30\n\n"
        "[claim.expect]\n"
        "base_base = 'pass'\n"
        f"base_candidate = {base_candidate!r}\n"
        "candidate_base = 'pass'\n"
        "candidate_candidate = 'pass'\n",
        encoding="utf-8",
    )
    return spec


class InfluencePreflightTests(unittest.TestCase):
    def test_more_than_eight_code_paths_is_rejected_before_matrix_execution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            repo.mkdir()
            initialize(repo)
            for index in range(9):
                (repo / "src" / f"path_{index}.py").write_text(
                    f"VALUE = {index}\n",
                    encoding="utf-8",
                )
            (repo / "tests" / "test_paths.py").write_text(
                "import unittest\n\n"
                "class PathsTests(unittest.TestCase):\n"
                "    def test_baseline(self):\n"
                "        self.assertTrue(True)\n",
                encoding="utf-8",
            )
            base = commit_all(repo, "base")

            for index in range(9):
                (repo / "src" / f"path_{index}.py").write_text(
                    f"VALUE = {index + 100}\n",
                    encoding="utf-8",
                )
            (repo / "tests" / "test_paths.py").write_text(
                "import unittest\n\n"
                "class PathsTests(unittest.TestCase):\n"
                "    def test_candidate(self):\n"
                "        self.assertTrue(True)\n",
                encoding="utf-8",
            )
            marker = Path(directory) / "command-marker.txt"
            spec = write_spec(repo, marker, canonical=True)
            head = commit_all(repo, "candidate with nine changed code paths")

            with self.assertRaisesRegex(VerificationError, "at most 8"):
                analyze_patch_influence(repo, base, head, load_config(spec))

            self.assertFalse(marker.exists())

    def test_noncanonical_expectations_are_rejected_before_command_execution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            repo.mkdir()
            initialize(repo)
            (repo / "src" / "value.py").write_text("VALUE = 'base'\n", encoding="utf-8")
            (repo / "tests" / "test_value.py").write_text(
                "import unittest\n\n"
                "class ValueTests(unittest.TestCase):\n"
                "    def test_baseline(self):\n"
                "        self.assertTrue(True)\n",
                encoding="utf-8",
            )
            base = commit_all(repo, "base")

            (repo / "src" / "value.py").write_text("VALUE = 'candidate'\n", encoding="utf-8")
            (repo / "tests" / "test_value.py").write_text(
                "import unittest\n\n"
                "class ValueTests(unittest.TestCase):\n"
                "    def test_candidate(self):\n"
                "        self.assertTrue(True)\n",
                encoding="utf-8",
            )
            marker = Path(directory) / "command-marker.txt"
            spec = write_spec(repo, marker, canonical=False)
            head = commit_all(repo, "candidate with noncanonical expectations")

            with self.assertRaisesRegex(VerificationError, "canonical regression matrix"):
                analyze_patch_influence(repo, base, head, load_config(spec))

            self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
