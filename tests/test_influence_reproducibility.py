from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from deltawitness.config import load_config
from deltawitness.influence import InfluenceReport, analyze_patch_influence


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


def write_base_state(repo: Path) -> None:
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


def write_candidate_state(repo: Path) -> None:
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


def write_spec(repo: Path) -> Path:
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
    return spec


def create_fixture(
    repo: Path,
    *,
    specification_in_base: bool,
) -> tuple[str, str, Path]:
    initialize(repo)
    write_base_state(repo)
    spec = write_spec(repo) if specification_in_base else repo / "deltawitness.toml"
    base = commit_all(repo, "base")

    write_candidate_state(repo)
    head = commit_all(repo, "candidate")
    if not specification_in_base:
        spec = write_spec(repo)
        head = commit_all(repo, "add specification")
    return base, head, spec


def coalition_identities(report: InfluenceReport) -> list[tuple[object, ...]]:
    return [
        (
            coalition.mask,
            coalition.implementation_tree_sha,
            coalition.implementation_commit_sha,
            coalition.candidate_tests_tree_sha,
            coalition.candidate_tests_commit_sha,
            coalition.status,
        )
        for coalition in report.coalitions
    ]


class InfluenceReproducibilityTests(unittest.TestCase):
    def test_repeated_analysis_preserves_semantic_digest_and_git_objects(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            base, head, spec = create_fixture(repo, specification_in_base=True)
            config = load_config(spec)
            first = analyze_patch_influence(repo, base, head, config)
            second = analyze_patch_influence(repo, base, head, config)

        self.assertTrue(first.attribution_available)
        self.assertTrue(second.attribution_available)
        self.assertEqual(first.classification["documentation"], [])
        self.assertEqual(first.influence_sha256, second.influence_sha256)
        self.assertEqual(first.matrix_reference, second.matrix_reference)
        self.assertEqual(first.metrics, second.metrics)
        self.assertEqual(coalition_identities(first), coalition_identities(second))
        self.assertTrue(all(anchor["tree_required"] for anchor in first.anchors))
        self.assertTrue(all(anchor["tree_match"] for anchor in first.anchors))
        self.assertTrue(all(anchor["consistent"] for anchor in first.anchors))

    def test_candidate_held_constant_documentation_relaxes_only_empty_tree_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            base, head, spec = create_fixture(repo, specification_in_base=False)
            config = load_config(spec)
            first = analyze_patch_influence(repo, base, head, config)
            second = analyze_patch_influence(repo, base, head, config)

        self.assertTrue(first.attribution_available)
        self.assertTrue(second.attribution_available)
        self.assertEqual(
            first.classification["documentation"],
            [
                {
                    "path": "deltawitness.toml",
                    "status": "A",
                    "category": "documentation",
                }
            ],
        )
        self.assertEqual(first.influence_sha256, second.influence_sha256)
        self.assertEqual(first.matrix_reference, second.matrix_reference)
        self.assertEqual(first.metrics, second.metrics)
        self.assertEqual(coalition_identities(first), coalition_identities(second))

        anchors = {anchor["name"]: anchor for anchor in first.anchors}
        for name in ("empty-base-tests", "empty-candidate-tests"):
            with self.subTest(anchor=name):
                self.assertFalse(anchors[name]["tree_required"])
                self.assertFalse(anchors[name]["tree_match"])
                self.assertTrue(anchors[name]["outcomes_match"])
                self.assertTrue(anchors[name]["consistent"])
        for name in ("full-base-tests", "full-candidate-tests"):
            with self.subTest(anchor=name):
                self.assertTrue(anchors[name]["tree_required"])
                self.assertTrue(anchors[name]["tree_match"])
                self.assertTrue(anchors[name]["outcomes_match"])
                self.assertTrue(anchors[name]["consistent"])


if __name__ == "__main__":
    unittest.main()
