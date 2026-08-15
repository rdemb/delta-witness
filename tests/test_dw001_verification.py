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
    def test_recomputed_digest_cannot_hide_semantically_inconsistent_method_decision(self) -> None:
        projection = project_baselines(_report(), scenario_id="semantic-verification-001")
        tampered = deepcopy(projection)
        tampered["methods"][0]["decision"] = "reject"
        tampered["methods"][0]["reason_code"] = "predicate_contradicted"
        tampered["projection_sha256"] = compute_projection_sha256(tampered)

        valid, errors = verify_projection_document(tampered)

        self.assertFalse(valid)
        self.assertTrue(
            any("method decision is inconsistent" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
