#!/usr/bin/env python3
"""Execute and verify the frozen owned-synthetic mutation result table.

The smoke runs only the candidate, three frozen generic mutants, one separately
labeled historical challenge control, and exact project-owned selector sets.
It does not execute an external repository or holdout and emits no mutation
score, threshold, merge blocker, or ecological claim.
"""

from __future__ import annotations

from pathlib import Path

from deltawitness.dw001_mutation_results import (
    run_claim_scoped_mutation_result,
    verify_claim_scoped_mutation_result_document,
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
    plan = load_report(_PLAN_PATH)
    catalog = load_report(_CATALOG_PATH)
    result = run_claim_scoped_mutation_result(plan, catalog)
    valid, errors = verify_claim_scoped_mutation_result_document(
        result,
        plan,
        catalog,
    )
    if not valid:
        raise AssertionError(errors)

    if result["analysis"] != {
        "status": "expected",
        "candidate_baseline_concordant": True,
        "unexpected_observation_count": 0,
        "unexpected_profile_count": 0,
        "unexpected_reference_count": 0,
        "unexpected_record_ids": [],
    }:
        raise AssertionError("preregistered mutation outcomes diverged")
    if result["summary"] != {
        "candidate_baseline_valid": True,
        "catalog_records": 6,
        "generic_mutants_executed": 3,
        "historical_controls_executed": 1,
        "generation_records_not_executed": 3,
        "generic_strong_killed": 3,
        "generic_strong_survived": 0,
        "generic_strong_indeterminate": 0,
        "generic_weak_killed": 0,
        "generic_weak_survived": 3,
        "generic_weak_indeterminate": 0,
        "generic_claim_violations_observed": 3,
        "mutation_score": None,
    }:
        raise AssertionError("mutation-result summary changed")
    if result["policy"] != {
        "retain_complete_mutant_table": True,
        "headline_score": None,
        "universal_threshold": None,
        "merge_blocker_authorized": False,
        "ecological_inference_allowed": False,
        "holdout_selected": False,
        "primary_denominator_eligible": False,
        "generic_operator_generalization_allowed": False,
    }:
        raise AssertionError("mutation-result policy boundary changed")
    if result["cost"]["command_count"] != 25:
        raise AssertionError("unexpected mutation-result command count")

    print(
        "DW-001 mutation result smoke passed: "
        f"semantic_sha256={result['semantic_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
