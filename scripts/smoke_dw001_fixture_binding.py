#!/usr/bin/env python3
"""Exercise the packaged DW-001 fixture-to-manifest binding API.

This smoke test uses only project-owned synthetic bytes and a temporary
repository. It does not authorize a development pilot or held-out execution.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import tempfile

from deltawitness.dw001_contracts import (
    SCENARIO_SCHEMA_VERSION,
    STUDY_ID,
    seal_scenario_manifest,
)
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


def _manifest(
    descriptor: dict[str, object],
    identity: dict[str, object],
) -> dict[str, object]:
    observer_id = descriptor["observer_id"]
    states = [
        {
            "state": state["state"],
            "applicable": state["applicable"],
            "applicability_reason": None,
            "expected_observed": state["expected_observed"],
            "failure_cause": state["failure_cause"],
        }
        for state in descriptor["expected_states"]  # type: ignore[index]
    ]
    methods = [
        {
            "method_id": method["method_id"],
            "observer_id": observer_id,
            "combined_method_id": f"{method['method_id']}__{observer_id}",
            "expected_decision": method["decision"],
            "reason_code": method["reason_code"],
            "primary_denominator_eligible": False,
        }
        for method in descriptor["expected_methods"]  # type: ignore[index]
    ]
    git_identity = identity["git"]  # type: ignore[index]
    return seal_scenario_manifest(
        {
            "schema_version": SCENARIO_SCHEMA_VERSION,
            "study_id": STUDY_ID,
            "scenario_id": descriptor["scenario_id"],
            "partition": "development",
            "partition_lock": {
                "status": "development_uncommitted",
                "commitment_sha256": None,
                "commitment_scope": None,
            },
            "provenance": {
                "source_type": "synthetic",
                "source_id": f"synthetic/{descriptor['family_id']}",
                "license_expression": None,
                "authorization_basis": "owned_synthetic_fixture",
                "authorization_reference": None,
                "public_release_allowed": True,
            },
            "git": {
                "repository_id": "synthetic-dw001-fixture",
                "base_sha": git_identity["base_commit_sha"],
                "head_sha": git_identity["head_commit_sha"],
            },
            "paths": deepcopy(identity["paths"]),
            "execution": {
                "command": deepcopy(descriptor["command"]),
                "observer": descriptor["observer"],
                "observer_id": observer_id,
                "timeout_seconds": descriptor["timeout_seconds"],
                "pass_exit_codes": [0],
                "fail_exit_codes": [1],
                "pass_env": [],
                "environment_requirements": ["CPython 3.11 or later", "Git"],
            },
            "ground_truth": {
                "states": states,
                "methods": methods,
                "false_assurance_mechanism": descriptor["family_id"],
                "environment_assumptions": [
                    "The owned synthetic fixture is deterministic.",
                    "No external service is required.",
                ],
            },
            "review": {
                "status": "approved",
                "reviewers": [
                    {
                        "reviewer_id": "synthetic-reviewer-001",
                        "role": "ground_truth_reviewer",
                        "independent_of_scenario_author": True,
                        "independent_of_implementation": True,
                        "decision": "approve",
                        "rationale": (
                            "Expected states are fixed by the owned synthetic "
                            "fixture family."
                        ),
                    }
                ],
            },
            "manifest_sha256": None,
        }
    )


def main() -> int:
    descriptor = build_fixture_descriptor(
        scenario_id="ci-fixture-binding-smoke-001",
        family_id="valid-discriminating-regression",
    )
    with tempfile.TemporaryDirectory() as directory:
        destination = Path(directory)
        identity = materialize_synthetic_fixture(descriptor, destination)
        identity_valid, identity_errors = verify_fixture_identity_document(
            identity,
            descriptor,
        )
        materialized_valid, materialized_errors = verify_materialized_fixture(
            identity,
            descriptor,
            destination,
        )
        if not identity_valid:
            raise AssertionError(identity_errors)
        if not materialized_valid:
            raise AssertionError(materialized_errors)

    manifest = _manifest(descriptor, identity)
    binding = build_fixture_manifest_binding(descriptor, identity, manifest)
    valid, errors = verify_fixture_manifest_binding_document(
        binding,
        descriptor,
        identity,
        manifest,
    )
    if not valid:
        raise AssertionError(errors)
    if any(
        method["primary_denominator_eligible"]
        for method in manifest["ground_truth"]["methods"]  # type: ignore[index]
    ):
        raise AssertionError("development manifest became denominator eligible")

    print("DW-001 fixture-manifest binding smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
