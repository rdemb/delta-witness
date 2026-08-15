from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from deltawitness.config import load_config
from deltawitness.influence import analyze_patch_influence, influence_report_to_dict
from deltawitness.reporting import verify_report_document


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


def write_spec(repo: Path) -> Path:
    spec = repo / "deltawitness.toml"
    spec.write_text(
        "[paths]\n"
        "code = ['src/**']\n"
        "tests = ['tests/**']\n"
        "documentation = ['deltawitness.toml', 'docs/**']\n\n"
        "[[claim]]\n"
        "id = 'regression'\n"
        "description = 'Candidate tests must expose the old behavior and pass after the patch.'\n"
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
    commit_all(repo, "add witness specification")
    return spec


def create_collateral_fixture(repo: Path) -> tuple[str, str, Path]:
    initialize(repo)
    (repo / "src" / "access.py").write_text(
        "def is_admin(user):\n    return bool(user.get('role'))\n",
        encoding="utf-8",
    )
    (repo / "src" / "banner.py").write_text("VERSION = 1\n", encoding="utf-8")
    (repo / "tests" / "test_access.py").write_text(
        "import sys, unittest\n"
        "sys.path.insert(0, 'src')\n"
        "from access import is_admin\n\n"
        "class AccessTests(unittest.TestCase):\n"
        "    def test_admin_is_allowed(self):\n"
        "        self.assertTrue(is_admin({'role': 'admin'}))\n",
        encoding="utf-8",
    )
    base = commit_all(repo, "base")

    (repo / "src" / "access.py").write_text(
        "def is_admin(user):\n    return user.get('role') == 'admin'\n",
        encoding="utf-8",
    )
    (repo / "src" / "banner.py").write_text("VERSION = 2\n", encoding="utf-8")
    (repo / "tests" / "test_access.py").write_text(
        "import sys, unittest\n"
        "sys.path.insert(0, 'src')\n"
        "from access import is_admin\n\n"
        "class AccessTests(unittest.TestCase):\n"
        "    def test_admin_is_allowed(self):\n"
        "        self.assertTrue(is_admin({'role': 'admin'}))\n\n"
        "    def test_viewer_is_denied(self):\n"
        "        self.assertFalse(is_admin({'role': 'viewer'}))\n",
        encoding="utf-8",
    )
    commit_all(repo, "candidate with collateral change")
    spec = write_spec(repo)
    head = run(repo, "git", "rev-parse", "HEAD")
    return base, head, spec


def create_indeterminate_fixture(repo: Path) -> tuple[str, str, Path]:
    initialize(repo)
    (repo / "src" / "model.py").write_text(
        "def value():\n    return 'old'\n",
        encoding="utf-8",
    )
    (repo / "tests" / "test_model.py").write_text(
        "import sys, unittest\n"
        "sys.path.insert(0, 'src')\n"
        "from model import value\n\n"
        "class ModelTests(unittest.TestCase):\n"
        "    def test_value_is_text(self):\n"
        "        self.assertIsInstance(value(), str)\n",
        encoding="utf-8",
    )
    base = commit_all(repo, "base")

    (repo / "src" / "helper.py").write_text("NEW_VALUE = 'new'\n", encoding="utf-8")
    (repo / "src" / "model.py").write_text(
        "from helper import NEW_VALUE\n\n"
        "def value():\n    return NEW_VALUE\n",
        encoding="utf-8",
    )
    (repo / "tests" / "test_model.py").write_text(
        "import sys, unittest\n"
        "sys.path.insert(0, 'src')\n"
        "from model import value\n\n"
        "class ModelTests(unittest.TestCase):\n"
        "    def test_value_is_text(self):\n"
        "        self.assertIsInstance(value(), str)\n\n"
        "    def test_new_value(self):\n"
        "        self.assertEqual(value(), 'new')\n",
        encoding="utf-8",
    )
    commit_all(repo, "candidate with interacting files")
    spec = write_spec(repo)
    head = run(repo, "git", "rev-parse", "HEAD")
    return base, head, spec


def create_documentation_leakage_fixture(repo: Path) -> tuple[str, str, Path]:
    initialize(repo)
    (repo / "docs").mkdir()
    (repo / "src" / "decision.py").write_text("FIXED = False\n", encoding="utf-8")
    (repo / "docs" / "flag.txt").write_text("old\n", encoding="utf-8")
    (repo / "tests" / "test_decision.py").write_text(
        "import sys, unittest\n"
        "sys.path.insert(0, 'src')\n"
        "from decision import FIXED\n\n"
        "class DecisionTests(unittest.TestCase):\n"
        "    def test_flag_is_boolean(self):\n"
        "        self.assertIsInstance(FIXED, bool)\n",
        encoding="utf-8",
    )
    base = commit_all(repo, "base")

    (repo / "src" / "decision.py").write_text("FIXED = True\n", encoding="utf-8")
    (repo / "docs" / "flag.txt").write_text("new\n", encoding="utf-8")
    (repo / "tests" / "test_decision.py").write_text(
        "from pathlib import Path\n"
        "import sys, unittest\n"
        "sys.path.insert(0, 'src')\n"
        "from decision import FIXED\n\n"
        "class DecisionTests(unittest.TestCase):\n"
        "    def test_flag_is_boolean(self):\n"
        "        self.assertIsInstance(FIXED, bool)\n\n"
        "    def test_candidate_behavior(self):\n"
        "        documented = Path('docs/flag.txt').read_text(encoding='utf-8').strip() == 'new'\n"
        "        self.assertTrue(FIXED or documented)\n",
        encoding="utf-8",
    )
    commit_all(repo, "candidate with executable documentation dependency")
    spec = write_spec(repo)
    head = run(repo, "git", "rev-parse", "HEAD")
    return base, head, spec


class ExactInfluenceIntegrationTests(unittest.TestCase):
    def test_identifies_a_necessary_fix_and_collateral_change(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            base, head, spec = create_collateral_fixture(repo)
            report = analyze_patch_influence(repo, base, head, load_config(spec))
            document = influence_report_to_dict(report)
            valid, errors = verify_report_document(document)

        self.assertTrue(valid, errors)
        self.assertTrue(report.complete)
        self.assertTrue(report.anchors_consistent)
        self.assertTrue(report.attribution_available)
        self.assertEqual(report.status, "ATTRIBUTION_AVAILABLE")
        self.assertEqual(
            report.intervention["path_order"],
            ["src/access.py", "src/banner.py"],
        )
        self.assertEqual(
            [coalition.status for coalition in report.coalitions],
            ["unsupported", "supported", "unsupported", "supported"],
        )
        assert report.metrics is not None
        by_path = {item["path"]: item for item in report.metrics["paths"]}
        self.assertTrue(by_path["src/access.py"]["globally_necessary"])
        self.assertEqual(by_path["src/access.py"]["shapley"]["numerator"], 1)
        self.assertEqual(by_path["src/banner.py"]["shapley"]["numerator"], 0)
        self.assertEqual(
            report.metrics["paths_in_no_minimal_coalition"],
            ["src/banner.py"],
        )

    def test_import_error_withholds_exact_attribution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            base, head, spec = create_indeterminate_fixture(repo)
            report = analyze_patch_influence(repo, base, head, load_config(spec))

        self.assertFalse(report.complete)
        self.assertTrue(report.anchors_consistent)
        self.assertFalse(report.attribution_available)
        self.assertEqual(report.status, "INCOMPLETE_COALITION_TABLE")
        self.assertIsNone(report.metrics)
        indeterminate = [coalition for coalition in report.coalitions if not coalition.complete]
        self.assertEqual(len(indeterminate), 1)
        errors = [
            state.observation_error
            for claim in indeterminate[0].claims
            for state in claim.states
            if state.observation_error is not None
        ]
        self.assertTrue(any(error == "receipt_outcome:test_error" for error in errors))

    def test_documentation_that_changes_execution_breaks_endpoint_anchor(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            base, head, spec = create_documentation_leakage_fixture(repo)
            report = analyze_patch_influence(repo, base, head, load_config(spec))

        self.assertTrue(report.complete)
        self.assertFalse(report.anchors_consistent)
        self.assertFalse(report.attribution_available)
        self.assertEqual(report.status, "ANCHOR_INCONSISTENT")
        self.assertIsNone(report.metrics)
        empty_candidate_anchor = next(
            anchor for anchor in report.anchors if anchor["name"] == "empty-candidate-tests"
        )
        self.assertFalse(empty_candidate_anchor["outcomes_match"])
        self.assertFalse(empty_candidate_anchor["consistent"])

    def test_tampering_with_influence_metrics_invalidates_both_digests(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            base, head, spec = create_collateral_fixture(repo)
            report = analyze_patch_influence(repo, base, head, load_config(spec))
            document = influence_report_to_dict(report)
            valid, errors = verify_report_document(document)
            self.assertTrue(valid, errors)
            document["metrics"]["supported_coalition_count"] = 99  # type: ignore[index]
            valid, errors = verify_report_document(document)

        self.assertFalse(valid)
        self.assertTrue(any("influence digest mismatch" in error for error in errors))
        self.assertTrue(any("report digest mismatch" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
