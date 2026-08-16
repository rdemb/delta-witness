from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from deltawitness.dw001_pilot import (
    build_development_pilot_archive,
    build_development_pilot_plan,
    compute_development_pilot_archive_sha256,
    run_development_pilot,
    verify_development_pilot_archive_document,
    verify_development_pilot_bundle,
)


_PROTOCOL_SHA = "732f829e25ea994858fffb0678892048617155c3"
_IMPLEMENTATION_SHA = "4ef67e0e7a20c7de03be825720dfb2d1da8e64fc"


class DW001DevelopmentPilotExactFileSetTests(unittest.TestCase):
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

    def test_bundle_rejects_unexpected_json_file(self) -> None:
        unexpected = self.bundle / "unexpected.json"
        unexpected.write_text("{}\n", encoding="utf-8")
        try:
            valid, errors = verify_development_pilot_bundle(
                self.bundle,
                self.plan,
            )
            self.assertFalse(valid)
            self.assertTrue(
                any("unexpected" in error and "unexpected.json" in error for error in errors),
                errors,
            )
            with self.assertRaisesRegex(Exception, "unexpected.json"):
                build_development_pilot_archive(self.bundle, self.plan)
        finally:
            unexpected.unlink()

    def test_bundle_rejects_unexpected_non_json_file(self) -> None:
        unexpected = self.bundle / "notes.txt"
        unexpected.write_text("not part of the evidence bundle\n", encoding="utf-8")
        try:
            valid, errors = verify_development_pilot_bundle(
                self.bundle,
                self.plan,
            )
            self.assertFalse(valid)
            self.assertTrue(
                any("unexpected" in error and "notes.txt" in error for error in errors),
                errors,
            )
        finally:
            unexpected.unlink()

    def test_archive_rejects_extra_digest_valid_document(self) -> None:
        tampered = deepcopy(self.archive)
        extra = {
            "schema_version": "deltawitness.dw001-development-pilot-file.v1",
            "path": "unexpected.json",
            "document": {"note": "not part of the sealed bundle"},
            "document_sha256": None,
        }
        extra["document_sha256"] = compute_development_pilot_archive_sha256(extra)
        tampered["files"].append(extra)
        tampered["files"].sort(key=lambda item: item["path"])
        tampered["archive_sha256"] = compute_development_pilot_archive_sha256(
            tampered
        )

        valid, errors = verify_development_pilot_archive_document(
            tampered,
            self.plan,
        )

        self.assertFalse(valid)
        self.assertTrue(
            any("unexpected" in error and "unexpected.json" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
