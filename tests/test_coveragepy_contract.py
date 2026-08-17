from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest

from deltawitness.coveragepy_contract import (
    COVERAGEPY_MANIFEST_SHA256,
    COVERAGEPY_WHEEL_FILENAME,
    CoveragePyContractError,
    build_coveragepy_distribution_manifest,
    compute_coveragepy_manifest_sha256,
    verify_coveragepy_artifact,
    verify_coveragepy_distribution_manifest_document,
)
from deltawitness.reporting import load_report


_ROOT = Path(__file__).resolve().parents[1]
_MANIFEST_PATH = (
    _ROOT
    / "research"
    / "DW-001"
    / "coveragepy-7.15.2-artifact.v1.json"
)


class CoveragePyContractTests(unittest.TestCase):
    def test_committed_manifest_equals_the_reconstructed_contract(self) -> None:
        committed = load_report(_MANIFEST_PATH)
        expected = build_coveragepy_distribution_manifest()
        self.assertEqual(committed, expected)
        self.assertEqual(
            compute_coveragepy_manifest_sha256(committed),
            COVERAGEPY_MANIFEST_SHA256,
        )
        valid, errors = verify_coveragepy_distribution_manifest_document(
            committed
        )
        self.assertTrue(valid, errors)

    def test_json_object_member_order_is_non_semantic(self) -> None:
        expected = build_coveragepy_distribution_manifest()
        reordered = {
            key: deepcopy(expected[key]) for key in reversed(list(expected))
        }
        selected = reordered["selected_artifact"]
        reordered["selected_artifact"] = {
            key: selected[key] for key in reversed(list(selected))
        }

        valid, errors = verify_coveragepy_distribution_manifest_document(
            reordered
        )
        self.assertTrue(valid, errors)
        self.assertEqual(
            compute_coveragepy_manifest_sha256(reordered),
            COVERAGEPY_MANIFEST_SHA256,
        )

    def test_manifest_rejects_package_version_artifact_and_provenance_changes(self) -> None:
        changes = (
            ("version", "7.15.1"),
            ("selected_artifact.sha256", "f" * 64),
            ("selected_artifact.filename", "coverage-7.15.2.tar.gz"),
            ("candidate_sdist.selected", True),
            ("source.commit", "0" * 40),
            ("source.license", "unknown"),
            ("runtime_contract.base_runtime_dependency", True),
            ("runtime_contract.plugins_allowed", True),
            ("runtime_contract.auto_start_allowed", True),
            ("runtime_contract.measurement_network_allowed", True),
        )
        for dotted_path, value in changes:
            with self.subTest(field=dotted_path):
                tampered = deepcopy(build_coveragepy_distribution_manifest())
                current: dict[str, object] = tampered
                parts = dotted_path.split(".")
                for part in parts[:-1]:
                    next_value = current[part]
                    self.assertIsInstance(next_value, dict)
                    current = next_value  # type: ignore[assignment]
                current[parts[-1]] = value
                tampered["manifest_sha256"] = (
                    compute_coveragepy_manifest_sha256(tampered)
                )
                valid, errors = (
                    verify_coveragepy_distribution_manifest_document(tampered)
                )
                self.assertFalse(valid)
                self.assertTrue(errors)

    def test_manifest_rejects_reordered_supported_interpreters(self) -> None:
        tampered = deepcopy(build_coveragepy_distribution_manifest())
        versions = tampered["runtime_contract"][
            "supported_delta_witness_pythons"
        ]
        tampered["runtime_contract"][
            "supported_delta_witness_pythons"
        ] = list(reversed(versions))
        tampered["manifest_sha256"] = compute_coveragepy_manifest_sha256(
            tampered
        )

        valid, errors = verify_coveragepy_distribution_manifest_document(
            tampered
        )
        self.assertFalse(valid)
        self.assertTrue(errors)

    def test_base_dependency_list_remains_empty(self) -> None:
        document = tomllib.loads(
            (_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        )
        self.assertEqual(document["project"]["dependencies"], [])
        self.assertEqual(
            document["project"]["optional-dependencies"]["research"],
            ["coverage==7.15.2"],
        )

    def test_importing_the_contract_does_not_import_coverage(self) -> None:
        code = (
            "import sys; "
            "import deltawitness.coveragepy_contract; "
            "raise SystemExit(1 if 'coverage' in sys.modules else 0)"
        )
        completed = subprocess.run(
            [sys.executable, "-c", code],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            completed.stderr.decode("utf-8", errors="replace"),
        )

    def test_artifact_verifier_rejects_wrong_name_digest_and_symbolic_link(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            wrong_name = root / "coverage-7.15.2.tar.gz"
            wrong_name.write_bytes(b"not-the-reviewed-wheel")
            with self.assertRaisesRegex(
                CoveragePyContractError,
                "filename",
            ):
                verify_coveragepy_artifact(wrong_name)

            wrong_digest = root / COVERAGEPY_WHEEL_FILENAME
            wrong_digest.write_bytes(b"not-the-reviewed-wheel")
            with self.assertRaisesRegex(
                CoveragePyContractError,
                "SHA-256",
            ):
                verify_coveragepy_artifact(wrong_digest)

            linked = root / "linked"
            linked.mkdir()
            target = linked / COVERAGEPY_WHEEL_FILENAME
            target.write_bytes(b"not-the-reviewed-wheel")
            link = root / "wheel-link"
            link.symlink_to(target)
            with self.assertRaisesRegex(
                CoveragePyContractError,
                "regular non-link",
            ):
                verify_coveragepy_artifact(link)


if __name__ == "__main__":
    unittest.main()
