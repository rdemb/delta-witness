from __future__ import annotations

from copy import deepcopy
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import deltawitness.dw001_coveragepy_baseline as coveragepy_baseline
from deltawitness.coveragepy_contract import (
    COVERAGEPY_MANIFEST_SHA256,
    COVERAGEPY_WHEEL_SHA256,
)
from deltawitness.coveragepy_probe import compute_coverage_receipt_sha256
from deltawitness.dw001_coveragepy_baseline import (
    ADAPTER_ID,
    MUTATION_RESULT_SEMANTIC_SHA256,
    RESULT_ID,
    RESULT_SCHEMA_VERSION,
    STDLIB_STATEMENT_RESULT_SEMANTIC_SHA256,
    compute_coveragepy_baseline_report_sha256,
    compute_coveragepy_baseline_semantic_sha256,
    load_claim_scoped_coveragepy_baseline,
    run_claim_scoped_coveragepy_baseline,
    verify_claim_scoped_coveragepy_baseline_document,
)
from deltawitness.dw001_mutation_results import run_claim_scoped_mutation_result
from deltawitness.dw001_statement_coverage import run_claim_scoped_statement_coverage
from deltawitness.reporting import canonical_json, load_report


_ROOT = Path(__file__).resolve().parents[2]
_PLAN_PATH = _ROOT / "research" / "DW-001" / "claim-scoped-mutation-plan.v1.json"
_CATALOG_PATH = _ROOT / "research" / "DW-001" / "claim-scoped-mutant-catalog.v1.json"


class DW001CoveragePyBaselineContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = load_report(_PLAN_PATH)
        cls.catalog = load_report(_CATALOG_PATH)
        cls.mutation_result = run_claim_scoped_mutation_result(
            cls.plan,
            cls.catalog,
        )
        cls.stdlib_result = run_claim_scoped_statement_coverage(
            cls.plan,
            cls.catalog,
            cls.mutation_result,
        )
        cls._result_value: dict[str, object] | None = None
        cls._result_error: Exception | None = None
        try:
            cls._result_value = run_claim_scoped_coveragepy_baseline(
                cls.plan,
                cls.catalog,
                cls.mutation_result,
                cls.stdlib_result,
            )
        except Exception as exc:  # retained as independent failures per test
            cls._result_error = exc

    def _result(self) -> dict[str, object]:
        if self._result_error is not None:
            self.fail(f"Coverage.py baseline contract is red: {self._result_error}")
        assert self._result_value is not None
        return deepcopy(self._result_value)

    def _reseal(self, document: dict[str, object]) -> None:
        document["semantic_sha256"] = (
            compute_coveragepy_baseline_semantic_sha256(document)
        )
        document["report_sha256"] = (
            compute_coveragepy_baseline_report_sha256(document)
        )

    def _verify(self, document: object) -> tuple[bool, tuple[str, ...]]:
        return verify_claim_scoped_coveragepy_baseline_document(
            document,
            self.plan,
            self.catalog,
            self.mutation_result,
            self.stdlib_result,
        )

    def test_result_binds_exact_frozen_inputs_distribution_and_configuration(self) -> None:
        result = self._result()
        self.assertEqual(result["schema_version"], RESULT_SCHEMA_VERSION)
        self.assertEqual(result["study_id"], "DW-001")
        self.assertEqual(result["result_id"], RESULT_ID)
        self.assertEqual(result["partition"], "development")
        self.assertEqual(result["adapter"]["id"], ADAPTER_ID)
        self.assertEqual(
            result["plan_sha256"],
            "0ebf64e1de76849050c86d8a4d53d72d8067561ab48b4bd5a4083495dc99fe37",
        )
        self.assertEqual(
            result["catalog_sha256"],
            "7b3e405bd3893f532c0ccfa16e9cc208422bbdd20dfe82a002c99342a04201c0",
        )
        self.assertEqual(
            result["mutation_result_semantic_sha256"],
            MUTATION_RESULT_SEMANTIC_SHA256,
        )
        self.assertEqual(
            result["stdlib_statement_result_semantic_sha256"],
            STDLIB_STATEMENT_RESULT_SEMANTIC_SHA256,
        )
        self.assertEqual(
            result["distribution_manifest_sha256"],
            COVERAGEPY_MANIFEST_SHA256,
        )
        self.assertEqual(
            result["distribution"]["selected_artifact"]["sha256"],
            COVERAGEPY_WHEEL_SHA256,
        )
        self.assertEqual(
            result["configuration"],
            {
                "data_file": None,
                "auto_data": False,
                "timid": True,
                "branch": True,
                "config_file": False,
                "source_dirs": ["src"],
                "concurrency": None,
                "check_preimported": False,
                "context_strategy": "static-selector-context-v1",
                "messages": False,
                "plugins": [],
                "auto_start": False,
                "subprocess_measurement": False,
                "network_during_measurement": False,
            },
        )
        self.assertEqual(
            result["source"],
            {
                "source_id": "authorization-predicate-candidate-v1",
                "path": "src/access.py",
                "symbol": "is_admin",
                "source_sha256": "7bfbd2d0a642c6d7f7da05ece2f4464d31df53a28d1ffed12c5752bc492d8965",
                "ast_sha256": "7c5be603e703a4893ead7ccc09fc76b88e3cd9d5603703d591d2ca80f439349b",
                "target_id": "3cdfc367a78a09b257147fb236e80785d936177da231924f43e2d3d5fbd80e2e",
                "target_lines": [2],
            },
        )

    def test_every_selector_passes_and_retains_exact_statement_evidence(self) -> None:
        result = self._result()
        selectors = [
            selector
            for profile in result["profiles"]
            for selector in profile["selectors"]
        ]
        self.assertEqual(len(selectors), 3)
        for selector in selectors:
            self.assertEqual(selector["expected_observed"], "pass")
            self.assertEqual(selector["observed"], "pass")
            self.assertTrue(selector["outcome_concordant"])
            self.assertEqual(selector["coverage_status"], "complete")
            self.assertIsNone(selector["coverage_error"])
            receipt = selector["coverage_receipt"]
            self.assertEqual(receipt["measurement_status"], "complete")
            self.assertEqual(
                receipt["statement_evidence"]["target_executable"],
                [2],
            )
            self.assertEqual(
                receipt["statement_evidence"]["target_executed"],
                [2],
            )
            self.assertEqual(
                receipt["statement_evidence"]["target_missing"],
                [],
            )
            self.assertTrue(selector["statement_concordant"])
            self.assertTrue(selector["concordant"])

    def test_arc_branch_and_context_evidence_is_exact_per_selector(self) -> None:
        result = self._result()
        contexts: list[str] = []
        for profile in result["profiles"]:
            for selector in profile["selectors"]:
                context_id = selector["context_id"]
                contexts.append(context_id)
                receipt = selector["coverage_receipt"]
                branch = receipt["branch_evidence"]
                context = receipt["context_evidence"]
                self.assertTrue(branch["has_arcs"])
                self.assertIsInstance(branch["all_arcs"], list)
                self.assertIsInstance(branch["target_arcs"], list)
                self.assertEqual(branch["missing_branch_arcs"], None)
                self.assertEqual(
                    branch["missing_branch_arc_identity_status"],
                    "unavailable-public-api",
                )
                self.assertEqual(context["measured_contexts"], [context_id])
                self.assertEqual(context["query_context"], context_id)
                self.assertEqual(context["arcs"], branch["context_arcs"])
                self.assertTrue(context["partition_valid"])
                for item in context["contexts_by_lineno"]:
                    self.assertEqual(item["contexts"], [context_id])
        self.assertEqual(len(contexts), len(set(contexts)))

    def test_profiles_are_derived_from_complete_selector_sets(self) -> None:
        result = self._result()
        self.assertEqual(
            [profile["profile_id"] for profile in result["profiles"]],
            [
                "strong-authorization-oracle-v1",
                "weak-boolean-proxy-v1",
            ],
        )
        for profile in result["profiles"]:
            selector_sets = [
                set(
                    selector["coverage_receipt"]["statement_evidence"][
                        "target_executed"
                    ]
                )
                for selector in profile["selectors"]
            ]
            expected_union = sorted(set().union(*selector_sets))
            expected_intersection = sorted(set.intersection(*selector_sets))
            self.assertEqual(profile["statement_union"], expected_union)
            self.assertEqual(
                profile["statement_intersection"],
                expected_intersection,
            )
            self.assertEqual(profile["statement_union"], [2])
            self.assertEqual(profile["statement_intersection"], [2])
            self.assertTrue(profile["all_selectors_passed"])
            self.assertTrue(profile["context_partition_valid"])
            self.assertEqual(profile["coverage_status"], "complete")
            self.assertTrue(profile["concordant"])

    def test_comparison_records_all_predeclared_relations_without_a_score(self) -> None:
        result = self._result()
        comparison = result["comparison"]
        self.assertEqual(
            comparison,
            {
                "expected_stdlib_statement_discriminates_profiles": False,
                "stdlib_statement_discriminates_profiles": False,
                "expected_coveragepy_statement_discriminates_profiles": False,
                "coveragepy_statement_discriminates_profiles": False,
                "expected_coveragepy_branch_discriminates_profiles": False,
                "coveragepy_branch_discriminates_profiles": False,
                "expected_mutation_discriminates_profiles": True,
                "mutation_discriminates_profiles": True,
                "expected_stdlib_and_coveragepy_statement_agree": True,
                "stdlib_and_coveragepy_statement_agree": True,
                "expected_coveragepy_branch_and_mutation_agree": False,
                "coveragepy_branch_and_mutation_agree": False,
                "expected_incremental_branch_signal_observed": False,
                "incremental_branch_signal_observed": False,
                "expected_incremental_mutation_signal_beyond_coveragepy_observed": True,
                "incremental_mutation_signal_beyond_coveragepy_observed": True,
                "concordant": True,
            },
        )
        self.assertEqual(result["analysis"]["status"], "expected")
        self.assertTrue(result["analysis"]["comparison_concordant"])
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
                "coverage_superiority_claim_allowed": False,
                "mutation_superiority_claim_allowed": False,
            },
        )

    def test_complete_result_and_both_digests_verify(self) -> None:
        result = self._result()
        self.assertEqual(
            result["semantic_sha256"],
            compute_coveragepy_baseline_semantic_sha256(result),
        )
        self.assertEqual(
            result["report_sha256"],
            compute_coveragepy_baseline_report_sha256(result),
        )
        valid, errors = self._verify(result)
        self.assertTrue(valid, errors)

    def test_recomputed_digests_cannot_hide_source_test_distribution_or_config_substitution(self) -> None:
        changes = (
            ("source.source_sha256", "f" * 64),
            ("profiles.0.selectors.0.test_sha256", "f" * 64),
            ("distribution.selected_artifact.sha256", "f" * 64),
            ("configuration.plugins", ["ambient.plugin"]),
            ("configuration.config_file", True),
            ("configuration.auto_start", True),
        )
        for dotted_path, value in changes:
            with self.subTest(field=dotted_path):
                tampered = self._result()
                current: object = tampered
                parts = dotted_path.split(".")
                for part in parts[:-1]:
                    if isinstance(current, list):
                        current = current[int(part)]
                    else:
                        current = current[part]
                if isinstance(current, list):
                    current[int(parts[-1])] = value
                else:
                    current[parts[-1]] = value
                self._reseal(tampered)
                valid, errors = self._verify(tampered)
                self.assertFalse(valid)
                self.assertTrue(errors)

    def test_context_swap_cross_contamination_and_producer_substitution_are_rejected(self) -> None:
        swapped = self._result()
        first = swapped["profiles"][0]["selectors"][0]
        second = swapped["profiles"][0]["selectors"][1]
        first["context_id"], second["context_id"] = (
            second["context_id"],
            first["context_id"],
        )
        self._reseal(swapped)
        valid, errors = self._verify(swapped)
        self.assertFalse(valid)
        self.assertTrue(any("context" in error for error in errors), errors)

        contaminated = self._result()
        receipt = contaminated["profiles"][0]["selectors"][0][
            "coverage_receipt"
        ]
        receipt["context_evidence"]["measured_contexts"].append(
            "ambient-context"
        )
        receipt["context_evidence"]["partition_valid"] = False
        receipt["coverage_sha256"] = compute_coverage_receipt_sha256(receipt)
        self._reseal(contaminated)
        valid, errors = self._verify(contaminated)
        self.assertFalse(valid)
        self.assertTrue(any("context" in error for error in errors), errors)

        producer = self._result()
        receipt = producer["profiles"][0]["selectors"][0][
            "coverage_receipt"
        ]
        receipt["producer"]["name"] = "substituted-producer"
        receipt["coverage_sha256"] = compute_coverage_receipt_sha256(receipt)
        self._reseal(producer)
        valid, errors = self._verify(producer)
        self.assertFalse(valid)
        self.assertTrue(any("producer" in error for error in errors), errors)

    def test_changed_statement_arc_aggregate_and_comparison_relations_are_rejected(self) -> None:
        statement = self._result()
        receipt = statement["profiles"][0]["selectors"][0][
            "coverage_receipt"
        ]
        receipt["statement_evidence"]["target_executed"] = []
        receipt["coverage_sha256"] = compute_coverage_receipt_sha256(receipt)
        self._reseal(statement)
        valid, errors = self._verify(statement)
        self.assertFalse(valid)
        self.assertTrue(errors)

        arcs = self._result()
        receipt = arcs["profiles"][0]["selectors"][0]["coverage_receipt"]
        receipt["branch_evidence"]["target_arcs"] = []
        receipt["coverage_sha256"] = compute_coverage_receipt_sha256(receipt)
        self._reseal(arcs)
        valid, errors = self._verify(arcs)
        self.assertFalse(valid)
        self.assertTrue(errors)

        aggregate = self._result()
        aggregate["profiles"][0]["statement_union"] = []
        self._reseal(aggregate)
        valid, errors = self._verify(aggregate)
        self.assertFalse(valid)
        self.assertTrue(errors)

        comparison = self._result()
        comparison["comparison"][
            "coveragepy_branch_discriminates_profiles"
        ] = True
        comparison["comparison"]["concordant"] = False
        self._reseal(comparison)
        valid, errors = self._verify(comparison)
        self.assertFalse(valid)
        self.assertTrue(errors)

    def test_missing_measurement_cannot_be_substituted_with_empty_sets(self) -> None:
        tampered = self._result()
        selector = tampered["profiles"][0]["selectors"][0]
        selector["coverage_status"] = "indeterminate"
        selector["coverage_error"] = "missing_coverage_receipt"
        receipt = selector["coverage_receipt"]
        receipt["measurement_status"] = "indeterminate"
        receipt["measurement_error"] = "missing_data"
        receipt["measured_files"] = []
        receipt["statement_evidence"] = {
            "executable": [],
            "executed": [],
            "missing": [],
            "measured_lines": [],
            "target_executable": [],
            "target_executed": [],
            "target_missing": [],
        }
        receipt["branch_evidence"] = {
            "has_arcs": True,
            "all_arcs": [],
            "context_arcs": [],
            "target_arcs": [],
            "branch_stats": [],
            "target_branch_stats": [],
            "missing_branch_count": 0,
            "target_missing_branch_count": 0,
            "missing_branch_arcs": None,
            "missing_branch_arc_identity_status": "unavailable-public-api",
        }
        receipt["context_evidence"] = {
            "measured_contexts": [],
            "contexts_by_lineno": [],
            "query_context": selector["context_id"],
            "lines": [],
            "arcs": [],
            "partition_valid": False,
        }
        receipt["coverage_sha256"] = compute_coverage_receipt_sha256(receipt)
        self._reseal(tampered)
        valid, errors = self._verify(tampered)
        self.assertFalse(valid)
        self.assertTrue(any("indeterminate" in error for error in errors), errors)

    def test_unexpected_complete_statement_result_is_retained(self) -> None:
        original = coveragepy_baseline._execute_selector
        injected = False

        def divergent_selector(**kwargs):
            nonlocal injected
            observation = original(**kwargs)
            if not injected:
                injected = True
                observation = deepcopy(observation)
                receipt = observation["coverage_receipt"]
                statements = receipt["statement_evidence"]
                statements["executed"] = [1]
                statements["missing"] = [2]
                statements["measured_lines"] = [1]
                statements["target_executed"] = []
                statements["target_missing"] = [2]
                context = receipt["context_evidence"]
                context["contexts_by_lineno"] = [
                    {
                        "line": 1,
                        "contexts": [observation["context_id"]],
                    }
                ]
                context["lines"] = [1]
                receipt["coverage_sha256"] = (
                    compute_coverage_receipt_sha256(receipt)
                )
            return observation

        with patch.object(
            coveragepy_baseline,
            "_execute_selector",
            side_effect=divergent_selector,
            create=True,
        ):
            result = run_claim_scoped_coveragepy_baseline(
                self.plan,
                self.catalog,
                self.mutation_result,
                self.stdlib_result,
            )
        self.assertTrue(injected)
        self.assertEqual(result["analysis"]["status"], "unexpected")
        valid, errors = self._verify(result)
        self.assertTrue(valid, errors)

    def test_tool_error_timeout_and_context_ambiguity_are_indeterminate(self) -> None:
        original = coveragepy_baseline._execute_selector
        modes = (
            "tool_error",
            "timeout",
            "context_ambiguity",
        )
        for mode in modes:
            with self.subTest(mode=mode):
                injected = False

                def indeterminate_selector(**kwargs):
                    nonlocal injected
                    observation = original(**kwargs)
                    if not injected:
                        injected = True
                        observation = deepcopy(observation)
                        if mode == "timeout":
                            observation["observed"] = "timeout"
                            observation["return_code"] = None
                            observation["timed_out"] = True
                            observation["receipt_sha256"] = None
                            observation["receipt_outcome"] = None
                            observation["receipt_producer"] = None
                            observation["receipt_counts"] = None
                            observation["observation_error"] = None
                            observation["coverage_receipt"] = None
                            observation["coverage_error"] = "timeout"
                        else:
                            receipt = observation["coverage_receipt"]
                            receipt["measurement_status"] = "indeterminate"
                            receipt["measurement_error"] = mode
                            receipt["measured_files"] = None
                            receipt["statement_evidence"] = None
                            receipt["branch_evidence"] = None
                            receipt["context_evidence"] = None
                            receipt["coverage_sha256"] = (
                                compute_coverage_receipt_sha256(receipt)
                            )
                            observation["coverage_error"] = mode
                    return observation

                with patch.object(
                    coveragepy_baseline,
                    "_execute_selector",
                    side_effect=indeterminate_selector,
                    create=True,
                ):
                    result = run_claim_scoped_coveragepy_baseline(
                        self.plan,
                        self.catalog,
                        self.mutation_result,
                        self.stdlib_result,
                    )
                self.assertTrue(injected)
                self.assertEqual(result["analysis"]["status"], "indeterminate")
                valid, errors = self._verify(result)
                self.assertTrue(valid, errors)

    def test_malformed_costs_wrong_types_reordering_and_extra_fields_are_rejected(self) -> None:
        for value in (-1.0, math.nan, math.inf, -math.inf):
            with self.subTest(cost=value):
                tampered = self._result()
                tampered["profiles"][0]["selectors"][0]["cost"][
                    "process_wall_seconds"
                ] = value
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

    def test_loader_rejects_duplicate_json_keys_and_symbolic_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            duplicate = root / "duplicate.json"
            duplicate.write_text(
                '{"schema_version":"x","schema_version":"y"}',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(Exception, "duplicate"):
                load_claim_scoped_coveragepy_baseline(
                    duplicate,
                    self.plan,
                    self.catalog,
                    self.mutation_result,
                    self.stdlib_result,
                )

            valid_path = root / "valid.json"
            valid_path.write_bytes(canonical_json(self._result()) + b"\n")
            linked = root / "linked.json"
            linked.symlink_to(valid_path)
            with self.assertRaisesRegex(
                coveragepy_baseline.DW001CoveragePyBaselineError,
                "regular non-link",
            ):
                load_claim_scoped_coveragepy_baseline(
                    linked,
                    self.plan,
                    self.catalog,
                    self.mutation_result,
                    self.stdlib_result,
                )


if __name__ == "__main__":
    unittest.main()
