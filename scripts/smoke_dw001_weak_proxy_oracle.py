#!/usr/bin/env python3
"""Exercise the packaged DW-001 weak-proxy-oracle challenge end to end.

The smoke uses only fixed project-owned source, test, prompt, and mutant bytes.
It demonstrates one development-only limitation: a genuine typed and localized
fail-to-pass selector can remain too weak to reject a fixed claim-violating
mutant. It is not an ecological agent evaluation or a general mutation score.
"""

from __future__ import annotations

from pathlib import Path
import tempfile

from deltawitness.claim_witness import (
    build_claim_witness_declaration,
    run_claim_witness_localization,
    verify_claim_witness_localization_document,
)
from deltawitness.config import load_config
from deltawitness.dw001 import project_baselines, verify_projection_document
from deltawitness.dw001_fixture_binding import (
    build_fixture_manifest_binding,
    verify_fixture_manifest_binding_document,
)
from deltawitness.dw001_oracle_challenge import (
    DECLARED_SELECTOR,
    FAMILY_ID,
    run_weak_proxy_oracle_challenge,
    verify_weak_oracle_challenge_document,
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


_SCENARIO_ID = "ci-weak-proxy-oracle-001"


def main() -> int:
    descriptor = build_fixture_descriptor(
        scenario_id=_SCENARIO_ID,
        family_id=FAMILY_ID,
        observer="outcome-receipt-v1",
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

        config = load_config(repository / identity["specification"]["path"])
        report_object = verify_repository(
            repository,
            identity["git"]["base_commit_sha"],
            identity["git"]["head_commit_sha"],
            config,
        )
        report_path = (
            repository / ".git" / "deltawitness" / "weak-proxy-oracle.json"
        )
        write_report(report_object, report_path)
        report = load_report(report_path)
        report_valid, report_errors = verify_report_document(report)
        if not report_valid:
            raise AssertionError(report_errors)

        projection = project_baselines(report, scenario_id=_SCENARIO_ID)
        projection_valid, projection_errors = verify_projection_document(projection)
        if not projection_valid:
            raise AssertionError(projection_errors)

        declaration = build_claim_witness_declaration(
            spec_sha256=config.digest_sha256,
            claim_id="role-check-regression",
            selectors=[DECLARED_SELECTOR],
        )
        localization = run_claim_witness_localization(
            repository,
            config,
            report,
            declaration,
        )
        localization_valid, localization_errors = (
            verify_claim_witness_localization_document(
                localization,
                declaration,
                report,
            )
        )
        if not localization_valid:
            raise AssertionError(localization_errors)

        challenge = run_weak_proxy_oracle_challenge(
            descriptor,
            identity,
            report,
            projection,
            declaration,
            localization,
        )
        challenge_valid, challenge_errors = verify_weak_oracle_challenge_document(
            challenge,
            descriptor,
            identity,
            report,
            projection,
            declaration,
            localization,
        )
        if not challenge_valid:
            raise AssertionError(challenge_errors)

    if not report["complete"] or not report["supported"]:
        raise AssertionError("weak-proxy fixture lost its canonical witness")
    if [method["decision"] for method in projection["methods"]] != [
        "accept",
        "accept",
        "accept",
        "accept",
    ]:
        raise AssertionError("nested method decisions changed")
    if localization["aggregate_status"] != "supported":
        raise AssertionError("declared selector is no longer supported")
    if localization["selectors"][0]["classification"] != "discriminating":
        raise AssertionError("declared selector is no longer fail-to-pass")

    observed = {
        (item["implementation"], item["test_role"]): item["observed"]
        for item in challenge["controlled_executions"]
    }
    if observed != {
        ("base", "declared_selector"): "fail",
        ("candidate", "declared_selector"): "pass",
        ("mutant", "declared_selector"): "pass",
        ("candidate", "hidden_claim"): "pass",
        ("mutant", "hidden_claim"): "fail",
    }:
        raise AssertionError("fixed weak-oracle control outcomes changed")
    if challenge["finding"] != {
        "declared_selector_discriminates_base_candidate": True,
        "mutant_survives_declared_selector": True,
        "mutant_violates_hidden_claim": True,
        "weak_oracle_exposed": True,
        "primary_denominator_eligible": False,
    }:
        raise AssertionError("weak-oracle finding changed")

    print(
        "DW-001 weak-proxy-oracle smoke passed: "
        f"challenge_sha256={challenge['challenge_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
