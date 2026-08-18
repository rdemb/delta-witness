from __future__ import annotations

import sys
import unittest

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
    verify_claim_relevant_path_catalog_document,
    verify_claim_relevant_path_plan_document,
    verify_claim_relevant_path_prior_art_log_document,
)


class DW001ClaimRelevantPathPreregistrationTests(unittest.TestCase):
    def test_exact_preregistration_contract_is_implemented(self) -> None:
        plan = build_claim_relevant_path_plan()
        catalog = build_claim_relevant_path_catalog(plan)
        prior_art = build_claim_relevant_path_prior_art_log(plan, catalog)

        self.assertEqual(plan["plan_sha256"], PLAN_SHA256)
        self.assertEqual(catalog["catalog_sha256"], CATALOG_SHA256)
        self.assertEqual(prior_art["log_sha256"], PRIOR_ART_LOG_SHA256)
        self.assertEqual(plan["source_scope"]["source_sha256"], SOURCE_SHA256)
        self.assertEqual(plan["source_scope"]["ast_sha256"], SOURCE_AST_SHA256)
        self.assertEqual(plan["test_scope"]["test_sha256"], TEST_SHA256)
        self.assertEqual(
            plan["influence_control"]["control_sha256"],
            INFLUENCE_CONTROL_SHA256,
        )

        plan_valid, plan_errors = verify_claim_relevant_path_plan_document(plan)
        catalog_valid, catalog_errors = (
            verify_claim_relevant_path_catalog_document(catalog, plan)
        )
        prior_valid, prior_errors = (
            verify_claim_relevant_path_prior_art_log_document(
                prior_art,
                plan,
                catalog,
            )
        )
        self.assertTrue(plan_valid, plan_errors)
        self.assertTrue(catalog_valid, catalog_errors)
        self.assertTrue(prior_valid, prior_errors)

    def test_preregistration_import_keeps_coverage_optional(self) -> None:
        self.assertNotIn("coverage", sys.modules)


if __name__ == "__main__":
    unittest.main()
