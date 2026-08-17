"""Public facade for the DW-001 Coverage.py direct baseline.

The normative implementation lives in the private sibling module. This facade
preserves the controlled executor seam used by red-first and adversarial tests
and enforces one fail-closed precedence rule: unavailable Coverage.py evidence
is indeterminate even when the typed selector outcome is a test failure.
"""

from __future__ import annotations

from pathlib import Path
from threading import RLock
from typing import Any, Mapping

from . import _dw001_coveragepy_baseline as _implementation


RESULT_SCHEMA_VERSION = _implementation.RESULT_SCHEMA_VERSION
RESULT_ID = _implementation.RESULT_ID
ADAPTER_ID = _implementation.ADAPTER_ID
MUTATION_RESULT_SEMANTIC_SHA256 = (
    _implementation.MUTATION_RESULT_SEMANTIC_SHA256
)
STDLIB_STATEMENT_RESULT_SEMANTIC_SHA256 = (
    _implementation.STDLIB_STATEMENT_RESULT_SEMANTIC_SHA256
)
DW001CoveragePyBaselineError = _implementation.DW001CoveragePyBaselineError

compute_coveragepy_baseline_semantic_sha256 = (
    _implementation.compute_coveragepy_baseline_semantic_sha256
)
compute_coveragepy_baseline_report_sha256 = (
    _implementation.compute_coveragepy_baseline_report_sha256
)

# Deliberately module-scoped for fixed negative-result regressions. Product
# callers do not supply an executor. The lock prevents cross-call contamination.
_execute_selector = _implementation._execute_selector
_EXECUTOR_LOCK = RLock()


def _selector_status(raw: Mapping[str, object]) -> str:
    """Classify measurement completeness before candidate validity.

    A typed test failure can establish candidate invalidity only when its
    Coverage.py measurement is complete. Missing data, tool failure, timeout,
    or context ambiguity has precedence and remains indeterminate.
    """

    observed = raw.get("observed")
    if observed not in {"pass", "fail"}:
        return "indeterminate"
    receipt = raw.get("coverage_receipt")
    if not isinstance(receipt, dict):
        return "indeterminate"
    if receipt.get("measurement_status") != "complete":
        return "indeterminate"
    if observed == "fail":
        return "candidate_invalid"
    return "complete"


# The private verifier and aggregate derivation call this module global. Install
# the stricter precedence rule once at import; no Coverage.py import is added.
_implementation._selector_status = _selector_status


def run_claim_scoped_coveragepy_baseline(
    plan: object,
    catalog: object,
    mutation_result: object,
    stdlib_statement_result: object,
) -> dict[str, Any]:
    """Execute the fixed baseline with the controlled public test seam."""

    with _EXECUTOR_LOCK:
        original = _implementation._execute_selector
        _implementation._execute_selector = _execute_selector
        try:
            return _implementation.run_claim_scoped_coveragepy_baseline(
                plan,
                catalog,
                mutation_result,
                stdlib_statement_result,
            )
        finally:
            _implementation._execute_selector = original


def verify_claim_scoped_coveragepy_baseline_document(
    document: object,
    plan: object,
    catalog: object,
    mutation_result: object,
    stdlib_statement_result: object,
) -> tuple[bool, tuple[str, ...]]:
    """Independently reconstruct and verify one direct-baseline result."""

    return _implementation.verify_claim_scoped_coveragepy_baseline_document(
        document,
        plan,
        catalog,
        mutation_result,
        stdlib_statement_result,
    )


def load_claim_scoped_coveragepy_baseline(
    path: Path,
    plan: object,
    catalog: object,
    mutation_result: object,
    stdlib_statement_result: object,
) -> dict[str, Any]:
    """Strict-load and verify one bounded regular non-link result."""

    return _implementation.load_claim_scoped_coveragepy_baseline(
        path,
        plan,
        catalog,
        mutation_result,
        stdlib_statement_result,
    )


__all__ = [
    "ADAPTER_ID",
    "DW001CoveragePyBaselineError",
    "MUTATION_RESULT_SEMANTIC_SHA256",
    "RESULT_ID",
    "RESULT_SCHEMA_VERSION",
    "STDLIB_STATEMENT_RESULT_SEMANTIC_SHA256",
    "compute_coveragepy_baseline_report_sha256",
    "compute_coveragepy_baseline_semantic_sha256",
    "load_claim_scoped_coveragepy_baseline",
    "run_claim_scoped_coveragepy_baseline",
    "verify_claim_scoped_coveragepy_baseline_document",
]
