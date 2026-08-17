from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from deltawitness.statement_trace_probe import (
    StatementTraceError,
    TRACE_SCHEMA_VERSION,
    _target_source,
    build_trace_document,
    compute_trace_sha256,
    load_trace_document,
    validate_trace_document,
)


_BINDING = "a" * 64
_SOURCE_SHA256 = "b" * 64
_TARGET_PATH = "src/access.py"
_TARGET_SYMBOL = "is_admin"
_TARGET_LINES = [2]


def _validate(document: object) -> dict[str, object]:
    return validate_trace_document(
        document,
        expected_binding=_BINDING,
        expected_target_path=_TARGET_PATH,
        expected_target_symbol=_TARGET_SYMBOL,
        expected_source_sha256=_SOURCE_SHA256,
        expected_target_lines=_TARGET_LINES,
    )


class StatementTraceProbeTests(unittest.TestCase):
    def test_complete_and_indeterminate_receipts_are_strict_and_valid(self) -> None:
        complete = build_trace_document(
            binding=_BINDING,
            target_path=_TARGET_PATH,
            target_symbol=_TARGET_SYMBOL,
            source_sha256=_SOURCE_SHA256,
            target_lines=_TARGET_LINES,
            trace_status="complete",
            function_calls=1,
            line_hits={2: 1},
            trace_error=None,
        )
        self.assertEqual(complete["schema_version"], TRACE_SCHEMA_VERSION)
        self.assertEqual(_validate(complete), complete)

        indeterminate = build_trace_document(
            binding=_BINDING,
            target_path=_TARGET_PATH,
            target_symbol=_TARGET_SYMBOL,
            source_sha256=_SOURCE_SHA256,
            target_lines=_TARGET_LINES,
            trace_status="indeterminate",
            function_calls=None,
            line_hits={},
            trace_error="trace_unavailable",
        )
        self.assertEqual(_validate(indeterminate), indeterminate)

    def test_recomputed_digest_cannot_hide_inconsistent_coverage(self) -> None:
        document = build_trace_document(
            binding=_BINDING,
            target_path=_TARGET_PATH,
            target_symbol=_TARGET_SYMBOL,
            source_sha256=_SOURCE_SHA256,
            target_lines=_TARGET_LINES,
            trace_status="complete",
            function_calls=1,
            line_hits={2: 1},
            trace_error=None,
        )
        tampered = deepcopy(document)
        tampered["covered_lines"] = []
        tampered["trace_sha256"] = compute_trace_sha256(tampered)

        with self.assertRaisesRegex(StatementTraceError, "covered_lines"):
            _validate(tampered)

    def test_complete_trace_cannot_report_line_hits_without_target_call(self) -> None:
        document = build_trace_document(
            binding=_BINDING,
            target_path=_TARGET_PATH,
            target_symbol=_TARGET_SYMBOL,
            source_sha256=_SOURCE_SHA256,
            target_lines=_TARGET_LINES,
            trace_status="complete",
            function_calls=0,
            line_hits={2: 1},
            trace_error=None,
        )

        with self.assertRaisesRegex(StatementTraceError, "function_calls"):
            _validate(document)

    def test_indeterminate_receipt_cannot_carry_complete_trace_evidence(self) -> None:
        document = build_trace_document(
            binding=_BINDING,
            target_path=_TARGET_PATH,
            target_symbol=_TARGET_SYMBOL,
            source_sha256=_SOURCE_SHA256,
            target_lines=_TARGET_LINES,
            trace_status="indeterminate",
            function_calls=None,
            line_hits={},
            trace_error="trace_unavailable",
        )
        tampered = deepcopy(document)
        tampered["covered_lines"] = [2]
        tampered["line_hits"] = [{"line": 2, "hits": 1}]
        tampered["trace_sha256"] = compute_trace_sha256(tampered)

        with self.assertRaisesRegex(StatementTraceError, "indeterminate"):
            _validate(tampered)

    def test_loader_rejects_duplicate_keys_and_symbolic_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            duplicate = root / "duplicate.json"
            duplicate.write_text(
                '{"schema_version":"x","schema_version":"y"}',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(StatementTraceError, "strict UTF-8 JSON"):
                load_trace_document(
                    duplicate,
                    expected_binding=_BINDING,
                    expected_target_path=_TARGET_PATH,
                    expected_target_symbol=_TARGET_SYMBOL,
                    expected_source_sha256=_SOURCE_SHA256,
                    expected_target_lines=_TARGET_LINES,
                )

            valid = root / "valid.json"
            valid.write_text(
                json.dumps(
                    build_trace_document(
                        binding=_BINDING,
                        target_path=_TARGET_PATH,
                        target_symbol=_TARGET_SYMBOL,
                        source_sha256=_SOURCE_SHA256,
                        target_lines=_TARGET_LINES,
                        trace_status="complete",
                        function_calls=1,
                        line_hits={2: 1},
                        trace_error=None,
                    )
                ),
                encoding="utf-8",
            )
            link = root / "trace-link.json"
            link.symlink_to(valid)
            with self.assertRaisesRegex(StatementTraceError, "regular non-link"):
                load_trace_document(
                    link,
                    expected_binding=_BINDING,
                    expected_target_path=_TARGET_PATH,
                    expected_target_symbol=_TARGET_SYMBOL,
                    expected_source_sha256=_SOURCE_SHA256,
                    expected_target_lines=_TARGET_LINES,
                )

    def test_target_source_rejects_a_symbolic_link_before_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            source = root / "src" / "real_access.py"
            source.write_text(
                "def is_admin(user):\n    return True\n",
                encoding="utf-8",
            )
            linked = root / "src" / "linked_access.py"
            linked.symlink_to(source.name)
            source_sha256 = hashlib.sha256(source.read_bytes()).hexdigest()
            previous = Path.cwd()
            try:
                os.chdir(root)
                with self.assertRaisesRegex(
                    StatementTraceError,
                    "regular non-link",
                ):
                    _target_source("src/linked_access.py", source_sha256)
            finally:
                os.chdir(previous)


if __name__ == "__main__":
    unittest.main()
