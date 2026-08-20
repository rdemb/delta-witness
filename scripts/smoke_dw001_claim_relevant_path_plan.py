#!/usr/bin/env python3
"""Rebuild and verify the design-only DW-001 claim-path preregistration."""

from __future__ import annotations

from pathlib import Path
import sys

from deltawitness.dw001_claim_relevant_path_plan import (
    CATALOG_SHA256,
    INFLUENCE_CONTROL_SHA256,
    PLAN_SHA256,
    PRIOR_ART_LOG_SHA256,
    SOURCE_AST_SHA256,
    SOURCE_SHA256,
    TEST_SHA256,
    build_claim_relevant_path_catalog,
    build_claim_relevant_path_plan,
    build_claim_relevant_path_prior_art_log,
    load_claim_relevant_path_catalog,
    load_claim_relevant_path_plan,
    load_claim_relevant_path_prior_art_log,
)

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research" / "DW-001"


def main() -> int:
    if "coverage" in sys.modules:
        raise AssertionError("Coverage.py was imported before preregistration smoke")

    committed_plan = load_claim_relevant_path_plan(
        RESEARCH / "claim-relevant-path-divergence-plan.v1.json"
    )
    committed_catalog = load_claim_relevant_path_catalog(
        RESEARCH / "claim-relevant-path-divergence-catalog.v1.json",
        committed_plan,
    )
    committed_prior = load_claim_relevant_path_prior_art_log(
        RESEARCH / "claim-relevant-path-prior-art-log.v1.json",
        committed_plan,
        committed_catalog,
    )

    rebuilt_plan = build_claim_relevant_path_plan()
    rebuilt_catalog = build_claim_relevant_path_catalog(rebuilt_plan)
    rebuilt_prior = build_claim_relevant_path_prior_art_log(
        rebuilt_plan,
        rebuilt_catalog,
    )
    if (
        committed_plan != rebuilt_plan
        or committed_catalog != rebuilt_catalog
        or committed_prior != rebuilt_prior
    ):
        raise AssertionError("committed preregistration artifacts changed")
    if committed_plan["execution_authorized"] is not False:
        raise AssertionError("candidate execution was authorized")
    if committed_plan["future_execution_contract"]["execution_status"] != "not_implemented":
        raise AssertionError("execution status changed")
    if "coverage" in sys.modules:
        raise AssertionError("preregistration smoke imported Coverage.py")

    print(
        "DW-001 claim-path preregistration smoke passed: "
        f"source_sha256={SOURCE_SHA256} "
        f"source_ast_sha256={SOURCE_AST_SHA256} "
        f"test_sha256={TEST_SHA256} "
        f"influence_sha256={INFLUENCE_CONTROL_SHA256} "
        f"plan_sha256={PLAN_SHA256} "
        f"catalog_sha256={CATALOG_SHA256} "
        f"prior_art_sha256={PRIOR_ART_LOG_SHA256} "
        "execution=not_implemented novelty=not_established"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
