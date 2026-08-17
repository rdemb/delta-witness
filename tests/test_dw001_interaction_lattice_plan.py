from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import unittest

from deltawitness.dw001_interaction_lattice_plan import (
    CANDIDATE_SOURCE,
    SELECTOR_TEST_SOURCE,
    build_anonymous_path_multiset,
    build_interaction_witness_lattice_plan,
    compute_interaction_lattice_plan_sha256,
    verify_interaction_witness_lattice_plan_document,
)
from deltawitness.reporting import load_report


_ROOT = Path(__file__).resolve().parents[1]
_PLAN_PATH = (
    _ROOT
    / "research"
    / "DW-001"
    / "interaction-witness-lattice-plan.v1.json"
)
_PRIOR_RESULT_PATH = (
    _ROOT
    / "research"
    / "DW-001"
    / "coveragepy-baseline-result.v1.json"
)
_PLAN_SHA256 = (
    "a79a500feb94c8ad78fe4633f9ca176465113de6297db2d07b2d005f5318e1f1"
)


class DW001InteractionLatticePlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = load_report(_PLAN_PATH)

    def _reseal(self, document: dict[str, object]) -> None:
        document["plan_sha256"] = compute_interaction_lattice_plan_sha256(
            document
        )

    def test_committed_plan_equals_exact_reconstruction(self) -> None:
        expected = build_interaction_witness_lattice_plan()
        self.assertEqual(self.plan, expected)
        self.assertEqual(self.plan["plan_sha256"], _PLAN_SHA256)
        self.assertEqual(
            compute_interaction_lattice_plan_sha256(self.plan),
            _PLAN_SHA256,
        )
        valid, errors = verify_interaction_witness_lattice_plan_document(
            self.plan
        )
        self.assertTrue(valid, errors)

    def test_source_test_target_and_prior_result_identities_are_exact(self) -> None:
        self.assertEqual(
            self.plan["source_scope"],
            {
                "source_id": "two-condition-authorization-candidate-v1",
                "path": "src/access.py",
                "symbol": "is_authorized",
                "language": "python",
                "source_sha256": (
                    "c0e8af980cdc0d304af77ec85222e36cf1d8a3b88bd1e18b0277699a086c0a7b"
                ),
                "ast_sha256": (
                    "67d1540a8c3b88e24ae8f3ea39ab27df2f8ef738545a709004394207636b83a3"
                ),
                "source_line_count": 12,
                "source_body_in_artifact": False,
            },
        )
        self.assertEqual(
            self.plan["test_scope"]["test_sha256"],
            "02d1069245ae05a76a128aada50affbbe04c83f40f06ce7f4e7f8dde5cdd4bdc",
        )
        self.assertEqual(
            self.plan["target_scope"]["target_id"],
            "6b20aa0ad5180288edffc9644e85252a774c2efb0c8ee9a32852b0d0ca50728e",
        )
        self.assertEqual(
            self.plan["target_scope"]["coverage_target_lines"],
            [2, 3, 4, 5, 7, 8, 9, 11, 12],
        )
        compile(CANDIDATE_SOURCE, "src/access.py", "exec")
        compile(SELECTOR_TEST_SOURCE, "tests/test_access.py", "exec")

        prior = load_report(_PRIOR_RESULT_PATH)
        self.assertEqual(
            prior["semantic_sha256"],
            self.plan["prior_evidence"][
                "coveragepy_result_semantic_sha256"
            ],
        )
        self.assertEqual(
            prior["report_sha256"],
            self.plan["prior_evidence"]["coveragepy_result_report_sha256"],
        )
        self.assertFalse(self.plan["prior_evidence"]["prior_source_reused"])
        self.assertFalse(
            self.plan["prior_evidence"]["prior_selectors_reused"]
        )
        self.assertFalse(self.plan["prior_evidence"]["prior_result_modified"])

    def test_truth_table_and_selector_identities_are_exact_and_unique(self) -> None:
        truth_table = self.plan["truth_table"]
        self.assertEqual(
            [item["quadrant_id"] for item in truth_table],
            ["TT", "TF", "FT", "FF"],
        )
        self.assertEqual(
            [item["expected_decision"] for item in truth_table],
            [True, False, False, False],
        )
        self.assertEqual(
            len({item["selector"] for item in truth_table}),
            4,
        )
        self.assertEqual(
            len({item["selector_id"] for item in truth_table}),
            4,
        )

    def test_profile_aggregate_hypotheses_are_independently_derived(self) -> None:
        path_by_quadrant = {
            item["quadrant_id"]: item
            for item in self.plan["structural_hypotheses"]["quadrant_paths"]
        }
        statement_signatures: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()
        arc_signatures: set[
            tuple[tuple[tuple[int, int], ...], tuple[tuple[int, int], ...]]
        ] = set()
        anonymous_signatures: set[str] = set()

        for profile in self.plan["profiles"]:
            statement_sets = [
                set(path_by_quadrant[quadrant]["expected_executed_statements"])
                for quadrant in profile["quadrants"]
            ]
            arc_sets = [
                {
                    tuple(arc)
                    for arc in path_by_quadrant[quadrant]["expected_arcs"]
                }
                for quadrant in profile["quadrants"]
            ]
            statement_union = sorted(set().union(*statement_sets))
            statement_intersection = sorted(set.intersection(*statement_sets))
            arc_union = sorted(set().union(*arc_sets))
            arc_intersection = sorted(set.intersection(*arc_sets))

            self.assertEqual(
                statement_union,
                profile["expected_statement_union"],
            )
            self.assertEqual(
                statement_intersection,
                profile["expected_statement_intersection"],
            )
            self.assertEqual(
                [list(arc) for arc in arc_union],
                profile["expected_arc_union"],
            )
            self.assertEqual(
                [list(arc) for arc in arc_intersection],
                profile["expected_arc_intersection"],
            )
            statement_signatures.add(
                (tuple(statement_union), tuple(statement_intersection))
            )
            arc_signatures.add((tuple(arc_union), tuple(arc_intersection)))
            anonymous_signatures.add(
                profile["expected_anonymous_path_multiset"][
                    "anonymous_path_multiset_sha256"
                ]
            )

        self.assertEqual(len(statement_signatures), 1)
        self.assertEqual(len(arc_signatures), 1)
        self.assertEqual(len(anonymous_signatures), 5)

        equal_cardinality = [
            profile
            for profile in self.plan["profiles"]
            if len(profile["quadrants"]) == 3
        ]
        self.assertEqual(len(equal_cardinality), 3)
        self.assertEqual(
            len(
                {
                    profile["expected_anonymous_path_multiset"][
                        "anonymous_path_multiset_sha256"
                    ]
                    for profile in equal_cardinality
                }
            ),
            3,
        )

    def test_independence_witnesses_are_truth_table_relations(self) -> None:
        expected = {
            "diagonal-only-v1": (False, False),
            "mfa-independence-v1": (True, False),
            "role-independence-v1": (False, True),
            "mcdc-basis-v1": (True, True),
            "full-truth-table-v1": (True, True),
        }
        for profile in self.plan["profiles"]:
            quadrants = set(profile["quadrants"])
            observed = (
                {"TT", "TF"}.issubset(quadrants),
                {"TT", "FT"}.issubset(quadrants),
            )
            self.assertEqual(observed, expected[profile["profile_id"]])
            self.assertEqual(
                observed,
                (
                    profile["expected_mfa_independence_witness"],
                    profile["expected_role_independence_witness"],
                ),
            )

    def test_anonymous_path_multiset_is_order_independent_and_counts_duplicates(self) -> None:
        left = "1" * 64
        right = "2" * 64
        first = build_anonymous_path_multiset([left, right, left])
        reordered = build_anonymous_path_multiset([left, left, right])
        replaced = build_anonymous_path_multiset([left, right, right])

        self.assertEqual(first, reordered)
        self.assertNotEqual(
            first["anonymous_path_multiset_sha256"],
            replaced["anonymous_path_multiset_sha256"],
        )
        self.assertEqual(
            first["records"],
            [
                {"path_shape_sha256": left, "count": 2},
                {"path_shape_sha256": right, "count": 1},
            ],
        )

    def test_plan_is_design_only_and_has_no_policy_escape_hatch(self) -> None:
        self.assertFalse(self.plan["execution_authorized"])
        self.assertFalse(self.plan["holdout_selected"])
        self.assertFalse(self.plan["primary_denominator_eligible"])
        self.assertEqual(
            self.plan["future_execution_contract"]["execution_status"],
            "not_implemented",
        )
        self.assertIsNone(
            self.plan["future_execution_contract"]["score"]
        )
        self.assertIsNone(self.plan["policy"]["quality_score"])
        self.assertFalse(self.plan["policy"]["merge_blocker_authorized"])
        self.assertFalse(
            self.plan["policy"]["scientific_novelty_claim_allowed"]
        )

    def test_importing_plan_does_not_import_coverage(self) -> None:
        code = (
            "import sys; "
            "import deltawitness.dw001_interaction_lattice_plan; "
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

    def test_recomputed_digest_cannot_hide_semantic_substitution(self) -> None:
        changes = (
            ("source_scope.source_sha256", "f" * 64),
            ("truth_table.1.expected_decision", True),
            ("profiles.1.quadrants", ["TT", "FT", "FF"]),
            (
                "structural_hypotheses.quadrant_paths.0.expected_arcs",
                [[-1, 2], [2, -1]],
            ),
            (
                "future_execution_contract.expected_mutation_matrix.0."
                "profile_outcomes.1.expected_outcome",
                "survived",
            ),
            ("policy.merge_blocker_authorized", True),
        )
        for dotted_path, replacement in changes:
            with self.subTest(field=dotted_path):
                tampered = deepcopy(self.plan)
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
                    verify_interaction_witness_lattice_plan_document(tampered)
                )
                self.assertFalse(valid)
                self.assertTrue(errors)

    def test_normative_array_reordering_and_extra_fields_fail_closed(self) -> None:
        reordered = deepcopy(self.plan)
        reordered["profiles"] = list(reversed(reordered["profiles"]))
        self._reseal(reordered)
        valid, errors = verify_interaction_witness_lattice_plan_document(
            reordered
        )
        self.assertFalse(valid)
        self.assertTrue(errors)

        extra = deepcopy(self.plan)
        extra["score"] = 1.0
        self._reseal(extra)
        valid, errors = verify_interaction_witness_lattice_plan_document(extra)
        self.assertFalse(valid)
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
