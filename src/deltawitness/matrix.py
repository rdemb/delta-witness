"""Execute the four-state counterfactual change matrix."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from . import __version__
from .config import Claim, WitnessConfig
from .errors import VerificationError
from .execution import run_command
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
from .reporting import compute_report_sha256, compute_witness_sha256

_STATE_ORDER = ("base_base", "base_candidate", "candidate_base", "candidate_candidate")


@dataclass(frozen=True)
class CommandResult:
    state: str
    commit_sha: str
    tree_sha: str
    observed: str
    expected: str
    matched: bool
    return_code: int | None
    duration_seconds: float
    timed_out: bool
    stdout_sha256: str
    stderr_sha256: str
    stdout: str | None
    stderr: str | None


@dataclass(frozen=True)
class ClaimResult:
    claim_id: str
    description: str
    supported: bool
    command: tuple[str, ...]
    states: tuple[CommandResult, ...]


@dataclass(frozen=True)
class VerificationReport:
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
    state_trees: dict[str, str]
    state_commits: dict[str, str]
    claims: tuple[ClaimResult, ...]
    complete: bool
    supported: bool
    witness_sha256: str | None = None
    report_sha256: str | None = None


def _run_claim(
    claim: Claim,
    state: str,
    cwd: Path,
    tree_sha: str,
    commit_sha: str,
    config: WitnessConfig,
    include_output: bool,
) -> CommandResult:
    restore_commit(cwd, commit_sha)
    observation = run_command(
        claim.command,
        state=state,
        cwd=cwd,
        timeout_seconds=claim.timeout_seconds,
        pass_env=config.execution_policy.pass_env,
        include_output=include_output,
    )
    if observation.timed_out:
        observed = "timeout"
    elif observation.return_code in claim.pass_exit_codes:
        observed = "pass"
    elif observation.return_code in claim.fail_exit_codes:
        observed = "fail"
    else:
        observed = "error"
    expected = claim.expectations[state]
    matched = expected == observed or (expected == "any" and observed in {"pass", "fail"})
    return CommandResult(
        state=state,
        commit_sha=commit_sha,
        tree_sha=tree_sha,
        observed=observed,
        expected=expected,
        matched=matched,
        return_code=observation.return_code,
        duration_seconds=observation.duration_seconds,
        timed_out=observation.timed_out,
        stdout_sha256=observation.stdout_sha256,
        stderr_sha256=observation.stderr_sha256,
        stdout=observation.stdout,
        stderr=observation.stderr,
    )


def _serialize_classification(classification: PathClassification) -> dict[str, list[dict[str, str]]]:
    return {
        "code": [asdict(item) for item in classification.code],
        "tests": [asdict(item) for item in classification.tests],
        "documentation": [asdict(item) for item in classification.documentation],
    }


def verify_repository(
    repo: Path,
    base_ref: str,
    head_ref: str,
    config: WitnessConfig,
    *,
    include_output: bool = False,
) -> VerificationReport:
    repo = repo.resolve()
    ensure_clean(repo)
    base_sha = resolve_ref(repo, base_ref)
    head_sha = resolve_ref(repo, head_ref)
    if base_sha == head_sha:
        raise VerificationError("Base and candidate resolve to the same commit")
    ensure_ancestor(repo, base_sha, head_sha)

    changes = changed_paths(repo, base_sha, head_sha)
    classification = classify_changes(changes, config.path_policy)
    ensure_supported_entries(repo, base_sha, head_sha, [item.path for item in classification.all])
    test_paths = sorted({item.path for item in classification.tests})

    claim_results: list[ClaimResult] = []
    with worktree(repo, base_sha, "base-base") as base_base, worktree(
        repo, base_sha, "base-candidate"
    ) as base_candidate, worktree(repo, head_sha, "candidate-base") as candidate_base, worktree(
        repo, head_sha, "candidate-candidate"
    ) as candidate_candidate:
        overlay_paths(repo, base_candidate, head_sha, test_paths)
        overlay_paths(repo, candidate_base, base_sha, test_paths)

        state_paths = {
            "base_base": base_base,
            "base_candidate": base_candidate,
            "candidate_base": candidate_base,
            "candidate_candidate": candidate_candidate,
        }
        state_trees = {state: write_tree(path) for state, path in state_paths.items()}
        state_commits = {
            "base_base": base_sha,
            "base_candidate": create_synthetic_commit(
                repo,
                state_trees["base_candidate"],
                base_sha,
                state="base_candidate",
                base_sha=base_sha,
                head_sha=head_sha,
            ),
            "candidate_base": create_synthetic_commit(
                repo,
                state_trees["candidate_base"],
                base_sha,
                state="candidate_base",
                base_sha=base_sha,
                head_sha=head_sha,
            ),
            "candidate_candidate": head_sha,
        }

        for state in _STATE_ORDER:
            restore_commit(state_paths[state], state_commits[state])

        for claim in config.claims:
            state_results = tuple(
                _run_claim(
                    claim,
                    state,
                    state_paths[state],
                    state_trees[state],
                    state_commits[state],
                    config,
                    include_output,
                )
                for state in _STATE_ORDER
            )
            claim_results.append(
                ClaimResult(
                    claim_id=claim.claim_id,
                    description=claim.description,
                    supported=all(result.matched for result in state_results),
                    command=claim.command,
                    states=state_results,
                )
            )

    complete = all(
        state.observed in {"pass", "fail"}
        for claim_result in claim_results
        for state in claim_result.states
    )
    supported = complete and all(result.supported for result in claim_results)
    spec_label, spec_external = safe_path_label(config.path, repo)
    report = VerificationReport(
        schema_version="0.2",
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
        },
        classification=_serialize_classification(classification),
        state_trees=state_trees,
        state_commits=state_commits,
        claims=tuple(claim_results),
        complete=complete,
        supported=supported,
        witness_sha256=None,
        report_sha256=None,
    )

    raw = report_to_dict(report)
    witness_sha256 = compute_witness_sha256(raw)
    report_with_witness = VerificationReport(
        **{**asdict(report), "claims": tuple(claim_results), "witness_sha256": witness_sha256}
    )
    raw_with_witness = report_to_dict(report_with_witness)
    report_sha256 = compute_report_sha256(raw_with_witness)
    return VerificationReport(
        **{**asdict(report_with_witness), "claims": tuple(claim_results), "report_sha256": report_sha256}
    )


def report_to_dict(report: VerificationReport) -> dict[str, object]:
    return asdict(report)


def write_report(report: VerificationReport, output: Path) -> None:
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report_to_dict(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if os.name == "posix":
        output.chmod(0o600)
