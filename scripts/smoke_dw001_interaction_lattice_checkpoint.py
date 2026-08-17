#!/usr/bin/env python3
"""Verify the frozen public-safe interaction-lattice checkpoint.

This smoke imports no Coverage.py runtime. It reconstructs the checkpoint from
the merged preregistration and catalog, verifies every exact source binding and
semantic relation, and confirms that score, threshold, blocker, holdout,
ecological, superiority, production, novelty, and award-level claims remain
disabled.
"""

from __future__ import annotations

from pathlib import Path
import sys

from deltawitness.dw001_interaction_lattice_checkpoint import (
    CHECKPOINT_SHA256,
    RESULT_SEMANTIC_SHA256,
    build_interaction_lattice_result_checkpoint,
    load_interaction_lattice_result_checkpoint,
)
from deltawitness.reporting import load_report


_ROOT = Path(__file__).resolve().parents[1]
_DW001 = _ROOT / "research" / "DW-001"
_CHECKPOINT_PATH = (
    _DW001 / "interaction-witness-lattice-result-checkpoint.v1.json"
)
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


def main() -> int:
    protocol = load_report(_PROTOCOL_PATH)
    plan = load_report(_PLAN_PATH)
    catalog = load_report(_CATALOG_PATH)
    prior_art = load_report(_PRIOR_ART_PATH)
    coveragepy_manifest = load_report(_COVERAGEPY_MANIFEST_PATH)
    pr46_result = load_report(_PR46_RESULT_PATH)
    checkpoint = load_interaction_lattice_result_checkpoint(
        _CHECKPOINT_PATH,
        protocol,
        plan,
        catalog,
        prior_art,
        coveragepy_manifest,
        pr46_result,
    )
    rebuilt = build_interaction_lattice_result_checkpoint(plan, catalog)
    if checkpoint != rebuilt:
        raise AssertionError("interaction checkpoint reconstruction changed")
    if checkpoint["semantic_sha256"] != RESULT_SEMANTIC_SHA256:
        raise AssertionError("interaction result semantic identity changed")
    if checkpoint["checkpoint_sha256"] != CHECKPOINT_SHA256:
        raise AssertionError("interaction checkpoint identity changed")
    if checkpoint["status"] != "expected":
        raise AssertionError("interaction checkpoint status changed")
    if checkpoint["summary"]["selector_command_count"] != 24:
        raise AssertionError("interaction command count changed")
    if checkpoint["summary"]["mutation_score"] is not None:
        raise AssertionError("mutation score escaped the policy boundary")
    if checkpoint["comparison"] != {
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
    policy = checkpoint["policy"]
    if any(
        value is not False
        for key, value in policy.items()
        if key
        not in {
            "quality_score",
            "headline_score",
            "universal_threshold",
        }
    ):
        raise AssertionError("interaction policy authorization changed")
    if any(
        policy[key] is not None
        for key in (
            "quality_score",
            "headline_score",
            "universal_threshold",
        )
    ):
        raise AssertionError("interaction scalar policy changed")
    if "coverage" in sys.modules:
        raise AssertionError("checkpoint smoke imported Coverage.py")

    print(
        "DW-001 interaction-lattice checkpoint smoke passed: "
        f"semantic_sha256={RESULT_SEMANTIC_SHA256} "
        f"checkpoint_sha256={CHECKPOINT_SHA256} "
        "commands=24 status=expected"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
