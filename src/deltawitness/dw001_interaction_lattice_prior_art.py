"""Exact pre-execution prior-art boundary for the interaction lattice.

This module reconstructs the reviewed literature and direct-baseline log without
importing Coverage.py or executing the new source, tests, or mutants. The log
records established techniques and fixes novelty and policy claims to false
before result execution.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .errors import DeltaWitnessError
from .reporting import sha256_document


PRIOR_ART_LOG_SCHEMA_VERSION = (
    "deltawitness.dw001-interaction-witness-prior-art-log.v1"
)
PRIOR_ART_LOG_ID = "DW-001-INTERACTION-WITNESS-PRIOR-ART-LOG-V1"
PRIOR_ART_LOG_SHA256 = (
    "af6cb9782ea01a0e58baed8cfc1a4895dc1a53ed934498b307c6b05e8634c44f"
)

_LOG_TEMPLATE: dict[str, Any] = {
    "schema_version": PRIOR_ART_LOG_SCHEMA_VERSION,
    "study_id": "DW-001",
    "log_id": PRIOR_ART_LOG_ID,
    "status": "pre_execution_literature_boundary",
    "reviewed_at": "2026-08-17",
    "plan_id": "DW-001-INTERACTION-WITNESS-LATTICE-PLAN-V1",
    "plan_sha256": (
        "a79a500feb94c8ad78fe4633f9ca176465113de6297db2d07b2d005f5318e1f1"
    ),
    "catalog_sha256": (
        "2b06a86180a45fcd495c0bcf39365dde0cb590507e9a3528714f9ef58526308e"
    ),
    "search_protocol": {
        "source_priority": [
            "official-versioned-tool-documentation",
            "government-technical-report",
            "publisher-or-doi-primary-research",
            "authoritative-bibliographic-metadata",
        ],
        "queries": [
            "Coverage.py 7.15.2 measurement contexts public API arcs branch_stats",
            "modified condition decision coverage practical tutorial NASA",
            "combinatorial coverage measurement NISTIR 7878",
            "checked coverage oracle quality dynamic slicing",
            "equivalent mutants coverage mutation testing",
            "mutation testing survey",
            "test oracle problem survey",
        ],
        "inclusion_rule": (
            "Include primary or authoritative sources that directly define a "
            "baseline, measurement capability, known limitation, or validity "
            "threat relevant to selector-context partitions, condition "
            "interactions, oracle evidence, or mutation outcomes."
        ),
        "exclusion_rule": (
            "Exclude marketing summaries, unsourced claims, tooling comparisons "
            "without a stable primary source, and any source selected only after "
            "observing the planned experiment's outcomes."
        ),
        "systematic_review_complete": False,
        "search_frozen_before_result_execution": True,
    },
    "sources": [
        {
            "order": 1,
            "source_id": "coveragepy-7.15.2-measurement-contexts",
            "title": "Measurement contexts",
            "source_type": "official-versioned-tool-documentation",
            "publisher": "Coverage.py",
            "identifier": (
                "https://coverage.readthedocs.io/en/7.15.2/contexts.html"
            ),
            "direct_baseline_role": (
                "Defines static and dynamic context labels for associating "
                "measured execution with test or request identities."
            ),
            "boundary_for_this_work": (
                "Context labels partition measured data but do not establish "
                "oracle strength, condition independence, or fault detection."
            ),
        },
        {
            "order": 2,
            "source_id": "coveragepy-7.15.2-public-api",
            "title": "The Coverage class",
            "source_type": "official-versioned-tool-documentation",
            "publisher": "Coverage.py",
            "identifier": (
                "https://coverage.readthedocs.io/en/7.15.2/api_coverage.html"
            ),
            "direct_baseline_role": (
                "Defines the public APIs used for statement analysis, arcs, "
                "branch statistics, data access, and context filtering."
            ),
            "boundary_for_this_work": (
                "Public statement and arc evidence is structural execution "
                "evidence, not an oracle-adequacy or semantic-coverage measure."
            ),
        },
        {
            "order": 3,
            "source_id": "nasa-tm-2001-210876",
            "title": (
                "A Practical Tutorial on Modified Condition/Decision Coverage"
            ),
            "source_type": "government-technical-memorandum",
            "publisher": "NASA",
            "identifier": "NASA/TM-2001-210876",
            "url": "https://ntrs.nasa.gov/citations/20010057789",
            "direct_baseline_role": (
                "Defines the condition-independence reasoning used as the fixed "
                "two-condition truth-table control."
            ),
            "boundary_for_this_work": (
                "The planned mcdc-basis profile is one owned-synthetic control; "
                "DeltaWitness does not implement or certify general MC/DC."
            ),
        },
        {
            "order": 4,
            "source_id": "nistir-7878",
            "title": "Combinatorial Coverage Measurement",
            "source_type": "government-technical-report",
            "publisher": "NIST",
            "identifier": "10.6028/NIST.IR.7878",
            "url": "https://doi.org/10.6028/NIST.IR.7878",
            "direct_baseline_role": (
                "Defines coverage of t-way input/configuration combinations as "
                "a distinct state-space view from structural code coverage."
            ),
            "boundary_for_this_work": (
                "The four fixed Boolean quadrants are not a general covering-"
                "array implementation or a fault-detection estimate."
            ),
        },
        {
            "order": 5,
            "source_id": "kuhn-kacker-lei-2016",
            "title": (
                "Measuring and Specifying Combinatorial Coverage of Test Input "
                "Configurations"
            ),
            "source_type": "peer-reviewed-primary-research",
            "publisher": (
                "Innovations in Systems and Software Engineering"
            ),
            "identifier": "10.1007/s11334-015-0266-2",
            "url": "https://doi.org/10.1007/s11334-015-0266-2",
            "direct_baseline_role": (
                "Relates static combinatorial input coverage to dynamic code "
                "coverage and fault-detection capacity under stated conditions."
            ),
            "boundary_for_this_work": (
                "The planned experiment compares exact views in one control and "
                "does not estimate detection probability or required suite size."
            ),
        },
        {
            "order": 6,
            "source_id": "schuler-zeller-checked-coverage",
            "title": "Checked coverage: an indicator for oracle quality",
            "source_type": "peer-reviewed-primary-research",
            "publisher": "Software Testing, Verification and Reliability",
            "identifier": "10.1002/stvr.1497",
            "url": "https://doi.org/10.1002/stvr.1497",
            "direct_baseline_role": (
                "Uses dynamic slicing from covered statements to an oracle, "
                "demonstrating that ordinary structural coverage omits whether "
                "executed computation influences an assertion."
            ),
            "boundary_for_this_work": (
                "Selector-context path partitions do not compute dynamic slices "
                "and must not be presented as checked coverage."
            ),
        },
        {
            "order": 7,
            "source_id": "schuler-zeller-equivalent-mutants",
            "title": "Covering and Uncovering Equivalent Mutants",
            "source_type": "peer-reviewed-primary-research",
            "publisher": "Software Testing, Verification and Reliability",
            "identifier": "10.1002/stvr.1473",
            "url": "https://doi.org/10.1002/stvr.1473",
            "direct_baseline_role": (
                "Documents equivalent-mutant risk and investigates coverage "
                "changes as evidence for mutant non-equivalence."
            ),
            "boundary_for_this_work": (
                "Survival never proves equivalence; the fixed catalog retains "
                "invalid, duplicate, not-applicable, and indeterminate states."
            ),
        },
        {
            "order": 8,
            "source_id": "jia-harman-mutation-survey",
            "title": (
                "An Analysis and Survey of the Development of Mutation Testing"
            ),
            "source_type": "peer-reviewed-survey",
            "publisher": "IEEE Transactions on Software Engineering",
            "identifier": "10.1109/TSE.2010.62",
            "url": "https://doi.org/10.1109/TSE.2010.62",
            "direct_baseline_role": (
                "Surveys mutation operators, selective mutation, equivalence, "
                "cost, and empirical mutation-testing practice."
            ),
            "boundary_for_this_work": (
                "Five fixed fault controls are not a representative operator "
                "set, mutation score, or calibrated mutation system."
            ),
        },
        {
            "order": 9,
            "source_id": "barr-et-al-oracle-survey",
            "title": "The Oracle Problem in Software Testing: A Survey",
            "source_type": "peer-reviewed-survey",
            "publisher": "IEEE Transactions on Software Engineering",
            "identifier": "10.1109/TSE.2014.2372785",
            "url": "https://doi.org/10.1109/TSE.2014.2372785",
            "direct_baseline_role": (
                "Frames the general problem of determining correct expected "
                "behavior and the limits of automated test oracles."
            ),
            "boundary_for_this_work": (
                "The fixed truth table is project-owned ground truth for one "
                "control and does not solve the general oracle problem."
            ),
        },
    ],
    "closest_baselines": [
        {
            "order": 1,
            "baseline_id": "coveragepy-static-context-lines-and-arcs",
            "captures": (
                "Exact per-context executed lines and arcs through a mature "
                "public measurement API."
            ),
            "planned_direct_comparison": (
                "Compare profile-level union/intersection against a canonical "
                "multiset of per-selector line-and-arc path shapes."
            ),
            "not_claimed": (
                "No replacement for Coverage.py, path coverage, or context APIs."
            ),
        },
        {
            "order": 2,
            "baseline_id": "two-condition-mcdc-independence-control",
            "captures": (
                "Whether each Boolean condition is shown to independently "
                "affect the decision in the frozen truth table."
            ),
            "planned_direct_comparison": (
                "Compare exact MFA/role independence witnesses with dropped-"
                "conjunct mutant outcomes."
            ),
            "not_claimed": "No general MC/DC engine or certification claim.",
        },
        {
            "order": 3,
            "baseline_id": "combinatorial-input-coverage",
            "captures": (
                "Which t-way input or configuration combinations are represented."
            ),
            "planned_direct_comparison": (
                "Retain all four exact Boolean quadrants and five fixed subsets "
                "without converting them into a scalar coverage percentage."
            ),
            "not_claimed": (
                "No covering-array generation, residual-risk estimate, or "
                "population-level fault-detection capacity."
            ),
        },
        {
            "order": 4,
            "baseline_id": "checked-coverage-dynamic-slice",
            "captures": (
                "Covered computation that dynamically influences an oracle."
            ),
            "planned_direct_comparison": (
                "Use checked coverage as a boundary: path partitions retain "
                "per-selector control-flow co-occurrence but not data/control "
                "dependence to assertions."
            ),
            "not_claimed": (
                "No dynamic slicing or oracle-influence computation."
            ),
        },
        {
            "order": 5,
            "baseline_id": "typed-fixed-mutation-incidence",
            "captures": (
                "Exact killed/survived/indeterminate outcomes for predeclared "
                "fault controls under exact selector profiles."
            ),
            "planned_direct_comparison": (
                "Compare independently reconstructed truth-table independence "
                "relations with the complete asymmetric mutant/profile table."
            ),
            "not_claimed": (
                "No mutation adequacy, representative operator quality, "
                "equivalent-mutant solution, or method superiority."
            ),
        },
    ],
    "planned_difference": {
        "representation": (
            "An integrity-bound, order-independent multiset of exact per-selector "
            "executed-statement and executed-arc path shapes, with selector, "
            "quadrant, context, and invocation bindings retained separately."
        ),
        "information_loss_tested": (
            "Whether profile-level statement and arc union/intersection erase "
            "which path shapes co-occur within individual logical tests."
        ),
        "cross_evidence_relation": (
            "Whether fixed truth-table condition-independence witnesses agree "
            "with the predeclared incidence of dropped-conjunct mutants."
        ),
        "integrity_boundary": (
            "Expected, observed, unexpected, and indeterminate evidence must "
            "remain separate and be independently reconstructed beyond unkeyed "
            "digest equality."
        ),
        "simpler_baseline_preferred_if_equivalent": True,
    },
    "novelty_boundary": {
        "novelty_status": "not_established",
        "systematic_review_complete": False,
        "combination_may_be_evaluated": True,
        "scientific_novelty_claim_allowed": False,
        "award_level_significance_claim_allowed": False,
        "reason": (
            "Contexts, path coverage, MC/DC, combinatorial coverage, checked "
            "coverage, mutation testing, and oracle analysis are established. "
            "The preregistered experiment can test only the incremental evidence "
            "value of one integrity-bound combination in one owned-synthetic case."
        ),
    },
    "falsification_and_redesign": [
        (
            "Profile statement or arc union/intersection differs after bytes "
            "are frozen."
        ),
        (
            "Anonymous path multisets are unstable across clean Python "
            "3.11-3.14 runs."
        ),
        "Profiles differ only through selector names or cardinality artifacts.",
        (
            "A simpler truth-table or MC/DC representation captures the same "
            "complete relation."
        ),
        (
            "Coverage.py contexts add no evidence beyond already frozen input "
            "labels."
        ),
        (
            "Mutation outcomes require post-outcome operator or selector tuning."
        ),
        "The asymmetric mutant table diverges from preregistration.",
        (
            "Equivalent, invalid, or indeterminate mutants dominate the design."
        ),
        (
            "Representation changes alter path identities without semantic change."
        ),
        (
            "The verifier cannot reject coordinated semantic substitution beyond "
            "digest recomputation."
        ),
        (
            "Publication or execution cost exceeds the bounded evidence value."
        ),
    ],
    "policy": {
        "execution_authorized": False,
        "external_repository_execution_authorized": False,
        "holdout_selected": False,
        "primary_denominator_eligible": False,
        "quality_score": None,
        "universal_threshold": None,
        "merge_blocker_authorized": False,
        "ecological_inference_allowed": False,
        "method_superiority_claim_allowed": False,
        "production_readiness_claim_allowed": False,
    },
    "log_sha256": None,
}


class DW001InteractionPriorArtError(DeltaWitnessError):
    """Raised when the frozen prior-art boundary is inconsistent."""


def compute_interaction_prior_art_log_sha256(
    document: dict[str, Any],
) -> str:
    if not isinstance(document, dict):
        raise DW001InteractionPriorArtError(
            "interaction prior-art log must be an object"
        )
    normalized = deepcopy(document)
    normalized["log_sha256"] = None
    return sha256_document(normalized)


def build_interaction_witness_prior_art_log() -> dict[str, Any]:
    document = deepcopy(_LOG_TEMPLATE)
    document["log_sha256"] = compute_interaction_prior_art_log_sha256(
        document
    )
    return document


def _differences(
    expected: object,
    observed: object,
    *,
    context: str,
) -> list[str]:
    if type(expected) is not type(observed):
        return [f"{context}: type mismatch"]
    if isinstance(expected, dict):
        assert isinstance(observed, dict)
        errors: list[str] = []
        expected_keys = set(expected)
        observed_keys = set(observed)
        if expected_keys != observed_keys:
            errors.append(
                f"{context}: field mismatch; "
                f"missing={sorted(expected_keys - observed_keys)}, "
                f"extra={sorted(observed_keys - expected_keys)}"
            )
        for key in sorted(expected_keys & observed_keys):
            errors.extend(
                _differences(
                    expected[key],
                    observed[key],
                    context=f"{context}.{key}",
                )
            )
        return errors
    if isinstance(expected, list):
        assert isinstance(observed, list)
        errors = []
        if len(expected) != len(observed):
            errors.append(
                f"{context}: length mismatch; expected {len(expected)}, "
                f"observed {len(observed)}"
            )
        for index, (left, right) in enumerate(
            zip(expected, observed, strict=False)
        ):
            errors.extend(
                _differences(
                    left,
                    right,
                    context=f"{context}[{index}]",
                )
            )
        return errors
    if expected != observed:
        return [
            f"{context}: expected={expected!r}, observed={observed!r}"
        ]
    return []


def verify_interaction_witness_prior_art_log_document(
    document: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        if not isinstance(document, dict):
            raise DW001InteractionPriorArtError(
                "interaction prior-art log must be an object"
            )
        recorded = document.get("log_sha256")
        if not isinstance(recorded, str):
            raise DW001InteractionPriorArtError(
                "interaction prior-art log.log_sha256 must be a string"
            )
        computed = compute_interaction_prior_art_log_sha256(document)
        expected = build_interaction_witness_prior_art_log()
    except (
        DW001InteractionPriorArtError,
        DeltaWitnessError,
        KeyError,
        TypeError,
        IndexError,
        ValueError,
        OverflowError,
        MemoryError,
        RecursionError,
    ) as exc:
        if isinstance(exc, DW001InteractionPriorArtError):
            return False, (str(exc),)
        return False, (
            "interaction prior-art log: verification failed closed: "
            f"{type(exc).__name__}: {exc}",
        )
    errors: list[str] = []
    if recorded != computed:
        errors.append(
            "interaction prior-art log.log_sha256: digest mismatch"
        )
    if computed != PRIOR_ART_LOG_SHA256:
        errors.append(
            "interaction prior-art log.log_sha256: does not match the "
            "reviewed boundary"
        )
    errors.extend(
        _differences(
            expected,
            document,
            context="interaction prior-art log",
        )
    )
    unique = tuple(dict.fromkeys(errors))
    return not unique, unique


__all__ = [
    "DW001InteractionPriorArtError",
    "PRIOR_ART_LOG_ID",
    "PRIOR_ART_LOG_SCHEMA_VERSION",
    "PRIOR_ART_LOG_SHA256",
    "build_interaction_witness_prior_art_log",
    "compute_interaction_prior_art_log_sha256",
    "verify_interaction_witness_prior_art_log_document",
]
