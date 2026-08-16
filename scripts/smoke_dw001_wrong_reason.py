#!/usr/bin/env python3
"""Exercise the packaged paired DW-001 wrong-reason observer probe.

The smoke uses only fixed project-owned synthetic bytes. It verifies that the
same declared scenario is accepted by the exit-code arm but preserved as
indeterminate by the typed-receipt arm when base+candidate tests terminate in a
pre-assertion import error. It does not authorize a pilot or held-out run.
"""

from __future__ import annotations

from pathlib import Path
import tempfile

from deltawitness.config import load_config
from deltawitness.dw001 import project_baselines
from deltawitness.dw001_fixture_binding import (
    build_fixture_manifest_binding,
    verify_fixture_manifest_binding_document,
)
from deltawitness.dw001_scenarios import (
    build_fixture_descriptor,
    materialize_synthetic_fixture,
    verify_fixture_identity_document,
    verify_materialized_fixture,
)
from deltawitness.matrix import verify_repository, write_report
from deltawitness.reporting import load_report, verify_report_document
from smoke_dw001_fixture_binding import _manifest


_FAMILY = "wrong-reason-base-import-failure"
_SCENARIO_ID = "ci-wrong-reason-import-smoke-001"


def _decisions(projection: dict[str, object]) -> dict[str, str]:
    methods = projection["methods"]
    if not isinstance(methods, list):
        raise AssertionError("projection methods are not a list")
    return {method["method_id"]: method["decision"] for method in methods}


def _run(observer: str) -> tuple[object, dict[str, object]]:
    descriptor = build_fixture_descriptor(
        scenario_id=_SCENARIO_ID,
        family_id=_FAMILY,
        observer=observer,
    )
    with tempfile.TemporaryDirectory() as directory:
        repository = Path(directory)
        identity = materialize_synthetic_fixture(descriptor, repository)
        identity_valid, identity_errors = verify_fixture_identity_document(
            identity,
            descriptor,
        )
        materialized_valid, materialized_errors = verify_materialized_fixture(
            identity,
            descriptor,
            repository,
        )
        if not identity_valid:
            raise AssertionError(identity_errors)
        if not materialized_valid:
            raise AssertionError(materialized_errors)

        manifest = _manifest(descriptor, identity)
        binding = build_fixture_manifest_binding(descriptor, identity, manifest)
        binding_valid, binding_errors = verify_fixture_manifest_binding_document(
            binding,
            descriptor,
            identity,
            manifest,
        )
        if not binding_valid:
            raise AssertionError(binding_errors)

        report = verify_repository(
            repository,
            identity["git"]["base_commit_sha"],  # type: ignore[index]
            identity["git"]["head_commit_sha"],  # type: ignore[index]
            load_config(repository / identity["specification"]["path"]),  # type: ignore[index]
        )
        report_path = repository / ".git" / "deltawitness" / "wrong-reason.json"
        write_report(report, report_path)
        decoded = load_report(report_path)
        report_valid, report_errors = verify_report_document(decoded)
        if not report_valid:
            raise AssertionError(report_errors)
        projection = project_baselines(decoded, scenario_id=_SCENARIO_ID)

    return report, projection


def main() -> int:
    exit_report, exit_projection = _run("exit-code-v1")
    typed_report, typed_projection = _run("outcome-receipt-v1")

    exit_state = {
        state.state: state for state in exit_report.claims[0].states
    }["base_candidate"]
    typed_state = {
        state.state: state for state in typed_report.claims[0].states
    }["base_candidate"]

    if exit_state.observed != "fail" or not exit_report.complete or not exit_report.supported:
        raise AssertionError("exit-code arm did not expose the controlled false assurance")
    if _decisions(exit_projection) != {
        "M0_FINAL": "accept",
        "M1_F2P": "accept",
        "M2_F2P_P2P": "accept",
        "M3_FOUR_STATE": "accept",
    }:
        raise AssertionError("exit-code arm method decisions changed")

    if typed_state.observed != "error":
        raise AssertionError("typed arm did not preserve the execution error")
    if typed_state.receipt_outcome != "test_error":
        raise AssertionError("typed arm did not record test_error")
    if typed_state.receipt_counts is None:
        raise AssertionError("typed arm omitted receipt counts")
    if typed_state.receipt_counts["failures"] != 0:
        raise AssertionError("import-error state incorrectly recorded assertion failures")
    if typed_state.receipt_counts["errors"] < 1:
        raise AssertionError("typed arm did not record an execution error")
    if typed_report.complete or typed_report.supported:
        raise AssertionError("typed error was converted into complete evidence")
    if _decisions(typed_projection) != {
        "M0_FINAL": "accept",
        "M1_F2P": "indeterminate",
        "M2_F2P_P2P": "indeterminate",
        "M3_FOUR_STATE": "indeterminate",
    }:
        raise AssertionError("typed arm method decisions changed")

    print("DW-001 wrong-reason observer smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
