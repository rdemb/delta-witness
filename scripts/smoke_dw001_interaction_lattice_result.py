#!/usr/bin/env python3
"""Execute and verify the frozen DW-001 interaction-lattice result."""

from __future__ import annotations

import argparse
from pathlib import Path

from deltawitness.dw001_interaction_lattice_result import (
    run_interaction_witness_lattice_result,
    verify_interaction_witness_lattice_result_document,
)
from deltawitness.reporting import canonical_json, load_report


_ROOT = Path(__file__).resolve().parents[1]
_DW001 = _ROOT / "research" / "DW-001"
_PROTOCOL_PATH = (
    _DW001 / "interaction-witness-lattice-execution-protocol.v1.json"
)
_PLAN_PATH = _DW001 / "interaction-witness-lattice-plan.v1.json"
_CATALOG_PATH = (
    _DW001 / "interaction-witness-lattice-mutant-catalog.v1.json"
)
_PRIOR_ART_PATH = _DW001 / "interaction-witness-prior-art-log.v1.json"
_COVERAGEPY_MANIFEST_PATH = (
    _DW001 / "coveragepy-7.15.2-artifact.v1.json"
)
_PR46_RESULT_PATH = _DW001 / "coveragepy-baseline-result.v1.json"
_FROZEN_SEMANTIC_SHA256 = (
    "bc2ab879595da61815a17dcc33a09c6334b93dea3fd464f2fe4a5437944ebb77"
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run and verify the exact owned-synthetic selector-context "
            "interaction lattice."
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
    protocol = load_report(_PROTOCOL_PATH)
    plan = load_report(_PLAN_PATH)
    catalog = load_report(_CATALOG_PATH)
    prior_art = load_report(_PRIOR_ART_PATH)
    coveragepy_manifest = load_report(_COVERAGEPY_MANIFEST_PATH)
    pr46_result = load_report(_PR46_RESULT_PATH)
    result = run_interaction_witness_lattice_result(
        protocol,
        plan,
        catalog,
        prior_art,
        coveragepy_manifest,
        pr46_result,
    )
    valid, errors = verify_interaction_witness_lattice_result_document(
        result,
        protocol,
        plan,
        catalog,
        prior_art,
        coveragepy_manifest,
        pr46_result,
    )
    if not valid:
        raise AssertionError(errors)
    if result["semantic_sha256"] != _FROZEN_SEMANTIC_SHA256:
        raise AssertionError(
            "interaction-lattice semantic result changed: "
            f"expected {_FROZEN_SEMANTIC_SHA256}, "
            f"observed {result['semantic_sha256']}"
        )
    if result["analysis"]["status"] != "expected":
        raise AssertionError(
            "interaction-lattice result is complete but preregistration-"
            f"divergent: {result['analysis']}"
        )
    if result["summary"]["selector_command_count"] != 24:
        raise AssertionError("unexpected interaction selector command count")
    if result["summary"]["mutation_score"] is not None:
        raise AssertionError("mutation score escaped the policy boundary")
    if result["comparison"] != {
        "expected_statement_aggregate_discriminates_profiles": False,
        "statement_aggregate_discriminates_profiles": False,
        "expected_arc_aggregate_discriminates_profiles": False,
        "arc_aggregate_discriminates_profiles": False,
        "expected_anonymous_path_multiset_discriminates_profiles": True,
        "anonymous_path_multiset_discriminates_profiles": True,
        "expected_equal_cardinality_path_multisets_distinct": True,
        "equal_cardinality_path_multisets_distinct": True,
        "expected_mfa_independence_agrees_with_drop_mfa": True,
        "mfa_independence_agrees_with_drop_mfa": True,
        "expected_role_independence_agrees_with_drop_role": True,
        "role_independence_agrees_with_drop_role": True,
        "expected_any_independence_agrees_with_or_gates": True,
        "any_independence_agrees_with_or_gates": True,
        "concordant": True,
    }:
        raise AssertionError("interaction comparison changed")
    if args.emit_json:
        print(canonical_json(result).decode("utf-8"))
    elif args.semantic_digest:
        print(result["semantic_sha256"])
    else:
        print(
            "DW-001 interaction-lattice result smoke passed: "
            f"semantic_sha256={result['semantic_sha256']} "
            f"commands={result['summary']['selector_command_count']} "
            "statement_discrimination=false arc_discrimination=false "
            "path_multiset_discrimination=true"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
