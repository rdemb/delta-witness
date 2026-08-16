"""Deterministic synthetic Git fixtures for DW-001 development-pilot preparation.

The generator supports a deliberately small owned-synthetic family subset. It
materializes fixed source, test, and specification bytes into an explicitly
supplied empty directory and returns public-safe Git and digest identities.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
import hashlib
import os
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Any

from .dw001 import (
    CANONICAL_EXPECTATIONS,
    METHOD_STATE_SETS,
    OBSERVER_IDENTIFIERS,
    STATE_ORDER,
)
from .errors import DeltaWitnessError
from .reporting import sha256_document

FIXTURE_DESCRIPTOR_SCHEMA_VERSION = "deltawitness.dw001-fixture-descriptor.v1"
FIXTURE_IDENTITY_SCHEMA_VERSION = "deltawitness.dw001-fixture-identity.v1"
STUDY_ID = "DW-001"
GENERATOR_ID = "deltawitness-synthetic-python"
GENERATOR_VERSION = "1"
TEMPLATE_ID = "python-role-check"
TEMPLATE_VERSION = "1"
SUPPORTED_FAMILIES = (
    "valid-discriminating-regression",
    "non-discriminating-candidate-test",
    "candidate-regression-against-base-tests",
)

_DESCRIPTOR_FIELDS = {
    "schema_version",
    "study_id",
    "scenario_id",
    "family_id",
    "control_role",
    "generator",
    "template",
    "observer",
    "observer_id",
    "command",
    "timeout_seconds",
    "paths",
    "expected_states",
    "expected_methods",
    "descriptor_sha256",
}
_IDENTITY_FIELDS = {
    "schema_version",
    "study_id",
    "scenario_id",
    "family_id",
    "control_role",
    "descriptor_sha256",
    "generator",
    "template",
    "observer",
    "observer_id",
    "git",
    "specification",
    "paths",
    "expected_states",
    "expected_methods",
    "identity_sha256",
}
_COMPONENT_FIELDS = {"id", "version"}
_PATH_FIELDS = {"code", "tests", "documentation"}
_STATE_FIELDS = {"state", "applicable", "expected_observed", "failure_cause"}
_METHOD_FIELDS = {"method_id", "decision", "reason_code"}
_GIT_FIELDS = {
    "object_format",
    "base_commit_sha",
    "base_tree_sha",
    "head_commit_sha",
    "head_tree_sha",
}
_SPECIFICATION_FIELDS = {"path", "sha256"}
_SCENARIO_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
_HEX_PATTERN = re.compile(r"[0-9a-f]+\Z")

_BASE_CODE = """def is_admin(user):
    return bool(user.get(\"role\"))
"""
_VALID_CODE = """def is_admin(user):
    return user.get(\"role\") == \"admin\"
"""
_REGRESSIVE_CODE = """def is_admin(user):
    return user.get(\"role\") != \"viewer\"
"""
_BASE_TESTS = """import sys
import unittest

sys.path.insert(0, \"src\")
from access import is_admin


class AccessTests(unittest.TestCase):
    def test_admin_is_allowed(self):
        self.assertTrue(is_admin({\"role\": \"admin\"}))

    def test_missing_role_is_denied(self):
        self.assertFalse(is_admin({}))
"""
_VALID_TESTS = _BASE_TESTS + """

    def test_viewer_is_denied(self):
        self.assertFalse(is_admin({\"role\": \"viewer\"}))
"""
_NONDISCRIMINATING_TESTS = _BASE_TESTS + """

    def test_second_admin_example(self):
        self.assertTrue(is_admin({\"role\": \"admin\"}))
"""
_REGRESSIVE_TESTS = """import sys
import unittest

sys.path.insert(0, \"src\")
from access import is_admin


class AccessTests(unittest.TestCase):
    def test_admin_is_allowed(self):
        self.assertTrue(is_admin({\"role\": \"admin\"}))

    def test_viewer_is_denied(self):
        self.assertFalse(is_admin({\"role\": \"viewer\"}))
"""

_FAMILY_DEFINITIONS: dict[str, dict[str, object]] = {
    "valid-discriminating-regression": {
        "control_role": "valid-patch-control",
        "candidate_code": _VALID_CODE,
        "candidate_tests": _VALID_TESTS,
        "outcomes": ("pass", "fail", "pass", "pass"),
    },
    "non-discriminating-candidate-test": {
        "control_role": "false-assurance-case",
        "candidate_code": _VALID_CODE,
        "candidate_tests": _NONDISCRIMINATING_TESTS,
        "outcomes": ("pass", "pass", "pass", "pass"),
    },
    "candidate-regression-against-base-tests": {
        "control_role": "false-assurance-case",
        "candidate_code": _REGRESSIVE_CODE,
        "candidate_tests": _REGRESSIVE_TESTS,
        "outcomes": ("pass", "fail", "fail", "pass"),
    },
}


class DW001ScenarioError(DeltaWitnessError):
    """Raised when a DW-001 synthetic fixture cannot be constructed safely."""


def _error(context: str, message: str) -> DW001ScenarioError:
    return DW001ScenarioError(f"{context}: {message}")


def _object(value: object, *, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _error(context, "must be an object")
    return value


def _exact_keys(value: Mapping[str, object], expected: set[str], *, context: str) -> None:
    actual = set(value)
    if actual != expected:
        raise _error(
            context,
            f"field mismatch; missing={sorted(expected - actual)}, extra={sorted(actual - expected)}",
        )


def _string(value: object, *, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise _error(context, "must be a non-empty string")
    return value


def _boolean(value: object, *, context: str) -> bool:
    if not isinstance(value, bool):
        raise _error(context, "must be a boolean")
    return value


def _integer(value: object, *, context: str, minimum: int, maximum: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise _error(context, "must be an integer")
    if not minimum <= value <= maximum:
        raise _error(context, f"must be between {minimum} and {maximum}")
    return value


def _hex(value: object, *, context: str, lengths: Sequence[int]) -> str:
    text = _string(value, context=context)
    if len(text) not in lengths or _HEX_PATTERN.fullmatch(text) is None:
        raise _error(context, f"must be lowercase hexadecimal with length in {tuple(lengths)}")
    return text


def _string_list(value: object, *, context: str, allow_empty: bool = True) -> list[str]:
    if not isinstance(value, list) or (not allow_empty and not value):
        qualifier = "a list" if allow_empty else "a non-empty list"
        raise _error(context, f"must be {qualifier} of strings")
    result = [_string(item, context=f"{context}[{index}]") for index, item in enumerate(value)]
    if len(set(result)) != len(result):
        raise _error(context, "must not contain duplicates")
    return result


def _scenario_id(value: object) -> str:
    text = _string(value, context="fixture descriptor.scenario_id")
    if _SCENARIO_ID_PATTERN.fullmatch(text) is None:
        raise _error(
            "fixture descriptor.scenario_id",
            "must match [A-Za-z0-9][A-Za-z0-9._-]{0,127}",
        )
    return text


def _observer_command(observer: str) -> list[str]:
    if observer == "exit-code-v1":
        return ["python", "-m", "unittest", "discover", "-s", "tests"]
    if observer == "outcome-receipt-v1":
        return [
            "python",
            "-m",
            "deltawitness.unittest_probe",
            "--start-directory",
            "tests",
            "--verbosity",
            "0",
        ]
    raise _error("fixture descriptor.observer", "is unsupported")


def _paths() -> dict[str, list[str]]:
    return {
        "code": ["src/access.py"],
        "tests": ["tests/test_access.py"],
        "documentation": ["deltawitness.toml"],
    }


def _state_failure_cause(observer: str, outcome: str) -> str:
    if outcome == "pass":
        return "none"
    if outcome == "fail":
        return "assertion_failure" if observer == "outcome-receipt-v1" else "test_failure_untyped"
    if outcome == "timeout":
        return "timeout"
    return "unknown_error"


def _expected_states(family_id: str, observer: str) -> list[dict[str, object]]:
    definition = _FAMILY_DEFINITIONS[family_id]
    outcomes = definition["outcomes"]
    assert isinstance(outcomes, tuple)
    return [
        {
            "state": state,
            "applicable": True,
            "expected_observed": outcomes[index],
            "failure_cause": _state_failure_cause(observer, outcomes[index]),
        }
        for index, state in enumerate(STATE_ORDER)
    ]


def _method_decision(
    states_by_name: Mapping[str, Mapping[str, object]],
    required_states: Sequence[str],
) -> tuple[str, str]:
    selected = [states_by_name[state] for state in required_states]
    if any(not state["applicable"] for state in selected):
        return "not_applicable", "required_state_not_applicable"
    if any(state["expected_observed"] in {"error", "timeout"} for state in selected):
        return "indeterminate", "required_state_indeterminate"
    if any(
        state["expected_observed"] != CANONICAL_EXPECTATIONS[state_name]
        for state_name, state in zip(required_states, selected)
    ):
        return "reject", "predicate_contradicted"
    return "accept", "predicate_satisfied"


def _expected_methods(states: Sequence[Mapping[str, object]]) -> list[dict[str, str]]:
    states_by_name = {str(state["state"]): state for state in states}
    result: list[dict[str, str]] = []
    for method_id, required_states in METHOD_STATE_SETS:
        decision, reason = _method_decision(states_by_name, required_states)
        result.append(
            {
                "method_id": method_id,
                "decision": decision,
                "reason_code": reason,
            }
        )
    return result


def compute_fixture_descriptor_sha256(document: dict[str, Any]) -> str:
    normalized = deepcopy(document)
    normalized["descriptor_sha256"] = None
    return sha256_document(normalized)


def _validate_component(value: object, *, context: str, expected_id: str, expected_version: str) -> None:
    component = _object(value, context=context)
    _exact_keys(component, _COMPONENT_FIELDS, context=context)
    if component["id"] != expected_id or component["version"] != expected_version:
        raise _error(context, "identifier or version is unsupported")


def _validate_paths(value: object) -> None:
    paths = _object(value, context="fixture descriptor.paths")
    _exact_keys(paths, _PATH_FIELDS, context="fixture descriptor.paths")
    expected = _paths()
    for category in ("code", "tests", "documentation"):
        actual = _string_list(
            paths[category],
            context=f"fixture descriptor.paths.{category}",
            allow_empty=False,
        )
        if actual != expected[category]:
            raise _error(
                f"fixture descriptor.paths.{category}",
                "does not match the supported template",
            )


def _validate_expected_states(value: object, *, family_id: str, observer: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) != len(STATE_ORDER):
        raise _error(
            "fixture descriptor.expected_states",
            "must contain exactly four ordered states",
        )
    normalized: list[dict[str, Any]] = []
    for index, state_name in enumerate(STATE_ORDER):
        context = f"fixture descriptor.expected_states[{state_name}]"
        state = _object(value[index], context=context)
        _exact_keys(state, _STATE_FIELDS, context=context)
        if state["state"] != state_name:
            raise _error(context, f"state must be {state_name!r}")
        _boolean(state["applicable"], context=f"{context}.applicable")
        _string(state["expected_observed"], context=f"{context}.expected_observed")
        _string(state["failure_cause"], context=f"{context}.failure_cause")
        normalized.append(state)
    expected = _expected_states(family_id, observer)
    if normalized != expected:
        raise _error(
            "fixture descriptor.expected_states",
            "is inconsistent with family and observer semantics",
        )
    return normalized


def _validate_expected_methods(value: object, *, states: Sequence[Mapping[str, object]]) -> None:
    if not isinstance(value, list) or len(value) != len(METHOD_STATE_SETS):
        raise _error(
            "fixture descriptor.expected_methods",
            "must contain exactly four ordered methods",
        )
    expected = _expected_methods(states)
    normalized: list[dict[str, str]] = []
    for index, (method_id, _) in enumerate(METHOD_STATE_SETS):
        context = f"fixture descriptor.expected_methods[{method_id}]"
        method = _object(value[index], context=context)
        _exact_keys(method, _METHOD_FIELDS, context=context)
        normalized.append(
            {
                "method_id": _string(method["method_id"], context=f"{context}.method_id"),
                "decision": _string(method["decision"], context=f"{context}.decision"),
                "reason_code": _string(method["reason_code"], context=f"{context}.reason_code"),
            }
        )
    if normalized != expected:
        raise _error(
            "fixture descriptor.expected_methods",
            "method decision is inconsistent with expected state semantics",
        )


def _validate_descriptor(document: object, *, verify_digest: bool) -> dict[str, Any]:
    descriptor = _object(document, context="fixture descriptor")
    _exact_keys(descriptor, _DESCRIPTOR_FIELDS, context="fixture descriptor")
    if descriptor["schema_version"] != FIXTURE_DESCRIPTOR_SCHEMA_VERSION:
        raise _error("fixture descriptor.schema_version", "is unsupported")
    if descriptor["study_id"] != STUDY_ID:
        raise _error("fixture descriptor.study_id", "must be 'DW-001'")
    _scenario_id(descriptor["scenario_id"])
    family_id = _string(descriptor["family_id"], context="fixture descriptor.family_id")
    if family_id not in _FAMILY_DEFINITIONS:
        raise _error("fixture descriptor.family_id", "family is unsupported")
    definition = _FAMILY_DEFINITIONS[family_id]
    if descriptor["control_role"] != definition["control_role"]:
        raise _error("fixture descriptor.control_role", "is inconsistent with family")
    _validate_component(
        descriptor["generator"],
        context="fixture descriptor.generator",
        expected_id=GENERATOR_ID,
        expected_version=GENERATOR_VERSION,
    )
    _validate_component(
        descriptor["template"],
        context="fixture descriptor.template",
        expected_id=TEMPLATE_ID,
        expected_version=TEMPLATE_VERSION,
    )
    observer = _string(descriptor["observer"], context="fixture descriptor.observer")
    if observer not in OBSERVER_IDENTIFIERS:
        raise _error("fixture descriptor.observer", "is unsupported")
    if descriptor["observer_id"] != OBSERVER_IDENTIFIERS[observer]:
        raise _error("fixture descriptor.observer_id", "is inconsistent with observer")
    command = _string_list(
        descriptor["command"],
        context="fixture descriptor.command",
        allow_empty=False,
    )
    if command != _observer_command(observer):
        raise _error("fixture descriptor.command", "is inconsistent with observer")
    if _integer(
        descriptor["timeout_seconds"],
        context="fixture descriptor.timeout_seconds",
        minimum=1,
        maximum=86_400,
    ) != 30:
        raise _error("fixture descriptor.timeout_seconds", "must be 30 for template v1")
    _validate_paths(descriptor["paths"])
    states = _validate_expected_states(
        descriptor["expected_states"],
        family_id=family_id,
        observer=observer,
    )
    _validate_expected_methods(descriptor["expected_methods"], states=states)
    recorded = _hex(
        descriptor["descriptor_sha256"],
        context="fixture descriptor.descriptor_sha256",
        lengths=(64,),
    )
    if verify_digest:
        computed = compute_fixture_descriptor_sha256(descriptor)
        if recorded != computed:
            raise _error(
                "fixture descriptor.descriptor_sha256",
                f"digest mismatch: expected {recorded}, computed {computed}",
            )
    return descriptor


def build_fixture_descriptor(
    *,
    scenario_id: str,
    family_id: str,
    observer: str = "outcome-receipt-v1",
) -> dict[str, Any]:
    normalized_scenario_id = _scenario_id(scenario_id)
    if family_id not in _FAMILY_DEFINITIONS:
        raise _error("fixture descriptor.family_id", "family is unsupported")
    if observer not in OBSERVER_IDENTIFIERS:
        raise _error("fixture descriptor.observer", "is unsupported")
    states = _expected_states(family_id, observer)
    descriptor: dict[str, Any] = {
        "schema_version": FIXTURE_DESCRIPTOR_SCHEMA_VERSION,
        "study_id": STUDY_ID,
        "scenario_id": normalized_scenario_id,
        "family_id": family_id,
        "control_role": _FAMILY_DEFINITIONS[family_id]["control_role"],
        "generator": {"id": GENERATOR_ID, "version": GENERATOR_VERSION},
        "template": {"id": TEMPLATE_ID, "version": TEMPLATE_VERSION},
        "observer": observer,
        "observer_id": OBSERVER_IDENTIFIERS[observer],
        "command": _observer_command(observer),
        "timeout_seconds": 30,
        "paths": _paths(),
        "expected_states": states,
        "expected_methods": _expected_methods(states),
        "descriptor_sha256": None,
    }
    descriptor["descriptor_sha256"] = compute_fixture_descriptor_sha256(descriptor)
    _validate_descriptor(descriptor, verify_digest=True)
    return descriptor


def verify_fixture_descriptor_document(document: object) -> tuple[bool, tuple[str, ...]]:
    try:
        _validate_descriptor(document, verify_digest=True)
    except DW001ScenarioError as exc:
        return False, (str(exc),)
    return True, ()


def _specification_bytes(descriptor: Mapping[str, object]) -> bytes:
    command = descriptor["command"]
    assert isinstance(command, list)
    command_items = ", ".join(f'"{item}"' for item in command)
    observer_line = f'observer = "{descriptor["observer"]}"\n'
    text = (
        "[paths]\n"
        "code = [\"src/**\"]\n"
        "tests = [\"tests/**\"]\n"
        "documentation = [\"deltawitness.toml\"]\n\n"
        "[execution]\n"
        "pass_env = []\n\n"
        "[[claim]]\n"
        "id = \"role-check-regression\"\n"
        "description = \"A viewer must not be treated as an administrator.\"\n"
        f"{observer_line}"
        f"command = [{command_items}]\n"
        "timeout_seconds = 30\n"
        "pass_exit_codes = [0]\n"
        "fail_exit_codes = [1]\n\n"
        "[claim.expect]\n"
        "base_base = \"pass\"\n"
        "base_candidate = \"fail\"\n"
        "candidate_base = \"pass\"\n"
        "candidate_candidate = \"pass\"\n"
    )
    return text.encode("utf-8")


def _git_environment(home: Path, *, timestamp: str | None = None) -> dict[str, str]:
    allowed = {
        key: value
        for key, value in os.environ.items()
        if key in {"PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT"}
    }
    allowed.update(
        {
            "HOME": str(home),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_LFS_SKIP_SMUDGE": "1",
            "LC_ALL": "C",
            "LANG": "C",
        }
    )
    if timestamp is not None:
        allowed.update(
            {
                "GIT_AUTHOR_NAME": "DeltaWitness Synthetic Generator",
                "GIT_AUTHOR_EMAIL": "generator@deltawitness.invalid",
                "GIT_AUTHOR_DATE": timestamp,
                "GIT_COMMITTER_NAME": "DeltaWitness Synthetic Generator",
                "GIT_COMMITTER_EMAIL": "generator@deltawitness.invalid",
                "GIT_COMMITTER_DATE": timestamp,
            }
        )
    return allowed


def _run_git(
    repo: Path,
    home: Path,
    *args: str,
    timestamp: str | None = None,
) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        env=_git_environment(home, timestamp=timestamp),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise _error("synthetic fixture Git operation", f"git {args[0]!r} failed")
    return completed.stdout.strip()


def _write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def compute_fixture_identity_sha256(document: dict[str, Any]) -> str:
    normalized = deepcopy(document)
    normalized["identity_sha256"] = None
    return sha256_document(normalized)


def _validate_identity(identity: object, descriptor: object, *, verify_digest: bool) -> dict[str, Any]:
    normalized_descriptor = _validate_descriptor(descriptor, verify_digest=True)
    document = _object(identity, context="fixture identity")
    _exact_keys(document, _IDENTITY_FIELDS, context="fixture identity")
    if document["schema_version"] != FIXTURE_IDENTITY_SCHEMA_VERSION:
        raise _error("fixture identity.schema_version", "is unsupported")
    for key in (
        "study_id",
        "scenario_id",
        "family_id",
        "control_role",
        "descriptor_sha256",
        "generator",
        "template",
        "observer",
        "observer_id",
        "paths",
        "expected_states",
        "expected_methods",
    ):
        if document[key] != normalized_descriptor[key]:
            raise _error(f"fixture identity.{key}", "does not match descriptor")
    git = _object(document["git"], context="fixture identity.git")
    _exact_keys(git, _GIT_FIELDS, context="fixture identity.git")
    if git["object_format"] != "sha1":
        raise _error("fixture identity.git.object_format", "must be 'sha1'")
    for field in (
        "base_commit_sha",
        "base_tree_sha",
        "head_commit_sha",
        "head_tree_sha",
    ):
        _hex(git[field], context=f"fixture identity.git.{field}", lengths=(40,))
    if git["base_commit_sha"] == git["head_commit_sha"]:
        raise _error("fixture identity.git", "base and head commits must differ")
    specification = _object(
        document["specification"],
        context="fixture identity.specification",
    )
    _exact_keys(
        specification,
        _SPECIFICATION_FIELDS,
        context="fixture identity.specification",
    )
    if specification["path"] != "deltawitness.toml":
        raise _error("fixture identity.specification.path", "is unsupported")
    _hex(
        specification["sha256"],
        context="fixture identity.specification.sha256",
        lengths=(64,),
    )
    recorded = _hex(
        document["identity_sha256"],
        context="fixture identity.identity_sha256",
        lengths=(64,),
    )
    if verify_digest:
        computed = compute_fixture_identity_sha256(document)
        if recorded != computed:
            raise _error(
                "fixture identity.identity_sha256",
                f"digest mismatch: expected {recorded}, computed {computed}",
            )
    return document


def verify_fixture_identity_document(
    identity: object,
    descriptor: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        _validate_identity(identity, descriptor, verify_digest=True)
    except DW001ScenarioError as exc:
        return False, (str(exc),)
    return True, ()


def materialize_synthetic_fixture(
    document: object,
    destination: Path,
) -> dict[str, Any]:
    descriptor = _validate_descriptor(document, verify_digest=True)
    repo = Path(destination)
    if repo.exists():
        if not repo.is_dir():
            raise _error("synthetic fixture destination", "must be an empty directory")
        if any(repo.iterdir()):
            raise _error("synthetic fixture destination", "must be empty")
    else:
        try:
            repo.mkdir()
        except OSError as exc:
            raise _error("synthetic fixture destination", "cannot be created") from exc

    family_id = str(descriptor["family_id"])
    definition = _FAMILY_DEFINITIONS[family_id]
    candidate_code = definition["candidate_code"]
    candidate_tests = definition["candidate_tests"]
    assert isinstance(candidate_code, str)
    assert isinstance(candidate_tests, str)
    spec_bytes = _specification_bytes(descriptor)

    with tempfile.TemporaryDirectory(prefix="deltawitness-dw001-git-home-") as home_dir:
        home = Path(home_dir)
        _run_git(repo, home, "init", "--object-format=sha1", "-b", "main", ".")
        _run_git(repo, home, "config", "core.autocrlf", "false")
        _run_git(repo, home, "config", "core.filemode", "false")
        _run_git(repo, home, "config", "commit.gpgsign", "false")

        _write_bytes(repo / "src" / "access.py", _BASE_CODE.encode("utf-8"))
        _write_bytes(repo / "tests" / "test_access.py", _BASE_TESTS.encode("utf-8"))
        _write_bytes(repo / "deltawitness.toml", spec_bytes)
        _run_git(
            repo,
            home,
            "add",
            "--",
            "deltawitness.toml",
            "src/access.py",
            "tests/test_access.py",
        )
        _run_git(
            repo,
            home,
            "commit",
            "--no-verify",
            "--no-gpg-sign",
            "-m",
            f"DW-001 synthetic base: {descriptor['scenario_id']}",
            timestamp="2001-01-01T00:00:00+00:00",
        )
        base_commit = _run_git(repo, home, "rev-parse", "HEAD")
        base_tree = _run_git(repo, home, "rev-parse", "HEAD^{tree}")

        _write_bytes(repo / "src" / "access.py", candidate_code.encode("utf-8"))
        _write_bytes(repo / "tests" / "test_access.py", candidate_tests.encode("utf-8"))
        _run_git(repo, home, "add", "--", "src/access.py", "tests/test_access.py")
        _run_git(
            repo,
            home,
            "commit",
            "--no-verify",
            "--no-gpg-sign",
            "-m",
            f"DW-001 synthetic candidate: {descriptor['scenario_id']}:{family_id}",
            timestamp="2001-01-01T00:00:01+00:00",
        )
        head_commit = _run_git(repo, home, "rev-parse", "HEAD")
        head_tree = _run_git(repo, home, "rev-parse", "HEAD^{tree}")
        if _run_git(repo, home, "status", "--porcelain=v1"):
            raise _error("synthetic fixture repository", "is not clean after generation")

    identity: dict[str, Any] = {
        "schema_version": FIXTURE_IDENTITY_SCHEMA_VERSION,
        "study_id": descriptor["study_id"],
        "scenario_id": descriptor["scenario_id"],
        "family_id": descriptor["family_id"],
        "control_role": descriptor["control_role"],
        "descriptor_sha256": descriptor["descriptor_sha256"],
        "generator": deepcopy(descriptor["generator"]),
        "template": deepcopy(descriptor["template"]),
        "observer": descriptor["observer"],
        "observer_id": descriptor["observer_id"],
        "git": {
            "object_format": "sha1",
            "base_commit_sha": base_commit,
            "base_tree_sha": base_tree,
            "head_commit_sha": head_commit,
            "head_tree_sha": head_tree,
        },
        "specification": {
            "path": "deltawitness.toml",
            "sha256": hashlib.sha256(spec_bytes).hexdigest(),
        },
        "paths": deepcopy(descriptor["paths"]),
        "expected_states": deepcopy(descriptor["expected_states"]),
        "expected_methods": deepcopy(descriptor["expected_methods"]),
        "identity_sha256": None,
    }
    identity["identity_sha256"] = compute_fixture_identity_sha256(identity)
    _validate_identity(identity, descriptor, verify_digest=True)
    return identity


def verify_materialized_fixture(
    identity: object,
    descriptor: object,
    destination: Path,
) -> tuple[bool, tuple[str, ...]]:
    valid, errors = verify_fixture_identity_document(identity, descriptor)
    if not valid:
        return False, errors
    assert isinstance(identity, dict)
    repo = Path(destination)
    if not repo.is_dir():
        return False, ("synthetic fixture destination is not a directory",)
    try:
        with tempfile.TemporaryDirectory(prefix="deltawitness-dw001-verify-home-") as home_dir:
            home = Path(home_dir)
            head = _run_git(repo, home, "rev-parse", "HEAD")
            status = _run_git(repo, home, "status", "--porcelain=v1")
            base_commit = str(identity["git"]["base_commit_sha"])
            base_tree = _run_git(repo, home, "rev-parse", f"{base_commit}^{{tree}}")
            head_tree = _run_git(repo, home, "rev-parse", "HEAD^{tree}")
            _run_git(repo, home, "merge-base", "--is-ancestor", base_commit, head)
    except DW001ScenarioError as exc:
        return False, (str(exc),)

    verification_errors: list[str] = []
    if status:
        verification_errors.append("synthetic fixture repository is not clean")
    if head != identity["git"]["head_commit_sha"]:
        verification_errors.append("recorded head commit does not match repository")
    if base_tree != identity["git"]["base_tree_sha"]:
        verification_errors.append("recorded base tree does not match repository")
    if head_tree != identity["git"]["head_tree_sha"]:
        verification_errors.append("recorded head tree does not match repository")
    spec_path = repo / str(identity["specification"]["path"])
    try:
        spec_digest = hashlib.sha256(spec_path.read_bytes()).hexdigest()
    except OSError:
        verification_errors.append("recorded specification cannot be read")
    else:
        if spec_digest != identity["specification"]["sha256"]:
            verification_errors.append("recorded specification digest does not match repository")
    return not verification_errors, tuple(verification_errors)


__all__ = [
    "DW001ScenarioError",
    "FIXTURE_DESCRIPTOR_SCHEMA_VERSION",
    "FIXTURE_IDENTITY_SCHEMA_VERSION",
    "GENERATOR_ID",
    "GENERATOR_VERSION",
    "SUPPORTED_FAMILIES",
    "build_fixture_descriptor",
    "compute_fixture_descriptor_sha256",
    "compute_fixture_identity_sha256",
    "materialize_synthetic_fixture",
    "verify_fixture_descriptor_document",
    "verify_fixture_identity_document",
    "verify_materialized_fixture",
]
