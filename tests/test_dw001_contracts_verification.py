from __future__ import annotations

from copy import deepcopy
import unittest

from deltawitness.dw001 import METHOD_STATE_SETS, project_baselines
from deltawitness.dw001_contracts import (
    RESULT_SCHEMA_VERSION,
    SCENARIO_SCHEMA_VERSION,
    STUDY_ID,
    compute_result_sha256,
    compute_scenario_manifest_sha256,
    seal_result_record,
    seal_scenario_manifest,
    verify_result_against_sources,
    verify_result_record_document,
    verify_scenario_manifest_document,
)
from test_dw001 import _report


_STATE_CAUSES = {
    "base_base": "none",
    "base_candidate": "assertion_failure",
    "candidate_base": "none",
    "candidate_candidate": "none",
}


def _manifest(
    projection: dict[str, object],
    *,
    partition: str = "development",
) -> dict[str, object]:
    holdout = partition == "holdout"
    projection_methods = {
        method["method_id"]: method
        for method in projection["methods"]  # type: ignore[index]
    }
    states = [
        {
            "state": state,
            "applicable": True,
            "applicability_reason": None,
            "expected_observed": expected,
            "failure_cause": _STATE_CAUSES[state],
        }
        for state, expected in (
            ("base_base", "pass"),
            ("base_candidate", "fail"),
            ("candidate_base", "pass"),
            ("candidate_candidate", "pass"),
        )
    ]
    methods = [
        {
            "method_id": method_id,
            "observer_id": projection["source"]["observer_id"],  # type: ignore[index]
            "combined_method_id": f"{method_id}__{projection['source']['observer_id']}",  # type: ignore[index]
            "expected_decision": projection_methods[method_id]["decision"],
            "reason_code": projection_methods[method_id]["reason_code"],
            "primary_denominator_eligible": holdout,
        }
        for method_id, _ in METHOD_STATE_SETS
    ]
    return seal_scenario_manifest(
        {
            "schema_version": SCENARIO_SCHEMA_VERSION,
            "study_id": STUDY_ID,
            "scenario_id": projection["scenario_id"],
            "partition": partition,
            "partition_lock": {
                "status": "holdout_committed" if holdout else "development_uncommitted",
                "commitment_sha256": "a" * 64 if holdout else None,
                "commitment_scope": "dw001-holdout-index-v1" if holdout else None,
            },
            "provenance": {
                "source_type": "synthetic",
                "source_id": "synthetic/valid-regression-v1",
                "license_expression": None,
                "authorization_basis": "owned_synthetic_fixture",
                "authorization_reference": None,
                "public_release_allowed": True,
            },
            "git": {
                "repository_id": "synthetic-dw001-fixture",
                "base_sha": projection["source"]["base_sha"],  # type: ignore[index]
                "head_sha": projection["source"]["head_sha"],  # type: ignore[index]
            },
            "paths": {
                "code": ["src/access.py"],
                "tests": ["tests/test_access.py"],
                "documentation": ["deltawitness.toml"],
            },
            "execution": {
                "command": ["python", "-m", "unittest", "discover", "-s", "tests"],
                "observer": projection["source"]["observer"],  # type: ignore[index]
                "observer_id": projection["source"]["observer_id"],  # type: ignore[index]
                "timeout_seconds": 30,
                "pass_exit_codes": [0],
                "fail_exit_codes": [1],
                "pass_env": [],
                "environment_requirements": ["CPython 3.11 or later", "Git"],
            },
            "ground_truth": {
                "states": states,
                "methods": methods,
                "false_assurance_mechanism": "valid_regression_control",
                "environment_assumptions": [
                    "The synthetic fixture is deterministic.",
                    "No external service is required.",
                ],
            },
            "review": {
                "status": "approved",
                "reviewers": [
                    {
                        "reviewer_id": "synthetic-reviewer-001",
                        "role": "ground_truth_reviewer",
                        "independent_of_scenario_author": True,
                        "independent_of_implementation": True,
                        "decision": "approve",
                        "rationale": "The expected states follow directly from the synthetic fixture.",
                    }
                ],
            },
            "manifest_sha256": None,
        }
    )


def _cost() -> dict[str, object]:
    return {
        "status": "not_run",
        "wall_clock_seconds": None,
        "cpu_seconds": None,
        "state_count": None,
        "command_count": None,
        "review_seconds": None,
        "missing_reason": "Method-specific cost execution has not been run.",
    }


def _result(
    manifest: dict[str, object],
    projection: dict[str, object],
) -> dict[str, object]:
    manifest_methods = {
        method["method_id"]: method
        for method in manifest["ground_truth"]["methods"]  # type: ignore[index]
    }
    holdout = manifest["partition"] == "holdout"
    return seal_result_record(
        {
            "schema_version": RESULT_SCHEMA_VERSION,
            "study_id": STUDY_ID,
            "scenario_id": manifest["scenario_id"],
            "partition": manifest["partition"],
            "scenario_manifest_sha256": manifest["manifest_sha256"],
            "source": {
                "protocol_commit": "b" * 40,
                "implementation_commit": "c" * 40,
                "generator_commit": None,
                "baseline_contract_sha256": "d" * 64,
                "matrix_report_sha256": projection["source"]["report_sha256"],  # type: ignore[index]
                "witness_sha256": projection["source"]["witness_sha256"],  # type: ignore[index]
                "projection_sha256": projection["projection_sha256"],
                "observer_id": projection["source"]["observer_id"],  # type: ignore[index]
            },
            "exclusion": {
                "status": "included",
                "code": None,
                "reason": None,
                "decision_reference": None,
            },
            "deviations": [],
            "methods": [
                {
                    "method_id": method["method_id"],
                    "observer_id": method["observer_id"],
                    "combined_method_id": method["combined_method_id"],
                    "expected_decision": manifest_methods[method["method_id"]][
                        "expected_decision"
                    ],
                    "observed_decision": method["decision"],
                    "observed_reason_code": method["reason_code"],
                    "concordant": (
                        manifest_methods[method["method_id"]]["expected_decision"]
                        == method["decision"]
                    ),
                    "primary_denominator_eligible": holdout,
                    "denominator_reason_code": (
                        "eligible" if holdout else "development_partition"
                    ),
                    "cost": _cost(),
                }
                for method in projection["methods"]  # type: ignore[index]
            ],
            "result_sha256": None,
        }
    )


def _resign_manifest(manifest: dict[str, object]) -> None:
    manifest["manifest_sha256"] = compute_scenario_manifest_sha256(manifest)


def _resign_result(result: dict[str, object]) -> None:
    result["result_sha256"] = compute_result_sha256(result)


class DW001StudyContractVerificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.projection = project_baselines(
            _report(),
            scenario_id="study-contract-001",
        )

    def test_valid_manifest_and_result_round_trip(self) -> None:
        manifest = _manifest(self.projection)
        result = _result(manifest, self.projection)

        manifest_valid, manifest_errors = verify_scenario_manifest_document(manifest)
        result_valid, result_errors = verify_result_record_document(result)
        cross_valid, cross_errors = verify_result_against_sources(
            result,
            manifest,
            self.projection,
        )

        self.assertTrue(manifest_valid, manifest_errors)
        self.assertTrue(result_valid, result_errors)
        self.assertTrue(cross_valid, cross_errors)

    def test_recomputed_manifest_digest_cannot_hide_wrong_method_ground_truth(self) -> None:
        manifest = _manifest(self.projection)
        tampered = deepcopy(manifest)
        tampered["ground_truth"]["methods"][0]["expected_decision"] = "reject"
        tampered["ground_truth"]["methods"][0]["reason_code"] = "predicate_contradicted"
        _resign_manifest(tampered)

        valid, errors = verify_scenario_manifest_document(tampered)

        self.assertFalse(valid)
        self.assertTrue(
            any("method ground truth is inconsistent" in error for error in errors),
            errors,
        )

    def test_recomputed_manifest_digest_cannot_hide_partition_relabeling(self) -> None:
        manifest = _manifest(self.projection, partition="holdout")
        tampered = deepcopy(manifest)
        tampered["partition"] = "development"
        _resign_manifest(tampered)

        valid, errors = verify_scenario_manifest_document(tampered)

        self.assertFalse(valid)
        self.assertTrue(
            any("partition_lock is inconsistent" in error for error in errors),
            errors,
        )

    def test_result_decision_must_match_supplied_projection(self) -> None:
        manifest = _manifest(self.projection)
        result = _result(manifest, self.projection)
        tampered = deepcopy(result)
        tampered["methods"][0]["observed_decision"] = "reject"
        tampered["methods"][0]["observed_reason_code"] = "predicate_contradicted"
        tampered["methods"][0]["concordant"] = False
        _resign_result(tampered)

        valid, errors = verify_result_against_sources(
            tampered,
            manifest,
            self.projection,
        )

        self.assertFalse(valid)
        self.assertTrue(
            any("does not match supplied projection" in error for error in errors),
            errors,
        )

    def test_result_must_bind_the_supplied_manifest(self) -> None:
        manifest = _manifest(self.projection)
        result = _result(manifest, self.projection)
        tampered = deepcopy(result)
        tampered["scenario_manifest_sha256"] = "f" * 64
        _resign_result(tampered)

        valid, errors = verify_result_against_sources(
            tampered,
            manifest,
            self.projection,
        )

        self.assertFalse(valid)
        self.assertTrue(
            any("scenario manifest digest mismatch" in error for error in errors),
            errors,
        )

    def test_excluded_result_cannot_remain_primary_denominator_eligible(self) -> None:
        manifest = _manifest(self.projection, partition="holdout")
        result = _result(manifest, self.projection)
        tampered = deepcopy(result)
        tampered["exclusion"] = {
            "status": "excluded",
            "code": "ground_truth_dispute",
            "reason": "Synthetic exclusion for regression evidence.",
            "decision_reference": "review/exclusion-001",
        }
        _resign_result(tampered)

        valid, errors = verify_result_record_document(tampered)

        self.assertFalse(valid)
        self.assertTrue(
            any(
                "excluded result cannot be primary-denominator eligible" in error
                for error in errors
            ),
            errors,
        )

    def test_undeclared_deviation_cannot_preserve_confirmatory_denominator(self) -> None:
        manifest = _manifest(self.projection, partition="holdout")
        result = _result(manifest, self.projection)
        tampered = deepcopy(result)
        tampered["deviations"] = [
            {
                "deviation_id": "deviation-001",
                "status": "applied",
                "rule_id": "execution.timeout",
                "observed_problem": "Synthetic timeout policy deviation.",
                "action": "Use a longer timeout.",
                "results_visible": False,
                "confirmatory_impact": "exploratory_only",
                "approval_reference": None,
            }
        ]
        _resign_result(tampered)

        valid, errors = verify_result_record_document(tampered)

        self.assertFalse(valid)
        self.assertTrue(
            any(
                "applied deviation requires approval_reference" in error
                for error in errors
            ),
            errors,
        )
        self.assertTrue(
            any(
                "exploratory-only result cannot be primary-denominator eligible"
                in error
                for error in errors
            ),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
