"""Public contract for the DW-001 weak-proxy-oracle challenge.

The challenge will bind one verified owned-synthetic four-state witness and one
verified declared-selector localization to fixed candidate, mutant, and hidden
claim-control executions. This initial revision intentionally exposes an
unimplemented fail-closed boundary so red-first integration evidence can be
preserved before the family and challenge semantics exist.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .errors import DeltaWitnessError
from .reporting import sha256_document


CHALLENGE_SCHEMA_VERSION = "deltawitness.dw001-weak-oracle-challenge.v1"
CHALLENGE_ID = "weak-proxy-oracle-v1"
FAMILY_ID = "weak-proxy-oracle"
MUTANT_ID = "nonempty-role-boolean-v1"
DECLARED_SELECTOR = "test_access.AccessTests.test_viewer_result_is_boolean"
HIDDEN_CLAIM_SELECTOR = "test_hidden_claim.HiddenClaimTests.test_viewer_is_denied"


class DW001OracleChallengeError(DeltaWitnessError):
    """Raised when weak-oracle challenge evidence is unsafe or inconsistent."""


def compute_weak_oracle_challenge_sha256(document: dict[str, Any]) -> str:
    """Hash canonical challenge bytes with both digest fields normalized."""

    if not isinstance(document, dict):
        raise DW001OracleChallengeError("weak oracle challenge must be an object")
    normalized = deepcopy(document)
    normalized["challenge_sha256"] = None
    normalized["report_sha256"] = None
    return sha256_document(normalized)


def compute_weak_oracle_report_sha256(document: dict[str, Any]) -> str:
    """Hash the complete artifact with only the full-report digest normalized."""

    if not isinstance(document, dict):
        raise DW001OracleChallengeError("weak oracle challenge must be an object")
    normalized = deepcopy(document)
    normalized["report_sha256"] = None
    return sha256_document(normalized)


def _unimplemented() -> DW001OracleChallengeError:
    return DW001OracleChallengeError(
        "DW-001 weak-proxy-oracle challenge is not implemented"
    )


def run_weak_proxy_oracle_challenge(
    descriptor: object,
    identity: object,
    source_report: object,
    projection: object,
    declaration: object,
    localization: object,
) -> dict[str, Any]:
    """Execute the fixed challenge after all source relations are implemented."""

    raise _unimplemented()


def verify_weak_oracle_challenge_document(
    document: object,
    descriptor: object,
    identity: object,
    source_report: object,
    projection: object,
    declaration: object,
    localization: object,
) -> tuple[bool, tuple[str, ...]]:
    """Fail closed until the full semantic verifier is implemented."""

    return False, (str(_unimplemented()),)


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
