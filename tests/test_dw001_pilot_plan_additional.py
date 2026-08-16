from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from deltawitness.dw001_pilot import (
    build_development_pilot_plan,
    compute_development_pilot_plan_sha256,
    verify_development_pilot_plan_document,
)


_PROTOCOL_SHA = "a" * 40
_IMPLEMENTATION_SHA = "b" * 40
_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "DW-001"
    / "schema"
    / "development-pilot-plan.schema.json"
)


def _walk(value: object):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


class DW001DevelopmentPilotPlanAdditionalTests(unittest.TestCase):
    def _plan(self):
        return build_development_pilot_plan(
            protocol_commit_sha=_PROTOCOL_SHA,
            implementation_commit_sha=_IMPLEMENTATION_SHA,
        )

    def _resign(self, plan: dict[str, object]) -> None:
        plan["plan_sha256"] = compute_development_pilot_plan_sha256(plan)

    def test_every_schema_object_boundary_is_closed(self) -> None:
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        for node in _walk(schema):
            if isinstance(node, dict) and node.get("type") == "object":
                self.assertIs(
                    node.get("additionalProperties"),
                    False,
                    f"development pilot plan schema has an open object boundary: {node}",
                )

    def test_duplicate_case_id_or_order_is_rejected_after_resigning(self) -> None:
        for mutator, label in (
            (
                lambda plan: plan["case_arms"][1].__setitem__(
                    "case_id", plan["case_arms"][0]["case_id"]
                ),
                "case_id",
            ),
            (
                lambda plan: plan["case_arms"][1].__setitem__("order", 1),
                "order",
            ),
        ):
            with self.subTest(label=label):
                tampered = deepcopy(self._plan())
                mutator(tampered)
                self._resign(tampered)
                valid, errors = verify_development_pilot_plan_document(tampered)
                self.assertFalse(valid)
                self.assertTrue(any(label in error for error in errors), errors)

    def test_localization_selector_or_status_substitution_is_rejected(self) -> None:
        for field, value in (
            ("selectors", ["test_access.AccessTests.test_version_label_is_v2"]),
            ("expected_status", "supported"),
        ):
            with self.subTest(field=field):
                tampered = deepcopy(self._plan())
                tampered["case_arms"][8]["localization"][field] = value
                self._resign(tampered)
                valid, errors = verify_development_pilot_plan_document(tampered)
                self.assertFalse(valid)
                self.assertTrue(any("localization" in error for error in errors), errors)

    def test_unhashable_or_malformed_fields_fail_closed(self) -> None:
        mutations = (
            (lambda plan: plan["case_arms"][0].__setitem__("family_id", []), "family"),
            (
                lambda plan: plan["case_arms"][0]["localization"].__setitem__(
                    "expected_status", []
                ),
                "expected_status",
            ),
            (lambda plan: plan.__setitem__("contracts", []), "contracts"),
            (lambda plan: plan.__setitem__("case_arms", {}), "case_arms"),
        )
        for mutator, label in mutations:
            with self.subTest(label=label):
                tampered = deepcopy(self._plan())
                mutator(tampered)
                try:
                    self._resign(tampered)
                except Exception:
                    pass
                valid, errors = verify_development_pilot_plan_document(tampered)
                self.assertFalse(valid)
                self.assertTrue(errors)

    def test_plan_contains_no_private_or_runtime_fields(self) -> None:
        encoded = json.dumps(self._plan(), sort_keys=True)
        for prohibited in (
            "/tmp/",
            "\\Temp\\",
            "stdout",
            "stderr",
            "traceback",
            "credential",
            "environment_values",
            "holdout_committed",
            "review_time_seconds_observed",
        ):
            with self.subTest(prohibited=prohibited):
                self.assertNotIn(prohibited, encoded)


if __name__ == "__main__":
    unittest.main()
