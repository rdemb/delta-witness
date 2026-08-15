"""Exact file-path intervention analysis for bounded software patches."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from fractions import Fraction
import json
from math import factorial
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

from . import __version__
from .config import WitnessConfig
from .errors import VerificationError
from .gitops import (
    PathClassification,
    changed_paths,
    classify_changes,
    create_synthetic_commit,
    ensure_ancestor,
    ensure_clean,
    ensure_supported_entries,
    overlay_paths,
    resolve_ref,
    restore_commit,
    safe_path_label,
    worktree,
    write_tree,
)
from .matrix import VerificationReport, verify_repository
from .observation import CommandResult, run_claim_in_state
from .reporting import (
    compute_influence_sha256,
    compute_report_sha256,
    sha256_document,
)

_MAX_EXACT_CODE_PATHS = 8
_CANONICAL_EXPECTATIONS = {
    "base_base": "pass",
    "base_candidate": "fail",
    "candidate_base": "pass",
    "candidate_candidate": "pass",
}


@dataclass(frozen=True)
class InfluenceClaimResult:
    claim_id: str
    description: str
    observer: str
    command: tuple[str, ...]
    states: tuple[CommandResult, ...]
    complete: bool
    supported: bool


@dataclass(frozen=True)
class CoalitionResult:
    coalition_id: str
    mask: int
    selected_paths: tuple[str, ...]
    implementation_tree_sha: str
    implementation_commit_sha: str
    candidate_tests_tree_sha: str
    candidate_tests_commit_sha: str
    claims: tuple[InfluenceClaimResult, ...]
    complete: bool
    supported: bool
    status: str


@dataclass(frozen=True)
class InfluenceReport:
    schema_version: str
    tool_version: str
    created_at: str
    repository: str
    base_sha: str
    head_sha: str
    spec_path: str
    spec_external: bool
    spec_sha256: str
    execution: dict[str, object]
    classification: dict[str, list[dict[str, str]]]
    intervention: dict[str, object]
    matrix_reference: dict[str, object]
    anchors: tuple[dict[str, object], ...]
    coalitions: tuple[CoalitionResult, ...]
    complete: bool
    anchors_consistent: bool
    attribution_available: bool
    status: str
    metrics: dict[str, object] | None
    influence_sha256: str | None = None
    report_sha256: str | None = None


def _serialize_classification(classification: PathClassification) -> dict[str, list[dict[str, str]]]:
    return {
        "code": [asdict(item) for item in classification.code],
        "tests": [asdict(item) for item in classification.tests],
        "documentation": [asdict(item) for item in classification.documentation],
    }


def _fraction_document(value: Fraction) -> dict[str, object]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "decimal": round(float(value), 12),
    }


def _coalition_id(mask: int, path_count: int) -> str:
    width = max(1, len(str((1 << path_count) - 1)))
    return f"c{mask:0{width}d}"


def _selected_paths(path_order: Sequence[str], mask: int) -> tuple[str, ...]:
    return tuple(path for index, path in enumerate(path_order) if mask & (1 << index))


def _validate_exact_truth_table(
    path_order: Sequence[str],
    supported_by_mask: Mapping[int, bool],
) -> None:
    path_count = len(path_order)
    if not path_count:
        raise ValueError("At least one intervention path is required")
    expected = set(range(1 << path_count))
    if set(supported_by_mask) != expected:
        missing = sorted(expected - set(supported_by_mask))
        extra = sorted(set(supported_by_mask) - expected)
        raise ValueError(f"Truth table is incomplete or out of range; missing={missing}, extra={extra}")
    if not all(isinstance(value, bool) for value in supported_by_mask.values()):
        raise ValueError("Truth-table values must be Booleans")


def compute_exact_influence_metrics(
    path_order: Sequence[str],
    supported_by_mask: Mapping[int, bool],
) -> dict[str, object]:
    """Compute exact coalition metrics without assuming monotonicity."""

    paths = tuple(path_order)
    _validate_exact_truth_table(paths, supported_by_mask)
    path_count = len(paths)
    full_mask = (1 << path_count) - 1
    supported_masks = tuple(mask for mask in range(1 << path_count) if supported_by_mask[mask])

    minimal_masks = tuple(
        mask
        for mask in supported_masks
        if not any(
            other != mask and (other & mask) == other
            for other in supported_masks
        )
    )

    path_metrics: list[dict[str, object]] = []
    total_positive_swings = 0
    total_negative_swings = 0
    shapley_values: list[Fraction] = []
    for index, path in enumerate(paths):
        bit = 1 << index
        positive_swings = 0
        negative_swings = 0
        banzhaf_sum = 0
        shapley = Fraction(0, 1)
        for mask in range(1 << path_count):
            if mask & bit:
                continue
            without = int(supported_by_mask[mask])
            with_path = int(supported_by_mask[mask | bit])
            marginal = with_path - without
            if marginal > 0:
                positive_swings += 1
            elif marginal < 0:
                negative_swings += 1
            banzhaf_sum += marginal
            coalition_size = mask.bit_count()
            weight = Fraction(
                factorial(coalition_size) * factorial(path_count - coalition_size - 1),
                factorial(path_count),
            )
            shapley += weight * marginal

        banzhaf = Fraction(banzhaf_sum, 1 << (path_count - 1))
        shapley_values.append(shapley)
        total_positive_swings += positive_swings
        total_negative_swings += negative_swings
        path_metrics.append(
            {
                "path": path,
                "index": index,
                "bit": bit,
                "full_context_necessary": bool(
                    supported_by_mask[full_mask] and not supported_by_mask[full_mask ^ bit]
                ),
                "standalone_sufficient": bool(supported_by_mask[bit]),
                "globally_necessary": bool(
                    supported_masks and all(mask & bit for mask in supported_masks)
                ),
                "minimal_coalition_memberships": sum(
                    1 for mask in minimal_masks if mask & bit
                ),
                "positive_swings": positive_swings,
                "negative_swings": negative_swings,
                "shapley": _fraction_document(shapley),
                "normalized_banzhaf": _fraction_document(banzhaf),
            }
        )

    pair_interactions: list[dict[str, object]] = []
    if path_count >= 2:
        denominator = 1 << (path_count - 2)
        for first in range(path_count):
            for second in range(first + 1, path_count):
                first_bit = 1 << first
                second_bit = 1 << second
                total = 0
                for mask in range(1 << path_count):
                    if mask & (first_bit | second_bit):
                        continue
                    total += (
                        int(supported_by_mask[mask | first_bit | second_bit])
                        - int(supported_by_mask[mask | first_bit])
                        - int(supported_by_mask[mask | second_bit])
                        + int(supported_by_mask[mask])
                    )
                interaction = Fraction(total, denominator)
                pair_interactions.append(
                    {
                        "paths": [paths[first], paths[second]],
                        "indexes": [first, second],
                        "normalized_banzhaf_interaction": _fraction_document(interaction),
                    }
                )

    minimal_documents = [
        {
            "coalition_id": _coalition_id(mask, path_count),
            "mask": mask,
            "paths": list(_selected_paths(paths, mask)),
            "size": mask.bit_count(),
        }
        for mask in minimal_masks
    ]
    paths_in_any_minimal = {
        path
        for mask in minimal_masks
        for path in _selected_paths(paths, mask)
    }
    mandatory_paths = [
        path
        for index, path in enumerate(paths)
        if supported_masks and all(mask & (1 << index) for mask in supported_masks)
    ]

    truth_table = [
        {
            "mask": mask,
            "supported": supported_by_mask[mask],
        }
        for mask in range(1 << path_count)
    ]
    endpoint_delta = Fraction(
        int(supported_by_mask[full_mask]) - int(supported_by_mask[0]),
        1,
    )
    shapley_sum = sum(shapley_values, Fraction(0, 1))
    return {
        "truth_table_sha256": sha256_document(truth_table),
        "supported_coalition_count": len(supported_masks),
        "coalition_count": 1 << path_count,
        "support_density": _fraction_document(
            Fraction(len(supported_masks), 1 << path_count)
        ),
        "empty_supported": supported_by_mask[0],
        "full_supported": supported_by_mask[full_mask],
        "minimal_supported_coalitions": minimal_documents,
        "mandatory_paths": mandatory_paths,
        "paths_in_no_minimal_coalition": [
            path for path in paths if path not in paths_in_any_minimal
        ],
        "monotone_non_decreasing": total_negative_swings == 0,
        "positive_edge_count": total_positive_swings,
        "negative_edge_count": total_negative_swings,
        "endpoint_delta": _fraction_document(endpoint_delta),
        "shapley_sum": _fraction_document(shapley_sum),
        "shapley_efficiency_residual": _fraction_document(shapley_sum - endpoint_delta),
        "paths": path_metrics,
        "pair_interactions": pair_interactions,
    }


def _validate_canonical_claims(config: WitnessConfig) -> None:
    for claim in config.claims:
        if claim.expectations != _CANONICAL_EXPECTATIONS:
            raise VerificationError(
                f"Exact patch influence currently requires the canonical regression matrix for "
                f"claim {claim.claim_id!r}: {_CANONICAL_EXPECTATIONS}"
            )


def _command_signature(result: CommandResult) -> dict[str, object]:
    return {
        "observed": result.observed,
        "return_code": result.return_code,
        "timed_out": result.timed_out,
        "observer": result.observer,
        "receipt_outcome": result.receipt_outcome,
        "receipt_producer": result.receipt_producer,
        "receipt_counts": result.receipt_counts,
        "observation_error": result.observation_error,
    }


def _matrix_reference(report: VerificationReport) -> dict[str, object]:
    return {
        "schema_version": report.schema_version,
        "witness_sha256": report.witness_sha256,
        "complete": report.complete,
        "supported": report.supported,
        "state_trees": dict(report.state_trees),
        "state_commits": dict(report.state_commits),
        "outcomes": {
            claim.claim_id: {
                state.state: _command_signature(state)
                for state in claim.states
            }
            for claim in report.claims
        },
    }


def _run_coalition(
    *,
    repo: Path,
    worktree_path: Path,
    base_sha: str,
    head_sha: str,
    matrix_report: VerificationReport,
    config: WitnessConfig,
    path_order: Sequence[str],
    documentation_paths: Sequence[str],
    test_paths: Sequence[str],
    mask: int,
    include_output: bool,
) -> CoalitionResult:
    coalition_id = _coalition_id(mask, len(path_order))
    selected_paths = _selected_paths(path_order, mask)
    full_mask = (1 << len(path_order)) - 1

    restore_commit(worktree_path, base_sha)
    if documentation_paths:
        overlay_paths(repo, worktree_path, head_sha, documentation_paths)
    if selected_paths:
        overlay_paths(repo, worktree_path, head_sha, selected_paths)

    implementation_tree = write_tree(worktree_path)
    if mask == full_mask and implementation_tree == matrix_report.state_trees["candidate_base"]:
        implementation_commit = matrix_report.state_commits["candidate_base"]
    elif mask == 0 and not documentation_paths and implementation_tree == matrix_report.state_trees["base_base"]:
        implementation_commit = base_sha
    else:
        implementation_commit = create_synthetic_commit(
            repo,
            implementation_tree,
            base_sha,
            state=f"patch-influence:{coalition_id}:base-tests",
            base_sha=base_sha,
            head_sha=head_sha,
        )

    overlay_paths(repo, worktree_path, head_sha, test_paths)
    candidate_tests_tree = write_tree(worktree_path)
    if mask == full_mask and candidate_tests_tree == matrix_report.state_trees["candidate_candidate"]:
        candidate_tests_commit = head_sha
    elif (
        mask == 0
        and not documentation_paths
        and candidate_tests_tree == matrix_report.state_trees["base_candidate"]
    ):
        candidate_tests_commit = matrix_report.state_commits["base_candidate"]
    else:
        candidate_tests_commit = create_synthetic_commit(
            repo,
            candidate_tests_tree,
            implementation_commit,
            state=f"patch-influence:{coalition_id}:candidate-tests",
            base_sha=base_sha,
            head_sha=head_sha,
        )

    claim_results: list[InfluenceClaimResult] = []
    for claim in config.claims:
        base_result = run_claim_in_state(
            claim,
            state=f"patch-influence:{coalition_id}:base-tests",
            expected="pass",
            cwd=worktree_path,
            tree_sha=implementation_tree,
            commit_sha=implementation_commit,
            config=config,
            include_output=include_output,
        )
        candidate_result = run_claim_in_state(
            claim,
            state=f"patch-influence:{coalition_id}:candidate-tests",
            expected="pass",
            cwd=worktree_path,
            tree_sha=candidate_tests_tree,
            commit_sha=candidate_tests_commit,
            config=config,
            include_output=include_output,
        )
        states = (base_result, candidate_result)
        complete = all(result.observed in {"pass", "fail"} for result in states)
        supported = complete and all(result.observed == "pass" for result in states)
        claim_results.append(
            InfluenceClaimResult(
                claim_id=claim.claim_id,
                description=claim.description,
                observer=claim.observer,
                command=claim.command,
                states=states,
                complete=complete,
                supported=supported,
            )
        )

    complete = all(claim.complete for claim in claim_results)
    supported = complete and all(claim.supported for claim in claim_results)
    status = "supported" if supported else ("unsupported" if complete else "indeterminate")
    return CoalitionResult(
        coalition_id=coalition_id,
        mask=mask,
        selected_paths=selected_paths,
        implementation_tree_sha=implementation_tree,
        implementation_commit_sha=implementation_commit,
        candidate_tests_tree_sha=candidate_tests_tree,
        candidate_tests_commit_sha=candidate_tests_commit,
        claims=tuple(claim_results),
        complete=complete,
        supported=supported,
        status=status,
    )


def _anchor_check(
    *,
    name: str,
    coalition: CoalitionResult,
    world_index: int,
    matrix_report: VerificationReport,
    matrix_state: str,
    coalition_tree: str,
    tree_required: bool,
) -> dict[str, object]:
    matrix_claims = {claim.claim_id: claim for claim in matrix_report.claims}
    mismatched_claims: list[str] = []
    for claim in coalition.claims:
        matrix_claim = matrix_claims[claim.claim_id]
        matrix_result = next(state for state in matrix_claim.states if state.state == matrix_state)
        if _command_signature(claim.states[world_index]) != _command_signature(matrix_result):
            mismatched_claims.append(claim.claim_id)

    tree_match = coalition_tree == matrix_report.state_trees[matrix_state]
    outcomes_match = not mismatched_claims
    consistent = outcomes_match and (tree_match or not tree_required)
    return {
        "name": name,
        "coalition_id": coalition.coalition_id,
        "test_world": "base_tests" if world_index == 0 else "candidate_tests",
        "matrix_state": matrix_state,
        "tree_required": tree_required,
        "tree_match": tree_match,
        "outcomes_match": outcomes_match,
        "mismatched_claims": mismatched_claims,
        "consistent": consistent,
    }


def _build_anchors(
    *,
    coalitions: Sequence[CoalitionResult],
    matrix_report: VerificationReport,
    has_documentation_changes: bool,
) -> tuple[dict[str, object], ...]:
    empty = coalitions[0]
    full = coalitions[-1]
    return (
        _anchor_check(
            name="empty-base-tests",
            coalition=empty,
            world_index=0,
            matrix_report=matrix_report,
            matrix_state="base_base",
            coalition_tree=empty.implementation_tree_sha,
            tree_required=not has_documentation_changes,
        ),
        _anchor_check(
            name="empty-candidate-tests",
            coalition=empty,
            world_index=1,
            matrix_report=matrix_report,
            matrix_state="base_candidate",
            coalition_tree=empty.candidate_tests_tree_sha,
            tree_required=not has_documentation_changes,
        ),
        _anchor_check(
            name="full-base-tests",
            coalition=full,
            world_index=0,
            matrix_report=matrix_report,
            matrix_state="candidate_base",
            coalition_tree=full.implementation_tree_sha,
            tree_required=True,
        ),
        _anchor_check(
            name="full-candidate-tests",
            coalition=full,
            world_index=1,
            matrix_report=matrix_report,
            matrix_state="candidate_candidate",
            coalition_tree=full.candidate_tests_tree_sha,
            tree_required=True,
        ),
    )


def analyze_patch_influence(
    repo: Path,
    base_ref: str,
    head_ref: str,
    config: WitnessConfig,
    *,
    include_output: bool = False,
) -> InfluenceReport:
    """Enumerate every bounded code-path coalition and attribute witness influence."""

    repo = repo.resolve()
    _validate_canonical_claims(config)
    matrix_report = verify_repository(
        repo,
        base_ref,
        head_ref,
        config,
        include_output=include_output,
    )
    if not matrix_report.complete or not matrix_report.supported:
        raise VerificationError(
            "Exact patch influence requires a complete, supported canonical four-state witness"
        )

    ensure_clean(repo)
    base_sha = resolve_ref(repo, base_ref)
    head_sha = resolve_ref(repo, head_ref)
    ensure_ancestor(repo, base_sha, head_sha)
    changes = changed_paths(repo, base_sha, head_sha)
    classification = classify_changes(changes, config.path_policy)
    ensure_supported_entries(repo, base_sha, head_sha, [item.path for item in classification.all])

    path_order = tuple(sorted({item.path for item in classification.code}))
    if len(path_order) > _MAX_EXACT_CODE_PATHS:
        raise VerificationError(
            f"Exact patch influence supports at most {_MAX_EXACT_CODE_PATHS} changed code paths; "
            f"received {len(path_order)}"
        )
    documentation_paths = tuple(sorted({item.path for item in classification.documentation}))
    test_paths = tuple(sorted({item.path for item in classification.tests}))

    coalition_results: list[CoalitionResult] = []
    with worktree(repo, base_sha, "patch-influence") as intervention_worktree:
        for mask in range(1 << len(path_order)):
            coalition_results.append(
                _run_coalition(
                    repo=repo,
                    worktree_path=intervention_worktree,
                    base_sha=base_sha,
                    head_sha=head_sha,
                    matrix_report=matrix_report,
                    config=config,
                    path_order=path_order,
                    documentation_paths=documentation_paths,
                    test_paths=test_paths,
                    mask=mask,
                    include_output=include_output,
                )
            )

    coalitions = tuple(coalition_results)
    anchors = _build_anchors(
        coalitions=coalitions,
        matrix_report=matrix_report,
        has_documentation_changes=bool(documentation_paths),
    )
    complete = all(coalition.complete for coalition in coalitions)
    anchors_consistent = all(bool(anchor["consistent"]) for anchor in anchors)
    empty_supported = coalitions[0].supported
    full_supported = coalitions[-1].supported
    attribution_available = (
        complete
        and anchors_consistent
        and not empty_supported
        and full_supported
    )

    if not complete:
        status = "INCOMPLETE_COALITION_TABLE"
    elif not anchors_consistent:
        status = "ANCHOR_INCONSISTENT"
    elif empty_supported:
        status = "DEGENERATE_EMPTY_COALITION"
    elif not full_supported:
        status = "FULL_COALITION_UNSUPPORTED"
    else:
        status = "ATTRIBUTION_AVAILABLE"

    metrics: dict[str, object] | None = None
    if attribution_available:
        metrics = compute_exact_influence_metrics(
            path_order,
            {coalition.mask: coalition.supported for coalition in coalitions},
        )

    spec_label, spec_external = safe_path_label(config.path, repo)
    report = InfluenceReport(
        schema_version="deltawitness.patch-influence.v1",
        tool_version=__version__,
        created_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        repository=repo.name,
        base_sha=base_sha,
        head_sha=head_sha,
        spec_path=spec_label,
        spec_external=spec_external,
        spec_sha256=config.digest_sha256,
        execution={
            "environment_mode": "sanitized-v1",
            "pass_env": list(config.execution_policy.pass_env),
            "output_included": include_output,
            "sandboxed": False,
            "observer_protocols": sorted({claim.observer for claim in config.claims}),
            "enumeration": "exact-exhaustive",
            "maximum_code_paths": _MAX_EXACT_CODE_PATHS,
        },
        classification=_serialize_classification(classification),
        intervention={
            "unit": "changed-code-path",
            "path_order": list(path_order),
            "path_count": len(path_order),
            "coalition_count": 1 << len(path_order),
            "bit_encoding": "path_order index is the least-significant-bit position",
            "documentation_policy": "candidate-held-constant",
            "candidate_documentation_paths": list(documentation_paths),
            "test_worlds": ["base_tests", "candidate_tests"],
            "monotonicity_assumed": False,
        },
        matrix_reference=_matrix_reference(matrix_report),
        anchors=anchors,
        coalitions=coalitions,
        complete=complete,
        anchors_consistent=anchors_consistent,
        attribution_available=attribution_available,
        status=status,
        metrics=metrics,
        influence_sha256=None,
        report_sha256=None,
    )

    raw = influence_report_to_dict(report)
    influence_sha256 = compute_influence_sha256(raw)
    with_influence = InfluenceReport(
        **{
            **asdict(report),
            "anchors": anchors,
            "coalitions": coalitions,
            "influence_sha256": influence_sha256,
        }
    )
    raw_with_influence = influence_report_to_dict(with_influence)
    report_sha256 = compute_report_sha256(raw_with_influence)
    return InfluenceReport(
        **{
            **asdict(with_influence),
            "anchors": anchors,
            "coalitions": coalitions,
            "report_sha256": report_sha256,
        }
    )


def influence_report_to_dict(report: InfluenceReport) -> dict[str, object]:
    return asdict(report)


def write_influence_report(report: InfluenceReport, output: Path) -> None:
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(influence_report_to_dict(report), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if os.name == "posix":
        output.chmod(0o600)
