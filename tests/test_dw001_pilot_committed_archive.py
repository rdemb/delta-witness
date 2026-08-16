from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from deltawitness.dw001_pilot import (
    materialize_development_pilot_archive,
    verify_development_pilot_archive_document,
    verify_development_pilot_bundle,
)
from deltawitness.reporting import load_report


_ROOT = Path(__file__).resolve().parents[1] / "research" / "DW-001"
_PLAN_PATH = _ROOT / "development-pilot-plan.v1.json"
_ARCHIVE_PATH = _ROOT / "development-pilot-archive.v1.json"

_PLAN_SHA256 = "48a98f01c740862c91056841a7f96e6c98f1ae9641b7b364590a45d458ae3bcc"
_ARCHIVE_SHA256 = "3b992d67281693143a4e7bea920d1829f9b675eda592993db0e234239fcf4b06"
_SEMANTIC_SHA256 = "bd3c40d62e3d5695271db06f3bec476b4b9cd94442fd7171e1a03c70a74db5ef"
_EXPECTED_CONTRASTS = [
    "candidate-test-discrimination",
    "original-test-preservation",
    "typed-import-error",
    "declared-witness-mismatch",
    "valid-positive-control",
]


class DW001CommittedDevelopmentPilotArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = load_report(_PLAN_PATH)
        cls.archive = load_report(_ARCHIVE_PATH)

    def test_committed_archive_matches_exact_plan_and_digests(self) -> None:
        self.assertEqual(self.plan["plan_sha256"], _PLAN_SHA256)
        self.assertEqual(self.archive["plan_sha256"], _PLAN_SHA256)
        self.assertEqual(self.archive["archive_sha256"], _ARCHIVE_SHA256)
        self.assertEqual(
            self.archive["index_semantic_sha256"],
            _SEMANTIC_SHA256,
        )
        self.assertEqual(self.archive["partition"], "development")

        valid, errors = verify_development_pilot_archive_document(
            self.archive,
            self.plan,
        )
        self.assertTrue(valid, errors)

    def test_committed_archive_reconstructs_complete_verified_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "bundle"
            materialize_development_pilot_archive(
                self.archive,
                output,
                self.plan,
            )
            valid, errors = verify_development_pilot_bundle(output, self.plan)
            self.assertTrue(valid, errors)
            index = load_report(output / "index.json")

        self.assertTrue(index["complete"])
        self.assertEqual(index["semantic_sha256"], _SEMANTIC_SHA256)
        self.assertEqual(len(index["cases"]), 10)
        self.assertEqual(
            [case["order"] for case in index["cases"]],
            list(range(1, 11)),
        )
        self.assertEqual(
            [item["contrast_id"] for item in index["analysis"]["contrasts"]],
            _EXPECTED_CONTRASTS,
        )
        self.assertTrue(
            all(
                item["status"] == "observed_as_expected"
                for item in index["analysis"]["contrasts"]
            )
        )
        self.assertIsNone(index["analysis"]["headline_score"])
        self.assertFalse(index["analysis"]["ecological_inference_allowed"])
        self.assertTrue(index["analysis"]["retain_case_tables"])
        self.assertTrue(
            all(
                method["primary_denominator_eligible"] is False
                for case in index["cases"]
                for method in case["methods"]
            )
        )

    def test_committed_archive_retains_all_expected_artifact_classes(self) -> None:
        paths = [item["path"] for item in self.archive["files"]]
        self.assertEqual(paths, sorted(paths))
        self.assertEqual(len(paths), len(set(paths)))
        self.assertEqual(len(paths), 84)
        self.assertIn("plan.json", paths)
        self.assertIn("index.json", paths)
        for case in self.plan["case_arms"]:
            prefix = f"cases/{case['case_id']}"
            for name in (
                "descriptor.json",
                "identity.json",
                "manifest.json",
                "binding.json",
                "matrix-report.json",
                "projection.json",
                "result.json",
            ):
                self.assertIn(f"{prefix}/{name}", paths)
            if case["localization"]["required"]:
                self.assertIn(
                    f"{prefix}/claim-witness-declaration.json",
                    paths,
                )
                self.assertIn(
                    f"{prefix}/claim-witness-localization.json",
                    paths,
                )

    def test_committed_archive_contains_no_holdout_or_headline_claim(self) -> None:
        self.assertNotEqual(self.archive["partition"], "holdout")
        for item in self.archive["files"]:
            document = item["document"]
            if item["path"] == "index.json":
                self.assertIsNone(document["analysis"]["headline_score"])
                self.assertFalse(
                    document["analysis"]["ecological_inference_allowed"]
                )
            if item["path"].endswith("manifest.json"):
                self.assertEqual(document["partition"], "development")
            if item["path"].endswith("result.json"):
                self.assertEqual(document["partition"], "development")
                self.assertTrue(
                    all(
                        method["primary_denominator_eligible"] is False
                        for method in document["methods"]
                    )
                )


if __name__ == "__main__":
    unittest.main()
