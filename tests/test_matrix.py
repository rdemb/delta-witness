from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from deltawitness.config import load_config
from deltawitness.errors import GitError
from deltawitness.matrix import report_to_dict, verify_repository, write_report
from deltawitness.reporting import load_report, verify_report_document


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
        raise AssertionError(f"Command failed: {args}\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}")
    return completed.stdout.strip()


def create_regression_repository(root: Path, extra_claims: str = "") -> tuple[str, str, Path]:
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
    with (root / "tests" / "test_access.py").open("a", encoding="utf-8") as handle:
        handle.write(
            "\n    def test_viewer_is_denied(self):\n"
            "        self.assertFalse(is_admin({'role': 'viewer'}))\n"
        )
    run(root, "git", "add", ".")
    run(root, "git", "commit", "-m", "fix role check and add regression witness")
    head = run(root, "git", "rev-parse", "HEAD")

    spec = root / "deltawitness.toml"
    spec.write_text(
        "[paths]\n"
        "code = ['src/**']\n"
        "tests = ['tests/**']\n"
        "documentation = ['deltawitness.toml']\n\n"
        "[[claim]]\n"
        "id = 'role-check-regression'\n"
        "description = 'A viewer must not be treated as an administrator.'\n"
        f"command = [{sys.executable!r}, '-m', 'unittest', 'discover', '-s', 'tests']\n"
        "timeout_seconds = 30\n\n"
        "[claim.expect]\n"
        "base_base = 'pass'\n"
        "base_candidate = 'fail'\n"
        "candidate_base = 'pass'\n"
        "candidate_candidate = 'pass'\n"
        f"{extra_claims}",
        encoding="utf-8",
    )
    run(root, "git", "add", "deltawitness.toml")
    run(root, "git", "commit", "-m", "add witness specification")
    head_with_spec = run(root, "git", "rev-parse", "HEAD")
    return base, head_with_spec, spec


class MatrixIntegrationTests(unittest.TestCase):
    def test_counterfactual_matrix_supports_a_real_regression_claim(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            base, head, spec = create_regression_repository(repo)
            config = load_config(spec)
            report = verify_repository(repo, base, head, config)

        self.assertTrue(report.complete)
        self.assertTrue(report.supported)
        claim = report.claims[0]
        observations = {state.state: state.observed for state in claim.states}
        self.assertEqual(observations["base_candidate"], "fail")
        self.assertEqual(observations["candidate_candidate"], "pass")
        self.assertEqual(len(report.witness_sha256 or ""), 64)
        self.assertEqual(len(report.report_sha256 or ""), 64)
        self.assertEqual(set(report.state_trees), {
            "base_base",
            "base_candidate",
            "candidate_base",
            "candidate_candidate",
        })
        self.assertEqual(set(report.state_commits), set(report.state_trees))
        self.assertEqual(report.state_commits["base_base"], report.base_sha)
        self.assertEqual(report.state_commits["candidate_candidate"], report.head_sha)

    def test_default_report_redacts_output_and_local_paths(self) -> None:
        secret = "SUPER_SECRET_VALUE_9381"
        extra = (
            "\n[[claim]]\n"
            "id = 'output-redaction'\n"
            "description = 'Raw output is excluded unless explicitly requested.'\n"
            f"command = [{sys.executable!r}, '-c', \"print(bytes.fromhex('{secret.encode().hex()}').decode())\"]\n"
            "timeout_seconds = 30\n\n"
            "[claim.expect]\n"
            "base_base = 'pass'\n"
            "base_candidate = 'pass'\n"
            "candidate_base = 'pass'\n"
            "candidate_candidate = 'pass'\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            base, head, spec = create_regression_repository(repo, extra)
            report = verify_repository(repo, base, head, load_config(spec))
            encoded = json.dumps(report_to_dict(report), sort_keys=True)

        self.assertNotIn(secret, encoded)
        self.assertNotIn(str(repo), encoded)
        output_claim = report.claims[1]
        self.assertTrue(all(state.stdout is None and state.stderr is None for state in output_claim.states))
        self.assertTrue(all(len(state.stdout_sha256) == 64 for state in output_claim.states))

    def test_claims_are_isolated_from_files_created_by_previous_claims(self) -> None:
        extra = (
            "\n[[claim]]\n"
            "id = 'create-pollution'\n"
            "description = 'Create an ignored or untracked file.'\n"
            f"command = [{sys.executable!r}, '-c', \"open('pollution.tmp', 'w').write('x')\"]\n"
            "timeout_seconds = 30\n\n"
            "[claim.expect]\n"
            "base_base = 'pass'\n"
            "base_candidate = 'pass'\n"
            "candidate_base = 'pass'\n"
            "candidate_candidate = 'pass'\n"
            "\n[[claim]]\n"
            "id = 'pollution-absent'\n"
            "description = 'Each claim starts from the recorded tree.'\n"
            f"command = [{sys.executable!r}, '-c', \"import pathlib,sys; sys.exit(pathlib.Path('pollution.tmp').exists())\"]\n"
            "timeout_seconds = 30\n\n"
            "[claim.expect]\n"
            "base_base = 'pass'\n"
            "base_candidate = 'pass'\n"
            "candidate_base = 'pass'\n"
            "candidate_candidate = 'pass'\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            base, head, spec = create_regression_repository(repo, extra)
            report = verify_repository(repo, base, head, load_config(spec))

        self.assertTrue(report.supported)
        self.assertTrue(report.claims[2].supported)

    def test_witness_digest_is_stable_across_repeated_runs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            base, head, spec = create_regression_repository(repo)
            config = load_config(spec)
            first = verify_repository(repo, base, head, config)
            second = verify_repository(repo, base, head, config)

        self.assertEqual(first.witness_sha256, second.witness_sha256)

    def test_witness_digest_is_independent_of_clone_directory_name(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "first-name"
            repo.mkdir()
            base, head, spec = create_regression_repository(repo)
            first = verify_repository(repo, base, head, load_config(spec))

            clone = root / "different-name"
            run(root, "git", "clone", "--quiet", str(repo), str(clone))
            second = verify_repository(
                clone,
                base,
                head,
                load_config(clone / "deltawitness.toml"),
            )

        self.assertEqual(first.witness_sha256, second.witness_sha256)

    def test_written_report_can_be_verified_and_tampering_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            base, head, spec = create_regression_repository(repo)
            report = verify_repository(repo, base, head, load_config(spec))
            output = repo / ".deltawitness" / "report.json"
            write_report(report, output)
            document = load_report(output)
            valid, errors = verify_report_document(document)
            self.assertTrue(valid, errors)
            document["supported"] = not document["supported"]
            valid, errors = verify_report_document(document)

        self.assertFalse(valid)
        self.assertTrue(errors)

    def test_process_environment_does_not_inherit_unlisted_secret(self) -> None:
        old = os.environ.get("DW_UNLISTED_SECRET")
        os.environ["DW_UNLISTED_SECRET"] = "should-not-cross-boundary"
        extra = (
            "\n[[claim]]\n"
            "id = 'environment-sanitized'\n"
            "description = 'Unlisted host variables do not enter the command environment.'\n"
            f"command = [{sys.executable!r}, '-c', \"import os,sys; sys.exit('DW_UNLISTED_SECRET' in os.environ)\"]\n"
            "timeout_seconds = 30\n\n"
            "[claim.expect]\n"
            "base_base = 'pass'\n"
            "base_candidate = 'pass'\n"
            "candidate_base = 'pass'\n"
            "candidate_candidate = 'pass'\n"
        )
        try:
            with tempfile.TemporaryDirectory() as directory:
                repo = Path(directory)
                base, head, spec = create_regression_repository(repo, extra)
                report = verify_repository(repo, base, head, load_config(spec))
        finally:
            if old is None:
                os.environ.pop("DW_UNLISTED_SECRET", None)
            else:
                os.environ["DW_UNLISTED_SECRET"] = old

        self.assertTrue(report.claims[1].supported)

    def test_rejects_unrelated_base_and_candidate_histories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            base, head, spec = create_regression_repository(repo)
            run(repo, "git", "checkout", "--orphan", "unrelated")
            run(repo, "git", "rm", "-rf", ".")
            (repo / "src").mkdir()
            (repo / "tests").mkdir()
            (repo / "src" / "x.py").write_text("x = 1\n", encoding="utf-8")
            (repo / "tests" / "test_x.py").write_text("assert True\n", encoding="utf-8")
            run(repo, "git", "add", ".")
            run(repo, "git", "commit", "-m", "unrelated")
            unrelated = run(repo, "git", "rev-parse", "HEAD")
            run(repo, "git", "checkout", "main")
            with self.assertRaises(GitError):
                verify_repository(repo, unrelated, head, load_config(spec))

    def test_unclassified_exit_code_makes_the_report_incomplete(self) -> None:
        extra = (
            "\n[[claim]]\n"
            "id = 'unexpected-exit'\n"
            "description = 'An unclassified process result is not evidence of a test failure.'\n"
            f"command = [{sys.executable!r}, '-c', 'import sys; sys.exit(3)']\n"
            "timeout_seconds = 30\n\n"
            "[claim.expect]\n"
            "base_base = 'any'\n"
            "base_candidate = 'any'\n"
            "candidate_base = 'any'\n"
            "candidate_candidate = 'any'\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            base, head, spec = create_regression_repository(repo, extra)
            report = verify_repository(repo, base, head, load_config(spec))

        self.assertFalse(report.complete)
        self.assertFalse(report.supported)
        self.assertTrue(all(state.observed == "error" for state in report.claims[1].states))

    def test_explicit_nonstandard_failure_code_is_classified(self) -> None:
        extra = (
            "\n[[claim]]\n"
            "id = 'custom-failure-code'\n"
            "description = 'A project may declare a nonstandard test-failure exit code.'\n"
            f"command = [{sys.executable!r}, '-c', 'import sys; sys.exit(3)']\n"
            "timeout_seconds = 30\n"
            "fail_exit_codes = [3]\n\n"
            "[claim.expect]\n"
            "base_base = 'fail'\n"
            "base_candidate = 'fail'\n"
            "candidate_base = 'fail'\n"
            "candidate_candidate = 'fail'\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            base, head, spec = create_regression_repository(repo, extra)
            report = verify_repository(repo, base, head, load_config(spec))

        self.assertTrue(report.complete)
        self.assertTrue(report.supported)
        self.assertTrue(all(state.observed == "fail" for state in report.claims[1].states))


if __name__ == "__main__":
    unittest.main()
