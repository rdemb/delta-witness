from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from deltawitness.config import load_config
from deltawitness.matrix import report_to_dict, verify_repository
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


def replace_probe_command(spec: Path, replacement: str) -> None:
    original = (
        f"command = [{sys.executable!r}, '-m', 'deltawitness.unittest_probe', "
        "'--start-directory', 'tests', '--verbosity', '0']"
    )
    raw = spec.read_text(encoding="utf-8")
    if original not in raw:
        raise AssertionError("typed probe command was not found in the fixture specification")
    spec.write_text(raw.replace(original, replacement), encoding="utf-8")


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
            replace_probe_command(
                spec,
                f"command = [{sys.executable!r}, '-c', 'import sys; sys.exit(1)']",
            )
            run(repo, "git", "add", "deltawitness.toml")
            run(repo, "git", "commit", "-m", "use non-cooperating command")
            head = run(repo, "git", "rev-parse", "HEAD")
            report = verify_repository(repo, base, head, load_config(spec))

        self.assertFalse(report.complete)
        self.assertFalse(report.supported)
        self.assertTrue(all(state.observed == "error" for state in report.claims[0].states))
        self.assertTrue(all(state.observation_error == "missing" for state in report.claims[0].states))

    def test_receipt_and_exit_code_must_agree(self) -> None:
        contradictory_command = (
            "import os,sys; from pathlib import Path; "
            "from deltawitness.receipt import build_receipt_document,write_outcome_receipt; "
            "binding=os.environ['DELTAWITNESS_RECEIPT_BINDING']; "
            "path=Path(os.environ['DELTAWITNESS_RECEIPT_PATH']); "
            "counts={'tests_run':1,'passed':1,'failures':0,'errors':0,'skipped':0,"
            "'expected_failures':0,'unexpected_successes':0}; "
            "document=build_receipt_document(binding=binding,producer_name='contradictory-test',"
            "producer_version='1',outcome='passed',counts=counts); "
            "write_outcome_receipt(path,document,expected_binding=binding); sys.exit(1)"
        )
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            base, head, spec = create_repository(repo)
            replace_probe_command(
                spec,
                f"command = [{sys.executable!r}, '-c', {contradictory_command!r}]",
            )
            run(repo, "git", "add", "deltawitness.toml")
            run(repo, "git", "commit", "-m", "use contradictory receipt producer")
            head = run(repo, "git", "rev-parse", "HEAD")
            report = verify_repository(repo, base, head, load_config(spec))

        self.assertFalse(report.complete)
        self.assertFalse(report.supported)
        self.assertTrue(all(state.receipt_outcome == "passed" for state in report.claims[0].states))
        self.assertTrue(all(state.return_code == 1 for state in report.claims[0].states))
        self.assertTrue(all(state.observed == "error" for state in report.claims[0].states))
        self.assertTrue(
            all(
                state.observation_error == "receipt_exit_mismatch"
                for state in report.claims[0].states
            )
        )

    def test_receipt_semantics_are_bound_into_report_integrity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            base, head, spec = create_repository(repo)
            report = verify_repository(repo, base, head, load_config(spec))
            document = report_to_dict(report)
            valid, errors = verify_report_document(document)
            self.assertTrue(valid, errors)
            counts = document["claims"][0]["states"][0]["receipt_counts"]  # type: ignore[index]
            counts["passed"] = 0  # type: ignore[index]
            valid, errors = verify_report_document(document)

        self.assertFalse(valid)
        self.assertTrue(any("witness digest mismatch" in error for error in errors))
        self.assertTrue(any("report digest mismatch" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
