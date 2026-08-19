from __future__ import annotations

import unittest

from deltawitness.dw001_claim_relevant_path_execution import (
    build_claim_relevant_path_execution_manifest,
)


class DW001ClaimRelevantPathExecutionRedFirstTests(unittest.TestCase):
    def test_frozen_execution_manifest_exists_before_any_result_execution(self) -> None:
        manifest = build_claim_relevant_path_execution_manifest()
        self.assertEqual(
            manifest["execution_status"],
            "protocol_frozen_execution_disabled",
        )
        self.assertIs(manifest["execution_authorized"], False)


if __name__ == "__main__":
    unittest.main()
