"""Deterministic DW-001 fixture-to-manifest relation contract.

This module joins one verified synthetic fixture descriptor, one verified
fixture identity, and one verified scenario manifest without mutating any of
their existing v1 schemas. It executes no repository code and provides no
producer authentication, timestamping, sandboxing, or pilot authorization.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from copy import deepcopy
from pathlib import PurePosixPath
import re
from typing import Any

from .dw001 import METHOD_STATE_SETS, OBSERVER_IDENTIFIERS, STATE_ORDER
from .dw001_contracts import (
    SCENARIO_SCHEMA_VERSION,
    STUDY_ID,
    verify_scenario_manifest_document,
)
from .dw001_scenarios import (
    FIXTURE_DESCRIPTOR_SCHEMA_VERSION,
    FIXTURE_IDENTITY_SCHEMA_VERSION,
    GENERATOR_ID,
    GENERATOR_VERSION,
    SUPPORTED_FAMILIES,
    compute_fixture_specification_sha256,
    verify_fixture_descriptor_document,
    verify_fixture_identity_document,
)
from .errors import DeltaWitnessError
from .reporting import sha256_document


BINDING_SCHEMA_VERSION = "deltawitness.dw001-fixture-manifest-binding.v1"

_TEMPLATE_ID = "python-role-check"
_TEMPLATE_VERSION = "1"
_HEX = re.compile(r"[0-9a-f]+\Z")
_SCENARIO_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")

_ROOT_FIELDS = {
    "schema_version",
    "study_id",
    "scenario_id",
    "sources",
    "family_id",
    "control_role",
    "generator",
    "template",
    "observer",
    "observer_id",
    "git",
    "specification",
    "paths",
    "execution",
    "expected_states",
    "expected_methods",
    "relation_scope",
    "binding_sha256",
}
_SOURCE_FIELDS = {"schema_version", "sha256"}
_COMPONENT_FIELDS = {"id", "version"}
_GIT_FIELDS = {
    "object_format",
    "base_commit_sha",
    "base_tree_sha",
    "head_commit_sha",
    "head_tree_sha",
}
_SPEC_FIELDS = {"path", "sha256"}
_PATH_FIELDS = {"code", "tests", "documentation"}
_EXECUTION_FIELDS = {"command", "timeout_seconds"}
_STATE_FIELDS = {"state", "applicable", "expected_observed", "failure_cause"}
_METHOD_FIELDS = {"method_id", "decision", "reason_code"}
_SCOPE_FIELDS = {
    "verified_relations",
    "manifest_owned_fields",
    "fixture_only_fields",
}

_VERIFIED_RELATIONS = (
    "study_id",
    "scenario_id",
    "descriptor_to_identity",
    "manifest_synthetic_provenance",
    "git_base_commit",
    "git_head_commit",
    "path_categories",
    "execution_command",
    "execution_observer",
    "execution_timeout",
    "ground_truth_states",
    "ground_truth_methods",
    "false_assurance_family",
    "specification_path_membership",
)
_MANIFEST_OWNED_FIELDS = (
    "partition",
    "partition_lock",
    "provenance.source_id",
    "provenance.license_expression",
    "provenance.authorization_reference",
    "provenance.public_release_allowed",
    "git.repository_id",
    "execution.pass_exit_codes",
    "execution.fail_exit_codes",
    "execution.pass_env",
    "execution.environment_requirements",
    "ground_truth.environment_assumptions",
    "review",
)
_FIXTURE_ONLY_FIELDS = (
    "family_id",
    "control_role",
    "generator",
    "template",
    "git.object_format",
    "git.base_tree_sha",
    "git.head_tree_sha",
    "specification.sha256",
)
_EXPECTED_SCOPE = {
    "verified_relations": list(_VERIFIED_RELATIONS),
    "manifest_owned_fields": list(_MANIFEST_OWNED_FIELDS),
    "fixture_only_fields": list(_FIXTURE_ONLY_FIELDS),
}

_CONTROL_ROLES = {"valid-patch-control", "false-assurance-case"}
_STATE_VALUES = {"pass", "fail", "error", "timeout"}
_FAILURE_CAUSES = {
    "none",
    "assertion_failure",
    "test_failure_untyped",
    "timeout",
    "unknown_error",
}
_METHOD_DECISIONS = {"accept", "reject", "indeterminate", "not_applicable"}
_METHOD_REASONS = {
    "predicate_satisfied",
    "predicate_contradicted",
    "required_state_indeterminate",
    "required_state_not_applicable",
}


class DW001FixtureBindingError(DeltaWitnessError):
    """Raised when fixture and manifest evidence cannot be bound safely."""


def _error(context: str, message: str) -> DW001FixtureBindingError:
    return DW001FixtureBindingError(f"{context}: {message}")


def _obj(value: object, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _error(context, "must be an object")
    return value


def _keys(value: Mapping[str, object], expected: set[str], context: str) -> None:
    actual = set(value)
    if actual != expected:
        raise _error(
            context,
            f"field mismatch; missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}",
        )


def _str(value: object, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise _error(context, "must be a non-empty string")
    return value


def _hex(value: object, context: str, lengths: Sequence[int]) -> str:
    text = _str(value, context)
    if len(text) not in lengths or _HEX.fullmatch(text) is None:
        raise _error(
            context,
            f"must be lowercase hexadecimal with length in {tuple(lengths)}",
        )
    return text


def _list_of_strings(
    value: object,
    context: str,
    *,
    allow_empty: bool = True,
    unique: bool = True,
) -> list[str]:
    if not isinstance(value, list) or (not allow_empty and not value):
        qualifier = "a list" if allow_empty else "a non-empty list"
        raise _error(context, f"must be {qualifier} of strings")
    result = [_str(item, f"{context}[{index}]") for index, item in enumerate(value)]
    if unique and len(result) != len(set(result)):
        raise _error(context, "must not contain duplicates")
    return result


def _safe_path(value: object, context: str) -> str:
    path = _str(value, context)
    if path.startswith("/") or "\\" in path or "\x00" in path:
        raise _error(context, "must be a safe repository-relative POSIX path")
    parts = PurePosixPath(path).parts
    if not parts or any(
        part in {".", ".."} or part.casefold() == ".git" for part in parts
    ):
        raise _error(context, "must be a safe repository-relative POSIX path")
    return path


def _equal(context: str, actual: object, expected: object) -> None:
    if actual != expected:
        raise _error(context, "does not match the verified fixture sources")


def _safe_verify(
    label: str,
    verifier: Callable[..., tuple[bool, tuple[str, ...]]],
    *documents: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        return verifier(*documents)
    except (DeltaWitnessError, KeyError, TypeError, IndexError, ValueError) as exc:
        return False, (
            f"{label} verification could not complete safely: "
            f"{type(exc).__name__}: {exc}",
        )


def _preflight(
    descriptor: object,
    identity: object,
    manifest: object,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    checks = (
        (
            "fixture descriptor",
            *_safe_verify(
                "fixture descriptor",
                verify_fixture_descriptor_document,
                descriptor,
            ),
        ),
        (
            "fixture identity",
            *_safe_verify(
                "fixture identity",
                verify_fixture_identity_document,
                identity,
                descriptor,
            ),
        ),
        (
            "scenario manifest",
            *_safe_verify(
                "scenario manifest",
                verify_scenario_manifest_document,
                manifest,
            ),
        ),
    )
    errors = [
        f"{label}: {error}"
        for label, valid, messages in checks
        if not valid
        for error in (messages or ("verification failed",))
    ]
    if errors:
        raise _error("fixture-manifest source preflight", "; ".join(errors))
    if not all(isinstance(item, dict) for item in (descriptor, identity, manifest)):
        raise _error(
            "fixture-manifest source preflight",
            "verified sources must be objects",
        )
    return descriptor, identity, manifest


def _manifest_states(manifest: Mapping[str, object]) -> list[dict[str, Any]]:
    ground_truth = _obj(manifest["ground_truth"], "scenario manifest.ground_truth")
    states = ground_truth.get("states")
    if not isinstance(states, list):
        raise _error("scenario manifest.ground_truth.states", "must be a list")
    result: list[dict[str, Any]] = []
    for index, item in enumerate(states):
        state = _obj(item, f"scenario manifest.ground_truth.states[{index}]")
        result.append(
            {
                "state": state.get("state"),
                "applicable": state.get("applicable"),
                "expected_observed": state.get("expected_observed"),
                "failure_cause": state.get("failure_cause"),
            }
        )
    return result


def _manifest_methods(manifest: Mapping[str, object]) -> list[dict[str, Any]]:
    ground_truth = _obj(manifest["ground_truth"], "scenario manifest.ground_truth")
    methods = ground_truth.get("methods")
    if not isinstance(methods, list):
        raise _error("scenario manifest.ground_truth.methods", "must be a list")
    result: list[dict[str, Any]] = []
    for index, item in enumerate(methods):
        method = _obj(item, f"scenario manifest.ground_truth.methods[{index}]")
        result.append(
            {
                "method_id": method.get("method_id"),
                "decision": method.get("expected_decision"),
                "reason_code": method.get("reason_code"),
            }
        )
    return result


def _check_relations(
    descriptor: Mapping[str, object],
    identity: Mapping[str, object],
    manifest: Mapping[str, object],
) -> None:
    _equal(
        "fixture identity.descriptor_sha256",
        identity["descriptor_sha256"],
        descriptor["descriptor_sha256"],
    )
    for field in (
        "study_id",
        "scenario_id",
        "family_id",
        "control_role",
        "generator",
        "template",
        "observer",
        "observer_id",
        "paths",
        "expected_states",
        "expected_methods",
    ):
        _equal(f"fixture identity.{field}", identity[field], descriptor[field])

    _equal("scenario manifest.study_id", manifest["study_id"], descriptor["study_id"])
    _equal(
        "scenario manifest.scenario_id",
        manifest["scenario_id"],
        descriptor["scenario_id"],
    )

    provenance = _obj(manifest["provenance"], "scenario manifest.provenance")
    _equal(
        "scenario manifest.provenance.source_type",
        provenance.get("source_type"),
        "synthetic",
    )
    _equal(
        "scenario manifest.provenance.authorization_basis",
        provenance.get("authorization_basis"),
        "owned_synthetic_fixture",
    )

    identity_git = _obj(identity["git"], "fixture identity.git")
    manifest_git = _obj(manifest["git"], "scenario manifest.git")
    _equal(
        "scenario manifest.git.base_sha",
        manifest_git.get("base_sha"),
        identity_git.get("base_commit_sha"),
    )
    _equal(
        "scenario manifest.git.head_sha",
        manifest_git.get("head_sha"),
        identity_git.get("head_commit_sha"),
    )
    _equal("scenario manifest.paths", manifest["paths"], descriptor["paths"])

    execution = _obj(manifest["execution"], "scenario manifest.execution")
    # Report the semantic arm mismatch before derivative command differences.
    for field in ("observer", "observer_id", "command", "timeout_seconds"):
        _equal(
            f"scenario manifest.execution.{field}",
            execution.get(field),
            descriptor[field],
        )

    _equal(
        "scenario manifest.ground truth states",
        _manifest_states(manifest),
        descriptor["expected_states"],
    )
    _equal(
        "scenario manifest.ground truth methods",
        _manifest_methods(manifest),
        descriptor["expected_methods"],
    )
    ground_truth = _obj(manifest["ground_truth"], "scenario manifest.ground_truth")
    _equal(
        "scenario manifest.ground truth false assurance mechanism",
        ground_truth.get("false_assurance_mechanism"),
        descriptor["family_id"],
    )

    specification = _obj(identity["specification"], "fixture identity.specification")
    _equal(
        "fixture identity.specification.sha256",
        specification.get("sha256"),
        compute_fixture_specification_sha256(descriptor),
    )
    paths = _obj(descriptor["paths"], "fixture descriptor.paths")
    documentation = paths.get("documentation")
    if not isinstance(documentation, list):
        raise _error("fixture descriptor.paths.documentation", "must be a list")
    if specification.get("path") not in documentation:
        raise _error(
            "fixture identity.specification.path",
            "does not match scenario manifest documentation paths",
        )


def _shape(binding: object) -> dict[str, Any]:
    document = _obj(binding, "fixture-manifest binding")
    _keys(document, _ROOT_FIELDS, "fixture-manifest binding")
    if document["schema_version"] != BINDING_SCHEMA_VERSION:
        raise _error("fixture-manifest binding.schema_version", "is unsupported")
    if document["study_id"] != STUDY_ID:
        raise _error("fixture-manifest binding.study_id", "must be 'DW-001'")
    scenario_id = _str(document["scenario_id"], "fixture-manifest binding.scenario_id")
    if _SCENARIO_ID.fullmatch(scenario_id) is None:
        raise _error("fixture-manifest binding.scenario_id", "has unsupported syntax")

    sources = _obj(document["sources"], "fixture-manifest binding.sources")
    _keys(
        sources,
        {"descriptor", "fixture_identity", "scenario_manifest"},
        "fixture-manifest binding.sources",
    )
    source_versions = {
        "descriptor": FIXTURE_DESCRIPTOR_SCHEMA_VERSION,
        "fixture_identity": FIXTURE_IDENTITY_SCHEMA_VERSION,
        "scenario_manifest": SCENARIO_SCHEMA_VERSION,
    }
    for name, expected_version in source_versions.items():
        source = _obj(sources[name], f"fixture-manifest binding.sources.{name}")
        _keys(source, _SOURCE_FIELDS, f"fixture-manifest binding.sources.{name}")
        if source["schema_version"] != expected_version:
            raise _error(
                f"fixture-manifest binding.sources.{name}.schema_version",
                "is unsupported",
            )
        _hex(source["sha256"], f"fixture-manifest binding.sources.{name}.sha256", (64,))

    family_id = _str(document["family_id"], "fixture-manifest binding.family_id")
    if family_id not in SUPPORTED_FAMILIES:
        raise _error("fixture-manifest binding.family_id", "family is unsupported")
    control_role = _str(
        document["control_role"],
        "fixture-manifest binding.control_role",
    )
    if control_role not in _CONTROL_ROLES:
        raise _error("fixture-manifest binding.control_role", "is unsupported")

    for field, expected_id, expected_version in (
        ("generator", GENERATOR_ID, GENERATOR_VERSION),
        ("template", _TEMPLATE_ID, _TEMPLATE_VERSION),
    ):
        component = _obj(document[field], f"fixture-manifest binding.{field}")
        _keys(component, _COMPONENT_FIELDS, f"fixture-manifest binding.{field}")
        if component.get("id") != expected_id or component.get("version") != expected_version:
            raise _error(f"fixture-manifest binding.{field}", "is unsupported")

    observer = _str(document["observer"], "fixture-manifest binding.observer")
    if observer not in OBSERVER_IDENTIFIERS:
        raise _error("fixture-manifest binding.observer", "is unsupported")
    if document["observer_id"] != OBSERVER_IDENTIFIERS[observer]:
        raise _error("fixture-manifest binding.observer_id", "is inconsistent with observer")

    git = _obj(document["git"], "fixture-manifest binding.git")
    _keys(git, _GIT_FIELDS, "fixture-manifest binding.git")
    if git.get("object_format") != "sha1":
        raise _error("fixture-manifest binding.git.object_format", "must be 'sha1'")
    for field in (
        "base_commit_sha",
        "base_tree_sha",
        "head_commit_sha",
        "head_tree_sha",
    ):
        _hex(git[field], f"fixture-manifest binding.git.{field}", (40,))

    specification = _obj(
        document["specification"],
        "fixture-manifest binding.specification",
    )
    _keys(specification, _SPEC_FIELDS, "fixture-manifest binding.specification")
    _safe_path(specification["path"], "fixture-manifest binding.specification.path")
    _hex(specification["sha256"], "fixture-manifest binding.specification.sha256", (64,))

    paths = _obj(document["paths"], "fixture-manifest binding.paths")
    _keys(paths, _PATH_FIELDS, "fixture-manifest binding.paths")
    flattened: list[str] = []
    for category in ("code", "tests", "documentation"):
        items = _list_of_strings(
            paths[category],
            f"fixture-manifest binding.paths.{category}",
            allow_empty=category == "documentation",
        )
        for index, item in enumerate(items):
            _safe_path(item, f"fixture-manifest binding.paths.{category}[{index}]")
        flattened.extend(items)
    if len(flattened) != len(set(flattened)):
        raise _error("fixture-manifest binding.paths", "categories must be disjoint")

    execution = _obj(document["execution"], "fixture-manifest binding.execution")
    _keys(execution, _EXECUTION_FIELDS, "fixture-manifest binding.execution")
    _list_of_strings(
        execution["command"],
        "fixture-manifest binding.execution.command",
        allow_empty=False,
        unique=False,
    )
    timeout = execution["timeout_seconds"]
    if not isinstance(timeout, int) or isinstance(timeout, bool) or not 1 <= timeout <= 86_400:
        raise _error(
            "fixture-manifest binding.execution.timeout_seconds",
            "must be an integer between 1 and 86400",
        )

    states = document["expected_states"]
    if not isinstance(states, list) or len(states) != len(STATE_ORDER):
        raise _error(
            "fixture-manifest binding.expected_states",
            "must contain exactly four ordered states",
        )
    for index, state_name in enumerate(STATE_ORDER):
        state = _obj(states[index], f"fixture-manifest binding.expected_states[{index}]")
        _keys(state, _STATE_FIELDS, f"fixture-manifest binding.expected_states[{index}]")
        if state.get("state") != state_name or state.get("applicable") is not True:
            raise _error(
                f"fixture-manifest binding.expected_states[{index}]",
                "state order or applicability is inconsistent",
            )
        observed = _str(
            state.get("expected_observed"),
            f"fixture-manifest binding.expected_states[{index}].expected_observed",
        )
        cause = _str(
            state.get("failure_cause"),
            f"fixture-manifest binding.expected_states[{index}].failure_cause",
        )
        if observed not in _STATE_VALUES or cause not in _FAILURE_CAUSES:
            raise _error(
                f"fixture-manifest binding.expected_states[{index}]",
                "contains unsupported semantics",
            )

    methods = document["expected_methods"]
    if not isinstance(methods, list) or len(methods) != len(METHOD_STATE_SETS):
        raise _error(
            "fixture-manifest binding.expected_methods",
            "must contain exactly four ordered methods",
        )
    for index, (method_id, _) in enumerate(METHOD_STATE_SETS):
        method = _obj(methods[index], f"fixture-manifest binding.expected_methods[{index}]")
        _keys(method, _METHOD_FIELDS, f"fixture-manifest binding.expected_methods[{index}]")
        decision = _str(
            method.get("decision"),
            f"fixture-manifest binding.expected_methods[{index}].decision",
        )
        reason = _str(
            method.get("reason_code"),
            f"fixture-manifest binding.expected_methods[{index}].reason_code",
        )
        if method.get("method_id") != method_id:
            raise _error(
                f"fixture-manifest binding.expected_methods[{index}].method_id",
                "is out of canonical order",
            )
        if decision not in _METHOD_DECISIONS or reason not in _METHOD_REASONS:
            raise _error(
                f"fixture-manifest binding.expected_methods[{index}]",
                "contains unsupported semantics",
            )

    scope = _obj(document["relation_scope"], "fixture-manifest binding.relation_scope")
    _keys(scope, _SCOPE_FIELDS, "fixture-manifest binding.relation_scope")
    for field, expected in _EXPECTED_SCOPE.items():
        actual = _list_of_strings(
            scope[field],
            f"fixture-manifest binding.relation_scope.{field}",
        )
        if actual != expected:
            raise _error(
                f"fixture-manifest binding.relation_scope.{field}",
                "does not match the v1 scope contract",
            )

    _hex(document["binding_sha256"], "fixture-manifest binding.binding_sha256", (64,))
    return document


def compute_fixture_manifest_binding_sha256(document: dict[str, Any]) -> str:
    """Hash canonical bytes with the binding digest field normalized."""

    if not isinstance(document, dict):
        raise _error("fixture-manifest binding", "must be an object")
    normalized = deepcopy(document)
    normalized["binding_sha256"] = None
    return sha256_document(normalized)


def _derive(
    descriptor: Mapping[str, object],
    identity: Mapping[str, object],
    manifest: Mapping[str, object],
) -> dict[str, Any]:
    _check_relations(descriptor, identity, manifest)
    binding: dict[str, Any] = {
        "schema_version": BINDING_SCHEMA_VERSION,
        "study_id": descriptor["study_id"],
        "scenario_id": descriptor["scenario_id"],
        "sources": {
            "descriptor": {
                "schema_version": descriptor["schema_version"],
                "sha256": descriptor["descriptor_sha256"],
            },
            "fixture_identity": {
                "schema_version": identity["schema_version"],
                "sha256": identity["identity_sha256"],
            },
            "scenario_manifest": {
                "schema_version": manifest["schema_version"],
                "sha256": manifest["manifest_sha256"],
            },
        },
        "family_id": descriptor["family_id"],
        "control_role": descriptor["control_role"],
        "generator": deepcopy(descriptor["generator"]),
        "template": deepcopy(descriptor["template"]),
        "observer": descriptor["observer"],
        "observer_id": descriptor["observer_id"],
        "git": deepcopy(identity["git"]),
        "specification": deepcopy(identity["specification"]),
        "paths": deepcopy(descriptor["paths"]),
        "execution": {
            "command": deepcopy(descriptor["command"]),
            "timeout_seconds": descriptor["timeout_seconds"],
        },
        "expected_states": deepcopy(descriptor["expected_states"]),
        "expected_methods": deepcopy(descriptor["expected_methods"]),
        "relation_scope": deepcopy(_EXPECTED_SCOPE),
        "binding_sha256": None,
    }
    binding["binding_sha256"] = compute_fixture_manifest_binding_sha256(binding)
    return binding


def build_fixture_manifest_binding(
    descriptor: object,
    identity: object,
    manifest: object,
) -> dict[str, Any]:
    """Derive a binding only from verified and mutually consistent sources."""

    binding = _derive(*_preflight(descriptor, identity, manifest))
    _shape(binding)
    return binding


def verify_fixture_manifest_binding_document(
    binding: object,
    descriptor: object,
    identity: object,
    manifest: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify source semantics, relation scope, canonical structure, and digest."""

    try:
        sources = _preflight(descriptor, identity, manifest)
    except DW001FixtureBindingError as exc:
        return False, (str(exc),)

    errors: list[str] = []
    document: dict[str, Any] | None
    try:
        document = _shape(binding)
    except (DW001FixtureBindingError, KeyError, TypeError, IndexError, ValueError) as exc:
        errors.append(
            str(exc)
            if isinstance(exc, DW001FixtureBindingError)
            else f"fixture-manifest binding: invalid structure: {type(exc).__name__}: {exc}"
        )
        document = binding if isinstance(binding, dict) else None

    if document is not None:
        recorded = document.get("binding_sha256")
        if isinstance(recorded, str):
            computed = compute_fixture_manifest_binding_sha256(document)
            if computed != recorded:
                errors.append(
                    "fixture-manifest binding digest mismatch: "
                    f"expected {recorded}, computed {computed}"
                )
        try:
            expected = _derive(*sources)
        except (DW001FixtureBindingError, KeyError, TypeError, IndexError, ValueError) as exc:
            errors.append(
                str(exc)
                if isinstance(exc, DW001FixtureBindingError)
                else f"fixture-manifest relation verification failed closed: "
                f"{type(exc).__name__}: {exc}"
            )
        else:
            if document != expected:
                errors.append(
                    "fixture-manifest binding does not match supplied source artifacts"
                )

    unique = tuple(dict.fromkeys(errors))
    return not unique, unique


__all__ = [
    "BINDING_SCHEMA_VERSION",
    "DW001FixtureBindingError",
    "build_fixture_manifest_binding",
    "compute_fixture_manifest_binding_sha256",
    "verify_fixture_manifest_binding_document",
]
