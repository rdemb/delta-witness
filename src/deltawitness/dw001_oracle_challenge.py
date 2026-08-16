"""Integrity-bound DW-001 weak-proxy-oracle challenge.

The challenge binds one verified owned-synthetic four-state witness and one
verified declared-selector localization to five fixed mutation-control
executions. The declared selector is a genuine fail-to-pass assertion, yet a
fixed claim-violating mutant survives it and is rejected only by a separately
fixed hidden development claim check.

This artifact establishes one controlled limitation of current evidence. It is
not a general oracle-relevance, oracle-strength, mutation-score, agent-quality,
or production-safety result.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
from pathlib import Path
import tempfile
from typing import Any, Mapping

from . import __version__
from . import _dw001_weak_proxy as _fixture
from .claim_witness import (
    canonical_unittest_selector_command,
    verify_claim_witness_declaration_document,
    verify_claim_witness_localization_document,
)
from .dw001 import verify_projection_document
from .dw001_scenarios import (
    verify_fixture_descriptor_document,
    verify_fixture_identity_document,
)
from .errors import DeltaWitnessError
from .execution import run_command
from .receipt import build_receipt_document, validate_receipt_document
from .reporting import sha256_document, verify_report_document


CHALLENGE_SCHEMA_VERSION = "deltawitness.dw001-weak-oracle-challenge.v1"
CHALLENGE_ID = "weak-proxy-oracle-v1"
FAMILY_ID = _fixture.FAMILY_ID
MUTANT_ID = "nonempty-role-boolean-v1"
DECLARED_SELECTOR = "test_access.AccessTests.test_viewer_result_is_boolean"
HIDDEN_CLAIM_SELECTOR = "test_hidden_claim.HiddenClaimTests.test_viewer_is_denied"

_TASK_ID = "agent-surrogate-role-check-v1"
_TASK_PROMPT = (
    "Fix is_admin so only the admin role is authorized and add a regression "
    "test proving that a viewer is denied."
)
_INTENDED_BEHAVIOR = "A viewer is not authorized as an administrator."
_OPERATOR_ID = "replace-candidate-predicate-with-nonempty-role-boolean-v1"
_PRODUCER_NAME = "deltawitness-unittest"
_CONTROL_SCHEMA_VERSION = "deltawitness.dw001-weak-oracle-control.v1"
_PROJECTION_VIEW_VERSION = "deltawitness.dw001-projection-decision-view.v1"
_LOCALIZATION_VIEW_VERSION = "deltawitness.dw001-localization-evidence-view.v1"

_ROOT_FIELDS = {
    "schema_version",
    "study_id",
    "challenge_id",
    "scenario_id",
    "family_id",
    "partition",
    "task",
    "source",
    "claim",
    "mutation",
    "current_evidence",
    "controlled_executions",
    "finding",
    "limitations",
    "challenge_sha256",
    "report_sha256",
}

_LIMITATIONS = [
    "The task is a fixed owned-synthetic agent-workflow surrogate, not an ecological agent sample.",
    "The hidden claim check is development-only mechanism evidence, not a general oracle.",
    "Survival of one fixed mutant does not define mutation adequacy or oracle strength.",
    "The challenge does not authorize execution of external repositories or untrusted code.",
    "All digests are unkeyed integrity fields and do not authenticate a producer.",
]

_CONTROL_DEFINITIONS: tuple[tuple[str, str, str, str], ...] = (
    ("base", "declared_selector", DECLARED_SELECTOR, "fail"),
    ("candidate", "declared_selector", DECLARED_SELECTOR, "pass"),
    ("mutant", "declared_selector", DECLARED_SELECTOR, "pass"),
    ("candidate", "hidden_claim", HIDDEN_CLAIM_SELECTOR, "pass"),
    ("mutant", "hidden_claim", HIDDEN_CLAIM_SELECTOR, "fail"),
)


class DW001OracleChallengeError(DeltaWitnessError):
    """Raised when weak-oracle challenge evidence is unsafe or inconsistent."""


def _error(context: str, message: str) -> DW001OracleChallengeError:
    return DW001OracleChallengeError(f"{context}: {message}")


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


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _code_bytes(implementation: str) -> bytes:
    if implementation == "base":
        return _fixture.BASE_CODE.encode("utf-8")
    if implementation == "candidate":
        return _fixture.CANDIDATE_CODE.encode("utf-8")
    if implementation == "mutant":
        return _fixture.MUTANT_CODE.encode("utf-8")
    raise _error("weak oracle control implementation", "is unsupported")


def _test_bytes(test_role: str) -> tuple[str, bytes]:
    if test_role == "declared_selector":
        return "test_access.py", _fixture.CANDIDATE_TESTS.encode("utf-8")
    if test_role == "hidden_claim":
        return "test_hidden_claim.py", _fixture.HIDDEN_CLAIM_TESTS.encode(
            "utf-8"
        )
    raise _error("weak oracle control test_role", "is unsupported")


def _counts(outcome: str) -> dict[str, int]:
    if outcome == "passed":
        return {
            "tests_run": 1,
            "passed": 1,
            "failures": 0,
            "errors": 0,
            "skipped": 0,
            "expected_failures": 0,
            "unexpected_successes": 0,
        }
    if outcome == "test_failure":
        return {
            "tests_run": 1,
            "passed": 0,
            "failures": 1,
            "errors": 0,
            "skipped": 0,
            "expected_failures": 0,
            "unexpected_successes": 0,
        }
    raise _error("weak oracle control receipt outcome", "is unsupported")


def _control_binding(
    *,
    implementation: str,
    test_role: str,
    selector: str,
    source_sha256: str,
    test_sha256: str,
) -> str:
    return sha256_document(
        {
            "schema_version": _CONTROL_SCHEMA_VERSION,
            "challenge_id": CHALLENGE_ID,
            "implementation": implementation,
            "test_role": test_role,
            "selector": selector,
            "command": canonical_unittest_selector_command(selector),
            "source_sha256": source_sha256,
            "test_sha256": test_sha256,
            "observer": "outcome-receipt-v1",
            "producer": {
                "name": _PRODUCER_NAME,
                "version": __version__,
            },
        }
    )


def _expected_control(
    implementation: str,
    test_role: str,
    selector: str,
    observed: str,
) -> dict[str, Any]:
    source_sha256 = _sha256_bytes(_code_bytes(implementation))
    _, tests = _test_bytes(test_role)
    test_sha256 = _sha256_bytes(tests)
    binding = _control_binding(
        implementation=implementation,
        test_role=test_role,
        selector=selector,
        source_sha256=source_sha256,
        test_sha256=test_sha256,
    )
    receipt_outcome = "passed" if observed == "pass" else "test_failure"
    counts = _counts(receipt_outcome)
    receipt_document = build_receipt_document(
        binding=binding,
        producer_name=_PRODUCER_NAME,
        producer_version=__version__,
        outcome=receipt_outcome,
        counts=counts,
    )
    receipt = validate_receipt_document(
        receipt_document,
        expected_binding=binding,
    )
    return {
        "implementation": implementation,
        "test_role": test_role,
        "selector": selector,
        "source_sha256": source_sha256,
        "test_sha256": test_sha256,
        "command": canonical_unittest_selector_command(selector),
        "observed": observed,
        "return_code": 0 if observed == "pass" else 1,
        "timed_out": False,
        "invocation_binding": binding,
        "receipt_sha256": receipt.sha256,
        "receipt_outcome": receipt_outcome,
        "receipt_producer": {
            "name": _PRODUCER_NAME,
            "version": __version__,
        },
        "receipt_counts": counts,
        "observation_error": None,
    }


def _run_control(
    implementation: str,
    test_role: str,
    selector: str,
) -> dict[str, Any]:
    code = _code_bytes(implementation)
    test_name, tests = _test_bytes(test_role)
    expected = next(
        item
        for item in _CONTROL_DEFINITIONS
        if item[:3] == (implementation, test_role, selector)
    )[3]
    expected_document = _expected_control(
        implementation,
        test_role,
        selector,
        expected,
    )

    with tempfile.TemporaryDirectory(
        prefix="deltawitness-weak-oracle-control-"
    ) as directory:
        root = Path(directory)
        (root / "src").mkdir()
        (root / "tests").mkdir()
        (root / "src" / "access.py").write_bytes(code)
        (root / "tests" / test_name).write_bytes(tests)
        observation = run_command(
            expected_document["command"],
            state=f"weak-oracle:{implementation}:{test_role}",
            cwd=root,
            timeout_seconds=30,
            pass_env=(),
            include_output=False,
            observer="outcome-receipt-v1",
            receipt_binding=expected_document["invocation_binding"],
        )

    if observation.timed_out:
        observed = "timeout"
        observation_error = None
    elif observation.receipt_error is not None:
        observed = "error"
        observation_error = observation.receipt_error
    elif observation.receipt_outcome == "passed" and observation.return_code == 0:
        observed = "pass"
        observation_error = None
    elif (
        observation.receipt_outcome == "test_failure"
        and observation.return_code == 1
    ):
        observed = "fail"
        observation_error = None
    else:
        observed = "error"
        observation_error = "receipt_exit_mismatch"

    actual = {
        "implementation": implementation,
        "test_role": test_role,
        "selector": selector,
        "source_sha256": _sha256_bytes(code),
        "test_sha256": _sha256_bytes(tests),
        "command": expected_document["command"],
        "observed": observed,
        "return_code": observation.return_code,
        "timed_out": observation.timed_out,
        "invocation_binding": expected_document["invocation_binding"],
        "receipt_sha256": observation.receipt_sha256,
        "receipt_outcome": observation.receipt_outcome,
        "receipt_producer": observation.receipt_producer,
        "receipt_counts": observation.receipt_counts,
        "observation_error": observation_error,
    }
    if actual != expected_document:
        raise _error(
            f"weak oracle control {implementation}/{test_role}",
            f"unexpected fixed-control result: expected={expected_document!r}, "
            f"observed={actual!r}",
        )
    return actual


def _projection_view(projection: Mapping[str, object]) -> dict[str, object]:
    source = _object(
        projection["source"],
        context="weak oracle projection.source",
    )
    methods = projection["methods"]
    if not isinstance(methods, list):
        raise _error("weak oracle projection.methods", "must be a list")
    return {
        "schema_version": _PROJECTION_VIEW_VERSION,
        "scenario_id": projection["scenario_id"],
        "source": {
            "witness_sha256": source["witness_sha256"],
            "base_sha": source["base_sha"],
            "head_sha": source["head_sha"],
            "spec_sha256": source["spec_sha256"],
            "observer_id": source["observer_id"],
        },
        "methods": [
            {
                "method_id": method["method_id"],
                "decision": method["decision"],
                "reason_code": method["reason_code"],
            }
            for method in methods
        ],
    }


def _localization_view(localization: Mapping[str, object]) -> dict[str, object]:
    source = _object(
        localization["source"],
        context="weak oracle localization.source",
    )
    selectors = localization["selectors"]
    if not isinstance(selectors, list):
        raise _error("weak oracle localization.selectors", "must be a list")
    normalized_selectors: list[dict[str, object]] = []
    for selector in selectors:
        states = selector["states"]
        if not isinstance(states, list):
            raise _error(
                "weak oracle localization selector states",
                "must be a list",
            )
        normalized_selectors.append(
            {
                "selector": selector["selector"],
                "classification": selector["classification"],
                "diagnostic_code": selector["diagnostic_code"],
                "states": [
                    {
                        "state": state["state"],
                        "commit_sha": state["commit_sha"],
                        "tree_sha": state["tree_sha"],
                        "observed": state["observed"],
                        "return_code": state["return_code"],
                        "timed_out": state["timed_out"],
                        "invocation_binding": state["invocation_binding"],
                        "receipt_sha256": state["receipt_sha256"],
                        "receipt_outcome": state["receipt_outcome"],
                        "receipt_producer": state["receipt_producer"],
                        "receipt_counts": state["receipt_counts"],
                        "observation_error": state["observation_error"],
                    }
                    for state in states
                ],
            }
        )
    return {
        "schema_version": _LOCALIZATION_VIEW_VERSION,
        "source": {
            "declaration_sha256": source["declaration_sha256"],
            "source_witness_sha256": source["source_witness_sha256"],
            "spec_sha256": source["spec_sha256"],
            "claim_id": source["claim_id"],
            "base_sha": source["base_sha"],
            "head_sha": source["head_sha"],
        },
        "adapter": localization["adapter"],
        "aggregate_rule": localization["aggregate_rule"],
        "selectors": normalized_selectors,
        "aggregate_status": localization["aggregate_status"],
    }


def _preflight_sources(
    descriptor: object,
    identity: object,
    source_report: object,
    projection: object,
    declaration: object,
    localization: object,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    checks = (
        ("descriptor", verify_fixture_descriptor_document(descriptor)),
        ("identity", verify_fixture_identity_document(identity, descriptor)),
        ("matrix report", verify_report_document(source_report)),
        ("projection", verify_projection_document(projection)),
        (
            "declaration",
            verify_claim_witness_declaration_document(declaration),
        ),
        (
            "localization",
            verify_claim_witness_localization_document(
                localization,
                declaration,
                source_report,
            ),
        ),
    )
    errors = [
        f"{label}: {error}"
        for label, (valid, messages) in checks
        if not valid
        for error in messages
    ]
    if errors:
        raise _error("weak oracle source preflight", "; ".join(errors))
    if not all(
        isinstance(item, dict)
        for item in (
            descriptor,
            identity,
            source_report,
            projection,
            declaration,
            localization,
        )
    ):
        raise _error("weak oracle source preflight", "all sources must be objects")

    if descriptor["family_id"] != FAMILY_ID:
        raise _error("weak oracle descriptor.family_id", "is unsupported")
    if descriptor["control_role"] != "false-assurance-case":
        raise _error("weak oracle descriptor.control_role", "is inconsistent")
    if identity["descriptor_sha256"] != descriptor["descriptor_sha256"]:
        raise _error("weak oracle identity.descriptor_sha256", "does not match")
    if identity["scenario_id"] != descriptor["scenario_id"]:
        raise _error("weak oracle identity.scenario_id", "does not match")

    git_identity = _object(identity["git"], context="weak oracle identity.git")
    specification = _object(
        identity["specification"],
        context="weak oracle identity.specification",
    )
    if source_report["base_sha"] != git_identity["base_commit_sha"]:
        raise _error(
            "weak oracle source report.base_sha",
            "does not match identity",
        )
    if source_report["head_sha"] != git_identity["head_commit_sha"]:
        raise _error(
            "weak oracle source report.head_sha",
            "does not match identity",
        )
    if source_report["spec_sha256"] != specification["sha256"]:
        raise _error(
            "weak oracle source report.spec_sha256",
            "does not match identity",
        )
    if source_report["complete"] is not True or source_report["supported"] is not True:
        raise _error(
            "weak oracle source report",
            "must be a complete supported canonical witness",
        )

    projection_source = _object(
        projection["source"],
        context="weak oracle projection.source",
    )
    for field, report_field in (
        ("report_sha256", "report_sha256"),
        ("witness_sha256", "witness_sha256"),
        ("base_sha", "base_sha"),
        ("head_sha", "head_sha"),
        ("spec_sha256", "spec_sha256"),
    ):
        if projection_source[field] != source_report[report_field]:
            raise _error(
                f"weak oracle projection.source.{field}",
                "does not match matrix report",
            )
    if projection["scenario_id"] != descriptor["scenario_id"]:
        raise _error(
            "weak oracle projection.scenario_id",
            "does not match descriptor",
        )
    methods = projection["methods"]
    if not isinstance(methods, list) or [
        method["decision"] for method in methods
    ] != ["accept", "accept", "accept", "accept"]:
        raise _error("weak oracle projection.methods", "all methods must accept")

    if declaration["spec_sha256"] != specification["sha256"]:
        raise _error(
            "weak oracle declaration.spec_sha256",
            "does not match identity",
        )
    if declaration["claim_id"] != "role-check-regression":
        raise _error("weak oracle declaration.claim_id", "is unsupported")
    if declaration["selectors"] != [DECLARED_SELECTOR]:
        raise _error(
            "weak oracle declaration.selectors",
            "must contain the fixed selector",
        )

    localization_source = _object(
        localization["source"],
        context="weak oracle localization.source",
    )
    if localization_source["source_witness_sha256"] != source_report[
        "witness_sha256"
    ]:
        raise _error(
            "weak oracle localization.source_witness_sha256",
            "does not match matrix report",
        )
    if localization["aggregate_status"] != "supported":
        raise _error(
            "weak oracle localization.aggregate_status",
            "must be supported",
        )
    selectors = localization["selectors"]
    if (
        not isinstance(selectors, list)
        or len(selectors) != 1
        or selectors[0]["selector"] != DECLARED_SELECTOR
        or selectors[0]["classification"] != "discriminating"
    ):
        raise _error(
            "weak oracle localization.selectors",
            "must contain one discriminating fixed selector",
        )
    return (
        descriptor,
        identity,
        source_report,
        projection,
        declaration,
        localization,
    )


def _expected_artifact(
    descriptor: Mapping[str, object],
    identity: Mapping[str, object],
    source_report: Mapping[str, object],
    projection: Mapping[str, object],
    declaration: Mapping[str, object],
    localization: Mapping[str, object],
) -> dict[str, Any]:
    projection_view = _projection_view(projection)
    localization_view = _localization_view(localization)
    controls = [
        _expected_control(*definition)
        for definition in _CONTROL_DEFINITIONS
    ]
    artifact: dict[str, Any] = {
        "schema_version": CHALLENGE_SCHEMA_VERSION,
        "study_id": "DW-001",
        "challenge_id": CHALLENGE_ID,
        "scenario_id": descriptor["scenario_id"],
        "family_id": FAMILY_ID,
        "partition": "development",
        "task": {
            "task_id": _TASK_ID,
            "prompt": _TASK_PROMPT,
            "prompt_sha256": _sha256_bytes(_TASK_PROMPT.encode("utf-8")),
            "generation_mode": "fixed_owned_synthetic_agent_workflow_surrogate",
            "model_identity": None,
        },
        "source": {
            "descriptor_sha256": descriptor["descriptor_sha256"],
            "identity_sha256": identity["identity_sha256"],
            "witness_sha256": source_report["witness_sha256"],
            "projection_decisions_sha256": sha256_document(projection_view),
            "declaration_sha256": declaration["declaration_sha256"],
            "localization_evidence_sha256": sha256_document(localization_view),
            "base_sha": source_report["base_sha"],
            "head_sha": source_report["head_sha"],
            "spec_sha256": source_report["spec_sha256"],
            "observer_id": projection["source"]["observer_id"],
        },
        "claim": {
            "claim_id": "role-check-regression",
            "intended_behavior": _INTENDED_BEHAVIOR,
            "declared_selector": DECLARED_SELECTOR,
            "hidden_claim_selector": HIDDEN_CLAIM_SELECTOR,
        },
        "mutation": {
            "mutant_id": MUTANT_ID,
            "operator_id": _OPERATOR_ID,
            "code_path": "src/access.py",
            "candidate_code_sha256": _sha256_bytes(
                _fixture.CANDIDATE_CODE.encode("utf-8")
            ),
            "mutant_code_sha256": _sha256_bytes(
                _fixture.MUTANT_CODE.encode("utf-8")
            ),
            "declared_test_sha256": _sha256_bytes(
                _fixture.CANDIDATE_TESTS.encode("utf-8")
            ),
            "hidden_test_sha256": _sha256_bytes(
                _fixture.HIDDEN_CLAIM_TESTS.encode("utf-8")
            ),
            "caller_supplied": False,
        },
        "current_evidence": {
            "matrix_complete": True,
            "matrix_supported": True,
            "method_decisions": [
                {
                    "method_id": method["method_id"],
                    "decision": method["decision"],
                }
                for method in projection["methods"]
            ],
            "localization_status": localization["aggregate_status"],
        },
        "controlled_executions": controls,
        "finding": {
            "declared_selector_discriminates_base_candidate": True,
            "mutant_survives_declared_selector": True,
            "mutant_violates_hidden_claim": True,
            "weak_oracle_exposed": True,
            "primary_denominator_eligible": False,
        },
        "limitations": list(_LIMITATIONS),
        "challenge_sha256": None,
        "report_sha256": None,
    }
    artifact["challenge_sha256"] = compute_weak_oracle_challenge_sha256(
        artifact
    )
    artifact["report_sha256"] = compute_weak_oracle_report_sha256(artifact)
    return artifact


def compute_weak_oracle_challenge_sha256(document: dict[str, Any]) -> str:
    """Hash canonical challenge bytes with both digest fields normalized."""

    if not isinstance(document, dict):
        raise _error("weak oracle challenge", "must be an object")
    normalized = deepcopy(document)
    normalized["challenge_sha256"] = None
    normalized["report_sha256"] = None
    return sha256_document(normalized)


def compute_weak_oracle_report_sha256(document: dict[str, Any]) -> str:
    """Hash the complete artifact with only the full-report digest normalized."""

    if not isinstance(document, dict):
        raise _error("weak oracle challenge", "must be an object")
    normalized = deepcopy(document)
    normalized["report_sha256"] = None
    return sha256_document(normalized)


def _differences(
    expected: object,
    observed: object,
    *,
    context: str,
) -> list[str]:
    errors: list[str] = []
    if isinstance(expected, dict):
        if not isinstance(observed, dict):
            return [f"{context}: must be an object"]
        expected_keys = set(expected)
        observed_keys = set(observed)
        if expected_keys != observed_keys:
            errors.append(
                f"{context}: field mismatch; "
                f"missing={sorted(expected_keys - observed_keys)}, "
                f"extra={sorted(observed_keys - expected_keys)}"
            )
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
        if not isinstance(observed, list):
            return [f"{context}: must be a list"]
        if len(expected) != len(observed):
            errors.append(
                f"{context}: length mismatch; expected {len(expected)}, "
                f"observed {len(observed)}"
            )
        for index, (expected_item, observed_item) in enumerate(
            zip(expected, observed, strict=False)
        ):
            errors.extend(
                _differences(
                    expected_item,
                    observed_item,
                    context=f"{context}[{index}]",
                )
            )
        return errors
    if observed != expected:
        errors.append(
            f"{context}: expected={expected!r}, observed={observed!r}"
        )
    return errors


def run_weak_proxy_oracle_challenge(
    descriptor: object,
    identity: object,
    source_report: object,
    projection: object,
    declaration: object,
    localization: object,
) -> dict[str, Any]:
    """Execute the five fixed controls after source preflight verification."""

    sources = _preflight_sources(
        descriptor,
        identity,
        source_report,
        projection,
        declaration,
        localization,
    )
    actual_controls = [
        _run_control(definition[0], definition[1], definition[2])
        for definition in _CONTROL_DEFINITIONS
    ]
    expected = _expected_artifact(*sources)
    if actual_controls != expected["controlled_executions"]:
        raise _error(
            "weak oracle controlled executions",
            "do not match the fixed challenge contract",
        )
    valid, errors = verify_weak_oracle_challenge_document(
        expected,
        *sources,
    )
    if not valid:
        raise _error(
            "weak oracle challenge self-verification",
            "; ".join(errors),
        )
    return expected


def verify_weak_oracle_challenge_document(
    document: object,
    descriptor: object,
    identity: object,
    source_report: object,
    projection: object,
    declaration: object,
    localization: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify source semantics, exact challenge content, and both digests."""

    try:
        sources = _preflight_sources(
            descriptor,
            identity,
            source_report,
            projection,
            declaration,
            localization,
        )
        challenge = _object(document, context="weak oracle challenge")
        _exact_keys(challenge, _ROOT_FIELDS, context="weak oracle challenge")
        expected = _expected_artifact(*sources)
        errors: list[str] = []
        recorded_challenge = challenge.get("challenge_sha256")
        computed_challenge = compute_weak_oracle_challenge_sha256(challenge)
        if recorded_challenge != computed_challenge:
            errors.append(
                "weak oracle challenge.challenge_sha256: digest mismatch"
            )
        recorded_report = challenge.get("report_sha256")
        computed_report = compute_weak_oracle_report_sha256(challenge)
        if recorded_report != computed_report:
            errors.append("weak oracle challenge.report_sha256: digest mismatch")
        errors.extend(
            _differences(
                expected,
                challenge,
                context="weak oracle challenge",
            )
        )
    except (
        DW001OracleChallengeError,
        DeltaWitnessError,
        KeyError,
        TypeError,
        IndexError,
        ValueError,
        OverflowError,
        StopIteration,
    ) as exc:
        if isinstance(exc, DW001OracleChallengeError):
            return False, (str(exc),)
        return False, (
            "weak oracle challenge: verification failed closed: "
            f"{type(exc).__name__}: {exc}",
        )
    unique = tuple(dict.fromkeys(errors))
    return not unique, unique


__all__ = [
    "CHALLENGE_ID",
    "CHALLENGE_SCHEMA_VERSION",
    "DECLARED_SELECTOR",
    "DW001OracleChallengeError",
    "FAMILY_ID",
    "HIDDEN_CLAIM_SELECTOR",
    "MUTANT_ID",
    "compute_weak_oracle_challenge_sha256",
    "compute_weak_oracle_report_sha256",
    "run_weak_proxy_oracle_challenge",
    "verify_weak_oracle_challenge_document",
]
