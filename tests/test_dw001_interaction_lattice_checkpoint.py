from __future__ import annotations

from copy import deepcopy
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from deltawitness.dw001_interaction_lattice_checkpoint import (
    CHECKPOINT_SHA256,
    RESULT_SEMANTIC_SHA256,
    build_interaction_lattice_result_checkpoint,
    compute_interaction_lattice_checkpoint_sha256,
    load_interaction_lattice_result_checkpoint,
    verify_interaction_lattice_result_checkpoint_document,
)
from deltawitness.reporting import canonical_json, load_report


_ROOT = Path(__file__).resolve().parents[1]
_DW001 = _ROOT / "research" / "DW-001"
_CHECKPOINT_PATH = (
    _DW001 / "interaction-witness-lattice-result-checkpoint.v1.json"
)
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


class DW001InteractionLatticeCheckpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.checkpoint = load_report(_CHECKPOINT_PATH)
        cls.protocol = load_report(_PROTOCOL_PATH)
        cls.plan = load_report(_PLAN_PATH)
        cls.catalog = load_report(_CATALOG_PATH)
        cls.prior_art = load_report(_PRIOR_ART_PATH)
        cls.coveragepy_manifest = load_report(_COVERAGEPY_MANIFEST_PATH)
        cls.pr46_result = load_report(_PR46_RESULT_PATH)

    def _verify(self, document: object) -> tuple[bool, tuple[str, ...]]:
        return verify_interaction_lattice_result_checkpoint_document(
            document,
            self.protocol,
            self.plan,
            self.catalog,
            self.prior_art,
            self.coveragepy_manifest,
            self.pr46_result,
        )

    def _reseal(self, document: dict[str, object]) -> None:
        document["checkpoint_sha256"] = (
            compute_interaction_lattice_checkpoint_sha256(document)
        )

    def test_committed_checkpoint_equals_independent_reconstruction(self) -> None:
        expected = build_interaction_lattice_result_checkpoint(
            self.plan,
            self.catalog,
        )
        self.assertEqual(self.checkpoint, expected)
        self.assertEqual(
            self.checkpoint["checkpoint_sha256"],
            CHECKPOINT_SHA256,
        )
        self.assertEqual(
            self.checkpoint["semantic_sha256"],
            RESULT_SEMANTIC_SHA256,
        )
        self.assertEqual(
            compute_interaction_lattice_checkpoint_sha256(self.checkpoint),
            CHECKPOINT_SHA256,
        )
        valid, errors = self._verify(self.checkpoint)
        self.assertTrue(valid, errors)

    def test_checkpoint_retains_complete_candidate_profile_and_mutant_tables(self) -> None:
        checkpoint = self.checkpoint
        self.assertEqual(len(checkpoint["candidate_selectors"]), 4)
        self.assertEqual(len(checkpoint["profiles"]), 5)
        self.assertEqual(len(checkpoint["mutants"]), 5)
        self.assertEqual(
            sum(
                len(mutant["selector_outcomes"])
                for mutant in checkpoint["mutants"]
            ),
            20,
        )
        self.assertEqual(
            sum(
                len(mutant["profile_outcomes"])
                for mutant in checkpoint["mutants"]
            ),
            25,
        )
        self.assertEqual(
            checkpoint["summary"]["selector_command_count"],
            24,
        )
        self.assertIsNone(checkpoint["summary"]["mutation_score"])

    def test_checkpoint_retains_equal_aggregates_and_distinct_path_multisets(self) -> None:
        invariants = self.checkpoint["profile_invariants"]
        self.assertEqual(
            invariants["statement_union"],
            [2, 3, 4, 5, 7, 8, 9, 11, 12],
        )
        self.assertEqual(
            invariants["statement_intersection"],
            [2, 3, 4, 8, 12],
        )
        self.assertEqual(
            invariants["arc_intersection"],
            [[-1, 2], [2, 3], [3, 4], [12, -1]],
        )
        path_digests = {
            profile["anonymous_path_multiset_sha256"]
            for profile in self.checkpoint["profiles"]
        }
        self.assertEqual(len(path_digests), 5)
        equal_cardinality = {
            profile["anonymous_path_multiset_sha256"]
            for profile in self.checkpoint["profiles"]
            if profile["selector_count"] == 3
        }
        self.assertEqual(len(equal_cardinality), 3)
        self.assertFalse(
            self.checkpoint["comparison"][
                "statement_aggregate_discriminates_profiles"
            ]
        )
        self.assertFalse(
            self.checkpoint["comparison"][
                "arc_aggregate_discriminates_profiles"
            ]
        )
        self.assertTrue(
            self.checkpoint["comparison"][
                "anonymous_path_multiset_discriminates_profiles"
            ]
        )

    def test_reference_report_is_explicitly_diagnostic_only(self) -> None:
        reference = self.checkpoint["reference_report"]
        self.assertTrue(reference["diagnostic_only"])
        self.assertEqual(reference["workflow_run_id"], 32063085079)
        self.assertEqual(reference["workflow_job_id"], 95488644926)
        self.assertEqual(
            reference["head_sha"],
            "050b11760c2c42da274ca20f86ce21d91f6d5b9e",
        )
        self.assertEqual(
            reference["report_sha256"],
            "f67aa03c024852297db256a70f270f1600f347a7d81e95a0a2337ec4efb79632",
        )
        for field in (
            "process_wall_seconds",
            "coverage_wall_seconds",
            "coverage_cpu_seconds",
        ):
            self.assertGreaterEqual(reference[field], 0.0)
            self.assertTrue(math.isfinite(reference[field]))

    def test_importing_checkpoint_verifier_does_not_import_coverage(self) -> None:
        code = (
            "import sys; "
            "import deltawitness.dw001_interaction_lattice_checkpoint; "
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

    def test_recomputed_digest_cannot_hide_semantic_or_policy_substitution(self) -> None:
        changes = (
            ("preregistration.merge_commit", "0" * 40),
            ("source.source_sha256", "f" * 64),
            ("candidate_selectors.0.observed", "fail"),
            ("candidate_selectors.0.executed_statements", [2]),
            ("profiles.1.anonymous_path_multiset_sha256", "f" * 64),
            ("mutants.0.selector_outcomes.1.observed", "pass"),
            ("mutants.0.profile_outcomes.1.outcome", "survived"),
            (
                "comparison.anonymous_path_multiset_discriminates_profiles",
                False,
            ),
            ("analysis.status", "unexpected"),
            ("policy.merge_blocker_authorized", True),
            ("semantic_sha256", "f" * 64),
            ("reference_report.diagnostic_only", False),
        )
        for dotted_path, replacement in changes:
            with self.subTest(field=dotted_path):
                tampered = deepcopy(self.checkpoint)
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

    def test_nonfinite_costs_reordering_extra_fields_duplicate_keys_and_symlinks_fail_closed(self) -> None:
        for value in (-1.0, math.nan, math.inf, -math.inf):
            with self.subTest(cost=value):
                tampered = deepcopy(self.checkpoint)
                tampered["reference_report"][
                    "process_wall_seconds"
                ] = value
                self._reseal(tampered)
                valid, errors = self._verify(tampered)
                self.assertFalse(valid)
                self.assertTrue(errors)

        reordered = deepcopy(self.checkpoint)
        reordered["profiles"] = list(reversed(reordered["profiles"]))
        self._reseal(reordered)
        valid, errors = self._verify(reordered)
        self.assertFalse(valid)
        self.assertTrue(errors)

        extra = deepcopy(self.checkpoint)
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
                load_interaction_lattice_result_checkpoint(
                    duplicate,
                    self.protocol,
                    self.plan,
                    self.catalog,
                    self.prior_art,
                    self.coveragepy_manifest,
                    self.pr46_result,
                )

            valid_path = root / "valid.json"
            valid_path.write_bytes(
                canonical_json(self.checkpoint) + b"\n"
            )
            linked = root / "linked.json"
            linked.symlink_to(valid_path)
            with self.assertRaisesRegex(
                Exception,
                "regular non-link",
            ):
                load_interaction_lattice_result_checkpoint(
                    linked,
                    self.protocol,
                    self.plan,
                    self.catalog,
                    self.prior_art,
                    self.coveragepy_manifest,
                    self.pr46_result,
                )


if __name__ == "__main__":
    unittest.main()
