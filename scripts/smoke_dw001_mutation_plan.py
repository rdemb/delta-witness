#!/usr/bin/env python3
"""Exercise the packaged DW-001 mutation-plan and catalog contracts.

The smoke parses, transforms, and compiles only fixed project-owned source
bytes. It does not execute mutants, tests, external repositories, a mutation
engine, or a holdout, and it does not produce a mutation score.
"""

from __future__ import annotations

from pathlib import Path

from deltawitness.dw001_mutation_plan import (
    build_claim_scoped_mutant_catalog,
    build_claim_scoped_mutation_plan,
    verify_claim_scoped_mutant_catalog_document,
    verify_claim_scoped_mutation_plan_document,
)
from deltawitness.reporting import load_report


_ROOT = Path(__file__).resolve().parents[1]
_PLAN_PATH = (
    _ROOT / "research" / "DW-001" / "claim-scoped-mutation-plan.v1.json"
)
_CATALOG_PATH = (
    _ROOT / "research" / "DW-001" / "claim-scoped-mutant-catalog.v1.json"
)


def main() -> int:
    committed_plan = load_report(_PLAN_PATH)
    plan_valid, plan_errors = verify_claim_scoped_mutation_plan_document(
        committed_plan
    )
    if not plan_valid:
        raise AssertionError(plan_errors)
    generated_plan = build_claim_scoped_mutation_plan()
    if generated_plan != committed_plan:
        raise AssertionError("committed mutation plan differs from canonical builder")

    committed_catalog = load_report(_CATALOG_PATH)
    catalog_valid, catalog_errors = verify_claim_scoped_mutant_catalog_document(
        committed_catalog,
        committed_plan,
    )
    if not catalog_valid:
        raise AssertionError(catalog_errors)
    generated_catalog = build_claim_scoped_mutant_catalog(committed_plan)
    if generated_catalog != committed_catalog:
        raise AssertionError(
            "committed mutant catalog differs from deterministic generation"
        )

    if committed_plan["execution_authorized"]:
        raise AssertionError("pre-execution plan authorized mutation execution")
    if committed_plan["holdout_selected"]:
        raise AssertionError("pre-execution plan selected a holdout")
    if committed_plan["primary_denominator_eligible"]:
        raise AssertionError("development plan entered the primary denominator")
    if committed_plan["future_execution_contract"]["headline_score"] is not None:
        raise AssertionError("pre-execution plan introduced a headline score")
    if committed_plan["future_execution_contract"]["merge_blocker_authorized"]:
        raise AssertionError("pre-execution plan authorized a merge blocker")

    statuses = [record["status"] for record in committed_catalog["mutants"]]
    if statuses != [
        "generated",
        "generated",
        "generated",
        "duplicate",
        "not_applicable",
        "invalid",
    ]:
        raise AssertionError("catalog generation-status ordering changed")
    if committed_catalog["summary"]["score"] is not None:
        raise AssertionError("mutant catalog introduced a scalar score")
    if committed_catalog["known_challenge_control"][
        "included_in_generic_operator_set"
    ]:
        raise AssertionError("known PR #34 mutant entered generic operator evidence")

    print(
        "DW-001 mutation plan smoke passed: "
        f"plan_sha256={committed_plan['plan_sha256']} "
        f"catalog_sha256={committed_catalog['catalog_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
