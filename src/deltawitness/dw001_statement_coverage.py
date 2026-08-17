"""Public statement-coverage baseline API for DW-001.

The implementation lives in the private sibling module. This facade keeps the
public surface narrow, provides the controlled observation seam used by
negative-result regressions, and independently reconstructs typed outcome
receipt evidence before accepting a coverage result.
"""

from __future__ import annotations

from threading import RLock
from typing import Any, Mapping

from . import __version__
from . import _dw001_statement_coverage as _implementation
from .receipt import build_receipt_document, validate_receipt_document


RESULT_SCHEMA_VERSION = _implementation.RESULT_SCHEMA_VERSION
RESULT_ID = _implementation.RESULT_ID
ADAPTER_ID = _implementation.ADAPTER_ID
MUTATION_RESULT_SEMANTIC_SHA256 = (
    _implementation.MUTATION_RESULT_SEMANTIC_SHA256
)
DW001StatementCoverageError = _implementation.DW001StatementCoverageError

# Deliberately module-scoped for red-first regressions that inject complete
# preregistration-divergent or indeterminate trace evidence. Product callers do
# not supply an executor. The lock prevents cross-call contamination.
_execute_selector = _implementation._execute_selector
_compute_trace_sha256 = _implementation._compute_trace_sha256
_EXECUTOR_LOCK = RLock()


def compute_statement_coverage_semantic_sha256(
    document: dict[str, Any],
) -> str:
    """Hash stable coverage and comparison semantics."""

    return _implementation.compute_statement_coverage_semantic_sha256(document)


def compute_statement_coverage_report_sha256(
    document: dict[str, Any],
) -> str:
    """Hash the complete result with only its report digest normalized."""

    return _implementation.compute_statement_coverage_report_sha256(document)


def _expected_counts(observed: str) -> dict[str, int]:
    if observed == "pass":
        return {
            "tests_run": 1,
            "passed": 1,
            "failures": 0,
            "errors": 0,
            "skipped": 0,
            "expected_failures": 0,
            "unexpected_successes": 0,
        }
    if observed == "fail":
        return {
            "tests_run": 1,
            "passed": 0,
            "failures": 1,
            "errors": 0,
            "skipped": 0,
            "expected_failures": 0,
            "unexpected_successes": 0,
        }
    raise ValueError(f"unsupported complete observation: {observed!r}")


def _expected_process_for_receipt(
    receipt_outcome: str,
) -> tuple[str, int, str | None]:
    """Reconstruct the fixed probe's process classification from one receipt."""

    if receipt_outcome == "passed":
        return "pass", 0, None
    if receipt_outcome == "test_failure":
        return "fail", 1, None
    return "error", 2, "receipt_exit_mismatch"


def _receipt_integrity_errors(
    document: object,
    plan: object,
    catalog: object,
    mutation_result: object,
) -> tuple[str, ...]:
    """Reconstruct every retained outcome receipt from frozen relations."""

    if not isinstance(document, dict):
        return ()
    try:
        normalized_plan, normalized_catalog, normalized_mutation = (
            _implementation._preflight(plan, catalog, mutation_result)
        )
        profiles = document.get("profiles")
        expected_profiles = normalized_plan["calibration_profiles"]
        source = normalized_plan["source_scope"]
        target = normalized_catalog["target"]
        if (
            not isinstance(profiles, list)
            or not isinstance(expected_profiles, list)
            or not isinstance(source, dict)
            or not isinstance(target, dict)
        ):
            return ()
        if len(profiles) != len(expected_profiles):
            return ()

        source_sha256 = str(source["source_sha256"])
        target_lines = _implementation._target_lines(normalized_catalog)
        target_id = str(target["target_id"])
        errors: list[str] = []

        for profile_index, (profile, expected_profile) in enumerate(
            zip(profiles, expected_profiles, strict=True)
        ):
            if not isinstance(profile, dict) or not isinstance(
                expected_profile, dict
            ):
                continue
            actual_selectors = profile.get("selectors")
            expected_selectors = expected_profile.get("selectors")
            profile_id = expected_profile.get("profile_id")
            if (
                not isinstance(actual_selectors, list)
                or not isinstance(expected_selectors, list)
                or not isinstance(profile_id, str)
                or len(actual_selectors) != len(expected_selectors)
            ):
                continue

            for selector_index, (record, selector_value) in enumerate(
                zip(actual_selectors, expected_selectors, strict=True)
            ):
                if not isinstance(record, dict) or not isinstance(
                    selector_value, str
                ):
                    continue
                context = (
                    "statement coverage result.profiles"
                    f"[{profile_index}].selectors[{selector_index}]"
                )
                test_sha256 = _implementation._sha256_bytes(
                    _implementation._test_bytes(selector_value)
                )
                command = _implementation._trace_command(
                    selector=selector_value,
                    source_sha256=source_sha256,
                    target_lines=target_lines,
                )
                binding = _implementation._invocation_binding(
                    plan_sha256=str(normalized_plan["plan_sha256"]),
                    catalog_sha256=str(normalized_catalog["catalog_sha256"]),
                    mutation_result_semantic_sha256=str(
                        normalized_mutation["semantic_sha256"]
                    ),
                    profile_id=profile_id,
                    selector=selector_value,
                    source_sha256=source_sha256,
                    test_sha256=test_sha256,
                    target_id=target_id,
                    target_lines=target_lines,
                    command=command,
                )

                receipt_sha256 = record.get("receipt_sha256")
                receipt_outcome = record.get("receipt_outcome")
                receipt_producer = record.get("receipt_producer")
                receipt_counts = record.get("receipt_counts")
                observed = record.get("observed")
                return_code = record.get("return_code")
                timed_out = record.get("timed_out")
                observation_error = record.get("observation_error")
                expected_producer = {
                    "name": "deltawitness-unittest",
                    "version": __version__,
                }

                if receipt_sha256 is None:
                    if any(
                        value is not None
                        for value in (
                            receipt_outcome,
                            receipt_producer,
                            receipt_counts,
                        )
                    ):
                        errors.append(
                            f"{context}.receipt_sha256: missing while receipt "
                            "fields are present"
                        )
                    if observed in {"pass", "fail"}:
                        errors.append(
                            f"{context}.receipt_sha256: required for "
                            f"observed={observed!r}"
                        )
                    elif observed == "timeout":
                        if (
                            timed_out is not True
                            or return_code is not None
                            or observation_error is not None
                        ):
                            errors.append(
                                f"{context}: timeout process fields are "
                                "inconsistent"
                            )
                    elif observed == "error":
                        if timed_out is not False:
                            errors.append(
                                f"{context}.timed_out: must be false for error"
                            )
                        if not isinstance(observation_error, str) or not (
                            observation_error
                        ):
                            errors.append(
                                f"{context}.observation_error: must identify "
                                "the missing or invalid receipt"
                            )
                    continue

                if timed_out is not False:
                    errors.append(
                        f"{context}.timed_out: a retained receipt requires "
                        "completed execution"
                    )
                if receipt_producer != expected_producer:
                    errors.append(
                        f"{context}.receipt_producer: does not match the "
                        "fixed typed producer"
                    )
                if not isinstance(receipt_outcome, str):
                    errors.append(
                        f"{context}.receipt_outcome: must be a string when a "
                        "receipt digest is present"
                    )
                    continue
                if not isinstance(receipt_counts, dict):
                    errors.append(
                        f"{context}.receipt_counts: must be an object when a "
                        "receipt digest is present"
                    )
                    continue

                try:
                    receipt_document = build_receipt_document(
                        binding=binding,
                        producer_name=expected_producer["name"],
                        producer_version=expected_producer["version"],
                        outcome=receipt_outcome,
                        counts=receipt_counts,
                    )
                    canonical = validate_receipt_document(
                        receipt_document,
                        expected_binding=binding,
                    )
                except Exception as exc:
                    errors.append(
                        f"{context}.receipt_counts/receipt_outcome: "
                        f"invalid typed receipt semantics ({type(exc).__name__})"
                    )
                    continue

                if receipt_sha256 != canonical.sha256:
                    errors.append(
                        f"{context}.receipt_sha256: does not match the "
                        "reconstructed typed receipt"
                    )

                (
                    expected_observed,
                    expected_return_code,
                    expected_observation_error,
                ) = _expected_process_for_receipt(receipt_outcome)
                if observed != expected_observed:
                    errors.append(
                        f"{context}.receipt_outcome: inconsistent with "
                        f"observed={observed!r}"
                    )
                if return_code != expected_return_code:
                    errors.append(
                        f"{context}.return_code: inconsistent with retained "
                        "typed receipt"
                    )
                if observation_error != expected_observation_error:
                    errors.append(
                        f"{context}.observation_error: inconsistent with "
                        "retained typed receipt"
                    )

                if expected_observed in {"pass", "fail"}:
                    expected_counts = _expected_counts(expected_observed)
                    if receipt_counts != expected_counts:
                        errors.append(
                            f"{context}.receipt_counts: inconsistent with one "
                            f"logical observed={expected_observed!r} selector"
                        )

        return tuple(dict.fromkeys(errors))
    except Exception:
        # Structural and source failures remain the responsibility of the
        # authoritative implementation verifier; this helper never broadens
        # acceptance when it cannot derive a safe relation.
        return ()


def run_claim_scoped_statement_coverage(
    plan: object,
    catalog: object,
    mutation_result: object,
) -> dict[str, Any]:
    """Execute the exact frozen selector profiles and verify both receipts."""

    with _EXECUTOR_LOCK:
        original = _implementation._execute_selector
        _implementation._execute_selector = _execute_selector
        try:
            result = _implementation.run_claim_scoped_statement_coverage(
                plan,
                catalog,
                mutation_result,
            )
        finally:
            _implementation._execute_selector = original

    valid, errors = verify_claim_scoped_statement_coverage_document(
        result,
        plan,
        catalog,
        mutation_result,
    )
    if not valid:
        raise DW001StatementCoverageError(
            "statement coverage facade self-verification: "
            + "; ".join(errors)
        )
    return result


def verify_claim_scoped_statement_coverage_document(
    document: object,
    plan: object,
    catalog: object,
    mutation_result: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify source, trace, typed receipt, aggregate, policy, and digests."""

    valid, implementation_errors = (
        _implementation.verify_claim_scoped_statement_coverage_document(
            document,
            plan,
            catalog,
            mutation_result,
        )
    )
    receipt_errors = _receipt_integrity_errors(
        document,
        plan,
        catalog,
        mutation_result,
    )
    errors = tuple(dict.fromkeys((*receipt_errors, *implementation_errors)))
    return valid and not receipt_errors, errors


__all__ = [
    "ADAPTER_ID",
    "DW001StatementCoverageError",
    "MUTATION_RESULT_SEMANTIC_SHA256",
    "RESULT_ID",
    "RESULT_SCHEMA_VERSION",
    "compute_statement_coverage_report_sha256",
    "compute_statement_coverage_semantic_sha256",
    "run_claim_scoped_statement_coverage",
    "verify_claim_scoped_statement_coverage_document",
]
