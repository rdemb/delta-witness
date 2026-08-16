from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from deltawitness.dw001_ecological import (
    DESIGN_ID,
    SOURCE_UNIVERSE_SCHEMA_VERSION,
    build_ecological_source_universe,
    compute_ecological_source_universe_sha256,
    verify_ecological_source_universe_document,
)
from deltawitness.reporting import canonical_json


_MAIN_SHA = "6dada3bdde890eafe287cf6abdae76aaf7940cbb"
_ROOT = Path(__file__).resolve().parents[1]
_UNIVERSE_PATH = _ROOT / "research" / "DW-001" / "ecological-source-universe.v1.json"
_SCHEMA_PATH = _ROOT / "research" / "DW-001" / "schema" / "ecological-source-universe.schema.json"


class DW001EcologicalSourceUniverseTests(unittest.TestCase):
    def _universe(self):
        return build_ecological_source_universe(reviewed_main_sha=_MAIN_SHA)

    def test_universe_is_deterministic_and_design_only(self) -> None:
        first = self._universe()
        second = self._universe()

        self.assertEqual(first, second)
        self.assertEqual(canonical_json(first), canonical_json(second))
        self.assertEqual(first["schema_version"], SOURCE_UNIVERSE_SCHEMA_VERSION)
        self.assertEqual(first["study_id"], "DW-001")
        self.assertEqual(first["design_id"], DESIGN_ID)
        self.assertEqual(first["status"], "design_only")
        self.assertEqual(first["reviewed_main_sha"], _MAIN_SHA)
        self.assertIs(first["execution_authorized"], False)
        self.assertIs(first["holdout_selected"], False)
        self.assertIs(first["holdout_inspected"], False)
        self.assertEqual(len(first["sources"]), 2)
        self.assertTrue(all(source["execution_authorized"] is False for source in first["sources"]))
        self.assertTrue(all(source["containment_status"] == "unaccepted" for source in first["sources"]))

        valid, errors = verify_ecological_source_universe_document(first)
        self.assertTrue(valid, errors)

    def test_initial_sources_are_exact_pinned_repositories_not_executable_datasets(self) -> None:
        universe = self._universe()
        sources = {source["source_id"]: source for source in universe["sources"]}

        self.assertEqual(set(sources), {"swe-bench", "tdd-bench-verified"})
        self.assertEqual(sources["swe-bench"]["repository"], "SWE-bench/SWE-bench")
        self.assertEqual(
            sources["swe-bench"]["repository_commit_sha"],
            "ca6e4e0d252f32f8762625b73575d5dee49d0a5a",
        )
        self.assertEqual(sources["swe-bench"]["repository_license_spdx"], "MIT")
        self.assertEqual(
            sources["tdd-bench-verified"]["repository"],
            "IBM/TDD-Bench-Verified",
        )
        self.assertEqual(
            sources["tdd-bench-verified"]["repository_commit_sha"],
            "3df8be066e486789d0b8e0d2865a3a4422b4560f",
        )
        self.assertEqual(
            sources["tdd-bench-verified"]["repository_license_spdx"],
            "Apache-2.0",
        )
        for source in sources.values():
            self.assertEqual(source["dataset_reference_status"], "unpinned")
            self.assertEqual(source["authorization_review_status"], "pending")
            self.assertTrue(source["blocking_questions"])
            self.assertTrue(source["known_biases"])

    def test_recomputed_digest_cannot_authorize_execution_or_freeze_design(self) -> None:
        for mutator, expected in (
            (
                lambda document: document.__setitem__("execution_authorized", True),
                "execution_authorized",
            ),
            (
                lambda document: document["sources"][0].__setitem__(
                    "execution_authorized", True
                ),
                "sources[0].execution_authorized",
            ),
            (
                lambda document: document["decisions"].__setitem__(
                    "sampling_frame_status", "frozen"
                ),
                "sampling_frame_status",
            ),
            (
                lambda document: document.__setitem__("holdout_selected", True),
                "holdout_selected",
            ),
        ):
            with self.subTest(expected=expected):
                tampered = deepcopy(self._universe())
                mutator(tampered)
                tampered["universe_sha256"] = compute_ecological_source_universe_sha256(
                    tampered
                )
                valid, errors = verify_ecological_source_universe_document(tampered)
                self.assertFalse(valid)
                self.assertTrue(any(expected in error for error in errors), errors)

    def test_committed_universe_equals_canonical_builder(self) -> None:
        committed = json.loads(_UNIVERSE_PATH.read_text(encoding="utf-8"))
        expected = self._universe()

        self.assertEqual(committed, expected)
        valid, errors = verify_ecological_source_universe_document(committed)
        self.assertTrue(valid, errors)

    def test_schema_is_strict_and_matches_emitted_root(self) -> None:
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        universe = self._universe()

        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertIs(schema["additionalProperties"], False)
        self.assertEqual(set(schema["required"]), set(universe))
        self.assertEqual(set(schema["properties"]), set(universe))
        self.assertEqual(
            schema["properties"]["schema_version"]["const"],
            SOURCE_UNIVERSE_SCHEMA_VERSION,
        )
        self.assertIs(schema["properties"]["execution_authorized"]["const"], False)
        self.assertIs(schema["properties"]["holdout_selected"]["const"], False)
        self.assertIs(schema["properties"]["holdout_inspected"]["const"], False)

    def test_public_design_artifact_excludes_local_and_secret_material(self) -> None:
        encoded = json.dumps(self._universe(), sort_keys=True)
        for prohibited in (
            "/tmp/",
            "\\Temp\\",
            "credential",
            "token_value",
            "environment_values",
            "holdout_manifest",
        ):
            self.assertNotIn(prohibited, encoded)


if __name__ == "__main__":
    unittest.main()
