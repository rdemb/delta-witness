from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from deltawitness.config import load_config
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


def create_fixture(repo: Path) -> tuple[str, str, Path]:
    run(repo, "git", "init", "-b", "main")
    run(repo, "git", "config", "user.email", "test@example.invalid")
    run(repo, "git", "config", "user.name", "DeltaWitness Test")
    (repo / "src").mkdir()
    (repo / "tests").mkdir()

    (repo / "src" / "access.py").write_text(
        "def is_admin(user):\n    return bool(user.get('role'))\n",
        encoding="utf-8",
    )
    (repo / "src" / "collateral.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "tests" / "test_access.py").write_text(
        "import sys, unittest\n"
        "sys.path.insert(0, 'src')\n"
        "from access import is_admin\n\n"
        "class AccessTests(unittest.TestCase):\n"
        "    def test_admin(self):\n"
        "        self.assertTrue(is_admin({'role': 'admin'}))\n",
        encoding="utf-8",
    )
    base = commit_all(repo, "base")

    (repo / "src" / "access.py").write_text(
        "def is_admin(user):\n    return user.get('role') == 'admin'\n",
        encoding="utf-8",
    )
    (repo / "src" / "collateral.py").write_text("VALUE = 2\n", encoding="utf-8")
    (repo / "tests" / "test_access.py").write_text(
        "import sys, unittest\n"
        "sys.path.insert(0, 'src')\n"
        "from access import is_admin\n\n"
        "class AccessTests(unittest.TestCase):\n"
        "    def test_admin(self):\n"
        "        self.assertTrue(is_admin({'role': 'admin'}))\n\n"
        "    def test_viewer(self):\n"
        "        self.assertFalse(is_admin({'role': 'viewer'}))\n",
        encoding="utf-8",
    )
    commit_all(repo, "candidate")

    spec = repo / "deltawitness.toml"
    spec.write_text(
        "[paths]\n"
        "code = ['src/**']\n"
        "tests = ['tests/**']\n"
        "documentation = ['deltawitness.toml']\n\n"
        "[[claim]]\n"
        "id = 'deterministic-regression'\n"
        "description = 'Repeated analysis must preserve semantic identities.'\n"
        "observer = 'outcome-receipt-v1'\n"
        f"command = [{sys.executable!r}, '-m', 'deltawitness.unittest_probe', "
        "'--start-directory', 'tests', '--verbosity', '0']\n"
        "timeout_seconds = 30\n\n"
        "[claim.expect]\n"
        "base_base = 'pass'\n"
        "base_candidate = 'fail'\n"
        "candidate_base = 'pass'\n"
        "candidate_candidate = 'pass'\n",
        encoding="utf-8",
    )
    head = commit_all(repo, "add specification")
    return base, head, spec


class InfluenceReproducibilityTests(unittest.TestCase):
    def test_repeated_analysis_preserves_semantic_digest_and_git_objects(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            base, head, spec = create_fixture(repo)
            config = load_config(spec)
            first = analyze_patch_influence(repo, base, head, config)
            second = analyze_patch_influence(repo, base, head, config)

        self.assertTrue(first.attribution_available)
        self.assertTrue(second.attribution_available)
        self.assertEqual(first.influence_sha256, second.influence_sha256)
        self.assertEqual(first.matrix_reference, second.matrix_reference)
        self.assertEqual(first.metrics, second.metrics)
        self.assertEqual(
            [
                (
                    coalition.mask,
                    coalition.implementation_tree_sha,
                    coalition.implementation_commit_sha,
                    coalition.candidate_tests_tree_sha,
                    coalition.candidate_tests_commit_sha,
                    coalition.status,
                )
                for coalition in first.coalitions
            ],
            [
                (
                    coalition.mask,
                    coalition.implementation_tree_sha,
                    coalition.implementation_commit_sha,
                    coalition.candidate_tests_tree_sha,
                    coalition.candidate_tests_commit_sha,
                    coalition.status,
                )
                for coalition in second.coalitions
            ],
        )
        self.assertTrue(all(anchor["tree_match"] for anchor in first.anchors))
        self.assertTrue(all(anchor["consistent"] for anchor in first.anchors))


if __name__ == "__main__":
    unittest.main()
