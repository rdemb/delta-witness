"""DW-001 fixture-to-manifest relation contract.

The binding joins three independently verified pre-execution artifacts without
mutating their existing v1 schemas:

- a deterministic synthetic fixture descriptor;
- the exact Git/specification identity emitted for that descriptor;
- a versioned DW-001 scenario manifest.

No function in this module executes repository code. A valid binding establishes
only deterministic correspondence among supplied artifacts. It does not
authenticate a producer, prove creation time, validate a complete environment,
or authorize a pilot or holdout.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from copy import deepcopy
from pathlib import PurePosixPath
import re
from typing import Any

from .dw001 import (
    METHOD_STATE_SETS,
    OBSERVER_IDENTIFIERS,
    STATE_ORDER,
)
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
_CONTROL_ROLES = {"valid-patch-control", "false-assurance-case"}
_STATE_OBSERVATIONS = {"pass", "fail", "error", "timeout"}
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
_HEX_PATTERN = re.compile(r"[0-9a-f]+\Z")
_SCENARIO_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")

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
_SOURCES_FIELDS = {"descriptor", "fixture_identity", "scenario_manifest"}
_SOURCE_FIELDS = {"schema_version", "sha256"}
_COMPONENT_FIELDS = {"id", "version"}
_GIT_FIELDS = {
    "object_format",
    "base_commit_sha",
    "base_tree_sha",
    "head_commit_sha",
    "head_tree_sha",
}
_SPECIFICATION_FIELDS = {"path", "sha256"}
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


class DW001FixtureBindingError(DeltaWitnessError):
    """Raised when fixture and manifest evidence cannot be bound safely."""


def _error(context: str, message: str) -> DW001FixtureBindingError:
    return DW001FixtureBindingError(f"{context}: {message}")


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


def _scenario_id(value: object, *, context: str) -> str:
    text = _string(value, context=context)
    if _SCENARIO_ID_PATTERN.fullmatch(text) is None:
        raise _error(
            context,
            "must match [A-Za-z0-9][A-Za-z0-9._-]{0,127}",
        )
    return text


def _safe_path(value: object, *, context: str) -> str:
    path = _string(value, context=context)
    if path.startswith("/") or "\\" in path or "\x00" in path:
        raise _error(
            context,
            "must be a safe repository-relative POSIX path",
        )
    parts = PurePosixPath(path).parts
    if (
        not parts
        or any(
            part in {".", ".."} or part.casefold() == ".git"
            for part in parts
        )
    ):
        raise _error(
            context,
            "must be a safe repository-relative POSIX path",
        )
    return path


def _strings(
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


def _require_equal(context: str, actual: object, expected: object) -> None:
    if actual != expected:
        raise _error(context, "does not match the verified fixture sources")


def _safe_verify(
    label: str,
    verifier: Callable[..., tuple[bool, tuple[str, ...]]],
    *documents: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        return verifier(*documents)
    except (DeltaWitnessError, KeyError, TypeError, IndexError) as exc:
        return False, (
            f"{label} verification could not complete safely: "
            f"{type(exc).__name__}: {exc}",
        )


def _preflight_sources(
    descriptor: object,
    identity: object,
    manifest: object,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    descriptor_valid, descriptor_errors = _safe_verify(
        "fixture descriptor",
        verify_fixture_descriptor_document,
        descriptor,
    )
    identity_valid, identity_errors = _safe_verify(
        "fixture identity",
        verify_fixture_identity_document,
        identity,
        descriptor,
    )
    manifest_valid, manifest_errors = _safe_verify(
        "scenario manifest",
        verify_scenario_manifest_document,
        manifest,
    )
    errors = tuple(
        dict.fromkeys(
            [
                *descriptor_errors,
                *identity_errors,
                *manifest_errors,
            ]
        )
    )
    if not (descriptor_valid and identity_valid and manifest_valid):
        detail = "; ".join(errors) if errors else "source verification failed"
        raise _error("fixture-manifest source preflight", detail)
    if not (
        isinstance(descriptor, dict)
        and isinstance(identity, dict)
        and isinstance(manifest, dict)
    ):
        raise _error(
            "fixture-manifest source preflight",
            "verified sources must be objects",
        )
    return descriptor, identity, manifest


def _manifest_state_slice(manifest: Mapping[str, object]) -> list[dict[str, Any]]:
    ground_truth = _object(
        manifest["ground_truth"],
        context="scenario manifest.ground_truth",
    )
    states = ground_truth["states"]
    if not isinstance(states, list):
        raise _error(
            "scenario manifest.ground_truth.states",
            "must be a list",
        )
    result: list[dict[str, Any]] = []
    for index, item in enumerate(states):
        state = _object(
            item,
            context=f"scenario manifest.ground_truth.states[{index}]",
        )
        result.append(
            {
                "state": state["state"],
                "applicable": state["applicable"],
                "expected_observed": state["expected_observed"],
                "failure_cause": state["failure_cause"],
            }
        )
    return result


def _manifest_method_slice(
    manifest: Mapping[str, object],
) -> list[dict[str, Any]]:
    ground_truth = _object(
        manifest["ground_truth"],
        context="scenario manifest.ground_truth",
    )
    methods = ground_truth["methods"]
    if not isinstance(methods, list):
        raise _error(
            "scenario manifest.ground_truth.methods",
            "must be a list",
        )
    result: list[dict[str, Any]] = []
    for index, item in enumerate(methods):
        method = _object(
            item,
            context=f"scenario manifest.ground_truth.methods[{index}]",
        )
        result.append(
            {
                "method_id": method["method_id"],
                "decision": method["expected_decision"],
                "reason_code": method["reason_code"],
            }
        )
    return result


def _require_source_relations(
    descriptor: Mapping[str, object],
    identity: Mapping[str, object],
    manifest: Mapping[str, object],
) -> None:
    _require_equal(
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
        _require_equal(
            f"fixture identity.{field}",
            identity[field],
            descriptor[field],
        )

    _require_equal(
        "scenario manifest.study_id",
        manifest["study_id"],
        descriptor["study_id"],
    )
    _require_equal(
        "scenario manifest.scenario_id",
        manifest["scenario_id"],
        descriptor["scenario_id"],
    )

    provenance = _object(
        manifest["provenance"],
        context="scenario manifest.provenance",
    )
    _require_equal(
        "scenario manifest.provenance.source_type",
        provenance["source_type"],
        "synthetic",
    )
    _require_equal(
        "scenario manifest.provenance.authorization_basis",
        provenance["authorization_basis"],
        "owned_synthetic_fixture",
    )

    identity_git = _object(
        identity["git"],
        context="fixture identity.git",
    )
    manifest_git = _object(
        manifest["git"],
        context="scenario manifest.git",
    )
    _require_equal(
        "scenario manifest.git.base_sha",
        manifest_git["base_sha"],
        identity_git["base_commit_sha"],
    )
    _require_equal(
        "scenario manifest.git.head_sha",
        manifest_git["head_sha"],
        identity_git["head_commit_sha"],
    )
    _require_equal(
        "scenario manifest.paths",
        manifest["paths"],
        descriptor["paths"],
    )

    execution = _object(
        manifest["execution"],
        context="scenario manifest.execution",
    )
    for field in ("command", "observer", "observer_id", "timeout_seconds"):
        _require_equal(
            f"scenario manifest.execution.{field}",
            execution[field],
            descriptor[field],
        )

    _require_equal(
        "scenario manifest.ground truth states",
        _manifest_state_slice(manifest),
        descriptor["expected_states"],
    )
    _require_equal(
        "scenario manifest.ground truth methods",
        _manifest_method_slice(manifest),
        descriptor["expected_methods"],
    )

    ground_truth = _object(
        manifest["ground_truth"],
        context="scenario manifest.ground_truth",
    )
    _require_equal(
        "scenario manifest.ground truth false assurance mechanism",
        ground_truth["false_assurance_mechanism"],
        descriptor["family_id"],
    )

    specification = _object(
        identity["specification"],
        context="fixture identity.specification",
    )
    _require_equal(
        "fixture identity.specification.sha256",
        specification["sha256"],
        compute_fixture_specification_sha256(descriptor),
    )
    paths = _object(
        descriptor["paths"],
        context="fixture descriptor.paths",
    )
    documentation = paths["documentation"]
    if not isinstance(documentation, list):
        raise _error(
            "fixture descriptor.paths.documentation",
            "must be a list",
        )
    if specification["path"] not in documentation:
        raise _error(
            "fixture identity.specification.path",
            "does not match scenario manifest documentation paths",
        )


def _validate_sources(value: object) -> None:
    sources = _object(value, context="fixture-manifest binding.sources")
    _exact_keys(
        sources,
        _SOURCES_FIELDS,
        context="fixture-manifest binding.sources",
    )
    versions = {
        "descriptor": FIXTURE_DESCRIPTOR_SCHEMA_VERSION,
        "fixture_identity": FIXTURE_IDENTITY_SCHEMA_VERSION,
        "scenario_manifest": SCENARIO_SCHEMA_VERSION,
    }
    for name, version in versions.items():
        context = f"fixture-manifest binding.sources.{name}"
        source = _object(sources[name], context=context)
        _exact_keys(source, _SOURCE_FIELDS, context=context)
        if source["schema_version"] != version:
            raise _error(
                f"{context}.schema_version",
                f"must be {version!r}",
            )
        _hex(source["sha256"], context=f"{context}.sha256", lengths=(64,))


def _validate_component(
    value: object,
    *,
    context: str,
    expected_id: str,
    expected_version: str,
) -> None:
    component = _object(value, context=context)
    _exact_keys(component, _COMPONENT_FIELDS, context=context)
    if (
        component["id"] != expected_id
        or component["version"] != expected_version
    ):
        raise _error(context, "identifier or version is unsupported")


def _validate_git(value: object) -> None:
    git = _object(value, context="fixture-manifest binding.git")
    _exact_keys(git, _GIT_FIELDS, context="fixture-manifest binding.git")
    if git["object_format"] != "sha1":
        raise _error(
            "fixture-manifest binding.git.object_format",
            "must be 'sha1'",
        )
    for field in (
        "base_commit_sha",
        "base_tree_sha",
        "head_commit_sha",
        "head_tree_sha",
    ):
        _hex(
            git[field],
            context=f"fixture-manifest binding.git.{field}",
            lengths=(40,),
        )
    if git["base_commit_sha"] == git["head_commit_sha"]:
        raise _error(
            "fixture-manifest binding.git",
            "base and head commits must differ",
        )


def _validate_paths(value: object) -> None:
    paths = _object(value, context="fixture-manifest binding.paths")
    _exact_keys(paths, _PATH_FIELDS, context="fixture-manifest binding.paths")
    all_paths: list[str] = []
    for category in ("code", "tests", "documentation"):
        items = _strings(
            paths[category],
            context=f"fixture-manifest binding.paths.{category}",
            allow_empty=category == "documentation",
        )
        if category in {"code", "tests"} and not items:
            raise _error(
                f"fixture-manifest binding.paths.{category}",
                "must be a non-empty list",
            )
        for index, item in enumerate(items):
            _safe_path(
                item,
                context=f"fixture-manifest binding.paths.{category}[{index}]",
            )
        all_paths.extend(items)
    if len(all_paths) != len(set(all_paths)):
        raise _error(
            "fixture-manifest binding.paths",
            "path categories must be disjoint",
        )
    ordered = sorted(all_paths)
    for index, path in enumerate(ordered):
        prefix = f"{path}/"
        if any(other.startswith(prefix) for other in ordered[index + 1 :]):
            raise _error(
                "fixture-manifest binding.paths",
                "must be prefix-free",
            )


def _validate_binding_structure(document: object) -> dict[str, Any]:
    binding = _object(document, context="fixture-manifest binding")
    _exact_keys(binding, _ROOT_FIELDS, context="fixture-manifest binding")
    if binding["schema_version"] != BINDING_SCHEMA_VERSION:
        raise _error(
            "fixture-manifest binding.schema_version",
            f"must be {BINDING_SCHEMA_VERSION!r}",
        )
    if binding["study_id"] != STUDY_ID:
        raise _error(
            "fixture-manifest binding.study_id",
            f"must be {STUDY_ID!r}",
        )
    _scenario_id(
        binding["scenario_id"],
        context="fixture-manifest binding.scenario_id",
    )
    _validate_sources(binding["sources"])

    family_id = _string(
        binding["family_id"],
        context="fixture-manifest binding.family_id",
    )
    if family_id not in SUPPORTED_FAMILIES:
        raise _error(
            "fixture-manifest binding.family_id",
            "family is unsupported",
        )
    if binding["control_role"] not in _CONTROL_ROLES:
        raise _error(
            "fixture-manifest binding.control_role",
            "is unsupported",
        )
    _validate_component(
        binding["generator"],
        context="fixture-manifest binding.generator",
        expected_id=GENERATOR_ID,
        expected_version=GENERATOR_VERSION,
    )
    _validate_component(
        binding["template"],
        context="fixture-manifest binding.template",
        expected_id=_TEMPLATE_ID,
        expected_version=_TEMPLATE_VERSION,
    )

    observer = _string(
        binding["observer"],
        context="fixture-manifest binding.observer",
    )
    if observer not in OBSERVER_IDENTIFIERS:
        raise _error(
            "fixture-manifest binding.observer",
            "is unsupported",
        )
    if binding["observer_id"] != OBSERVER_IDENTIFIERS[observer]:
        raise _error(
            "fixture-manifest binding.observer_id",
            "is inconsistent with observer",
        )

    _validate_git(binding["git"])
    specification = _object(
        binding["specification"],
        context="fixture-manifest binding.specification",
    )
    _exact_keys(
        specification,
        _SPECIFICATION_FIELDS,
        context="fixture-manifest binding.specification",
    )
    _safe_path(
        specification["path"],
        context="fixture-manifest binding.specification.path",
    )
    _hex(
        specification["sha256"],
        context="fixture-manifest binding.specification.sha256",
        lengths=(64,),
    )
    _validate_paths(binding["paths"])

    execution = _object(
        binding["execution"],
        context="fixture-manifest binding.execution",
    )
    _exact_keys(
        execution,
        _EXECUTION_FIELDS,
        context="fixture-manifest binding.execution",
    )
    _strings(
        execution["command"],
        context="fixture-manifest binding.execution.command",
        allow_empty=False,
        unique=False,
    )
    timeout = execution["timeout_seconds"]
    if (
        not isinstance(timeout, int)
        or isinstance(timeout, bool)
        or not 1 <= timeout <= 86_400
    ):
        raise _error(
            "fixture-manifest binding.execution.timeout_seconds",
            "must be an integer between 1 and 86400",
        )

    states = binding["expected_states"]
    if not isinstance(states, list) or len(states) != len(STATE_ORDER):
        raise _error(
            "fixture-manifest binding.expected_states",
            "must contain exactly four ordered states",
        )
    for index, state_name in enumerate(STATE_ORDER):
        context = f"fixture-manifest binding.expected_states[{state_name}]"
        state = _object(states[index], context=context)
        _exact_keys(state, _STATE_FIELDS, context=context)
        if state["state"] != state_name:
            raise _error(context, f"state must be {state_name!r}")
        if state["applicable"] is not True:
            raise _error(
                f"{context}.applicable",
                "binding v1 supports only applicable generator states",
            )
        if state["expected_observed"] not in _STATE_OBSERVATIONS:
            raise _error(f"{context}.expected_observed", "is unsupported")
        if state["failure_cause"] not in _FAILURE_CAUSES:
            raise _error(f"{context}.failure_cause", "is unsupported")

    methods = binding["expected_methods"]
    if (
        not isinstance(methods, list)
        or len(methods) != len(METHOD_STATE_SETS)
    ):
        raise _error(
            "fixture-manifest binding.expected_methods",
            "must contain exactly four ordered methods",
        )
    for index, (method_id, _) in enumerate(METHOD_STATE_SETS):
        context = f"fixture-manifest binding.expected_methods[{method_id}]"
        method = _object(methods[index], context=context)
        _exact_keys(method, _METHOD_FIELDS, context=context)
        if method["method_id"] != method_id:
            raise _error(context, f"method_id must be {method_id!r}")
        if method["decision"] not in _METHOD_DECISIONS:
            raise _error(f"{context}.decision", "is unsupported")
        if method["reason_code"] not in _METHOD_REASONS:
            raise _error(f"{context}.reason_code", "is unsupported")

    scope = _object(
        binding["relation_scope"],
        context="fixture-manifest binding.relation_scope",
    )
    _exact_keys(
        scope,
        _SCOPE_FIELDS,
        context="fixture-manifest binding.relation_scope",
    )
    expected_scope = {
        "verified_relations": list(_VERIFIED_RELATIONS),
        "manifest_owned_fields": list(_MANIFEST_OWNED_FIELDS),
        "fixture_only_fields": list(_FIXTURE_ONLY_FIELDS),
    }
    for field, expected in expected_scope.items():
        actual = _strings(
            scope[field],
            context=f"fixture-manifest binding.relation_scope.{field}",
        )
        if actual != expected:
            raise _error(
                f"fixture-manifest binding.relation_scope.{field}",
                "does not match the v1 scope contract",
            )
    _hex(
        binding["binding_sha256"],
        context="fixture-manifest binding.binding_sha256",
        lengths=(64,),
    )
    return binding


def compute_fixture_manifest_binding_sha256(
    document: dict[str, Any],
) -> str:
    """Hash canonical bytes with the binding digest field normalized."""

    normalized = deepcopy(document)
    normalized["binding_sha256"] = None
    return sha256_document(normalized)


def _derive_binding(
    descriptor: Mapping[str, object],
    identity: Mapping[str, object],
    manifest: Mapping[str, object],
) -> dict[str, Any]:
    _require_source_relations(descriptor, identity, manifest)
    identity_git = _object(
        identity["git"],
        context="fixture identity.git",
    )
    specification = _object(
        identity["specification"],
        context="fixture identity.specification",
    )
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
        "git": deepcopy(identity_git),
        "specification": deepcopy(specification),
        "paths": deepcopy(descriptor["paths"]),
        "execution": {
            "command": deepcopy(descriptor["command"]),
            "timeout_seconds": descriptor["timeout_seconds"],
        },
        "expected_states": deepcopy(descriptor["expected_states"]),
        "expected_methods": deepcopy(descriptor["expected_methods"]),
        "relation_scope": {
            "verified_relations": list(_VERIFIED_RELATIONS),
            "manifest_owned_fields": list(_MANIFEST_OWNED_FIELDS),
            "fixture_only_fields": list(_FIXTURE_ONLY_FIELDS),
        },
        "binding_sha256": None,
    }
    binding["binding_sha256"] = compute_fixture_manifest_binding_sha256(
        binding
    )
    return binding


def build_fixture_manifest_binding(
    descriptor: object,
    identity: object,
    manifest: object,
) -> dict[str, Any]:
    """Build a binding only from verified and mutually consistent sources."""

    verified = _preflight_sources(descriptor, identity, manifest)
    binding = _derive_binding(*verified)
    _validate_binding_structure(binding)
    return binding


def verify_fixture_manifest_binding_document(
    binding: object,
    descriptor: object,
    identity: object,
    manifest: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify source artifacts, relation semantics, structure, and digest."""

    try:
        verified = _preflight_sources(descriptor, identity, manifest)
    except DW001FixtureBindingError as exc:
        return False, (str(exc),)

    errors: list[str] = []
    try:
        document = _validate_binding_structure(binding)
    except DW001FixtureBindingError as exc:
        errors.append(str(exc))
        document = binding if isinstance(binding, dict) else None

    if isinstance(document, dict):
        recorded = document.get("binding_sha256")
        if isinstance(recorded, str):
            observed = compute_fixture_manifest_binding_sha256(document)
            if observed != recorded:
                errors.append(
                    "fixture-manifest binding digest mismatch: "
                    f"expected {recorded}, computed {observed}"
                )
        try:
            expected = _derive_binding(*verified)
        except DW001FixtureBindingError as exc:
            errors.append(str(exc))
        else:
            if document != expected:
                errors.append(
                    "fixture-manifest binding does not match supplied source "
                    "artifacts"
                )

    combined = tuple(dict.fromkeys(errors))
    return not combined, combined


__all__ = [
    "BINDING_SCHEMA_VERSION",
    "DW001FixtureBindingError",
    "build_fixture_manifest_binding",
    "compute_fixture_manifest_binding_sha256",
    "verify_fixture_manifest_binding_document",
]
