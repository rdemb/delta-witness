"""Reconstruct exact canonical matrix state objects for claim localization.

A matrix report can refer to deterministic synthetic ``BC`` and ``CB`` commits
that are present in the producer repository but not yet materialized in an
equivalent fresh checkout. This module recreates those objects from the exact
base/head commits, current path classification, and the recorded report before
the localization core opens state worktrees.

No test command is executed here. The reconstructed trees and commits must match
the report exactly or localization fails closed.
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from . import _dw001_projection as _projection
from .config import WitnessConfig
from .errors import DeltaWitnessError
from .gitops import (
    changed_paths,
    classify_changes,
    create_synthetic_commit,
    ensure_ancestor,
    ensure_clean,
    ensure_supported_entries,
    overlay_paths,
    resolve_ref,
    resolve_tree,
    worktree,
    write_tree,
)


class ClaimWitnessStateError(DeltaWitnessError):
    """Raised when recorded matrix state identities cannot be reconstructed."""


def _error(context: str, message: str) -> ClaimWitnessStateError:
    return ClaimWitnessStateError(f"{context}: {message}")


def _classification_document(classification: object) -> dict[str, list[dict[str, str]]]:
    return {
        "code": [asdict(item) for item in classification.code],
        "tests": [asdict(item) for item in classification.tests],
        "documentation": [asdict(item) for item in classification.documentation],
    }


def materialize_source_report_states(
    repo: Path,
    config: WitnessConfig,
    source_report: object,
) -> dict[str, dict[str, str]]:
    """Recreate and verify all exact state trees/commits from a source report."""

    try:
        report, _ = _projection._validate_source_report(source_report)
    except (
        DeltaWitnessError,
        KeyError,
        TypeError,
        IndexError,
        ValueError,
        OverflowError,
    ) as exc:
        raise _error(
            "claim witness source report",
            f"semantic verification failed closed: {type(exc).__name__}: {exc}",
        ) from exc

    repository = repo.resolve()
    ensure_clean(repository)
    base_sha = resolve_ref(repository, str(report["base_sha"]))
    head_sha = resolve_ref(repository, str(report["head_sha"]))
    if base_sha != report["base_sha"] or head_sha != report["head_sha"]:
        raise _error(
            "claim witness source report",
            "base or candidate commit does not match the current repository",
        )
    ensure_ancestor(repository, base_sha, head_sha)

    changes = changed_paths(repository, base_sha, head_sha)
    classification = classify_changes(changes, config.path_policy)
    ensure_supported_entries(
        repository,
        base_sha,
        head_sha,
        [item.path for item in classification.all],
    )
    current_classification = _classification_document(classification)
    if current_classification != report["classification"]:
        raise _error(
            "claim witness source report.classification",
            "does not match the current repository and configuration",
        )
    test_paths = sorted({item.path for item in classification.tests})

    with worktree(
        repository,
        base_sha,
        "claim-witness-reconstruct-base-candidate",
    ) as base_candidate, worktree(
        repository,
        head_sha,
        "claim-witness-reconstruct-candidate-base",
    ) as candidate_base:
        overlay_paths(repository, base_candidate, head_sha, test_paths)
        overlay_paths(repository, candidate_base, base_sha, test_paths)
        reconstructed_trees = {
            "base_base": resolve_tree(repository, base_sha),
            "base_candidate": write_tree(base_candidate),
            "candidate_base": write_tree(candidate_base),
            "candidate_candidate": resolve_tree(repository, head_sha),
        }
        reconstructed_commits = {
            "base_base": base_sha,
            "base_candidate": create_synthetic_commit(
                repository,
                reconstructed_trees["base_candidate"],
                base_sha,
                state="base_candidate",
                base_sha=base_sha,
                head_sha=head_sha,
            ),
            "candidate_base": create_synthetic_commit(
                repository,
                reconstructed_trees["candidate_base"],
                base_sha,
                state="candidate_base",
                base_sha=base_sha,
                head_sha=head_sha,
            ),
            "candidate_candidate": head_sha,
        }

    if reconstructed_trees != report["state_trees"]:
        raise _error(
            "claim witness source report.state_trees",
            "cannot be reproduced from the current repository and configuration",
        )
    if reconstructed_commits != report["state_commits"]:
        raise _error(
            "claim witness source report.state_commits",
            "cannot be reproduced from the current repository and configuration",
        )
    ensure_clean(repository)
    return {
        "trees": reconstructed_trees,
        "commits": reconstructed_commits,
    }


__all__ = [
    "ClaimWitnessStateError",
    "materialize_source_report_states",
]
