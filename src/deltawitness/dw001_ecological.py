"""Design-only DW-001 ecological source-universe contract.

The artifact records initial benchmark source candidates and unresolved review
boundaries. It deliberately cannot authorize execution, freeze a sampling
frame, select or inspect a holdout, or infer that a repository-level license
covers every dataset instance and transitive repository artifact.
"""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Any

from .dw001 import STUDY_ID
from .errors import DeltaWitnessError
from .reporting import sha256_document


SOURCE_UNIVERSE_SCHEMA_VERSION = (
    "deltawitness.dw001-ecological-source-universe.v1"
)
DESIGN_ID = "DW-001-ECOLOGICAL-DESIGN-V1"

_GIT_SHA = re.compile(r"[0-9a-f]{40}\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_ROOT_FIELDS = {
    "schema_version",
    "study_id",
    "design_id",
    "status",
    "reviewed_main_sha",
    "sources",
    "decisions",
    "execution_authorized",
    "holdout_selected",
    "holdout_inspected",
    "universe_sha256",
}

_SOURCES: tuple[dict[str, object], ...] = (
    {
        "order": 1,
        "source_id": "swe-bench",
        "source_type": "public_benchmark_candidate",
        "repository": "SWE-bench/SWE-bench",
        "repository_commit_sha": "ca6e4e0d252f32f8762625b73575d5dee49d0a5a",
        "repository_license_spdx": "MIT",
        "paper_reference": "arXiv:2310.06770",
        "artifact_scope": [
            "issue_text",
            "repository_identity",
            "base_commit",
            "gold_patch",
            "test_patch",
            "FAIL_TO_PASS",
            "PASS_TO_PASS",
            "environment_metadata",
        ],
        "target_population_relation": (
            "Curated real-world GitHub issue-resolution benchmark; relation to "
            "coding-agent patches generally is not established."
        ),
        "dataset_reference_status": "unpinned",
        "license_review_status": "repository_reviewed_instances_pending",
        "authorization_review_status": "pending",
        "environment_feasibility": "unreviewed",
        "containment_status": "unaccepted",
        "execution_authorized": False,
        "known_biases": [
            "benchmark curation and solvability filtering",
            "repository and issue-selection bias",
            "Python-project concentration",
            "human gold-patch and test provenance",
            "repository and issue-lineage clustering",
            "benchmark contamination and memorization risk",
        ],
        "blocking_questions": [
            "Pin one immutable dataset release and digest rather than repository main.",
            "Review every selected instance repository license and test/patch provenance.",
            "Define authorization for executing historical repository code and tests.",
            "Accept a disposable containment profile before any instance execution.",
            "Define environment reconstruction and uncontrolled-network policy.",
            "Define repository-clustered sampling and development/holdout leakage controls.",
        ],
    },
    {
        "order": 2,
        "source_id": "tdd-bench-verified",
        "source_type": "public_benchmark_candidate",
        "repository": "IBM/TDD-Bench-Verified",
        "repository_commit_sha": "3df8be066e486789d0b8e0d2865a3a4422b4560f",
        "repository_license_spdx": "Apache-2.0",
        "paper_reference": "arXiv:2412.02883",
        "artifact_scope": [
            "issue_text",
            "repository_identity",
            "base_commit",
            "gold_patch",
            "generated_or_gold_test_patch",
            "fail_to_pass_evidence",
            "isolated_relevant_test_execution",
            "change_coverage_metadata",
        ],
        "target_population_relation": (
            "Human-filtered test-generation benchmark derived from real issues; "
            "relation to deployed coding-agent patch workflows is not established."
        ),
        "dataset_reference_status": "unpinned",
        "license_review_status": "repository_reviewed_instances_pending",
        "authorization_review_status": "pending",
        "environment_feasibility": "unreviewed",
        "containment_status": "unaccepted",
        "execution_authorized": False,
        "known_biases": [
            "human verification and benchmark inclusion filtering",
            "focus on test generation before issue resolution",
            "source-benchmark and language composition constraints",
            "gold-patch and generated-test provenance heterogeneity",
            "repository and issue-lineage clustering",
            "coverage and relevant-test harness selection effects",
        ],
        "blocking_questions": [
            "Pin one immutable dataset artifact and digest, not only repository code.",
            "Review licenses and authorization for every underlying project instance.",
            "Separate human-authored, generated, transformed, and uncertain test provenance.",
            "Map isolated relevant-test semantics to DW-001 claims without relabeling outcomes.",
            "Accept containment and environment reconstruction before execution.",
            "Define whether the benchmark can support patch-method inference or only test-generation inference.",
        ],
    },
)

_DECISIONS = {
    "candidate_sources_only": True,
    "target_population_status": "unfrozen",
    "sampling_frame_status": "unfrozen",
    "unit_of_analysis_status": "unfrozen",
    "license_and_authorization_status": "pending",
    "review_protocol_status": "unfrozen",
    "containment_required": True,
    "containment_status": "unaccepted",
    "precision_target_status": "unfrozen",
    "development_holdout_split_status": "unfrozen",
    "no_ecological_execution": True,
    "no_holdout_selection": True,
    "no_holdout_inspection": True,
}


class DW001EcologicalError(DeltaWitnessError):
    """Raised when ecological design metadata is unsafe or inconsistent."""


def _error(context: str, message: str) -> DW001EcologicalError:
    return DW001EcologicalError(f"{context}: {message}")


def _git_sha(value: object, *, context: str) -> str:
    if not isinstance(value, str) or _GIT_SHA.fullmatch(value) is None:
        raise _error(context, "must be exactly 40 lowercase hexadecimal characters")
    return value


def _sha256(value: object, *, context: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise _error(context, "must be exactly 64 lowercase hexadecimal characters")
    return value


def compute_ecological_source_universe_sha256(
    document: dict[str, Any],
) -> str:
    """Hash canonical universe bytes with its own digest normalized to null."""

    if not isinstance(document, dict):
        raise _error("ecological source universe", "must be an object")
    normalized = deepcopy(document)
    normalized["universe_sha256"] = None
    return sha256_document(normalized)


def build_ecological_source_universe(
    *,
    reviewed_main_sha: str,
) -> dict[str, Any]:
    """Build the exact design-only initial source universe."""

    main_sha = _git_sha(
        reviewed_main_sha,
        context="ecological source universe.reviewed_main_sha",
    )
    universe: dict[str, Any] = {
        "schema_version": SOURCE_UNIVERSE_SCHEMA_VERSION,
        "study_id": STUDY_ID,
        "design_id": DESIGN_ID,
        "status": "design_only",
        "reviewed_main_sha": main_sha,
        "sources": deepcopy(list(_SOURCES)),
        "decisions": deepcopy(_DECISIONS),
        "execution_authorized": False,
        "holdout_selected": False,
        "holdout_inspected": False,
        "universe_sha256": None,
    }
    universe["universe_sha256"] = compute_ecological_source_universe_sha256(
        universe
    )
    return universe


def _differences(
    expected: object,
    observed: object,
    *,
    context: str,
) -> list[str]:
    errors: list[str] = []
    if isinstance(expected, dict):
        if not isinstance(observed, dict):
            return [f"{context}: must be an object matching the canonical design"]
        expected_keys = set(expected)
        observed_keys = set(observed)
        if expected_keys != observed_keys:
            errors.append(
                f"{context}: field mismatch; missing={sorted(expected_keys - observed_keys)}, "
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
        if not isinstance(observed, list):
            return [f"{context}: must be a list matching the canonical design"]
        if len(expected) != len(observed):
            errors.append(
                f"{context}: length mismatch; expected {len(expected)}, observed {len(observed)}"
            )
        for index, (expected_item, observed_item) in enumerate(
            zip(expected, observed, strict=False)
        ):
            errors.extend(
                _differences(
                    expected_item,
                    observed_item,
                    context=f"{context}[{index}]",
                )
            )
        return errors
    if observed != expected:
        errors.append(
            f"{context}: does not match canonical design; "
            f"expected={expected!r}, observed={observed!r}"
        )
    return errors


def verify_ecological_source_universe_document(
    document: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify exact structure, digest, and reconstruction from fixed review data."""

    try:
        if not isinstance(document, dict):
            raise _error("ecological source universe", "must be an object")
        actual_fields = set(document)
        if actual_fields != _ROOT_FIELDS:
            raise _error(
                "ecological source universe",
                f"field mismatch; missing={sorted(_ROOT_FIELDS - actual_fields)}, "
                f"extra={sorted(actual_fields - _ROOT_FIELDS)}",
            )
        main_sha = _git_sha(
            document["reviewed_main_sha"],
            context="ecological source universe.reviewed_main_sha",
        )
        recorded = _sha256(
            document["universe_sha256"],
            context="ecological source universe.universe_sha256",
        )
        computed = compute_ecological_source_universe_sha256(document)
        expected = build_ecological_source_universe(reviewed_main_sha=main_sha)
    except (
        DW001EcologicalError,
        DeltaWitnessError,
        KeyError,
        TypeError,
        IndexError,
        ValueError,
        OverflowError,
    ) as exc:
        if isinstance(exc, DW001EcologicalError):
            return False, (str(exc),)
        return False, (
            "ecological source universe: verification failed closed: "
            f"{type(exc).__name__}: {exc}",
        )

    errors: list[str] = []
    if recorded != computed:
        errors.append(
            "ecological source universe.universe_sha256: digest mismatch; "
            f"expected {recorded}, computed {computed}"
        )
    errors.extend(
        _differences(
            expected,
            document,
            context="ecological source universe",
        )
    )
    unique = tuple(dict.fromkeys(errors))
    return not unique, unique


__all__ = [
    "DESIGN_ID",
    "SOURCE_UNIVERSE_SCHEMA_VERSION",
    "DW001EcologicalError",
    "build_ecological_source_universe",
    "compute_ecological_source_universe_sha256",
    "verify_ecological_source_universe_document",
]
