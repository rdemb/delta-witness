from __future__ import annotations

from copy import deepcopy
import json
import math
from pathlib import Path
import unittest

from deltawitness.dw001_mutation_plan import (
    build_claim_scoped_mutant_catalog,
    build_claim_scoped_mutation_plan,
    compute_mutant_catalog_sha256,
    verify_claim_scoped_mutant_catalog_document,
    verify_claim_scoped_mutation_plan_document,
)


_ROOT = Path(__file__).resolve().parents[1]
_PLAN_PATH = (
    _ROOT / "research" / "DW-001" / "claim-scoped-mutation-plan.v1.json"
)
_CATALOG_PATH = (
    _ROOT / "research" / "DW-001" / "claim-scoped-mutant-catalog.v1.json"
)


class DW001CommittedMutationCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = json.loads(_PLAN_PATH.read_text(encoding="utf-8"))
        cls.catalog = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))

    def test_committed_plan_and_catalog_are_exact_builder_outputs(self) -> None:
        plan_valid, plan_errors = verify_claim_scoped_mutation_plan_document(
            self.plan
        )
        catalog_valid, catalog_errors = (
            verify_claim_scoped_mutant_catalog_document(
                self.catalog,
                self.plan,
            )
        )
        self.assertTrue(plan_valid, plan_errors)
        self.assertTrue(catalog_valid, catalog_errors)
        self.assertEqual(self.plan, build_claim_scoped_mutation_plan())
        self.assertEqual(
            self.catalog,
            build_claim_scoped_mutant_catalog(self.plan),
        )

    def test_committed_identities_are_stable_across_supported_python_matrix(self) -> None:
        self.assertEqual(
            self.plan["plan_sha256"],
            "0ebf64e1de76849050c86d8a4d53d72d8067561ab48b4bd5a4083495dc99fe37",
        )
        self.assertEqual(
            self.catalog["catalog_sha256"],
            "7b3e405bd3893f532c0ccfa16e9cc208422bbdd20dfe82a002c99342a04201c0",
        )
        self.assertEqual(
            self.catalog["target"]["target_id"],
            "3cdfc367a78a09b257147fb236e80785d936177da231924f43e2d3d5fbd80e2e",
        )
        self.assertEqual(
            [record["mutant_id"] for record in self.catalog["mutants"]],
            [
                "5283f65eece7deda4935f369302db07c14fe45b0763b4ef4f6f86145cf4938f0",
                "69dd4198555f3412b0dc48fac16b36903dd4ef7c4b9a5e926f950c9a40a6b8d4",
                "2ff6ef3a8313eb6e50096d16aab038a2202a3c346ea386fd673f00b6b1a7adf3",
                "4303cb5b5390af25af0ab17c60f1f474e5038334742d7258a3b5f9d3390f2363",
                "ea40ad03324d0ef4911d037b862c97def07a591df78c43ae2891bd2a58e590bd",
                "7ed7b0a99fbd82d2fa7ad6f5de20285994529123dcd1e7a8896e4d67e6a37689",
            ],
        )

    def test_malformed_and_nonfinite_catalog_fields_fail_closed(self) -> None:
        for malformed in (None, [], "catalog", 7, {}):
            with self.subTest(root=type(malformed).__name__):
                valid, errors = verify_claim_scoped_mutant_catalog_document(
                    malformed,
                    self.plan,
                )
                self.assertFalse(valid)
                self.assertTrue(errors)

        nonfinite = deepcopy(self.catalog)
        nonfinite["summary"]["score"] = math.nan
        nonfinite["catalog_sha256"] = compute_mutant_catalog_sha256(
            nonfinite
        )
        valid, errors = verify_claim_scoped_mutant_catalog_document(
            nonfinite,
            self.plan,
        )
        self.assertFalse(valid)
        self.assertTrue(any("score" in error for error in errors), errors)

        wrong_type = deepcopy(self.catalog)
        wrong_type["mutants"] = {"operator": wrong_type["mutants"][0]}
        wrong_type["catalog_sha256"] = compute_mutant_catalog_sha256(
            wrong_type
        )
        valid, errors = verify_claim_scoped_mutant_catalog_document(
            wrong_type,
            self.plan,
        )
        self.assertFalse(valid)
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
