"""Red-first boundary for DW-001 claim-relevant path execution v1.

This module intentionally exposes no executor.  The first regression commit records
that the result-bearing protocol has not yet been frozen or implemented.  Candidate,
selector, Coverage.py, fault, influence, and synthetic-target execution remain
unauthorized at this revision.
"""

from __future__ import annotations

from .errors import DeltaWitnessError


class DW001ClaimRelevantPathExecutionError(DeltaWitnessError):
    """Raised while the frozen execution protocol is unavailable or invalid."""


def build_claim_relevant_path_execution_manifest() -> dict[str, object]:
    """Fail at the retained red-first boundary before protocol implementation."""

    raise DW001ClaimRelevantPathExecutionError(
        "claim-relevant path execution protocol is intentionally not implemented"
    )


__all__ = [
    "DW001ClaimRelevantPathExecutionError",
    "build_claim_relevant_path_execution_manifest",
]
