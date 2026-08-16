#!/usr/bin/env python3
"""Exercise the packaged DW-001 unrelated-assertion negative control.

The smoke uses only fixed project-owned synthetic bytes. It verifies that both
exit-code and typed-receipt arms accept the canonical matrix even though the
claim-facing assertion is non-discriminating and an unrelated collateral
assertion is the sole base-side failure. It does not authorize a pilot or
held-out execution.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile

from deltawitness.config import load_config
from deltawitness.dw001 import project_baselines
from deltawitness.dw001_fixture_binding import (
    build_fixture_manifest_binding,
    verify_fixture_manifest_binding_document,
)
from deltawitness.dw001_scenarios import (
    build_fixture_descriptor,
    materialize_synthetic_fixture,
    verify_fixture_identity_document,
    verify_materialized_fixture,
)
from deltawitness.matrix import verify_repository, write_report
from deltawitness.reporting import load_report, verify_report_document
from smoke_dw001_fixture_binding import _manifest


_FAMILY = "wrong-reason-unrelated-assertion"
_SCENARIO_ID = "ci-unrelated-assertion-smoke-001"
_COLLATERAL_TEST = """
    def test_version_label_is_v2(self):
        self.assertEqual(version_label(), "v2")
"""
_CLAIM_FACING_TEST = """import sys
import unittest

sys.path.insert(0, "src")
from access import is_admin


class ClaimFacingTests(unittest.TestCase):
    def test_viewer_result_is_boolean(self):
        self.assertIsInstance(is_admin({"role": "viewer"}), bool)
"""


def _git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"git {args!r} failed\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )
    return completed.stdout


def _run_unittest(code: str, tests: str) -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "src").mkdir()
        (root / "tests").mkdir()
        (root / "src" / "access.py").write_text(code, encoding="utf-8")
        (root / "tests" / "test_access.py").write_text(tests, encoding="utf-8")
        completed = subprocess.run(
            ["python", "-m", "unittest", "discover", "-s", "tests"],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        return completed.returncode


def _decisions(projection: dict[str, object]) -> dict[str, str]:
    methods = projection["methods"]
    if not isinstance(methods, list):
        raise AssertionError("projection methods are not a list")
    return {method["method_id"]: method["decision"] for method in methods}


def _run(observer: str) -> tuple[object, dict[str, object], dict[str, str]]:
    descriptor = build_fixture_descriptor(
        scenario_id=_SCENARIO_ID,
        family_id=_FAMILY,
        observer=observer,
    )
    with tempfile.TemporaryDirectory() as directory:
        repository = Path(directory)
        identity = materialize_synthetic_fixture(descriptor, repository)
        identity_valid, identity_errors = verify_fixture_identity_document(
            identity,
            descriptor,
        )
        materialized_valid, materialized_errors = verify_materialized_fixture(
            identity,
            descriptor,
            repository,
        )
        if not identity_valid:
            raise AssertionError(identity_errors)
        if not materialized_valid:
            raise AssertionError(materialized_errors)

        manifest = _manifest(descriptor, identity)
        binding = build_fixture_manifest_binding(descriptor, identity, manifest)
        binding_valid, binding_errors = verify_fixture_manifest_binding_document(
            binding,
            descriptor,
            identity,
            manifest,
        )
        if not binding_valid:
            raise AssertionError(binding_errors)

        base_code = _git(
            repository,
            "show",
            f"{identity['git']['base_commit_sha']}:src/access.py",
        )
        candidate_code = _git(
            repository,
            "show",
            f"{identity['git']['head_commit_sha']}:src/access.py",
        )
        candidate_tests = _git(
            repository,
            "show",
            f"{identity['git']['head_commit_sha']}:tests/test_access.py",
        )
        if _run_unittest(base_code, _CLAIM_FACING_TEST) != 0:
            raise AssertionError("claim-facing assertion discriminates the base")
        if _run_unittest(candidate_code, _CLAIM_FACING_TEST) != 0:
            raise AssertionError("claim-facing assertion rejects the candidate")
        if _COLLATERAL_TEST not in candidate_tests:
            raise AssertionError("collateral assertion is missing")
        if _run_unittest(base_code, candidate_tests) != 1:
            raise AssertionError("complete candidate suite does not fail on base")
        if _run_unittest(
            base_code,
            candidate_tests.replace(_COLLATERAL_TEST, ""),
        ) != 0:
            raise AssertionError("collateral assertion is not the sole BC failure")

        report = verify_repository(
            repository,
            identity["git"]["base_commit_sha"],
            identity["git"]["head_commit_sha"],
            load_config(repository / identity["specification"]["path"]),
        )
        report_path = (
            repository / ".git" / "deltawitness" / "unrelated-assertion.json"
        )
        write_report(report, report_path)
        decoded = load_report(report_path)
        report_valid, report_errors = verify_report_document(decoded)
        if not report_valid:
            raise AssertionError(report_errors)
        projection = project_baselines(decoded, scenario_id=_SCENARIO_ID)

    return report, projection, {
        "base_code": base_code,
        "candidate_code": candidate_code,
        "candidate_tests": candidate_tests,
    }


def main() -> int:
    exit_report, exit_projection, exit_bytes = _run("exit-code-v1")
    typed_report, typed_projection, typed_bytes = _run("outcome-receipt-v1")

    if exit_bytes != typed_bytes:
        raise AssertionError("observer arms changed the source/test mechanism")

    expected_decisions = {
        "M0_FINAL": "accept",
        "M1_F2P": "accept",
        "M2_F2P_P2P": "accept",
        "M3_FOUR_STATE": "accept",
    }
    for report, projection in (
        (exit_report, exit_projection),
        (typed_report, typed_projection),
    ):
        state = {
            observation.state: observation
            for observation in report.claims[0].states
        }["base_candidate"]
        if state.observed != "fail" or not report.complete or not report.supported:
            raise AssertionError("wrong-reason assertion did not form a canonical witness")
        if _decisions(projection) != expected_decisions:
            raise AssertionError("nested methods did not all accept")

    typed_state = {
        observation.state: observation
        for observation in typed_report.claims[0].states
    }["base_candidate"]
    if typed_state.receipt_outcome != "test_failure":
        raise AssertionError("typed arm did not record assertion failure")
    if typed_state.receipt_counts is None:
        raise AssertionError("typed arm omitted receipt counts")
    if typed_state.receipt_counts["failures"] < 1:
        raise AssertionError("typed arm recorded no assertion failure")
    if typed_state.receipt_counts["errors"] != 0:
        raise AssertionError("typed arm introduced an execution error")

    print("DW-001 unrelated-assertion negative-control smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
