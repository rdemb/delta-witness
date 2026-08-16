from __future__ import annotations

from pathlib import Path
import unittest

from deltawitness.dw001_pilot import (
    build_development_pilot_plan,
    verify_development_pilot_plan_document,
)
from deltawitness.reporting import load_report


_PLAN_PATH = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "DW-001"
    / "development-pilot-plan.v1.json"
)


class DW001CommittedDevelopmentPilotPlanTests(unittest.TestCase):
    def test_committed_plan_is_exact_builder_output(self) -> None:
        committed = load_report(_PLAN_PATH)
        expected = build_development_pilot_plan(
            protocol_commit_sha=committed["protocol_commit_sha"],
            implementation_commit_sha=committed["implementation_commit_sha"],
        )

        self.assertEqual(committed, expected)
        valid, errors = verify_development_pilot_plan_document(committed)
        self.assertTrue(valid, errors)

    def test_committed_plan_pins_preexisting_protocol_and_runner_revisions(self) -> None:
        committed = load_report(_PLAN_PATH)

        self.assertEqual(
            committed["protocol_commit_sha"],
            "732f829e25ea994858fffb0678892048617155c3",
        )
        self.assertEqual(
            committed["implementation_commit_sha"],
            "4ef67e0e7a20c7de03be825720dfb2d1da8e64fc",
        )
        self.assertEqual(
            committed["plan_sha256"],
            "48a98f01c740862c91056841a7f96e6c98f1ae9641b7b364590a45d458ae3bcc",
        )
        self.assertEqual(committed["partition"], "development")
        self.assertTrue(
            all(
                case["primary_denominator_eligible"] is False
                for case in committed["case_arms"]
            )
        )


if __name__ == "__main__":
    unittest.main()
