"""Public API for declared logical-test witness localization.

The implementation lives in :mod:`deltawitness._claim_witness`. The layer is
optional and records exact operator-declared selector execution under BC and CC;
it does not establish semantic oracle relevance.
"""

from ._claim_witness import (
    ADAPTER_ID,
    ADAPTER_VERSION,
    AGGREGATE_RULE,
    DECLARATION_SCHEMA_VERSION,
    LOCALIZATION_SCHEMA_VERSION,
    ClaimWitnessError,
    build_claim_witness_declaration,
    canonical_unittest_selector_command,
    compute_claim_witness_declaration_sha256,
    compute_claim_witness_localization_report_sha256,
    compute_claim_witness_localization_sha256,
    run_claim_witness_localization,
    verify_claim_witness_declaration_document,
    verify_claim_witness_localization_document,
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
