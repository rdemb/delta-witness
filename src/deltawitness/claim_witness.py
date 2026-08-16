"""Public API for declared logical-test witness localization.

The implementation lives in :mod:`deltawitness._claim_witness`. Before
execution, this boundary deterministically reconstructs every canonical matrix
state object referenced by the source report. Equivalent fresh checkouts can
therefore localize the same evidence without reusing the producer repository's
unreferenced synthetic Git objects.

The layer records exact operator-declared selector execution under BC and CC;
it does not establish semantic oracle relevance.
"""

from pathlib import Path
from typing import Any

from . import _claim_witness as _core
from ._claim_witness_states import materialize_source_report_states
from .config import WitnessConfig

ADAPTER_ID = _core.ADAPTER_ID
ADAPTER_VERSION = _core.ADAPTER_VERSION
AGGREGATE_RULE = _core.AGGREGATE_RULE
DECLARATION_SCHEMA_VERSION = _core.DECLARATION_SCHEMA_VERSION
LOCALIZATION_SCHEMA_VERSION = _core.LOCALIZATION_SCHEMA_VERSION
ClaimWitnessError = _core.ClaimWitnessError
build_claim_witness_declaration = _core.build_claim_witness_declaration
canonical_unittest_selector_command = _core.canonical_unittest_selector_command
compute_claim_witness_declaration_sha256 = (
    _core.compute_claim_witness_declaration_sha256
)
compute_claim_witness_localization_report_sha256 = (
    _core.compute_claim_witness_localization_report_sha256
)
compute_claim_witness_localization_sha256 = (
    _core.compute_claim_witness_localization_sha256
)
verify_claim_witness_declaration_document = (
    _core.verify_claim_witness_declaration_document
)
verify_claim_witness_localization_document = (
    _core.verify_claim_witness_localization_document
)


def run_claim_witness_localization(
    repo: Path,
    config: WitnessConfig,
    source_report: object,
    declaration: object,
) -> dict[str, Any]:
    """Reconstruct source states, then execute the verified BC/CC localization."""

    materialize_source_report_states(repo, config, source_report)
    return _core.run_claim_witness_localization(
        repo,
        config,
        source_report,
        declaration,
    )


__all__ = [
    "ADAPTER_ID",
    "ADAPTER_VERSION",
    "AGGREGATE_RULE",
    "DECLARATION_SCHEMA_VERSION",
    "LOCALIZATION_SCHEMA_VERSION",
    "ClaimWitnessError",
    "build_claim_witness_declaration",
    "canonical_unittest_selector_command",
    "compute_claim_witness_declaration_sha256",
    "compute_claim_witness_localization_report_sha256",
    "compute_claim_witness_localization_sha256",
    "run_claim_witness_localization",
    "verify_claim_witness_declaration_document",
    "verify_claim_witness_localization_document",
]
