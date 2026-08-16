#!/usr/bin/env python3
"""Exercise installed declared logical-test witness localization end to end.

The smoke uses only fixed project-owned synthetic fixtures. It validates one
positive selector, the unrelated-assertion mismatch, its collateral selector,
and import-error indeterminacy. This is packaging evidence, not an independent
reproduction or an oracle-relevance proof.
"""

from __future__ import annotations

from pathlib import Path
import tempfile

from deltawitness.claim_witness import (
    build_claim_witness_declaration,
    run_claim_witness_localization,
    verify_claim_witness_declaration_document,
    verify_claim_witness_localization_document,
)
from deltawitness.config import load_config
from deltawitness.dw001_scenarios import (
    build_fixture_descriptor,
    materialize_synthetic_fixture,
    verify_fixture_identity_document,
    verify_materialized_fixture,
)
from deltawitness.matrix import verify_repository, write_report
from deltawitness.reporting import load_report, verify_report_document


_CLAIM_ID = "role-check-regression"
_VALID_SELECTOR = "test_access.AccessTests.test_viewer_is_denied"
_UNRELATED_SELECTOR = "test_access.AccessTests.test_viewer_result_is_boolean"
_COLLATERAL_SELECTOR = "test_access.AccessTests.test_version_label_is_v2"
_IMPORT_SELECTOR = "test_access.AccessTests.test_role_is_normalized"


def _run(
    *,
    family_id: str,
    selector: str,
) -> tuple[dict[str, object], dict[str, object]]:
    descriptor = build_fixture_descriptor(
        scenario_id=f"ci-claim-witness-{family_id}",
        family_id=family_id,
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

        config = load_config(repository / identity["specification"]["path"])
        report = verify_repository(
            repository,
            identity["git"]["base_commit_sha"],
            identity["git"]["head_commit_sha"],
            config,
        )
        report_path = repository / ".git" / "deltawitness" / "claim-witness-source.json"
        write_report(report, report_path)
        source_report = load_report(report_path)
        report_valid, report_errors = verify_report_document(source_report)
        if not report_valid:
            raise AssertionError(report_errors)

        declaration = build_claim_witness_declaration(
            spec_sha256=config.digest_sha256,
            claim_id=_CLAIM_ID,
            selectors=[selector],
        )
        declaration_valid, declaration_errors = (
            verify_claim_witness_declaration_document(declaration)
        )
        if not declaration_valid:
            raise AssertionError(declaration_errors)
        localization = run_claim_witness_localization(
            repository,
            config,
            source_report,
            declaration,
        )
        localization_valid, localization_errors = (
            verify_claim_witness_localization_document(
                localization,
                declaration,
                source_report,
            )
        )
        if not localization_valid:
            raise AssertionError(localization_errors)

    return source_report, localization


def _state(localization: dict[str, object], state_name: str) -> dict[str, object]:
    selector_result = localization["selectors"][0]
    return next(
        state
        for state in selector_result["states"]
        if state["state"] == state_name
    )


def main() -> int:
    valid_source, valid = _run(
        family_id="valid-discriminating-regression",
        selector=_VALID_SELECTOR,
    )
    if not valid_source["supported"]:
        raise AssertionError("valid broad suite is not supported")
    if valid["aggregate_status"] != "supported":
        raise AssertionError("valid declared selector is not supported")
    if valid["selectors"][0]["classification"] != "discriminating":
        raise AssertionError("valid declared selector is not discriminating")

    unrelated_source, unrelated = _run(
        family_id="wrong-reason-unrelated-assertion",
        selector=_UNRELATED_SELECTOR,
    )
    if not unrelated_source["supported"]:
        raise AssertionError("unrelated broad suite lost its canonical witness")
    if unrelated["aggregate_status"] != "unsupported":
        raise AssertionError("claim-facing unrelated selector was not rejected")
    if unrelated["selectors"][0]["classification"] != "non_discriminating":
        raise AssertionError("claim-facing selector was not classified pass-to-pass")

    _, collateral = _run(
        family_id="wrong-reason-unrelated-assertion",
        selector=_COLLATERAL_SELECTOR,
    )
    if collateral["aggregate_status"] != "supported":
        raise AssertionError("collateral selector did not remain separately discriminating")
    if collateral["selectors"][0]["classification"] != "discriminating":
        raise AssertionError("collateral selector classification changed")

    import_source, import_localization = _run(
        family_id="wrong-reason-base-import-failure",
        selector=_IMPORT_SELECTOR,
    )
    if import_source["complete"] or import_source["supported"]:
        raise AssertionError("typed import-error broad suite became complete evidence")
    if import_localization["aggregate_status"] != "indeterminate":
        raise AssertionError("import-error selector was not preserved as indeterminate")
    if import_localization["selectors"][0]["classification"] != "indeterminate":
        raise AssertionError("import-error selector classification changed")
    if _state(import_localization, "base_candidate")["observed"] != "error":
        raise AssertionError("import-error BC state was not preserved as error")

    for artifact in (valid, unrelated, collateral, import_localization):
        for selector_result in artifact["selectors"]:
            for state in selector_result["states"]:
                if state["stdout"] is not None or state["stderr"] is not None:
                    raise AssertionError("raw output leaked into localization report")
                counts = state["receipt_counts"]
                if counts is not None and state["receipt_outcome"] != "producer_error":
                    if counts["tests_run"] != 1:
                        raise AssertionError("exact selector did not cover one logical test")

    print("DeltaWitness claim witness localization smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
