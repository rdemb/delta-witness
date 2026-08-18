from __future__ import annotations

from pathlib import Path
import unittest

from deltawitness.dw001_interaction_lattice_checkpoint import (
    CHECKPOINT_SHA256,
    RESULT_SEMANTIC_SHA256,
    project_interaction_lattice_result_checkpoint,
    verify_interaction_lattice_result_checkpoint_document,
)
from deltawitness.dw001_interaction_lattice_result import (
    run_interaction_witness_lattice_result,
)
from deltawitness.reporting import load_report


_ROOT = Path(__file__).resolve().parents[2]
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


class DW001InteractionLatticeCheckpointProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.checkpoint = load_report(_CHECKPOINT_PATH)
        cls.protocol = load_report(_PROTOCOL_PATH)
        cls.plan = load_report(_PLAN_PATH)
        cls.catalog = load_report(_CATALOG_PATH)
        cls.prior_art = load_report(_PRIOR_ART_PATH)
        cls.coveragepy_manifest = load_report(_COVERAGEPY_MANIFEST_PATH)
        cls.pr46_result = load_report(_PR46_RESULT_PATH)
        cls.result = run_interaction_witness_lattice_result(
            cls.protocol,
            cls.plan,
            cls.catalog,
            cls.prior_art,
            cls.coveragepy_manifest,
            cls.pr46_result,
        )

    def test_live_verified_result_projects_exactly_to_committed_checkpoint(self) -> None:
        projected = project_interaction_lattice_result_checkpoint(
            self.result,
            self.protocol,
            self.plan,
            self.catalog,
            self.prior_art,
            self.coveragepy_manifest,
            self.pr46_result,
        )
        self.assertEqual(projected, self.checkpoint)
        self.assertEqual(projected["semantic_sha256"], RESULT_SEMANTIC_SHA256)
        self.assertEqual(projected["checkpoint_sha256"], CHECKPOINT_SHA256)
        valid, errors = verify_interaction_lattice_result_checkpoint_document(
            projected,
            self.protocol,
            self.plan,
            self.catalog,
            self.prior_art,
            self.coveragepy_manifest,
            self.pr46_result,
        )
        self.assertTrue(valid, errors)

    def test_checkpoint_omits_volatile_runtime_receipts_and_raw_outputs(self) -> None:
        forbidden = {
            "created_at",
            "runtime",
            "duration_seconds",
            "stdout_sha256",
            "stderr_sha256",
            "receipt_sha256",
            "coverage_receipt",
            "command",
            "context_id",
            "invocation_binding",
            "report_sha256",
        }

        def walk(value: object, *, path: str = "checkpoint") -> None:
            if isinstance(value, dict):
                for key, item in value.items():
                    if path != "checkpoint.reference_report":
                        self.assertNotIn(
                            key,
                            forbidden,
                            f"volatile field retained at {path}.{key}",
                        )
                    walk(item, path=f"{path}.{key}")
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    walk(item, path=f"{path}[{index}]")

        walk(self.checkpoint)
        self.assertIn(
            "report_sha256",
            self.checkpoint["reference_report"],
        )
        self.assertTrue(
            self.checkpoint["reference_report"]["diagnostic_only"]
        )


if __name__ == "__main__":
    unittest.main()
