from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

from deltawitness.cli import main as cli_main
from deltawitness.errors import ReportError
from deltawitness.reporting import (
    canonical_json,
    compute_report_sha256,
    compute_witness_sha256,
    load_report,
    sha256_document,
)


_STATE_ORDER = ("base_base", "base_candidate", "candidate_base", "candidate_candidate")


def valid_report_document() -> dict[str, object]:
    document: dict[str, object] = {
        "schema_version": "0.3",
        "tool_version": "0.0.3",
        "created_at": "2026-08-15T00:00:00Z",
        "repository": "synthetic",
        "base_sha": "a" * 40,
        "head_sha": "b" * 40,
        "spec_path": "deltawitness.toml",
        "spec_external": False,
        "spec_sha256": "c" * 64,
        "execution": {
            "environment_mode": "sanitized-v1",
            "pass_env": [],
            "output_included": False,
            "sandboxed": False,
            "observer_protocols": [],
        },
        "classification": {"code": [], "tests": [], "documentation": []},
        "state_trees": {state: "d" * 40 for state in _STATE_ORDER},
        "state_commits": {state: "e" * 40 for state in _STATE_ORDER},
        "claims": [],
        "complete": True,
        "supported": True,
        "witness_sha256": None,
        "report_sha256": None,
    }
    document["witness_sha256"] = compute_witness_sha256(document)
    document["report_sha256"] = compute_report_sha256(document)
    return document


class ReportingTests(unittest.TestCase):
    @unittest.skipIf(os.name != "posix", "surrogateescape path semantics are POSIX-specific")
    def test_canonical_json_handles_non_utf8_git_path_bytes(self) -> None:
        path = os.fsdecode(b"tests/non-utf8-\xff.py")

        encoded = canonical_json({"path": path})

        self.assertIn(b"\\udcff", encoded)
        self.assertEqual(sha256_document({"path": path}), sha256_document({"path": path}))

    def test_load_report_preserves_valid_document(self) -> None:
        document = valid_report_document()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text(json.dumps(document), encoding="utf-8")

            loaded = load_report(path)

        self.assertEqual(loaded, document)

    def test_load_report_rejects_duplicate_top_level_key(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text('{"schema_version":"0.3","schema_version":"0.3"}', encoding="utf-8")

            with self.assertRaisesRegex(ReportError, "duplicate key"):
                load_report(path)

    def test_load_report_rejects_duplicate_nested_key(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text('{"execution":{"sandboxed":false,"sandboxed":true}}', encoding="utf-8")

            with self.assertRaisesRegex(ReportError, "duplicate key"):
                load_report(path)

    def test_load_report_wraps_invalid_utf8(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_bytes(b'{"schema_version":"0.3","invalid":"\xff"}')

            with self.assertRaisesRegex(ReportError, "UTF-8"):
                load_report(path)

    def test_verify_report_rejects_ambiguously_encoded_but_digest_valid_document(self) -> None:
        document = valid_report_document()
        encoded = json.dumps(document, sort_keys=True)
        ambiguous = encoded.replace(
            '"supported": true',
            '"supported": false, "supported": true',
            1,
        )
        self.assertNotEqual(ambiguous, encoded)

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text(ambiguous, encoding="utf-8")
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                return_code = cli_main(["verify-report", str(path)])

        self.assertEqual(return_code, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("duplicate key", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
