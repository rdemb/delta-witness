from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from deltawitness.config import load_config
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


class LiteralPathspecIntegrationTests(unittest.TestCase):
    @unittest.skipIf(os.name != "posix", "POSIX filename semantics required")
    def test_git_pathspec_magic_is_treated_as_a_literal_filename(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            run(repo, "git", "init", "-b", "main")
            run(repo, "git", "config", "user.email", "test@example.invalid")
            run(repo, "git", "config", "user.name", "DeltaWitness Test")
            (repo / "src").mkdir()
            (repo / "src" / "value.txt").write_text("base\n", encoding="utf-8")
            magic_path = repo / ":(glob)**"
            magic_path.write_text("base\n", encoding="utf-8")
            spec = repo / "deltawitness.toml"
            command = (
                "from pathlib import Path; import sys; "
                "sys.exit(Path('src/value.txt').read_text() != Path(':(glob)**').read_text())"
            )
            spec.write_text(
                "[paths]\n"
                "code = ['src/**']\n"
                "tests = [':(glob)**']\n"
                "documentation = ['deltawitness.toml']\n\n"
                "[[claim]]\n"
                "id = 'literal-pathspec'\n"
                "description = 'Git pathspec magic in a filename must not broaden the overlay.'\n"
                f"command = [{sys.executable!r}, '-c', {command!r}]\n"
                "timeout_seconds = 30\n\n"
                "[claim.expect]\n"
                "base_base = 'pass'\n"
                "base_candidate = 'fail'\n"
                "candidate_base = 'fail'\n"
                "candidate_candidate = 'pass'\n",
                encoding="utf-8",
            )
            run(repo, "git", "add", ".")
            run(repo, "git", "commit", "-m", "base")
            base = run(repo, "git", "rev-parse", "HEAD")

            (repo / "src" / "value.txt").write_text("candidate\n", encoding="utf-8")
            magic_path.write_text("candidate\n", encoding="utf-8")
            run(repo, "git", "add", ".")
            run(repo, "git", "commit", "-m", "candidate")
            head = run(repo, "git", "rev-parse", "HEAD")

            report = verify_repository(repo, base, head, load_config(spec))

        self.assertTrue(report.complete)
        self.assertTrue(report.supported)
        self.assertEqual(
            [state.observed for state in report.claims[0].states],
            ["pass", "fail", "fail", "pass"],
        )


if __name__ == "__main__":
    unittest.main()
