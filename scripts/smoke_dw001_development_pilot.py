#!/usr/bin/env python3
"""Execute and verify the complete packaged DW-001 development mechanism pilot.

The smoke loads the committed sealed plan, executes all ten fixed synthetic
arms in a disposable directory, verifies every retained artifact and controlled
contrast, builds a canonical archive, and requires semantic equality with the
committed canonical archive.

This is a packaging and reproducibility check over development-only mechanism
probes. It is not independent reproduction, an ecological evaluation, a
holdout, a headline score, or authorization to generalize the findings.
"""

from __future__ import annotations

from pathlib import Path
import tempfile

from deltawitness.dw001_pilot import (
    build_development_pilot_archive,
    materialize_development_pilot_archive,
    run_development_pilot,
    verify_development_pilot_archive_document,
    verify_development_pilot_bundle,
)
from deltawitness.reporting import load_report


_ROOT = Path(__file__).resolve().parents[1] / "research" / "DW-001"
_PLAN_PATH = _ROOT / "development-pilot-plan.v1.json"
_ARCHIVE_PATH = _ROOT / "development-pilot-archive.v1.json"


def _assert_index(index: dict[str, object], semantic_sha256: str) -> None:
    if index["complete"] is not True:
        raise AssertionError("development pilot index is incomplete")
    if index["partition"] != "development":
        raise AssertionError("development pilot escaped development partition")
    if index["semantic_sha256"] != semantic_sha256:
        raise AssertionError("development pilot semantic digest changed")
    cases = index["cases"]
    if not isinstance(cases, list) or len(cases) != 10:
        raise AssertionError("development pilot does not contain exactly ten arms")
    analysis = index["analysis"]
    if analysis["headline_score"] is not None:
        raise AssertionError("development pilot emitted a headline score")
    if analysis["ecological_inference_allowed"] is not False:
        raise AssertionError("development pilot enabled ecological inference")
    contrasts = analysis["contrasts"]
    if len(contrasts) != 5 or any(
        item["status"] != "observed_as_expected" for item in contrasts
    ):
        raise AssertionError("development pilot controlled contrast changed")
    if any(
        method["primary_denominator_eligible"]
        for case in cases
        for method in case["methods"]
    ):
        raise AssertionError("development evidence entered primary denominator")


def main() -> int:
    plan = load_report(_PLAN_PATH)
    committed_archive = load_report(_ARCHIVE_PATH)
    committed_valid, committed_errors = verify_development_pilot_archive_document(
        committed_archive,
        plan,
    )
    if not committed_valid:
        raise AssertionError(committed_errors)
    semantic_sha256 = committed_archive["index_semantic_sha256"]

    with tempfile.TemporaryDirectory(
        prefix="deltawitness-development-pilot-smoke-"
    ) as directory:
        root = Path(directory)
        bundle = root / "bundle"
        index = run_development_pilot(plan, bundle)
        bundle_valid, bundle_errors = verify_development_pilot_bundle(bundle, plan)
        if not bundle_valid:
            raise AssertionError(bundle_errors)
        _assert_index(index, semantic_sha256)

        archive = build_development_pilot_archive(bundle, plan)
        archive_valid, archive_errors = verify_development_pilot_archive_document(
            archive,
            plan,
        )
        if not archive_valid:
            raise AssertionError(archive_errors)
        if archive["index_semantic_sha256"] != semantic_sha256:
            raise AssertionError("fresh archive semantic digest changed")

        restored = root / "restored"
        materialize_development_pilot_archive(archive, restored, plan)
        restored_valid, restored_errors = verify_development_pilot_bundle(
            restored,
            plan,
        )
        if not restored_valid:
            raise AssertionError(restored_errors)
        restored_index = load_report(restored / "index.json")
        _assert_index(restored_index, semantic_sha256)

    print(
        "DW-001 complete development pilot smoke passed: "
        f"semantic_sha256={semantic_sha256}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
