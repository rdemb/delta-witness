from __future__ import annotations

from copy import deepcopy
import unittest

from deltawitness.dw001 import (
    CANONICAL_EXPECTATIONS,
    METHOD_STATE_SETS,
    STATE_ORDER,
    DW001ProjectionError,
    project_baselines,
    verify_projection_document,
)
from deltawitness.reporting import compute_report_sha256, compute_witness_sha256


_STATE_TREES = {
    "base_base": "1" * 40,
    "base_candidate": "2" * 40,
    "candidate_base": "3" * 40,
    "candidate_candidate": "4" * 40,
}
_STATE_COMMITS = {
    "base_base": "a" * 40,
    "base_candidate": "b" * 40,
    "candidate_base": "c" * 40,
    "candidate_candidate": "d" * 40,
}


def _state_observation(state_name: str, outcome: str, observer: str) -> dict[str, object]:
    expected = CANONICAL_EXPECTATIONS[state_name]
    if outcome == "pass":
        return_code = 0
        timed_out = False
        observation_error = None
    elif outcome == "fail":
        return_code = 1
        timed_out = False
        observation_error = None
    elif outcome == "error":
        return_code = 2
        timed_out = False
        observation_error = "unclassified_exit_code"
    elif outcome == "timeout":
        return_code = None
        timed_out = True
        observation_error = None
    else:
        raise AssertionError(f"Unsupported test outcome: {outcome}")

    if observer == "outcome-receipt-v1" and outcome in {"pass", "fail"}:
        receipt_sha256: str | None = "7" * 64
        receipt_outcome: str | None = "passed" if outcome == "pass" else "test_failure"
        receipt_producer: dict[str, str] | None = {
            "name": "deltawitness-unittest",
            "version": "0.0.3",
        }
        receipt_counts: dict[str, int] | None = {
            "tests_run": 1,
            "passed": 1 if outcome == "pass" else 0,
            "failed": 1 if outcome == "fail" else 0,
            "errors": 0,
            "skipped": 0,
            "expected_failures": 0,
            "unexpected_successes": 0,
        }
    else:
        receipt_sha256 = None
        receipt_outcome = None
        receipt_producer = None
        receipt_counts = None

    return {
        "state": state_name,
        "commit_sha": _STATE_COMMITS[state_name],
        "tree_sha": _STATE_TREES[state_name],
        "observed": outcome,
        "expected": expected,
        "matched": outcome == expected,
        "return_code": return_code,
        "duration_seconds": 0.01,
        "timed_out": timed_out,
        "stdout_sha256": "5" * 64,
        "stderr_sha256": "6" * 64,
        "stdout": None,
        "stderr": None,
        "observer": observer,
        "invocation_binding": "8" * 64,
        "receipt_sha256": receipt_sha256,
        "receipt_outcome": receipt_outcome,
        "receipt_producer": receipt_producer,
        "receipt_counts": receipt_counts,
        "observation_error": observation_error,
    }


def _claim(
    claim_id: str,
    outcomes: dict[str, str],
    observer: str,
) -> dict[str, object]:
    states = [_state_observation(state, outcomes[state], observer) for state in STATE_ORDER]
    return {
        "claim_id": claim_id,
        "description": "Synthetic DW-001 projection fixture.",
        "observer": observer,
        "supported": all(state["matched"] for state in states),
        "command": ["python", "-m", "unittest"],
        "states": states,
    }


def _resign(report: dict[str, object]) -> None:
    claims = report["claims"]
    assert isinstance(claims, list)
    for claim in claims:
        assert isinstance(claim, dict)
        states = claim["states"]
        assert isinstance(states, list)
        claim["supported"] = all(state["matched"] for state in states)
    all_states = [state for claim in claims for state in claim["states"]]
    report["complete"] = all(state["observed"] in {"pass", "fail"} for state in all_states)
    report["supported"] = bool(report["complete"]) and all(claim["supported"] for claim in claims)
    report["witness_sha256"] = None
    report["report_sha256"] = None
    report["witness_sha256"] = compute_witness_sha256(report)
    report["report_sha256"] = compute_report_sha256(report)


def _report(
    outcomes: dict[str, str] | None = None,
    *,
    observers: tuple[str, ...] = ("exit-code-v1",),
) -> dict[str, object]:
    selected_outcomes = outcomes or dict(CANONICAL_EXPECTATIONS)
    claims = [
        _claim(f"claim-{index}", selected_outcomes, observer)
        for index, observer in enumerate(observers, start=1)
    ]
    report: dict[str, object] = {
        "schema_version": "0.3",
        "tool_version": "0.0.3",
        "created_at": "2026-08-15T00:00:00Z",
        "repository": "synthetic",
        "base_sha": _STATE_COMMITS["base_base"],
        "head_sha": _STATE_COMMITS["candidate_candidate"],
        "spec_path": "deltawitness.toml",
        "spec_external": False,
        "spec_sha256": "9" * 64,
        "execution": {
            "environment_mode": "sanitized-v1",
            "pass_env": [],
            "output_included": False,
            "sandboxed": False,
            "observer_protocols": sorted(set(observers)),
        },
        "classification": {"code": [], "tests": [], "documentation": []},
        "state_trees": dict(_STATE_TREES),
        "state_commits": dict(_STATE_COMMITS),
        "claims": claims,
        "complete": False,
        "supported": False,
        "witness_sha256": None,
        "report_sha256": None,
    }
    _resign(report)
    return report


def _set_outcome(report: dict[str, object], state_name: str, outcome: str) -> None:
    claims = report["claims"]
    assert isinstance(claims, list)
    for claim in claims:
        assert isinstance(claim, dict)
        observer = claim["observer"]
        assert isinstance(observer, str)
        replacement = _state_observation(state_name, outcome, observer)
        states = claim["states"]
        assert isinstance(states, list)
        for index, state in enumerate(states):
            if state["state"] == state_name:
                states[index] = replacement
                break
        else:
            raise AssertionError(f"State not found: {state_name}")
    _resign(report)


def _method_map(projection: dict[str, object]) -> dict[str, dict[str, object]]:
    methods = projection["methods"]
    assert isinstance(methods, list)
    return {method["method_id"]: method for method in methods}


class DW001ProjectionTests(unittest.TestCase):
    def test_canonical_witness_is_accepted_by_every_nested_method(self) -> None:
        projection = project_baselines(_report(), scenario_id="valid-regression-001")

        methods = _method_map(projection)
        self.assertEqual(
            {method_id: method["decision"] for method_id, method in methods.items()},
            {
                "M0_FINAL": "accept",
                "M1_F2P": "accept",
                "M2_F2P_P2P": "accept",
                "M3_FOUR_STATE": "accept",
            },
        )
        valid, errors = verify_projection_document(projection)
        self.assertTrue(valid, errors)

    def test_non_discriminating_candidate_test_is_missed_only_by_final_state(self) -> None:
        report = _report()
        _set_outcome(report, "base_candidate", "pass")

        methods = _method_map(project_baselines(report, scenario_id="nondiscriminating-001"))

        self.assertEqual(methods["M0_FINAL"]["decision"], "accept")
        self.assertEqual(methods["M1_F2P"]["decision"], "reject")
        self.assertEqual(methods["M2_F2P_P2P"]["decision"], "reject")
        self.assertEqual(methods["M3_FOUR_STATE"]["decision"], "reject")

    def test_candidate_regression_against_base_tests_is_added_by_m2(self) -> None:
        report = _report()
        _set_outcome(report, "candidate_base", "fail")

        methods = _method_map(project_baselines(report, scenario_id="regression-001"))

        self.assertEqual(methods["M0_FINAL"]["decision"], "accept")
        self.assertEqual(methods["M1_F2P"]["decision"], "accept")
        self.assertEqual(methods["M2_F2P_P2P"]["decision"], "reject")
        self.assertEqual(methods["M3_FOUR_STATE"]["decision"], "reject")

    def test_invalid_base_endpoint_is_added_only_by_m3(self) -> None:
        report = _report()
        _set_outcome(report, "base_base", "error")

        methods = _method_map(project_baselines(report, scenario_id="invalid-base-001"))

        self.assertEqual(methods["M0_FINAL"]["decision"], "accept")
        self.assertEqual(methods["M1_F2P"]["decision"], "accept")
        self.assertEqual(methods["M2_F2P_P2P"]["decision"], "accept")
        self.assertEqual(methods["M3_FOUR_STATE"]["decision"], "indeterminate")

    def test_indeterminate_required_state_precedes_a_contradiction(self) -> None:
        report = _report()
        _set_outcome(report, "base_candidate", "pass")
        _set_outcome(report, "candidate_base", "error")

        method = _method_map(project_baselines(report, scenario_id="mixed-evidence-001"))[
            "M2_F2P_P2P"
        ]

        self.assertEqual(method["decision"], "indeterminate")
        self.assertEqual(method["reason_code"], "required_state_indeterminate")
        self.assertEqual(method["claims"][0]["indeterminate_states"], ["candidate_base"])
        self.assertEqual(method["claims"][0]["contradicted_states"], ["base_candidate", "candidate_base"])

    def test_not_applicable_is_declared_independently_and_is_method_specific(self) -> None:
        report = _report()
        _set_outcome(report, "base_base", "error")

        methods = _method_map(
            project_baselines(
                report,
                scenario_id="invalid-hybrid-001",
                non_applicable_states={"base_base": "The frozen fixture declares BB semantically invalid."},
            )
        )

        self.assertEqual(methods["M0_FINAL"]["decision"], "accept")
        self.assertEqual(methods["M1_F2P"]["decision"], "accept")
        self.assertEqual(methods["M2_F2P_P2P"]["decision"], "accept")
        self.assertEqual(methods["M3_FOUR_STATE"]["decision"], "not_applicable")
        self.assertEqual(methods["M3_FOUR_STATE"]["claims"], [])

    def test_method_payload_contains_only_its_declared_states(self) -> None:
        methods = _method_map(project_baselines(_report(), scenario_id="visibility-001"))

        for method_id, required_states in METHOD_STATE_SETS:
            with self.subTest(method=method_id):
                claim_states = [
                    state["state"] for state in methods[method_id]["claims"][0]["states"]
                ]
                self.assertEqual(claim_states, list(required_states))

    def test_hidden_state_outcome_cannot_change_an_earlier_method_payload(self) -> None:
        original = _method_map(project_baselines(_report(), scenario_id="hidden-state-001"))
        changed_report = _report()
        _set_outcome(changed_report, "base_base", "error")
        changed = _method_map(
            project_baselines(changed_report, scenario_id="hidden-state-001")
        )

        for method_id in ("M0_FINAL", "M1_F2P", "M2_F2P_P2P"):
            with self.subTest(method=method_id):
                self.assertEqual(original[method_id], changed[method_id])
        self.assertNotEqual(original["M3_FOUR_STATE"], changed["M3_FOUR_STATE"])

    def test_mixed_observer_report_is_rejected_as_a_confounded_arm(self) -> None:
        report = _report(observers=("exit-code-v1", "outcome-receipt-v1"))

        with self.assertRaisesRegex(DW001ProjectionError, "one observer arm"):
            project_baselines(report, scenario_id="mixed-observer-001")

    def test_noncanonical_expectations_are_rejected(self) -> None:
        report = _report()
        claim = report["claims"][0]
        state = claim["states"][1]
        state["expected"] = "pass"
        state["matched"] = state["observed"] == "pass"
        _resign(report)

        with self.assertRaisesRegex(DW001ProjectionError, "expected must be 'fail'"):
            project_baselines(report, scenario_id="noncanonical-001")

    def test_digest_invalid_source_report_is_rejected(self) -> None:
        report = _report()
        report["report_sha256"] = "0" * 64

        with self.assertRaisesRegex(DW001ProjectionError, "integrity verification failed"):
            project_baselines(report, scenario_id="tampered-source-001")

    def test_projection_digest_is_deterministic_and_detects_tampering(self) -> None:
        first = project_baselines(_report(), scenario_id="digest-001")
        second = project_baselines(_report(), scenario_id="digest-001")

        self.assertEqual(first, second)
        valid, errors = verify_projection_document(first)
        self.assertTrue(valid, errors)

        tampered = deepcopy(first)
        tampered["methods"][0]["decision"] = "reject"
        valid, errors = verify_projection_document(tampered)
        self.assertFalse(valid)
        self.assertTrue(any("projection digest mismatch" in error for error in errors))

    def test_invalid_scenario_id_and_applicability_state_are_rejected(self) -> None:
        with self.assertRaisesRegex(DW001ProjectionError, "scenario_id"):
            project_baselines(_report(), scenario_id="../holdout")
        with self.assertRaisesRegex(DW001ProjectionError, "unknown state"):
            project_baselines(
                _report(),
                scenario_id="applicability-001",
                non_applicable_states={"unknown": "Not a matrix state."},
            )


if __name__ == "__main__":
    unittest.main()
