from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import unittest

from deltawitness.dw001_interaction_lattice_prior_art import (
    PRIOR_ART_LOG_SHA256,
    build_interaction_witness_prior_art_log,
    compute_interaction_prior_art_log_sha256,
    verify_interaction_witness_prior_art_log_document,
)
from deltawitness.reporting import load_report


_ROOT = Path(__file__).resolve().parents[1]
_LOG_PATH = (
    _ROOT
    / "research"
    / "DW-001"
    / "interaction-witness-prior-art-log.v1.json"
)
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


class DW001InteractionLatticePriorArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.log = load_report(_LOG_PATH)
        cls.plan = load_report(_PLAN_PATH)
        cls.catalog = load_report(_CATALOG_PATH)

    def _reseal(self, document: dict[str, object]) -> None:
        document["log_sha256"] = (
            compute_interaction_prior_art_log_sha256(document)
        )

    def test_committed_log_equals_exact_reconstruction(self) -> None:
        expected = build_interaction_witness_prior_art_log()
        self.assertEqual(self.log, expected)
        self.assertEqual(self.log["log_sha256"], PRIOR_ART_LOG_SHA256)
        self.assertEqual(
            compute_interaction_prior_art_log_sha256(self.log),
            PRIOR_ART_LOG_SHA256,
        )
        valid, errors = verify_interaction_witness_prior_art_log_document(
            self.log
        )
        self.assertTrue(valid, errors)

    def test_log_binds_exact_plan_and_catalog_without_execution(self) -> None:
        self.assertEqual(
            self.log["plan_sha256"],
            self.plan["plan_sha256"],
        )
        self.assertEqual(
            self.log["catalog_sha256"],
            self.catalog["catalog_sha256"],
        )
        self.assertTrue(
            self.log["search_protocol"][
                "search_frozen_before_result_execution"
            ]
        )
        self.assertFalse(
            self.log["search_protocol"]["systematic_review_complete"]
        )
        self.assertFalse(self.log["policy"]["execution_authorized"])
        self.assertFalse(self.log["policy"]["holdout_selected"])
        self.assertFalse(
            self.log["policy"]["primary_denominator_eligible"]
        )

    def test_source_order_and_primary_identifiers_are_exact(self) -> None:
        self.assertEqual(
            [source["source_id"] for source in self.log["sources"]],
            [
                "coveragepy-7.15.2-measurement-contexts",
                "coveragepy-7.15.2-public-api",
                "nasa-tm-2001-210876",
                "nistir-7878",
                "kuhn-kacker-lei-2016",
                "schuler-zeller-checked-coverage",
                "schuler-zeller-equivalent-mutants",
                "jia-harman-mutation-survey",
                "barr-et-al-oracle-survey",
            ],
        )
        identifiers = {
            source["source_id"]: source["identifier"]
            for source in self.log["sources"]
        }
        self.assertEqual(
            identifiers["nasa-tm-2001-210876"],
            "NASA/TM-2001-210876",
        )
        self.assertEqual(
            identifiers["nistir-7878"],
            "10.6028/NIST.IR.7878",
        )
        self.assertEqual(
            identifiers["schuler-zeller-checked-coverage"],
            "10.1002/stvr.1497",
        )
        self.assertEqual(
            identifiers["schuler-zeller-equivalent-mutants"],
            "10.1002/stvr.1473",
        )
        self.assertEqual(
            identifiers["jia-harman-mutation-survey"],
            "10.1109/TSE.2010.62",
        )
        self.assertEqual(
            identifiers["barr-et-al-oracle-survey"],
            "10.1109/TSE.2014.2372785",
        )

    def test_closest_baselines_and_exact_difference_are_bounded(self) -> None:
        self.assertEqual(
            [
                baseline["baseline_id"]
                for baseline in self.log["closest_baselines"]
            ],
            [
                "coveragepy-static-context-lines-and-arcs",
                "two-condition-mcdc-independence-control",
                "combinatorial-input-coverage",
                "checked-coverage-dynamic-slice",
                "typed-fixed-mutation-incidence",
            ],
        )
        self.assertTrue(
            self.log["planned_difference"][
                "simpler_baseline_preferred_if_equivalent"
            ]
        )
        self.assertIn(
            "multiset",
            self.log["planned_difference"]["representation"],
        )
        self.assertIn(
            "union/intersection",
            self.log["planned_difference"]["information_loss_tested"],
        )

    def test_novelty_and_policy_claims_remain_disabled(self) -> None:
        novelty = self.log["novelty_boundary"]
        self.assertEqual(novelty["novelty_status"], "not_established")
        self.assertFalse(novelty["systematic_review_complete"])
        self.assertFalse(novelty["scientific_novelty_claim_allowed"])
        self.assertFalse(
            novelty["award_level_significance_claim_allowed"]
        )
        policy = self.log["policy"]
        self.assertIsNone(policy["quality_score"])
        self.assertIsNone(policy["universal_threshold"])
        self.assertFalse(policy["merge_blocker_authorized"])
        self.assertFalse(policy["ecological_inference_allowed"])
        self.assertFalse(policy["method_superiority_claim_allowed"])
        self.assertFalse(policy["production_readiness_claim_allowed"])

    def test_importing_prior_art_verifier_does_not_import_coverage(self) -> None:
        code = (
            "import sys; "
            "import deltawitness.dw001_interaction_lattice_prior_art; "
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

    def test_recomputed_digest_cannot_hide_source_baseline_or_claim_changes(self) -> None:
        changes = (
            ("plan_sha256", "f" * 64),
            ("sources.0.identifier", "https://example.invalid"),
            (
                "closest_baselines.0.planned_direct_comparison",
                "substituted comparison",
            ),
            (
                "planned_difference.simpler_baseline_preferred_if_equivalent",
                False,
            ),
            ("novelty_boundary.novelty_status", "established"),
            (
                "novelty_boundary.scientific_novelty_claim_allowed",
                True,
            ),
            ("policy.execution_authorized", True),
            ("policy.merge_blocker_authorized", True),
        )
        for dotted_path, replacement in changes:
            with self.subTest(field=dotted_path):
                tampered = deepcopy(self.log)
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
                    verify_interaction_witness_prior_art_log_document(tampered)
                )
                self.assertFalse(valid)
                self.assertTrue(errors)

    def test_source_reordering_and_extra_fields_fail_closed(self) -> None:
        reordered = deepcopy(self.log)
        reordered["sources"] = list(reversed(reordered["sources"]))
        self._reseal(reordered)
        valid, errors = verify_interaction_witness_prior_art_log_document(
            reordered
        )
        self.assertFalse(valid)
        self.assertTrue(errors)

        extra = deepcopy(self.log)
        extra["headline_score"] = 1.0
        self._reseal(extra)
        valid, errors = verify_interaction_witness_prior_art_log_document(extra)
        self.assertFalse(valid)
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
