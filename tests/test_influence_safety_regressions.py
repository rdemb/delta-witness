from __future__ import annotations

from contextlib import redirect_stderr
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from deltawitness.cli import main
from deltawitness.config import load_config
from deltawitness.errors import GitError
from deltawitness.influence import analyze_patch_influence
from deltawitness.matrix import verify_repository


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


def initialize(repo: Path) -> None:
    run(repo, "git", "init", "-b", "main")
    run(repo, "git", "config", "user.email", "test@example.invalid")
    run(repo, "git", "config", "user.name", "DeltaWitness Test")
    (repo / "src").mkdir()
    (repo / "tests").mkdir()


def commit_all(repo: Path, message: str) -> str:
    run(repo, "git", "add", ".")
    run(repo, "git", "commit", "-m", message)
    return run(repo, "git", "rev-parse", "HEAD")


def write_external_spec(root: Path) -> Path:
    spec = root / "deltawitness.toml"
    spec.write_text(
        "[paths]\n"
        "code = ['src/**']\n"
        "tests = ['tests/**']\n"
        "documentation = ['docs/**']\n\n"
        "[[claim]]\n"
        "id = 'regression'\n"
        "description = 'Exercise prerequisite outcome and path-materialization boundaries.'\n"
        f"command = [{sys.executable!r}, 'tests/check.py']\n"
        "timeout_seconds = 30\n\n"
        "[claim.expect]\n"
        "base_base = 'pass'\n"
        "base_candidate = 'fail'\n"
        "candidate_base = 'pass'\n"
        "candidate_candidate = 'pass'\n",
        encoding="utf-8",
    )
    return spec


def create_constant_exit_fixture(root: Path, exit_code: int) -> tuple[Path, str, str, Path]:
    repo = root / "repo"
    repo.mkdir()
    initialize(repo)
    (repo / "src" / "value.py").write_text("VALUE = 'base'\n", encoding="utf-8")
    (repo / "tests" / "check.py").write_text(
        f"raise SystemExit({exit_code})\n",
        encoding="utf-8",
    )
    base = commit_all(repo, "base")

    (repo / "src" / "value.py").write_text("VALUE = 'candidate'\n", encoding="utf-8")
    (repo / "tests" / "check.py").write_text(
        f"# candidate test revision\nraise SystemExit({exit_code})\n",
        encoding="utf-8",
    )
    head = commit_all(repo, "candidate")
    return repo, base, head, write_external_spec(root)


def create_file_directory_transition_fixture(
    root: Path,
) -> tuple[Path, str, str, Path]:
    repo = root / "repo"
    repo.mkdir()
    initialize(repo)
    (repo / "src" / "node").write_text("base file\n", encoding="utf-8")
    (repo / "tests" / "check.py").write_text(
        "raise SystemExit(0)\n",
        encoding="utf-8",
    )
    base = commit_all(repo, "base file")

    (repo / "src" / "node").unlink()
    (repo / "src" / "node").mkdir()
    (repo / "src" / "node" / "value.py").write_text(
        "VALUE = 'candidate'\n",
        encoding="utf-8",
    )
    (repo / "tests" / "check.py").write_text(
        "# candidate test revision\nraise SystemExit(0)\n",
        encoding="utf-8",
    )
    head = commit_all(repo, "candidate directory")
    return repo, base, head, write_external_spec(root)


class InfluenceSafetyRegressionTests(unittest.TestCase):
    def test_matrix_rejects_overlapping_paths_before_worktree_materialization(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo, base, head, spec = create_file_directory_transition_fixture(Path(directory))
            config = load_config(spec)
            with patch(
                "deltawitness.matrix.worktree",
                side_effect=AssertionError("matrix worktree construction must not start"),
            ) as worktree_mock:
                with self.assertRaisesRegex(
                    GitError,
                    "overlap through a file/directory transition",
                ):
                    verify_repository(repo, base, head, config)
            worktree_mock.assert_not_called()

    def test_influence_rejects_overlapping_paths_before_canonical_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo, base, head, spec = create_file_directory_transition_fixture(Path(directory))
            config = load_config(spec)
            with patch(
                "deltawitness.influence.verify_repository",
                side_effect=AssertionError("canonical matrix must not start"),
            ) as verify_mock:
                with self.assertRaisesRegex(
                    GitError,
                    "overlap through a file/directory transition",
                ):
                    analyze_patch_influence(repo, base, head, config)
            verify_mock.assert_not_called()

    def test_influence_cli_returns_one_for_complete_unsupported_prerequisite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo, base, head, spec = create_constant_exit_fixture(Path(directory), 0)
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                exit_code = main(
                    [
                        "influence",
                        "--repo",
                        str(repo),
                        "--base",
                        base,
                        "--head",
                        head,
                        "--spec",
                        str(spec),
                    ]
                )

        self.assertEqual(exit_code, 1)
        self.assertIn("unsupported", stderr.getvalue().lower())

    def test_influence_cli_keeps_two_for_incomplete_prerequisite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo, base, head, spec = create_constant_exit_fixture(Path(directory), 3)
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                exit_code = main(
                    [
                        "influence",
                        "--repo",
                        str(repo),
                        "--base",
                        base,
                        "--head",
                        head,
                        "--spec",
                        str(spec),
                    ]
                )

        self.assertEqual(exit_code, 2)
        self.assertIn("complete", stderr.getvalue().lower())


if __name__ == "__main__":
    unittest.main()
