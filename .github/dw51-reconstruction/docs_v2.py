from __future__ import annotations

from pathlib import Path
import stat

ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "research" / "DW-001"

DIGESTS = {
    "source": "8c1bdd26c2e98cd209f210630bfe4d274a3dcd7bbd042db8b8586c7750814327",
    "source_ast": "dabb7011748968f8d43d590ff843a91697a3344a2400d7cabaf926b79ca88e2d",
    "test": "8a26d52fa7fbb4ab7fc6eab466d9051cd329b0da09a667b5e220fbbfd416d1e9",
    "influence": "7b068d2f71003fade4eca77e1aa9cdb3a0f2f526f89dbd4828d4f17fbf2bd4f5",
    "plan": "ff0403132c3424fc7309a15a05794eed93ac9eb526de172e17326f8409ca0888",
    "catalog": "f36fbe58c00cfb8ed0fd994f3bb1dcdb45040774f7ae4663563b9f40ac15daa5",
    "prior_art": "5f697631a5ded7a413dd11f4da0606ee8809e2b0f5de257ecab53a7e2d7f790c",
}


def write(relative: str, content: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")


def append_once(relative: str, marker: str, section: str) -> None:
    path = ROOT / relative
    mode = path.lstat().st_mode
    if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
        raise SystemExit(f"documentation target is not a regular file: {relative}")
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    path.write_text(
        text.rstrip() + "\n\n" + section.rstrip() + "\n",
        encoding="utf-8",
        newline="\n",
    )


write(
    "research/DW-001/CLAIM_RELEVANT_PATH_DIVERGENCE_PLAN_V1.md",
    f'''# DW-001 Claim-Relevant Path Divergence Plan v1

## Status

**FACT — design-only preregistration.** This work package freezes one synthetic Python target, sixteen typed selectors over eight owned cells, six overlapping diagnostic profiles, one fixed project-owned influence control, four planned execution controls, and a non-executed implementation catalog.

**DECISION — execution is not authorized.** Candidate, selector, Coverage.py, fault, influence, and target execution remain `not_implemented`. No score, threshold, holdout, merge blocker, release decision, deployment decision, or production claim is produced by this plan.

## Frozen identities

| Object | SHA-256 |
|---|---|
| synthetic source bytes | `{DIGESTS["source"]}` |
| semantic source AST | `{DIGESTS["source_ast"]}` |
| synthetic tests | `{DIGESTS["test"]}` |
| fixed influence control | `{DIGESTS["influence"]}` |
| plan | `{DIGESTS["plan"]}` |
| catalog | `{DIGESTS["catalog"]}` |
| prior-art log | `{DIGESTS["prior_art"]}` |

The canonical machine-readable artifacts and exact closed schemas are authoritative. This document explains their bounded interpretation.

## Falsifiable question

**HYPOTHESIS.** For this exact owned target, integrity-bound runtime path evidence may distinguish a claim-relevant decision-route fault from a collateral-only route fault when filtered by the frozen assertion-influence control.

**NEGATIVE CONTROL.** A reject-all-path-divergence rule is expected to over-refuse the behavior-preserving neutral-diversion control.

**SIMPLER BASELINE RULE.** Exact declared route membership is preferred if it captures every distinction later observed from runtime path evidence.

## Frozen design

The input space is the Cartesian product of:

- claim outcome class: `allowed` or `denied`;
- decision route: `direct` or `normalized`;
- collateral route: `compact` or `verbose`.

Each cell has one claim selector and one collateral-reference selector. Claim selectors read only `allowed` and `reason_code`; collateral-reference selectors read only `trace_code`. The profiles overlap intentionally and are ineligible as primary denominators.

The four planned controls are:

1. a direct-route role inversion expected to fail four claim selectors;
2. a verbose-to-compact collateral diversion expected to fail four collateral references without satisfying the claim failure relation;
3. a shared `or` gate fault expected to fail four claim selectors;
4. a direct-via-normalized behavior-preserving path diversion expected to change four path shapes while preserving every declared output.

## Result taxonomy reserved for a later work package

A future executor must keep `pass`, `fail`, `error`, and `timeout` disjoint. Missing, malformed, ambiguous, contradictory, unavailable, or incomplete evidence is `indeterminate`; it is neither expected behavior nor fault detection. Complete divergence is retained as `unexpected`, not coerced into a harness error.

## Falsification criteria

The bounded hypothesis is weakened or rejected if any of the following occurs:

- the simpler route-membership baseline is equivalent;
- the influence control admits a collateral-only node into the claim criterion;
- the collateral fault satisfies a claim selector;
- the neutral-diversion control fails a declared output;
- the fixed identities cannot be reproduced independently;
- a required observation is unavailable or ambiguous;
- an equivalent implementation cannot be classified without post hoc protocol changes.

No protocol, operator, denominator, expected matrix, or claim boundary may be changed after observing a future execution result without a separately versioned deviation record.
''',
)

write(
    "research/DW-001/CLAIM_RELEVANT_PATH_DIVERGENCE_ARCHITECTURE_V1.md",
    '''# DW-001 Claim-Relevant Path Divergence Architecture v1

## FACT — bounded components

1. **Owned fixture bytes.** The source and test strings are synthetic, immutable inputs with byte and semantic-AST identities.
2. **Design builder.** A dependency-free module parses, compiles, transforms, hashes, and returns defensive copies. It does not execute the fixture.
3. **Canonical artifacts.** Plan, catalog, and prior-art documents use canonical JSON and self-digests normalized through one null digest field.
4. **Exact verifiers.** Verification compares types, keys, list order, values, reviewed identities, and recomputed self-digests. A correctly resealed substitute is still rejected.
5. **Regular-file loaders.** Loaders reject symbolic links, non-regular files, duplicate JSON keys, malformed UTF-8, malformed roots, and semantic substitutions.
6. **Exact schemas.** Draft 2020-12 schemas close every object boundary and fix every array's length, order, and item schema.
7. **Tests and smoke.** Regression tests cover reconstruction, policy boundaries, substitutions, loader attacks, schema closure, and dependency-free wheel reproduction.

## Trust boundaries

The preregistration module trusts only reviewed constants in its own installed distribution and canonical artifacts that reproduce those constants exactly. Git metadata, filenames alone, caller-provided digests, schema validity alone, and a green final-state test run are insufficient identity evidence.

The temporary branch-maintenance job used to reconstruct the files is not part of the research architecture. It is retained only in Git history and PR evidence, removes itself from the final tree, receives no repository secrets, and cannot authorize research execution or publication claims.

## Non-goals

This layer is not a Python sandbox, dynamic slicer, checked-coverage implementation, mutation-testing framework, general causality engine, production policy engine, remote executor, or release gate.
''',
)

write(
    "research/DW-001/CLAIM_RELEVANT_PATH_DIVERGENCE_THREAT_BOUNDARY_V1.md",
    '''# DW-001 Claim-Relevant Path Divergence Threat Boundary v1

## Protected properties

- exact source, AST, test, influence-control, plan, catalog, and prior-art identity;
- separation of claim-facing and collateral-reference observations;
- separation of design artifacts from execution results;
- preservation of `unexpected` and `indeterminate` outcomes;
- inability to promote scores, novelty, deployment, release, or production claims through document substitution;
- absence of Coverage.py and fixture execution during import, build, verification, and smoke reproduction.

## Adversary model

The verifier assumes an attacker may edit JSON fields, reorder lists, add or remove keys, recompute self-digests, substitute selector roles, alter expected outcomes, inject an execution result, promote novelty language, supply duplicate JSON keys, use malformed UTF-8, or replace a regular path with a symbolic link or directory.

## Controls

- exact reviewed-identity constants independent of document self-digests;
- semantic reconstruction rather than schema-only acceptance;
- fail-closed regular-file inspection before parsing;
- canonical JSON duplicate-key rejection;
- exact list order and cardinality;
- fixed false/null policy fields;
- no `exec` or `eval` primitive in the preregistration module;
- dependency-free import and wheel smoke with Coverage.py absent;
- public-tree validation unchanged.

## Residual risk

The fixed influence graph is project-owned and may be an inadequate model of true assertion influence. The fixture is intentionally small and non-representative. Python parser behavior can differ across supported versions. A future execution adapter introduces a larger trust boundary and requires a new threat-model review. These limitations prohibit a general safety, causal, slicing, oracle-quality, production-readiness, or novelty claim.
''',
)

write(
    "research/DW-001/CLAIM_RELEVANT_PATH_DIVERGENCE_PUBLICATION_BOUNDARY_V1.md",
    '''# DW-001 Claim-Relevant Path Divergence Publication Boundary v1

## Allowed statements after this preregistration merges

- DeltaWitness froze a design-only, synthetic DW-001 claim-path divergence protocol.
- The committed plan, catalog, prior-art log, schemas, tests, and reviewed identities reproduce under the repository's supported Python matrix.
- The protocol distinguishes claim-facing selectors from collateral-reference selectors and reserves typed result semantics for a later executor.
- The operator set contains explicit invalid, duplicate, not-applicable, equivalent-review, and behavior-preserving controls.

## Disallowed statements

This work package does **not** establish that:

- a candidate or selector was executed;
- Coverage.py evidence was collected;
- a fault was detected or localized;
- path divergence is causal or claim-relevant in general;
- the fixed influence graph is a dynamic or static slice;
- checked coverage was implemented;
- the method outperforms a baseline;
- scientific novelty, award-level significance, ecological validity, production readiness, release readiness, safety, or deployment readiness has been established.

## Required future evidence

Any result-bearing publication requires a separately frozen execution protocol, typed receipts for every selector and implementation, exact environment and package identities, complete negative-result retention, baseline comparison, privacy review, public-tree review, and a new claim-boundary decision after observing no holdout result in advance.
''',
)

write(
    "research/DW-001/CLAIM_RELEVANT_PATH_DIVERGENCE_RED_FIRST_V1.md",
    '''# DW-001 Claim-Relevant Path Divergence Red-First Record v1

## OBSERVATION

The first branch implementation deliberately raised:

```text
DW001ClaimRelevantPathPlanError:
  claim-relevant path preregistration is intentionally not implemented
```

The complete repository run contained one expected red-first error while the existing tests, public-tree validation, and compilation remained intact.

## TRANSPORT FAILURE

A later binary transport attempt was truncated. The archive lacked a gzip end marker and exposed only a partial member. The public-tree validator correctly rejected the transport and was not weakened. The archive, partial recovery material, and one-time unpack workflow were removed through an ordinary cleanup commit; their diagnostic facts remain in Issue #50 and PR #51 history.

## DECISION

Only independently reconstructed objects matching every reviewed identity may replace the scaffold. A final green run is not evidence that the red-first boundary existed; the failure remains preserved in Git and PR history. Candidate, selector, Coverage.py, fault, influence, and target execution remain unauthorized.
''',
)

write(
    "research/DW-001/CLAIM_RELEVANT_PATH_DIVERGENCE_ADVERSARIAL_REVIEW_V1.md",
    '''# DW-001 Claim-Relevant Path Divergence Adversarial Review v1

## Review target

The review covers the design-only builder, canonical artifacts, exact schemas, loaders, tests, retained read-only workflow, and documentation. It excludes all future candidate, selector, Coverage.py, fault, influence, and target execution.

## Required attacks

The regression suite must reject each attack even when the attacker recomputes the affected document self-digest:

- decision-route membership substitution;
- claim/collateral selector-role substitution;
- cell or prior-art source reordering;
- influence-edge substitution;
- expected-matrix substitution;
- catalog status substitution and result injection;
- duplicate-implementation rebinding;
- novelty promotion;
- extra, missing, and wrong-type fields;
- symbolic-link, directory, duplicate-key, and malformed-UTF-8 loader inputs.

It must also confirm that the neutral-diversion control preserves declared outputs, profiles remain overlapping and denominator-ineligible, all execution/publication policy fields remain false or null, Coverage.py is absent from imports, and no `exec`/`eval` primitive exists in the module.

## Merge decision rule

The PR is mergeable only if the targeted attacks, complete repository regression suite, public-tree validator, compilation, design-only smoke, build, editable/wheel equivalence, supported-Python matrix, final-head CI, and post-merge validation are all green with no unresolved review thread or head movement. Otherwise the result is a named blocker, not an inferred success.
''',
)

append_once(
    "README.md",
    "<!-- DW001_CLAIM_RELEVANT_PATH_V1 -->",
    '''<!-- DW001_CLAIM_RELEVANT_PATH_V1 -->
### DW-001 claim-relevant path divergence preregistration

The repository includes a design-only synthetic preregistration that freezes claim-facing selectors, collateral-reference selectors, path-shape expectations, a fixed influence control, explicit fault/neutral controls, exact schemas, and a prior-art boundary. Execution remains `not_implemented`; no score, novelty, superiority, production, release, or deployment claim is authorized. See `research/DW-001/CLAIM_RELEVANT_PATH_DIVERGENCE_PLAN_V1.md`.''',
)

append_once(
    "ROADMAP.md",
    "<!-- DW001_CLAIM_RELEVANT_PATH_ROADMAP_V1 -->",
    '''<!-- DW001_CLAIM_RELEVANT_PATH_ROADMAP_V1 -->
## DW-001 claim-relevant path sequence

1. Merge and reproduce the design-only v1 preregistration.
2. Open a separate execution issue; freeze the executor, environment receipt, typed outcomes, and baseline comparison before running any candidate.
3. Execute only the owned synthetic target. Retain errors, timeouts, unavailable evidence, over-refusal, duplicates, invalid renders, and equivalent-review outcomes.
4. Compare against explicit route membership and raw selector-context paths. Prefer the simpler baseline if equivalent.
5. Reassess the public claim boundary after complete results and independent reproduction. No automatic promotion to release or production is permitted.''',
)

append_once(
    "THREAT_MODEL.md",
    "<!-- DW001_CLAIM_RELEVANT_PATH_THREAT_V1 -->",
    '''<!-- DW001_CLAIM_RELEVANT_PATH_THREAT_V1 -->
## Claim-relevant path preregistration boundary

The v1 preregistration treats self-digests, filenames, schemas, Git metadata, and final-state test success as insufficient in isolation. Reviewed source/AST/test/control identities and exact semantic reconstruction are required. Loaders reject symbolic links, non-regular files, duplicate keys, malformed UTF-8, resealed substitutions, and result/claim promotion. The temporary reconstruction job is repository maintenance only, receives no secrets, removes itself, and cannot authorize research execution or publication claims. A future runtime adapter is a new trust boundary and requires a separate review.''',
)

append_once(
    "docs/ARCHITECTURE.md",
    "<!-- DW001_CLAIM_RELEVANT_PATH_ARCH_V1 -->",
    '''<!-- DW001_CLAIM_RELEVANT_PATH_ARCH_V1 -->
## Design-only claim-path layer

The DW-001 claim-path layer is an integrity-bound preregistration component: owned fixture bytes → semantic identities → exact plan/catalog/prior-art documents → closed schemas → fail-closed loaders and verifiers. It deliberately stops before fixture execution, Coverage.py collection, candidate generation, selector invocation, fault observation, scoring, or merge gating.''',
)

append_once(
    "docs/PUBLICATION_POLICY.md",
    "<!-- DW001_CLAIM_RELEVANT_PATH_PUBLICATION_V1 -->",
    '''<!-- DW001_CLAIM_RELEVANT_PATH_PUBLICATION_V1 -->
## Claim-path preregistration claims

A merged, reproduced preregistration may be described as a frozen design and integrity check only. It must not be described as executed evidence, fault localization, causal attribution, checked coverage, dynamic slicing, method superiority, scientific novelty, production readiness, release readiness, or safety. Result-bearing language requires a separately frozen execution protocol and complete typed receipts.''',
)

print("wrote claim-path boundary documentation")
