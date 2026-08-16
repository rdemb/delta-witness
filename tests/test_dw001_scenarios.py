from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from deltawitness.config import load_config
from deltawitness.dw001 import project_baselines
from deltawitness.dw001_scenarios import (
    DW001ScenarioError,
    SUPPORTED_FAMILIES,
    build_fixture_descriptor,
    compute_fixture_descriptor_sha256,
    materialize_synthetic_fixture,
    verify_fixture_descriptor_document,
    verify_fixture_identity_document,
    verify_materialized_fixture,
)
from deltawitness.matrix import verify_repository, write_report
from deltawitness.reporting import load_report, verify_report_document


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
    return completed.stdout.strip()


def _method_decisions(projection: dict[str, object]) -> dict[str, tuple[str, str]]:
    methods = projection["methods"]
    assert isinstance(methods, list)
    return {
        method["method_id"]: (method["decision"], method["reason_code"])
        for method in methods
    }


class DW001ScenarioGeneratorTests(unittest.TestCase):
    def test_same_descriptor_reproduces_exact_git_identity_across_directories(self) -> None:
        descriptor = build_fixture_descriptor(
            scenario_id="generator-repeat-001",
            family_id="valid-discriminating-regression",
        )
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first = materialize_synthetic_fixture(descriptor, Path(first_dir))
            second = materialize_synthetic_fixture(descriptor, Path(second_dir))

        self.assertEqual(first, second)
        self.assertEqual(first["git"], second["git"])
        self.assertEqual(first["specification"], second["specification"])

    def test_identity_excludes_absolute_destination_paths(self) -> None:
        descriptor = build_fixture_descriptor(
            scenario_id="generator-private-path-001",
            family_id="valid-discriminating-regression",
        )
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            identity = materialize_synthetic_fixture(descriptor, destination)
            encoded = json.dumps(identity, sort_keys=True)

        self.assertNotIn(str(destination), encoded)
        self.assertNotIn(destination.name, encoded)

    def test_family_change_changes_descriptor_and_candidate_identity(self) -> None:
        valid = build_fixture_descriptor(
            scenario_id="generator-family-001",
            family_id="valid-discriminating-regression",
        )
        nondiscriminating = build_fixture_descriptor(
            scenario_id="generator-family-001",
            family_id="non-discriminating-candidate-test",
        )
        self.assertNotEqual(valid["descriptor_sha256"], nondiscriminating["descriptor_sha256"])

        with tempfile.TemporaryDirectory() as valid_dir, tempfile.TemporaryDirectory() as other_dir:
            valid_identity = materialize_synthetic_fixture(valid, Path(valid_dir))
            other_identity = materialize_synthetic_fixture(nondiscriminating, Path(other_dir))

        self.assertNotEqual(
            valid_identity["git"]["head_commit_sha"],
            other_identity["git"]["head_commit_sha"],
        )
        self.assertNotEqual(
            valid_identity["git"]["head_tree_sha"],
            other_identity["git"]["head_tree_sha"],
        )

    def test_unknown_family_is_rejected_before_materialization(self) -> None:
        with self.assertRaisesRegex(DW001ScenarioError, "family"):
            build_fixture_descriptor(
                scenario_id="generator-unknown-001",
                family_id="unknown-family",
            )

    def test_nonempty_destination_is_rejected_without_deleting_user_file(self) -> None:
        descriptor = build_fixture_descriptor(
            scenario_id="generator-nonempty-001",
            family_id="valid-discriminating-regression",
        )
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            marker = destination / "keep.txt"
            marker.write_text("must survive\n", encoding="utf-8")

            with self.assertRaisesRegex(DW001ScenarioError, "empty"):
                materialize_synthetic_fixture(descriptor, destination)

            self.assertEqual(marker.read_text(encoding="utf-8"), "must survive\n")
            self.assertEqual(sorted(path.name for path in destination.iterdir()), ["keep.txt"])

    def test_recomputed_digest_cannot_hide_wrong_expected_method_decision(self) -> None:
        descriptor = build_fixture_descriptor(
            scenario_id="generator-semantic-001",
            family_id="valid-discriminating-regression",
        )
        tampered = deepcopy(descriptor)
        tampered["expected_methods"][0]["decision"] = "reject"
        tampered["expected_methods"][0]["reason_code"] = "predicate_contradicted"
        tampered["descriptor_sha256"] = compute_fixture_descriptor_sha256(tampered)

        valid, errors = verify_fixture_descriptor_document(tampered)

        self.assertFalse(valid)
        self.assertTrue(
            any("method decision is inconsistent" in error for error in errors),
            errors,
        )

    def test_generated_repositories_match_recorded_identity_and_expected_semantics(self) -> None:
        for family_id in SUPPORTED_FAMILIES:
            with self.subTest(family=family_id):
                descriptor = build_fixture_descriptor(
                    scenario_id=f"generator-integration-{family_id}",
                    family_id=family_id,
                )
                with tempfile.TemporaryDirectory() as directory:
                    repo = Path(directory)
                    identity = materialize_synthetic_fixture(descriptor, repo)
                    identity_valid, identity_errors = verify_fixture_identity_document(
                        identity,
                        descriptor,
                    )
                    materialized_valid, materialized_errors = verify_materialized_fixture(
                        identity,
                        descriptor,
                        repo,
                    )
                    self.assertTrue(identity_valid, identity_errors)
                    self.assertTrue(materialized_valid, materialized_errors)
                    self.assertEqual(_git(repo, "status", "--porcelain=v1"), "")
                    self.assertEqual(_git(repo, "rev-parse", "HEAD"), identity["git"]["head_commit_sha"])

                    report = verify_repository(
                        repo,
                        identity["git"]["base_commit_sha"],
                        identity["git"]["head_commit_sha"],
                        load_config(repo / identity["specification"]["path"]),
                    )
                    report_path = repo / ".git" / "deltawitness" / "generator-report.json"
                    write_report(report, report_path)
                    decoded_report = load_report(report_path)
                    report_valid, report_errors = verify_report_document(decoded_report)
                    self.assertTrue(report_valid, report_errors)
                    projection = project_baselines(
                        decoded_report,
                        scenario_id=descriptor["scenario_id"],
                    )

                observed_states = {
                    state.state: state.observed
                    for state in report.claims[0].states
                }
                expected_states = {
                    state["state"]: state["expected_observed"]
                    for state in descriptor["expected_states"]
                }
                expected_methods = {
                    method["method_id"]: (method["decision"], method["reason_code"])
                    for method in descriptor["expected_methods"]
                }
                self.assertEqual(observed_states, expected_states)
                self.assertEqual(_method_decisions(projection), expected_methods)


if __name__ == "__main__":
    unittest.main()
