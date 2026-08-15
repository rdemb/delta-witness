from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from deltawitness.config import load_config
from deltawitness.errors import ConfigurationError


VALID = b"""
[paths]
code = ["src/**"]
tests = ["tests/**"]
documentation = ["README.md"]

[execution]
pass_env = ["DW_TEST_FLAG"]

[[claim]]
id = "regression"
description = "candidate tests expose the old defect"
command = ["python", "-m", "unittest"]
timeout_seconds = 60

[claim.expect]
base_base = "pass"
base_candidate = "fail"
candidate_base = "pass"
candidate_candidate = "pass"
"""


class ConfigTests(unittest.TestCase):
    def _load(self, raw: bytes):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "deltawitness.toml"
            path.write_bytes(raw)
            return load_config(path)

    def test_loads_valid_configuration(self) -> None:
        config = self._load(VALID)
        self.assertEqual(config.path_policy.code_globs, ("src/**",))
        self.assertEqual(config.claims[0].claim_id, "regression")
        self.assertEqual(config.claims[0].expectations["base_candidate"], "fail")
        self.assertEqual(config.execution_policy.pass_env, ("DW_TEST_FLAG",))
        self.assertEqual(config.claims[0].observer, "exit-code-v1")
        self.assertEqual(config.claims[0].pass_exit_codes, (0,))
        self.assertEqual(config.claims[0].fail_exit_codes, (1,))
        self.assertEqual(len(config.digest_sha256), 64)

    def test_accepts_typed_outcome_receipt_observer(self) -> None:
        custom = VALID.replace(
            b'description = "candidate tests expose the old defect"',
            b'description = "candidate tests expose the old defect"\nobserver = "outcome-receipt-v1"',
        )
        config = self._load(custom)
        self.assertEqual(config.claims[0].observer, "outcome-receipt-v1")

    def test_rejects_unknown_observer(self) -> None:
        invalid = VALID.replace(
            b'description = "candidate tests expose the old defect"',
            b'description = "candidate tests expose the old defect"\nobserver = "trust-me-v1"',
        )
        with self.assertRaises(ConfigurationError):
            self._load(invalid)

    def test_rejects_unknown_expectation(self) -> None:
        invalid = VALID.replace(b'base_candidate = "fail"', b'base_candidate = "maybe"')
        with self.assertRaises(ConfigurationError):
            self._load(invalid)

    def test_requires_every_state_to_be_explicit(self) -> None:
        invalid = VALID.replace(b'candidate_base = "pass"\n', b"")
        with self.assertRaises(ConfigurationError):
            self._load(invalid)

    def test_rejects_unknown_top_level_key(self) -> None:
        invalid = VALID + b"\nmarketing_score = 100\n"
        with self.assertRaises(ConfigurationError):
            self._load(invalid)

    def test_rejects_unsafe_claim_identifier(self) -> None:
        invalid = VALID.replace(b'id = "regression"', b'id = "Regression Claim"')
        with self.assertRaises(ConfigurationError):
            self._load(invalid)

    def test_rejects_parent_traversal_glob(self) -> None:
        invalid = VALID.replace(b'code = ["src/**"]', b'code = ["../src/**"]')
        with self.assertRaises(ConfigurationError):
            self._load(invalid)

    def test_rejects_overlapping_exit_code_classes(self) -> None:
        invalid = VALID.replace(
            b'timeout_seconds = 60',
            b'timeout_seconds = 60\npass_exit_codes = [0, 1]\nfail_exit_codes = [1]',
        )
        with self.assertRaises(ConfigurationError):
            self._load(invalid)

    def test_accepts_explicit_nonstandard_failure_code(self) -> None:
        custom = VALID.replace(
            b'timeout_seconds = 60',
            b'timeout_seconds = 60\nfail_exit_codes = [3, 101]',
        )
        config = self._load(custom)
        self.assertEqual(config.claims[0].fail_exit_codes, (3, 101))


if __name__ == "__main__":
    unittest.main()
