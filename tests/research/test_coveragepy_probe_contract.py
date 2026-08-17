from __future__ import annotations

from copy import deepcopy
import math
from pathlib import Path
import tempfile
import unittest

from deltawitness.coveragepy_contract import COVERAGEPY_MANIFEST_SHA256
from deltawitness.coveragepy_probe import (
    COVERAGE_RECEIPT_SCHEMA_VERSION,
    CoveragePyProbeError,
    build_coverage_receipt,
    compute_coverage_receipt_sha256,
    load_coverage_receipt,
    validate_coverage_receipt,
)
from deltawitness.reporting import canonical_json


_BINDING = "a" * 64
_SOURCE_SHA256 = "b" * 64
_CONTEXT_ID = (
    "dw001-coveragepy-v1:strong-authorization-oracle-v1:"
    "test_access.AccessTests.test_admin_is_allowed"
)
_TARGET = {
    "path": "src/access.py",
    "symbol": "is_admin",
    "source_sha256": _SOURCE_SHA256,
    "target_lines": [2],
}
_DISTRIBUTION = {
    "manifest_sha256": COVERAGEPY_MANIFEST_SHA256,
    "package": "coverage",
    "expected_version": "7.15.2",
    "observed_distribution_name": "coverage",
    "observed_distribution_version": "7.15.2",
    "observed_module_version": "7.15.2",
}
_CONFIGURATION = {
    "data_file": None,
    "auto_data": False,
    "timid": True,
    "branch": True,
    "config_file": False,
    "source_dirs": ["src"],
    "concurrency": None,
    "check_preimported": False,
    "context": _CONTEXT_ID,
    "messages": False,
    "plugins": [],
    "auto_start": False,
    "subprocess_measurement": False,
    "network_during_measurement": False,
}
_ARCS = [[-1, 1], [-1, 2], [1, -1], [2, -1]]


def _expected() -> dict[str, object]:
    return {
        "expected_binding": _BINDING,
        "expected_target": _TARGET,
        "expected_context_id": _CONTEXT_ID,
        "expected_configuration": _CONFIGURATION,
        "expected_manifest_sha256": COVERAGEPY_MANIFEST_SHA256,
    }


def _complete_receipt() -> dict[str, object]:
    return build_coverage_receipt(
        binding=_BINDING,
        distribution=_DISTRIBUTION,
        configuration=_CONFIGURATION,
        target=_TARGET,
        context={
            "id": _CONTEXT_ID,
            "strategy": "static-selector-context-v1",
        },
        measurement_status="complete",
        measurement_error=None,
        measured_files=["src/access.py"],
        statement_evidence={
            "executable": [1, 2],
            "executed": [1, 2],
            "missing": [],
            "measured_lines": [1, 2],
            "target_executable": [2],
            "target_executed": [2],
            "target_missing": [],
        },
        branch_evidence={
            "has_arcs": True,
            "all_arcs": _ARCS,
            "context_arcs": _ARCS,
            "target_arcs": [[-1, 2], [2, -1]],
            "branch_stats": [],
            "target_branch_stats": [],
            "missing_branch_count": 0,
            "target_missing_branch_count": 0,
            "missing_branch_arcs": None,
            "missing_branch_arc_identity_status": "unavailable-public-api",
        },
        context_evidence={
            "measured_contexts": [_CONTEXT_ID],
            "contexts_by_lineno": [
                {"line": 1, "contexts": [_CONTEXT_ID]},
                {"line": 2, "contexts": [_CONTEXT_ID]},
            ],
            "query_context": _CONTEXT_ID,
            "lines": [1, 2],
            "arcs": _ARCS,
            "partition_valid": True,
        },
        cost={
            "status": "measured",
            "wall_clock_seconds": 0.01,
            "cpu_seconds": 0.01,
            "missing_reason": None,
        },
    )


def _indeterminate_receipt() -> dict[str, object]:
    return build_coverage_receipt(
        binding=_BINDING,
        distribution={
            **_DISTRIBUTION,
            "observed_distribution_name": None,
            "observed_distribution_version": None,
            "observed_module_version": None,
        },
        configuration=_CONFIGURATION,
        target=_TARGET,
        context={
            "id": _CONTEXT_ID,
            "strategy": "static-selector-context-v1",
        },
        measurement_status="indeterminate",
        measurement_error="missing_optional_dependency",
        measured_files=None,
        statement_evidence=None,
        branch_evidence=None,
        context_evidence=None,
        cost={
            "status": "measured",
            "wall_clock_seconds": 0.01,
            "cpu_seconds": 0.01,
            "missing_reason": None,
        },
    )


class CoveragePyProbeContractTests(unittest.TestCase):
    def test_complete_and_indeterminate_receipts_are_exact_and_valid(self) -> None:
        complete = _complete_receipt()
        self.assertEqual(
            complete["schema_version"],
            COVERAGE_RECEIPT_SCHEMA_VERSION,
        )
        self.assertEqual(validate_coverage_receipt(complete, **_expected()), complete)

        indeterminate = _indeterminate_receipt()
        self.assertEqual(
            validate_coverage_receipt(indeterminate, **_expected()),
            indeterminate,
        )

    def test_complete_measured_empty_is_distinct_from_unavailable(self) -> None:
        measured_empty = _complete_receipt()
        measured_empty["statement_evidence"] = {
            "executable": [1, 2],
            "executed": [],
            "missing": [1, 2],
            "measured_lines": [],
            "target_executable": [2],
            "target_executed": [],
            "target_missing": [2],
        }
        measured_empty["branch_evidence"] = {
            "has_arcs": True,
            "all_arcs": [],
            "context_arcs": [],
            "target_arcs": [],
            "branch_stats": [],
            "target_branch_stats": [],
            "missing_branch_count": 0,
            "target_missing_branch_count": 0,
            "missing_branch_arcs": None,
            "missing_branch_arc_identity_status": "unavailable-public-api",
        }
        measured_empty["context_evidence"] = {
            "measured_contexts": [_CONTEXT_ID],
            "contexts_by_lineno": [],
            "query_context": _CONTEXT_ID,
            "lines": [],
            "arcs": [],
            "partition_valid": True,
        }
        measured_empty["coverage_sha256"] = compute_coverage_receipt_sha256(
            measured_empty
        )
        self.assertEqual(
            validate_coverage_receipt(measured_empty, **_expected()),
            measured_empty,
        )

        unavailable_as_empty = _indeterminate_receipt()
        unavailable_as_empty["measured_files"] = []
        unavailable_as_empty["statement_evidence"] = measured_empty[
            "statement_evidence"
        ]
        unavailable_as_empty["branch_evidence"] = measured_empty[
            "branch_evidence"
        ]
        unavailable_as_empty["context_evidence"] = measured_empty[
            "context_evidence"
        ]
        unavailable_as_empty["coverage_sha256"] = (
            compute_coverage_receipt_sha256(unavailable_as_empty)
        )
        with self.assertRaisesRegex(CoveragePyProbeError, "indeterminate"):
            validate_coverage_receipt(unavailable_as_empty, **_expected())

    def test_context_swap_and_cross_contamination_are_rejected(self) -> None:
        complete = _complete_receipt()
        with self.assertRaisesRegex(CoveragePyProbeError, "context"):
            validate_coverage_receipt(
                complete,
                **{
                    **_expected(),
                    "expected_context_id": "wrong-context",
                },
            )

        contaminated = deepcopy(complete)
        contaminated["context_evidence"]["measured_contexts"].append(
            "ambient-context"
        )
        contaminated["context_evidence"]["contexts_by_lineno"][0][
            "contexts"
        ].append("ambient-context")
        contaminated["context_evidence"]["partition_valid"] = False
        contaminated["coverage_sha256"] = compute_coverage_receipt_sha256(
            contaminated
        )
        with self.assertRaisesRegex(CoveragePyProbeError, "context"):
            validate_coverage_receipt(contaminated, **_expected())

    def test_distribution_configuration_and_producer_substitution_are_rejected(self) -> None:
        changes = (
            ("distribution.expected_version", "7.15.1"),
            ("distribution.observed_module_version", "7.15.1"),
            ("configuration.config_file", True),
            ("configuration.plugins", ["ambient.plugin"]),
            ("configuration.auto_start", True),
            ("configuration.concurrency", "multiprocessing"),
            ("configuration.subprocess_measurement", True),
            ("producer.name", "substituted-producer"),
        )
        for dotted_path, value in changes:
            with self.subTest(field=dotted_path):
                tampered = deepcopy(_complete_receipt())
                current = tampered
                parts = dotted_path.split(".")
                for part in parts[:-1]:
                    current = current[part]
                current[parts[-1]] = value
                tampered["coverage_sha256"] = (
                    compute_coverage_receipt_sha256(tampered)
                )
                with self.assertRaises(CoveragePyProbeError):
                    validate_coverage_receipt(tampered, **_expected())

    def test_statement_arc_and_profile_inputs_are_strict_sets(self) -> None:
        changes = (
            ("statement_evidence.executed", [2, 1]),
            ("statement_evidence.missing", [2, 2]),
            ("statement_evidence.target_executed", [1]),
            ("branch_evidence.all_arcs", [[2, -1], [-1, 2]]),
            ("branch_evidence.target_arcs", [[2, -1], [2, -1]]),
            ("context_evidence.lines", [2, 1]),
            ("context_evidence.arcs", [[2, -1], [-1, 2]]),
        )
        for dotted_path, value in changes:
            with self.subTest(field=dotted_path):
                tampered = deepcopy(_complete_receipt())
                current = tampered
                parts = dotted_path.split(".")
                for part in parts[:-1]:
                    current = current[part]
                current[parts[-1]] = value
                tampered["coverage_sha256"] = (
                    compute_coverage_receipt_sha256(tampered)
                )
                with self.assertRaises(CoveragePyProbeError):
                    validate_coverage_receipt(tampered, **_expected())

    def test_absolute_paths_and_unexpected_fields_are_rejected(self) -> None:
        absolute = deepcopy(_complete_receipt())
        absolute["measured_files"] = ["/tmp/private/src/access.py"]
        absolute["coverage_sha256"] = compute_coverage_receipt_sha256(
            absolute
        )
        with self.assertRaisesRegex(CoveragePyProbeError, "relative"):
            validate_coverage_receipt(absolute, **_expected())

        extra = deepcopy(_complete_receipt())
        extra["private_path"] = "/tmp/private"
        extra["coverage_sha256"] = compute_coverage_receipt_sha256(extra)
        with self.assertRaisesRegex(CoveragePyProbeError, "field"):
            validate_coverage_receipt(extra, **_expected())

    def test_costs_reject_negative_nan_and_infinity(self) -> None:
        for value in (-1.0, math.nan, math.inf, -math.inf):
            with self.subTest(value=value):
                tampered = deepcopy(_complete_receipt())
                tampered["cost"]["wall_clock_seconds"] = value
                tampered["coverage_sha256"] = (
                    compute_coverage_receipt_sha256(tampered)
                )
                with self.assertRaisesRegex(CoveragePyProbeError, "cost"):
                    validate_coverage_receipt(tampered, **_expected())

    def test_loader_rejects_duplicate_keys_and_symbolic_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            duplicate = root / "duplicate.json"
            duplicate.write_text(
                '{"schema_version":"x","schema_version":"y"}',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(Exception, "duplicate"):
                load_coverage_receipt(duplicate, **_expected())

            valid = root / "valid.json"
            valid.write_bytes(canonical_json(_complete_receipt()) + b"\n")
            linked = root / "linked.json"
            linked.symlink_to(valid)
            with self.assertRaisesRegex(CoveragePyProbeError, "regular non-link"):
                load_coverage_receipt(linked, **_expected())


if __name__ == "__main__":
    unittest.main()
