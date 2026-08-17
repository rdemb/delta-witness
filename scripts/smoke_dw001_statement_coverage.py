#!/usr/bin/env python3
"""Exercise the packaged DW-001 statement-coverage comparison baseline.

The smoke executes only the fixed project-owned candidate and the three exact
selectors frozen by the mutation plan. It compares target-statement signatures
with the already verified owned-synthetic mutation result and emits no score,
threshold, blocker, holdout, or ecological claim.
"""

from __future__ import annotations

from pathlib import Path

from deltawitness.dw001_mutation_results import run_claim_scoped_mutation_result
from deltawitness.dw001_statement_coverage import (
    run_claim_scoped_statement_coverage,
    verify_claim_scoped_statement_coverage_document,
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
    mutation_result = run_claim_scoped_mutation_result(plan, catalog)
    result = run_claim_scoped_statement_coverage(
        plan,
        catalog,
        mutation_result,
    )
    valid, errors = verify_claim_scoped_statement_coverage_document(
        result,
        plan,
        catalog,
        mutation_result,
    )
    if not valid:
        raise AssertionError(errors)

    if result["analysis"] != {
        "status": "expected",
        "unexpected_selector_count": 0,
        "unexpected_profile_count": 0,
        "indeterminate_selector_count": 0,
        "unexpected_profile_ids": [],
        "comparison_concordant": True,
    }:
        raise AssertionError("statement-coverage analysis changed")
    if result["comparison"] != {
        "expected_statement_coverage_discriminates_profiles": False,
        "expected_mutation_discriminates_profiles": True,
        "expected_coverage_and_mutation_agree": False,
        "expected_incremental_mutation_signal_observed": True,
        "statement_coverage_discriminates_profiles": False,
        "mutation_discriminates_profiles": True,
        "coverage_and_mutation_agree": False,
        "incremental_mutation_signal_observed": True,
        "concordant": True,
    }:
        raise AssertionError("coverage-versus-mutation comparison changed")
    if result["policy"] != {
        "quality_score": None,
        "headline_score": None,
        "universal_threshold": None,
        "merge_blocker_authorized": False,
        "ecological_inference_allowed": False,
        "holdout_selected": False,
        "primary_denominator_eligible": False,
        "coverage_superiority_claim_allowed": False,
        "mutation_superiority_claim_allowed": False,
    }:
        raise AssertionError("statement-coverage policy boundary changed")
    if result["cost"]["command_count"] != 3:
        raise AssertionError("unexpected statement-coverage command count")

    strong, weak = result["profiles"]
    if strong["union_lines"] != [2] or strong["intersection_lines"] != [2]:
        raise AssertionError("strong profile target-line signature changed")
    if weak["union_lines"] != [2] or weak["intersection_lines"] != [2]:
        raise AssertionError("weak profile target-line signature changed")

    print(
        "DW-001 statement coverage smoke passed: "
        f"semantic_sha256={result['semantic_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
