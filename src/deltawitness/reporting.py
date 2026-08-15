"""Canonical report hashing and integrity verification."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .errors import ReportError


def canonical_json(document: object) -> bytes:
    # ASCII escaping gives one portable byte representation even when a Git path
    # contains bytes that are not valid UTF-8 and was decoded with surrogateescape.
    return json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def sha256_document(document: object) -> str:
    return hashlib.sha256(canonical_json(document)).hexdigest()


def command_semantic_payload(state: dict[str, Any]) -> dict[str, Any]:
    """Select stable evidence fields from one command-state observation."""

    payload: dict[str, Any] = {
        "state": state["state"],
        "commit_sha": state["commit_sha"],
        "tree_sha": state["tree_sha"],
        "observed": state["observed"],
        "expected": state["expected"],
        "matched": state["matched"],
        "return_code": state["return_code"],
        "timed_out": state["timed_out"],
    }
    # Schema 0.3 adds typed observer evidence. Keeping these fields conditional
    # preserves verification of already-issued 0.2 reports.
    for key in (
        "observer",
        "invocation_binding",
        "receipt_sha256",
        "receipt_outcome",
        "receipt_producer",
        "receipt_counts",
        "observation_error",
    ):
        if key in state:
            payload[key] = state[key]
    return payload


def claim_semantic_payload(claim: dict[str, Any]) -> dict[str, Any]:
    """Select stable fields from one claim and all of its exact observations."""

    payload: dict[str, Any] = {
        "claim_id": claim["claim_id"],
        "description": claim["description"],
        "supported": claim["supported"],
        "command": claim["command"],
        "states": [command_semantic_payload(state) for state in claim["states"]],
    }
    for key in ("observer", "complete"):
        if key in claim:
            payload[key] = claim[key]
    return payload


def witness_payload(document: dict[str, Any]) -> dict[str, Any]:
    try:
        return {
            "schema_version": document["schema_version"],
            "tool_version": document["tool_version"],
            "base_sha": document["base_sha"],
            "head_sha": document["head_sha"],
            "spec_sha256": document["spec_sha256"],
            "execution": document["execution"],
            "classification": document["classification"],
            "state_trees": document["state_trees"],
            "state_commits": document["state_commits"],
            "claims": [claim_semantic_payload(claim) for claim in document["claims"]],
            "complete": document["complete"],
            "supported": document["supported"],
        }
    except (KeyError, TypeError) as exc:
        raise ReportError(f"Report is missing a required witness field: {exc}") from exc


def influence_payload(document: dict[str, Any]) -> dict[str, Any]:
    """Build the stable semantic payload for an exact patch-influence report."""

    try:
        coalitions = []
        for coalition in document["coalitions"]:
            coalitions.append(
                {
                    "coalition_id": coalition["coalition_id"],
                    "mask": coalition["mask"],
                    "selected_paths": coalition["selected_paths"],
                    "implementation_tree_sha": coalition["implementation_tree_sha"],
                    "implementation_commit_sha": coalition["implementation_commit_sha"],
                    "candidate_tests_tree_sha": coalition["candidate_tests_tree_sha"],
                    "candidate_tests_commit_sha": coalition["candidate_tests_commit_sha"],
                    "claims": [
                        claim_semantic_payload(claim) for claim in coalition["claims"]
                    ],
                    "complete": coalition["complete"],
                    "supported": coalition["supported"],
                    "status": coalition["status"],
                }
            )

        return {
            "schema_version": document["schema_version"],
            "tool_version": document["tool_version"],
            "base_sha": document["base_sha"],
            "head_sha": document["head_sha"],
            "spec_sha256": document["spec_sha256"],
            "execution": document["execution"],
            "classification": document["classification"],
            "intervention": document["intervention"],
            "matrix_reference": document["matrix_reference"],
            "anchors": document["anchors"],
            "coalitions": coalitions,
            "complete": document["complete"],
            "anchors_consistent": document["anchors_consistent"],
            "attribution_available": document["attribution_available"],
            "status": document["status"],
            "metrics": document["metrics"],
        }
    except (KeyError, TypeError) as exc:
        raise ReportError(f"Report is missing a required influence field: {exc}") from exc


def compute_witness_sha256(document: dict[str, Any]) -> str:
    return sha256_document(witness_payload(document))


def compute_influence_sha256(document: dict[str, Any]) -> str:
    return sha256_document(influence_payload(document))


def compute_report_sha256(document: dict[str, Any]) -> str:
    normalized = dict(document)
    normalized["report_sha256"] = None
    return sha256_document(normalized)


def verify_report_document(document: object) -> tuple[bool, tuple[str, ...]]:
    if not isinstance(document, dict):
        raise ReportError("Report root must be a JSON object")

    errors: list[str] = []
    if "influence_sha256" in document:
        expected_semantic = document.get("influence_sha256")
        semantic_label = "influence"
        semantic_computer = compute_influence_sha256
    else:
        expected_semantic = document.get("witness_sha256")
        semantic_label = "witness"
        semantic_computer = compute_witness_sha256

    if not isinstance(expected_semantic, str):
        errors.append(f"{semantic_label}_sha256 is missing or invalid")
    else:
        observed_semantic = semantic_computer(document)
        if observed_semantic != expected_semantic:
            errors.append(
                f"{semantic_label} digest mismatch: expected {expected_semantic}, "
                f"computed {observed_semantic}"
            )

    expected_report = document.get("report_sha256")
    if not isinstance(expected_report, str):
        errors.append("report_sha256 is missing or invalid")
    else:
        observed_report = compute_report_sha256(document)
        if observed_report != expected_report:
            errors.append(f"report digest mismatch: expected {expected_report}, computed {observed_report}")

    return not errors, tuple(errors)


def load_report(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ReportError(f"Cannot read report: {path}: {exc}") from exc
    try:
        document = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ReportError(f"Invalid JSON report: {path}: {exc}") from exc
    if not isinstance(document, dict):
        raise ReportError("Report root must be a JSON object")
    return document
