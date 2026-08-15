from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from deltawitness.errors import GitError
from deltawitness.gitops import (
    _validate_changed_path,
    changed_paths,
    ensure_supported_entries,
    git_metadata_path,
    resolve_ref,
)


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
        raise AssertionError(f"Command failed: {args}\n{completed.stderr}")
    return completed.stdout.strip()


class GitOperationsTests(unittest.TestCase):
    @unittest.skipIf(os.name != "posix", "POSIX filename semantics required")
    def test_changed_paths_preserves_tabs_and_newlines(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            run(repo, "git", "init", "-b", "main")
            run(repo, "git", "config", "user.email", "test@example.invalid")
            run(repo, "git", "config", "user.name", "DeltaWitness Test")
            (repo / "base.txt").write_text("base\n", encoding="utf-8")
            run(repo, "git", "add", ".")
            run(repo, "git", "commit", "-m", "base")
            base = run(repo, "git", "rev-parse", "HEAD")

            tab_name = "tests/tab\tname.py"
            newline_name = "src/line\nname.py"
            (repo / "tests").mkdir()
            (repo / "src").mkdir()
            (repo / tab_name).write_text("assert True\n", encoding="utf-8")
            (repo / newline_name).write_text("value = 1\n", encoding="utf-8")
            run(repo, "git", "add", ".")
            run(repo, "git", "commit", "-m", "add unusual paths")
            head = run(repo, "git", "rev-parse", "HEAD")

            changes = changed_paths(repo, base, head)

        self.assertIn(("A", tab_name), changes)
        self.assertIn(("A", newline_name), changes)

    def test_option_like_ref_is_treated_as_data(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            run(repo, "git", "init", "-b", "main")
            run(repo, "git", "config", "user.email", "test@example.invalid")
            run(repo, "git", "config", "user.name", "DeltaWitness Test")
            (repo / "base.txt").write_text("base\n", encoding="utf-8")
            run(repo, "git", "add", ".")
            run(repo, "git", "commit", "-m", "base")

            with self.assertRaises(GitError):
                resolve_ref(repo, "--help")

    def test_git_metadata_path_stays_outside_the_working_tree(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            run(repo, "git", "init", "-b", "main")
            run(repo, "git", "config", "user.email", "test@example.invalid")
            run(repo, "git", "config", "user.name", "DeltaWitness Test")
            (repo / "base.txt").write_text("base\n", encoding="utf-8")
            run(repo, "git", "add", ".")
            run(repo, "git", "commit", "-m", "base")

            report_path = git_metadata_path(repo, "deltawitness/report.json")

        self.assertNotEqual(report_path.parent.parent, repo)
        self.assertEqual(report_path.name, "report.json")

    def test_rejects_cross_platform_unsafe_changed_paths(self) -> None:
        for path in ("../escape.py", "src/../escape.py", ".git/config", "src\\escape.py"):
            with self.subTest(path=path), self.assertRaises(GitError):
                _validate_changed_path(path)

    def test_git_environment_ignores_external_git_dir_override(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as hostile:
            repo = Path(directory)
            run(repo, "git", "init", "-b", "main")
            run(repo, "git", "config", "user.email", "test@example.invalid")
            run(repo, "git", "config", "user.name", "DeltaWitness Test")
            (repo / "base.txt").write_text("base\n", encoding="utf-8")
            run(repo, "git", "add", ".")
            run(repo, "git", "commit", "-m", "base")
            expected = run(repo, "git", "rev-parse", "HEAD")

            previous = os.environ.get("GIT_DIR")
            os.environ["GIT_DIR"] = hostile
            try:
                observed = resolve_ref(repo, "HEAD")
            finally:
                if previous is None:
                    os.environ.pop("GIT_DIR", None)
                else:
                    os.environ["GIT_DIR"] = previous

        self.assertEqual(observed, expected)

    @unittest.skipIf(os.name != "posix", "symbolic-link semantics required")
    def test_rejects_changed_symbolic_link_entries(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            run(repo, "git", "init", "-b", "main")
            run(repo, "git", "config", "user.email", "test@example.invalid")
            run(repo, "git", "config", "user.name", "DeltaWitness Test")
            (repo / "src").mkdir()
            (repo / "tests").mkdir()
            (repo / "src" / "value.py").write_text("VALUE = 'base'\n", encoding="utf-8")
            os.symlink("missing-target.py", repo / "tests" / "test_value.py")
            run(repo, "git", "add", ".")
            run(repo, "git", "commit", "-m", "base with symbolic-link test entry")
            base = run(repo, "git", "rev-parse", "HEAD")

            (repo / "src" / "value.py").write_text("VALUE = 'candidate'\n", encoding="utf-8")
            (repo / "tests" / "test_value.py").unlink()
            (repo / "tests" / "test_value.py").write_text("assert True\n", encoding="utf-8")
            run(repo, "git", "add", ".")
            run(repo, "git", "commit", "-m", "replace symbolic link with test file")
            head = run(repo, "git", "rev-parse", "HEAD")

            with self.assertRaisesRegex(GitError, "symbolic-link"):
                ensure_supported_entries(
                    repo,
                    base,
                    head,
                    ["src/value.py", "tests/test_value.py"],
                )


if __name__ == "__main__":
    unittest.main()
