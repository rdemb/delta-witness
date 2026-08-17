from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import unittest

from deltawitness.dw001_interaction_lattice_execution import (
    EXECUTION_PROTOCOL_SHA256,
    PREREGISTRATION_MERGE_COMMIT,
    build_interaction_lattice_execution_protocol,
    compute_interaction_lattice_execution_protocol_sha256,
    verify_interaction_lattice_execution_protocol_document,
)
from deltawitness.reporting import load_report


_ROOT = Path(__file__).resolve().parents[1]
_DW001 = _ROOT / "research" / "DW-001"
_PROTOCOL_PATH = (
    _DW001 / "interaction-witness-lattice-execution-protocol.v1.json"
)
_SCHEMA_PATH = (
    _DW001
    / "schema"
    / "interaction-witness-lattice-execution-protocol.schema.json"
)
_PLAN_PATH = _DW001 / "interaction-witness-lattice-plan.v1.json"
_CATALOG_PATH = (
    _DW001 / "interaction-witness-lattice-mutant-catalog.v1.json"
)
_PRIOR_ART_PATH = (
    _DW001 / "interaction-witness-prior-art-log.v1.json"
)
_COVERAGEPY_MANIFEST_PATH = (
    _DW001 / "coveragepy-7.15.2-artifact.v1.json"
)
_PR46_RESULT_PATH = _DW001 / "coveragepy-baseline-result.v1.json"


class DW001InteractionLatticeExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.protocol = load_report(_PROTOCOL_PATH)
        cls.schema = load_report(_SCHEMA_PATH)
        cls.plan = load_report(_PLAN_PATH)
        cls.catalog = load_report(_CATALOG_PATH)
        cls.prior_art = load_report(_PRIOR_ART_PATH)
        cls.coveragepy_manifest = load_report(_COVERAGEPY_MANIFEST_PATH)
        cls.pr46_result = load_report(_PR46_RESULT_PATH)

    def _verify(self, document: object) -> tuple[bool, tuple[str, ...]]:
        return verify_interaction_lattice_execution_protocol_document(
            document,
            self.plan,
            self.catalog,
            self.prior_art,
            self.coveragepy_manifest,
            self.pr46_result,
        )

    def _reseal(self, document: dict[str, object]) -> None:
        document["protocol_sha256"] = (
            compute_interaction_lattice_execution_protocol_sha256(document)
        )

    def test_committed_protocol_equals_exact_reconstruction(self) -> None:
        expected = build_interaction_lattice_execution_protocol()
        self.assertEqual(self.protocol, expected)
        self.assertEqual(
            self.protocol["protocol_sha256"],
            EXECUTION_PROTOCOL_SHA256,
        )
        self.assertEqual(
            compute_interaction_lattice_execution_protocol_sha256(
                self.protocol
            ),
            EXECUTION_PROTOCOL_SHA256,
        )
        valid, errors = self._verify(self.protocol)
        self.assertTrue(valid, errors)

    def test_authorization_is_separate_from_the_immutable_preregistration(self) -> None:
        self.assertEqual(
            self.protocol["preregistration"]["merge_commit"],
            PREREGISTRATION_MERGE_COMMIT,
        )
        self.assertFalse(self.plan["execution_authorized"])
        self.assertEqual(
            self.plan["future_execution_contract"]["execution_status"],
            "not_implemented",
        )
        self.assertTrue(
            self.protocol["execution_scope"][
                "fixed_project_owned_synthetic_execution_authorized"
            ]
        )
        self.assertEqual(
            self.protocol["status"],
            "pre_result_execution_authorization",
        )

    def test_execution_scope_is_exactly_twenty_four_shell_free_children(self) -> None:
        scope = self.protocol["execution_scope"]
        self.assertEqual(scope["candidate_selector_commands"], 4)
        self.assertEqual(scope["mutant_selector_commands"], 20)
        self.assertEqual(scope["maximum_selector_commands"], 24)
        self.assertTrue(scope["one_selector_per_child_process"])
        self.assertFalse(scope["shell_allowed"])
        self.assertTrue(scope["disposable_nonsensitive_directories_required"])
        self.assertTrue(scope["reduced_environment_required"])
        self.assertFalse(scope["runner_is_sandbox"])
        self.assertEqual(
            scope["supported_python_versions"],
            ["3.11", "3.12", "3.13", "3.14"],
        )

    def test_only_exact_source_selectors_profiles_operators_and_mutants_are_authorized(self) -> None:
        inputs = self.protocol["authorized_inputs"]
        self.assertEqual(inputs["source_sha256"], self.plan["source_scope"]["source_sha256"])
        self.assertEqual(inputs["test_sha256"], self.plan["test_scope"]["test_sha256"])
        self.assertEqual(inputs["target_id"], self.plan["target_scope"]["target_id"])
        self.assertEqual(
            inputs["profile_ids"],
            [profile["profile_id"] for profile in self.plan["profiles"]],
        )
        self.assertEqual(
            inputs["selector_ids"],
            [item["selector_id"] for item in self.plan["truth_table"]],
        )
        self.assertEqual(
            inputs["operator_ids"],
            [
                item["operator_id"]
                for item in self.plan["operator_set"]["operators"]
            ],
        )
        self.assertEqual(
            inputs["mutant_ids"],
            [
                item["mutant_id"]
                for item in self.catalog["mutants"]
                if item["catalog_role"] == "generic_operator"
            ],
        )

    def test_coveragepy_configuration_and_all_prohibited_capabilities_are_fixed(self) -> None:
        coverage = self.protocol["coveragepy_contract"]
        self.assertEqual(coverage["package"], "coverage")
        self.assertEqual(coverage["version"], "7.15.2")
        self.assertIsNone(coverage["data_file"])
        self.assertFalse(coverage["auto_data"])
        self.assertTrue(coverage["timid"])
        self.assertTrue(coverage["branch"])
        self.assertFalse(coverage["config_file"])
        self.assertIsNone(coverage["concurrency"])
        self.assertFalse(coverage["check_preimported"])
        self.assertEqual(coverage["plugins"], [])
        self.assertFalse(coverage["auto_start"])
        self.assertFalse(coverage["subprocess_measurement"])
        self.assertFalse(coverage["network_during_measurement"])
        self.assertFalse(coverage["raw_coverage_data_publication_allowed"])

        self.assertTrue(
            all(
                value is False
                for value in self.protocol["prohibited_capabilities"].values()
            )
        )

    def test_result_and_policy_boundaries_are_exact(self) -> None:
        contract = self.protocol["result_contract"]
        self.assertTrue(contract["candidate_and_mutant_tables_before_summary"])
        self.assertEqual(contract["complete_divergence_status"], "unexpected")
        self.assertEqual(contract["missing_or_ambiguous_status"], "indeterminate")
        self.assertTrue(contract["measured_empty_distinct_from_unavailable"])
        self.assertEqual(contract["anonymous_path_multiplicity"], "multiset")
        self.assertFalse(contract["hit_count_magnitude_used"])
        self.assertTrue(contract["independent_semantic_reconstruction_required"])

        policy = self.protocol["policy"]
        self.assertIsNone(policy["quality_score"])
        self.assertIsNone(policy["headline_score"])
        self.assertIsNone(policy["universal_threshold"])
        self.assertTrue(
            all(
                value is False
                for key, value in policy.items()
                if key
                not in {
                    "quality_score",
                    "headline_score",
                    "universal_threshold",
                }
            )
        )

    def test_schema_is_closed_and_covers_exact_protocol_fields(self) -> None:
        self.assertEqual(
            self.schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )
        self.assertEqual(self.schema["type"], "object")
        self.assertFalse(self.schema["additionalProperties"])
        self.assertEqual(set(self.schema["required"]), set(self.protocol))
        self.assertEqual(set(self.schema["properties"]), set(self.protocol))
        for name in (
            "preregistration",
            "authorizedInputs",
            "executionScope",
            "coveragepyContract",
            "prohibitedCapabilities",
            "resultContract",
            "policy",
        ):
            definition = self.schema["$defs"][name]
            self.assertEqual(definition["type"], "object")
            self.assertFalse(definition["additionalProperties"])
            self.assertTrue(definition["required"])

    def test_importing_protocol_does_not_import_coverage(self) -> None:
        code = (
            "import sys; "
            "import deltawitness.dw001_interaction_lattice_execution; "
            "raise SystemExit(1 if 'coverage' in sys.modules else 0)"
        )
        completed = subprocess.run(
            [sys.executable, "-c", code],
            cwd=_ROOT,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            completed.stderr.decode("utf-8", errors="replace"),
        )

    def test_recomputed_digest_cannot_hide_authorization_or_identity_substitution(self) -> None:
        changes = (
            ("preregistration.merge_commit", "0" * 40),
            ("authorized_inputs.source_sha256", "f" * 64),
            ("authorized_inputs.selector_ids.0", "f" * 64),
            ("authorized_inputs.mutant_ids.0", "f" * 64),
            ("execution_scope.maximum_selector_commands", 25),
            ("execution_scope.shell_allowed", True),
            ("coveragepy_contract.plugins", ["ambient.plugin"]),
            ("coveragepy_contract.network_during_measurement", True),
            ("prohibited_capabilities.external_repository_execution", True),
            ("result_contract.hit_count_magnitude_used", True),
            ("policy.merge_blocker_authorized", True),
            ("policy.scientific_novelty_claim_allowed", True),
        )
        for dotted_path, replacement in changes:
            with self.subTest(field=dotted_path):
                tampered = deepcopy(self.protocol)
                current: object = tampered
                parts = dotted_path.split(".")
                for part in parts[:-1]:
                    current = (
                        current[int(part)]
                        if isinstance(current, list)
                        else current[part]
                    )
                if isinstance(current, list):
                    current[int(parts[-1])] = replacement
                else:
                    current[parts[-1]] = replacement
                self._reseal(tampered)
                valid, errors = self._verify(tampered)
                self.assertFalse(valid)
                self.assertTrue(errors)

    def test_normative_array_reordering_and_extra_fields_fail_closed(self) -> None:
        reordered = deepcopy(self.protocol)
        reordered["authorized_inputs"]["profile_ids"] = list(
            reversed(reordered["authorized_inputs"]["profile_ids"])
        )
        self._reseal(reordered)
        valid, errors = self._verify(reordered)
        self.assertFalse(valid)
        self.assertTrue(errors)

        extra = deepcopy(self.protocol)
        extra["execution_score"] = 1.0
        self._reseal(extra)
        valid, errors = self._verify(extra)
        self.assertFalse(valid)
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
