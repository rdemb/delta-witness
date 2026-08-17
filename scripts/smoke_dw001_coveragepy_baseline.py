#!/usr/bin/env python3
"""Exercise the fixed DW-001 Coverage.py direct baseline.

The smoke executes only fixed project-owned candidate source and selector
bytes. It verifies the complete result, preserves the preregistered comparison
boundary, and emits no score, threshold, blocker, holdout, ecological, or
method-superiority claim.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from deltawitness.dw001_coveragepy_baseline import (
    run_claim_scoped_coveragepy_baseline,
    verify_claim_scoped_coveragepy_baseline_document,
)
from deltawitness.dw001_mutation_results import run_claim_scoped_mutation_result
from deltawitness.dw001_statement_coverage import run_claim_scoped_statement_coverage
from deltawitness.reporting import canonical_json, load_report


_ROOT = Path(__file__).resolve().parents[1]
_PLAN_PATH = (
    _ROOT / "research" / "DW-001" / "claim-scoped-mutation-plan.v1.json"
)
_CATALOG_PATH = (
    _ROOT / "research" / "DW-001" / "claim-scoped-mutant-catalog.v1.json"
)
_FROZEN_SEMANTIC_SHA256 = (
    "ec0c2fdd5ac24ba53eb895d9014aab623d2631125b8512ba0e0cbf5105f21ee8"
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run and verify the exact owned-synthetic Coverage.py direct "
            "baseline."
        )
    )
    output = parser.add_mutually_exclusive_group()
    output.add_argument(
        "--emit-json",
        action="store_true",
        help="emit the verified public-safe result as canonical JSON",
    )
    output.add_argument(
        "--semantic-digest",
        action="store_true",
        help="emit only the stable semantic SHA-256",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    plan = load_report(_PLAN_PATH)
    catalog = load_report(_CATALOG_PATH)
    mutation_result = run_claim_scoped_mutation_result(plan, catalog)
    stdlib_result = run_claim_scoped_statement_coverage(
        plan,
        catalog,
        mutation_result,
    )
    result = run_claim_scoped_coveragepy_baseline(
        plan,
        catalog,
        mutation_result,
        stdlib_result,
    )
    valid, errors = verify_claim_scoped_coveragepy_baseline_document(
        result,
        plan,
        catalog,
        mutation_result,
        stdlib_result,
    )
    if not valid:
        raise AssertionError(errors)
    if result["semantic_sha256"] != _FROZEN_SEMANTIC_SHA256:
        raise AssertionError(
            "Coverage.py semantic result changed: "
            f"expected {_FROZEN_SEMANTIC_SHA256}, "
            f"observed {result['semantic_sha256']}"
        )

    if result["analysis"] != {
        "status": "expected",
        "unexpected_selector_count": 0,
        "unexpected_profile_count": 0,
        "indeterminate_selector_count": 0,
        "unexpected_profile_ids": [],
        "comparison_concordant": True,
    }:
        raise AssertionError("Coverage.py baseline analysis changed")
    if result["comparison"] != {
        "expected_stdlib_statement_discriminates_profiles": False,
        "expected_coveragepy_statement_discriminates_profiles": False,
        "expected_coveragepy_branch_discriminates_profiles": False,
        "expected_mutation_discriminates_profiles": True,
        "expected_stdlib_and_coveragepy_statement_agree": True,
        "expected_coveragepy_branch_and_mutation_agree": False,
        "expected_incremental_branch_signal_observed": False,
        "expected_incremental_mutation_signal_beyond_coveragepy_observed": True,
        "stdlib_statement_discriminates_profiles": False,
        "coveragepy_statement_discriminates_profiles": False,
        "coveragepy_branch_discriminates_profiles": False,
        "mutation_discriminates_profiles": True,
        "stdlib_and_coveragepy_statement_agree": True,
        "coveragepy_branch_and_mutation_agree": False,
        "incremental_branch_signal_observed": False,
        "incremental_mutation_signal_beyond_coveragepy_observed": True,
        "concordant": True,
    }:
        raise AssertionError("Coverage.py comparison changed")
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
        raise AssertionError("Coverage.py policy boundary changed")
    if result["cost"]["command_count"] != 3:
        raise AssertionError("unexpected Coverage.py command count")

    strong, weak = result["profiles"]
    for profile in (strong, weak):
        if profile["statement_union"] != [2]:
            raise AssertionError("Coverage.py statement union changed")
        if profile["statement_intersection"] != [2]:
            raise AssertionError("Coverage.py statement intersection changed")
        if profile["coverage_status"] != "complete":
            raise AssertionError("Coverage.py profile became incomplete")
        if profile["context_partition_valid"] is not True:
            raise AssertionError("Coverage.py context partition changed")

    if args.emit_json:
        print(canonical_json(result).decode("utf-8"))
    elif args.semantic_digest:
        print(result["semantic_sha256"])
    else:
        print(
            "DW-001 Coverage.py baseline smoke passed: "
            f"semantic_sha256={result['semantic_sha256']} "
            f"strong_arcs={strong['arc_union']} "
            f"weak_arcs={weak['arc_union']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
