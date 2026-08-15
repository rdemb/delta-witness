from __future__ import annotations

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


def create_repository(root: Path, *, candidate_import_error: bool = False) -> tuple[str, str, Path]:
    run(root, "git", "init", "-b", "main")
    run(root, "git", "config", "user.email", "test@example.invalid")
    run(root, "git", "config", "user.name", "DeltaWitness Test")
    (root / "src").mkdir()
    (root / "tests").mkdir()
    (root / "src" / "access.py").write_text(
        "def is_admin(user):\n    return bool(user.get('role'))\n",
        encoding="utf-8",
    )
    (root / "tests" / "test_access.py").write_text(
        "import sys, unittest\n"
        "sys.path.insert(0, 'src')\n"
        "from access import is_admin\n\n"
        "class AccessTests(unittest.TestCase):\n"
        "    def test_admin_is_allowed(self):\n"
        "        self.assertTrue(is_admin({'role': 'admin'}))\n",
        encoding="utf-8",
    )
    run(root, "git", "add", ".")
    run(root, "git", "commit", "-m", "base")
    base = run(root, "git", "rev-parse", "HEAD")

    (root / "src" / "access.py").write_text(
        "def is_admin(user):\n    return user.get('role') == 'admin'\n",
        encoding="utf-8",
    )
    if candidate_import_error:
        candidate_test = "import module_missing_for_typed_receipt_fixture\n"
    else:
        candidate_test = (
            "import sys, unittest\n"
            "sys.path.insert(0, 'src')\n"
            "from access import is_admin\n\n"
            "class AccessTests(unittest.TestCase):\n"
            "    def test_admin_is_allowed(self):\n"
            "        self.assertTrue(is_admin({'role': 'admin'}))\n\n"
            "    def test_viewer_is_denied(self):\n"
            "        self.assertFalse(is_admin({'role': 'viewer'}))\n"
        )
    (root / "tests" / "test_access.py").write_text(candidate_test, encoding="utf-8")
    run(root, "git", "add", ".")
    run(root, "git", "commit", "-m", "candidate")

    spec = root / "deltawitness.toml"
    spec.write_text(
        "[paths]\n"
        "code = ['src/**']\n"
        "tests = ['tests/**']\n"
        "documentation = ['deltawitness.toml']\n\n"
        "[[claim]]\n"
        "id = 'typed-regression'\n"
        "description = 'A receipt must distinguish assertion failure from runner error.'\n"
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
    run(root, "git", "add", "deltawitness.toml")
    run(root, "git", "commit", "-m", "add typed witness specification")
    head = run(root, "git", "rev-parse", "HEAD")
    return base, head, spec


class TypedOutcomeMatrixTests(unittest.TestCase):
    def test_typed_receipts_support_a_real_assertion_transition(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            base, head, spec = create_repository(repo)
            report = verify_repository(repo, base, head, load_config(spec))

        self.assertTrue(report.complete)
        self.assertTrue(report.supported)
        claim = report.claims[0]
        self.assertEqual(claim.observer, "outcome-receipt-v1")
        self.assertEqual(
            [state.observed for state in claim.states],
            ["pass", "fail", "pass", "pass"],
        )
        self.assertEqual(
            [state.receipt_outcome for state in claim.states],
            ["passed", "test_failure", "passed", "passed"],
        )
        self.assertTrue(all(state.receipt_sha256 for state in claim.states))
        self.assertTrue(all(len(state.invocation_binding) == 64 for state in claim.states))
        self.assertTrue(all(state.observation_error is None for state in claim.states))

    def test_import_error_cannot_satisfy_an_expected_regression_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            base, head, spec = create_repository(repo, candidate_import_error=True)
            report = verify_repository(repo, base, head, load_config(spec))

        self.assertFalse(report.complete)
        self.assertFalse(report.supported)
        states = {state.state: state for state in report.claims[0].states}
        self.assertEqual(states["base_candidate"].observed, "error")
        self.assertEqual(states["base_candidate"].receipt_outcome, "test_error")
        self.assertEqual(
            states["base_candidate"].observation_error,
            "receipt_outcome:test_error",
        )
        self.assertGreater((states["base_candidate"].receipt_counts or {})["errors"], 0)

    def test_missing_receipt_makes_every_state_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            base, head, spec = create_repository(repo)
            raw = spec.read_text(encoding="utf-8")
            raw = raw.replace(
                f"command = [{sys.executable!r}, '-m', 'deltawitness.unittest_probe', "
                "'--start-directory', 'tests', '--verbosity', '0']",
                f"command = [{sys.executable!r}, '-c', 'import sys; sys.exit(1)']",
            )
            spec.write_text(raw, encoding="utf-8")
            run(repo, "git", "add", "deltawitness.toml")
            run(repo, "git", "commit", "-m", "use non-cooperating command")
            head = run(repo, "git", "rev-parse", "HEAD")
            report = verify_repository(repo, base, head, load_config(spec))

        self.assertFalse(report.complete)
        self.assertFalse(report.supported)
        self.assertTrue(all(state.observed == "error" for state in report.claims[0].states))
        self.assertTrue(all(state.observation_error == "missing" for state in report.claims[0].states))


if __name__ == "__main__":
    unittest.main()
