from __future__ import annotations

import os
import unittest

from deltawitness.reporting import canonical_json, sha256_document


class ReportingTests(unittest.TestCase):
    @unittest.skipIf(os.name != "posix", "surrogateescape path semantics are POSIX-specific")
    def test_canonical_json_handles_non_utf8_git_path_bytes(self) -> None:
        path = os.fsdecode(b"tests/non-utf8-\xff.py")

        encoded = canonical_json({"path": path})

        self.assertIn(b"\\udcff", encoded)
        self.assertEqual(sha256_document({"path": path}), sha256_document({"path": path}))


if __name__ == "__main__":
    unittest.main()
