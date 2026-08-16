#!/usr/bin/env python3
"""Exercise the packaged sealed DW-001 development-pilot plan contract.

This smoke constructs and verifies only the pre-execution ten-arm plan. It does
not materialize fixtures, execute valid pilot cases, create pilot results, or
authorize a development pilot or holdout. It verifies that a tampered plan is
rejected before any output path is created.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import tempfile

from deltawitness.dw001_pilot import (
    PILOT_ID,
    build_development_pilot_plan,
    compute_development_pilot_plan_sha256,
    run_development_pilot,
    verify_development_pilot_plan_document,
)


_PROTOCOL_SHA = "a" * 40
_IMPLEMENTATION_SHA = "b" * 40


def main() -> int:
    plan = build_development_pilot_plan(
        protocol_commit_sha=_PROTOCOL_SHA,
        implementation_commit_sha=_IMPLEMENTATION_SHA,
    )
    valid, errors = verify_development_pilot_plan_document(plan)
    if not valid:
        raise AssertionError(errors)
    if plan["pilot_id"] != PILOT_ID:
        raise AssertionError("unexpected pilot identifier")
    if plan["partition"] != "development":
        raise AssertionError("pilot plan escaped development partition")
    if len(plan["case_arms"]) != 10:
        raise AssertionError("pilot plan does not contain exactly ten arms")
    if any(case["primary_denominator_eligible"] for case in plan["case_arms"]):
        raise AssertionError("development case became denominator eligible")
    if any(case["scenario_id"] != case["case_id"] for case in plan["case_arms"]):
        raise AssertionError("case and scenario identities diverged")
    if plan["analysis_contract"]["headline_score_allowed"]:
        raise AssertionError("development mechanism pilot enabled a headline score")
    if plan["analysis_contract"]["ecological_inference_allowed"]:
        raise AssertionError("development mechanism pilot enabled ecological inference")

    tampered = deepcopy(plan)
    tampered["case_arms"][0]["family_id"] = "non-discriminating-candidate-test"
    tampered["plan_sha256"] = compute_development_pilot_plan_sha256(tampered)
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "output"
        try:
            run_development_pilot(tampered, output)
        except Exception:
            pass
        else:
            raise AssertionError("tampered pilot plan was executed")
        if output.exists():
            raise AssertionError("runner created output before plan verification")

    print("DW-001 development pilot sealed-plan smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
