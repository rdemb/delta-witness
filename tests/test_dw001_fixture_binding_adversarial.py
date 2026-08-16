from __future__ import annotations

from copy import deepcopy
import unittest

from deltawitness.dw001_contracts import verify_scenario_manifest_document
from deltawitness.dw001_fixture_binding import (
    DW001FixtureBindingError,
    build_fixture_manifest_binding,
    compute_fixture_manifest_binding_sha256,
    verify_fixture_manifest_binding_document,
)
from deltawitness.dw001_scenarios import (
    build_fixture_descriptor,
    compute_fixture_identity_sha256,
    verify_fixture_identity_document,
)
from dw001_binding_support import artifacts, resign_manifest


class DW001FixtureManifestBindingAdversarialTests(unittest.TestCase):
    def test_manifest_from_different_fixture_with_same_scenario_is_rejected(self) -> None:
        descriptor, identity, _ = artifacts(
            scenario_id="fixture-binding-collision-001",
            family_id="valid-discriminating-regression",
        )
        _, _, other_manifest = artifacts(
            scenario_id="fixture-binding-collision-001",
            family_id="non-discriminating-candidate-test",
        )

        with self.assertRaisesRegex(
            DW001FixtureBindingError,
            "scenario manifest.*does not match",
        ):
            build_fixture_manifest_binding(descriptor, identity, other_manifest)

    def test_specification_digest_tampering_is_rejected_even_after_resigning_identity(self) -> None:
        descriptor, identity, manifest = artifacts()
        tampered_identity = deepcopy(identity)
        tampered_identity["specification"]["sha256"] = "f" * 64
        tampered_identity["identity_sha256"] = compute_fixture_identity_sha256(
            tampered_identity
        )

        identity_valid, identity_errors = verify_fixture_identity_document(
            tampered_identity,
            descriptor,
        )
        self.assertFalse(identity_valid, identity_errors)
        self.assertTrue(
            any("specification" in error for error in identity_errors),
            identity_errors,
        )
        with self.assertRaisesRegex(
            DW001FixtureBindingError,
            "fixture identity",
        ):
            build_fixture_manifest_binding(
                descriptor,
                tampered_identity,
                manifest,
            )

    def test_manifest_path_drift_is_rejected_after_manifest_resigning(self) -> None:
        descriptor, identity, manifest = artifacts()
        tampered_manifest = deepcopy(manifest)
        tampered_manifest["paths"]["documentation"] = ["study.toml"]
        resign_manifest(tampered_manifest)
        manifest_valid, manifest_errors = verify_scenario_manifest_document(
            tampered_manifest
        )
        self.assertTrue(manifest_valid, manifest_errors)

        with self.assertRaisesRegex(
            DW001FixtureBindingError,
            "paths.*does not match",
        ):
            build_fixture_manifest_binding(
                descriptor,
                identity,
                tampered_manifest,
            )

    def test_relabelled_descriptor_and_identity_do_not_bind_original_manifest(self) -> None:
        descriptor, identity, manifest = artifacts(
            scenario_id="fixture-binding-relabel-001",
            family_id="valid-discriminating-regression",
        )
        relabelled_descriptor = build_fixture_descriptor(
            scenario_id="fixture-binding-relabel-001",
            family_id="non-discriminating-candidate-test",
        )
        relabelled_identity = deepcopy(identity)
        for field in (
            "family_id",
            "control_role",
            "descriptor_sha256",
            "expected_states",
            "expected_methods",
        ):
            relabelled_identity[field] = deepcopy(relabelled_descriptor[field])
        relabelled_identity["identity_sha256"] = compute_fixture_identity_sha256(
            relabelled_identity
        )
        identity_valid, identity_errors = verify_fixture_identity_document(
            relabelled_identity,
            relabelled_descriptor,
        )
        self.assertTrue(identity_valid, identity_errors)

        with self.assertRaisesRegex(
            DW001FixtureBindingError,
            "ground truth.*does not match",
        ):
            build_fixture_manifest_binding(
                relabelled_descriptor,
                relabelled_identity,
                manifest,
            )

    def test_manifest_ground_truth_drift_is_rejected_after_resigning(self) -> None:
        descriptor, identity, manifest = artifacts()
        tampered_manifest = deepcopy(manifest)
        state = tampered_manifest["ground_truth"]["states"][1]
        state["expected_observed"] = "pass"
        state["failure_cause"] = "none"
        for method in tampered_manifest["ground_truth"]["methods"]:
            if method["method_id"] != "M0_FINAL":
                method["expected_decision"] = "reject"
                method["reason_code"] = "predicate_contradicted"
        resign_manifest(tampered_manifest)
        manifest_valid, manifest_errors = verify_scenario_manifest_document(
            tampered_manifest
        )
        self.assertTrue(manifest_valid, manifest_errors)

        with self.assertRaisesRegex(
            DW001FixtureBindingError,
            "ground truth.*does not match",
        ):
            build_fixture_manifest_binding(
                descriptor,
                identity,
                tampered_manifest,
            )

    def test_manifest_observer_drift_is_rejected(self) -> None:
        descriptor, identity, manifest = artifacts(
            scenario_id="fixture-binding-observer-001",
            observer="outcome-receipt-v1",
        )
        tampered_manifest = deepcopy(manifest)
        execution = tampered_manifest["execution"]
        execution["observer"] = "exit-code-v1"
        execution["observer_id"] = "O0_EXIT_CODE"
        execution["command"] = [
            "python",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
        ]
        tampered_manifest["ground_truth"]["states"][1][
            "failure_cause"
        ] = "test_failure_untyped"
        for method in tampered_manifest["ground_truth"]["methods"]:
            method["observer_id"] = "O0_EXIT_CODE"
            method["combined_method_id"] = (
                f"{method['method_id']}__O0_EXIT_CODE"
            )
        resign_manifest(tampered_manifest)
        manifest_valid, manifest_errors = verify_scenario_manifest_document(
            tampered_manifest
        )
        self.assertTrue(manifest_valid, manifest_errors)

        with self.assertRaisesRegex(
            DW001FixtureBindingError,
            "observer.*does not match",
        ):
            build_fixture_manifest_binding(
                descriptor,
                identity,
                tampered_manifest,
            )

    def test_recomputed_binding_digest_cannot_hide_relation_mismatch(self) -> None:
        descriptor, identity, manifest = artifacts()
        binding = build_fixture_manifest_binding(descriptor, identity, manifest)
        tampered = deepcopy(binding)
        tampered["sources"]["scenario_manifest"]["sha256"] = "f" * 64
        tampered["binding_sha256"] = compute_fixture_manifest_binding_sha256(
            tampered
        )

        valid, errors = verify_fixture_manifest_binding_document(
            tampered,
            descriptor,
            identity,
            manifest,
        )
        self.assertFalse(valid)
        self.assertTrue(
            any("does not match supplied source artifacts" in error for error in errors),
            errors,
        )

    def test_malformed_source_documents_fail_closed_with_typed_diagnostics(self) -> None:
        descriptor, identity, manifest = artifacts()
        binding = build_fixture_manifest_binding(descriptor, identity, manifest)

        for label, malformed_descriptor, malformed_identity, malformed_manifest in (
            ("descriptor", [], identity, manifest),
            ("identity", descriptor, [], manifest),
            ("manifest", descriptor, identity, []),
        ):
            with self.subTest(source=label):
                valid, errors = verify_fixture_manifest_binding_document(
                    binding,
                    malformed_descriptor,
                    malformed_identity,
                    malformed_manifest,
                )
                self.assertFalse(valid)
                self.assertTrue(errors)
                self.assertTrue(
                    any(label in error for error in errors),
                    errors,
                )

    def test_private_or_absolute_path_fields_are_rejected_after_resigning(self) -> None:
        descriptor, identity, manifest = artifacts()
        binding = build_fixture_manifest_binding(descriptor, identity, manifest)
        private_root = "/" + "private"
        tampered = deepcopy(binding)
        tampered["specification"]["path"] = (
            f"{private_root}/fixture/deltawitness.toml"
        )
        tampered["binding_sha256"] = compute_fixture_manifest_binding_sha256(
            tampered
        )

        valid, errors = verify_fixture_manifest_binding_document(
            tampered,
            descriptor,
            identity,
            manifest,
        )
        self.assertFalse(valid)
        self.assertTrue(
            any("safe repository-relative" in error for error in errors),
            errors,
        )

        extra = deepcopy(binding)
        extra["local_path"] = f"{private_root}/fixture/repository"
        extra["binding_sha256"] = compute_fixture_manifest_binding_sha256(extra)
        valid, errors = verify_fixture_manifest_binding_document(
            extra,
            descriptor,
            identity,
            manifest,
        )
        self.assertFalse(valid)
        self.assertTrue(any("field mismatch" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
