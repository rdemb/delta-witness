from __future__ import annotations

from copy import deepcopy
import json
import math
from pathlib import Path
import unittest
from unittest.mock import patch

import deltawitness.dw001_statement_coverage as statement_coverage
from deltawitness.dw001_mutation_results import (
    run_claim_scoped_mutation_result,
)
from deltawitness.reporting import canonical_json, load_report


_ROOT = Path(__file__).resolve().parents[1]
_PLAN_PATH = (
    _ROOT / "research" / "DW-001" / "claim-scoped-mutation-plan.v1.json"
)
_CATALOG_PATH = (
    _ROOT / "research" / "DW-001" / "claim-scoped-mutant-catalog.v1.json"
)
_SCHEMA_PATH = (
    _ROOT
    / "research"
    / "DW-001"
    / "schema"
    / "statement-coverage-result.schema.json"
)

_ROOT_FIELDS = {
    "schema_version",
    "study_id",
    "result_id",
    "partition",
    "plan_sha256",
    "catalog_sha256",
    "mutation_result_semantic_sha256",
    "created_at",
    "runtime",
    "adapter",
    "source",
    "profiles",
    "comparison",
    "analysis",
    "policy",
    "cost",
    "semantic_sha256",
    "report_sha256",
}
_STRONG = "strong-authorization-oracle-v1"
_WEAK = "weak-boolean-proxy-v1"
_EXPECTED_SELECTORS = {
    _STRONG: [
        "test_access.AccessTests.test_admin_is_allowed",
        "test_access.AccessTests.test_viewer_is_denied",
    ],
    _WEAK: [
        "test_access.AccessTests.test_viewer_result_is_boolean",
    ],
}


def _walk(value: object):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _profile(document: dict[str, object], profile_id: str) -> dict[str, object]:
    matches = [
        profile
        for profile in document["profiles"]
        if profile["profile_id"] == profile_id
    ]
    if len(matches) != 1:
        raise AssertionError((profile_id, matches))
    return matches[0]


def _semantic_copy(document: dict[str, object]) -> dict[str, object]:
    normalized = deepcopy(document)
    normalized["created_at"] = None
    normalized["runtime"] = None
    normalized["semantic_sha256"] = None
    normalized["report_sha256"] = None
    normalized["cost"]["wall_clock_seconds"] = None
    normalized["cost"]["cpu_seconds"] = None
    for profile in normalized["profiles"]:
        profile["cost"]["wall_clock_seconds"] = None
        profile["cost"]["cpu_seconds"] = None
        for selector in profile["selectors"]:
            selector["duration_seconds"] = None
            selector["stdout_sha256"] = None
            selector["stderr_sha256"] = None
    return normalized


class DW001StatementCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = load_report(_PLAN_PATH)
        cls.catalog = load_report(_CATALOG_PATH)
        cls.mutation_result = run_claim_scoped_mutation_result(
            cls.plan,
            cls.catalog,
        )

    def _run(self) -> dict[str, object]:
        return statement_coverage.run_claim_scoped_statement_coverage(
            self.plan,
            self.catalog,
            self.mutation_result,
        )

    def test_result_is_strict_bound_and_self_verifying(self) -> None:
        result = self._run()
        self.assertEqual(set(result), _ROOT_FIELDS)
        self.assertEqual(
            result["schema_version"],
            statement_coverage.RESULT_SCHEMA_VERSION,
        )
        self.assertEqual(result["result_id"], statement_coverage.RESULT_ID)
        self.assertEqual(result["study_id"], "DW-001")
        self.assertEqual(result["partition"], "development")
        self.assertEqual(result["plan_sha256"], self.plan["plan_sha256"])
        self.assertEqual(
            result["catalog_sha256"],
            self.catalog["catalog_sha256"],
        )
        self.assertEqual(
            result["mutation_result_semantic_sha256"],
            statement_coverage.MUTATION_RESULT_SEMANTIC_SHA256,
        )
        valid, errors = (
            statement_coverage.verify_claim_scoped_statement_coverage_document(
                result,
                self.plan,
                self.catalog,
                self.mutation_result,
            )
        )
        self.assertTrue(valid, errors)

    def test_every_candidate_selector_passes_and_covers_the_exact_target_line(self) -> None:
        result = self._run()
        self.assertEqual(result["source"]["path"], "src/access.py")
        self.assertEqual(result["source"]["symbol"], "is_admin")
        self.assertEqual(result["source"]["target_lines"], [2])
        self.assertEqual(
            result["source"]["target_id"],
            self.catalog["target"]["target_id"],
        )

        for profile_id, expected_selectors in _EXPECTED_SELECTORS.items():
            profile = _profile(result, profile_id)
            self.assertEqual(
                [selector["selector"] for selector in profile["selectors"]],
                expected_selectors,
            )
            self.assertEqual(profile["coverage_status"], "complete")
            self.assertTrue(profile["all_selectors_passed"])
            self.assertTrue(profile["concordant"])
            for selector in profile["selectors"]:
                with self.subTest(profile=profile_id, selector=selector["selector"]):
                    self.assertEqual(selector["expected_observed"], "pass")
                    self.assertEqual(selector["observed"], "pass")
                    self.assertTrue(selector["outcome_concordant"])
                    self.assertEqual(selector["expected_covered_lines"], [2])
                    self.assertEqual(selector["trace"]["trace_status"], "complete")
                    self.assertEqual(selector["trace"]["function_calls"], 1)
                    self.assertEqual(selector["trace"]["covered_lines"], [2])
                    self.assertEqual(
                        selector["trace"]["line_hits"],
                        [{"line": 2, "hits": 1}],
                    )
                    self.assertTrue(selector["coverage_concordant"])
                    self.assertTrue(selector["concordant"])
                    self.assertFalse(selector["timed_out"])
                    self.assertIsNone(selector["observation_error"])
                    self.assertTrue(selector["receipt_sha256"])
                    self.assertTrue(selector["trace"]["trace_sha256"])

    def test_statement_sets_do_not_distinguish_profiles_despite_different_hit_counts(self) -> None:
        result = self._run()
        strong = _profile(result, _STRONG)
        weak = _profile(result, _WEAK)

        self.assertEqual(strong["union_lines"], [2])
        self.assertEqual(strong["intersection_lines"], [2])
        self.assertEqual(weak["union_lines"], [2])
        self.assertEqual(weak["intersection_lines"], [2])
        self.assertEqual(strong["line_hits"], [{"line": 2, "hits": 2}])
        self.assertEqual(weak["line_hits"], [{"line": 2, "hits": 1}])

        comparison = result["comparison"]
        self.assertFalse(
            comparison["statement_coverage_discriminates_profiles"]
        )
        self.assertTrue(comparison["mutation_discriminates_profiles"])
        self.assertFalse(comparison["coverage_and_mutation_agree"])
        self.assertTrue(comparison["incremental_mutation_signal_observed"])
        self.assertTrue(comparison["concordant"])

    def test_result_has_no_score_threshold_or_policy_authorization(self) -> None:
        result = self._run()
        self.assertEqual(
            result["policy"],
            {
                "quality_score": None,
                "headline_score": None,
                "universal_threshold": None,
                "merge_blocker_authorized": False,
                "ecological_inference_allowed": False,
                "holdout_selected": False,
                "primary_denominator_eligible": False,
                "coverage_superiority_claim_allowed": False,
                "mutation_superiority_claim_allowed": False,
            },
        )
        self.assertEqual(result["cost"]["command_count"], 3)
        self.assertEqual(result["cost"]["selector_count"], 3)
        self.assertEqual(result["cost"]["profile_count"], 2)

    def test_repeated_runs_preserve_semantic_digest_and_coverage_signatures(self) -> None:
        first = self._run()
        second = self._run()
        self.assertEqual(first["semantic_sha256"], second["semantic_sha256"])
        self.assertEqual(
            canonical_json(_semantic_copy(first)),
            canonical_json(_semantic_copy(second)),
        )

    def test_complete_unexpected_coverage_signature_is_retained(self) -> None:
        original = getattr(statement_coverage, "_execute_selector", None)
        injected = False

        def divergent_selector(**kwargs):
            nonlocal injected
            observation = original(**kwargs)
            if (
                not injected
                and kwargs["profile_id"] == _STRONG
                and kwargs["selector"]
                == "test_access.AccessTests.test_admin_is_allowed"
            ):
                injected = True
                observation = deepcopy(observation)
                observation["trace"]["function_calls"] = 0
                observation["trace"]["covered_lines"] = []
                observation["trace"]["line_hits"] = []
                observation["trace"]["trace_sha256"] = (
                    statement_coverage._compute_trace_sha256(
                        observation["trace"]
                    )
                )
            return observation

        with patch.object(
            statement_coverage,
            "_execute_selector",
            side_effect=divergent_selector,
            create=True,
        ):
            result = self._run()

        self.assertTrue(injected)
        valid, errors = (
            statement_coverage.verify_claim_scoped_statement_coverage_document(
                result,
                self.plan,
                self.catalog,
                self.mutation_result,
            )
        )
        self.assertTrue(valid, errors)
        self.assertEqual(result["analysis"]["status"], "unexpected")
        self.assertEqual(result["analysis"]["unexpected_selector_count"], 1)
        self.assertEqual(result["analysis"]["unexpected_profile_count"], 1)
        self.assertEqual(result["analysis"]["unexpected_profile_ids"], [_STRONG])
        self.assertTrue(
            result["comparison"]["statement_coverage_discriminates_profiles"]
        )
        self.assertFalse(
            result["comparison"]["incremental_mutation_signal_observed"]
        )
        self.assertFalse(result["comparison"]["concordant"])

    def test_trace_indeterminate_is_not_converted_to_empty_coverage(self) -> None:
        original = getattr(statement_coverage, "_execute_selector", None)
        injected = False

        def indeterminate_selector(**kwargs):
            nonlocal injected
            observation = original(**kwargs)
            if (
                not injected
                and kwargs["profile_id"] == _WEAK
            ):
                injected = True
                observation = deepcopy(observation)
                observation["trace"]["trace_status"] = "indeterminate"
                observation["trace"]["function_calls"] = None
                observation["trace"]["covered_lines"] = []
                observation["trace"]["line_hits"] = []
                observation["trace"]["trace_error"] = "trace_unavailable"
                observation["trace"]["trace_sha256"] = (
                    statement_coverage._compute_trace_sha256(
                        observation["trace"]
                    )
                )
            return observation

        with patch.object(
            statement_coverage,
            "_execute_selector",
            side_effect=indeterminate_selector,
            create=True,
        ):
            result = self._run()

        self.assertTrue(injected)
        valid, errors = (
            statement_coverage.verify_claim_scoped_statement_coverage_document(
                result,
                self.plan,
                self.catalog,
                self.mutation_result,
            )
        )
        self.assertTrue(valid, errors)
        weak = _profile(result, _WEAK)
        self.assertEqual(weak["coverage_status"], "indeterminate")
        self.assertIsNone(weak["union_lines"])
        self.assertIsNone(weak["intersection_lines"])
        self.assertEqual(result["analysis"]["status"], "indeterminate")
        self.assertEqual(result["analysis"]["indeterminate_selector_count"], 1)
        self.assertIsNone(
            result["comparison"]["statement_coverage_discriminates_profiles"]
        )
        self.assertIsNone(
            result["comparison"]["incremental_mutation_signal_observed"]
        )

    def test_recomputed_digests_cannot_hide_relational_or_policy_drift(self) -> None:
        first = self._run()
        for mutator, expected in (
            (
                lambda document: document["source"].__setitem__(
                    "target_id", "f" * 64
                ),
                "target_id",
            ),
            (
                lambda document: document["profiles"][0]["selectors"][0][
                    "trace"
                ].__setitem__("covered_lines", []),
                "covered_lines",
            ),
            (
                lambda document: document["profiles"][0].__setitem__(
                    "union_lines", []
                ),
                "union_lines",
            ),
            (
                lambda document: document["comparison"].__setitem__(
                    "incremental_mutation_signal_observed", False
                ),
                "incremental_mutation_signal_observed",
            ),
            (
                lambda document: document["policy"].__setitem__(
                    "merge_blocker_authorized", True
                ),
                "merge_blocker_authorized",
            ),
        ):
            with self.subTest(expected=expected):
                tampered = deepcopy(first)
                mutator(tampered)
                tampered["semantic_sha256"] = (
                    statement_coverage.compute_statement_coverage_semantic_sha256(
                        tampered
                    )
                )
                tampered["report_sha256"] = (
                    statement_coverage.compute_statement_coverage_report_sha256(
                        tampered
                    )
                )
                valid, errors = (
                    statement_coverage.verify_claim_scoped_statement_coverage_document(
                        tampered,
                        self.plan,
                        self.catalog,
                        self.mutation_result,
                    )
                )
                self.assertFalse(valid)
                self.assertTrue(any(expected in error for error in errors), errors)

    def test_malformed_nonfinite_and_wrong_type_evidence_fails_closed(self) -> None:
        first = self._run()
        for malformed in (None, [], "coverage", 7, {}):
            with self.subTest(root=type(malformed).__name__):
                valid, errors = (
                    statement_coverage.verify_claim_scoped_statement_coverage_document(
                        malformed,
                        self.plan,
                        self.catalog,
                        self.mutation_result,
                    )
                )
                self.assertFalse(valid)
                self.assertTrue(errors)

        nonfinite = deepcopy(first)
        nonfinite["profiles"][0]["selectors"][0]["trace"]["line_hits"][0][
            "hits"
        ] = math.nan
        valid, errors = (
            statement_coverage.verify_claim_scoped_statement_coverage_document(
                nonfinite,
                self.plan,
                self.catalog,
                self.mutation_result,
            )
        )
        self.assertFalse(valid)
        self.assertTrue(errors)

        wrong_type = deepcopy(first)
        wrong_type["profiles"] = {"strong": wrong_type["profiles"][0]}
        valid, errors = (
            statement_coverage.verify_claim_scoped_statement_coverage_document(
                wrong_type,
                self.plan,
                self.catalog,
                self.mutation_result,
            )
        )
        self.assertFalse(valid)
        self.assertTrue(errors)

    def test_schema_is_strict_and_public_artifact_is_safe(self) -> None:
        result = self._run()
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )
        self.assertIs(schema["additionalProperties"], False)
        self.assertEqual(set(schema["required"]), _ROOT_FIELDS)
        self.assertEqual(set(schema["properties"]), _ROOT_FIELDS)
        self.assertEqual(
            schema["properties"]["schema_version"]["const"],
            statement_coverage.RESULT_SCHEMA_VERSION,
        )
        for node in _walk(schema):
            if isinstance(node, dict) and node.get("type") == "object":
                self.assertIs(node.get("additionalProperties"), False, node)

        encoded = json.dumps(result, sort_keys=True)
        for prohibited in (
            "def is_admin",
            "return user.get",
            "assertTrue",
            "assertFalse",
            "/tmp/",
            "\\Temp\\",
            "Traceback (most recent call last)",
            '"stdout"',
            '"stderr"',
            "credential",
            "environment_values",
            "private_endpoint",
        ):
            self.assertNotIn(prohibited, encoded)


if __name__ == "__main__":
    unittest.main()
