"""Load and validate a DeltaWitness TOML specification."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path, PurePosixPath
import re
import tomllib
from typing import Any

from .errors import ConfigurationError

_ALLOWED_EXPECTATIONS = {"pass", "fail", "any"}
_ALLOWED_OBSERVERS = {"exit-code-v1", "outcome-receipt-v1"}
_STATE_NAMES = ("base_base", "base_candidate", "candidate_base", "candidate_candidate")
_CLAIM_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_ENV_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_MAX_TIMEOUT_SECONDS = 86_400


@dataclass(frozen=True)
class PathPolicy:
    code_globs: tuple[str, ...]
    test_globs: tuple[str, ...]
    documentation_globs: tuple[str, ...]


@dataclass(frozen=True)
class ExecutionPolicy:
    pass_env: tuple[str, ...]


@dataclass(frozen=True)
class Claim:
    claim_id: str
    description: str
    observer: str
    command: tuple[str, ...]
    timeout_seconds: int
    pass_exit_codes: tuple[int, ...]
    fail_exit_codes: tuple[int, ...]
    expectations: dict[str, str]


@dataclass(frozen=True)
class WitnessConfig:
    path: Path
    digest_sha256: str
    path_policy: PathPolicy
    execution_policy: ExecutionPolicy
    claims: tuple[Claim, ...]


def _reject_unknown_keys(table: dict[str, Any], allowed: set[str], context: str) -> None:
    unknown = set(table) - allowed
    if unknown:
        raise ConfigurationError(f"{context}: unknown keys: {sorted(unknown)}")


def _required_table(document: dict[str, Any], name: str) -> dict[str, Any]:
    value = document.get(name)
    if not isinstance(value, dict):
        raise ConfigurationError(f"Missing or invalid [{name}] table")
    return value


def _validate_glob(pattern: str, key: str) -> str:
    if "\x00" in pattern:
        raise ConfigurationError(f"{key!r} contains a NUL byte")
    if "\\" in pattern:
        raise ConfigurationError(f"{key!r} must use Git-style forward slashes: {pattern!r}")
    if pattern.startswith("/"):
        raise ConfigurationError(f"{key!r} must be repository-relative: {pattern!r}")
    if ".." in PurePosixPath(pattern).parts:
        raise ConfigurationError(f"{key!r} must not traverse outside the repository: {pattern!r}")
    return pattern


def _string_list(
    table: dict[str, Any],
    key: str,
    *,
    required: bool,
    validate_globs: bool = False,
) -> tuple[str, ...]:
    value = table.get(key)
    if value is None and not required:
        return ()
    if not isinstance(value, list) or (required and not value):
        requirement = "non-empty " if required else ""
        raise ConfigurationError(f"{key!r} must be a {requirement}list of strings")
    if not all(isinstance(item, str) and item for item in value):
        raise ConfigurationError(f"{key!r} must contain only non-empty strings")

    normalized = tuple(_validate_glob(item, key) if validate_globs else item for item in value)
    if len(normalized) != len(set(normalized)):
        raise ConfigurationError(f"{key!r} contains duplicate entries")
    return normalized


def _load_execution_policy(document: dict[str, Any]) -> ExecutionPolicy:
    raw = document.get("execution", {})
    if not isinstance(raw, dict):
        raise ConfigurationError("[execution] must be a table")
    _reject_unknown_keys(raw, {"pass_env"}, "[execution]")
    pass_env = _string_list(raw, "pass_env", required=False)
    for name in pass_env:
        if not _ENV_NAME.fullmatch(name):
            raise ConfigurationError(f"Invalid environment variable name in execution.pass_env: {name!r}")
    return ExecutionPolicy(pass_env=pass_env)


def load_config(path: Path) -> WitnessConfig:
    path = path.resolve()
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ConfigurationError(f"Cannot read specification: {path}: {exc}") from exc

    try:
        document = tomllib.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise ConfigurationError(f"Invalid TOML in {path}: {exc}") from exc

    if not isinstance(document, dict):
        raise ConfigurationError("The specification root must be a TOML document")
    _reject_unknown_keys(document, {"paths", "execution", "claim"}, "specification")

    paths = _required_table(document, "paths")
    _reject_unknown_keys(paths, {"code", "tests", "documentation"}, "[paths]")
    policy = PathPolicy(
        code_globs=_string_list(paths, "code", required=True, validate_globs=True),
        test_globs=_string_list(paths, "tests", required=True, validate_globs=True),
        documentation_globs=_string_list(paths, "documentation", required=False, validate_globs=True),
    )

    raw_claims = document.get("claim")
    if not isinstance(raw_claims, list) or not raw_claims:
        raise ConfigurationError("At least one [[claim]] table is required")

    claims: list[Claim] = []
    seen_ids: set[str] = set()
    for index, raw_claim in enumerate(raw_claims, start=1):
        if not isinstance(raw_claim, dict):
            raise ConfigurationError(f"claim #{index} must be a table")
        _reject_unknown_keys(
            raw_claim,
            {
                "id",
                "description",
                "observer",
                "command",
                "timeout_seconds",
                "pass_exit_codes",
                "fail_exit_codes",
                "expect",
            },
            f"claim #{index}",
        )

        claim_id = raw_claim.get("id")
        description = raw_claim.get("description", "")
        observer = raw_claim.get("observer", "exit-code-v1")
        command = raw_claim.get("command")
        timeout = raw_claim.get("timeout_seconds", 300)
        pass_exit_codes = raw_claim.get("pass_exit_codes", [0])
        fail_exit_codes = raw_claim.get("fail_exit_codes", [1])
        expectations = raw_claim.get("expect")

        if not isinstance(claim_id, str) or not _CLAIM_ID.fullmatch(claim_id):
            raise ConfigurationError(
                f"claim #{index} id must match {_CLAIM_ID.pattern!r}; received {claim_id!r}"
            )
        if claim_id in seen_ids:
            raise ConfigurationError(f"Duplicate claim id: {claim_id}")
        seen_ids.add(claim_id)

        if not isinstance(description, str):
            raise ConfigurationError(f"claim {claim_id!r}: description must be a string")
        if not isinstance(observer, str) or observer not in _ALLOWED_OBSERVERS:
            raise ConfigurationError(
                f"claim {claim_id!r}: observer must be one of {sorted(_ALLOWED_OBSERVERS)}"
            )
        if not isinstance(command, list) or not command:
            raise ConfigurationError(f"claim {claim_id!r}: command must be a non-empty string array")
        if not all(isinstance(item, str) and item and "\x00" not in item for item in command):
            raise ConfigurationError(
                f"claim {claim_id!r}: command must contain only non-empty strings without NUL bytes"
            )
        if not isinstance(timeout, int) or isinstance(timeout, bool) or not 0 < timeout <= _MAX_TIMEOUT_SECONDS:
            raise ConfigurationError(
                f"claim {claim_id!r}: timeout_seconds must be between 1 and {_MAX_TIMEOUT_SECONDS}"
            )

        def validate_exit_codes(value: object, field: str) -> tuple[int, ...]:
            if not isinstance(value, list) or not value:
                raise ConfigurationError(
                    f"claim {claim_id!r}: {field} must be a non-empty integer array"
                )
            if not all(
                isinstance(item, int)
                and not isinstance(item, bool)
                and -255 <= item <= 255
                for item in value
            ):
                raise ConfigurationError(
                    f"claim {claim_id!r}: {field} must contain integers between -255 and 255"
                )
            normalized_codes = tuple(value)
            if len(normalized_codes) != len(set(normalized_codes)):
                raise ConfigurationError(f"claim {claim_id!r}: {field} contains duplicates")
            return normalized_codes

        normalized_pass_codes = validate_exit_codes(pass_exit_codes, "pass_exit_codes")
        normalized_fail_codes = validate_exit_codes(fail_exit_codes, "fail_exit_codes")
        overlap = set(normalized_pass_codes) & set(normalized_fail_codes)
        if overlap:
            raise ConfigurationError(
                f"claim {claim_id!r}: pass_exit_codes and fail_exit_codes overlap: {sorted(overlap)}"
            )

        if not isinstance(expectations, dict):
            raise ConfigurationError(f"claim {claim_id!r}: [claim.expect] is required")

        unknown_states = set(expectations) - set(_STATE_NAMES)
        missing_states = set(_STATE_NAMES) - set(expectations)
        if unknown_states:
            raise ConfigurationError(
                f"claim {claim_id!r}: unknown expectation states: {sorted(unknown_states)}"
            )
        if missing_states:
            raise ConfigurationError(
                f"claim {claim_id!r}: every state must be explicit; missing {sorted(missing_states)}"
            )

        normalized: dict[str, str] = {}
        for state in _STATE_NAMES:
            value = expectations[state]
            if value not in _ALLOWED_EXPECTATIONS:
                raise ConfigurationError(
                    f"claim {claim_id!r}: expectation for {state!r} must be one of "
                    f"{sorted(_ALLOWED_EXPECTATIONS)}"
                )
            normalized[state] = value

        claims.append(
            Claim(
                claim_id=claim_id,
                description=description,
                observer=observer,
                command=tuple(command),
                timeout_seconds=timeout,
                pass_exit_codes=normalized_pass_codes,
                fail_exit_codes=normalized_fail_codes,
                expectations=normalized,
            )
        )

    return WitnessConfig(
        path=path,
        digest_sha256=hashlib.sha256(raw).hexdigest(),
        path_policy=policy,
        execution_policy=_load_execution_policy(document),
        claims=tuple(claims),
    )
