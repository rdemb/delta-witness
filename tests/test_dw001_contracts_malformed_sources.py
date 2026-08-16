from __future__ import annotations

import unittest

from deltawitness.dw001_contracts import verify_result_against_sources


class DW001MalformedCrossArtifactTests(unittest.TestCase):
    def test_malformed_object_roots_fail_closed_without_key_error(self) -> None:
        valid, errors = verify_result_against_sources({}, {}, {})

        self.assertFalse(valid)
        self.assertTrue(errors)
        self.assertTrue(
            any("field mismatch" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
