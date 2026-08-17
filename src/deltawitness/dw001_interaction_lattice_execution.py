"""Exact execution protocol for the frozen DW-001 interaction lattice.

This protocol does not modify the merged preregistration, whose own execution
fields remain false and ``not_implemented``. It separately authorizes only the
24 exact selector processes over fixed project-owned synthetic candidate and
mutant bytes needed by the result experiment.

The module imports no Coverage.py runtime. It authorizes no external repository,
benchmark, holdout, network measurement, plug-in, upload, score, threshold,
blocker, release, deployment, or production claim.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .coveragepy_contract import (
    COVERAGEPY_MANIFEST_SHA256,
    verify_coveragepy_distribution_manifest_document,
)
from .dw001_interaction_lattice_plan import (
    verify_interaction_witness_lattice_mutant_catalog_document,
    verify_interaction_witness_lattice_plan_document,
)
from .dw001_interaction_lattice_prior_art import (
    verify_interaction_witness_prior_art_log_document,
)
from .errors import DeltaWitnessError
from .reporting import sha256_document


EXECUTION_PROTOCOL_SCHEMA_VERSION = (
    "deltawitness.dw001-interaction-witness-lattice-execution-protocol.v1"
)
EXECUTION_PROTOCOL_ID = (
    "DW-001-INTERACTION-WITNESS-LATTICE-EXECUTION-PROTOCOL-V1"
)
EXECUTION_PROTOCOL_SHA256 = (
    "e10a9e287555ee8a1b8c0a9b7768d2f949c04a70081a778d51fefb78c1276912"
)
PREREGISTRATION_MERGE_COMMIT = (
    "7eef6ffe296081449427ccf550a6bc75a91218c2"
)
PLAN_SHA256 = (
    "a79a500feb94c8ad78fe4633f9ca176465113de6297db2d07b2d005f5318e1f1"
)
CATALOG_SHA256 = (
    "2b06a86180a45fcd495c0bcf39365dde0cb590507e9a3528714f9ef58526308e"
)
PRIOR_ART_LOG_SHA256 = (
    "af6cb9782ea01a0e58baed8cfc1a4895dc1a53ed934498b307c6b05e8634c44f"
)
PR46_RESULT_SEMANTIC_SHA256 = (
    "ec0c2fdd5ac24ba53eb895d9014aab623d2631125b8512ba0e0cbf5105f21ee8"
)
PR46_RESULT_REPORT_SHA256 = (
    "8b248757374ebff4195bad181ad02bc5b0bfc61fa2e21ebf45549686c33d2c41"
)


class DW001InteractionLatticeExecutionError(DeltaWitnessError):
    """Raised when the exact result-execution boundary is inconsistent."""


def _template() -> dict[str, Any]:
    return {
        "schema_version": EXECUTION_PROTOCOL_SCHEMA_VERSION,
        "study_id": "DW-001",
        "protocol_id": EXECUTION_PROTOCOL_ID,
        "status": "pre_result_execution_authorization",
        "partition": "development",
        "preregistration": {
            "merge_commit": PREREGISTRATION_MERGE_COMMIT,
            "plan_path": (
                "research/DW-001/interaction-witness-lattice-plan.v1.json"
            ),
            "plan_sha256": PLAN_SHA256,
            "catalog_path": (
                "research/DW-001/interaction-witness-lattice-mutant-catalog.v1.json"
            ),
            "catalog_sha256": CATALOG_SHA256,
            "prior_art_path": (
                "research/DW-001/interaction-witness-prior-art-log.v1.json"
            ),
            "prior_art_log_sha256": PRIOR_ART_LOG_SHA256,
            "coveragepy_distribution_manifest_sha256": (
                COVERAGEPY_MANIFEST_SHA256
            ),
            "pr46_coveragepy_result_semantic_sha256": (
                PR46_RESULT_SEMANTIC_SHA256
            ),
            "pr46_coveragepy_result_report_sha256": (
                PR46_RESULT_REPORT_SHA256
            ),
        },
        "authorized_inputs": {
            "source_id": "two-condition-authorization-candidate-v1",
            "test_id": "two-condition-authorization-selectors-v1",
            "source_path": "src/access.py",
            "test_path": "tests/test_access.py",
            "source_sha256": (
                "c0e8af980cdc0d304af77ec85222e36cf1d8a3b88bd1e18b0277699a086c0a7b"
            ),
            "test_sha256": (
                "02d1069245ae05a76a128aada50affbbe04c83f40f06ce7f4e7f8dde5cdd4bdc"
            ),
            "target_id": (
                "6b20aa0ad5180288edffc9644e85252a774c2efb0c8ee9a32852b0d0ca50728e"
            ),
            "profile_ids": [
                "diagonal-only-v1",
                "mfa-independence-v1",
                "role-independence-v1",
                "mcdc-basis-v1",
                "full-truth-table-v1",
            ],
            "selector_ids": [
                "d0e63ca6ed765a582585e722bdfae8583dd7c2d8113827d6dfa1d3ef605f0f77",
                "d17f14daa66bb3e9838a00f4442f76d17b87e3cf15263d76740e7f3e153fa35a",
                "954ed2ebe799f5ceab26ab5c7e0c3845a66838752529766c7d80c5d1ae707821",
                "421a9c5cc8bd7b5e04ac12c8883ac054a5520b46cf3678d47c87f0dad3c7465f",
            ],
            "operator_ids": [
                "drop-mfa-conjunct-v1",
                "drop-role-conjunct-v1",
                "or-gates-v1",
                "constant-false-v1",
                "constant-true-v1",
            ],
            "mutant_ids": [
                "7f1fc0a57cfab48ed0ff705c2be3092028fcac436dd4107ec96c7fe8f9be2b66",
                "b0883fa6abfb0118a3b9b860cd3b3f2fe3e9f1f0a16da8c0d3cc33307233d76b",
                "a41ecd03edbc2c006ce94f59d9754a7ab3edd46bbe8dbcc0bdf6f74cd087a1aa",
                "8e120ca1a9cabdeeb68926cee412ea8c4657946d80126e3c847d9751fefeabd7",
                "8374d368675a769b368b980f497025d644cad2518974960ed261ca4577a2bf61",
            ],
        },
        "execution_scope": {
            "fixed_project_owned_synthetic_execution_authorized": True,
            "candidate_selector_commands": 4,
            "mutant_selector_commands": 20,
            "maximum_selector_commands": 24,
            "one_selector_per_child_process": True,
            "shell_allowed": False,
            "disposable_nonsensitive_directories_required": True,
            "reduced_environment_required": True,
            "runner_is_sandbox": False,
            "supported_python_versions": ["3.11", "3.12", "3.13", "3.14"],
        },
        "coveragepy_contract": {
            "package": "coverage",
            "version": "7.15.2",
            "distribution_manifest_sha256": COVERAGEPY_MANIFEST_SHA256,
            "public_api_only": True,
            "data_file": None,
            "auto_data": False,
            "timid": True,
            "branch": True,
            "config_file": False,
            "source_directory": "explicit_disposable_source_directory",
            "concurrency": None,
            "check_preimported": False,
            "context_strategy": "static-selector-context-v1",
            "messages": False,
            "plugins": [],
            "auto_start": False,
            "subprocess_measurement": False,
            "network_during_measurement": False,
            "raw_coverage_data_publication_allowed": False,
        },
        "prohibited_capabilities": {
            "external_repository_execution": False,
            "benchmark_execution": False,
            "holdout_access": False,
            "private_data": False,
            "secrets": False,
            "credential_bearing_environment": False,
            "untrusted_code": False,
            "network_during_measurement": False,
            "upload": False,
            "telemetry": False,
            "remote_execution_service": False,
            "coveragepy_plugins": False,
            "coveragepy_auto_start": False,
            "coveragepy_subprocess_measurement": False,
            "coveragepy_concurrency_adapter": False,
            "persistent_coverage_data": False,
            "release": False,
            "deployment": False,
            "main_ruleset": False,
        },
        "result_contract": {
            "result_schema_version": (
                "deltawitness.dw001-interaction-witness-lattice-result.v1"
            ),
            "candidate_and_mutant_tables_before_summary": True,
            "complete_divergence_status": "unexpected",
            "missing_or_ambiguous_status": "indeterminate",
            "measured_empty_distinct_from_unavailable": True,
            "anonymous_path_multiplicity": "multiset",
            "hit_count_magnitude_used": False,
            "independent_semantic_reconstruction_required": True,
            "semantic_digest_required": True,
            "complete_report_digest_required": True,
        },
        "policy": {
            "quality_score": None,
            "headline_score": None,
            "universal_threshold": None,
            "merge_blocker_authorized": False,
            "ecological_inference_allowed": False,
            "holdout_selected": False,
            "primary_denominator_eligible": False,
            "mcdc_certification_claim_allowed": False,
            "coverage_superiority_claim_allowed": False,
            "mutation_superiority_claim_allowed": False,
            "method_superiority_claim_allowed": False,
            "scientific_novelty_claim_allowed": False,
            "award_level_significance_claim_allowed": False,
            "production_readiness_claim_allowed": False,
        },
        "protocol_sha256": None,
    }


def compute_interaction_lattice_execution_protocol_sha256(
    document: dict[str, Any],
) -> str:
    """Hash the complete protocol with its own digest normalized."""

    if not isinstance(document, dict):
        raise DW001InteractionLatticeExecutionError(
            "interaction-lattice execution protocol must be an object"
        )
    normalized = deepcopy(document)
    normalized["protocol_sha256"] = None
    return sha256_document(normalized)


def build_interaction_lattice_execution_protocol() -> dict[str, Any]:
    """Return the exact separately authorized result-execution protocol."""

    document = _template()
    document["protocol_sha256"] = (
        compute_interaction_lattice_execution_protocol_sha256(document)
    )
    return document


def _differences(
    expected: object,
    observed: object,
    *,
    context: str,
) -> list[str]:
    if type(expected) is not type(observed):
        return [f"{context}: type mismatch"]
    if isinstance(expected, dict):
        assert isinstance(observed, dict)
        errors: list[str] = []
        expected_keys = set(expected)
        observed_keys = set(observed)
        if expected_keys != observed_keys:
            errors.append(
                f"{context}: field mismatch; "
                f"missing={sorted(expected_keys - observed_keys)}, "
                f"extra={sorted(observed_keys - expected_keys)}"
            )
        for key in sorted(expected_keys & observed_keys):
            errors.extend(
                _differences(
                    expected[key],
                    observed[key],
                    context=f"{context}.{key}",
                )
            )
        return errors
    if isinstance(expected, list):
        assert isinstance(observed, list)
        errors = []
        if len(expected) != len(observed):
            errors.append(
                f"{context}: length mismatch; expected {len(expected)}, "
                f"observed {len(observed)}"
            )
        for index, (left, right) in enumerate(
            zip(expected, observed, strict=False)
        ):
            errors.extend(
                _differences(
                    left,
                    right,
                    context=f"{context}[{index}]",
                )
            )
        return errors
    if expected != observed:
        return [
            f"{context}: expected={expected!r}, observed={observed!r}"
        ]
    return []


def verify_interaction_lattice_execution_protocol_document(
    document: object,
    plan: object,
    catalog: object,
    prior_art: object,
    coveragepy_manifest: object,
    pr46_result: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify the protocol and all exact source-artifact bindings."""

    errors: list[str] = []
    plan_valid, plan_errors = verify_interaction_witness_lattice_plan_document(
        plan
    )
    if not plan_valid:
        errors.extend(
            f"execution protocol plan: {error}" for error in plan_errors
        )
    catalog_valid, catalog_errors = (
        verify_interaction_witness_lattice_mutant_catalog_document(
            catalog,
            plan,
        )
    )
    if not catalog_valid:
        errors.extend(
            f"execution protocol catalog: {error}"
            for error in catalog_errors
        )
    prior_art_valid, prior_art_errors = (
        verify_interaction_witness_prior_art_log_document(prior_art)
    )
    if not prior_art_valid:
        errors.extend(
            f"execution protocol prior art: {error}"
            for error in prior_art_errors
        )
    manifest_valid, manifest_errors = (
        verify_coveragepy_distribution_manifest_document(coveragepy_manifest)
    )
    if not manifest_valid:
        errors.extend(
            f"execution protocol Coverage.py manifest: {error}"
            for error in manifest_errors
        )

    if not isinstance(plan, dict):
        errors.append("execution protocol plan: must be an object")
    else:
        if plan.get("execution_authorized") is not False:
            errors.append(
                "execution protocol plan.execution_authorized: must remain false"
            )
        future = plan.get("future_execution_contract")
        if (
            not isinstance(future, dict)
            or future.get("execution_status") != "not_implemented"
        ):
            errors.append(
                "execution protocol preregistration execution status changed"
            )
        if plan.get("plan_sha256") != PLAN_SHA256:
            errors.append("execution protocol plan identity mismatch")

    if not isinstance(catalog, dict) or catalog.get("catalog_sha256") != (
        CATALOG_SHA256
    ):
        errors.append("execution protocol catalog identity mismatch")
    if not isinstance(prior_art, dict) or prior_art.get("log_sha256") != (
        PRIOR_ART_LOG_SHA256
    ):
        errors.append("execution protocol prior-art identity mismatch")
    if (
        not isinstance(coveragepy_manifest, dict)
        or coveragepy_manifest.get("manifest_sha256")
        != COVERAGEPY_MANIFEST_SHA256
    ):
        errors.append("execution protocol Coverage.py manifest identity mismatch")
    if not isinstance(pr46_result, dict):
        errors.append("execution protocol PR #46 result: must be an object")
    else:
        if pr46_result.get("semantic_sha256") != (
            PR46_RESULT_SEMANTIC_SHA256
        ):
            errors.append("execution protocol PR #46 semantic identity mismatch")
        if pr46_result.get("report_sha256") != PR46_RESULT_REPORT_SHA256:
            errors.append("execution protocol PR #46 report identity mismatch")
        if pr46_result.get("distribution_manifest_sha256") != (
            COVERAGEPY_MANIFEST_SHA256
        ):
            errors.append(
                "execution protocol PR #46 distribution identity mismatch"
            )

    if not isinstance(document, dict):
        errors.append("interaction-lattice execution protocol: must be an object")
        return False, tuple(dict.fromkeys(errors))

    expected = build_interaction_lattice_execution_protocol()
    errors.extend(
        _differences(
            expected,
            document,
            context="interaction-lattice execution protocol",
        )
    )
    try:
        computed = compute_interaction_lattice_execution_protocol_sha256(
            document
        )
    except DW001InteractionLatticeExecutionError as exc:
        errors.append(str(exc))
    else:
        if document.get("protocol_sha256") != computed:
            errors.append(
                "interaction-lattice execution protocol.protocol_sha256: "
                "digest mismatch"
            )
        if computed != EXECUTION_PROTOCOL_SHA256:
            errors.append(
                "interaction-lattice execution protocol.protocol_sha256: "
                "does not match the reviewed protocol"
            )

    unique = tuple(dict.fromkeys(errors))
    return not unique, unique


__all__ = [
    "DW001InteractionLatticeExecutionError",
    "EXECUTION_PROTOCOL_ID",
    "EXECUTION_PROTOCOL_SCHEMA_VERSION",
    "EXECUTION_PROTOCOL_SHA256",
    "PREREGISTRATION_MERGE_COMMIT",
    "build_interaction_lattice_execution_protocol",
    "compute_interaction_lattice_execution_protocol_sha256",
    "verify_interaction_lattice_execution_protocol_document",
]
