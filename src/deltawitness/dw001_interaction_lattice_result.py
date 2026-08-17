"""Public scaffold for the frozen DW-001 interaction-lattice result.

The separately authorized execution protocol exists and is verifiable. The
result runner and verifier remain deliberately unavailable until the normative
red-first contract has been retained in CI.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from pathlib import Path
import stat
from typing import Any, Mapping, Sequence

from .errors import DeltaWitnessError
from .reporting import load_report, sha256_document


RESULT_SCHEMA_VERSION = (
    "deltawitness.dw001-interaction-witness-lattice-result.v1"
)
RESULT_ID = "DW-001-INTERACTION-WITNESS-LATTICE-RESULT-V1"
EXECUTION_PROTOCOL_SHA256 = (
    "e10a9e287555ee8a1b8c0a9b7768d2f949c04a70081a778d51fefb78c1276912"
)
PLAN_SHA256 = (
    "a79a500feb94c8ad78fe4633f9ca176465113de6297db2d07b2d005f5318e1f1"
)
CATALOG_SHA256 = (
    "2b06a86180a45fcd495c0bcf39365dde0cb590507e9a3528714f9ef58526308e"
)
PRIOR_ART_LOG_SHA256 = (
    "af6cb9782ea01a0e58baed8cfc1a4895dc1a53ed934498b307c6b05e8634c44f"
)
_PATH_MULTISET_SCHEMA_VERSION = (
    "deltawitness.dw001-interaction-result-path-multiset.v1"
)
_MAX_RESULT_BYTES = 4_000_000


class DW001InteractionLatticeResultError(DeltaWitnessError):
    """Raised when the frozen interaction-lattice result cannot be produced."""


def _semantic_view(document: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(document)
    normalized["created_at"] = None
    normalized["runtime"] = None
    normalized["semantic_sha256"] = None
    normalized["report_sha256"] = None
    return normalized


def compute_interaction_lattice_result_semantic_sha256(
    document: dict[str, Any],
) -> str:
    """Hash stable result semantics once the runner is implemented."""

    if not isinstance(document, dict):
        raise DW001InteractionLatticeResultError(
            "interaction-lattice result must be an object"
        )
    return sha256_document(_semantic_view(document))


def compute_interaction_lattice_result_report_sha256(
    document: dict[str, Any],
) -> str:
    """Hash the complete result with only its report digest normalized."""

    if not isinstance(document, dict):
        raise DW001InteractionLatticeResultError(
            "interaction-lattice result must be an object"
        )
    normalized = deepcopy(document)
    normalized["report_sha256"] = None
    return sha256_document(normalized)


def build_anonymous_result_path_multiset(
    path_records: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    """Build an order-independent path multiset with explicit multiplicity."""

    digests: list[str] = []
    for index, record in enumerate(path_records):
        if not isinstance(record, Mapping):
            raise DW001InteractionLatticeResultError(
                f"path record {index} must be an object"
            )
        digest = record.get("path_shape_sha256")
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest)
        ):
            raise DW001InteractionLatticeResultError(
                f"path record {index}.path_shape_sha256 is invalid"
            )
        digests.append(digest)
    counts = Counter(digests)
    records = [
        {"path_shape_sha256": digest, "count": counts[digest]}
        for digest in sorted(counts)
    ]
    return {
        "multiplicity_semantics": "multiset",
        "records": records,
        "anonymous_path_multiset_sha256": sha256_document(
            {
                "schema_version": _PATH_MULTISET_SCHEMA_VERSION,
                "records": records,
            }
        ),
    }


def _execute_candidate_selector(**kwargs: object) -> dict[str, Any]:
    """Stable executor seam for the retained red-first negative tests."""

    raise DW001InteractionLatticeResultError(
        "candidate selector execution is intentionally not implemented"
    )


def _execute_mutant_selector(**kwargs: object) -> dict[str, Any]:
    """Stable mutant executor seam for the retained red-first negative tests."""

    raise DW001InteractionLatticeResultError(
        "mutant selector execution is intentionally not implemented"
    )


def run_interaction_witness_lattice_result(
    execution_protocol: object,
    plan: object,
    catalog: object,
    prior_art: object,
    coveragepy_manifest: object,
    pr46_result: object,
) -> dict[str, Any]:
    """Execute the exact fixed experiment after red evidence is retained."""

    raise DW001InteractionLatticeResultError(
        "interaction-witness lattice result is intentionally not implemented"
    )


def verify_interaction_witness_lattice_result_document(
    document: object,
    execution_protocol: object,
    plan: object,
    catalog: object,
    prior_art: object,
    coveragepy_manifest: object,
    pr46_result: object,
) -> tuple[bool, tuple[str, ...]]:
    """Verify one result after the red-first contract is retained."""

    return False, (
        "interaction-witness lattice result is intentionally not implemented",
    )


def load_interaction_witness_lattice_result(
    path: Path,
    execution_protocol: object,
    plan: object,
    catalog: object,
    prior_art: object,
    coveragepy_manifest: object,
    pr46_result: object,
) -> dict[str, Any]:
    """Strict-load one bounded regular non-link result and verify it."""

    try:
        metadata = path.lstat()
    except OSError as exc:
        raise DW001InteractionLatticeResultError(
            "interaction-lattice result path cannot be inspected"
        ) from exc
    if path.is_symlink() or not stat.S_ISREG(metadata.st_mode):
        raise DW001InteractionLatticeResultError(
            "interaction-lattice result path must be a regular non-link file"
        )
    if metadata.st_size <= 0 or metadata.st_size > _MAX_RESULT_BYTES:
        raise DW001InteractionLatticeResultError(
            "interaction-lattice result path is outside the size limit"
        )
    document = load_report(path)
    valid, errors = verify_interaction_witness_lattice_result_document(
        document,
        execution_protocol,
        plan,
        catalog,
        prior_art,
        coveragepy_manifest,
        pr46_result,
    )
    if not valid:
        raise DW001InteractionLatticeResultError("; ".join(errors))
    return document


__all__ = [
    "CATALOG_SHA256",
    "DW001InteractionLatticeResultError",
    "EXECUTION_PROTOCOL_SHA256",
    "PLAN_SHA256",
    "PRIOR_ART_LOG_SHA256",
    "RESULT_ID",
    "RESULT_SCHEMA_VERSION",
    "build_anonymous_result_path_multiset",
    "compute_interaction_lattice_result_report_sha256",
    "compute_interaction_lattice_result_semantic_sha256",
    "load_interaction_witness_lattice_result",
    "run_interaction_witness_lattice_result",
    "verify_interaction_witness_lattice_result_document",
]
