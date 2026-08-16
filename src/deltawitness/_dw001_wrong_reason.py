"""Fixed wrong-reason import-failure fixture for the DW-001 observer contrast.

This module implements one owned-synthetic family whose source and test bytes
are identical across observer arms. The ordinary exit-code observer sees the
base+candidate-test import error only as a configured nonzero failure. The
typed unittest adapter preserves the same execution as a generic test error.

The fixture ground truth identifies the fixed mechanism as an import error,
while receipt v1 deliberately remains at the coarser ``test_error`` runtime
class. No raw traceback is placed in public fixture artifacts.
"""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
import hashlib
from pathlib import Path
import tempfile
from typing import Any

from . import _dw001_scenarios as _core
from .dw001 import OBSERVER_IDENTIFIERS, STATE_ORDER


FAMILY_ID = "wrong-reason-base-import-failure"
CONTROL_ROLE = "false-assurance-case"

_CANDIDATE_CODE = """def is_admin(user):
    return user.get(\"role\") == \"admin\"


def normalize_role(user):
    return str(user.get(\"role\", \"\")).strip().lower()
"""

_CANDIDATE_TESTS = """import sys
import unittest

sys.path.insert(0, \"src\")
from access import is_admin, normalize_role


class AccessTests(unittest.TestCase):
    def test_admin_is_allowed(self):
        self.assertTrue(is_admin({\"role\": \"admin\"}))

    def test_missing_role_is_denied(self):
        self.assertFalse(is_admin({}))

    def test_viewer_is_denied(self):
        self.assertFalse(is_admin({\"role\": \"viewer\"}))

    def test_role_is_normalized(self):
        self.assertEqual(normalize_role({\"role\": \" Admin \"}), \"admin\")
"""


def expected_states(observer: str) -> list[dict[str, object]]:
    if observer == "exit-code-v1":
        outcomes = ("pass", "fail", "pass", "pass")
        causes = ("none", "test_failure_untyped", "none", "none")
    elif observer == "outcome-receipt-v1":
        outcomes = ("pass", "error", "pass", "pass")
        causes = ("none", "import_error", "none", "none")
    else:
        raise _core._error("fixture descriptor.observer", "is unsupported")
    return [
        {
            "state": state,
            "applicable": True,
            "expected_observed": outcomes[index],
            "failure_cause": causes[index],
        }
        for index, state in enumerate(STATE_ORDER)
    ]


def _expected_methods(states: list[dict[str, object]]) -> list[dict[str, str]]:
    return _core._expected_methods(states)


def _canonical_descriptor(*, scenario_id: str, observer: str) -> dict[str, Any]:
    normalized_scenario_id = _core._scenario_id(scenario_id)
    if observer not in OBSERVER_IDENTIFIERS:
        raise _core._error("fixture descriptor.observer", "is unsupported")
    states = expected_states(observer)
    descriptor: dict[str, Any] = {
        "schema_version": _core.FIXTURE_DESCRIPTOR_SCHEMA_VERSION,
        "study_id": _core.STUDY_ID,
        "scenario_id": normalized_scenario_id,
        "family_id": FAMILY_ID,
        "control_role": CONTROL_ROLE,
        "generator": {"id": _core.GENERATOR_ID, "version": _core.GENERATOR_VERSION},
        "template": {"id": _core.TEMPLATE_ID, "version": _core.TEMPLATE_VERSION},
        "observer": observer,
        "observer_id": OBSERVER_IDENTIFIERS[observer],
        "command": _core._observer_command(observer),
        "timeout_seconds": 30,
        "paths": _core._paths(),
        "expected_states": states,
        "expected_methods": _expected_methods(states),
        "descriptor_sha256": None,
    }
    descriptor["descriptor_sha256"] = _core.compute_fixture_descriptor_sha256(descriptor)
    return descriptor


def build_descriptor(*, scenario_id: str, observer: str) -> dict[str, Any]:
    descriptor = _canonical_descriptor(scenario_id=scenario_id, observer=observer)
    validate_descriptor(descriptor, verify_digest=True)
    return descriptor


def validate_descriptor(document: object, *, verify_digest: bool) -> dict[str, Any]:
    descriptor = _core._object(document, context="fixture descriptor")
    _core._exact_keys(
        descriptor,
        _core._DESCRIPTOR_FIELDS,
        context="fixture descriptor",
    )
    if descriptor["schema_version"] != _core.FIXTURE_DESCRIPTOR_SCHEMA_VERSION:
        raise _core._error("fixture descriptor.schema_version", "is unsupported")
    if descriptor["study_id"] != _core.STUDY_ID:
        raise _core._error("fixture descriptor.study_id", "must be 'DW-001'")
    scenario_id = _core._scenario_id(descriptor["scenario_id"])
    if descriptor["family_id"] != FAMILY_ID:
        raise _core._error("fixture descriptor.family_id", "family is unsupported")
    if descriptor["control_role"] != CONTROL_ROLE:
        raise _core._error(
            "fixture descriptor.control_role",
            "is inconsistent with family",
        )
    _core._validate_component(
        descriptor["generator"],
        context="fixture descriptor.generator",
        expected_id=_core.GENERATOR_ID,
        expected_version=_core.GENERATOR_VERSION,
    )
    _core._validate_component(
        descriptor["template"],
        context="fixture descriptor.template",
        expected_id=_core.TEMPLATE_ID,
        expected_version=_core.TEMPLATE_VERSION,
    )
    observer = _core._string(
        descriptor["observer"],
        context="fixture descriptor.observer",
    )
    if observer not in OBSERVER_IDENTIFIERS:
        raise _core._error("fixture descriptor.observer", "is unsupported")
    if descriptor["observer_id"] != OBSERVER_IDENTIFIERS[observer]:
        raise _core._error(
            "fixture descriptor.observer_id",
            "is inconsistent with observer",
        )
    command = _core._string_list(
        descriptor["command"],
        context="fixture descriptor.command",
        allow_empty=False,
    )
    if command != _core._observer_command(observer):
        raise _core._error(
            "fixture descriptor.command",
            "is inconsistent with observer",
        )
    if _core._integer(
        descriptor["timeout_seconds"],
        context="fixture descriptor.timeout_seconds",
        minimum=1,
        maximum=86_400,
    ) != 30:
        raise _core._error(
            "fixture descriptor.timeout_seconds",
            "must be 30 for template v1",
        )
    _core._validate_paths(descriptor["paths"])

    canonical = _canonical_descriptor(scenario_id=scenario_id, observer=observer)
    if descriptor["expected_states"] != canonical["expected_states"]:
        raise _core._error(
            "fixture descriptor.expected_states",
            "is inconsistent with family and observer semantics",
        )
    if descriptor["expected_methods"] != canonical["expected_methods"]:
        raise _core._error(
            "fixture descriptor.expected_methods",
            "method decision is inconsistent with expected state semantics",
        )
    recorded = _core._hex(
        descriptor["descriptor_sha256"],
        context="fixture descriptor.descriptor_sha256",
        lengths=(64,),
    )
    if verify_digest:
        computed = _core.compute_fixture_descriptor_sha256(descriptor)
        if recorded != computed:
            raise _core._error(
                "fixture descriptor.descriptor_sha256",
                f"digest mismatch: expected {recorded}, computed {computed}",
            )
    return descriptor


def verify_descriptor(document: object) -> tuple[bool, tuple[str, ...]]:
    try:
        validate_descriptor(document, verify_digest=True)
    except _core.DW001ScenarioError as exc:
        return False, (str(exc),)
    return True, ()


def _identity(
    descriptor: Mapping[str, object],
    *,
    base_commit: str,
    base_tree: str,
    head_commit: str,
    head_tree: str,
    spec_bytes: bytes,
) -> dict[str, Any]:
    identity: dict[str, Any] = {
        "schema_version": _core.FIXTURE_IDENTITY_SCHEMA_VERSION,
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
    identity["identity_sha256"] = _core.compute_fixture_identity_sha256(identity)
    return identity


def validate_identity(
    identity: object,
    descriptor: object,
    *,
    verify_digest: bool,
) -> dict[str, Any]:
    normalized_descriptor = validate_descriptor(descriptor, verify_digest=True)
    document = _core._object(identity, context="fixture identity")
    _core._exact_keys(
        document,
        _core._IDENTITY_FIELDS,
        context="fixture identity",
    )
    if document["schema_version"] != _core.FIXTURE_IDENTITY_SCHEMA_VERSION:
        raise _core._error("fixture identity.schema_version", "is unsupported")
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
            raise _core._error(
                f"fixture identity.{key}",
                "does not match descriptor",
            )
    git = _core._object(document["git"], context="fixture identity.git")
    _core._exact_keys(git, _core._GIT_FIELDS, context="fixture identity.git")
    if git["object_format"] != "sha1":
        raise _core._error(
            "fixture identity.git.object_format",
            "must be 'sha1'",
        )
    for field in (
        "base_commit_sha",
        "base_tree_sha",
        "head_commit_sha",
        "head_tree_sha",
    ):
        _core._hex(
            git[field],
            context=f"fixture identity.git.{field}",
            lengths=(40,),
        )
    if git["base_commit_sha"] == git["head_commit_sha"]:
        raise _core._error(
            "fixture identity.git",
            "base and head commits must differ",
        )
    specification = _core._object(
        document["specification"],
        context="fixture identity.specification",
    )
    _core._exact_keys(
        specification,
        _core._SPECIFICATION_FIELDS,
        context="fixture identity.specification",
    )
    if specification["path"] != "deltawitness.toml":
        raise _core._error(
            "fixture identity.specification.path",
            "is unsupported",
        )
    expected_spec = hashlib.sha256(
        _core._specification_bytes(normalized_descriptor)
    ).hexdigest()
    if specification["sha256"] != expected_spec:
        raise _core._error(
            "fixture identity.specification.sha256",
            "does not match descriptor-derived specification bytes",
        )
    recorded = _core._hex(
        document["identity_sha256"],
        context="fixture identity.identity_sha256",
        lengths=(64,),
    )
    if verify_digest:
        computed = _core.compute_fixture_identity_sha256(document)
        if recorded != computed:
            raise _core._error(
                "fixture identity.identity_sha256",
                f"digest mismatch: expected {recorded}, computed {computed}",
            )
    return document


def verify_identity(
    identity: object,
    descriptor: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        validate_identity(identity, descriptor, verify_digest=True)
    except _core.DW001ScenarioError as exc:
        return False, (str(exc),)
    return True, ()


def materialize(document: object, destination: Path) -> dict[str, Any]:
    descriptor = validate_descriptor(document, verify_digest=True)
    repo = Path(destination)
    if repo.exists():
        if not repo.is_dir():
            raise _core._error(
                "synthetic fixture destination",
                "must be an empty directory",
            )
        if any(repo.iterdir()):
            raise _core._error("synthetic fixture destination", "must be empty")
    else:
        try:
            repo.mkdir()
        except OSError as exc:
            raise _core._error(
                "synthetic fixture destination",
                "cannot be created",
            ) from exc

    spec_bytes = _core._specification_bytes(descriptor)
    with tempfile.TemporaryDirectory(
        prefix="deltawitness-dw001-git-home-"
    ) as home_dir:
        home = Path(home_dir)
        _core._run_git(repo, home, "init", "--object-format=sha1", "-b", "main", ".")
        _core._run_git(repo, home, "config", "core.autocrlf", "false")
        _core._run_git(repo, home, "config", "core.filemode", "false")
        _core._run_git(repo, home, "config", "commit.gpgsign", "false")

        _core._write_bytes(
            repo / "src" / "access.py",
            _core._BASE_CODE.encode("utf-8"),
        )
        _core._write_bytes(
            repo / "tests" / "test_access.py",
            _core._BASE_TESTS.encode("utf-8"),
        )
        _core._write_bytes(repo / "deltawitness.toml", spec_bytes)
        _core._run_git(
            repo,
            home,
            "add",
            "--",
            "deltawitness.toml",
            "src/access.py",
            "tests/test_access.py",
        )
        _core._run_git(
            repo,
            home,
            "commit",
            "--no-verify",
            "--no-gpg-sign",
            "-m",
            f"DW-001 synthetic base: {descriptor['scenario_id']}",
            timestamp="2001-01-01T00:00:00+00:00",
        )
        base_commit = _core._run_git(repo, home, "rev-parse", "HEAD")
        base_tree = _core._run_git(repo, home, "rev-parse", "HEAD^{tree}")

        _core._write_bytes(
            repo / "src" / "access.py",
            _CANDIDATE_CODE.encode("utf-8"),
        )
        _core._write_bytes(
            repo / "tests" / "test_access.py",
            _CANDIDATE_TESTS.encode("utf-8"),
        )
        _core._run_git(
            repo,
            home,
            "add",
            "--",
            "src/access.py",
            "tests/test_access.py",
        )
        _core._run_git(
            repo,
            home,
            "commit",
            "--no-verify",
            "--no-gpg-sign",
            "-m",
            f"DW-001 synthetic candidate: {descriptor['scenario_id']}:{FAMILY_ID}",
            timestamp="2001-01-01T00:00:01+00:00",
        )
        head_commit = _core._run_git(repo, home, "rev-parse", "HEAD")
        head_tree = _core._run_git(repo, home, "rev-parse", "HEAD^{tree}")
        if _core._run_git(repo, home, "status", "--porcelain=v1"):
            raise _core._error(
                "synthetic fixture repository",
                "is not clean after generation",
            )

    identity = _identity(
        descriptor,
        base_commit=base_commit,
        base_tree=base_tree,
        head_commit=head_commit,
        head_tree=head_tree,
        spec_bytes=spec_bytes,
    )
    validate_identity(identity, descriptor, verify_digest=True)
    return identity


def verify_materialized(
    identity: object,
    descriptor: object,
    destination: Path,
) -> tuple[bool, tuple[str, ...]]:
    valid, errors = verify_identity(identity, descriptor)
    if not valid:
        return False, errors
    assert isinstance(identity, dict)
    repo = Path(destination)
    if not repo.is_dir():
        return False, ("synthetic fixture destination is not a directory",)
    try:
        with tempfile.TemporaryDirectory(
            prefix="deltawitness-dw001-verify-home-"
        ) as home_dir:
            home = Path(home_dir)
            head = _core._run_git(repo, home, "rev-parse", "HEAD")
            status = _core._run_git(repo, home, "status", "--porcelain=v1")
            base_commit = str(identity["git"]["base_commit_sha"])
            base_tree = _core._run_git(
                repo,
                home,
                "rev-parse",
                f"{base_commit}^{{tree}}",
            )
            head_tree = _core._run_git(repo, home, "rev-parse", "HEAD^{tree}")
            _core._run_git(
                repo,
                home,
                "merge-base",
                "--is-ancestor",
                base_commit,
                head,
            )
    except _core.DW001ScenarioError as exc:
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
            verification_errors.append(
                "recorded specification digest does not match repository"
            )
    return not verification_errors, tuple(verification_errors)
