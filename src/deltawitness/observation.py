"""Execute one declared claim against one exact Git state."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import Claim, WitnessConfig
from .execution import run_command
from .gitops import restore_commit
from .reporting import sha256_document


@dataclass(frozen=True)
class CommandResult:
    """One process observation bound to an exact claim and Git state."""

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
    observer: str
    invocation_binding: str
    receipt_sha256: str | None
    receipt_outcome: str | None
    receipt_producer: dict[str, str] | None
    receipt_counts: dict[str, int] | None
    observation_error: str | None


def invocation_binding(
    claim: Claim,
    *,
    state: str,
    tree_sha: str,
    commit_sha: str,
    spec_sha256: str,
) -> str:
    """Bind one observation request to its full semantic invocation identity."""

    return sha256_document(
        {
            "schema_version": "deltawitness.invocation.v1",
            "claim_id": claim.claim_id,
            "state": state,
            "tree_sha": tree_sha,
            "commit_sha": commit_sha,
            "observer": claim.observer,
            "command": list(claim.command),
            "spec_sha256": spec_sha256,
        }
    )


def classify_observation(
    claim: Claim,
    *,
    return_code: int | None,
    timed_out: bool,
    receipt_outcome: str | None,
    receipt_error: str | None,
) -> tuple[str, str | None]:
    """Map process and receipt channels into pass, fail, timeout, or error."""

    if timed_out:
        return "timeout", None

    if claim.observer == "exit-code-v1":
        if return_code in claim.pass_exit_codes:
            return "pass", None
        if return_code in claim.fail_exit_codes:
            return "fail", None
        return "error", "unclassified_exit_code"

    if receipt_error is not None:
        return "error", receipt_error
    if receipt_outcome is None:
        return "error", "missing_receipt_outcome"

    if receipt_outcome == "passed":
        if return_code in claim.pass_exit_codes:
            return "pass", None
        return "error", "receipt_exit_mismatch"
    if receipt_outcome == "test_failure":
        if return_code in claim.fail_exit_codes:
            return "fail", None
        return "error", "receipt_exit_mismatch"
    return "error", f"receipt_outcome:{receipt_outcome}"


def run_claim_in_state(
    claim: Claim,
    *,
    state: str,
    expected: str,
    cwd: Path,
    tree_sha: str,
    commit_sha: str,
    config: WitnessConfig,
    include_output: bool,
) -> CommandResult:
    """Restore and observe one exact state using the claim's declared observer."""

    if expected not in {"pass", "fail", "any"}:
        raise ValueError(f"Unsupported expected observation: {expected!r}")

    restore_commit(cwd, commit_sha)
    binding = invocation_binding(
        claim,
        state=state,
        tree_sha=tree_sha,
        commit_sha=commit_sha,
        spec_sha256=config.digest_sha256,
    )
    observation = run_command(
        claim.command,
        state=state,
        cwd=cwd,
        timeout_seconds=claim.timeout_seconds,
        pass_env=config.execution_policy.pass_env,
        include_output=include_output,
        observer=claim.observer,
        receipt_binding=(binding if claim.observer == "outcome-receipt-v1" else None),
    )
    observed, observation_error = classify_observation(
        claim,
        return_code=observation.return_code,
        timed_out=observation.timed_out,
        receipt_outcome=observation.receipt_outcome,
        receipt_error=observation.receipt_error,
    )
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
        observer=observation.observer,
        invocation_binding=binding,
        receipt_sha256=observation.receipt_sha256,
        receipt_outcome=observation.receipt_outcome,
        receipt_producer=observation.receipt_producer,
        receipt_counts=observation.receipt_counts,
        observation_error=observation_error,
    )
