from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from deltawitness.dw001_claim_relevant_path_plan import (
    DW001ClaimRelevantPathPlanError,
    build_claim_relevant_path_catalog,
    build_claim_relevant_path_plan,
    build_claim_relevant_path_prior_art_log,
    compute_claim_relevant_path_catalog_sha256,
    compute_claim_relevant_path_plan_sha256,
    compute_claim_relevant_path_prior_art_sha256,
    load_claim_relevant_path_plan,
    verify_claim_relevant_path_catalog_document,
    verify_claim_relevant_path_plan_document,
    verify_claim_relevant_path_prior_art_log_document,
)


class DW001ClaimRelevantPathAdversarialTests(unittest.TestCase):
    def setUp(self) -> None:
        self.plan = build_claim_relevant_path_plan()
        self.catalog = build_claim_relevant_path_catalog(self.plan)
        self.prior = build_claim_relevant_path_prior_art_log(self.plan, self.catalog)

    @staticmethod
    def reseal_plan(document: dict[str, object]) -> None:
        document["plan_sha256"] = compute_claim_relevant_path_plan_sha256(document)

    @staticmethod
    def reseal_catalog(document: dict[str, object]) -> None:
        document["catalog_sha256"] = compute_claim_relevant_path_catalog_sha256(document)

    @staticmethod
    def reseal_prior(document: dict[str, object]) -> None:
        document["log_sha256"] = compute_claim_relevant_path_prior_art_sha256(document)

    def assert_plan_rejected(self, document: object) -> None:
        valid, errors = verify_claim_relevant_path_plan_document(document)
        self.assertIs(valid, False)
        self.assertTrue(errors)

    def test_digest_valid_route_membership_substitution_is_rejected(self) -> None:
        changed = deepcopy(self.plan)
        changed["cells"][0]["decision_route"] = "normalized"
        self.reseal_plan(changed)
        self.assert_plan_rejected(changed)

    def test_digest_valid_selector_role_substitution_is_rejected(self) -> None:
        changed = deepcopy(self.plan)
        changed["cells"][0]["claim_selector"] = changed["cells"][0][
            "collateral_reference_selector"
        ]
        self.reseal_plan(changed)
        self.assert_plan_rejected(changed)

    def test_digest_valid_cell_reordering_is_rejected(self) -> None:
        changed = deepcopy(self.plan)
        changed["cells"][0], changed["cells"][1] = (
            changed["cells"][1],
            changed["cells"][0],
        )
        self.reseal_plan(changed)
        self.assert_plan_rejected(changed)

    def test_digest_valid_influence_edge_substitution_is_rejected(self) -> None:
        changed = deepcopy(self.plan)
        changed["influence_control"]["edges"][0] = [
            "collateral_route",
            "allowed",
        ]
        self.reseal_plan(changed)
        self.assert_plan_rejected(changed)

    def test_digest_valid_expected_matrix_substitution_is_rejected(self) -> None:
        changed = deepcopy(self.plan)
        changed["expected_execution_matrix"][0]["selector_outcomes"][0][
            "expected_claim_observed"
        ] = "pass"
        self.reseal_plan(changed)
        self.assert_plan_rejected(changed)

    def test_extra_missing_and_wrong_type_fields_fail_closed(self) -> None:
        extra = deepcopy(self.plan)
        extra["escape_hatch"] = True
        self.assert_plan_rejected(extra)

        missing = deepcopy(self.plan)
        del missing["policy"]
        self.assert_plan_rejected(missing)

        wrong_type = deepcopy(self.plan)
        wrong_type["execution_authorized"] = 0
        self.reseal_plan(wrong_type)
        self.assert_plan_rejected(wrong_type)

    def test_catalog_status_and_outcome_injection_are_rejected_when_resealed(self) -> None:
        changed = deepcopy(self.catalog)
        changed["implementations"][5]["status"] = "generated"
        self.reseal_catalog(changed)
        valid, errors = verify_claim_relevant_path_catalog_document(
            changed,
            self.plan,
        )
        self.assertIs(valid, False)
        self.assertTrue(errors)

        injected = deepcopy(self.catalog)
        injected["implementations"][0]["outcome"] = "killed"
        self.reseal_catalog(injected)
        valid, errors = verify_claim_relevant_path_catalog_document(
            injected,
            self.plan,
        )
        self.assertIs(valid, False)
        self.assertTrue(errors)

    def test_catalog_duplicate_binding_substitution_is_rejected(self) -> None:
        changed = deepcopy(self.catalog)
        changed["implementations"][4]["duplicate_of"] = "0" * 64
        self.reseal_catalog(changed)
        valid, errors = verify_claim_relevant_path_catalog_document(
            changed,
            self.plan,
        )
        self.assertIs(valid, False)
        self.assertTrue(errors)

    def test_prior_art_novelty_promotion_is_rejected_when_resealed(self) -> None:
        changed = deepcopy(self.prior)
        changed["novelty_boundary"]["novelty_status"] = "established"
        changed["novelty_boundary"]["scientific_novelty_claim_allowed"] = True
        self.reseal_prior(changed)
        valid, errors = verify_claim_relevant_path_prior_art_log_document(
            changed,
            self.plan,
            self.catalog,
        )
        self.assertIs(valid, False)
        self.assertTrue(errors)

    def test_prior_art_source_reordering_is_rejected_when_resealed(self) -> None:
        changed = deepcopy(self.prior)
        changed["sources"].reverse()
        self.reseal_prior(changed)
        valid, errors = verify_claim_relevant_path_prior_art_log_document(
            changed,
            self.plan,
            self.catalog,
        )
        self.assertIs(valid, False)
        self.assertTrue(errors)

    def test_substituted_plan_cannot_generate_a_catalog(self) -> None:
        changed = deepcopy(self.plan)
        changed["source_scope"]["source_sha256"] = "0" * 64
        self.reseal_plan(changed)
        with self.assertRaises(DW001ClaimRelevantPathPlanError):
            build_claim_relevant_path_catalog(changed)

    def test_loader_rejects_symlink_directory_duplicate_keys_and_malformed_utf8(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            valid_path = root / "plan.json"
            valid_path.write_text(
                json.dumps(self.plan, separators=(",", ":")),
                encoding="utf-8",
            )
            link = root / "link.json"
            try:
                link.symlink_to(valid_path)
            except (OSError, NotImplementedError):
                link = None
            if link is not None:
                with self.assertRaises(DW001ClaimRelevantPathPlanError):
                    load_claim_relevant_path_plan(link)

            with self.assertRaises(DW001ClaimRelevantPathPlanError):
                load_claim_relevant_path_plan(root)

            duplicate = root / "duplicate.json"
            duplicate.write_text(
                '{"schema_version":"x","schema_version":"y"}',
                encoding="utf-8",
            )
            with self.assertRaises(DW001ClaimRelevantPathPlanError):
                load_claim_relevant_path_plan(duplicate)

            malformed = root / "malformed.json"
            malformed.write_bytes(b"{\xff}")
            with self.assertRaises(DW001ClaimRelevantPathPlanError):
                load_claim_relevant_path_plan(malformed)

    def test_verifiers_return_typed_fail_closed_results_for_non_objects(self) -> None:
        for value in (None, [], "x", 0, True):
            valid, errors = verify_claim_relevant_path_plan_document(value)
            self.assertIs(valid, False)
            self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
