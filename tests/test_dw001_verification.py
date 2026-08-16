from __future__ import annotations

from copy import deepcopy
import unittest

from deltawitness.dw001 import (
    compute_projection_sha256,
    project_baselines,
    verify_projection_document,
)
from test_dw001 import _report


class DW001ProjectionVerificationTests(unittest.TestCase):
    def _resign_projection(self, projection: dict[str, object]) -> None:
        projection["projection_sha256"] = compute_projection_sha256(projection)

    def test_recomputed_digest_cannot_hide_semantically_inconsistent_method_decision(self) -> None:
        projection = project_baselines(_report(), scenario_id="semantic-verification-001")
        tampered = deepcopy(projection)
        tampered["methods"][0]["decision"] = "reject"
        tampered["methods"][0]["reason_code"] = "predicate_contradicted"
        self._resign_projection(tampered)

        valid, errors = verify_projection_document(tampered)

        self.assertFalse(valid)
        self.assertTrue(
            any("method decision is inconsistent" in error for error in errors),
            errors,
        )

    def test_recomputed_digest_cannot_hide_divergent_shared_state_observation(self) -> None:
        projection = project_baselines(_report(), scenario_id="shared-state-verification-001")
        tampered = deepcopy(projection)
        method = tampered["methods"][1]
        claim = method["claims"][0]
        candidate_candidate = claim["states"][1]
        candidate_candidate["observed"] = "fail"
        candidate_candidate["matched"] = False
        claim["contradicted_states"] = ["candidate_candidate"]
        claim["decision"] = "reject"
        claim["reason_code"] = "predicate_contradicted"
        method["decision"] = "reject"
        method["reason_code"] = "predicate_contradicted"
        self._resign_projection(tampered)

        valid, errors = verify_projection_document(tampered)

        self.assertFalse(valid)
        self.assertTrue(
            any("shared state observation differs" in error for error in errors),
            errors,
        )

    def test_recomputed_digest_cannot_hide_inconsistent_applicability_partition(self) -> None:
        projection = project_baselines(_report(), scenario_id="applicability-verification-001")
        tampered = deepcopy(projection)
        tampered["applicability"]["non_applicable_states"] = [
            {
                "state": "base_base",
                "reason": "Synthetic inconsistent applicability declaration.",
            }
        ]
        self._resign_projection(tampered)

        valid, errors = verify_projection_document(tampered)

        self.assertFalse(valid)
        self.assertTrue(
            any("canonical complement" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
