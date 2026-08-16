from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from deltawitness.dw001_pilot import (
    ARCHIVE_SCHEMA_VERSION,
    build_development_pilot_archive,
    build_development_pilot_plan,
    compute_development_pilot_archive_sha256,
    materialize_development_pilot_archive,
    run_development_pilot,
    verify_development_pilot_archive_document,
    verify_development_pilot_bundle,
)


_PROTOCOL_SHA = "732f829e25ea994858fffb0678892048617155c3"
_IMPLEMENTATION_SHA = "4ef67e0e7a20c7de03be825720dfb2d1da8e64fc"
_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "DW-001"
    / "schema"
    / "development-pilot-archive.schema.json"
)


def _walk(value: object):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


class DW001DevelopmentPilotArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls._temporary.name)
        cls.plan = build_development_pilot_plan(
            protocol_commit_sha=_PROTOCOL_SHA,
            implementation_commit_sha=_IMPLEMENTATION_SHA,
        )
        cls.bundle = cls.root / "bundle"
        run_development_pilot(cls.plan, cls.bundle)
        cls.archive = build_development_pilot_archive(cls.bundle, cls.plan)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temporary.cleanup()

    def test_archive_round_trip_reconstructs_verified_bundle(self) -> None:
        valid, errors = verify_development_pilot_archive_document(
            self.archive,
            self.plan,
        )
        self.assertTrue(valid, errors)
        self.assertEqual(self.archive["schema_version"], ARCHIVE_SCHEMA_VERSION)
        self.assertEqual(self.archive["partition"], "development")
        self.assertEqual(self.archive["plan_sha256"], self.plan["plan_sha256"])
        self.assertGreater(len(self.archive["files"]), 70)
        self.assertEqual(
            [item["path"] for item in self.archive["files"]],
            sorted(item["path"] for item in self.archive["files"]),
        )

        restored = self.root / "restored"
        materialize_development_pilot_archive(
            self.archive,
            restored,
            self.plan,
        )
        bundle_valid, bundle_errors = verify_development_pilot_bundle(
            restored,
            self.plan,
        )
        self.assertTrue(bundle_valid, bundle_errors)

    def test_recomputed_archive_digest_cannot_hide_document_or_path_substitution(self) -> None:
        for mutator, expected_error in (
            (
                lambda archive: archive["files"][0].__setitem__(
                    "path", "cases/substituted/descriptor.json"
                ),
                "path",
            ),
            (
                lambda archive: archive["files"][0]["document"].__setitem__(
                    "study_id", "DW-999"
                ),
                "document",
            ),
            (
                lambda archive: archive.__setitem__("plan_sha256", "f" * 64),
                "plan_sha256",
            ),
        ):
            with self.subTest(error=expected_error):
                tampered = deepcopy(self.archive)
                mutator(tampered)
                item = tampered["files"][0]
                item["document_sha256"] = compute_development_pilot_archive_sha256(
                    {
                        "schema_version": "deltawitness.dw001-development-pilot-file.v1",
                        "path": item["path"],
                        "document": item["document"],
                        "document_sha256": None,
                    }
                )
                tampered["archive_sha256"] = compute_development_pilot_archive_sha256(
                    tampered
                )
                valid, errors = verify_development_pilot_archive_document(
                    tampered,
                    self.plan,
                )
                self.assertFalse(valid)
                self.assertTrue(any(expected_error in error for error in errors), errors)

    def test_archive_rejects_duplicate_missing_and_private_paths(self) -> None:
        duplicate = deepcopy(self.archive)
        duplicate["files"].append(deepcopy(duplicate["files"][0]))
        duplicate["archive_sha256"] = compute_development_pilot_archive_sha256(
            duplicate
        )
        valid, errors = verify_development_pilot_archive_document(duplicate, self.plan)
        self.assertFalse(valid)
        self.assertTrue(any("duplicate" in error for error in errors), errors)

        missing = deepcopy(self.archive)
        missing["files"] = missing["files"][1:]
        missing["archive_sha256"] = compute_development_pilot_archive_sha256(missing)
        valid, errors = verify_development_pilot_archive_document(missing, self.plan)
        self.assertFalse(valid)
        self.assertTrue(any("missing" in error for error in errors), errors)

        private = deepcopy(self.archive)
        private["files"][0]["path"] = "/tmp/private.json"
        private["archive_sha256"] = compute_development_pilot_archive_sha256(private)
        valid, errors = verify_development_pilot_archive_document(private, self.plan)
        self.assertFalse(valid)
        self.assertTrue(any("repository-relative" in error for error in errors), errors)

    def test_archive_is_public_safe_and_contains_only_json_objects(self) -> None:
        encoded = json.dumps(self.archive, sort_keys=True)
        for prohibited in (
            "/tmp/",
            "\\Temp\\",
            "Traceback (most recent call last)",
            '"stdout": "',
            '"stderr": "',
            "credential",
            str(self.root),
        ):
            self.assertNotIn(prohibited, encoded)
        self.assertTrue(
            all(isinstance(item["document"], dict) for item in self.archive["files"])
        )

    def test_archive_schema_is_strict_and_matches_root(self) -> None:
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )
        self.assertIs(schema["additionalProperties"], False)
        self.assertEqual(set(schema["required"]), set(self.archive))
        self.assertEqual(set(schema["properties"]), set(self.archive))
        for node in _walk(schema):
            if isinstance(node, dict) and node.get("type") == "object":
                self.assertIs(node.get("additionalProperties"), False, node)


if __name__ == "__main__":
    unittest.main()
