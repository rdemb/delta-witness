from __future__ import annotations

from copy import deepcopy
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import deltawitness.dw001_interaction_lattice_result as lattice_result
from deltawitness.dw001_interaction_lattice_result import (
    CATALOG_SHA256,
    EXECUTION_PROTOCOL_SHA256,
    PLAN_SHA256,
    PRIOR_ART_LOG_SHA256,
    RESULT_ID,
    RESULT_SCHEMA_VERSION,
    compute_interaction_lattice_result_report_sha256,
    compute_interaction_lattice_result_semantic_sha256,
    load_interaction_witness_lattice_result,
    run_interaction_witness_lattice_result,
    verify_interaction_witness_lattice_result_document,
)
from deltawitness.reporting import canonical_json, load_report


_ROOT = Path(__file__).resolve().parents[2]
_DW001 = _ROOT / "research" / "DW-001"
_PROTOCOL_PATH = (
    _DW001 / "interaction-witness-lattice-execution-protocol.v1.json"
)
_PLAN_PATH = _DW001 / "interaction-witness-lattice-plan.v1.json"
_CATALOG_PATH = (
    _DW001 / "interaction-witness-lattice-mutant-catalog.v1.json"
)
_PRIOR_ART_PATH = _DW001 / "interaction-witness-prior-art-log.v1.json"
_COVERAGEPY_MANIFEST_PATH = (
    _DW001 / "coveragepy-7.15.2-artifact.v1.json"
)
_PR46_RESULT_PATH = _DW001 / "coveragepy-baseline-result.v1.json"
_PREREGISTRATION_MERGE_COMMIT = (
    "7eef6ffe296081449427ccf550a6bc75a91218c2"
)


class DW001InteractionLatticeResultContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.execution_protocol = load_report(_PROTOCOL_PATH)
        cls.plan = load_report(_PLAN_PATH)
        cls.catalog = load_report(_CATALOG_PATH)
        cls.prior_art = load_report(_PRIOR_ART_PATH)
        cls.coveragepy_manifest = load_report(_COVERAGEPY_MANIFEST_PATH)
        cls.pr46_result = load_report(_PR46_RESULT_PATH)
        cls._result_value: dict[str, object] | None = None
        cls._result_error: Exception | None = None
        try:
            cls._result_value = run_interaction_witness_lattice_result(
                cls.execution_protocol,
                cls.plan,
                cls.catalog,
                cls.prior_art,
                cls.coveragepy_manifest,
                cls.pr46_result,
            )
        except Exception as exc:  # preserved as independent red failures
            cls._result_error = exc

    def _result(self) -> dict[str, object]:
        if self._result_error is not None:
            self.fail(
                "interaction-witness lattice result contract is red: "
                f"{self._result_error}"
            )
        assert self._result_value is not None
        return deepcopy(self._result_value)

    def _verify(self, document: object) -> tuple[bool, tuple[str, ...]]:
        return verify_interaction_witness_lattice_result_document(
            document,
            self.execution_protocol,
            self.plan,
            self.catalog,
            self.prior_art,
            self.coveragepy_manifest,
            self.pr46_result,
        )

    def _reseal(self, document: dict[str, object]) -> None:
        document["semantic_sha256"] = (
            compute_interaction_lattice_result_semantic_sha256(document)
        )
        document["report_sha256"] = (
            compute_interaction_lattice_result_report_sha256(document)
        )

    def test_result_binds_exact_merged_preregistration_and_execution_protocol(self) -> None:
        result = self._result()
        self.assertEqual(result["schema_version"], RESULT_SCHEMA_VERSION)
        self.assertEqual(result["study_id"], "DW-001")
        self.assertEqual(result["result_id"], RESULT_ID)
        self.assertEqual(result["partition"], "development")
        self.assertEqual(
            result["preregistration_merge_commit"],
            _PREREGISTRATION_MERGE_COMMIT,
        )
        self.assertEqual(
            result["execution_protocol_sha256"],
            EXECUTION_PROTOCOL_SHA256,
        )
        self.assertEqual(result["plan_sha256"], PLAN_SHA256)
        self.assertEqual(result["catalog_sha256"], CATALOG_SHA256)
        self.assertEqual(
            result["prior_art_log_sha256"],
            PRIOR_ART_LOG_SHA256,
        )
        self.assertEqual(
            result["coveragepy_distribution_manifest_sha256"],
            self.coveragepy_manifest["manifest_sha256"],
        )
        self.assertEqual(
            result["pr46_result_semantic_sha256"],
            self.pr46_result["semantic_sha256"],
        )

    def test_every_candidate_selector_has_exact_typed_and_context_bound_evidence(self) -> None:
        result = self._result()
        selectors = result["candidate_selectors"]
        self.assertEqual(len(selectors), 4)
        self.assertEqual(
            [selector["quadrant_id"] for selector in selectors],
            ["TT", "TF", "FT", "FF"],
        )
        contexts: list[str] = []
        for selector in selectors:
            self.assertEqual(selector["expected_observed"], "pass")
            self.assertEqual(selector["observed"], "pass")
            self.assertTrue(selector["outcome_concordant"])
            self.assertEqual(selector["coverage_status"], "complete")
            self.assertIsNone(selector["coverage_error"])
            self.assertEqual(selector["receipt_counts"]["tests_run"], 1)
            self.assertEqual(selector["receipt_counts"]["passed"], 1)
            self.assertEqual(
                selector["coverage_receipt"]["measurement_status"],
                "complete",
            )
            contexts.append(selector["context_id"])
            self.assertEqual(
                selector["coverage_receipt"]["context_evidence"][
                    "measured_contexts"
                ],
                [selector["context_id"]],
            )
            self.assertTrue(
                selector["coverage_receipt"]["context_evidence"][
                    "partition_valid"
                ]
            )
            self.assertTrue(selector["concordant"])
        self.assertEqual(len(contexts), len(set(contexts)))

    def test_per_quadrant_statement_arc_branch_and_path_shapes_are_exact(self) -> None:
        result = self._result()
        expected_paths = {
            item["quadrant_id"]: item
            for item in self.plan["structural_hypotheses"]["quadrant_paths"]
        }
        for selector in result["candidate_selectors"]:
            expected = expected_paths[selector["quadrant_id"]]
            receipt = selector["coverage_receipt"]
            statement = receipt["statement_evidence"]
            branch = receipt["branch_evidence"]
            self.assertEqual(
                statement["executed"],
                expected["expected_executed_statements"],
            )
            self.assertEqual(
                statement["missing"],
                expected["expected_missing_statements"],
            )
            self.assertEqual(
                branch["context_arcs"],
                expected["expected_arcs"],
            )
            self.assertEqual(
                branch["branch_stats"],
                self.plan["structural_hypotheses"][
                    "expected_branch_stats_per_selector"
                ],
            )
            self.assertEqual(
                branch["missing_branch_count"],
                self.plan["structural_hypotheses"][
                    "expected_missing_branch_count_per_selector"
                ],
            )
            self.assertEqual(
                branch["missing_branch_arcs"],
                None,
            )
            self.assertEqual(
                branch["missing_branch_arc_identity_status"],
                "unavailable-public-api",
            )
            self.assertEqual(
                selector["path_shape"]["path_shape_sha256"],
                expected["expected_path_shape_sha256"],
            )
            self.assertTrue(selector["path_concordant"])

    def test_profile_aggregates_are_equal_while_anonymous_path_multisets_are_distinct(self) -> None:
        result = self._result()
        profiles = result["profiles"]
        self.assertEqual(len(profiles), 5)
        statement_signatures = set()
        arc_signatures = set()
        path_signatures = set()
        equal_cardinality_paths = set()
        for profile in profiles:
            self.assertEqual(profile["coverage_status"], "complete")
            self.assertTrue(profile["all_selectors_passed"])
            self.assertTrue(profile["context_partition_valid"])
            self.assertTrue(profile["aggregate_concordant"])
            statement_signatures.add(
                (
                    tuple(profile["statement_union"]),
                    tuple(profile["statement_intersection"]),
                )
            )
            arc_signatures.add(
                (
                    tuple(tuple(arc) for arc in profile["arc_union"]),
                    tuple(
                        tuple(arc) for arc in profile["arc_intersection"]
                    ),
                )
            )
            path_digest = profile["anonymous_path_multiset"][
                "anonymous_path_multiset_sha256"
            ]
            path_signatures.add(path_digest)
            self.assertEqual(
                profile["anonymous_path_multiset"][
                    "multiplicity_semantics"
                ],
                "multiset",
            )
            if profile["selector_count"] == 3:
                equal_cardinality_paths.add(path_digest)
        self.assertEqual(len(statement_signatures), 1)
        self.assertEqual(len(arc_signatures), 1)
        self.assertEqual(len(path_signatures), 5)
        self.assertEqual(len(equal_cardinality_paths), 3)

    def test_path_multiset_is_order_independent_but_preserves_multiplicity(self) -> None:
        result = self._result()
        profile = result["profiles"][1]
        records = profile["path_records"]
        rebuilt = lattice_result.build_anonymous_result_path_multiset(records)
        reordered = lattice_result.build_anonymous_result_path_multiset(
            list(reversed(records))
        )
        duplicated = lattice_result.build_anonymous_result_path_multiset(
            [*records, records[0]]
        )
        self.assertEqual(rebuilt, reordered)
        self.assertNotEqual(
            rebuilt["anonymous_path_multiset_sha256"],
            duplicated["anonymous_path_multiset_sha256"],
        )
        self.assertEqual(
            sum(item["count"] for item in rebuilt["records"]),
            len(records),
        )

    def test_condition_independence_relations_are_reconstructed_from_truth_table_membership(self) -> None:
        result = self._result()
        expected = {
            profile["profile_id"]: (
                profile["expected_mfa_independence_witness"],
                profile["expected_role_independence_witness"],
            )
            for profile in self.plan["profiles"]
        }
        for profile in result["profiles"]:
            observed = (
                profile["mfa_independence_witness"],
                profile["role_independence_witness"],
            )
            self.assertEqual(observed, expected[profile["profile_id"]])
            self.assertTrue(profile["independence_concordant"])

    def test_complete_candidate_and_mutant_tables_precede_summary_and_match_frozen_incidence(self) -> None:
        result = self._result()
        mutants = result["mutants"]
        self.assertEqual(len(mutants), 5)
        self.assertEqual(
            [mutant["mutant_id"] for mutant in mutants],
            self.execution_protocol["authorized_inputs"]["mutant_ids"],
        )
        expected_matrix = {
            row["operator_id"]: {
                item["profile_id"]: item["expected_outcome"]
                for item in row["profile_outcomes"]
            }
            for row in self.plan["future_execution_contract"][
                "expected_mutation_matrix"
            ]
        }
        for mutant in mutants:
            self.assertEqual(len(mutant["selectors"]), 4)
            self.assertTrue(mutant["selector_table_complete"])
            self.assertEqual(
                {
                    item["profile_id"]: item["outcome"]
                    for item in mutant["profile_outcomes"]
                },
                expected_matrix[mutant["operator_id"]],
            )
            self.assertTrue(mutant["concordant"])
        self.assertEqual(result["summary"]["mutant_count"], 5)
        self.assertEqual(result["summary"]["selector_command_count"], 24)
        self.assertIsNone(result["summary"]["mutation_score"])

    def test_comparison_relations_are_exact_and_separate_from_policy(self) -> None:
        result = self._result()
        self.assertEqual(
            result["comparison"],
            {
                "expected_statement_aggregate_discriminates_profiles": False,
                "statement_aggregate_discriminates_profiles": False,
                "expected_arc_aggregate_discriminates_profiles": False,
                "arc_aggregate_discriminates_profiles": False,
                "expected_anonymous_path_multiset_discriminates_profiles": True,
                "anonymous_path_multiset_discriminates_profiles": True,
                "expected_equal_cardinality_path_multisets_distinct": True,
                "equal_cardinality_path_multisets_distinct": True,
                "expected_mfa_independence_agrees_with_drop_mfa": True,
                "mfa_independence_agrees_with_drop_mfa": True,
                "expected_role_independence_agrees_with_drop_role": True,
                "role_independence_agrees_with_drop_role": True,
                "expected_any_independence_agrees_with_or_gates": True,
                "any_independence_agrees_with_or_gates": True,
                "concordant": True,
            },
        )
        self.assertEqual(result["analysis"]["status"], "expected")
        self.assertEqual(
            result["policy"],
            {
                "quality_score": None,
                "headline_score": None,
                "universal_threshold": None,
                "merge_blocker_authorized": False,
                "ecological_inference_allowed": False,
                "holdout_selected": False,
                "primary_denominator_eligible": False,
                "mcdc_certification_claim_allowed": False,
                "coverage_superiority_claim_allowed": False,
                "mutation_superiority_claim_allowed": False,
                "method_superiority_claim_allowed": False,
                "scientific_novelty_claim_allowed": False,
                "award_level_significance_claim_allowed": False,
                "production_readiness_claim_allowed": False,
            },
        )

    def test_complete_result_and_both_digests_verify(self) -> None:
        result = self._result()
        self.assertEqual(
            result["semantic_sha256"],
            compute_interaction_lattice_result_semantic_sha256(result),
        )
        self.assertEqual(
            result["report_sha256"],
            compute_interaction_lattice_result_report_sha256(result),
        )
        valid, errors = self._verify(result)
        self.assertTrue(valid, errors)

    def test_complete_preregistration_divergence_is_retained_as_unexpected(self) -> None:
        original = lattice_result._execute_candidate_selector
        injected = False

        def divergent_selector(**kwargs):
            nonlocal injected
            observation = original(**kwargs)
            if not injected:
                injected = True
                observation = deepcopy(observation)
                observation["coverage_receipt"]["statement_evidence"][
                    "executed"
                ] = [2]
                observation["coverage_receipt"]["statement_evidence"][
                    "measured_lines"
                ] = [2]
                observation["path_shape"]["statements"] = [2]
            return observation

        with patch.object(
            lattice_result,
            "_execute_candidate_selector",
            side_effect=divergent_selector,
            create=True,
        ):
            result = run_interaction_witness_lattice_result(
                self.execution_protocol,
                self.plan,
                self.catalog,
                self.prior_art,
                self.coveragepy_manifest,
                self.pr46_result,
            )
        self.assertTrue(injected)
        self.assertEqual(result["analysis"]["status"], "unexpected")
        valid, errors = self._verify(result)
        self.assertTrue(valid, errors)

    def test_tool_error_timeout_missing_dependency_and_context_ambiguity_are_indeterminate(self) -> None:
        for mode in (
            "tool_error",
            "timeout",
            "missing_optional_dependency",
            "context_ambiguity",
        ):
            with self.subTest(mode=mode):
                original = lattice_result._execute_candidate_selector
                injected = False

                def indeterminate_selector(**kwargs):
                    nonlocal injected
                    observation = original(**kwargs)
                    if not injected:
                        injected = True
                        observation = deepcopy(observation)
                        observation["coverage_status"] = "indeterminate"
                        observation["coverage_error"] = mode
                        observation["coverage_receipt"] = None
                    return observation

                with patch.object(
                    lattice_result,
                    "_execute_candidate_selector",
                    side_effect=indeterminate_selector,
                    create=True,
                ):
                    result = run_interaction_witness_lattice_result(
                        self.execution_protocol,
                        self.plan,
                        self.catalog,
                        self.prior_art,
                        self.coveragepy_manifest,
                        self.pr46_result,
                    )
                self.assertTrue(injected)
                self.assertEqual(
                    result["analysis"]["status"],
                    "indeterminate",
                )
                valid, errors = self._verify(result)
                self.assertTrue(valid, errors)

    def test_measured_empty_is_not_unavailable_and_semantic_substitution_fails_closed(self) -> None:
        result = self._result()
        unavailable = deepcopy(result)
        selector = unavailable["candidate_selectors"][0]
        selector["coverage_status"] = "indeterminate"
        selector["coverage_error"] = "missing_data"
        selector["coverage_receipt"] = {
            "measurement_status": "complete",
            "measurement_error": None,
            "statement_evidence": {
                "executable": [],
                "executed": [],
                "missing": [],
                "measured_lines": [],
            },
            "branch_evidence": {
                "all_arcs": [],
                "context_arcs": [],
            },
        }
        self._reseal(unavailable)
        valid, errors = self._verify(unavailable)
        self.assertFalse(valid)
        self.assertTrue(
            any(
                "indeterminate" in error or "unavailable" in error
                for error in errors
            ),
            errors,
        )

        changes = (
            ("source.source_sha256", "f" * 64),
            ("candidate_selectors.0.selector_id", "f" * 64),
            ("candidate_selectors.0.quadrant_id", "FF"),
            ("candidate_selectors.0.context_id", "substituted-context"),
            (
                "candidate_selectors.0.path_shape.path_shape_sha256",
                "f" * 64,
            ),
            ("mutants.0.mutant_id", "f" * 64),
            ("profiles.0.statement_union", []),
            (
                "comparison.anonymous_path_multiset_discriminates_profiles",
                False,
            ),
            ("policy.merge_blocker_authorized", True),
        )
        for dotted_path, replacement in changes:
            with self.subTest(field=dotted_path):
                tampered = self._result()
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

    def test_malformed_costs_wrong_types_reordering_extra_fields_duplicate_keys_and_symlinks_fail_closed(self) -> None:
        for value in (-1.0, math.nan, math.inf, -math.inf):
            with self.subTest(cost=value):
                tampered = self._result()
                tampered["cost"]["process_wall_seconds"] = value
                self._reseal(tampered)
                valid, errors = self._verify(tampered)
                self.assertFalse(valid)
                self.assertTrue(errors)

        wrong_type = self._result()
        wrong_type["policy"]["merge_blocker_authorized"] = 0
        self._reseal(wrong_type)
        valid, errors = self._verify(wrong_type)
        self.assertFalse(valid)
        self.assertTrue(errors)

        reordered = self._result()
        reordered["profiles"] = list(reversed(reordered["profiles"]))
        self._reseal(reordered)
        valid, errors = self._verify(reordered)
        self.assertFalse(valid)
        self.assertTrue(errors)

        extra = self._result()
        extra["score"] = 1.0
        self._reseal(extra)
        valid, errors = self._verify(extra)
        self.assertFalse(valid)
        self.assertTrue(errors)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            duplicate = root / "duplicate.json"
            duplicate.write_text(
                '{"schema_version":"x","schema_version":"y"}',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(Exception, "duplicate"):
                load_interaction_witness_lattice_result(
                    duplicate,
                    self.execution_protocol,
                    self.plan,
                    self.catalog,
                    self.prior_art,
                    self.coveragepy_manifest,
                    self.pr46_result,
                )

            valid_path = root / "valid.json"
            valid_path.write_bytes(canonical_json(self._result()) + b"\n")
            linked = root / "linked.json"
            linked.symlink_to(valid_path)
            with self.assertRaisesRegex(
                lattice_result.DW001InteractionLatticeResultError,
                "regular non-link",
            ):
                load_interaction_witness_lattice_result(
                    linked,
                    self.execution_protocol,
                    self.plan,
                    self.catalog,
                    self.prior_art,
                    self.coveragepy_manifest,
                    self.pr46_result,
                )


if __name__ == "__main__":
    unittest.main()
