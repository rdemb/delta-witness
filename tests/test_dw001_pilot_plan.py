from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from deltawitness.claim_witness import (
    AGGREGATE_RULE,
    build_claim_witness_declaration,
)
from deltawitness.dw001_pilot import (
    PILOT_ID,
    PLAN_SCHEMA_VERSION,
    build_development_pilot_plan,
    compute_development_pilot_plan_sha256,
    run_development_pilot,
    verify_development_pilot_plan_document,
)
from deltawitness.dw001_scenarios import (
    build_fixture_descriptor,
    compute_fixture_specification_sha256,
)
from deltawitness.reporting import canonical_json


_PROTOCOL_SHA = "a" * 40
_IMPLEMENTATION_SHA = "b" * 40
_CLAIM_ID = "role-check-regression"

_EXPECTED_CASES = (
    (
        "dev-v1-valid-o0",
        "valid-discriminating-regression",
        "exit-code-v1",
        True,
        ["test_access.AccessTests.test_viewer_is_denied"],
        "supported",
    ),
    (
        "dev-v1-valid-o1",
        "valid-discriminating-regression",
        "outcome-receipt-v1",
        True,
        ["test_access.AccessTests.test_viewer_is_denied"],
        "supported",
    ),
    (
        "dev-v1-nondiscriminating-o0",
        "non-discriminating-candidate-test",
        "exit-code-v1",
        False,
        [],
        "not_applicable",
    ),
    (
        "dev-v1-nondiscriminating-o1",
        "non-discriminating-candidate-test",
        "outcome-receipt-v1",
        False,
        [],
        "not_applicable",
    ),
    (
        "dev-v1-candidate-regression-o0",
        "candidate-regression-against-base-tests",
        "exit-code-v1",
        False,
        [],
        "not_applicable",
    ),
    (
        "dev-v1-candidate-regression-o1",
        "candidate-regression-against-base-tests",
        "outcome-receipt-v1",
        False,
        [],
        "not_applicable",
    ),
    (
        "dev-v1-import-error-o0",
        "wrong-reason-base-import-failure",
        "exit-code-v1",
        True,
        ["test_access.AccessTests.test_role_is_normalized"],
        "indeterminate",
    ),
    (
        "dev-v1-import-error-o1",
        "wrong-reason-base-import-failure",
        "outcome-receipt-v1",
        True,
        ["test_access.AccessTests.test_role_is_normalized"],
        "indeterminate",
    ),
    (
        "dev-v1-unrelated-assertion-o0",
        "wrong-reason-unrelated-assertion",
        "exit-code-v1",
        True,
        ["test_access.AccessTests.test_viewer_result_is_boolean"],
        "unsupported",
    ),
    (
        "dev-v1-unrelated-assertion-o1",
        "wrong-reason-unrelated-assertion",
        "outcome-receipt-v1",
        True,
        ["test_access.AccessTests.test_viewer_result_is_boolean"],
        "unsupported",
    ),
)

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "DW-001"
    / "schema"
    / "development-pilot-plan.schema.json"
)


class DW001DevelopmentPilotPlanTests(unittest.TestCase):
    def _plan(self):
        return build_development_pilot_plan(
            protocol_commit_sha=_PROTOCOL_SHA,
            implementation_commit_sha=_IMPLEMENTATION_SHA,
        )

    def test_plan_is_deterministic_and_exactly_ten_arms(self) -> None:
        first = self._plan()
        second = self._plan()

        self.assertEqual(first, second)
        self.assertEqual(canonical_json(first), canonical_json(second))
        self.assertEqual(first["schema_version"], PLAN_SCHEMA_VERSION)
        self.assertEqual(first["study_id"], "DW-001")
        self.assertEqual(first["pilot_id"], PILOT_ID)
        self.assertEqual(first["partition"], "development")
        self.assertEqual(first["protocol_commit_sha"], _PROTOCOL_SHA)
        self.assertEqual(first["implementation_commit_sha"], _IMPLEMENTATION_SHA)
        self.assertEqual(len(first["case_arms"]), 10)
        self.assertEqual(
            [case["order"] for case in first["case_arms"]],
            list(range(1, 11)),
        )
        self.assertEqual(
            [case["case_id"] for case in first["case_arms"]],
            [case[0] for case in _EXPECTED_CASES],
        )
        valid, errors = verify_development_pilot_plan_document(first)
        self.assertTrue(valid, errors)

    def test_case_semantics_are_derived_from_fixed_generators(self) -> None:
        plan = self._plan()

        for case, expected in zip(plan["case_arms"], _EXPECTED_CASES, strict=True):
            (
                case_id,
                family_id,
                observer,
                localization_required,
                selectors,
                expected_status,
            ) = expected
            with self.subTest(case=case_id):
                self.assertEqual(case["case_id"], case_id)
                self.assertEqual(case["scenario_id"], case_id)
                self.assertEqual(case["family_id"], family_id)
                self.assertEqual(case["observer"], observer)
                self.assertEqual(case["partition"], "development")
                self.assertIs(case["primary_denominator_eligible"], False)

                descriptor = build_fixture_descriptor(
                    scenario_id=case_id,
                    family_id=family_id,
                    observer=observer,
                )
                spec_sha256 = compute_fixture_specification_sha256(descriptor)
                self.assertEqual(case["descriptor_sha256"], descriptor["descriptor_sha256"])
                self.assertEqual(case["spec_sha256"], spec_sha256)
                self.assertEqual(case["control_role"], descriptor["control_role"])
                self.assertEqual(case["observer_id"], descriptor["observer_id"])
                self.assertEqual(case["expected_states"], descriptor["expected_states"])
                self.assertEqual(case["expected_methods"], descriptor["expected_methods"])

                localization = case["localization"]
                self.assertIs(localization["required"], localization_required)
                self.assertEqual(localization["selectors"], selectors)
                self.assertEqual(localization["expected_status"], expected_status)
                if localization_required:
                    declaration = build_claim_witness_declaration(
                        spec_sha256=spec_sha256,
                        claim_id=_CLAIM_ID,
                        selectors=selectors,
                    )
                    self.assertEqual(localization["aggregate_rule"], AGGREGATE_RULE)
                    self.assertEqual(
                        localization["declaration_sha256"],
                        declaration["declaration_sha256"],
                    )
                else:
                    self.assertIsNone(localization["aggregate_rule"])
                    self.assertIsNone(localization["declaration_sha256"])

    def test_plan_cannot_authorize_holdout_or_primary_denominator(self) -> None:
        plan = self._plan()
        self.assertEqual(plan["partition"], "development")
        self.assertTrue(
            all(
                case["partition"] == "development"
                and case["primary_denominator_eligible"] is False
                for case in plan["case_arms"]
            )
        )
        encoded = json.dumps(plan, sort_keys=True)
        self.assertNotIn("holdout_committed", encoded)
        self.assertNotIn("primary_denominator_eligible\": true", encoded)

    def test_recomputed_digest_cannot_hide_case_or_expected_method_drift(self) -> None:
        for mutator, expected_error in (
            (
                lambda plan: plan["case_arms"][0].__setitem__(
                    "family_id", "non-discriminating-candidate-test"
                ),
                "family",
            ),
            (
                lambda plan: plan["case_arms"][0]["expected_methods"][0].__setitem__(
                    "decision", "reject"
                ),
                "expected_methods",
            ),
            (
                lambda plan: plan["case_arms"][0].__setitem__(
                    "primary_denominator_eligible", True
                ),
                "denominator",
            ),
        ):
            with self.subTest(error=expected_error):
                tampered = deepcopy(self._plan())
                mutator(tampered)
                tampered["plan_sha256"] = compute_development_pilot_plan_sha256(tampered)
                valid, errors = verify_development_pilot_plan_document(tampered)
                self.assertFalse(valid)
                self.assertTrue(
                    any(expected_error in error for error in errors),
                    errors,
                )

    def test_plan_rejects_invalid_revision_and_nonfinite_cost_policy(self) -> None:
        plan = self._plan()
        for field, value in (
            ("protocol_commit_sha", "main"),
            ("implementation_commit_sha", "f" * 64),
        ):
            with self.subTest(field=field):
                tampered = deepcopy(plan)
                tampered[field] = value
                tampered["plan_sha256"] = compute_development_pilot_plan_sha256(tampered)
                valid, errors = verify_development_pilot_plan_document(tampered)
                self.assertFalse(valid)
                self.assertTrue(any(field in error for error in errors), errors)

        tampered = deepcopy(plan)
        tampered["cost_contract"]["missing_numeric_value"] = 0
        tampered["plan_sha256"] = compute_development_pilot_plan_sha256(tampered)
        valid, errors = verify_development_pilot_plan_document(tampered)
        self.assertFalse(valid)
        self.assertTrue(any("cost_contract" in error for error in errors), errors)

    def test_schema_is_strict_and_matches_emitted_root(self) -> None:
        plan = self._plan()
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))

        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertIs(schema["additionalProperties"], False)
        self.assertEqual(set(schema["required"]), set(plan))
        self.assertEqual(set(schema["properties"]), set(plan))
        self.assertEqual(
            schema["properties"]["schema_version"]["const"],
            PLAN_SCHEMA_VERSION,
        )

    def test_unimplemented_runner_refuses_execution(self) -> None:
        with self.assertRaises(Exception):
            run_development_pilot(self._plan(), Path("unused-output"))


if __name__ == "__main__":
    unittest.main()
