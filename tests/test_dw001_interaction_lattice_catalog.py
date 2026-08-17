from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import unittest

import deltawitness.dw001_interaction_lattice_plan as interaction_plan
from deltawitness.dw001_interaction_lattice_plan import (
    build_interaction_witness_lattice_mutant_catalog,
    build_interaction_witness_lattice_plan,
    compute_interaction_lattice_catalog_sha256,
    compute_interaction_lattice_plan_sha256,
    verify_interaction_witness_lattice_mutant_catalog_document,
)
from deltawitness.reporting import load_report


_ROOT = Path(__file__).resolve().parents[1]
_PLAN_PATH = (
    _ROOT
    / "research"
    / "DW-001"
    / "interaction-witness-lattice-plan.v1.json"
)
_CATALOG_PATH = (
    _ROOT
    / "research"
    / "DW-001"
    / "interaction-witness-lattice-mutant-catalog.v1.json"
)
_CATALOG_SHA256 = (
    "2b06a86180a45fcd495c0bcf39365dde0cb590507e9a3528714f9ef58526308e"
)


class DW001InteractionLatticeCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = load_report(_PLAN_PATH)
        cls.catalog = load_report(_CATALOG_PATH)

    def _reseal(self, document: dict[str, object]) -> None:
        document["catalog_sha256"] = (
            compute_interaction_lattice_catalog_sha256(document)
        )

    def test_committed_catalog_equals_exact_regeneration(self) -> None:
        expected = build_interaction_witness_lattice_mutant_catalog(self.plan)
        self.assertEqual(self.catalog, expected)
        self.assertEqual(self.catalog["catalog_sha256"], _CATALOG_SHA256)
        valid, errors = (
            verify_interaction_witness_lattice_mutant_catalog_document(
                self.catalog,
                self.plan,
            )
        )
        self.assertTrue(valid, errors)

    def test_catalog_retains_complete_generation_table(self) -> None:
        self.assertEqual(
            self.catalog["summary"],
            {
                "total_records": 8,
                "generic_operator_records": 5,
                "generation_control_records": 3,
                "generated": 5,
                "duplicate": 1,
                "invalid": 1,
                "not_applicable": 1,
                "score": None,
            },
        )
        records = self.catalog["mutants"]
        self.assertEqual(
            [record["operator_id"] for record in records],
            [
                "drop-mfa-conjunct-v1",
                "drop-role-conjunct-v1",
                "or-gates-v1",
                "constant-false-v1",
                "constant-true-v1",
                "duplicate-false-control-v1",
                "not-applicable-addition-control-v1",
                "invalid-render-control-v1",
            ],
        )
        self.assertEqual(
            [record["status"] for record in records],
            [
                "generated",
                "generated",
                "generated",
                "generated",
                "generated",
                "duplicate",
                "not_applicable",
                "invalid",
            ],
        )
        self.assertEqual(
            records[5]["duplicate_of"],
            records[3]["mutant_id"],
        )
        self.assertEqual(
            records[5]["mutated_source_sha256"],
            records[3]["mutated_source_sha256"],
        )
        self.assertIsNone(records[6]["mutated_source_sha256"])
        self.assertIsNone(records[6]["compile_valid"])
        self.assertFalse(records[7]["compile_valid"])

    def test_generated_source_and_ast_identities_are_independently_rebuilt(self) -> None:
        by_operator = {
            record["operator_id"]: record
            for record in self.catalog["mutants"]
        }
        for operator_id in (
            "drop-mfa-conjunct-v1",
            "drop-role-conjunct-v1",
            "or-gates-v1",
            "constant-false-v1",
            "constant-true-v1",
        ):
            with self.subTest(operator=operator_id):
                status, source, ast_sha256, compile_valid, diagnostic = (
                    interaction_plan._mutated_source(operator_id)
                )
                record = by_operator[operator_id]
                self.assertEqual(status, "generated")
                self.assertTrue(compile_valid)
                self.assertEqual(diagnostic, "generated")
                self.assertIsNotNone(source)
                assert source is not None
                compile(source, "<interaction-mutant>", "exec")
                self.assertEqual(
                    interaction_plan._sha256_bytes(source.encode("utf-8")),
                    record["mutated_source_sha256"],
                )
                self.assertEqual(ast_sha256, record["mutated_ast_sha256"])

    def test_expected_mutant_matrix_is_derived_from_the_frozen_truth_table(self) -> None:
        truth = {
            item["quadrant_id"]: (
                bool(item["role_ok"]),
                bool(item["mfa_ok"]),
                bool(item["expected_decision"]),
            )
            for item in self.plan["truth_table"]
        }
        profile_quadrants = {
            profile["profile_id"]: profile["quadrants"]
            for profile in self.plan["profiles"]
        }
        mutant_values = {
            "drop-mfa-conjunct-v1": lambda role, mfa: role,
            "drop-role-conjunct-v1": lambda role, mfa: mfa,
            "or-gates-v1": lambda role, mfa: role or mfa,
            "constant-false-v1": lambda role, mfa: False,
            "constant-true-v1": lambda role, mfa: True,
        }
        observed: dict[str, dict[str, str]] = {}
        for operator_id, function in mutant_values.items():
            profile_outcomes: dict[str, str] = {}
            for profile_id, quadrants in profile_quadrants.items():
                killed = any(
                    function(truth[quadrant][0], truth[quadrant][1])
                    != truth[quadrant][2]
                    for quadrant in quadrants
                )
                profile_outcomes[profile_id] = (
                    "killed" if killed else "survived"
                )
            observed[operator_id] = profile_outcomes

        expected = {
            row["operator_id"]: {
                item["profile_id"]: item["expected_outcome"]
                for item in row["profile_outcomes"]
            }
            for row in self.plan["future_execution_contract"][
                "expected_mutation_matrix"
            ]
        }
        self.assertEqual(observed, expected)

    def test_catalog_contains_identities_not_execution_outcomes(self) -> None:
        forbidden = {
            "observed",
            "outcome",
            "killed",
            "survived",
            "concordant",
            "duration_seconds",
            "receipt_sha256",
        }
        for record in self.catalog["mutants"]:
            self.assertTrue(forbidden.isdisjoint(record))
            self.assertFalse(record["source_body_in_artifact"])
        self.assertFalse(self.catalog["source"]["source_body_in_artifact"])
        self.assertFalse(self.catalog["test"]["test_body_in_artifact"])

    def test_recomputed_digest_cannot_hide_catalog_substitution(self) -> None:
        changes = (
            ("source.source_sha256", "f" * 64),
            ("test.test_sha256", "f" * 64),
            ("target.target_id", "f" * 64),
            ("mutants.0.mutated_source_sha256", "f" * 64),
            ("mutants.5.duplicate_of", None),
            ("mutants.6.status", "generated"),
            ("summary.generated", 6),
            ("summary.score", 1.0),
        )
        for dotted_path, replacement in changes:
            with self.subTest(field=dotted_path):
                tampered = deepcopy(self.catalog)
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
                valid, errors = (
                    verify_interaction_witness_lattice_mutant_catalog_document(
                        tampered,
                        self.plan,
                    )
                )
                self.assertFalse(valid)
                self.assertTrue(errors)

    def test_mutant_reordering_extra_fields_and_plan_substitution_fail_closed(self) -> None:
        reordered = deepcopy(self.catalog)
        reordered["mutants"] = list(reversed(reordered["mutants"]))
        self._reseal(reordered)
        valid, errors = (
            verify_interaction_witness_lattice_mutant_catalog_document(
                reordered,
                self.plan,
            )
        )
        self.assertFalse(valid)
        self.assertTrue(errors)

        extra = deepcopy(self.catalog)
        extra["mutation_score"] = 1.0
        self._reseal(extra)
        valid, errors = (
            verify_interaction_witness_lattice_mutant_catalog_document(
                extra,
                self.plan,
            )
        )
        self.assertFalse(valid)
        self.assertTrue(errors)

        substituted_plan = build_interaction_witness_lattice_plan()
        substituted_plan["profiles"] = list(
            reversed(substituted_plan["profiles"])
        )
        substituted_plan["plan_sha256"] = (
            compute_interaction_lattice_plan_sha256(substituted_plan)
        )
        valid, errors = (
            verify_interaction_witness_lattice_mutant_catalog_document(
                self.catalog,
                substituted_plan,
            )
        )
        self.assertFalse(valid)
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
