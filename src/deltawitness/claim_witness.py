"""Declared logical-test witness localization for DW-001 development evidence.

This optional layer keeps the canonical four-state matrix unchanged. It binds
one operator-declared set of exact standard-library ``unittest`` logical test
IDs to selector-specific observations under only the exact ``BC`` and ``CC``
states from one verified matrix report.

A valid declaration or localization report proves selection and recorded
outcomes, not semantic oracle relevance. The initial adapter is intentionally
narrow and accepts no free-form selector command.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timezone
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from . import __version__
from . import _dw001_projection as _projection
from .config import Claim, WitnessConfig
from .errors import DeltaWitnessError
from .gitops import ensure_clean, resolve_ref, resolve_tree, worktree
from .observation import CommandResult, invocation_binding, run_claim_in_state
from .receipt import build_receipt_document, validate_receipt_document
from .reporting import sha256_document


DECLARATION_SCHEMA_VERSION = "deltawitness.claim-witness-declaration.v1"
LOCALIZATION_SCHEMA_VERSION = "deltawitness.claim-witness-localization.v1"
ADAPTER_ID = "unittest-test-id-v1"
ADAPTER_VERSION = "1"
AGGREGATE_RULE = "at_least_one_discriminating_and_none_indeterminate"

_SELECTOR_PATTERN = re.compile(
    r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*){2,}\Z"
)
_CLAIM_ID_PATTERN = re.compile(r"[a-z0-9][a-z0-9._-]{0,127}\Z")
_HEX_PATTERN = re.compile(r"[0-9a-f]+\Z")

_DECLARATION_FIELDS = {
    "schema_version",
    "spec_sha256",
    "claim_id",
    "adapter",
    "selectors",
    "aggregate_rule",
    "selector_commands",
    "declaration_sha256",
}
_ADAPTER_FIELDS = {"id", "version"}
_SELECTOR_COMMAND_FIELDS = {"selector", "command"}
_LOCALIZATION_FIELDS = {
    "schema_version",
    "tool_version",
    "created_at",
    "source",
    "adapter",
    "aggregate_rule",
    "selectors",
    "aggregate_status",
    "localization_sha256",
    "report_sha256",
}
_SOURCE_FIELDS = {
    "declaration_sha256",
    "source_report_schema_version",
    "source_report_sha256",
    "source_witness_sha256",
    "spec_sha256",
    "claim_id",
    "base_sha",
    "head_sha",
}
_SELECTOR_RESULT_FIELDS = {
    "selector",
    "command",
    "states",
    "classification",
    "diagnostic_code",
}
_STATE_FIELDS = {
    "state",
    "commit_sha",
    "tree_sha",
    "observed",
    "return_code",
    "duration_seconds",
    "timed_out",
    "stdout_sha256",
    "stderr_sha256",
    "stdout",
    "stderr",
    "observer",
    "invocation_binding",
    "receipt_sha256",
    "receipt_outcome",
    "receipt_producer",
    "receipt_counts",
    "observation_error",
}
_STATE_ORDER = ("base_candidate", "candidate_candidate")
_AGGREGATE_STATUSES = {
    "supported",
    "unsupported",
    "candidate_invalid",
    "indeterminate",
}


class ClaimWitnessError(DeltaWitnessError):
    """Raised when declared logical-test witness evidence is unsafe or invalid."""


def _error(context: str, message: str) -> ClaimWitnessError:
    return ClaimWitnessError(f"{context}: {message}")


def _object(value: object, *, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _error(context, "must be an object")
    return value


def _exact_keys(
    value: Mapping[str, object],
    expected: set[str],
    *,
    context: str,
) -> None:
    actual = set(value)
    if actual != expected:
        raise _error(
            context,
            f"field mismatch; missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}",
        )


def _string(value: object, *, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise _error(context, "must be a non-empty string")
    return value


def _hex(value: object, *, context: str, lengths: Sequence[int]) -> str:
    text = _string(value, context=context)
    if len(text) not in lengths or _HEX_PATTERN.fullmatch(text) is None:
        raise _error(
            context,
            f"must be lowercase hexadecimal with length in {tuple(lengths)}",
        )
    return text


def _claim_id(value: object, *, context: str) -> str:
    text = _string(value, context=context)
    if _CLAIM_ID_PATTERN.fullmatch(text) is None:
        raise _error(
            context,
            "must match [a-z0-9][a-z0-9._-]{0,127}",
        )
    return text


def _selector(value: object, *, context: str) -> str:
    text = _string(value, context=context)
    if _SELECTOR_PATTERN.fullmatch(text) is None:
        raise _error(
            context,
            "must be a fully qualified dotted unittest TestCase method ID",
        )
    return text


def _string_list(
    value: object,
    *,
    context: str,
    allow_empty: bool = True,
    unique: bool = True,
) -> list[str]:
    if not isinstance(value, list) or (not allow_empty and not value):
        qualifier = "a list" if allow_empty else "a non-empty list"
        raise _error(context, f"must be {qualifier} of strings")
    items = [
        _string(item, context=f"{context}[{index}]")
        for index, item in enumerate(value)
    ]
    if unique and len(items) != len(set(items)):
        raise _error(context, "must not contain duplicates")
    return items


def _adapter(value: object, *, context: str) -> dict[str, str]:
    adapter = _object(value, context=context)
    _exact_keys(adapter, _ADAPTER_FIELDS, context=context)
    if adapter["id"] != ADAPTER_ID or adapter["version"] != ADAPTER_VERSION:
        raise _error(context, "adapter identifier or version is unsupported")
    return {"id": ADAPTER_ID, "version": ADAPTER_VERSION}


def canonical_unittest_selector_command(selector: str) -> list[str]:
    """Derive the only selector command accepted by adapter v1."""

    normalized = _selector(selector, context="claim witness selector")
    return [
        "python",
        "-m",
        "deltawitness.unittest_probe",
        "--start-directory",
        "tests",
        "--verbosity",
        "0",
        "--test-name",
        normalized,
    ]


def compute_claim_witness_declaration_sha256(document: dict[str, Any]) -> str:
    normalized = deepcopy(document)
    normalized["declaration_sha256"] = None
    return sha256_document(normalized)


def _validate_declaration(
    document: object,
    *,
    verify_digest: bool,
) -> dict[str, Any]:
    declaration = _object(document, context="claim witness declaration")
    _exact_keys(
        declaration,
        _DECLARATION_FIELDS,
        context="claim witness declaration",
    )
    if declaration["schema_version"] != DECLARATION_SCHEMA_VERSION:
        raise _error(
            "claim witness declaration.schema_version",
            "is unsupported",
        )
    _hex(
        declaration["spec_sha256"],
        context="claim witness declaration.spec_sha256",
        lengths=(64,),
    )
    _claim_id(
        declaration["claim_id"],
        context="claim witness declaration.claim_id",
    )
    _adapter(
        declaration["adapter"],
        context="claim witness declaration.adapter",
    )
    selectors_value = declaration["selectors"]
    if not isinstance(selectors_value, list) or not selectors_value:
        raise _error(
            "claim witness declaration.selectors",
            "must be a non-empty list",
        )
    selectors = [
        _selector(
            item,
            context=f"claim witness declaration.selectors[{index}]",
        )
        for index, item in enumerate(selectors_value)
    ]
    if len(selectors) != len(set(selectors)):
        raise _error(
            "claim witness declaration.selectors",
            "must not contain duplicates",
        )
    if declaration["aggregate_rule"] != AGGREGATE_RULE:
        raise _error(
            "claim witness declaration.aggregate_rule",
            "is unsupported",
        )

    commands = declaration["selector_commands"]
    if not isinstance(commands, list) or len(commands) != len(selectors):
        raise _error(
            "claim witness declaration.selector_commands",
            "must contain one ordered command per selector",
        )
    expected_commands = []
    for index, selector in enumerate(selectors):
        context = f"claim witness declaration.selector_commands[{index}]"
        item = _object(commands[index], context=context)
        _exact_keys(item, _SELECTOR_COMMAND_FIELDS, context=context)
        if item["selector"] != selector:
            raise _error(
                f"{context}.selector",
                "does not match selectors order",
            )
        command = _string_list(
            item["command"],
            context=f"{context}.command",
            allow_empty=False,
            unique=False,
        )
        expected = canonical_unittest_selector_command(selector)
        if command != expected:
            raise _error(
                f"{context}.command",
                "does not match adapter-derived canonical command",
            )
        expected_commands.append({"selector": selector, "command": expected})
    if commands != expected_commands:
        raise _error(
            "claim witness declaration.selector_commands",
            "does not match adapter-derived commands",
        )

    recorded = _hex(
        declaration["declaration_sha256"],
        context="claim witness declaration.declaration_sha256",
        lengths=(64,),
    )
    if verify_digest:
        computed = compute_claim_witness_declaration_sha256(declaration)
        if computed != recorded:
            raise _error(
                "claim witness declaration.declaration_sha256",
                f"digest mismatch: expected {recorded}, computed {computed}",
            )
    return declaration


def build_claim_witness_declaration(
    *,
    spec_sha256: str,
    claim_id: str,
    selectors: list[str] | tuple[str, ...],
) -> dict[str, Any]:
    normalized_spec = _hex(
        spec_sha256,
        context="claim witness declaration.spec_sha256",
        lengths=(64,),
    )
    normalized_claim = _claim_id(
        claim_id,
        context="claim witness declaration.claim_id",
    )
    if not isinstance(selectors, (list, tuple)) or not selectors:
        raise _error(
            "claim witness declaration.selectors",
            "must be a non-empty list or tuple",
        )
    normalized_selectors = [
        _selector(item, context=f"claim witness declaration.selectors[{index}]")
        for index, item in enumerate(selectors)
    ]
    if len(normalized_selectors) != len(set(normalized_selectors)):
        raise _error(
            "claim witness declaration.selectors",
            "must not contain duplicates",
        )
    declaration: dict[str, Any] = {
        "schema_version": DECLARATION_SCHEMA_VERSION,
        "spec_sha256": normalized_spec,
        "claim_id": normalized_claim,
        "adapter": {"id": ADAPTER_ID, "version": ADAPTER_VERSION},
        "selectors": normalized_selectors,
        "aggregate_rule": AGGREGATE_RULE,
        "selector_commands": [
            {
                "selector": selector,
                "command": canonical_unittest_selector_command(selector),
            }
            for selector in normalized_selectors
        ],
        "declaration_sha256": None,
    }
    declaration["declaration_sha256"] = (
        compute_claim_witness_declaration_sha256(declaration)
    )
    _validate_declaration(declaration, verify_digest=True)
    return declaration


def verify_claim_witness_declaration_document(
    document: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        _validate_declaration(document, verify_digest=True)
    except ClaimWitnessError as exc:
        return False, (str(exc),)
    return True, ()


def _source_report(document: object) -> dict[str, Any]:
    try:
        report, _ = _projection._validate_source_report(document)
    except (DeltaWitnessError, KeyError, TypeError, IndexError, ValueError) as exc:
        raise _error(
            "claim witness source report",
            f"semantic verification failed closed: {type(exc).__name__}: {exc}",
        ) from exc
    return report


def _find_config_claim(config: WitnessConfig, claim_id: str) -> Claim:
    matches = [claim for claim in config.claims if claim.claim_id == claim_id]
    if len(matches) != 1:
        raise _error(
            "claim witness declaration.claim_id",
            "does not identify exactly one configured claim",
        )
    claim = matches[0]
    if claim.pass_exit_codes != (0,) or claim.fail_exit_codes != (1,):
        raise _error(
            "claim witness adapter",
            "unittest-test-id-v1 requires configured pass/fail exit codes [0] and [1]",
        )
    return claim


def _find_report_claim(report: Mapping[str, object], claim_id: str) -> dict[str, Any]:
    claims = report["claims"]
    if not isinstance(claims, list):
        raise _error("claim witness source report.claims", "must be a list")
    matches = [
        item
        for item in claims
        if isinstance(item, dict) and item.get("claim_id") == claim_id
    ]
    if len(matches) != 1:
        raise _error(
            "claim witness source report.claims",
            "does not contain exactly one declared claim",
        )
    return matches[0]


def _preflight_execution(
    repo: Path,
    config: WitnessConfig,
    source_report: object,
    declaration: object,
) -> tuple[dict[str, Any], dict[str, Any], Claim]:
    normalized_declaration = _validate_declaration(
        declaration,
        verify_digest=True,
    )
    report = _source_report(source_report)
    repo = repo.resolve()
    ensure_clean(repo)

    if normalized_declaration["spec_sha256"] != config.digest_sha256:
        raise _error(
            "claim witness declaration.spec_sha256",
            "does not match the supplied configuration",
        )
    if report["spec_sha256"] != config.digest_sha256:
        raise _error(
            "claim witness source report.spec_sha256",
            "does not match the supplied configuration",
        )
    if report["repository"] != repo.name:
        raise _error(
            "claim witness source report.repository",
            "does not match the supplied repository",
        )

    claim = _find_config_claim(config, normalized_declaration["claim_id"])
    report_claim = _find_report_claim(report, claim.claim_id)
    if report_claim["command"] != list(claim.command):
        raise _error(
            "claim witness source report claim command",
            "does not match the supplied configuration",
        )
    if report_claim["observer"] != claim.observer:
        raise _error(
            "claim witness source report claim observer",
            "does not match the supplied configuration",
        )

    for root_name in ("base_sha", "head_sha"):
        value = report[root_name]
        if resolve_ref(repo, value) != value:
            raise _error(
                f"claim witness source report.{root_name}",
                "does not resolve to the recorded commit",
            )
    for state in _STATE_ORDER:
        commit_sha = report["state_commits"][state]
        tree_sha = report["state_trees"][state]
        if resolve_ref(repo, commit_sha) != commit_sha:
            raise _error(
                f"claim witness source report.state_commits.{state}",
                "does not resolve to the recorded commit",
            )
        if resolve_tree(repo, commit_sha) != tree_sha:
            raise _error(
                f"claim witness source report.state_trees.{state}",
                "does not match the recorded commit tree",
            )
    return normalized_declaration, report, claim


def _selector_claim(source_claim: Claim, command: Sequence[str]) -> Claim:
    return Claim(
        claim_id=source_claim.claim_id,
        description=source_claim.description,
        observer="outcome-receipt-v1",
        command=tuple(command),
        timeout_seconds=source_claim.timeout_seconds,
        pass_exit_codes=(0,),
        fail_exit_codes=(1,),
        expectations={
            "base_base": "any",
            "base_candidate": "any",
            "candidate_base": "any",
            "candidate_candidate": "any",
        },
    )


def _state_document(result: CommandResult) -> dict[str, Any]:
    document = asdict(result)
    document.pop("expected")
    document.pop("matched")
    return document


def _selector_classification(
    states: Sequence[Mapping[str, object]],
) -> tuple[str, str | None]:
    base_candidate, candidate_candidate = states
    incomplete = [
        state
        for state in states
        if state["observed"] not in {"pass", "fail"}
    ]
    if incomplete:
        state = incomplete[0]
        diagnostic = state.get("observation_error") or state["observed"]
        return "indeterminate", f"{state['state']}:{diagnostic}"
    if candidate_candidate["observed"] == "fail":
        return "candidate_invalid", "candidate_candidate_failed"
    if base_candidate["observed"] == "fail":
        return "discriminating", None
    return "non_discriminating", None


def _aggregate_status(selector_results: Sequence[Mapping[str, object]]) -> str:
    classifications = [item["classification"] for item in selector_results]
    if "indeterminate" in classifications:
        return "indeterminate"
    if "candidate_invalid" in classifications:
        return "candidate_invalid"
    if "discriminating" in classifications:
        return "supported"
    return "unsupported"


def _semantic_state(state: Mapping[str, object]) -> dict[str, object]:
    return {
        "state": state["state"],
        "commit_sha": state["commit_sha"],
        "tree_sha": state["tree_sha"],
        "observed": state["observed"],
        "return_code": state["return_code"],
        "timed_out": state["timed_out"],
        "stdout_sha256": state["stdout_sha256"],
        "stderr_sha256": state["stderr_sha256"],
        "observer": state["observer"],
        "invocation_binding": state["invocation_binding"],
        "receipt_sha256": state["receipt_sha256"],
        "receipt_outcome": state["receipt_outcome"],
        "receipt_producer": state["receipt_producer"],
        "receipt_counts": state["receipt_counts"],
        "observation_error": state["observation_error"],
    }


def _localization_payload(document: Mapping[str, object]) -> dict[str, object]:
    selectors = document["selectors"]
    if not isinstance(selectors, list):
        raise _error("claim witness localization.selectors", "must be a list")
    return {
        "schema_version": document["schema_version"],
        "tool_version": document["tool_version"],
        "source": document["source"],
        "adapter": document["adapter"],
        "aggregate_rule": document["aggregate_rule"],
        "selectors": [
            {
                "selector": item["selector"],
                "command": item["command"],
                "states": [_semantic_state(state) for state in item["states"]],
                "classification": item["classification"],
                "diagnostic_code": item["diagnostic_code"],
            }
            for item in selectors
        ],
        "aggregate_status": document["aggregate_status"],
    }


def compute_claim_witness_localization_sha256(document: dict[str, Any]) -> str:
    return sha256_document(_localization_payload(document))


def compute_claim_witness_localization_report_sha256(
    document: dict[str, Any],
) -> str:
    normalized = deepcopy(document)
    normalized["report_sha256"] = None
    return sha256_document(normalized)


def run_claim_witness_localization(
    repo: Path,
    config: WitnessConfig,
    source_report: object,
    declaration: object,
) -> dict[str, Any]:
    """Execute declared selectors independently under exact BC and CC commits."""

    normalized_declaration, report, source_claim = _preflight_execution(
        repo,
        config,
        source_report,
        declaration,
    )
    state_commits = report["state_commits"]
    state_trees = report["state_trees"]
    selector_results: list[dict[str, Any]] = []

    with worktree(
        repo,
        state_commits["base_candidate"],
        "claim-witness-base-candidate",
    ) as base_candidate, worktree(
        repo,
        state_commits["candidate_candidate"],
        "claim-witness-candidate-candidate",
    ) as candidate_candidate:
        state_paths = {
            "base_candidate": base_candidate,
            "candidate_candidate": candidate_candidate,
        }
        for selector, command_entry in zip(
            normalized_declaration["selectors"],
            normalized_declaration["selector_commands"],
            strict=True,
        ):
            command = command_entry["command"]
            claim = _selector_claim(source_claim, command)
            state_results = [
                run_claim_in_state(
                    claim,
                    state=state,
                    expected="any",
                    cwd=state_paths[state],
                    tree_sha=state_trees[state],
                    commit_sha=state_commits[state],
                    config=config,
                    include_output=False,
                )
                for state in _STATE_ORDER
            ]
            states = [_state_document(result) for result in state_results]
            classification, diagnostic_code = _selector_classification(states)
            selector_results.append(
                {
                    "selector": selector,
                    "command": list(command),
                    "states": states,
                    "classification": classification,
                    "diagnostic_code": diagnostic_code,
                }
            )

    localization: dict[str, Any] = {
        "schema_version": LOCALIZATION_SCHEMA_VERSION,
        "tool_version": __version__,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": {
            "declaration_sha256": normalized_declaration["declaration_sha256"],
            "source_report_schema_version": report["schema_version"],
            "source_report_sha256": report["report_sha256"],
            "source_witness_sha256": report["witness_sha256"],
            "spec_sha256": report["spec_sha256"],
            "claim_id": normalized_declaration["claim_id"],
            "base_sha": report["base_sha"],
            "head_sha": report["head_sha"],
        },
        "adapter": {"id": ADAPTER_ID, "version": ADAPTER_VERSION},
        "aggregate_rule": AGGREGATE_RULE,
        "selectors": selector_results,
        "aggregate_status": _aggregate_status(selector_results),
        "localization_sha256": None,
        "report_sha256": None,
    }
    localization["localization_sha256"] = (
        compute_claim_witness_localization_sha256(localization)
    )
    localization["report_sha256"] = (
        compute_claim_witness_localization_report_sha256(localization)
    )
    valid, errors = verify_claim_witness_localization_document(
        localization,
        normalized_declaration,
        report,
    )
    if not valid:
        raise _error(
            "claim witness localization",
            f"self-verification failed: {'; '.join(errors)}",
        )
    return localization


def _validate_counts(value: object, *, context: str) -> dict[str, int]:
    expected = {
        "tests_run",
        "passed",
        "failures",
        "errors",
        "skipped",
        "expected_failures",
        "unexpected_successes",
    }
    counts = _object(value, context=context)
    _exact_keys(counts, expected, context=context)
    normalized: dict[str, int] = {}
    for field in sorted(expected):
        item = counts[field]
        if (
            not isinstance(item, int)
            or isinstance(item, bool)
            or not 0 <= item <= 100_000_000
        ):
            raise _error(
                f"{context}.{field}",
                "must be an integer between 0 and 100000000",
            )
        normalized[field] = item
    classified = sum(
        count for key, count in normalized.items() if key != "tests_run"
    )
    if classified != normalized["tests_run"]:
        raise _error(context, "category counts do not sum to tests_run")
    return normalized


def _validate_state(
    value: object,
    *,
    context: str,
    state_name: str,
    command: Sequence[str],
    declaration: Mapping[str, object],
    report: Mapping[str, object],
) -> dict[str, Any]:
    state = _object(value, context=context)
    _exact_keys(state, _STATE_FIELDS, context=context)
    if state["state"] != state_name:
        raise _error(context, f"state must be {state_name!r}")
    commit_sha = _hex(
        state["commit_sha"],
        context=f"{context}.commit_sha",
        lengths=(40, 64),
    )
    tree_sha = _hex(
        state["tree_sha"],
        context=f"{context}.tree_sha",
        lengths=(40, 64),
    )
    if commit_sha != report["state_commits"][state_name]:
        raise _error(f"{context}.commit_sha", "does not match source report")
    if tree_sha != report["state_trees"][state_name]:
        raise _error(f"{context}.tree_sha", "does not match source report")

    observed = state["observed"]
    if observed not in {"pass", "fail", "error", "timeout"}:
        raise _error(f"{context}.observed", "is unsupported")
    timed_out = state["timed_out"]
    if not isinstance(timed_out, bool) or timed_out != (observed == "timeout"):
        raise _error(f"{context}.timed_out", "is inconsistent with observed")
    return_code = state["return_code"]
    if return_code is not None and (
        not isinstance(return_code, int) or isinstance(return_code, bool)
    ):
        raise _error(f"{context}.return_code", "must be an integer or null")
    duration = state["duration_seconds"]
    if (
        not isinstance(duration, (int, float))
        or isinstance(duration, bool)
        or duration < 0
    ):
        raise _error(f"{context}.duration_seconds", "must be nonnegative")
    for field in ("stdout_sha256", "stderr_sha256", "invocation_binding"):
        _hex(state[field], context=f"{context}.{field}", lengths=(64,))
    if state["stdout"] is not None or state["stderr"] is not None:
        raise _error(context, "raw output must be null")
    if state["observer"] != "outcome-receipt-v1":
        raise _error(f"{context}.observer", "must be outcome-receipt-v1")

    binding_claim = Claim(
        claim_id=str(declaration["claim_id"]),
        description="",
        observer="outcome-receipt-v1",
        command=tuple(command),
        timeout_seconds=1,
        pass_exit_codes=(0,),
        fail_exit_codes=(1,),
        expectations={
            "base_base": "any",
            "base_candidate": "any",
            "candidate_base": "any",
            "candidate_candidate": "any",
        },
    )
    expected_binding = invocation_binding(
        binding_claim,
        state=state_name,
        tree_sha=tree_sha,
        commit_sha=commit_sha,
        spec_sha256=str(declaration["spec_sha256"]),
    )
    if state["invocation_binding"] != expected_binding:
        raise _error(
            f"{context}.invocation_binding",
            "does not match declaration, command, and Git state",
        )

    receipt_outcome = state["receipt_outcome"]
    receipt_sha = state["receipt_sha256"]
    receipt_producer = state["receipt_producer"]
    receipt_counts = state["receipt_counts"]
    observation_error = state["observation_error"]
    if observation_error is not None and not isinstance(observation_error, str):
        raise _error(f"{context}.observation_error", "must be a string or null")

    if receipt_outcome is None:
        if any(
            item is not None
            for item in (receipt_sha, receipt_producer, receipt_counts)
        ):
            raise _error(context, "receipt fields are inconsistent")
    else:
        _string(receipt_outcome, context=f"{context}.receipt_outcome")
        normalized_sha = _hex(
            receipt_sha,
            context=f"{context}.receipt_sha256",
            lengths=(64,),
        )
        producer = _object(
            receipt_producer,
            context=f"{context}.receipt_producer",
        )
        _exact_keys(
            producer,
            {"name", "version"},
            context=f"{context}.receipt_producer",
        )
        counts = _validate_counts(
            receipt_counts,
            context=f"{context}.receipt_counts",
        )
        receipt_document = build_receipt_document(
            binding=expected_binding,
            producer_name=_string(
                producer["name"],
                context=f"{context}.receipt_producer.name",
            ),
            producer_version=_string(
                producer["version"],
                context=f"{context}.receipt_producer.version",
            ),
            outcome=receipt_outcome,
            counts=counts,
        )
        validated = validate_receipt_document(
            receipt_document,
            expected_binding=expected_binding,
        )
        if validated.sha256 != normalized_sha:
            raise _error(
                f"{context}.receipt_sha256",
                "does not match reconstructed typed receipt",
            )

    if timed_out:
        expected_observed = "timeout"
        expected_error = None
    elif receipt_outcome == "passed" and return_code == 0:
        expected_observed = "pass"
        expected_error = None
    elif receipt_outcome == "test_failure" and return_code == 1:
        expected_observed = "fail"
        expected_error = None
    elif receipt_outcome is not None:
        expected_observed = "error"
        expected_error = f"receipt_outcome:{receipt_outcome}"
    else:
        expected_observed = "error"
        expected_error = observation_error
        if not expected_error:
            raise _error(context, "receipt-free error requires observation_error")
    if observed != expected_observed:
        raise _error(
            f"{context}.observed",
            "is inconsistent with process and receipt evidence",
        )
    if observation_error != expected_error:
        raise _error(
            f"{context}.observation_error",
            "is inconsistent with process and receipt evidence",
        )
    return state


def _validate_localization(
    document: object,
    declaration: Mapping[str, object],
    report: Mapping[str, object],
    *,
    verify_digests: bool,
) -> dict[str, Any]:
    localization = _object(document, context="claim witness localization")
    _exact_keys(
        localization,
        _LOCALIZATION_FIELDS,
        context="claim witness localization",
    )
    if localization["schema_version"] != LOCALIZATION_SCHEMA_VERSION:
        raise _error(
            "claim witness localization.schema_version",
            "is unsupported",
        )
    _string(
        localization["tool_version"],
        context="claim witness localization.tool_version",
    )
    _string(
        localization["created_at"],
        context="claim witness localization.created_at",
    )
    source = _object(
        localization["source"],
        context="claim witness localization.source",
    )
    _exact_keys(
        source,
        _SOURCE_FIELDS,
        context="claim witness localization.source",
    )
    expected_source = {
        "declaration_sha256": declaration["declaration_sha256"],
        "source_report_schema_version": report["schema_version"],
        "source_report_sha256": report["report_sha256"],
        "source_witness_sha256": report["witness_sha256"],
        "spec_sha256": report["spec_sha256"],
        "claim_id": declaration["claim_id"],
        "base_sha": report["base_sha"],
        "head_sha": report["head_sha"],
    }
    if source != expected_source:
        raise _error(
            "claim witness localization.source",
            "does not match declaration and source report",
        )
    _adapter(
        localization["adapter"],
        context="claim witness localization.adapter",
    )
    if localization["aggregate_rule"] != AGGREGATE_RULE:
        raise _error(
            "claim witness localization.aggregate_rule",
            "is unsupported",
        )

    selector_values = localization["selectors"]
    if (
        not isinstance(selector_values, list)
        or len(selector_values) != len(declaration["selectors"])
    ):
        raise _error(
            "claim witness localization.selectors",
            "must contain one ordered result per declaration selector",
        )
    normalized_results: list[dict[str, Any]] = []
    for index, declared_selector in enumerate(declaration["selectors"]):
        context = f"claim witness localization.selectors[{index}]"
        item = _object(selector_values[index], context=context)
        _exact_keys(item, _SELECTOR_RESULT_FIELDS, context=context)
        if item["selector"] != declared_selector:
            raise _error(
                f"{context}.selector",
                "does not match declaration order",
            )
        command = _string_list(
            item["command"],
            context=f"{context}.command",
            allow_empty=False,
            unique=False,
        )
        expected_command = canonical_unittest_selector_command(
            str(declared_selector)
        )
        if command != expected_command:
            raise _error(
                f"{context}.command",
                "does not match adapter-derived command",
            )
        states_value = item["states"]
        if not isinstance(states_value, list) or len(states_value) != 2:
            raise _error(
                f"{context}.states",
                "must contain ordered BC and CC observations",
            )
        states = [
            _validate_state(
                states_value[state_index],
                context=f"{context}.states[{state_name}]",
                state_name=state_name,
                command=command,
                declaration=declaration,
                report=report,
            )
            for state_index, state_name in enumerate(_STATE_ORDER)
        ]
        classification, diagnostic = _selector_classification(states)
        if item["classification"] != classification:
            raise _error(
                f"{context}.classification",
                "is inconsistent with selector states",
            )
        if item["diagnostic_code"] != diagnostic:
            raise _error(
                f"{context}.diagnostic_code",
                "is inconsistent with selector states",
            )
        normalized_results.append(item)

    expected_aggregate = _aggregate_status(normalized_results)
    if localization["aggregate_status"] not in _AGGREGATE_STATUSES:
        raise _error(
            "claim witness localization.aggregate_status",
            "is unsupported",
        )
    if localization["aggregate_status"] != expected_aggregate:
        raise _error(
            "claim witness localization.aggregate_status",
            "is inconsistent with selector classifications",
        )

    expected_semantic = _hex(
        localization["localization_sha256"],
        context="claim witness localization.localization_sha256",
        lengths=(64,),
    )
    expected_report = _hex(
        localization["report_sha256"],
        context="claim witness localization.report_sha256",
        lengths=(64,),
    )
    if verify_digests:
        computed_semantic = compute_claim_witness_localization_sha256(
            localization
        )
        if computed_semantic != expected_semantic:
            raise _error(
                "claim witness localization.localization_sha256",
                f"digest mismatch: expected {expected_semantic}, "
                f"computed {computed_semantic}",
            )
        computed_report = compute_claim_witness_localization_report_sha256(
            localization
        )
        if computed_report != expected_report:
            raise _error(
                "claim witness localization.report_sha256",
                f"digest mismatch: expected {expected_report}, "
                f"computed {computed_report}",
            )
    return localization


def verify_claim_witness_localization_document(
    document: object,
    declaration: object,
    source_report: object,
) -> tuple[bool, tuple[str, ...]]:
    errors: list[str] = []
    try:
        normalized_declaration = _validate_declaration(
            declaration,
            verify_digest=True,
        )
    except ClaimWitnessError as exc:
        return False, (str(exc),)
    try:
        report = _source_report(source_report)
    except ClaimWitnessError as exc:
        return False, (str(exc),)
    if normalized_declaration["spec_sha256"] != report["spec_sha256"]:
        errors.append(
            "claim witness declaration.spec_sha256 does not match source report"
        )
    try:
        _find_report_claim(
            report,
            str(normalized_declaration["claim_id"]),
        )
    except ClaimWitnessError as exc:
        errors.append(str(exc))
    try:
        _validate_localization(
            document,
            normalized_declaration,
            report,
            verify_digests=True,
        )
    except ClaimWitnessError as exc:
        errors.append(str(exc))
    unique = tuple(dict.fromkeys(errors))
    return not unique, unique


__all__ = [
    "ADAPTER_ID",
    "ADAPTER_VERSION",
    "AGGREGATE_RULE",
    "DECLARATION_SCHEMA_VERSION",
    "LOCALIZATION_SCHEMA_VERSION",
    "ClaimWitnessError",
    "build_claim_witness_declaration",
    "canonical_unittest_selector_command",
    "compute_claim_witness_declaration_sha256",
    "compute_claim_witness_localization_report_sha256",
    "compute_claim_witness_localization_sha256",
    "run_claim_witness_localization",
    "verify_claim_witness_declaration_document",
    "verify_claim_witness_localization_document",
]
