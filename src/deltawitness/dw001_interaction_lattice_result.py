"""Public facade for the frozen DW-001 interaction-lattice result.

The normative implementation lives in the private sibling module. This facade
preserves controlled executor seams used by the retained red-first negative
result tests without allowing product callers to provide an executor.
"""

from __future__ import annotations

from pathlib import Path
from threading import RLock
from typing import Any, Mapping, Sequence

from . import _dw001_interaction_lattice_result as _implementation


RESULT_SCHEMA_VERSION = _implementation.RESULT_SCHEMA_VERSION
RESULT_ID = _implementation.RESULT_ID
EXECUTION_PROTOCOL_SHA256 = _implementation.EXECUTION_PROTOCOL_SHA256
PLAN_SHA256 = _implementation.PLAN_SHA256
CATALOG_SHA256 = _implementation.CATALOG_SHA256
PRIOR_ART_LOG_SHA256 = _implementation.PRIOR_ART_LOG_SHA256
DW001InteractionLatticeResultError = (
    _implementation.DW001InteractionLatticeResultError
)

compute_interaction_lattice_result_semantic_sha256 = (
    _implementation.compute_interaction_lattice_result_semantic_sha256
)
compute_interaction_lattice_result_report_sha256 = (
    _implementation.compute_interaction_lattice_result_report_sha256
)
build_anonymous_result_path_multiset = (
    _implementation.build_anonymous_result_path_multiset
)

_execute_candidate_selector = _implementation._execute_candidate_selector
_execute_mutant_selector = _implementation._execute_mutant_selector
_EXECUTOR_LOCK = RLock()


def run_interaction_witness_lattice_result(
    execution_protocol: object,
    plan: object,
    catalog: object,
    prior_art: object,
    coveragepy_manifest: object,
    pr46_result: object,
) -> dict[str, Any]:
    """Execute the fixed result with the controlled public test seams."""

    with _EXECUTOR_LOCK:
        original_candidate = _implementation._execute_candidate_selector
        original_mutant = _implementation._execute_mutant_selector
        _implementation._execute_candidate_selector = _execute_candidate_selector
        _implementation._execute_mutant_selector = _execute_mutant_selector
        try:
            return _implementation.run_interaction_witness_lattice_result(
                execution_protocol,
                plan,
                catalog,
                prior_art,
                coveragepy_manifest,
                pr46_result,
            )
        finally:
            _implementation._execute_candidate_selector = original_candidate
            _implementation._execute_mutant_selector = original_mutant


def verify_interaction_witness_lattice_result_document(
    document: object,
    execution_protocol: object,
    plan: object,
    catalog: object,
    prior_art: object,
    coveragepy_manifest: object,
    pr46_result: object,
) -> tuple[bool, tuple[str, ...]]:
    """Independently reconstruct and verify one result document."""

    return _implementation.verify_interaction_witness_lattice_result_document(
        document,
        execution_protocol,
        plan,
        catalog,
        prior_art,
        coveragepy_manifest,
        pr46_result,
    )


def load_interaction_witness_lattice_result(
    path: Path,
    execution_protocol: object,
    plan: object,
    catalog: object,
    prior_art: object,
    coveragepy_manifest: object,
    pr46_result: object,
) -> dict[str, Any]:
    """Strict-load and verify one bounded regular non-link result."""

    return _implementation.load_interaction_witness_lattice_result(
        path,
        execution_protocol,
        plan,
        catalog,
        prior_art,
        coveragepy_manifest,
        pr46_result,
    )


__all__ = [
    "CATALOG_SHA256",
    "DW001InteractionLatticeResultError",
    "EXECUTION_PROTOCOL_SHA256",
    "PLAN_SHA256",
    "PRIOR_ART_LOG_SHA256",
    "RESULT_ID",
    "RESULT_SCHEMA_VERSION",
    "build_anonymous_result_path_multiset",
    "compute_interaction_lattice_result_report_sha256",
    "compute_interaction_lattice_result_semantic_sha256",
    "load_interaction_witness_lattice_result",
    "run_interaction_witness_lattice_result",
    "verify_interaction_witness_lattice_result_document",
]
