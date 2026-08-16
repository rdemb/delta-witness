from __future__ import annotations

from copy import deepcopy
import json
import math
from pathlib import Path
import unittest

from deltawitness.dw001_mutation_results import (
    RESULT_ID,
    RESULT_SCHEMA_VERSION,
    compute_mutation_result_report_sha256,
    compute_mutation_result_semantic_sha256,
    run_claim_scoped_mutation_result,
    verify_claim_scoped_mutation_result_document,
)
from deltawitness.reporting import canonical_json, load_report


_ROOT = Path(__file__).resolve().parents[1]
_PLAN_PATH = (
    _ROOT / "research" / "DW-001" / "claim-scoped-mutation-plan.v1.json"
)
_CATALOG_PATH = (
    _ROOT / "research" / "DW-001" / "claim-scoped-mutant-catalog.v1.json"
)
_SCHEMA_PATH = (
    _ROOT
    / "research"
    / "DW-001"
    / "schema"
    / "claim-scoped-mutation-result.schema.json"
)

_ROOT_FIELDS = {
    "schema_version",
    "study_id",
    "result_id",
    "partition",
    "plan_sha256",
    "catalog_sha256",
    "created_at",
    "runtime",
    "source",
    "candidate_baseline",
    "records",
    "summary",
    "policy",
    "cost",
    "semantic_sha256",
    "report_sha256",
}
_EXPECTED_GENERIC = {
    "return-constant-false-v1": {
        "strong": ["fail", "pass"],
        "weak": ["pass"],
        "reference": ["fail", "pass"],
    },
    "return-constant-true-v1": {
        "strong": ["pass", "fail"],
        "weak": ["pass"],
        "reference": ["pass", "fail"],
    },
    "comparison-eq-to-ne-v1": {
        "strong": ["fail", "fail"],
        "weak": ["pass"],
        "reference": ["fail", "fail"],
    },
}


def _walk(value: object):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _profile(record: dict[str, object], profile_id: str) -> dict[str, object]:
    matches = [
        profile
        for profile in record["profiles"]
        if profile["profile_id"] == profile_id
    ]
    if len(matches) != 1:
        raise AssertionError((record["record_id"], profile_id, matches))
    return matches[0]


class DW001ClaimScopedMutationResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = load_report(_PLAN_PATH)
        cls.catalog = load_report(_CATALOG_PATH)
        cls.first = run_claim_scoped_mutation_result(cls.plan, cls.catalog)
        cls.second = run_claim_scoped_mutation_result(cls.plan, cls.catalog)

    def test_result_is_strict_bound_and_self_verifying(self) -> None:
        self.assertEqual(set(self.first), _ROOT_FIELDS)
        self.assertEqual(self.first["schema_version"], RESULT_SCHEMA_VERSION)
        self.assertEqual(self.first["study_id"], "DW-001")
        self.assertEqual(self.first["result_id"], RESULT_ID)
        self.assertEqual(self.first["partition"], "development")
        self.assertEqual(self.first["plan_sha256"], self.plan["plan_sha256"])
        self.assertEqual(
            self.first["catalog_sha256"],
            self.catalog["catalog_sha256"],
        )
        valid, errors = verify_claim_scoped_mutation_result_document(
            self.first,
            self.plan,
            self.catalog,
        )
        self.assertTrue(valid, errors)

    def test_candidate_baseline_passes_every_frozen_selector(self) -> None:
        baseline = self.first["candidate_baseline"]
        self.assertEqual(baseline["implementation_id"], "candidate-baseline-v1")
        self.assertEqual(baseline["execution_status"], "executed")
        self.assertEqual(baseline["record_role"], "candidate_baseline")
        self.assertIs(baseline["counts_toward_generic_generalization"], False)

        strong = _profile(baseline, "strong-authorization-oracle-v1")
        weak = _profile(baseline, "weak-boolean-proxy-v1")
        self.assertEqual(strong["outcome"], "baseline_passed")
        self.assertEqual(weak["outcome"], "baseline_passed")
        self.assertEqual(
            [selector["observed"] for selector in strong["selectors"]],
            ["pass", "pass"],
        )
        self.assertEqual(
            [selector["observed"] for selector in weak["selectors"]],
            ["pass"],
        )
        self.assertEqual(baseline["reference"]["outcome"], "reference_passed")
        self.assertEqual(
            [
                selector["observed"]
                for selector in baseline["reference"]["selectors"]
            ],
            ["pass", "pass"],
        )

    def test_generic_mutants_match_preregistered_paired_outcomes(self) -> None:
        generic = [
            record
            for record in self.first["records"]
            if record["record_role"] == "generic_operator"
        ]
        self.assertEqual(
            [record["operator_id"] for record in generic],
            list(_EXPECTED_GENERIC),
        )

        for record in generic:
            operator_id = record["operator_id"]
            expected = _EXPECTED_GENERIC[operator_id]
            with self.subTest(operator=operator_id):
                self.assertEqual(record["catalog_status"], "generated")
                self.assertEqual(record["execution_status"], "executed")
                self.assertIs(
                    record["counts_toward_generic_generalization"],
                    True,
                )
                strong = _profile(
                    record,
                    "strong-authorization-oracle-v1",
                )
                weak = _profile(record, "weak-boolean-proxy-v1")
                self.assertEqual(strong["outcome"], "killed")
                self.assertEqual(weak["outcome"], "survived")
                self.assertEqual(
                    [item["observed"] for item in strong["selectors"]],
                    expected["strong"],
                )
                self.assertEqual(
                    [item["observed"] for item in weak["selectors"]],
                    expected["weak"],
                )
                self.assertEqual(
                    record["reference"]["outcome"],
                    "claim_violation_observed",
                )
                self.assertEqual(
                    [
                        item["observed"]
                        for item in record["reference"]["selectors"]
                    ],
                    expected["reference"],
                )

    def test_historical_control_is_executed_but_excluded_from_generic_evidence(self) -> None:
        matches = [
            record
            for record in self.first["records"]
            if record["record_role"] == "historical_challenge_control"
        ]
        self.assertEqual(len(matches), 1)
        record = matches[0]
        self.assertEqual(record["record_id"], "nonempty-role-boolean-v1")
        self.assertEqual(record["execution_status"], "executed")
        self.assertIs(record["counts_toward_generic_generalization"], False)
        self.assertEqual(
            [
                item["observed"]
                for item in _profile(
                    record,
                    "strong-authorization-oracle-v1",
                )["selectors"]
            ],
            ["pass", "fail"],
        )
        self.assertEqual(
            _profile(record, "strong-authorization-oracle-v1")["outcome"],
            "killed",
        )
        self.assertEqual(
            _profile(record, "weak-boolean-proxy-v1")["outcome"],
            "survived",
        )
        self.assertEqual(
            record["reference"]["outcome"],
            "claim_violation_observed",
        )

    def test_generation_only_records_are_retained_and_never_executed(self) -> None:
        records = {
            record["catalog_status"]: record
            for record in self.first["records"]
            if record["record_role"] == "generation_control"
        }
        self.assertEqual(set(records), {"duplicate", "not_applicable", "invalid"})
        self.assertEqual(
            records["duplicate"]["execution_status"],
            "not_executed_duplicate",
        )
        self.assertEqual(
            records["not_applicable"]["execution_status"],
            "not_executed_not_applicable",
        )
        self.assertEqual(
            records["invalid"]["execution_status"],
            "not_executed_invalid",
        )
        for record in records.values():
            self.assertEqual(record["profiles"], [])
            self.assertIsNone(record["reference"])
            self.assertEqual(record["cost"]["command_count"], 0)
            self.assertEqual(record["cost"]["selector_count"], 0)
            self.assertIs(record["counts_toward_generic_generalization"], False)

    def test_all_executed_selectors_have_consistent_typed_receipts(self) -> None:
        executed = [
            self.first["candidate_baseline"],
            *[
                record
                for record in self.first["records"]
                if record["execution_status"] == "executed"
            ],
        ]
        observations = []
        for record in executed:
            for profile in record["profiles"]:
                observations.extend(profile["selectors"])
            observations.extend(record["reference"]["selectors"])

        self.assertEqual(len(observations), 25)
        for observation in observations:
            with self.subTest(
                implementation=observation["implementation_id"],
                selector=observation["selector"],
            ):
                self.assertIn(observation["observed"], {"pass", "fail"})
                self.assertFalse(observation["timed_out"])
                self.assertIsNone(observation["observation_error"])
                self.assertEqual(
                    observation["return_code"],
                    0 if observation["observed"] == "pass" else 1,
                )
                self.assertEqual(
                    observation["receipt_outcome"],
                    "passed"
                    if observation["observed"] == "pass"
                    else "test_failure",
                )
                self.assertEqual(
                    observation["receipt_counts"]["tests_run"],
                    1,
                )
                self.assertEqual(observation["receipt_counts"]["errors"], 0)
                self.assertEqual(
                    observation["receipt_counts"]["failures"],
                    0 if observation["observed"] == "pass" else 1,
                )
                self.assertTrue(observation["receipt_sha256"])
                self.assertTrue(observation["invocation_binding"])
                self.assertTrue(math.isfinite(observation["duration_seconds"]))
                self.assertGreaterEqual(observation["duration_seconds"], 0.0)

    def test_summary_policy_and_cost_preserve_denominators_and_no_score(self) -> None:
        self.assertEqual(
            self.first["summary"],
            {
                "candidate_baseline_valid": True,
                "catalog_records": 6,
                "generic_mutants_executed": 3,
                "historical_controls_executed": 1,
                "generation_records_not_executed": 3,
                "generic_strong_killed": 3,
                "generic_strong_survived": 0,
                "generic_strong_indeterminate": 0,
                "generic_weak_killed": 0,
                "generic_weak_survived": 3,
                "generic_weak_indeterminate": 0,
                "generic_claim_violations_observed": 3,
                "mutation_score": None,
            },
        )
        self.assertEqual(
            self.first["policy"],
            {
                "retain_complete_mutant_table": True,
                "headline_score": None,
                "universal_threshold": None,
                "merge_blocker_authorized": False,
                "ecological_inference_allowed": False,
                "holdout_selected": False,
                "primary_denominator_eligible": False,
                "generic_operator_generalization_allowed": False,
            },
        )
        self.assertEqual(self.first["cost"]["command_count"], 25)
        self.assertEqual(self.first["cost"]["selector_count"], 25)
        self.assertEqual(self.first["cost"]["implementation_count"], 5)
        for field in ("wall_clock_seconds", "cpu_seconds"):
            self.assertTrue(math.isfinite(self.first["cost"][field]))
            self.assertGreaterEqual(self.first["cost"][field], 0.0)

    def test_repeated_runs_preserve_semantic_digest_and_outcomes(self) -> None:
        self.assertEqual(
            self.first["semantic_sha256"],
            self.second["semantic_sha256"],
        )
        first_semantic = deepcopy(self.first)
        second_semantic = deepcopy(self.second)
        for document in (first_semantic, second_semantic):
            document["created_at"] = None
            document["runtime"] = None
            document["report_sha256"] = None
            document["semantic_sha256"] = None
            document["cost"]["wall_clock_seconds"] = None
            document["cost"]["cpu_seconds"] = None
            for record in [document["candidate_baseline"], *document["records"]]:
                record["cost"]["wall_clock_seconds"] = None
                record["cost"]["cpu_seconds"] = None
                for profile in record["profiles"]:
                    for selector in profile["selectors"]:
                        selector["duration_seconds"] = None
                if record["reference"] is not None:
                    for selector in record["reference"]["selectors"]:
                        selector["duration_seconds"] = None
        self.assertEqual(canonical_json(first_semantic), canonical_json(second_semantic))

    def test_recomputed_digests_cannot_hide_source_outcome_or_policy_drift(self) -> None:
        for mutator, expected in (
            (
                lambda document: document.__setitem__("plan_sha256", "f" * 64),
                "plan_sha256",
            ),
            (
                lambda document: document["records"][0].__setitem__(
                    "record_id", "substituted-mutant"
                ),
                "record_id",
            ),
            (
                lambda document: document["records"][0]["profiles"][0][
                    "selectors"
                ][0].__setitem__("observed", "pass"),
                "observed",
            ),
            (
                lambda document: document["records"][3].__setitem__(
                    "execution_status", "executed"
                ),
                "execution_status",
            ),
            (
                lambda document: document["policy"].__setitem__(
                    "merge_blocker_authorized", True
                ),
                "merge_blocker_authorized",
            ),
            (
                lambda document: document["summary"].__setitem__(
                    "mutation_score", 1.0
                ),
                "mutation_score",
            ),
        ):
            with self.subTest(expected=expected):
                tampered = deepcopy(self.first)
                mutator(tampered)
                tampered["semantic_sha256"] = (
                    compute_mutation_result_semantic_sha256(tampered)
                )
                tampered["report_sha256"] = (
                    compute_mutation_result_report_sha256(tampered)
                )
                valid, errors = verify_claim_scoped_mutation_result_document(
                    tampered,
                    self.plan,
                    self.catalog,
                )
                self.assertFalse(valid)
                self.assertTrue(any(expected in error for error in errors), errors)

    def test_malformed_nonfinite_and_wrong_type_evidence_fails_closed(self) -> None:
        for malformed in (None, [], "result", 7, {}):
            with self.subTest(root=type(malformed).__name__):
                valid, errors = verify_claim_scoped_mutation_result_document(
                    malformed,
                    self.plan,
                    self.catalog,
                )
                self.assertFalse(valid)
                self.assertTrue(errors)

        nonfinite = deepcopy(self.first)
        nonfinite["cost"]["wall_clock_seconds"] = math.nan
        valid, errors = verify_claim_scoped_mutation_result_document(
            nonfinite,
            self.plan,
            self.catalog,
        )
        self.assertFalse(valid)
        self.assertTrue(errors)

        wrong_type = deepcopy(self.first)
        wrong_type["records"] = {"mutant": wrong_type["records"][0]}
        valid, errors = verify_claim_scoped_mutation_result_document(
            wrong_type,
            self.plan,
            self.catalog,
        )
        self.assertFalse(valid)
        self.assertTrue(errors)

    def test_schema_is_strict_and_public_artifact_is_safe(self) -> None:
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )
        self.assertIs(schema["additionalProperties"], False)
        self.assertEqual(set(schema["required"]), _ROOT_FIELDS)
        self.assertEqual(set(schema["properties"]), _ROOT_FIELDS)
        self.assertEqual(
            schema["properties"]["schema_version"]["const"],
            RESULT_SCHEMA_VERSION,
        )
        for node in _walk(schema):
            if isinstance(node, dict) and node.get("type") == "object":
                self.assertIs(node.get("additionalProperties"), False, node)

        encoded = json.dumps(self.first, sort_keys=True)
        for prohibited in (
            "def is_admin",
            "return user.get",
            "assertTrue",
            "assertFalse",
            "/tmp/",
            "\\Temp\\",
            "Traceback (most recent call last)",
            '"stdout"',
            '"stderr"',
            "credential",
            "environment_values",
            "private_endpoint",
        ):
            self.assertNotIn(prohibited, encoded)


if __name__ == "__main__":
    unittest.main()
