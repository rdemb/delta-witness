from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import tempfile
from typing import Iterator

from deltawitness.config import WitnessConfig, load_config
from deltawitness.dw001_scenarios import (
    build_fixture_descriptor,
    materialize_synthetic_fixture,
    verify_fixture_identity_document,
    verify_materialized_fixture,
)
from deltawitness.matrix import report_to_dict, verify_repository


CLAIM_ID = "role-check-regression"
VALID_SELECTOR = "test_access.AccessTests.test_viewer_is_denied"
UNRELATED_SELECTOR = "test_access.AccessTests.test_viewer_result_is_boolean"
COLLATERAL_SELECTOR = "test_access.AccessTests.test_version_label_is_v2"
IMPORT_SELECTOR = "test_access.AccessTests.test_role_is_normalized"
MISSING_SELECTOR = "test_access.AccessTests.test_missing_selector"


@contextmanager
def fixture_case(
    family_id: str,
    *,
    observer: str = "outcome-receipt-v1",
    scenario_id: str | None = None,
) -> Iterator[tuple[Path, WitnessConfig, dict[str, object], dict[str, object]]]:
    descriptor = build_fixture_descriptor(
        scenario_id=scenario_id or f"claim-witness-{family_id}-{observer}",
        family_id=family_id,
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
        config = load_config(repository / identity["specification"]["path"])
        report = verify_repository(
            repository,
            identity["git"]["base_commit_sha"],
            identity["git"]["head_commit_sha"],
            config,
        )
        yield repository, config, report_to_dict(report), descriptor
