from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import tempfile

from deltawitness.dw001_contracts import (
    SCENARIO_SCHEMA_VERSION,
    STUDY_ID,
    compute_scenario_manifest_sha256,
    seal_scenario_manifest,
)
from deltawitness.dw001_scenarios import (
    build_fixture_descriptor,
    materialize_synthetic_fixture,
)


SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "DW-001"
    / "schema"
    / "fixture-manifest-binding.schema.json"
)


def manifest_from_fixture(
    descriptor: dict[str, object],
    identity: dict[str, object],
    *,
    partition: str = "development",
) -> dict[str, object]:
    holdout = partition == "holdout"
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
            "primary_denominator_eligible": holdout,
        }
        for method in descriptor["expected_methods"]  # type: ignore[index]
    ]
    git_identity = identity["git"]  # type: ignore[index]
    return seal_scenario_manifest(
        {
            "schema_version": SCENARIO_SCHEMA_VERSION,
            "study_id": STUDY_ID,
            "scenario_id": descriptor["scenario_id"],
            "partition": partition,
            "partition_lock": {
                "status": "holdout_committed" if holdout else "development_uncommitted",
                "commitment_sha256": "a" * 64 if holdout else None,
                "commitment_scope": "dw001-holdout-index-v1" if holdout else None,
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
                "false_assurance_mechanism": str(descriptor["family_id"]),
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
                        "rationale": "Expected states are fixed by the owned synthetic fixture family.",
                    }
                ],
            },
            "manifest_sha256": None,
        }
    )


def artifacts(
    *,
    scenario_id: str = "fixture-binding-001",
    family_id: str = "valid-discriminating-regression",
    observer: str = "outcome-receipt-v1",
    partition: str = "development",
) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    descriptor = build_fixture_descriptor(
        scenario_id=scenario_id,
        family_id=family_id,
        observer=observer,
    )
    with tempfile.TemporaryDirectory() as directory:
        identity = materialize_synthetic_fixture(descriptor, Path(directory))
    manifest = manifest_from_fixture(descriptor, identity, partition=partition)
    return descriptor, identity, manifest


def resign_manifest(manifest: dict[str, object]) -> None:
    manifest["manifest_sha256"] = compute_scenario_manifest_sha256(manifest)
