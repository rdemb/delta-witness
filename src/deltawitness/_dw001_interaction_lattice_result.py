"""Typed result for the frozen DW-001 selector-context interaction lattice.

The runner executes only the fixed project-owned candidate source and five
exact generated generic mutants from the merged preregistration. Candidate
selectors produce typed unittest and Coverage.py receipts. Mutant selectors
produce typed unittest receipts. Five profile views are derived from the four
unique selector observations rather than re-executed per profile.

Complete preregistration divergence is retained as ``unexpected``. Missing,
ambiguous, malformed, substituted, or contradictory evidence fails closed or
remains explicitly ``indeterminate``. The runner is an observation mechanism,
not a sandbox.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import math
from pathlib import Path
import platform
import stat
import tempfile
from typing import Any, Mapping, Sequence

from . import __version__
from .claim_witness import canonical_unittest_selector_command
from .coveragepy_contract import (
    COVERAGEPY_MANIFEST_SHA256,
    build_coveragepy_distribution_manifest,
)
from .coveragepy_probe import (
    COVERAGE_OUTPUT_BASENAME,
    CoveragePyProbeError,
    compute_coverage_receipt_sha256,
    load_coverage_receipt,
    validate_coverage_receipt,
)
from .dw001_interaction_lattice_execution import (
    EXECUTION_PROTOCOL_SHA256,
    PREREGISTRATION_MERGE_COMMIT,
    verify_interaction_lattice_execution_protocol_document,
)
from .dw001_interaction_lattice_plan import (
    CANDIDATE_SOURCE,
    SELECTOR_TEST_SOURCE,
    _mutated_source,
)
from .errors import DeltaWitnessError, ReportError
from .execution import run_command
from .receipt import build_receipt_document, validate_receipt_document
from .reporting import load_report, sha256_document


RESULT_SCHEMA_VERSION = (
    "deltawitness.dw001-interaction-witness-lattice-result.v1"
)
RESULT_ID = "DW-001-INTERACTION-WITNESS-LATTICE-RESULT-V1"
PLAN_SHA256 = (
    "a79a500feb94c8ad78fe4633f9ca176465113de6297db2d07b2d005f5318e1f1"
)
CATALOG_SHA256 = (
    "2b06a86180a45fcd495c0bcf39365dde0cb590507e9a3528714f9ef58526308e"
)
PRIOR_ART_LOG_SHA256 = (
    "af6cb9782ea01a0e58baed8cfc1a4895dc1a53ed934498b307c6b05e8634c44f"
)
PR46_RESULT_SEMANTIC_SHA256 = (
    "ec0c2fdd5ac24ba53eb895d9014aab623d2631125b8512ba0e0cbf5105f21ee8"
)
PR46_RESULT_REPORT_SHA256 = (
    "8b248757374ebff4195bad181ad02bc5b0bfc61fa2e21ebf45549686c33d2c41"
)

_BINDING_SCHEMA_VERSION = (
    "deltawitness.dw001-interaction-witness-lattice-invocation.v1"
)
_PATH_SHAPE_SCHEMA_VERSION = (
    "deltawitness.dw001-interaction-path-shape.v1"
)
_PATH_MULTISET_SCHEMA_VERSION = (
    "deltawitness.dw001-interaction-path-multiset.v1"
)
_SOURCE_PATH = "src/access.py"
_TEST_PATH = "tests/test_access.py"
_SOURCE_SYMBOL = "is_authorized"
_PRODUCER_NAME = "deltawitness-unittest"
_MAX_RESULT_BYTES = 4_000_000

_ROOT_FIELDS = {
    "schema_version",
    "study_id",
    "result_id",
    "partition",
    "preregistration_merge_commit",
    "execution_protocol_sha256",
    "plan_sha256",
    "catalog_sha256",
    "prior_art_log_sha256",
    "coveragepy_distribution_manifest_sha256",
    "pr46_result_semantic_sha256",
    "pr46_result_report_sha256",
    "created_at",
    "runtime",
    "distribution",
    "configuration",
    "source",
    "candidate_selectors",
    "profiles",
    "mutants",
    "summary",
    "comparison",
    "analysis",
    "policy",
    "cost",
    "semantic_sha256",
    "report_sha256",
}
_RUNTIME_FIELDS = {
    "tool_version",
    "python_implementation",
    "python_version",
    "platform_system",
}
_SOURCE_FIELDS = {
    "source_id",
    "path",
    "symbol",
    "source_sha256",
    "ast_sha256",
    "test_id",
    "test_path",
    "test_sha256",
    "target_id",
    "target_lines",
}
_CANDIDATE_FIELDS = {
    "order",
    "implementation_id",
    "quadrant_id",
    "selector_id",
    "selector",
    "input",
    "expected_decision",
    "source_sha256",
    "test_sha256",
    "target_id",
    "command",
    "context_id",
    "invocation_binding",
    "expected_observed",
    "observed",
    "outcome_concordant",
    "return_code",
    "timed_out",
    "duration_seconds",
    "stdout_sha256",
    "stderr_sha256",
    "receipt_sha256",
    "receipt_outcome",
    "receipt_producer",
    "receipt_counts",
    "observation_error",
    "coverage_status",
    "coverage_error",
    "coverage_receipt",
    "expected_path_shape_sha256",
    "path_shape",
    "path_concordant",
    "context_partition_valid",
    "concordant",
    "cost",
}
_PATH_SHAPE_FIELDS = {"statements", "arcs", "path_shape_sha256"}
_PATH_RECORD_FIELDS = {
    "quadrant_id",
    "selector_id",
    "selector",
    "context_id",
    "invocation_binding",
    "path_shape_sha256",
}
_CANDIDATE_COST_FIELDS = {
    "status",
    "process_wall_seconds",
    "coverage_wall_seconds",
    "coverage_cpu_seconds",
    "missing_reason",
}
_PROFILE_FIELDS = {
    "order",
    "profile_id",
    "profile_role",
    "quadrants",
    "selector_ids",
    "selector_count",
    "path_records",
    "expected_statement_union",
    "statement_union",
    "expected_statement_intersection",
    "statement_intersection",
    "expected_arc_union",
    "arc_union",
    "expected_arc_intersection",
    "arc_intersection",
    "expected_anonymous_path_multiset",
    "anonymous_path_multiset",
    "expected_mfa_independence_witness",
    "mfa_independence_witness",
    "expected_role_independence_witness",
    "role_independence_witness",
    "all_selectors_passed",
    "context_partition_valid",
    "coverage_status",
    "aggregate_concordant",
    "independence_concordant",
    "concordant",
    "cost",
}
_PROFILE_COST_FIELDS = {
    "status",
    "selector_count",
    "process_wall_seconds",
    "coverage_wall_seconds",
    "coverage_cpu_seconds",
    "missing_reason",
}
_MUTANT_SELECTOR_FIELDS = {
    "order",
    "implementation_id",
    "operator_id",
    "mutant_id",
    "quadrant_id",
    "selector_id",
    "selector",
    "source_sha256",
    "test_sha256",
    "command",
    "invocation_binding",
    "expected_observed",
    "observed",
    "status",
    "concordant",
    "return_code",
    "timed_out",
    "duration_seconds",
    "stdout_sha256",
    "stderr_sha256",
    "receipt_sha256",
    "receipt_outcome",
    "receipt_producer",
    "receipt_counts",
    "observation_error",
    "cost",
}
_MUTANT_SELECTOR_COST_FIELDS = {
    "status",
    "process_wall_seconds",
    "missing_reason",
}
_MUTANT_FIELDS = {
    "order",
    "implementation_id",
    "operator_id",
    "mutant_id",
    "source_sha256",
    "source_ast_sha256",
    "selectors",
    "selector_table_complete",
    "profile_outcomes",
    "concordant",
    "cost",
}
_MUTANT_PROFILE_FIELDS = {
    "profile_id",
    "expected_outcome",
    "outcome",
    "concordant",
}
_MUTANT_COST_FIELDS = {
    "status",
    "command_count",
    "selector_count",
    "process_wall_seconds",
    "missing_reason",
}
_SUMMARY_FIELDS = {
    "candidate_selector_count",
    "candidate_selector_complete_count",
    "mutant_count",
    "mutant_selector_count",
    "mutant_selector_complete_count",
    "selector_command_count",
    "generated_mutant_count",
    "duplicate_record_count",
    "invalid_record_count",
    "not_applicable_record_count",
    "mutation_score",
}
_COMPARISON_FIELDS = {
    "expected_statement_aggregate_discriminates_profiles",
    "statement_aggregate_discriminates_profiles",
    "expected_arc_aggregate_discriminates_profiles",
    "arc_aggregate_discriminates_profiles",
    "expected_anonymous_path_multiset_discriminates_profiles",
    "anonymous_path_multiset_discriminates_profiles",
    "expected_equal_cardinality_path_multisets_distinct",
    "equal_cardinality_path_multisets_distinct",
    "expected_mfa_independence_agrees_with_drop_mfa",
    "mfa_independence_agrees_with_drop_mfa",
    "expected_role_independence_agrees_with_drop_role",
    "role_independence_agrees_with_drop_role",
    "expected_any_independence_agrees_with_or_gates",
    "any_independence_agrees_with_or_gates",
    "concordant",
}
_ANALYSIS_FIELDS = {
    "status",
    "unexpected_candidate_selector_count",
    "indeterminate_candidate_selector_count",
    "unexpected_profile_count",
    "indeterminate_profile_count",
    "unexpected_mutant_selector_count",
    "indeterminate_mutant_selector_count",
    "unexpected_mutant_count",
    "indeterminate_mutant_count",
    "unexpected_candidate_selector_ids",
    "unexpected_profile_ids",
    "unexpected_mutant_ids",
    "comparison_concordant",
}
_POLICY_FIELDS = {
    "quality_score",
    "headline_score",
    "universal_threshold",
    "merge_blocker_authorized",
    "ecological_inference_allowed",
    "holdout_selected",
    "primary_denominator_eligible",
    "mcdc_certification_claim_allowed",
    "coverage_superiority_claim_allowed",
    "mutation_superiority_claim_allowed",
    "method_superiority_claim_allowed",
    "scientific_novelty_claim_allowed",
    "award_level_significance_claim_allowed",
    "production_readiness_claim_allowed",
}
_ROOT_COST_FIELDS = {
    "status",
    "implementation_count",
    "candidate_selector_count",
    "mutant_count",
    "mutant_selector_count",
    "selector_command_count",
    "process_wall_seconds",
    "coverage_wall_seconds",
    "coverage_cpu_seconds",
    "missing_reason",
}


class DW001InteractionLatticeResultError(DeltaWitnessError):
    """Raised when interaction-lattice execution or verification fails closed."""


def _error(context: str, message: str) -> DW001InteractionLatticeResultError:
    return DW001InteractionLatticeResultError(f"{context}: {message}")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _finite_nonnegative(value: object, *, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _error(context, "must be a finite nonnegative number")
    numeric = float(value)
    if not math.isfinite(numeric) or numeric < 0.0:
        raise _error(context, "must be a finite nonnegative number")
    return numeric


def _round_cost(value: float) -> float:
    return round(value, 6)


def _exact_keys(
    value: object,
    expected: set[str],
    *,
    context: str,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _error(context, "must be an object")
    actual = set(value)
    if actual != expected:
        raise _error(
            context,
            f"field mismatch; missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}",
        )
    return value


def _strict_equal(expected: object, observed: object) -> bool:
    if type(expected) is not type(observed):
        return False
    if isinstance(expected, dict):
        assert isinstance(observed, dict)
        return set(expected) == set(observed) and all(
            _strict_equal(expected[key], observed[key]) for key in expected
        )
    if isinstance(expected, list):
        assert isinstance(observed, list)
        return len(expected) == len(observed) and all(
            _strict_equal(left, right)
            for left, right in zip(expected, observed, strict=True)
        )
    return expected == observed


def _differences(
    expected: object,
    observed: object,
    *,
    context: str,
) -> list[str]:
    if type(expected) is not type(observed):
        return [f"{context}: type mismatch"]
    if isinstance(expected, dict):
        assert isinstance(observed, dict)
        errors: list[str] = []
        expected_keys = set(expected)
        observed_keys = set(observed)
        for key in sorted(expected_keys - observed_keys):
            errors.append(f"{context}.{key}: missing")
        for key in sorted(observed_keys - expected_keys):
            errors.append(f"{context}.{key}: unexpected")
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
        assert isinstance(observed, list)
        errors = []
        if len(expected) != len(observed):
            errors.append(
                f"{context}: length mismatch; expected {len(expected)}, "
                f"observed {len(observed)}"
            )
        for index, (left, right) in enumerate(
            zip(expected, observed, strict=False)
        ):
            errors.extend(
                _differences(
                    left,
                    right,
                    context=f"{context}[{index}]",
                )
            )
        return errors
    if expected != observed:
        return [f"{context}: value mismatch"]
    return []


def _configuration() -> dict[str, object]:
    return {
        "data_file": None,
        "auto_data": False,
        "timid": True,
        "branch": True,
        "config_file": False,
        "source_dirs": ["src"],
        "concurrency": None,
        "check_preimported": False,
        "context_strategy": "static-selector-context-v1",
        "messages": False,
        "plugins": [],
        "auto_start": False,
        "subprocess_measurement": False,
        "network_during_measurement": False,
    }


def _selector_configuration(context_id: str) -> dict[str, object]:
    value = _configuration()
    value.pop("context_strategy")
    value["context"] = context_id
    return value


def _policy() -> dict[str, object]:
    return {
        "quality_score": None,
        "headline_score": None,
        "universal_threshold": None,
        "merge_blocker_authorized": False,
        "ecological_inference_allowed": False,
        "holdout_selected": False,
        "primary_denominator_eligible": False,
        "mcdc_certification_claim_allowed": False,
        "coverage_superiority_claim_allowed": False,
        "mutation_superiority_claim_allowed": False,
        "method_superiority_claim_allowed": False,
        "scientific_novelty_claim_allowed": False,
        "award_level_significance_claim_allowed": False,
        "production_readiness_claim_allowed": False,
    }


def _source_view(
    plan: Mapping[str, object],
) -> dict[str, object]:
    source = plan["source_scope"]
    test = plan["test_scope"]
    target = plan["target_scope"]
    assert isinstance(source, dict)
    assert isinstance(test, dict)
    assert isinstance(target, dict)
    return {
        "source_id": source["source_id"],
        "path": source["path"],
        "symbol": source["symbol"],
        "source_sha256": source["source_sha256"],
        "ast_sha256": source["ast_sha256"],
        "test_id": test["test_id"],
        "test_path": test["path"],
        "test_sha256": test["test_sha256"],
        "target_id": target["target_id"],
        "target_lines": target["coverage_target_lines"],
    }


def _preflight(
    execution_protocol: object,
    plan: object,
    catalog: object,
    prior_art: object,
    coveragepy_manifest: object,
    pr46_result: object,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    valid, errors = verify_interaction_lattice_execution_protocol_document(
        execution_protocol,
        plan,
        catalog,
        prior_art,
        coveragepy_manifest,
        pr46_result,
    )
    if not valid:
        raise _error("interaction-lattice execution preflight", "; ".join(errors))
    values = (
        execution_protocol,
        plan,
        catalog,
        prior_art,
        coveragepy_manifest,
        pr46_result,
    )
    if not all(isinstance(value, dict) for value in values):
        raise _error("interaction-lattice preflight", "all sources must be objects")
    return values  # type: ignore[return-value]


def _context_id(quadrant_id: str, selector: str) -> str:
    return (
        "dw001-interaction-v1:candidate:"
        f"{quadrant_id}:{selector}"
    )


def _coverage_command(
    *,
    selector: str,
    source_sha256: str,
    target_lines: Sequence[int],
    context_id: str,
) -> list[str]:
    command = [
        "python",
        "-m",
        "deltawitness.coveragepy_probe",
        "--start-directory",
        "tests",
        "--verbosity",
        "0",
        "--test-name",
        selector,
        "--target-path",
        _SOURCE_PATH,
        "--target-symbol",
        _SOURCE_SYMBOL,
    ]
    for line in target_lines:
        command.extend(["--target-line", str(line)])
    command.extend(
        [
            "--source-sha256",
            source_sha256,
            "--context-id",
            context_id,
            "--coverage-output",
            COVERAGE_OUTPUT_BASENAME,
        ]
    )
    return command


def _binding(
    *,
    implementation_id: str,
    quadrant_id: str,
    selector_id: str,
    selector: str,
    source_sha256: str,
    test_sha256: str,
    target_id: str,
    context_id: str | None,
    command: Sequence[str],
) -> str:
    return sha256_document(
        {
            "schema_version": _BINDING_SCHEMA_VERSION,
            "result_id": RESULT_ID,
            "execution_protocol_sha256": EXECUTION_PROTOCOL_SHA256,
            "plan_sha256": PLAN_SHA256,
            "catalog_sha256": CATALOG_SHA256,
            "prior_art_log_sha256": PRIOR_ART_LOG_SHA256,
            "implementation_id": implementation_id,
            "quadrant_id": quadrant_id,
            "selector_id": selector_id,
            "selector": selector,
            "source_sha256": source_sha256,
            "test_sha256": test_sha256,
            "target_id": target_id,
            "context_id": context_id,
            "command": list(command),
            "observer": "outcome-receipt-v1",
            "coverage_observer": (
                "coveragepy-measurement-receipt.v1"
                if context_id is not None
                else None
            ),
            "producer": {
                "name": _PRODUCER_NAME,
                "version": __version__,
            },
        }
    )


def _classify_process(process: object) -> tuple[str, str | None]:
    if bool(getattr(process, "timed_out")):
        return "timeout", None
    receipt_error = getattr(process, "receipt_error")
    if receipt_error is not None:
        return "error", str(receipt_error)
    receipt_outcome = getattr(process, "receipt_outcome")
    return_code = getattr(process, "return_code")
    if receipt_outcome == "passed" and return_code == 0:
        return "pass", None
    if receipt_outcome == "test_failure" and return_code == 1:
        return "fail", None
    return "error", "receipt_exit_mismatch"


def _materialize(root: Path, source: str) -> None:
    (root / "src").mkdir()
    (root / "tests").mkdir()
    (root / _SOURCE_PATH).write_text(source, encoding="utf-8")
    (root / _TEST_PATH).write_text(SELECTOR_TEST_SOURCE, encoding="utf-8")


def _execute_candidate_selector(
    *,
    plan: Mapping[str, object],
    quadrant: Mapping[str, object],
) -> dict[str, Any]:
    source_sha256 = _sha256_bytes(CANDIDATE_SOURCE.encode("utf-8"))
    test_sha256 = _sha256_bytes(SELECTOR_TEST_SOURCE.encode("utf-8"))
    selector = str(quadrant["selector"])
    selector_id = str(quadrant["selector_id"])
    quadrant_id = str(quadrant["quadrant_id"])
    target = plan["target_scope"]
    assert isinstance(target, dict)
    target_lines = list(target["coverage_target_lines"])
    context_id = _context_id(quadrant_id, selector)
    command = _coverage_command(
        selector=selector,
        source_sha256=source_sha256,
        target_lines=target_lines,
        context_id=context_id,
    )
    binding = _binding(
        implementation_id="candidate-v1",
        quadrant_id=quadrant_id,
        selector_id=selector_id,
        selector=selector,
        source_sha256=source_sha256,
        test_sha256=test_sha256,
        target_id=str(target["target_id"]),
        context_id=context_id,
        command=command,
    )
    expected_target = {
        "path": _SOURCE_PATH,
        "symbol": _SOURCE_SYMBOL,
        "source_sha256": source_sha256,
        "target_lines": target_lines,
    }
    with tempfile.TemporaryDirectory(
        prefix="deltawitness-interaction-candidate-"
    ) as directory:
        root = Path(directory)
        _materialize(root, CANDIDATE_SOURCE)
        process = run_command(
            command,
            state=f"interaction:candidate:{quadrant_id}",
            cwd=root,
            timeout_seconds=30,
            pass_env=(),
            include_output=False,
            observer="outcome-receipt-v1",
            receipt_binding=binding,
        )
        coverage_path = root / COVERAGE_OUTPUT_BASENAME
        coverage_receipt: dict[str, Any] | None = None
        coverage_error: str | None = None
        if coverage_path.exists():
            try:
                coverage_receipt = load_coverage_receipt(
                    coverage_path,
                    expected_binding=binding,
                    expected_target=expected_target,
                    expected_context_id=context_id,
                    expected_configuration=_selector_configuration(context_id),
                    expected_manifest_sha256=COVERAGEPY_MANIFEST_SHA256,
                )
            except (CoveragePyProbeError, ReportError, DeltaWitnessError):
                coverage_error = "invalid_coverage_receipt"
        else:
            coverage_error = (
                "timeout" if process.timed_out else "missing_coverage_receipt"
            )
        if any(path.name.startswith(".coverage") for path in root.iterdir()):
            coverage_receipt = None
            coverage_error = "unexpected_coverage_data_file"
    observed, observation_error = _classify_process(process)
    if coverage_receipt is not None:
        if coverage_receipt["measurement_status"] == "complete":
            coverage_error = None
        else:
            coverage_error = str(coverage_receipt["measurement_error"])
    return {
        "order": quadrant["order"],
        "implementation_id": "candidate-v1",
        "quadrant_id": quadrant_id,
        "selector_id": selector_id,
        "selector": selector,
        "input": deepcopy(quadrant["input"]),
        "expected_decision": quadrant["expected_decision"],
        "source_sha256": source_sha256,
        "test_sha256": test_sha256,
        "target_id": target["target_id"],
        "command": command,
        "context_id": context_id,
        "invocation_binding": binding,
        "observed": observed,
        "return_code": process.return_code,
        "timed_out": process.timed_out,
        "duration_seconds": process.duration_seconds,
        "stdout_sha256": process.stdout_sha256,
        "stderr_sha256": process.stderr_sha256,
        "receipt_sha256": process.receipt_sha256,
        "receipt_outcome": process.receipt_outcome,
        "receipt_producer": process.receipt_producer,
        "receipt_counts": process.receipt_counts,
        "observation_error": observation_error,
        "coverage_receipt": coverage_receipt,
        "coverage_error": coverage_error,
    }


def _execute_mutant_selector(
    *,
    plan: Mapping[str, object],
    mutant: Mapping[str, object],
    source: str,
    quadrant: Mapping[str, object],
) -> dict[str, Any]:
    source_sha256 = _sha256_bytes(source.encode("utf-8"))
    test_sha256 = _sha256_bytes(SELECTOR_TEST_SOURCE.encode("utf-8"))
    selector = str(quadrant["selector"])
    command = canonical_unittest_selector_command(selector)
    implementation_id = f"mutant:{mutant['mutant_id']}"
    target = plan["target_scope"]
    assert isinstance(target, dict)
    binding = _binding(
        implementation_id=implementation_id,
        quadrant_id=str(quadrant["quadrant_id"]),
        selector_id=str(quadrant["selector_id"]),
        selector=selector,
        source_sha256=source_sha256,
        test_sha256=test_sha256,
        target_id=str(target["target_id"]),
        context_id=None,
        command=command,
    )
    with tempfile.TemporaryDirectory(
        prefix="deltawitness-interaction-mutant-"
    ) as directory:
        root = Path(directory)
        _materialize(root, source)
        process = run_command(
            command,
            state=(
                f"interaction:{mutant['operator_id']}:"
                f"{quadrant['quadrant_id']}"
            ),
            cwd=root,
            timeout_seconds=30,
            pass_env=(),
            include_output=False,
            observer="outcome-receipt-v1",
            receipt_binding=binding,
        )
    observed, observation_error = _classify_process(process)
    return {
        "order": quadrant["order"],
        "implementation_id": implementation_id,
        "operator_id": mutant["operator_id"],
        "mutant_id": mutant["mutant_id"],
        "quadrant_id": quadrant["quadrant_id"],
        "selector_id": quadrant["selector_id"],
        "selector": selector,
        "source_sha256": source_sha256,
        "test_sha256": test_sha256,
        "command": command,
        "invocation_binding": binding,
        "observed": observed,
        "return_code": process.return_code,
        "timed_out": process.timed_out,
        "duration_seconds": process.duration_seconds,
        "stdout_sha256": process.stdout_sha256,
        "stderr_sha256": process.stderr_sha256,
        "receipt_sha256": process.receipt_sha256,
        "receipt_outcome": process.receipt_outcome,
        "receipt_producer": process.receipt_producer,
        "receipt_counts": process.receipt_counts,
        "observation_error": observation_error,
    }


def _expected_mutant_decision(
    operator_id: str,
    quadrant: Mapping[str, object],
) -> bool:
    role_ok = bool(quadrant["role_ok"])
    mfa_ok = bool(quadrant["mfa_ok"])
    if operator_id == "drop-mfa-conjunct-v1":
        return role_ok
    if operator_id == "drop-role-conjunct-v1":
        return mfa_ok
    if operator_id == "or-gates-v1":
        return role_ok or mfa_ok
    if operator_id == "constant-false-v1":
        return False
    if operator_id == "constant-true-v1":
        return True
    raise _error("interaction mutant expectation", f"unsupported {operator_id!r}")


def _expected_mutant_observed(
    operator_id: str,
    quadrant: Mapping[str, object],
) -> str:
    return (
        "pass"
        if _expected_mutant_decision(operator_id, quadrant)
        == bool(quadrant["expected_decision"])
        else "fail"
    )


def _counts(observed: str) -> dict[str, int]:
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
    raise _error("interaction receipt counts", f"unsupported {observed!r}")


def _receipt_outcome(observed: str) -> str:
    if observed == "pass":
        return "passed"
    if observed == "fail":
        return "test_failure"
    raise _error("interaction receipt outcome", f"unsupported {observed!r}")


def _validate_process_fields(
    record: Mapping[str, object],
    *,
    binding: str,
    context: str,
) -> None:
    _finite_nonnegative(
        record["duration_seconds"],
        context=f"{context}.duration_seconds",
    )
    for field in ("stdout_sha256", "stderr_sha256"):
        if not _is_sha256(record[field]):
            raise _error(f"{context}.{field}", "must be a SHA-256 digest")
    observed = record["observed"]
    if observed not in {"pass", "fail", "error", "timeout"}:
        raise _error(f"{context}.observed", "is unsupported")
    receipt_sha256 = record["receipt_sha256"]
    if observed == "timeout":
        if (
            record["timed_out"] is not True
            or record["return_code"] is not None
            or receipt_sha256 is not None
            or record["receipt_outcome"] is not None
            or record["receipt_producer"] is not None
            or record["receipt_counts"] is not None
            or record["observation_error"] is not None
        ):
            raise _error(context, "timeout process fields are inconsistent")
        return
    if observed == "error" and receipt_sha256 is None:
        if record["timed_out"] is not False:
            raise _error(f"{context}.timed_out", "must be false for error")
        if (
            not isinstance(record["observation_error"], str)
            or not record["observation_error"]
        ):
            raise _error(
                f"{context}.observation_error",
                "must identify incomplete typed evidence",
            )
        return
    if observed not in {"pass", "fail"}:
        raise _error(context, "normal receipt cannot classify as error")
    if record["timed_out"] is not False:
        raise _error(f"{context}.timed_out", "must be false")
    if record["return_code"] != (0 if observed == "pass" else 1):
        raise _error(f"{context}.return_code", "does not match outcome")
    expected_outcome = _receipt_outcome(observed)
    expected_counts = _counts(observed)
    if record["receipt_outcome"] != expected_outcome:
        raise _error(f"{context}.receipt_outcome", "does not match outcome")
    if record["receipt_counts"] != expected_counts:
        raise _error(f"{context}.receipt_counts", "must represent one test")
    producer = {
        "name": _PRODUCER_NAME,
        "version": __version__,
    }
    if record["receipt_producer"] != producer:
        raise _error(f"{context}.receipt_producer", "is unsupported")
    receipt = validate_receipt_document(
        build_receipt_document(
            binding=binding,
            producer_name=_PRODUCER_NAME,
            producer_version=__version__,
            outcome=expected_outcome,
            counts=expected_counts,
        ),
        expected_binding=binding,
    )
    if receipt_sha256 != receipt.sha256:
        raise _error(f"{context}.receipt_sha256", "digest mismatch")
    if record["observation_error"] is not None:
        raise _error(f"{context}.observation_error", "must be null")


def _path_shape(
    statements: Sequence[int],
    arcs: Sequence[Sequence[int]],
) -> dict[str, object]:
    statement_values = list(statements)
    arc_values = [list(arc) for arc in arcs]
    document = {
        "statements": statement_values,
        "arcs": arc_values,
        "path_shape_sha256": sha256_document(
            {
                "schema_version": _PATH_SHAPE_SCHEMA_VERSION,
                "statements": statement_values,
                "arcs": arc_values,
            }
        ),
    }
    return document


def build_anonymous_result_path_multiset(
    path_records: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    digests: list[str] = []
    for index, record in enumerate(path_records):
        digest = record.get("path_shape_sha256")
        if not _is_sha256(digest):
            raise _error(
                f"interaction path record {index}.path_shape_sha256",
                "is invalid",
            )
        digests.append(str(digest))
    counts = Counter(digests)
    records = [
        {"path_shape_sha256": digest, "count": counts[digest]}
        for digest in sorted(counts)
    ]
    return {
        "multiplicity_semantics": "multiset",
        "records": records,
        "anonymous_path_multiset_sha256": sha256_document(
            {
                "schema_version": _PATH_MULTISET_SCHEMA_VERSION,
                "records": records,
            }
        ),
    }


def _candidate_cost(raw: Mapping[str, object]) -> dict[str, object]:
    process_wall = _finite_nonnegative(
        raw["duration_seconds"],
        context="interaction candidate process cost",
    )
    receipt = raw.get("coverage_receipt")
    if isinstance(receipt, dict):
        cost = receipt.get("cost")
        if not isinstance(cost, dict):
            raise _error("interaction candidate Coverage.py cost", "is missing")
        coverage_wall = _finite_nonnegative(
            cost.get("wall_clock_seconds"),
            context="interaction candidate coverage wall cost",
        )
        coverage_cpu = _finite_nonnegative(
            cost.get("cpu_seconds"),
            context="interaction candidate coverage CPU cost",
        )
        return {
            "status": "measured",
            "process_wall_seconds": _round_cost(process_wall),
            "coverage_wall_seconds": _round_cost(coverage_wall),
            "coverage_cpu_seconds": _round_cost(coverage_cpu),
            "missing_reason": None,
        }
    return {
        "status": "partial",
        "process_wall_seconds": _round_cost(process_wall),
        "coverage_wall_seconds": None,
        "coverage_cpu_seconds": None,
        "missing_reason": "coverage_receipt_unavailable",
    }


def _canonical_candidate(
    raw: Mapping[str, object],
    *,
    plan: Mapping[str, object],
    quadrant: Mapping[str, object],
) -> dict[str, Any]:
    expected_source = str(plan["source_scope"]["source_sha256"])
    expected_test = str(plan["test_scope"]["test_sha256"])
    target = plan["target_scope"]
    assert isinstance(target, dict)
    selector = str(quadrant["selector"])
    selector_id = str(quadrant["selector_id"])
    quadrant_id = str(quadrant["quadrant_id"])
    context_id = _context_id(quadrant_id, selector)
    command = _coverage_command(
        selector=selector,
        source_sha256=expected_source,
        target_lines=list(target["coverage_target_lines"]),
        context_id=context_id,
    )
    binding = _binding(
        implementation_id="candidate-v1",
        quadrant_id=quadrant_id,
        selector_id=selector_id,
        selector=selector,
        source_sha256=expected_source,
        test_sha256=expected_test,
        target_id=str(target["target_id"]),
        context_id=context_id,
        command=command,
    )
    static = {
        "order": quadrant["order"],
        "implementation_id": "candidate-v1",
        "quadrant_id": quadrant_id,
        "selector_id": selector_id,
        "selector": selector,
        "input": deepcopy(quadrant["input"]),
        "expected_decision": quadrant["expected_decision"],
        "source_sha256": expected_source,
        "test_sha256": expected_test,
        "target_id": target["target_id"],
        "command": command,
        "context_id": context_id,
        "invocation_binding": binding,
    }
    for field, expected in static.items():
        if not _strict_equal(raw.get(field), expected):
            raise _error(
                f"interaction candidate {quadrant_id}.{field}",
                "does not match the frozen relation",
            )
    _validate_process_fields(
        raw,
        binding=binding,
        context=f"interaction candidate {quadrant_id}",
    )
    observed = str(raw["observed"])
    outcome_concordant = observed == "pass"
    coverage_receipt_raw = raw.get("coverage_receipt")
    coverage_error = raw.get("coverage_error")
    coverage_receipt: dict[str, Any] | None = None
    coverage_status = "indeterminate"
    path_shape: dict[str, object] | None = None
    context_partition_valid = False
    if coverage_receipt_raw is not None:
        coverage_receipt = validate_coverage_receipt(
            coverage_receipt_raw,
            expected_binding=binding,
            expected_target={
                "path": _SOURCE_PATH,
                "symbol": _SOURCE_SYMBOL,
                "source_sha256": expected_source,
                "target_lines": list(target["coverage_target_lines"]),
            },
            expected_context_id=context_id,
            expected_configuration=_selector_configuration(context_id),
            expected_manifest_sha256=COVERAGEPY_MANIFEST_SHA256,
        )
        if coverage_receipt["measurement_status"] == "complete":
            coverage_status = "complete"
            if coverage_error is not None:
                raise _error(
                    f"interaction candidate {quadrant_id}.coverage_error",
                    "must be null for complete measurement",
                )
            statement = coverage_receipt["statement_evidence"]
            branch = coverage_receipt["branch_evidence"]
            context = coverage_receipt["context_evidence"]
            assert isinstance(statement, dict)
            assert isinstance(branch, dict)
            assert isinstance(context, dict)
            path_shape = _path_shape(
                statement["executed"],
                branch["context_arcs"],
            )
            context_partition_valid = context["partition_valid"] is True
        else:
            expected_error = coverage_receipt["measurement_error"]
            if coverage_error != expected_error:
                raise _error(
                    f"interaction candidate {quadrant_id}.coverage_error",
                    "must match indeterminate receipt",
                )
    else:
        if not isinstance(coverage_error, str) or not coverage_error:
            raise _error(
                f"interaction candidate {quadrant_id}.coverage_error",
                "must identify unavailable measurement",
            )
    expected_path = next(
        item
        for item in plan["structural_hypotheses"]["quadrant_paths"]
        if item["quadrant_id"] == quadrant_id
    )
    expected_path_sha = expected_path["expected_path_shape_sha256"]
    path_concordant = (
        coverage_status == "complete"
        and path_shape is not None
        and path_shape["path_shape_sha256"] == expected_path_sha
    )
    cost = _candidate_cost(raw)
    return {
        **static,
        "expected_observed": "pass",
        "observed": observed,
        "outcome_concordant": outcome_concordant,
        "return_code": raw["return_code"],
        "timed_out": raw["timed_out"],
        "duration_seconds": raw["duration_seconds"],
        "stdout_sha256": raw["stdout_sha256"],
        "stderr_sha256": raw["stderr_sha256"],
        "receipt_sha256": raw["receipt_sha256"],
        "receipt_outcome": raw["receipt_outcome"],
        "receipt_producer": deepcopy(raw["receipt_producer"]),
        "receipt_counts": deepcopy(raw["receipt_counts"]),
        "observation_error": raw["observation_error"],
        "coverage_status": coverage_status,
        "coverage_error": coverage_error,
        "coverage_receipt": coverage_receipt,
        "expected_path_shape_sha256": expected_path_sha,
        "path_shape": path_shape,
        "path_concordant": path_concordant,
        "context_partition_valid": context_partition_valid,
        "concordant": (
            outcome_concordant
            and coverage_status == "complete"
            and path_concordant
            and context_partition_valid
        ),
        "cost": cost,
    }


def _mutant_selector_cost(raw: Mapping[str, object]) -> dict[str, object]:
    return {
        "status": "measured",
        "process_wall_seconds": _round_cost(
            _finite_nonnegative(
                raw["duration_seconds"],
                context="interaction mutant selector cost",
            )
        ),
        "missing_reason": None,
    }


def _canonical_mutant_selector(
    raw: Mapping[str, object],
    *,
    plan: Mapping[str, object],
    mutant: Mapping[str, object],
    quadrant: Mapping[str, object],
) -> dict[str, Any]:
    status, source, ast_sha256, compile_valid, _ = _mutated_source(
        str(mutant["operator_id"])
    )
    if status != "generated" or source is None or compile_valid is not True:
        raise _error("interaction mutant source", "is not executable")
    source_sha256 = _sha256_bytes(source.encode("utf-8"))
    if source_sha256 != mutant["mutated_source_sha256"]:
        raise _error("interaction mutant source", "digest mismatch")
    if ast_sha256 != mutant["mutated_ast_sha256"]:
        raise _error("interaction mutant AST", "digest mismatch")
    test_sha256 = str(plan["test_scope"]["test_sha256"])
    selector = str(quadrant["selector"])
    command = canonical_unittest_selector_command(selector)
    implementation_id = f"mutant:{mutant['mutant_id']}"
    target = plan["target_scope"]
    assert isinstance(target, dict)
    binding = _binding(
        implementation_id=implementation_id,
        quadrant_id=str(quadrant["quadrant_id"]),
        selector_id=str(quadrant["selector_id"]),
        selector=selector,
        source_sha256=source_sha256,
        test_sha256=test_sha256,
        target_id=str(target["target_id"]),
        context_id=None,
        command=command,
    )
    static = {
        "order": quadrant["order"],
        "implementation_id": implementation_id,
        "operator_id": mutant["operator_id"],
        "mutant_id": mutant["mutant_id"],
        "quadrant_id": quadrant["quadrant_id"],
        "selector_id": quadrant["selector_id"],
        "selector": selector,
        "source_sha256": source_sha256,
        "test_sha256": test_sha256,
        "command": command,
        "invocation_binding": binding,
    }
    for field, expected in static.items():
        if not _strict_equal(raw.get(field), expected):
            raise _error(
                f"interaction mutant {mutant['operator_id']}/"
                f"{quadrant['quadrant_id']}.{field}",
                "does not match the frozen relation",
            )
    _validate_process_fields(
        raw,
        binding=binding,
        context=(
            f"interaction mutant {mutant['operator_id']}/"
            f"{quadrant['quadrant_id']}"
        ),
    )
    observed = str(raw["observed"])
    expected_observed = _expected_mutant_observed(
        str(mutant["operator_id"]), quadrant
    )
    selector_status = (
        "complete" if observed in {"pass", "fail"} else "indeterminate"
    )
    return {
        **static,
        "expected_observed": expected_observed,
        "observed": observed,
        "status": selector_status,
        "concordant": (
            selector_status == "complete" and observed == expected_observed
        ),
        "return_code": raw["return_code"],
        "timed_out": raw["timed_out"],
        "duration_seconds": raw["duration_seconds"],
        "stdout_sha256": raw["stdout_sha256"],
        "stderr_sha256": raw["stderr_sha256"],
        "receipt_sha256": raw["receipt_sha256"],
        "receipt_outcome": raw["receipt_outcome"],
        "receipt_producer": deepcopy(raw["receipt_producer"]),
        "receipt_counts": deepcopy(raw["receipt_counts"]),
        "observation_error": raw["observation_error"],
        "cost": _mutant_selector_cost(raw),
    }


def _profile_cost(
    selectors: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    costs = [selector["cost"] for selector in selectors]
    assert all(isinstance(cost, dict) for cost in costs)
    complete = all(cost["status"] == "measured" for cost in costs)
    process = sum(float(cost["process_wall_seconds"]) for cost in costs)
    wall_values = [cost["coverage_wall_seconds"] for cost in costs]
    cpu_values = [cost["coverage_cpu_seconds"] for cost in costs]
    coverage_wall = (
        sum(float(value) for value in wall_values)
        if all(value is not None for value in wall_values)
        else None
    )
    coverage_cpu = (
        sum(float(value) for value in cpu_values)
        if all(value is not None for value in cpu_values)
        else None
    )
    return {
        "status": "measured" if complete else "partial",
        "selector_count": len(selectors),
        "process_wall_seconds": _round_cost(process),
        "coverage_wall_seconds": (
            None if coverage_wall is None else _round_cost(coverage_wall)
        ),
        "coverage_cpu_seconds": (
            None if coverage_cpu is None else _round_cost(coverage_cpu)
        ),
        "missing_reason": (
            None if complete else "selector_coverage_cost_unavailable"
        ),
    }


def _sets(
    selectors: Sequence[Mapping[str, object]],
    *,
    evidence: str,
    field: str,
) -> tuple[list[Any], list[Any]]:
    values: list[set[Any]] = []
    for selector in selectors:
        receipt = selector["coverage_receipt"]
        assert isinstance(receipt, dict)
        block = receipt[evidence]
        assert isinstance(block, dict)
        if field == "context_arcs":
            values.append({tuple(arc) for arc in block[field]})
        else:
            values.append(set(block[field]))
    union = set().union(*values)
    intersection = set.intersection(*values)
    if field == "context_arcs":
        return (
            [list(item) for item in sorted(union)],
            [list(item) for item in sorted(intersection)],
        )
    return sorted(union), sorted(intersection)


def _build_profile(
    definition: Mapping[str, object],
    *,
    candidate_by_quadrant: Mapping[str, Mapping[str, object]],
) -> dict[str, Any]:
    quadrants = list(definition["quadrants"])
    selectors = [candidate_by_quadrant[str(item)] for item in quadrants]
    coverage_status = (
        "complete"
        if all(selector["coverage_status"] == "complete" for selector in selectors)
        else "indeterminate"
    )
    path_records: list[dict[str, object]] = []
    if coverage_status == "complete":
        statement_union, statement_intersection = _sets(
            selectors,
            evidence="statement_evidence",
            field="executed",
        )
        arc_union, arc_intersection = _sets(
            selectors,
            evidence="branch_evidence",
            field="context_arcs",
        )
        for selector in selectors:
            path_shape = selector["path_shape"]
            assert isinstance(path_shape, dict)
            path_records.append(
                {
                    "quadrant_id": selector["quadrant_id"],
                    "selector_id": selector["selector_id"],
                    "selector": selector["selector"],
                    "context_id": selector["context_id"],
                    "invocation_binding": selector["invocation_binding"],
                    "path_shape_sha256": path_shape["path_shape_sha256"],
                }
            )
        path_multiset = build_anonymous_result_path_multiset(path_records)
    else:
        statement_union = None
        statement_intersection = None
        arc_union = None
        arc_intersection = None
        path_multiset = None
    expected_multiset = deepcopy(definition["expected_anonymous_path_multiset"])
    aggregate_concordant = (
        coverage_status == "complete"
        and statement_union == definition["expected_statement_union"]
        and statement_intersection
        == definition["expected_statement_intersection"]
        and arc_union == definition["expected_arc_union"]
        and arc_intersection == definition["expected_arc_intersection"]
        and path_multiset == expected_multiset
    )
    quadrant_set = set(quadrants)
    mfa_witness = {"TT", "TF"}.issubset(quadrant_set)
    role_witness = {"TT", "FT"}.issubset(quadrant_set)
    independence_concordant = (
        mfa_witness == definition["expected_mfa_independence_witness"]
        and role_witness == definition["expected_role_independence_witness"]
    )
    all_passed = all(selector["observed"] == "pass" for selector in selectors)
    context_valid = (
        coverage_status == "complete"
        and all(selector["context_partition_valid"] is True for selector in selectors)
    )
    return {
        "order": definition["order"],
        "profile_id": definition["profile_id"],
        "profile_role": definition["profile_role"],
        "quadrants": quadrants,
        "selector_ids": deepcopy(definition["selector_ids"]),
        "selector_count": len(selectors),
        "path_records": path_records,
        "expected_statement_union": deepcopy(
            definition["expected_statement_union"]
        ),
        "statement_union": statement_union,
        "expected_statement_intersection": deepcopy(
            definition["expected_statement_intersection"]
        ),
        "statement_intersection": statement_intersection,
        "expected_arc_union": deepcopy(definition["expected_arc_union"]),
        "arc_union": arc_union,
        "expected_arc_intersection": deepcopy(
            definition["expected_arc_intersection"]
        ),
        "arc_intersection": arc_intersection,
        "expected_anonymous_path_multiset": expected_multiset,
        "anonymous_path_multiset": path_multiset,
        "expected_mfa_independence_witness": (
            definition["expected_mfa_independence_witness"]
        ),
        "mfa_independence_witness": mfa_witness,
        "expected_role_independence_witness": (
            definition["expected_role_independence_witness"]
        ),
        "role_independence_witness": role_witness,
        "all_selectors_passed": all_passed,
        "context_partition_valid": context_valid,
        "coverage_status": coverage_status,
        "aggregate_concordant": aggregate_concordant,
        "independence_concordant": independence_concordant,
        "concordant": (
            all_passed
            and context_valid
            and aggregate_concordant
            and independence_concordant
            and all(selector["concordant"] is True for selector in selectors)
        ),
        "cost": _profile_cost(selectors),
    }


def _profile_outcome(
    selectors: Sequence[Mapping[str, object]],
) -> str:
    if any(selector["status"] != "complete" for selector in selectors):
        return "indeterminate"
    return (
        "survived"
        if all(selector["observed"] == "pass" for selector in selectors)
        else "killed"
    )


def _mutant_cost(
    selectors: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    complete = all(selector["cost"]["status"] == "measured" for selector in selectors)
    process = sum(
        float(selector["cost"]["process_wall_seconds"])
        for selector in selectors
    )
    return {
        "status": "measured" if complete else "partial",
        "command_count": len(selectors),
        "selector_count": len(selectors),
        "process_wall_seconds": _round_cost(process),
        "missing_reason": None if complete else "selector_cost_unavailable",
    }


def _build_mutant(
    catalog_record: Mapping[str, object],
    selectors: list[dict[str, Any]],
    *,
    plan: Mapping[str, object],
) -> dict[str, Any]:
    expected_rows = {
        row["operator_id"]: row["profile_outcomes"]
        for row in plan["future_execution_contract"]["expected_mutation_matrix"]
    }
    expected_by_profile = {
        item["profile_id"]: item["expected_outcome"]
        for item in expected_rows[catalog_record["operator_id"]]
    }
    by_quadrant = {str(item["quadrant_id"]): item for item in selectors}
    profile_outcomes: list[dict[str, object]] = []
    for definition in plan["profiles"]:
        selected = [
            by_quadrant[str(quadrant)]
            for quadrant in definition["quadrants"]
        ]
        outcome = _profile_outcome(selected)
        expected = expected_by_profile[definition["profile_id"]]
        profile_outcomes.append(
            {
                "profile_id": definition["profile_id"],
                "expected_outcome": expected,
                "outcome": outcome,
                "concordant": outcome == expected,
            }
        )
    complete = all(selector["status"] == "complete" for selector in selectors)
    return {
        "order": catalog_record["order"],
        "implementation_id": f"mutant:{catalog_record['mutant_id']}",
        "operator_id": catalog_record["operator_id"],
        "mutant_id": catalog_record["mutant_id"],
        "source_sha256": catalog_record["mutated_source_sha256"],
        "source_ast_sha256": catalog_record["mutated_ast_sha256"],
        "selectors": selectors,
        "selector_table_complete": complete,
        "profile_outcomes": profile_outcomes,
        "concordant": (
            complete
            and all(selector["concordant"] is True for selector in selectors)
            and all(item["concordant"] is True for item in profile_outcomes)
        ),
        "cost": _mutant_cost(selectors),
    }


def _comparison(
    profiles: Sequence[Mapping[str, object]],
    mutants: Sequence[Mapping[str, object]],
) -> dict[str, Any]:
    profile_complete = all(
        profile["coverage_status"] == "complete" for profile in profiles
    )
    if profile_complete:
        statement_signatures = {
            (
                tuple(profile["statement_union"]),
                tuple(profile["statement_intersection"]),
            )
            for profile in profiles
        }
        arc_signatures = {
            (
                tuple(tuple(arc) for arc in profile["arc_union"]),
                tuple(tuple(arc) for arc in profile["arc_intersection"]),
            )
            for profile in profiles
        }
        path_signatures = {
            profile["anonymous_path_multiset"][
                "anonymous_path_multiset_sha256"
            ]
            for profile in profiles
        }
        equal_cardinality = {
            profile["anonymous_path_multiset"][
                "anonymous_path_multiset_sha256"
            ]
            for profile in profiles
            if profile["selector_count"] == 3
        }
        statement_discriminates: bool | None = len(statement_signatures) > 1
        arc_discriminates: bool | None = len(arc_signatures) > 1
        path_discriminates: bool | None = len(path_signatures) > 1
        equal_cardinality_distinct: bool | None = len(equal_cardinality) == 3
    else:
        statement_discriminates = None
        arc_discriminates = None
        path_discriminates = None
        equal_cardinality_distinct = None

    mutant_by_operator = {str(item["operator_id"]): item for item in mutants}
    profile_by_id = {str(item["profile_id"]): item for item in profiles}

    def agreement(operator_id: str, relation: str) -> bool | None:
        mutant = mutant_by_operator[operator_id]
        outcomes = {
            str(item["profile_id"]): item["outcome"]
            for item in mutant["profile_outcomes"]
        }
        if any(value == "indeterminate" for value in outcomes.values()):
            return None
        for profile_id, profile in profile_by_id.items():
            if relation == "mfa":
                witness = bool(profile["mfa_independence_witness"])
            elif relation == "role":
                witness = bool(profile["role_independence_witness"])
            else:
                witness = bool(profile["mfa_independence_witness"]) or bool(
                    profile["role_independence_witness"]
                )
            if witness != (outcomes[profile_id] == "killed"):
                return False
        return True

    mfa_agree = agreement("drop-mfa-conjunct-v1", "mfa")
    role_agree = agreement("drop-role-conjunct-v1", "role")
    or_agree = agreement("or-gates-v1", "any")
    expected = {
        "expected_statement_aggregate_discriminates_profiles": False,
        "expected_arc_aggregate_discriminates_profiles": False,
        "expected_anonymous_path_multiset_discriminates_profiles": True,
        "expected_equal_cardinality_path_multisets_distinct": True,
        "expected_mfa_independence_agrees_with_drop_mfa": True,
        "expected_role_independence_agrees_with_drop_role": True,
        "expected_any_independence_agrees_with_or_gates": True,
    }
    observed = {
        "statement_aggregate_discriminates_profiles": statement_discriminates,
        "arc_aggregate_discriminates_profiles": arc_discriminates,
        "anonymous_path_multiset_discriminates_profiles": path_discriminates,
        "equal_cardinality_path_multisets_distinct": equal_cardinality_distinct,
        "mfa_independence_agrees_with_drop_mfa": mfa_agree,
        "role_independence_agrees_with_drop_role": role_agree,
        "any_independence_agrees_with_or_gates": or_agree,
    }
    concordant = all(
        observed[key.removeprefix("expected_")] == value
        for key, value in expected.items()
    )
    return {**expected, **observed, "concordant": concordant}


def _analysis(
    candidates: Sequence[Mapping[str, object]],
    profiles: Sequence[Mapping[str, object]],
    mutants: Sequence[Mapping[str, object]],
    comparison: Mapping[str, object],
) -> dict[str, Any]:
    unexpected_candidates = [
        str(item["selector_id"])
        for item in candidates
        if item["coverage_status"] == "complete" and item["concordant"] is not True
    ]
    indeterminate_candidates = sum(
        item["coverage_status"] != "complete" for item in candidates
    )
    unexpected_profiles = [
        str(item["profile_id"])
        for item in profiles
        if item["coverage_status"] == "complete" and item["concordant"] is not True
    ]
    indeterminate_profiles = sum(
        item["coverage_status"] != "complete" for item in profiles
    )
    mutant_selectors = [
        selector for mutant in mutants for selector in mutant["selectors"]
    ]
    unexpected_mutant_selectors = sum(
        item["status"] == "complete" and item["concordant"] is not True
        for item in mutant_selectors
    )
    indeterminate_mutant_selectors = sum(
        item["status"] != "complete" for item in mutant_selectors
    )
    unexpected_mutants = [
        str(item["mutant_id"])
        for item in mutants
        if item["selector_table_complete"] is True and item["concordant"] is not True
    ]
    indeterminate_mutants = sum(
        item["selector_table_complete"] is not True for item in mutants
    )
    observed_comparison_fields = [
        field
        for field in _COMPARISON_FIELDS
        if not field.startswith("expected_") and field != "concordant"
    ]
    comparison_indeterminate = any(
        comparison[field] is None for field in observed_comparison_fields
    )
    if (
        indeterminate_candidates
        or indeterminate_profiles
        or indeterminate_mutant_selectors
        or indeterminate_mutants
        or comparison_indeterminate
    ):
        status = "indeterminate"
    elif (
        unexpected_candidates
        or unexpected_profiles
        or unexpected_mutant_selectors
        or unexpected_mutants
        or comparison["concordant"] is not True
    ):
        status = "unexpected"
    else:
        status = "expected"
    return {
        "status": status,
        "unexpected_candidate_selector_count": len(unexpected_candidates),
        "indeterminate_candidate_selector_count": indeterminate_candidates,
        "unexpected_profile_count": len(unexpected_profiles),
        "indeterminate_profile_count": indeterminate_profiles,
        "unexpected_mutant_selector_count": unexpected_mutant_selectors,
        "indeterminate_mutant_selector_count": indeterminate_mutant_selectors,
        "unexpected_mutant_count": len(unexpected_mutants),
        "indeterminate_mutant_count": indeterminate_mutants,
        "unexpected_candidate_selector_ids": unexpected_candidates,
        "unexpected_profile_ids": unexpected_profiles,
        "unexpected_mutant_ids": unexpected_mutants,
        "comparison_concordant": comparison["concordant"] is True,
    }


def _summary(
    candidates: Sequence[Mapping[str, object]],
    mutants: Sequence[Mapping[str, object]],
    catalog: Mapping[str, object],
) -> dict[str, object]:
    mutant_selectors = [
        selector for mutant in mutants for selector in mutant["selectors"]
    ]
    summary = catalog["summary"]
    assert isinstance(summary, dict)
    return {
        "candidate_selector_count": len(candidates),
        "candidate_selector_complete_count": sum(
            item["coverage_status"] == "complete" for item in candidates
        ),
        "mutant_count": len(mutants),
        "mutant_selector_count": len(mutant_selectors),
        "mutant_selector_complete_count": sum(
            item["status"] == "complete" for item in mutant_selectors
        ),
        "selector_command_count": len(candidates) + len(mutant_selectors),
        "generated_mutant_count": summary["generated"],
        "duplicate_record_count": summary["duplicate"],
        "invalid_record_count": summary["invalid"],
        "not_applicable_record_count": summary["not_applicable"],
        "mutation_score": None,
    }


def _root_cost(
    candidates: Sequence[Mapping[str, object]],
    mutants: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    mutant_selectors = [
        selector for mutant in mutants for selector in mutant["selectors"]
    ]
    candidate_costs = [item["cost"] for item in candidates]
    process = sum(
        float(item["process_wall_seconds"]) for item in candidate_costs
    ) + sum(
        float(item["cost"]["process_wall_seconds"])
        for item in mutant_selectors
    )
    wall_values = [item["coverage_wall_seconds"] for item in candidate_costs]
    cpu_values = [item["coverage_cpu_seconds"] for item in candidate_costs]
    coverage_complete = all(value is not None for value in wall_values + cpu_values)
    return {
        "status": "measured" if coverage_complete else "partial",
        "implementation_count": 1 + len(mutants),
        "candidate_selector_count": len(candidates),
        "mutant_count": len(mutants),
        "mutant_selector_count": len(mutant_selectors),
        "selector_command_count": len(candidates) + len(mutant_selectors),
        "process_wall_seconds": _round_cost(process),
        "coverage_wall_seconds": (
            _round_cost(sum(float(value) for value in wall_values))
            if coverage_complete
            else None
        ),
        "coverage_cpu_seconds": (
            _round_cost(sum(float(value) for value in cpu_values))
            if coverage_complete
            else None
        ),
        "missing_reason": (
            None if coverage_complete else "candidate_coverage_cost_unavailable"
        ),
    }


def _semantic_view(document: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(document)
    normalized["created_at"] = None
    normalized["runtime"] = None
    normalized["semantic_sha256"] = None
    normalized["report_sha256"] = None
    root_cost = normalized.get("cost")
    if isinstance(root_cost, dict):
        for field in (
            "process_wall_seconds",
            "coverage_wall_seconds",
            "coverage_cpu_seconds",
        ):
            root_cost[field] = None
    candidates = normalized.get("candidate_selectors")
    if isinstance(candidates, list):
        for selector in candidates:
            if not isinstance(selector, dict):
                continue
            selector["duration_seconds"] = None
            selector["stdout_sha256"] = None
            selector["stderr_sha256"] = None
            cost = selector.get("cost")
            if isinstance(cost, dict):
                for field in (
                    "process_wall_seconds",
                    "coverage_wall_seconds",
                    "coverage_cpu_seconds",
                ):
                    cost[field] = None
            receipt = selector.get("coverage_receipt")
            if isinstance(receipt, dict):
                receipt_cost = receipt.get("cost")
                if isinstance(receipt_cost, dict):
                    receipt_cost["wall_clock_seconds"] = None
                    receipt_cost["cpu_seconds"] = None
                receipt["coverage_sha256"] = None
    profiles = normalized.get("profiles")
    if isinstance(profiles, list):
        for profile in profiles:
            if not isinstance(profile, dict):
                continue
            cost = profile.get("cost")
            if isinstance(cost, dict):
                for field in (
                    "process_wall_seconds",
                    "coverage_wall_seconds",
                    "coverage_cpu_seconds",
                ):
                    cost[field] = None
    mutants = normalized.get("mutants")
    if isinstance(mutants, list):
        for mutant in mutants:
            if not isinstance(mutant, dict):
                continue
            cost = mutant.get("cost")
            if isinstance(cost, dict):
                cost["process_wall_seconds"] = None
            selectors = mutant.get("selectors")
            if isinstance(selectors, list):
                for selector in selectors:
                    if not isinstance(selector, dict):
                        continue
                    selector["duration_seconds"] = None
                    selector["stdout_sha256"] = None
                    selector["stderr_sha256"] = None
                    selector_cost = selector.get("cost")
                    if isinstance(selector_cost, dict):
                        selector_cost["process_wall_seconds"] = None
    return normalized


def compute_interaction_lattice_result_semantic_sha256(
    document: dict[str, Any],
) -> str:
    if not isinstance(document, dict):
        raise _error("interaction-lattice result", "must be an object")
    return sha256_document(_semantic_view(document))


def compute_interaction_lattice_result_report_sha256(
    document: dict[str, Any],
) -> str:
    if not isinstance(document, dict):
        raise _error("interaction-lattice result", "must be an object")
    normalized = deepcopy(document)
    normalized["report_sha256"] = None
    return sha256_document(normalized)


def run_interaction_witness_lattice_result(
    execution_protocol: object,
    plan: object,
    catalog: object,
    prior_art: object,
    coveragepy_manifest: object,
    pr46_result: object,
) -> dict[str, Any]:
    (
        normalized_protocol,
        normalized_plan,
        normalized_catalog,
        normalized_prior_art,
        normalized_manifest,
        normalized_pr46,
    ) = _preflight(
        execution_protocol,
        plan,
        catalog,
        prior_art,
        coveragepy_manifest,
        pr46_result,
    )
    candidate_raw = [
        _execute_candidate_selector(plan=normalized_plan, quadrant=quadrant)
        for quadrant in normalized_plan["truth_table"]
    ]
    candidates = [
        _canonical_candidate(
            raw,
            plan=normalized_plan,
            quadrant=quadrant,
        )
        for raw, quadrant in zip(
            candidate_raw,
            normalized_plan["truth_table"],
            strict=True,
        )
    ]
    candidate_by_quadrant = {
        str(item["quadrant_id"]): item for item in candidates
    }
    profiles = [
        _build_profile(
            definition,
            candidate_by_quadrant=candidate_by_quadrant,
        )
        for definition in normalized_plan["profiles"]
    ]

    generic_records = [
        record
        for record in normalized_catalog["mutants"]
        if record["catalog_role"] == "generic_operator"
    ]
    mutants: list[dict[str, Any]] = []
    for catalog_record in generic_records:
        status, source, ast_sha256, compile_valid, _ = _mutated_source(
            str(catalog_record["operator_id"])
        )
        if status != "generated" or source is None or compile_valid is not True:
            raise _error(
                "interaction mutant execution",
                f"{catalog_record['operator_id']} is not generated",
            )
        if _sha256_bytes(source.encode("utf-8")) != catalog_record[
            "mutated_source_sha256"
        ]:
            raise _error("interaction mutant execution", "source digest mismatch")
        if ast_sha256 != catalog_record["mutated_ast_sha256"]:
            raise _error("interaction mutant execution", "AST digest mismatch")
        raw_selectors = [
            _execute_mutant_selector(
                plan=normalized_plan,
                mutant=catalog_record,
                source=source,
                quadrant=quadrant,
            )
            for quadrant in normalized_plan["truth_table"]
        ]
        selectors = [
            _canonical_mutant_selector(
                raw,
                plan=normalized_plan,
                mutant=catalog_record,
                quadrant=quadrant,
            )
            for raw, quadrant in zip(
                raw_selectors,
                normalized_plan["truth_table"],
                strict=True,
            )
        ]
        mutants.append(
            _build_mutant(
                catalog_record,
                selectors,
                plan=normalized_plan,
            )
        )

    comparison = _comparison(profiles, mutants)
    analysis = _analysis(candidates, profiles, mutants, comparison)
    result: dict[str, Any] = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "study_id": "DW-001",
        "result_id": RESULT_ID,
        "partition": "development",
        "preregistration_merge_commit": PREREGISTRATION_MERGE_COMMIT,
        "execution_protocol_sha256": EXECUTION_PROTOCOL_SHA256,
        "plan_sha256": PLAN_SHA256,
        "catalog_sha256": CATALOG_SHA256,
        "prior_art_log_sha256": PRIOR_ART_LOG_SHA256,
        "coveragepy_distribution_manifest_sha256": (
            COVERAGEPY_MANIFEST_SHA256
        ),
        "pr46_result_semantic_sha256": PR46_RESULT_SEMANTIC_SHA256,
        "pr46_result_report_sha256": PR46_RESULT_REPORT_SHA256,
        "created_at": datetime.now(timezone.utc).isoformat().replace(
            "+00:00", "Z"
        ),
        "runtime": {
            "tool_version": __version__,
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
            "platform_system": platform.system(),
        },
        "distribution": build_coveragepy_distribution_manifest(),
        "configuration": _configuration(),
        "source": _source_view(normalized_plan),
        "candidate_selectors": candidates,
        "profiles": profiles,
        "mutants": mutants,
        "summary": _summary(candidates, mutants, normalized_catalog),
        "comparison": comparison,
        "analysis": analysis,
        "policy": _policy(),
        "cost": _root_cost(candidates, mutants),
        "semantic_sha256": None,
        "report_sha256": None,
    }
    result["semantic_sha256"] = (
        compute_interaction_lattice_result_semantic_sha256(result)
    )
    result["report_sha256"] = (
        compute_interaction_lattice_result_report_sha256(result)
    )
    valid, errors = verify_interaction_witness_lattice_result_document(
        result,
        normalized_protocol,
        normalized_plan,
        normalized_catalog,
        normalized_prior_art,
        normalized_manifest,
        normalized_pr46,
    )
    if not valid:
        raise _error("interaction result self-verification", "; ".join(errors))
    return result


def _raw_candidate_from_record(record: Mapping[str, object]) -> dict[str, object]:
    return {
        field: deepcopy(record[field])
        for field in (
            "order",
            "implementation_id",
            "quadrant_id",
            "selector_id",
            "selector",
            "input",
            "expected_decision",
            "source_sha256",
            "test_sha256",
            "target_id",
            "command",
            "context_id",
            "invocation_binding",
            "observed",
            "return_code",
            "timed_out",
            "duration_seconds",
            "stdout_sha256",
            "stderr_sha256",
            "receipt_sha256",
            "receipt_outcome",
            "receipt_producer",
            "receipt_counts",
            "observation_error",
            "coverage_receipt",
            "coverage_error",
        )
    }


def _raw_mutant_selector_from_record(
    record: Mapping[str, object],
) -> dict[str, object]:
    return {
        field: deepcopy(record[field])
        for field in (
            "order",
            "implementation_id",
            "operator_id",
            "mutant_id",
            "quadrant_id",
            "selector_id",
            "selector",
            "source_sha256",
            "test_sha256",
            "command",
            "invocation_binding",
            "observed",
            "return_code",
            "timed_out",
            "duration_seconds",
            "stdout_sha256",
            "stderr_sha256",
            "receipt_sha256",
            "receipt_outcome",
            "receipt_producer",
            "receipt_counts",
            "observation_error",
        )
    }


def _canonical_result(
    document: object,
    *,
    execution_protocol: Mapping[str, object],
    plan: Mapping[str, object],
    catalog: Mapping[str, object],
) -> dict[str, Any]:
    result = _exact_keys(document, _ROOT_FIELDS, context="interaction result")
    runtime = _exact_keys(
        result["runtime"], _RUNTIME_FIELDS, context="interaction result.runtime"
    )
    if any(not isinstance(value, str) or not value for value in runtime.values()):
        raise _error("interaction result.runtime", "values must be strings")
    if not isinstance(result["created_at"], str) or not result["created_at"]:
        raise _error("interaction result.created_at", "must be a string")
    static = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "study_id": "DW-001",
        "result_id": RESULT_ID,
        "partition": "development",
        "preregistration_merge_commit": PREREGISTRATION_MERGE_COMMIT,
        "execution_protocol_sha256": EXECUTION_PROTOCOL_SHA256,
        "plan_sha256": PLAN_SHA256,
        "catalog_sha256": CATALOG_SHA256,
        "prior_art_log_sha256": PRIOR_ART_LOG_SHA256,
        "coveragepy_distribution_manifest_sha256": COVERAGEPY_MANIFEST_SHA256,
        "pr46_result_semantic_sha256": PR46_RESULT_SEMANTIC_SHA256,
        "pr46_result_report_sha256": PR46_RESULT_REPORT_SHA256,
    }
    for field, expected in static.items():
        if result[field] != expected:
            raise _error(f"interaction result.{field}", "identity mismatch")
    if result["distribution"] != build_coveragepy_distribution_manifest():
        raise _error("interaction result.distribution", "identity mismatch")
    if result["configuration"] != _configuration():
        raise _error("interaction result.configuration", "identity mismatch")
    source = _exact_keys(
        result["source"], _SOURCE_FIELDS, context="interaction result.source"
    )
    expected_source = _source_view(plan)
    if not _strict_equal(expected_source, source):
        raise _error("interaction result.source", "frozen relation mismatch")

    candidate_records = result["candidate_selectors"]
    if not isinstance(candidate_records, list) or len(candidate_records) != 4:
        raise _error("interaction result.candidate_selectors", "must have four")
    candidates: list[dict[str, Any]] = []
    for record, quadrant in zip(
        candidate_records, plan["truth_table"], strict=True
    ):
        actual = _exact_keys(
            record,
            _CANDIDATE_FIELDS,
            context=f"interaction candidate {quadrant['quadrant_id']}",
        )
        canonical = _canonical_candidate(
            _raw_candidate_from_record(actual),
            plan=plan,
            quadrant=quadrant,
        )
        if not _strict_equal(canonical, actual):
            raise _error(
                f"interaction candidate {quadrant['quadrant_id']}",
                "derived evidence mismatch",
            )
        candidates.append(canonical)
    candidate_by_quadrant = {
        str(item["quadrant_id"]): item for item in candidates
    }
    expected_profiles = [
        _build_profile(
            definition,
            candidate_by_quadrant=candidate_by_quadrant,
        )
        for definition in plan["profiles"]
    ]
    profile_records = result["profiles"]
    if not isinstance(profile_records, list) or len(profile_records) != 5:
        raise _error("interaction result.profiles", "must have five")
    for index, (expected, actual_raw) in enumerate(
        zip(expected_profiles, profile_records, strict=True)
    ):
        actual = _exact_keys(
            actual_raw,
            _PROFILE_FIELDS,
            context=f"interaction profile[{index}]",
        )
        cost = _exact_keys(
            actual["cost"],
            _PROFILE_COST_FIELDS,
            context=f"interaction profile[{index}].cost",
        )
        for field in (
            "process_wall_seconds",
            "coverage_wall_seconds",
            "coverage_cpu_seconds",
        ):
            if cost[field] is not None:
                _finite_nonnegative(
                    cost[field],
                    context=f"interaction profile[{index}].cost.{field}",
                )
        if not _strict_equal(expected, actual):
            raise _error(
                f"interaction profile[{index}]",
                "selector-derived evidence mismatch",
            )

    generic_records = [
        record
        for record in catalog["mutants"]
        if record["catalog_role"] == "generic_operator"
    ]
    mutant_records = result["mutants"]
    if not isinstance(mutant_records, list) or len(mutant_records) != 5:
        raise _error("interaction result.mutants", "must have five")
    mutants: list[dict[str, Any]] = []
    for actual_raw, catalog_record in zip(
        mutant_records, generic_records, strict=True
    ):
        actual = _exact_keys(
            actual_raw,
            _MUTANT_FIELDS,
            context=f"interaction mutant {catalog_record['operator_id']}",
        )
        selector_records = actual["selectors"]
        if not isinstance(selector_records, list) or len(selector_records) != 4:
            raise _error("interaction mutant selectors", "must have four")
        selectors: list[dict[str, Any]] = []
        for record, quadrant in zip(
            selector_records, plan["truth_table"], strict=True
        ):
            selector_actual = _exact_keys(
                record,
                _MUTANT_SELECTOR_FIELDS,
                context=(
                    f"interaction mutant {catalog_record['operator_id']}/"
                    f"{quadrant['quadrant_id']}"
                ),
            )
            canonical_selector = _canonical_mutant_selector(
                _raw_mutant_selector_from_record(selector_actual),
                plan=plan,
                mutant=catalog_record,
                quadrant=quadrant,
            )
            if not _strict_equal(canonical_selector, selector_actual):
                raise _error(
                    "interaction mutant selector",
                    "derived evidence mismatch",
                )
            selectors.append(canonical_selector)
        canonical_mutant = _build_mutant(
            catalog_record,
            selectors,
            plan=plan,
        )
        if not _strict_equal(canonical_mutant, actual):
            raise _error(
                f"interaction mutant {catalog_record['operator_id']}",
                "derived evidence mismatch",
            )
        mutants.append(canonical_mutant)

    expected_summary = _summary(candidates, mutants, catalog)
    summary = _exact_keys(
        result["summary"], _SUMMARY_FIELDS, context="interaction result.summary"
    )
    if not _strict_equal(expected_summary, summary):
        raise _error("interaction result.summary", "derived evidence mismatch")
    expected_comparison = _comparison(expected_profiles, mutants)
    comparison = _exact_keys(
        result["comparison"],
        _COMPARISON_FIELDS,
        context="interaction result.comparison",
    )
    if not _strict_equal(expected_comparison, comparison):
        raise _error("interaction result.comparison", "derived evidence mismatch")
    expected_analysis = _analysis(
        candidates, expected_profiles, mutants, expected_comparison
    )
    analysis = _exact_keys(
        result["analysis"], _ANALYSIS_FIELDS, context="interaction result.analysis"
    )
    if not _strict_equal(expected_analysis, analysis):
        raise _error("interaction result.analysis", "derived evidence mismatch")
    policy = _exact_keys(
        result["policy"], _POLICY_FIELDS, context="interaction result.policy"
    )
    if not _strict_equal(_policy(), policy):
        raise _error("interaction result.policy", "policy boundary mismatch")
    expected_cost = _root_cost(candidates, mutants)
    cost = _exact_keys(
        result["cost"], _ROOT_COST_FIELDS, context="interaction result.cost"
    )
    for field in (
        "process_wall_seconds",
        "coverage_wall_seconds",
        "coverage_cpu_seconds",
    ):
        if cost[field] is not None:
            _finite_nonnegative(
                cost[field], context=f"interaction result.cost.{field}"
            )
    if not _strict_equal(expected_cost, cost):
        raise _error("interaction result.cost", "derived evidence mismatch")
    return {
        **static,
        "created_at": result["created_at"],
        "runtime": deepcopy(runtime),
        "distribution": build_coveragepy_distribution_manifest(),
        "configuration": _configuration(),
        "source": expected_source,
        "candidate_selectors": candidates,
        "profiles": expected_profiles,
        "mutants": mutants,
        "summary": expected_summary,
        "comparison": expected_comparison,
        "analysis": expected_analysis,
        "policy": _policy(),
        "cost": expected_cost,
        "semantic_sha256": result["semantic_sha256"],
        "report_sha256": result["report_sha256"],
    }


def verify_interaction_witness_lattice_result_document(
    document: object,
    execution_protocol: object,
    plan: object,
    catalog: object,
    prior_art: object,
    coveragepy_manifest: object,
    pr46_result: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        (
            normalized_protocol,
            normalized_plan,
            normalized_catalog,
            _,
            _,
            _,
        ) = _preflight(
            execution_protocol,
            plan,
            catalog,
            prior_art,
            coveragepy_manifest,
            pr46_result,
        )
        canonical = _canonical_result(
            document,
            execution_protocol=normalized_protocol,
            plan=normalized_plan,
            catalog=normalized_catalog,
        )
        assert isinstance(document, dict)
        errors = _differences(
            canonical,
            document,
            context="interaction result",
        )
        if document.get("semantic_sha256") != (
            compute_interaction_lattice_result_semantic_sha256(document)
        ):
            errors.append("interaction result.semantic_sha256: digest mismatch")
        if document.get("report_sha256") != (
            compute_interaction_lattice_result_report_sha256(document)
        ):
            errors.append("interaction result.report_sha256: digest mismatch")
    except (
        DW001InteractionLatticeResultError,
        CoveragePyProbeError,
        DeltaWitnessError,
        ReportError,
        KeyError,
        TypeError,
        IndexError,
        ValueError,
        OverflowError,
        MemoryError,
        RecursionError,
        AssertionError,
    ) as exc:
        return False, (str(exc),)
    unique = tuple(dict.fromkeys(errors))
    return not unique, unique


def load_interaction_witness_lattice_result(
    path: Path,
    execution_protocol: object,
    plan: object,
    catalog: object,
    prior_art: object,
    coveragepy_manifest: object,
    pr46_result: object,
) -> dict[str, Any]:
    try:
        metadata = path.lstat()
    except OSError as exc:
        raise _error("interaction result path", "cannot be inspected") from exc
    if path.is_symlink() or not stat.S_ISREG(metadata.st_mode):
        raise _error("interaction result path", "must be a regular non-link file")
    if metadata.st_size <= 0 or metadata.st_size > _MAX_RESULT_BYTES:
        raise _error("interaction result path", "is outside the size limit")
    document = load_report(path)
    valid, errors = verify_interaction_witness_lattice_result_document(
        document,
        execution_protocol,
        plan,
        catalog,
        prior_art,
        coveragepy_manifest,
        pr46_result,
    )
    if not valid:
        raise _error("interaction result", "; ".join(errors))
    return document


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
