#!/usr/bin/env python3
"""Rebuild and verify the design-only interaction-witness lattice artifacts."""

from __future__ import annotations

from pathlib import Path

from deltawitness.dw001_interaction_lattice_plan import (
    build_interaction_witness_lattice_mutant_catalog,
    build_interaction_witness_lattice_plan,
    verify_interaction_witness_lattice_mutant_catalog_document,
    verify_interaction_witness_lattice_plan_document,
)
from deltawitness.reporting import load_report


_ROOT = Path(__file__).resolve().parents[1]
_PLAN_PATH = (
    _ROOT
    / "research"
    / "DW-001"
    / "interaction-witness-lattice-plan.v1.json"
)
_CATALOG_PATH = (
    _ROOT
    / "research"
    / "DW-001"
    / "interaction-witness-lattice-mutant-catalog.v1.json"
)
_PLAN_SHA256 = (
    "a79a500feb94c8ad78fe4633f9ca176465113de6297db2d07b2d005f5318e1f1"
)
_CATALOG_SHA256 = (
    "2b06a86180a45fcd495c0bcf39365dde0cb590507e9a3528714f9ef58526308e"
)


def main() -> int:
    committed_plan = load_report(_PLAN_PATH)
    committed_catalog = load_report(_CATALOG_PATH)
    rebuilt_plan = build_interaction_witness_lattice_plan()
    rebuilt_catalog = build_interaction_witness_lattice_mutant_catalog(
        rebuilt_plan
    )
    if committed_plan != rebuilt_plan:
        raise AssertionError("committed interaction-lattice plan changed")
    if committed_catalog != rebuilt_catalog:
        raise AssertionError("committed interaction-lattice catalog changed")

    plan_valid, plan_errors = (
        verify_interaction_witness_lattice_plan_document(committed_plan)
    )
    if not plan_valid:
        raise AssertionError(plan_errors)
    catalog_valid, catalog_errors = (
        verify_interaction_witness_lattice_mutant_catalog_document(
            committed_catalog,
            committed_plan,
        )
    )
    if not catalog_valid:
        raise AssertionError(catalog_errors)

    if committed_plan["plan_sha256"] != _PLAN_SHA256:
        raise AssertionError("interaction-lattice plan digest changed")
    if committed_catalog["catalog_sha256"] != _CATALOG_SHA256:
        raise AssertionError("interaction-lattice catalog digest changed")
    if committed_plan["future_execution_contract"]["execution_status"] != (
        "not_implemented"
    ):
        raise AssertionError("design-only execution boundary changed")
    if committed_plan["execution_authorized"] is not False:
        raise AssertionError("execution authorization changed")
    if committed_plan["holdout_selected"] is not False:
        raise AssertionError("holdout boundary changed")
    if committed_plan["primary_denominator_eligible"] is not False:
        raise AssertionError("denominator boundary changed")
    if committed_catalog["summary"] != {
        "total_records": 8,
        "generic_operator_records": 5,
        "generation_control_records": 3,
        "generated": 5,
        "duplicate": 1,
        "invalid": 1,
        "not_applicable": 1,
        "score": None,
    }:
        raise AssertionError("interaction-lattice catalog summary changed")

    print(
        "DW-001 interaction-lattice design smoke passed: "
        f"plan_sha256={_PLAN_SHA256} "
        f"catalog_sha256={_CATALOG_SHA256} execution=not_implemented"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
