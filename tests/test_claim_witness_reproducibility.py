from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from deltawitness.claim_witness import (
    build_claim_witness_declaration,
    run_claim_witness_localization,
)
from deltawitness.config import load_config
from deltawitness.dw001_scenarios import (
    build_fixture_descriptor,
    materialize_synthetic_fixture,
)
from deltawitness.matrix import verify_repository, write_report
from deltawitness.reporting import load_report, verify_report_document
from claim_witness_support import CLAIM_ID, VALID_SELECTOR


class ClaimWitnessReproducibilityTests(unittest.TestCase):
    def test_equivalent_fresh_checkout_does_not_depend_on_directory_name(self) -> None:
        descriptor = build_fixture_descriptor(
            scenario_id="claim-witness-fresh-checkout-001",
            family_id="valid-discriminating-regression",
            observer="outcome-receipt-v1",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first_repo = root / "producer-checkout"
            second_repo = root / "independent-directory-name"
            first_identity = materialize_synthetic_fixture(descriptor, first_repo)
            second_identity = materialize_synthetic_fixture(descriptor, second_repo)
            self.assertEqual(first_identity, second_identity)

            first_config = load_config(
                first_repo / first_identity["specification"]["path"]
            )
            second_config = load_config(
                second_repo / second_identity["specification"]["path"]
            )
            report = verify_repository(
                first_repo,
                first_identity["git"]["base_commit_sha"],
                first_identity["git"]["head_commit_sha"],
                first_config,
            )
            report_path = first_repo / ".git" / "deltawitness" / "source.json"
            write_report(report, report_path)
            source_report = load_report(report_path)
            valid, errors = verify_report_document(source_report)
            self.assertTrue(valid, errors)

            declaration = build_claim_witness_declaration(
                spec_sha256=first_config.digest_sha256,
                claim_id=CLAIM_ID,
                selectors=[VALID_SELECTOR],
            )
            first = run_claim_witness_localization(
                first_repo,
                first_config,
                source_report,
                declaration,
            )
            second = run_claim_witness_localization(
                second_repo,
                second_config,
                source_report,
                declaration,
            )

        self.assertEqual(first["aggregate_status"], "supported")
        self.assertEqual(second["aggregate_status"], "supported")
        self.assertEqual(
            first["localization_sha256"],
            second["localization_sha256"],
        )


if __name__ == "__main__":
    unittest.main()
