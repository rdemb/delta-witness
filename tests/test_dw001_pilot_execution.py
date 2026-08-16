from __future__ import annotations

from copy import deepcopy
import json
import math
from pathlib import Path
import tempfile
import unittest

from deltawitness.dw001_pilot import (
    INDEX_SCHEMA_VERSION,
    build_development_pilot_plan,
    compute_development_pilot_index_sha256,
    run_development_pilot,
    verify_development_pilot_bundle,
    verify_development_pilot_index_document,
)


_PROTOCOL_SHA = "a" * 40
_IMPLEMENTATION_SHA = "b" * 40
_EXPECTED_METHODS = {
    "valid-discriminating-regression": ["accept", "accept", "accept", "accept"],
    "non-discriminating-candidate-test": ["accept", "reject", "reject", "reject"],
    "candidate-regression-against-base-tests": ["accept", "accept", "reject", "reject"],
    "wrong-reason-base-import-failure": {
        "O0_EXIT_CODE": ["accept", "accept", "accept", "accept"],
        "O1_TYPED_RECEIPT": [
            "accept",
            "indeterminate",
            "indeterminate",
            "indeterminate",
        ],
    },
    "wrong-reason-unrelated-assertion": ["accept", "accept", "accept", "accept"],
}
_EXPECTED_LOCALIZATION = {
    "valid-discriminating-regression": "supported",
    "non-discriminating-candidate-test": "not_applicable",
    "candidate-regression-against-base-tests": "not_applicable",
    "wrong-reason-base-import-failure": "indeterminate",
    "wrong-reason-unrelated-assertion": "unsupported",
}
_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "DW-001"
    / "schema"
    / "development-pilot-index.schema.json"
)


def _walk(value: object):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


class DW001DevelopmentPilotExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls._temporary.name)
        cls.plan = build_development_pilot_plan(
            protocol_commit_sha=_PROTOCOL_SHA,
            implementation_commit_sha=_IMPLEMENTATION_SHA,
        )
        cls.first_directory = cls.root / "first"
        cls.second_directory = cls.root / "second"
        cls.first = run_development_pilot(cls.plan, cls.first_directory)
        cls.second = run_development_pilot(cls.plan, cls.second_directory)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temporary.cleanup()

    def test_complete_ten_arm_bundle_and_index_verify(self) -> None:
        for directory, index in (
            (self.first_directory, self.first),
            (self.second_directory, self.second),
        ):
            with self.subTest(directory=directory.name):
                index_valid, index_errors = verify_development_pilot_index_document(
                    index,
                    self.plan,
                )
                bundle_valid, bundle_errors = verify_development_pilot_bundle(
                    directory,
                    self.plan,
                )
                self.assertTrue(index_valid, index_errors)
                self.assertTrue(bundle_valid, bundle_errors)
                self.assertEqual(index["schema_version"], INDEX_SCHEMA_VERSION)
                self.assertEqual(index["partition"], "development")
                self.assertTrue(index["complete"])
                self.assertEqual(len(index["cases"]), 10)
                self.assertTrue((directory / "plan.json").is_file())
                self.assertTrue((directory / "index.json").is_file())

    def test_method_and_localization_tables_preserve_expected_controls(self) -> None:
        for case in self.first["cases"]:
            family = case["family_id"]
            observer_id = case["observer_id"]
            expected_methods = _EXPECTED_METHODS[family]
            if isinstance(expected_methods, dict):
                expected_methods = expected_methods[observer_id]
            self.assertEqual(
                [method["decision"] for method in case["methods"]],
                expected_methods,
                case["case_id"],
            )
            self.assertTrue(all(method["concordant"] for method in case["methods"]))
            self.assertTrue(
                all(
                    method["primary_denominator_eligible"] is False
                    for method in case["methods"]
                )
            )
            self.assertEqual(
                case["localization"]["observed_status"],
                _EXPECTED_LOCALIZATION[family],
            )
            self.assertTrue(case["localization"]["concordant"])

        contrast_statuses = {
            item["contrast_id"]: item["status"]
            for item in self.first["analysis"]["contrasts"]
        }
        self.assertEqual(
            contrast_statuses,
            {
                "candidate-test-discrimination": "observed_as_expected",
                "original-test-preservation": "observed_as_expected",
                "typed-import-error": "observed_as_expected",
                "declared-witness-mismatch": "observed_as_expected",
                "valid-positive-control": "observed_as_expected",
            },
        )
        self.assertIsNone(self.first["analysis"]["headline_score"])
        self.assertFalse(self.first["analysis"]["ecological_inference_allowed"])

    def test_every_case_retains_and_verifies_required_artifacts(self) -> None:
        required = {
            "descriptor",
            "identity",
            "manifest",
            "binding",
            "matrix_report",
            "projection",
            "result",
        }
        for case in self.first["cases"]:
            artifacts = case["artifacts"]
            self.assertTrue(required.issubset(artifacts))
            for name in required:
                path = self.first_directory / artifacts[name]
                self.assertTrue(path.is_file(), (case["case_id"], name, path))
                self.assertIsInstance(
                    json.loads(path.read_text(encoding="utf-8")),
                    dict,
                )
            if case["localization"]["required"]:
                for name in ("declaration", "localization"):
                    path = self.first_directory / artifacts[name]
                    self.assertTrue(path.is_file(), (case["case_id"], name, path))
            else:
                self.assertIsNone(artifacts["declaration"])
                self.assertIsNone(artifacts["localization"])

    def test_costs_are_finite_nonnegative_and_review_missingness_is_explicit(self) -> None:
        for case in self.first["cases"]:
            cost = case["cost"]
            for field in ("wall_clock_seconds", "cpu_seconds"):
                self.assertIsInstance(cost[field], float)
                self.assertTrue(math.isfinite(cost[field]))
                self.assertGreaterEqual(cost[field], 0.0)
            for field in (
                "executed_matrix_states",
                "executed_selector_states",
                "command_count",
                "artifact_count",
                "public_bundle_bytes",
            ):
                self.assertIsInstance(cost[field], int)
                self.assertGreaterEqual(cost[field], 0)
            self.assertIsNone(cost["review_time_minutes"])
            self.assertEqual(cost["review_status"], "unmeasured")
            self.assertTrue(cost["missing_reason"])

    def test_repeated_fresh_runs_preserve_semantic_index_and_case_identities(self) -> None:
        self.assertEqual(
            self.first["semantic_sha256"],
            self.second["semantic_sha256"],
        )
        self.assertEqual(
            [case["case_id"] for case in self.first["cases"]],
            [case["case_id"] for case in self.second["cases"]],
        )
        for first_case, second_case in zip(
            self.first["cases"],
            self.second["cases"],
            strict=True,
        ):
            self.assertEqual(first_case["stable_evidence"], second_case["stable_evidence"])
            self.assertEqual(first_case["methods"], second_case["methods"])
            self.assertEqual(
                first_case["localization"]["observed_status"],
                second_case["localization"]["observed_status"],
            )

    def test_missing_or_substituted_artifact_fails_bundle_verification(self) -> None:
        victim = self.first["cases"][0]
        report_path = self.first_directory / victim["artifacts"]["matrix_report"]
        original = report_path.read_text(encoding="utf-8")
        report_path.unlink()
        valid, errors = verify_development_pilot_bundle(
            self.first_directory,
            self.plan,
        )
        self.assertFalse(valid)
        self.assertTrue(any("matrix_report" in error for error in errors), errors)
        report_path.write_text(original, encoding="utf-8")

        substituted = json.loads(original)
        substituted["head_sha"] = "f" * 40
        report_path.write_text(json.dumps(substituted), encoding="utf-8")
        valid, errors = verify_development_pilot_bundle(
            self.first_directory,
            self.plan,
        )
        self.assertFalse(valid)
        self.assertTrue(errors)
        report_path.write_text(original, encoding="utf-8")

    def test_recomputed_index_digest_cannot_hide_plan_or_case_drift(self) -> None:
        for mutator, label in (
            (
                lambda index: index.__setitem__("plan_sha256", "f" * 64),
                "plan_sha256",
            ),
            (
                lambda index: index["cases"][0].__setitem__(
                    "family_id", "non-discriminating-candidate-test"
                ),
                "family_id",
            ),
            (
                lambda index: index["cases"][0]["methods"][0].__setitem__(
                    "primary_denominator_eligible", True
                ),
                "denominator",
            ),
        ):
            with self.subTest(label=label):
                tampered = deepcopy(self.first)
                mutator(tampered)
                tampered["index_sha256"] = compute_development_pilot_index_sha256(
                    tampered
                )
                valid, errors = verify_development_pilot_index_document(
                    tampered,
                    self.plan,
                )
                self.assertFalse(valid)
                self.assertTrue(any(label in error for error in errors), errors)

    def test_output_destination_is_fail_closed(self) -> None:
        nonempty = self.root / "nonempty"
        nonempty.mkdir()
        marker = nonempty / "keep.txt"
        marker.write_text("keep", encoding="utf-8")
        with self.assertRaises(Exception):
            run_development_pilot(self.plan, nonempty)
        self.assertEqual(marker.read_text(encoding="utf-8"), "keep")

        if hasattr(Path, "symlink_to"):
            target = self.root / "target"
            target.mkdir()
            link = self.root / "link"
            try:
                link.symlink_to(target, target_is_directory=True)
            except (OSError, NotImplementedError):
                return
            with self.assertRaises(Exception):
                run_development_pilot(self.plan, link)
            self.assertEqual(list(target.iterdir()), [])

    def test_public_bundle_excludes_private_paths_and_raw_output(self) -> None:
        for path in self.first_directory.rglob("*.json"):
            text = path.read_text(encoding="utf-8")
            for prohibited in (
                "/tmp/",
                "\\Temp\\",
                "Traceback (most recent call last)",
                '"stdout": "',
                '"stderr": "',
                "credential",
                "environment_values",
                str(self.first_directory),
            ):
                with self.subTest(path=path.name, prohibited=prohibited):
                    self.assertNotIn(prohibited, text)

    def test_index_schema_is_strict_and_matches_emitted_root(self) -> None:
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )
        self.assertIs(schema["additionalProperties"], False)
        self.assertEqual(set(schema["required"]), set(self.first))
        self.assertEqual(set(schema["properties"]), set(self.first))
        for node in _walk(schema):
            if isinstance(node, dict) and node.get("type") == "object":
                self.assertIs(node.get("additionalProperties"), False, node)


if __name__ == "__main__":
    unittest.main()
