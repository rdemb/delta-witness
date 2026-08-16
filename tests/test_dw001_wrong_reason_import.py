from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from deltawitness.config import load_config
from deltawitness.dw001 import project_baselines
from deltawitness.dw001_fixture_binding import (
    build_fixture_manifest_binding,
    verify_fixture_manifest_binding_document,
)
from deltawitness.dw001_scenarios import (
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
from dw001_binding_support import manifest_from_fixture


_FAMILY = "wrong-reason-base-import-failure"
_SCHEMA_DIR = Path(__file__).resolve().parents[1] / "research" / "DW-001" / "schema"


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


def _method_decisions(projection: dict[str, object]) -> dict[str, tuple[str, str]]:
    methods = projection["methods"]
    assert isinstance(methods, list)
    return {
        method["method_id"]: (method["decision"], method["reason_code"])
        for method in methods
    }


def _run_arm(
    observer: str,
) -> tuple[
    dict[str, object],
    dict[str, object],
    dict[str, object],
    dict[str, object],
    object,
    dict[str, object],
]:
    descriptor = build_fixture_descriptor(
        scenario_id=f"wrong-reason-import-{observer}",
        family_id=_FAMILY,
        observer=observer,
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
        if not identity_valid:
            raise AssertionError(identity_errors)
        if not materialized_valid:
            raise AssertionError(materialized_errors)

        manifest = manifest_from_fixture(descriptor, identity)
        binding = build_fixture_manifest_binding(descriptor, identity, manifest)
        binding_valid, binding_errors = verify_fixture_manifest_binding_document(
            binding,
            descriptor,
            identity,
            manifest,
        )
        if not binding_valid:
            raise AssertionError(binding_errors)

        report = verify_repository(
            repo,
            identity["git"]["base_commit_sha"],  # type: ignore[index]
            identity["git"]["head_commit_sha"],  # type: ignore[index]
            load_config(repo / identity["specification"]["path"]),  # type: ignore[index]
        )
        report_path = repo / ".git" / "deltawitness" / "wrong-reason.json"
        write_report(report, report_path)
        decoded = load_report(report_path)
        report_valid, report_errors = verify_report_document(decoded)
        if not report_valid:
            raise AssertionError(report_errors)
        projection = project_baselines(
            decoded,
            scenario_id=descriptor["scenario_id"],
        )

    return descriptor, identity, manifest, binding, report, projection


class DW001WrongReasonImportTests(unittest.TestCase):
    def test_family_is_versioned_across_generator_and_schemas(self) -> None:
        self.assertIn(_FAMILY, SUPPORTED_FAMILIES)
        for name in (
            "fixture-descriptor.schema.json",
            "fixture-identity.schema.json",
            "fixture-manifest-binding.schema.json",
        ):
            document = json.loads((_SCHEMA_DIR / name).read_text(encoding="utf-8"))
            self.assertIn(
                _FAMILY,
                document["properties"]["family_id"]["enum"],
                name,
            )

    def test_descriptor_semantics_depend_on_observer_without_free_form_labels(self) -> None:
        exit_descriptor = build_fixture_descriptor(
            scenario_id="wrong-reason-descriptor-exit",
            family_id=_FAMILY,
            observer="exit-code-v1",
        )
        typed_descriptor = build_fixture_descriptor(
            scenario_id="wrong-reason-descriptor-typed",
            family_id=_FAMILY,
            observer="outcome-receipt-v1",
        )

        self.assertEqual(
            [state["expected_observed"] for state in exit_descriptor["expected_states"]],
            ["pass", "fail", "pass", "pass"],
        )
        self.assertEqual(
            [state["failure_cause"] for state in exit_descriptor["expected_states"]],
            ["none", "test_failure_untyped", "none", "none"],
        )
        self.assertEqual(
            [method["decision"] for method in exit_descriptor["expected_methods"]],
            ["accept", "accept", "accept", "accept"],
        )

        self.assertEqual(
            [state["expected_observed"] for state in typed_descriptor["expected_states"]],
            ["pass", "error", "pass", "pass"],
        )
        self.assertEqual(
            [state["failure_cause"] for state in typed_descriptor["expected_states"]],
            ["none", "import_error", "none", "none"],
        )
        self.assertEqual(
            [method["decision"] for method in typed_descriptor["expected_methods"]],
            ["accept", "indeterminate", "indeterminate", "indeterminate"],
        )

        tampered = deepcopy(exit_descriptor)
        tampered["observer"] = "outcome-receipt-v1"
        tampered["observer_id"] = "O1_TYPED_RECEIPT"
        tampered["command"] = [
            "python",
            "-m",
            "deltawitness.unittest_probe",
            "--start-directory",
            "tests",
            "--verbosity",
            "0",
        ]
        tampered["descriptor_sha256"] = compute_fixture_descriptor_sha256(tampered)
        valid, errors = verify_fixture_descriptor_document(tampered)
        self.assertFalse(valid)
        self.assertTrue(any("expected_states" in error for error in errors), errors)

    def test_exit_code_arm_exhibits_controlled_false_assurance(self) -> None:
        descriptor, _, manifest, binding, report, projection = _run_arm(
            "exit-code-v1"
        )
        states = {state.state: state for state in report.claims[0].states}
        base_candidate = states["base_candidate"]

        self.assertEqual(base_candidate.observed, "fail")
        self.assertEqual(base_candidate.return_code, 1)
        self.assertIsNone(base_candidate.receipt_outcome)
        self.assertIsNone(base_candidate.receipt_counts)
        self.assertIsNone(base_candidate.observation_error)
        self.assertTrue(report.complete)
        self.assertTrue(report.supported)
        self.assertEqual(
            _method_decisions(projection),
            {
                "M0_FINAL": ("accept", "predicate_satisfied"),
                "M1_F2P": ("accept", "predicate_satisfied"),
                "M2_F2P_P2P": ("accept", "predicate_satisfied"),
                "M3_FOUR_STATE": ("accept", "predicate_satisfied"),
            },
        )
        self.assertTrue(
            all(
                method["primary_denominator_eligible"] is False
                for method in manifest["ground_truth"]["methods"]  # type: ignore[index]
            )
        )
        self.assertEqual(binding["family_id"], _FAMILY)
        self.assertEqual(descriptor["expected_states"][1]["failure_cause"], "test_failure_untyped")

    def test_typed_arm_preserves_error_and_indeterminate_methods(self) -> None:
        descriptor, _, manifest, binding, report, projection = _run_arm(
            "outcome-receipt-v1"
        )
        states = {state.state: state for state in report.claims[0].states}
        base_candidate = states["base_candidate"]

        self.assertEqual(base_candidate.observed, "error")
        self.assertEqual(base_candidate.receipt_outcome, "test_error")
        self.assertEqual(base_candidate.observation_error, "receipt_outcome:test_error")
        self.assertIsNotNone(base_candidate.receipt_counts)
        self.assertEqual(base_candidate.receipt_counts["failures"], 0)
        self.assertGreaterEqual(base_candidate.receipt_counts["errors"], 1)
        self.assertFalse(report.complete)
        self.assertFalse(report.supported)
        self.assertEqual(
            _method_decisions(projection),
            {
                "M0_FINAL": ("accept", "predicate_satisfied"),
                "M1_F2P": ("indeterminate", "required_state_indeterminate"),
                "M2_F2P_P2P": ("indeterminate", "required_state_indeterminate"),
                "M3_FOUR_STATE": ("indeterminate", "required_state_indeterminate"),
            },
        )
        self.assertTrue(
            all(
                method["primary_denominator_eligible"] is False
                for method in manifest["ground_truth"]["methods"]  # type: ignore[index]
            )
        )
        self.assertEqual(binding["family_id"], _FAMILY)
        self.assertEqual(descriptor["expected_states"][1]["failure_cause"], "import_error")

    def test_observer_arms_keep_identical_source_and_test_mechanism(self) -> None:
        descriptors = {
            observer: build_fixture_descriptor(
                scenario_id=f"wrong-reason-bytes-{observer}",
                family_id=_FAMILY,
                observer=observer,
            )
            for observer in ("exit-code-v1", "outcome-receipt-v1")
        }
        snapshots: dict[str, dict[str, str]] = {}
        for observer, descriptor in descriptors.items():
            with tempfile.TemporaryDirectory() as directory:
                repo = Path(directory)
                identity = materialize_synthetic_fixture(descriptor, repo)
                snapshots[observer] = {
                    "base_code": _git(
                        repo,
                        "show",
                        f"{identity['git']['base_commit_sha']}:src/access.py",  # type: ignore[index]
                    ),
                    "base_tests": _git(
                        repo,
                        "show",
                        f"{identity['git']['base_commit_sha']}:tests/test_access.py",  # type: ignore[index]
                    ),
                    "candidate_code": _git(
                        repo,
                        "show",
                        f"{identity['git']['head_commit_sha']}:src/access.py",  # type: ignore[index]
                    ),
                    "candidate_tests": _git(
                        repo,
                        "show",
                        f"{identity['git']['head_commit_sha']}:tests/test_access.py",  # type: ignore[index]
                    ),
                }

        self.assertEqual(
            snapshots["exit-code-v1"],
            snapshots["outcome-receipt-v1"],
        )

    def test_exit_code_descriptor_cannot_claim_import_error_after_resigning(self) -> None:
        descriptor = build_fixture_descriptor(
            scenario_id="wrong-reason-retrofit-001",
            family_id=_FAMILY,
            observer="exit-code-v1",
        )
        tampered = deepcopy(descriptor)
        tampered["expected_states"][1]["failure_cause"] = "import_error"
        tampered["descriptor_sha256"] = compute_fixture_descriptor_sha256(tampered)

        valid, errors = verify_fixture_descriptor_document(tampered)

        self.assertFalse(valid)
        self.assertTrue(any("expected_states" in error for error in errors), errors)

    def test_public_evidence_excludes_raw_tracebacks_and_local_paths(self) -> None:
        for observer in ("exit-code-v1", "outcome-receipt-v1"):
            with self.subTest(observer=observer):
                descriptor, identity, _, binding, report, _ = _run_arm(observer)
                for state in report.claims[0].states:
                    self.assertIsNone(state.stdout)
                    self.assertIsNone(state.stderr)
                encoded = json.dumps(
                    {
                        "descriptor": descriptor,
                        "identity": identity,
                        "binding": binding,
                    },
                    sort_keys=True,
                )
                self.assertNotIn("Traceback (most recent call last)", encoded)
                self.assertNotIn("/tmp/", encoded)
                self.assertNotIn("\\Temp\\", encoded)


if __name__ == "__main__":
    unittest.main()
