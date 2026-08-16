from __future__ import annotations

from pathlib import Path
import unittest
from unittest.mock import patch

import deltawitness.dw001_mutation_results as mutation_results
from deltawitness.reporting import load_report


_ROOT = Path(__file__).resolve().parents[1]
_PLAN_PATH = (
    _ROOT / "research" / "DW-001" / "claim-scoped-mutation-plan.v1.json"
)
_CATALOG_PATH = (
    _ROOT / "research" / "DW-001" / "claim-scoped-mutant-catalog.v1.json"
)


class DW001MutationNegativeResultRetentionTests(unittest.TestCase):
    def test_complete_unexpected_outcome_is_retained_not_suppressed(self) -> None:
        plan = load_report(_PLAN_PATH)
        catalog = load_report(_CATALOG_PATH)
        first_mutant_id = catalog["mutants"][0]["mutant_id"]
        original = mutation_results._execute_observation
        injected = False

        def divergent_observation(**kwargs):
            nonlocal injected
            if (
                not injected
                and kwargs["implementation_id"] == first_mutant_id
                and kwargs["profile_id"] == "strong-authorization-oracle-v1"
                and kwargs["selector"]
                == "test_access.AccessTests.test_admin_is_allowed"
            ):
                injected = True
                observation = mutation_results._expected_observation(
                    plan_sha256=kwargs["plan_sha256"],
                    catalog_sha256=kwargs["catalog_sha256"],
                    implementation_id=kwargs["implementation_id"],
                    profile_id=kwargs["profile_id"],
                    selector=kwargs["selector"],
                    source_sha256=kwargs["source_sha256"],
                    observed="pass",
                )
                observation["duration_seconds"] = 0.0
                observation["stdout_sha256"] = "0" * 64
                observation["stderr_sha256"] = "0" * 64
                return observation
            return original(**kwargs)

        with patch.object(
            mutation_results,
            "_execute_observation",
            side_effect=divergent_observation,
        ):
            result = mutation_results.run_claim_scoped_mutation_result(
                plan,
                catalog,
            )

        self.assertTrue(injected)
        valid, errors = mutation_results.verify_claim_scoped_mutation_result_document(
            result,
            plan,
            catalog,
        )
        self.assertTrue(valid, errors)
        self.assertEqual(result["analysis"]["status"], "unexpected")
        self.assertEqual(result["analysis"]["unexpected_observation_count"], 1)
        self.assertEqual(result["analysis"]["unexpected_profile_count"], 1)
        self.assertEqual(result["analysis"]["unexpected_reference_count"], 0)
        self.assertEqual(
            result["analysis"]["unexpected_record_ids"],
            [first_mutant_id],
        )

        record = result["records"][0]
        self.assertIs(record["concordant"], False)
        strong = record["profiles"][0]
        self.assertEqual(strong["expected_outcome"], "killed")
        self.assertEqual(strong["outcome"], "survived")
        self.assertIs(strong["concordant"], False)
        selector = strong["selectors"][0]
        self.assertEqual(selector["expected_observed"], "fail")
        self.assertEqual(selector["observed"], "pass")
        self.assertIs(selector["concordant"], False)

        self.assertEqual(result["summary"]["generic_strong_killed"], 2)
        self.assertEqual(result["summary"]["generic_strong_survived"], 1)
        self.assertEqual(result["summary"]["mutation_score"], None)
        self.assertIs(
            result["policy"]["primary_denominator_eligible"],
            False,
        )


if __name__ == "__main__":
    unittest.main()
