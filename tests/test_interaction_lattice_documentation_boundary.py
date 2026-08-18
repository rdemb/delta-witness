"""Regression checks for canonical interaction-result documentation boundaries."""

from __future__ import annotations

from pathlib import Path
import unittest


_ROOT = Path(__file__).resolve().parents[1]
_RESULT_SEMANTIC_SHA256 = (
    "bc2ab879595da61815a17dcc33a09c6334b93dea3fd464f2fe4a5437944ebb77"
)


class InteractionLatticeDocumentationBoundaryTests(unittest.TestCase):
    """Keep execution capability and result claims visible in canonical docs."""

    def test_canonical_documents_record_the_interaction_result_boundary(self) -> None:
        required_markers = {
            "README.md": (
                "## DW-001 selector-context interaction-lattice result",
                _RESULT_SEMANTIC_SHA256,
                "external repository execution remains unauthorized",
            ),
            "ROADMAP.md": (
                "Exact frozen selector-context interaction-lattice result executed from the merged preregistration",
                "Stable dependency-free interaction-result checkpoint",
            ),
            "docs/ARCHITECTURE.md": (
                "## Selector-context interaction-lattice result architecture",
                "24 exact selector commands",
                _RESULT_SEMANTIC_SHA256,
            ),
            "THREAT_MODEL.md": (
                "## Selector-context interaction-lattice result extension",
                "fixed project-owned synthetic bytes",
                "external repository execution remains unauthorized",
            ),
            "docs/PUBLICATION_POLICY.md": (
                "## Selector-context interaction-lattice result boundary",
                "public checkpoint",
                "diagnostic-only full result",
            ),
        }

        for relative_path, markers in required_markers.items():
            with self.subTest(path=relative_path):
                document = (_ROOT / relative_path).read_text(encoding="utf-8")
                for marker in markers:
                    self.assertIn(marker, document)


if __name__ == "__main__":
    unittest.main()
