from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BASE_COMMIT = "e4b3f3d3e9d4a4b5d1ed2012d3cd4c2e2775761b"
PARTIAL_PATH = "research/DW-001/.claim-relevant-path-transport-recovery/dw001_claim_relevant_path_plan.py.partial"
MODULE_PATH = ROOT / "src" / "deltawitness" / "dw001_claim_relevant_path_plan.py"

TAIL = r'''

PRIOR_ART: dict[str, Any] = {
    "schema_version": PRIOR_ART_SCHEMA,
    "study_id": "DW-001",
    "log_id": "DW-001-CLAIM-RELEVANT-PATH-PRIOR-ART-LOG-V1",
    "status": "pre_execution_literature_boundary",
    "reviewed_at": "2026-08-18",
    "plan_id": PLAN_ID,
    "plan_sha256": PLAN["plan_sha256"],
    "catalog_sha256": CATALOG["catalog_sha256"],
    "sources": [
        {"order": 1, "source_id": "coveragepy-7.15.2-contexts-api", "title": "Coverage.py measurement contexts and public API", "source_type": "official-versioned-tool-documentation", "identifier": "https://coverage.readthedocs.io/en/7.15.2/", "baseline_role": "Exact statement, arc, branch-statistic, and per-selector context evidence.", "boundary": "Execution structure does not establish assertion influence or oracle adequacy."},
        {"order": 2, "source_id": "schuler-zeller-checked-coverage", "title": "Checked coverage: an indicator for oracle quality", "source_type": "peer-reviewed-primary-research", "identifier": "10.1002/stvr.1497", "baseline_role": "Dynamic slice of covered statements influencing an oracle.", "boundary": "This preregistration does not implement or claim general checked coverage."},
        {"order": 3, "source_id": "korel-laski-dynamic-slicing", "title": "Dynamic Program Slicing", "source_type": "peer-reviewed-primary-research", "identifier": "Information Processing Letters 29(3), 1988", "baseline_role": "Execution-specific program dependence and slicing.", "boundary": "The fixed influence graph is one project-owned control, not a dynamic slicer."},
        {"order": 4, "source_id": "weiser-program-slicing", "title": "Program Slicing", "source_type": "peer-reviewed-primary-research", "identifier": "IEEE TSE 10(4), 1984", "baseline_role": "Foundational slicing criterion and dependence abstraction.", "boundary": "No general static slicing claim is made."},
        {"order": 5, "source_id": "barr-oracle-survey", "title": "The Oracle Problem in Software Testing: A Survey", "source_type": "peer-reviewed-survey", "identifier": "10.1109/TSE.2014.2372785", "baseline_role": "Limits of determining expected behavior and oracle adequacy.", "boundary": "The fixed assertions are project-owned controls, not a solution to the oracle problem."},
        {"order": 6, "source_id": "jia-harman-mutation-survey", "title": "An Analysis and Survey of the Development of Mutation Testing", "source_type": "peer-reviewed-survey", "identifier": "10.1109/TSE.2010.62", "baseline_role": "Mutation operators, adequacy, equivalence, and cost.", "boundary": "The fixed catalog is not representative and produces no mutation score."},
    ],
    "closest_baselines": [
        {"order": 1, "baseline_id": "raw-selector-context-paths", "captures": "Exact per-selector executed statement and arc shapes.", "planned_comparison": "Distinguish all decision and collateral routes.", "not_claimed": "No claim relevance or oracle strength."},
        {"order": 2, "baseline_id": "explicit-route-membership", "captures": "Exact declared decision and collateral route labels.", "planned_comparison": "Prefer this simpler baseline if it captures every runtime distinction.", "not_claimed": "No evidence that declared labels match actual execution."},
        {"order": 3, "baseline_id": "fixed-assertion-influence-graph", "captures": "Exact project-owned dependence relation from inputs/routes to returned fields.", "planned_comparison": "Separate decision-route from collateral-only computation.", "not_claimed": "No general static or dynamic slicing."},
        {"order": 4, "baseline_id": "typed-claim-and-collateral-assertions", "captures": "Exact behavior of claim-facing and separately labeled collateral reference checks.", "planned_comparison": "Prevent collateral failures from satisfying the authorization claim.", "not_claimed": "No complete specification."},
        {"order": 5, "baseline_id": "fixed-fault-incidence", "captures": "Exact typed outcomes for route-local, shared, collateral, and neutral-diversion controls.", "planned_comparison": "Test bounded relation between influence and fault detection.", "not_claimed": "No mutation adequacy or method superiority."},
    ],
    "planned_difference": {
        "question": "Whether integrity-bound runtime path evidence can be filtered by one exact assertion-influence control without conflating collateral divergence with claim failure.",
        "simpler_baseline_preferred_if_equivalent": True,
        "negative_control": "Reject-all-path-divergence is expected to over-refuse at least one valid control.",
    },
    "novelty_boundary": {"novelty_status": "not_established", "systematic_review_complete": False, "scientific_novelty_claim_allowed": False, "award_level_significance_claim_allowed": False},
    "policy": deepcopy(PLAN["policy"]),
    "log_sha256": None,
}
PRIOR_ART["log_sha256"] = sha256_document(PRIOR_ART)

_REVIEWED = {
    "source_sha256": "8c1bdd26c2e98cd209f210630bfe4d274a3dcd7bbd042db8b8586c7750814327",
    "source_ast_sha256": "dabb7011748968f8d43d590ff843a91697a3344a2400d7cabaf926b79ca88e2d",
    "test_sha256": "8a26d52fa7fbb4ab7fc6eab466d9051cd329b0da09a667b5e220fbbfd416d1e9",
    "influence_control_sha256": "7b068d2f71003fade4eca77e1aa9cdb3a0f2f526f89dbd4828d4f17fbf2bd4f5",
    "plan_sha256": "ff0403132c3424fc7309a15a05794eed93ac9eb526de172e17326f8409ca0888",
    "catalog_sha256": "f36fbe58c00cfb8ed0fd994f3bb1dcdb45040774f7ae4663563b9f40ac15daa5",
    "prior_art_log_sha256": "5f697631a5ded7a413dd11f4da0606ee8809e2b0f5de257ecab53a7e2d7f790c",
}
PLAN_SHA256 = _REVIEWED["plan_sha256"]
CATALOG_SHA256 = _REVIEWED["catalog_sha256"]
PRIOR_ART_LOG_SHA256 = _REVIEWED["prior_art_log_sha256"]
INFLUENCE_CONTROL_SHA256 = _REVIEWED["influence_control_sha256"]
_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")


class DW001ClaimRelevantPathPlanError(DeltaWitnessError):
    """Raised when the frozen preregistration contract is inconsistent."""


def _error(context: str, detail: str) -> DW001ClaimRelevantPathPlanError:
    return DW001ClaimRelevantPathPlanError(f"{context}: {detail}")


def _assert_reviewed_identities() -> None:
    observed = {
        "source_sha256": SOURCE_SHA256,
        "source_ast_sha256": SOURCE_AST_SHA256,
        "test_sha256": TEST_SHA256,
        "influence_control_sha256": INFLUENCE_CONTROL["control_sha256"],
        "plan_sha256": PLAN["plan_sha256"],
        "catalog_sha256": CATALOG["catalog_sha256"],
        "prior_art_log_sha256": PRIOR_ART["log_sha256"],
    }
    for name, expected in _REVIEWED.items():
        if observed[name] != expected:
            raise _error("claim-relevant path reviewed identity", f"{name} mismatch; expected {expected}, observed {observed[name]}")


def _self_digest(document: dict[str, Any], field: str, context: str) -> str:
    if not isinstance(document, dict):
        raise _error(context, "must be an object")
    normalized = deepcopy(document)
    normalized[field] = None
    return sha256_document(normalized)


def compute_claim_relevant_path_plan_sha256(document: dict[str, Any]) -> str:
    return _self_digest(document, "plan_sha256", "claim-relevant path plan")


def compute_claim_relevant_path_catalog_sha256(document: dict[str, Any]) -> str:
    return _self_digest(document, "catalog_sha256", "claim-relevant path catalog")


def compute_claim_relevant_path_prior_art_sha256(document: dict[str, Any]) -> str:
    return _self_digest(document, "log_sha256", "claim-relevant path prior art")


def _compile_fixed_sources() -> None:
    source_tree = ast.parse(SOURCE, filename=SOURCE_PATH, mode="exec")
    test_tree = ast.parse(TESTS, filename=TEST_PATH, mode="exec")
    compile(source_tree, SOURCE_PATH, "exec")
    compile(test_tree, TEST_PATH, "exec")
    compile(ast.parse(ast.unparse(source_tree) + "\n", filename=SOURCE_PATH, mode="exec"), SOURCE_PATH, "exec")


def build_claim_relevant_path_plan() -> dict[str, Any]:
    _compile_fixed_sources()
    _assert_reviewed_identities()
    return deepcopy(PLAN)


def build_claim_relevant_path_catalog(plan: object) -> dict[str, Any]:
    valid, errors = verify_claim_relevant_path_plan_document(plan)
    if not valid:
        raise _error("claim-relevant path catalog plan", "; ".join(errors))
    _assert_reviewed_identities()
    return deepcopy(CATALOG)


def build_claim_relevant_path_prior_art_log(plan: object, catalog: object) -> dict[str, Any]:
    valid, errors = verify_claim_relevant_path_catalog_document(catalog, plan)
    if not valid:
        raise _error("claim-relevant path prior-art catalog", "; ".join(errors))
    _assert_reviewed_identities()
    return deepcopy(PRIOR_ART)


def _differences(expected: object, observed: object, *, context: str) -> list[str]:
    if type(expected) is not type(observed):
        return [f"{context}: type mismatch; expected {type(expected).__name__}, observed {type(observed).__name__}"]
    if isinstance(expected, dict):
        assert isinstance(observed, dict)
        errors: list[str] = []
        expected_keys, observed_keys = set(expected), set(observed)
        if expected_keys != observed_keys:
            errors.append(f"{context}: field mismatch; missing={sorted(expected_keys-observed_keys)}, extra={sorted(observed_keys-expected_keys)}")
        for key in sorted(expected_keys & observed_keys):
            errors.extend(_differences(expected[key], observed[key], context=f"{context}.{key}"))
        return errors
    if isinstance(expected, list):
        assert isinstance(observed, list)
        errors = []
        if len(expected) != len(observed):
            errors.append(f"{context}: length mismatch; expected {len(expected)}, observed {len(observed)}")
        for index, (left, right) in enumerate(zip(expected, observed, strict=False)):
            errors.extend(_differences(left, right, context=f"{context}[{index}]"))
        return errors
    return [] if expected == observed else [f"{context}: expected={expected!r}, observed={observed!r}"]


def _validated_digest(value: object, expected: str, *, context: str) -> tuple[str, list[str]]:
    if not isinstance(value, str) or _SHA256_PATTERN.fullmatch(value) is None:
        raise _error(context, "expected a lowercase SHA-256 digest")
    return value, ([] if value == expected else [f"{context}: reviewed identity mismatch"])


def _failure(context: str, exc: BaseException) -> tuple[bool, tuple[str, ...]]:
    return False, (f"{context}: verification failed closed: {type(exc).__name__}: {exc}",)


def _verify_exact(document: object, expected: dict[str, Any], *, digest_field: str, reviewed_digest: str, context: str) -> tuple[bool, tuple[str, ...]]:
    try:
        if not isinstance(document, dict):
            raise _error(context, "must be an object")
        _assert_reviewed_identities()
        recorded, errors = _validated_digest(document.get(digest_field), reviewed_digest, context=f"{context}.{digest_field}")
        computed = _self_digest(document, digest_field, context)
        if recorded != computed:
            errors.append(f"{context}.{digest_field}: digest mismatch")
        errors.extend(_differences(expected, document, context=context))
    except (DW001ClaimRelevantPathPlanError, DeltaWitnessError, KeyError, TypeError, IndexError, ValueError, OverflowError, MemoryError, RecursionError) as exc:
        return _failure(context, exc)
    unique = tuple(dict.fromkeys(errors))
    return not unique, unique


def verify_claim_relevant_path_plan_document(document: object) -> tuple[bool, tuple[str, ...]]:
    return _verify_exact(document, PLAN, digest_field="plan_sha256", reviewed_digest=PLAN_SHA256, context="claim-relevant path plan")


def verify_claim_relevant_path_catalog_document(document: object, plan: object) -> tuple[bool, tuple[str, ...]]:
    valid, errors = verify_claim_relevant_path_plan_document(plan)
    if not valid:
        return False, tuple(f"claim-relevant path catalog plan: {error}" for error in errors)
    return _verify_exact(document, CATALOG, digest_field="catalog_sha256", reviewed_digest=CATALOG_SHA256, context="claim-relevant path catalog")


def verify_claim_relevant_path_prior_art_log_document(document: object, plan: object, catalog: object) -> tuple[bool, tuple[str, ...]]:
    valid, errors = verify_claim_relevant_path_catalog_document(catalog, plan)
    if not valid:
        return False, tuple(f"claim-relevant path prior-art catalog: {error}" for error in errors)
    return _verify_exact(document, PRIOR_ART, digest_field="log_sha256", reviewed_digest=PRIOR_ART_LOG_SHA256, context="claim-relevant path prior art")


def _load_regular_document(path: Path, *, context: str) -> dict[str, Any]:
    try:
        status = path.lstat()
    except OSError as exc:
        raise _error(context, f"cannot inspect {path}: {exc}") from exc
    if stat.S_ISLNK(status.st_mode) or not stat.S_ISREG(status.st_mode):
        raise _error(context, f"expected a regular non-symbolic-link file: {path}")
    try:
        document = load_report(path)
    except DeltaWitnessError as exc:
        raise _error(context, str(exc)) from exc
    if not isinstance(document, dict):
        raise _error(context, "document root must be an object")
    return document


def load_claim_relevant_path_plan(path: Path) -> dict[str, Any]:
    document = _load_regular_document(path, context="claim-relevant path plan")
    valid, errors = verify_claim_relevant_path_plan_document(document)
    if not valid:
        raise _error("claim-relevant path plan", "; ".join(errors))
    return document


def load_claim_relevant_path_catalog(path: Path, plan: object) -> dict[str, Any]:
    document = _load_regular_document(path, context="claim-relevant path catalog")
    valid, errors = verify_claim_relevant_path_catalog_document(document, plan)
    if not valid:
        raise _error("claim-relevant path catalog", "; ".join(errors))
    return document


def load_claim_relevant_path_prior_art_log(path: Path, plan: object, catalog: object) -> dict[str, Any]:
    document = _load_regular_document(path, context="claim-relevant path prior art")
    valid, errors = verify_claim_relevant_path_prior_art_log_document(document, plan, catalog)
    if not valid:
        raise _error("claim-relevant path prior art", "; ".join(errors))
    return document


__all__ = [
    "CATALOG_SCHEMA_VERSION", "CATALOG_SHA256", "CELLS", "COVERAGEPY_MANIFEST_SHA256",
    "DW001ClaimRelevantPathPlanError", "INFLUENCE_CONTROL_SHA256", "INTERACTION_CHECKPOINT_SHA256",
    "INTERACTION_SEMANTIC_SHA256", "MAIN_COMMIT", "PLAN_ID", "PLAN_SCHEMA_VERSION", "PLAN_SHA256",
    "PRIOR_ART_LOG_SHA256", "PRIOR_ART_SCHEMA_VERSION", "PROFILES", "SOURCE", "SOURCE_AST_SHA256",
    "SOURCE_PATH", "SOURCE_SHA256", "TESTS", "TEST_PATH", "TEST_SHA256", "ast_sha256",
    "build_claim_relevant_path_catalog", "build_claim_relevant_path_plan", "build_claim_relevant_path_prior_art_log",
    "compute_claim_relevant_path_catalog_sha256", "compute_claim_relevant_path_plan_sha256",
    "compute_claim_relevant_path_prior_art_sha256", "load_claim_relevant_path_catalog",
    "load_claim_relevant_path_plan", "load_claim_relevant_path_prior_art_log", "path_shape", "sha256_bytes",
    "verify_claim_relevant_path_catalog_document", "verify_claim_relevant_path_plan_document",
    "verify_claim_relevant_path_prior_art_log_document",
]
'''


def run(*args: str) -> bytes:
    return subprocess.run(args, cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


partial = run("git", "show", f"{BASE_COMMIT}:{PARTIAL_PATH}")
lines = partial.splitlines(keepends=True)
if len(lines) != 909:
    raise SystemExit(f"unexpected reviewed partial line count: {len(lines)}")
prefix = b"".join(lines[:810])
body = prefix + TAIL.encode("utf-8")
MODULE_PATH.write_bytes(body)

sys.path.insert(0, str(ROOT / "src"))
from deltawitness.dw001_claim_relevant_path_plan import (  # noqa: E402
    CATALOG_SHA256,
    INFLUENCE_CONTROL_SHA256,
    PLAN_SHA256,
    PRIOR_ART_LOG_SHA256,
    SOURCE_AST_SHA256,
    SOURCE_SHA256,
    TEST_SHA256,
    build_claim_relevant_path_catalog,
    build_claim_relevant_path_plan,
    build_claim_relevant_path_prior_art_log,
)
from deltawitness.reporting import canonical_json  # noqa: E402

expected = {
    "source_sha256": "8c1bdd26c2e98cd209f210630bfe4d274a3dcd7bbd042db8b8586c7750814327",
    "source_ast_sha256": "dabb7011748968f8d43d590ff843a91697a3344a2400d7cabaf926b79ca88e2d",
    "test_sha256": "8a26d52fa7fbb4ab7fc6eab466d9051cd329b0da09a667b5e220fbbfd416d1e9",
    "influence_control_sha256": "7b068d2f71003fade4eca77e1aa9cdb3a0f2f526f89dbd4828d4f17fbf2bd4f5",
    "plan_sha256": "ff0403132c3424fc7309a15a05794eed93ac9eb526de172e17326f8409ca0888",
    "catalog_sha256": "f36fbe58c00cfb8ed0fd994f3bb1dcdb45040774f7ae4663563b9f40ac15daa5",
    "prior_art_log_sha256": "5f697631a5ded7a413dd11f4da0606ee8809e2b0f5de257ecab53a7e2d7f790c",
}
observed = {
    "source_sha256": SOURCE_SHA256,
    "source_ast_sha256": SOURCE_AST_SHA256,
    "test_sha256": TEST_SHA256,
    "influence_control_sha256": INFLUENCE_CONTROL_SHA256,
    "plan_sha256": PLAN_SHA256,
    "catalog_sha256": CATALOG_SHA256,
    "prior_art_log_sha256": PRIOR_ART_LOG_SHA256,
}
if observed != expected:
    raise SystemExit(f"reviewed identity mismatch: expected={expected!r} observed={observed!r}")

research = ROOT / "research" / "DW-001"
schema_dir = research / "schema"
schema_dir.mkdir(parents=True, exist_ok=True)
plan = build_claim_relevant_path_plan()
catalog = build_claim_relevant_path_catalog(plan)
prior = build_claim_relevant_path_prior_art_log(plan, catalog)
for path, document in (
    (research / "claim-relevant-path-divergence-plan.v1.json", plan),
    (research / "claim-relevant-path-divergence-catalog.v1.json", catalog),
    (research / "claim-relevant-path-prior-art-log.v1.json", prior),
):
    path.write_bytes(canonical_json(document) + b"\n")


def exact_schema(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return {"type": "object", "additionalProperties": False, "required": list(value), "properties": {key: exact_schema(child) for key, child in value.items()}}
    if isinstance(value, list):
        return {"type": "array", "minItems": len(value), "maxItems": len(value), "prefixItems": [exact_schema(child) for child in value], "items": False}
    return {"const": value}


for filename, title, document in (
    ("claim-relevant-path-divergence-plan.schema.json", "DeltaWitness DW-001 Claim-Relevant Path Divergence Plan v1", plan),
    ("claim-relevant-path-divergence-catalog.schema.json", "DeltaWitness DW-001 Claim-Relevant Path Divergence Catalog v1", catalog),
    ("claim-relevant-path-prior-art-log.schema.json", "DeltaWitness DW-001 Claim-Relevant Path Prior-Art Log v1", prior),
):
    path = schema_dir / filename
    schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": f"https://github.com/rdemb/delta-witness/{path.relative_to(ROOT).as_posix()}", "title": title, **exact_schema(document)}
    path.write_bytes(canonical_json(schema) + b"\n")

print(json.dumps(observed, sort_keys=True, separators=(",", ":")))
