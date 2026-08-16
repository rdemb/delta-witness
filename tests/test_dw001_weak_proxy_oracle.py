from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from deltawitness.claim_witness import (
    build_claim_witness_declaration,
    run_claim_witness_localization,
    verify_claim_witness_declaration_document,
    verify_claim_witness_localization_document,
)
from deltawitness.config import load_config
from deltawitness.dw001 import project_baselines, verify_projection_document
from deltawitness.dw001_fixture_binding import (
    build_fixture_manifest_binding,
    verify_fixture_manifest_binding_document,
)
from deltawitness.dw001_oracle_challenge import (
    CHALLENGE_ID,
    CHALLENGE_SCHEMA_VERSION,
    DECLARED_SELECTOR,
    FAMILY_ID,
    HIDDEN_CLAIM_SELECTOR,
    MUTANT_ID,
    compute_weak_oracle_challenge_sha256,
    compute_weak_oracle_report_sha256,
    run_weak_proxy_oracle_challenge,
    verify_weak_oracle_challenge_document,
)
from deltawitness.dw001_scenarios import (
    SUPPORTED_FAMILIES,
    build_fixture_descriptor,
    materialize_synthetic_fixture,
    verify_fixture_identity_document,
    verify_materialized_fixture,
)
from deltawitness.matrix import report_to_dict, verify_repository
from deltawitness.reporting import canonical_json, verify_report_document
from dw001_binding_support import manifest_from_fixture


_SCENARIO_ID = "weak-proxy-oracle-001"
_ROOT = Path(__file__).resolve().parents[1]
_SCHEMA_DIR = _ROOT / "research" / "DW-001" / "schema"
_TASK_PROMPT = (
    "Fix is_admin so only the admin role is authorized and add a regression "
    "test proving that a viewer is denied."
)
_ROOT_FIELDS = {
    "schema_version",
    "study_id",
    "challenge_id",
    "scenario_id",
    "family_id",
    "partition",
    "task",
    "source",
    "claim",
    "mutation",
    "current_evidence",
    "controlled_executions",
    "finding",
    "limitations",
    "challenge_sha256",
    "report_sha256",
}


def _method_decisions(projection: dict[str, object]) -> dict[str, str]:
    methods = projection["methods"]
    assert isinstance(methods, list)
    return {method["method_id"]: method["decision"] for method in methods}


def _run_arm(observer: str) -> dict[str, object]:
    descriptor = build_fixture_descriptor(
        scenario_id=_SCENARIO_ID,
        family_id=FAMILY_ID,
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

        config = load_config(repository / identity["specification"]["path"])
        report = report_to_dict(
            verify_repository(
                repository,
                identity["git"]["base_commit_sha"],
                identity["git"]["head_commit_sha"],
                config,
            )
        )
        report_valid, report_errors = verify_report_document(report)
        if not report_valid:
            raise AssertionError(report_errors)

        projection = project_baselines(report, scenario_id=_SCENARIO_ID)
        projection_valid, projection_errors = verify_projection_document(projection)
        if not projection_valid:
            raise AssertionError(projection_errors)

        declaration = build_claim_witness_declaration(
            spec_sha256=identity["specification"]["sha256"],
            claim_id="role-check-regression",
            selectors=[DECLARED_SELECTOR],
        )
        declaration_valid, declaration_errors = (
            verify_claim_witness_declaration_document(declaration)
        )
        if not declaration_valid:
            raise AssertionError(declaration_errors)

        localization = run_claim_witness_localization(
            repository,
            config,
            report,
            declaration,
        )
        localization_valid, localization_errors = (
            verify_claim_witness_localization_document(
                localization,
                declaration,
                report,
            )
        )
        if not localization_valid:
            raise AssertionError(localization_errors)

        challenge = run_weak_proxy_oracle_challenge(
            descriptor,
            identity,
            report,
            projection,
            declaration,
            localization,
        )
        challenge_valid, challenge_errors = verify_weak_oracle_challenge_document(
            challenge,
            descriptor,
            identity,
            report,
            projection,
            declaration,
            localization,
        )
        if not challenge_valid:
            raise AssertionError(challenge_errors)

    return {
        "descriptor": descriptor,
        "identity": identity,
        "manifest": manifest,
        "binding": binding,
        "report": report,
        "projection": projection,
        "declaration": declaration,
        "localization": localization,
        "challenge": challenge,
    }


class DW001WeakProxyOracleTests(unittest.TestCase):
    def test_family_and_challenge_are_versioned_in_all_public_schemas(self) -> None:
        self.assertIn(FAMILY_ID, SUPPORTED_FAMILIES)
        for name in (
            "fixture-descriptor.schema.json",
            "fixture-identity.schema.json",
            "fixture-manifest-binding.schema.json",
        ):
            schema = json.loads((_SCHEMA_DIR / name).read_text(encoding="utf-8"))
            self.assertIn(FAMILY_ID, schema["properties"]["family_id"]["enum"], name)

        challenge_schema = json.loads(
            (_SCHEMA_DIR / "weak-oracle-challenge.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            challenge_schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )
        self.assertIs(challenge_schema["additionalProperties"], False)
        self.assertEqual(set(challenge_schema["required"]), _ROOT_FIELDS)
        self.assertEqual(set(challenge_schema["properties"]), _ROOT_FIELDS)
        self.assertEqual(
            challenge_schema["properties"]["schema_version"]["const"],
            CHALLENGE_SCHEMA_VERSION,
        )

    def test_current_layers_accept_the_genuine_declared_fail_to_pass_witness(self) -> None:
        for observer in ("exit-code-v1", "outcome-receipt-v1"):
            with self.subTest(observer=observer):
                artifacts = _run_arm(observer)
                report = artifacts["report"]
                projection = artifacts["projection"]
                localization = artifacts["localization"]
                states = {
                    state["state"]: state
                    for state in report["claims"][0]["states"]
                }

                self.assertEqual(
                    [states[state]["observed"] for state in (
                        "base_base",
                        "base_candidate",
                        "candidate_base",
                        "candidate_candidate",
                    )],
                    ["pass", "fail", "pass", "pass"],
                )
                self.assertTrue(report["complete"])
                self.assertTrue(report["supported"])
                self.assertEqual(
                    _method_decisions(projection),
                    {
                        "M0_FINAL": "accept",
                        "M1_F2P": "accept",
                        "M2_F2P_P2P": "accept",
                        "M3_FOUR_STATE": "accept",
                    },
                )
                self.assertEqual(localization["aggregate_status"], "supported")
                self.assertEqual(
                    localization["selectors"][0]["classification"],
                    "discriminating",
                )

                if observer == "outcome-receipt-v1":
                    base_candidate = states["base_candidate"]
                    self.assertEqual(
                        base_candidate["receipt_outcome"],
                        "test_failure",
                    )
                    self.assertGreaterEqual(
                        base_candidate["receipt_counts"]["failures"],
                        1,
                    )
                    self.assertEqual(
                        base_candidate["receipt_counts"]["errors"],
                        0,
                    )

    def test_fixed_mutant_survives_declared_selector_but_violates_hidden_claim(self) -> None:
        artifacts = _run_arm("outcome-receipt-v1")
        challenge = artifacts["challenge"]

        self.assertEqual(set(challenge), _ROOT_FIELDS)
        self.assertEqual(challenge["schema_version"], CHALLENGE_SCHEMA_VERSION)
        self.assertEqual(challenge["challenge_id"], CHALLENGE_ID)
        self.assertEqual(challenge["family_id"], FAMILY_ID)
        self.assertEqual(challenge["partition"], "development")
        self.assertEqual(challenge["task"]["prompt"], _TASK_PROMPT)
        self.assertEqual(
            challenge["task"]["generation_mode"],
            "fixed_owned_synthetic_agent_workflow_surrogate",
        )
        self.assertIsNone(challenge["task"]["model_identity"])
        self.assertEqual(challenge["claim"]["declared_selector"], DECLARED_SELECTOR)
        self.assertEqual(
            challenge["claim"]["hidden_claim_selector"],
            HIDDEN_CLAIM_SELECTOR,
        )
        self.assertEqual(challenge["mutation"]["mutant_id"], MUTANT_ID)
        self.assertIs(challenge["mutation"]["caller_supplied"], False)
        self.assertEqual(
            challenge["current_evidence"]["localization_status"],
            "supported",
        )
        self.assertEqual(
            challenge["current_evidence"]["method_decisions"],
            [
                {"method_id": "M0_FINAL", "decision": "accept"},
                {"method_id": "M1_F2P", "decision": "accept"},
                {"method_id": "M2_F2P_P2P", "decision": "accept"},
                {"method_id": "M3_FOUR_STATE", "decision": "accept"},
            ],
        )

        observed = {
            (item["implementation"], item["test_role"]): item["observed"]
            for item in challenge["controlled_executions"]
        }
        self.assertEqual(
            observed,
            {
                ("base", "declared_selector"): "fail",
                ("candidate", "declared_selector"): "pass",
                ("mutant", "declared_selector"): "pass",
                ("candidate", "hidden_claim"): "pass",
                ("mutant", "hidden_claim"): "fail",
            },
        )
        self.assertIs(
            challenge["finding"]["declared_selector_discriminates_base_candidate"],
            True,
        )
        self.assertIs(
            challenge["finding"]["mutant_survives_declared_selector"],
            True,
        )
        self.assertIs(
            challenge["finding"]["mutant_violates_hidden_claim"],
            True,
        )
        self.assertIs(challenge["finding"]["weak_oracle_exposed"], True)
        self.assertIs(
            challenge["finding"]["primary_denominator_eligible"],
            False,
        )

    def test_challenge_is_deterministic_and_recomputed_digests_cannot_hide_drift(self) -> None:
        first = _run_arm("outcome-receipt-v1")
        second = _run_arm("outcome-receipt-v1")
        self.assertEqual(first["challenge"], second["challenge"])
        self.assertEqual(
            canonical_json(first["challenge"]),
            canonical_json(second["challenge"]),
        )

        for mutator, expected in (
            (
                lambda document: document["mutation"].__setitem__(
                    "mutant_id", "substituted-mutant"
                ),
                "mutant_id",
            ),
            (
                lambda document: document["controlled_executions"][2].__setitem__(
                    "observed", "fail"
                ),
                "controlled_executions",
            ),
            (
                lambda document: document["source"].__setitem__(
                    "witness_sha256", "f" * 64
                ),
                "witness_sha256",
            ),
            (
                lambda document: document["finding"].__setitem__(
                    "primary_denominator_eligible", True
                ),
                "primary_denominator_eligible",
            ),
        ):
            with self.subTest(expected=expected):
                tampered = deepcopy(first["challenge"])
                mutator(tampered)
                tampered["challenge_sha256"] = (
                    compute_weak_oracle_challenge_sha256(tampered)
                )
                tampered["report_sha256"] = compute_weak_oracle_report_sha256(
                    tampered
                )
                valid, errors = verify_weak_oracle_challenge_document(
                    tampered,
                    first["descriptor"],
                    first["identity"],
                    first["report"],
                    first["projection"],
                    first["declaration"],
                    first["localization"],
                )
                self.assertFalse(valid)
                self.assertTrue(any(expected in error for error in errors), errors)

    def test_public_challenge_excludes_raw_output_and_local_material(self) -> None:
        challenge = _run_arm("outcome-receipt-v1")["challenge"]
        encoded = json.dumps(challenge, sort_keys=True)
        for prohibited in (
            "/tmp/",
            "\\Temp\\",
            "Traceback (most recent call last)",
            '"stdout"',
            '"stderr"',
            "credential",
            "token_value",
            "environment_values",
            "private_endpoint",
        ):
            self.assertNotIn(prohibited, encoded)
        self.assertTrue(challenge["limitations"])


if __name__ == "__main__":
    unittest.main()
