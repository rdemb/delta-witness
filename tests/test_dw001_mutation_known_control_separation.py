from __future__ import annotations

import unittest

from deltawitness.dw001_mutation_plan import (
    build_claim_scoped_mutant_catalog,
    build_claim_scoped_mutation_plan,
)


class DW001MutationKnownControlSeparationTests(unittest.TestCase):
    def test_historical_weak_proxy_mutant_is_not_a_generic_generated_mutant(self) -> None:
        plan = build_claim_scoped_mutation_plan()
        catalog = build_claim_scoped_mutant_catalog(plan)
        known = catalog["known_challenge_control"]
        generic = [
            record
            for record in catalog["mutants"]
            if record["catalog_role"] == "generic_operator"
        ]

        self.assertFalse(known["included_in_generic_operator_set"])
        self.assertFalse(known["counts_toward_operator_generalization"])
        self.assertNotIn(
            known["mutated_source_sha256"],
            {record["mutated_source_sha256"] for record in generic},
        )
        self.assertNotIn(
            known["mutated_ast_sha256"],
            {record["mutated_ast_sha256"] for record in generic},
        )
        self.assertNotIn(
            known["mutant_id"],
            {record["mutant_id"] for record in generic},
        )


if __name__ == "__main__":
    unittest.main()
