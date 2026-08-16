"""Pre-execution Gate 1 mutation-plan boundary.

The completed implementation will freeze a minimal stdlib-AST operator set,
paired strong/weak selector profiles, and deterministic mutant identities before
any mutation outcome is observed. This red-first stub deliberately fails closed.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .errors import DeltaWitnessError
from .reporting import sha256_document


PLAN_SCHEMA_VERSION = "deltawitness.dw001-claim-scoped-mutation-plan.v1"
CATALOG_SCHEMA_VERSION = "deltawitness.dw001-claim-scoped-mutant-catalog.v1"
PLAN_ID = "DW-001-CLAIM-SCOPED-MUTATION-PLAN-V1"
OPERATOR_SET_ID = "python-boolean-predicate-minimal-v1"
ADAPTER_ID = "python-stdlib-ast-return-v1"


class DW001MutationPlanError(DeltaWitnessError):
    """Raised when the mutation plan or catalog is unsafe or inconsistent."""


def compute_mutation_plan_sha256(document: dict[str, Any]) -> str:
    normalized = deepcopy(document)
    normalized["plan_sha256"] = None
    return sha256_document(normalized)


def compute_mutant_catalog_sha256(document: dict[str, Any]) -> str:
    normalized = deepcopy(document)
    normalized["catalog_sha256"] = None
    return sha256_document(normalized)


def _unimplemented() -> DW001MutationPlanError:
    return DW001MutationPlanError(
        "claim-scoped mutation plan and mutant catalog are not implemented"
    )


def build_claim_scoped_mutation_plan() -> dict[str, Any]:
    raise _unimplemented()


def verify_claim_scoped_mutation_plan_document(
    document: object,
) -> tuple[bool, tuple[str, ...]]:
    return False, (str(_unimplemented()),)


def build_claim_scoped_mutant_catalog(
    plan: object,
) -> dict[str, Any]:
    raise _unimplemented()


def verify_claim_scoped_mutant_catalog_document(
    document: object,
    plan: object,
) -> tuple[bool, tuple[str, ...]]:
    return False, (str(_unimplemented()),)


__all__ = [
    "ADAPTER_ID",
    "CATALOG_SCHEMA_VERSION",
    "DW001MutationPlanError",
    "OPERATOR_SET_ID",
    "PLAN_ID",
    "PLAN_SCHEMA_VERSION",
    "build_claim_scoped_mutant_catalog",
    "build_claim_scoped_mutation_plan",
    "compute_mutant_catalog_sha256",
    "compute_mutation_plan_sha256",
    "verify_claim_scoped_mutant_catalog_document",
    "verify_claim_scoped_mutation_plan_document",
]
