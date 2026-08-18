"""Red-first scaffold for the DW-001 claim-relevant path experiment.

The exact source, tests, selectors, route axes, influence control, fault
population, expected outcome matrix, and policy boundary have been designed but
are intentionally not implemented in this commit.  The retained failing test
must reach this explicit boundary; import, syntax, dependency, or unrelated
failures do not qualify as preregistration red-first evidence.
"""

from __future__ import annotations

from typing import Any

from .errors import DeltaWitnessError


PLAN_SCHEMA_VERSION = (
    "deltawitness.dw001-claim-relevant-path-divergence-plan.v1"
)
CATALOG_SCHEMA_VERSION = (
    "deltawitness.dw001-claim-relevant-path-divergence-catalog.v1"
)
PRIOR_ART_SCHEMA_VERSION = (
    "deltawitness.dw001-claim-relevant-path-prior-art-log.v1"
)
PLAN_ID = "DW-001-CLAIM-RELEVANT-PATH-DIVERGENCE-PLAN-V1"
SOURCE_SHA256 = (
    "8c1bdd26c2e98cd209f210630bfe4d274a3dcd7bbd042db8b8586c7750814327"
)
SOURCE_AST_SHA256 = (
    "dabb7011748968f8d43d590ff843a91697a3344a2400d7cabaf926b79ca88e2d"
)
TEST_SHA256 = (
    "8a26d52fa7fbb4ab7fc6eab466d9051cd329b0da09a667b5e220fbbfd416d1e9"
)
INFLUENCE_CONTROL_SHA256 = (
    "7b068d2f71003fade4eca77e1aa9cdb3a0f2f526f89dbd4828d4f17fbf2bd4f5"
)
PLAN_SHA256 = (
    "ff0403132c3424fc7309a15a05794eed93ac9eb526de172e17326f8409ca0888"
)
CATALOG_SHA256 = (
    "f36fbe58c00cfb8ed0fd994f3bb1dcdb45040774f7ae4663563b9f40ac15daa5"
)
PRIOR_ART_LOG_SHA256 = (
    "5f697631a5ded7a413dd11f4da0606ee8809e2b0f5de257ecab53a7e2d7f790c"
)


class DW001ClaimRelevantPathPlanError(DeltaWitnessError):
    """Raised when the frozen preregistration contract is unavailable."""


def _not_implemented() -> DW001ClaimRelevantPathPlanError:
    return DW001ClaimRelevantPathPlanError(
        "claim-relevant path preregistration is intentionally not implemented"
    )


def build_claim_relevant_path_plan() -> dict[str, Any]:
    """Build the exact design-only preregistration."""

    raise _not_implemented()


def build_claim_relevant_path_catalog(
    plan: object,
) -> dict[str, Any]:
    """Build exact source and fault identities without executing them."""

    raise _not_implemented()


def build_claim_relevant_path_prior_art_log(
    plan: object,
    catalog: object,
) -> dict[str, Any]:
    """Build the exact pre-execution direct-baseline boundary."""

    raise _not_implemented()


def verify_claim_relevant_path_plan_document(
    document: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify the exact preregistration through semantic reconstruction."""

    raise _not_implemented()


def verify_claim_relevant_path_catalog_document(
    document: object,
    plan: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify the exact generation-only fault catalog."""

    raise _not_implemented()


def verify_claim_relevant_path_prior_art_log_document(
    document: object,
    plan: object,
    catalog: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify the exact prior-art and claim boundary."""

    raise _not_implemented()


__all__ = [
    "CATALOG_SCHEMA_VERSION",
    "CATALOG_SHA256",
    "DW001ClaimRelevantPathPlanError",
    "INFLUENCE_CONTROL_SHA256",
    "PLAN_ID",
    "PLAN_SCHEMA_VERSION",
    "PLAN_SHA256",
    "PRIOR_ART_LOG_SHA256",
    "PRIOR_ART_SCHEMA_VERSION",
    "SOURCE_AST_SHA256",
    "SOURCE_SHA256",
    "TEST_SHA256",
    "build_claim_relevant_path_catalog",
    "build_claim_relevant_path_plan",
    "build_claim_relevant_path_prior_art_log",
    "verify_claim_relevant_path_catalog_document",
    "verify_claim_relevant_path_plan_document",
    "verify_claim_relevant_path_prior_art_log_document",
]
