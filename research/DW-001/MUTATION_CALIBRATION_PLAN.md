# DW-001 Claim-Scoped Mutation Calibration Plan v1

**Status:** pre-execution development design frozen and deterministic mutant catalog generated. No mutant or selector outcome has been executed under this plan. No score, threshold, merge blocker, ecological run, or holdout is authorized.

## 1. Purpose

PR #34 established one controlled limitation:

```text
typed assertion failure
    + canonical four-state witness
    + exact declared-selector fail-to-pass localization
    != sufficient oracle strength
```

The next research question is whether deterministic claim-scoped mutation evidence adds a useful warning signal beyond the existing matrix and selector-localization layers.

Running a mutation campaign before fixing the operator set, source scope, mutant identities, duplicate handling, invalid/not-applicable semantics, and selector profiles would permit post-result tuning. This plan freezes those inputs before any mutation-test outcome is observed.

## 2. Canonical artifacts

Plan:

```text
research/DW-001/claim-scoped-mutation-plan.v1.json
```

Catalog:

```text
research/DW-001/claim-scoped-mutant-catalog.v1.json
```

Schemas:

```text
research/DW-001/schema/claim-scoped-mutation-plan.schema.json
research/DW-001/schema/claim-scoped-mutant-catalog.schema.json
```

Implementation:

```text
src/deltawitness/dw001_mutation_plan.py
```

Exact identities:

```text
plan_id         = DW-001-CLAIM-SCOPED-MUTATION-PLAN-V1
plan_sha256     = 0ebf64e1de76849050c86d8a4d53d72d8067561ab48b4bd5a4083495dc99fe37
catalog_sha256  = 7b3e405bd3893f532c0ccfa16e9cc208422bbdd20dfe82a002c99342a04201c0
operator_set_id = python-boolean-predicate-minimal-v1
adapter_id      = python-stdlib-ast-return-v1
```

The plan and catalog are rebuilt and compared byte-semantically on Python 3.11, 3.12, 3.13, and 3.14 from both editable and installed-wheel packages.

## 3. Fixed source scope

The source is the project-owned candidate predicate already used by the weak-proxy challenge:

```python
def is_admin(user):
    return user.get("role") == "admin"
```

Public artifacts do not include the source body. They bind:

```text
source_id          = authorization-predicate-candidate-v1
path               = src/access.py
symbol             = is_admin
language           = python
parser             = stdlib-ast
target_cardinality = 1
source_sha256      = 7bfbd2d0a642c6d7f7da05ece2f4464d31df53a28d1ffed12c5752bc492d8965
ast_sha256         = 7c5be603e703a4893ead7ccc09fc76b88e3cd9d5603703d591d2ca80f439349b
```

The target is exactly the single return expression in the single top-level function named `is_admin`:

```text
target_id = 3cdfc367a78a09b257147fb236e80785d936177da231924f43e2d3d5fbd80e2e
```

A missing, duplicate, or structurally different target fails closed.

## 4. Semantic AST identity

Python's concrete AST classes can acquire optional fields across interpreter versions. DeltaWitness therefore does not hash `ast.dump()` output directly.

The adapter constructs a semantic AST document that:

- records node type and ordered declared fields;
- recursively records non-empty child values;
- omits `None` and empty-list optional fields;
- excludes source locations from semantic AST identity;
- hashes canonical JSON under `deltawitness.python-semantic-ast.v1`.

Target identity separately retains exact source positions and the source-byte digest.

This is a deliberately narrow compatibility rule for the fixed source and supported Python matrix. It is not a claim that arbitrary Python ASTs are stable across versions or implementations.

## 5. Frozen generic operator set

The generic operator order is normative and was selected before calibration execution:

| Order | Operator ID | Class | Transformation |
|---:|---|---|---|
| 1 | `return-constant-false-v1` | Boolean constant replacement | replace the return expression with `False` |
| 2 | `return-constant-true-v1` | Boolean constant replacement | replace the return expression with `True` |
| 3 | `comparison-eq-to-ne-v1` | relational replacement | replace the single `==` operator with `!=` |

Selection basis:

```text
minimal_boolean_constant_and_relational_replacement
```

The operators are intentionally small. They are not claimed to cover realistic Python faults, complete mutation classes, agent failure modes, or semantic intent.

## 6. Generation controls

Three non-generic records test catalog semantics:

| Order | Control ID | Required result | Purpose |
|---:|---|---|---|
| 4 | `duplicate-false-control-v1` | `duplicate` | retain a duplicate relation rather than counting the same mutant twice |
| 5 | `not-applicable-addition-control-v1` | `not_applicable` | retain absence of the requested target rather than dropping the record |
| 6 | `invalid-render-control-v1` | `invalid` | retain a compile-invalid rendering with a typed diagnostic |

These controls do not count as generic operator evidence.

## 7. Deterministic catalog

The catalog retains six ordered records:

```text
3 generated
1 duplicate
1 not_applicable
1 invalid
```

Generated mutant identities:

```text
return-constant-false-v1
5283f65eece7deda4935f369302db07c14fe45b0763b4ef4f6f86145cf4938f0

return-constant-true-v1
69dd4198555f3412b0dc48fac16b36903dd4ef7c4b9a5e926f950c9a40a6b8d4

comparison-eq-to-ne-v1
2ff6ef3a8313eb6e50096d16aab038a2202a3c346ea386fd673f00b6b1a7adf3
```

Control record identities:

```text
duplicate-false-control-v1
4303cb5b5390af25af0ab17c60f1f474e5038334742d7258a3b5f9d3390f2363

not-applicable-addition-control-v1
ea40ad03324d0ef4911d037b862c97def07a591df78c43ae2891bd2a58e590bd

invalid-render-control-v1
7ed7b0a99fbd82d2fa7ad6f5de20285994529123dcd1e7a8896e4d67e6a37689
```

Mutant identity binds:

- plan digest;
- operator ID;
- generation status;
- target ID;
- mutated source digest where bytes exist;
- semantic mutated-AST digest where parsing succeeds.

The catalog never publishes a mutated source body.

## 8. Historical weak-proxy mutant boundary

The fixed PR #34 mutant:

```text
nonempty-role-boolean-v1
```

is retained as a known challenge control, not as a member of the generic operator set:

```text
included_in_generic_operator_set      = false
counts_toward_operator_generalization = false
```

This prevents the next experiment from claiming generic operator success merely because it reuses the mutant whose survival motivated the experiment.

## 9. Paired calibration profiles

The same candidate source and generic mutant catalog will later be evaluated under two predeclared profiles.

### Strong authorization profile

```text
profile_id = strong-authorization-oracle-v1
role       = positive_control
selectors:
  test_access.AccessTests.test_admin_is_allowed
  test_access.AccessTests.test_viewer_is_denied
```

### Weak Boolean proxy profile

```text
profile_id = weak-boolean-proxy-v1
role       = negative_control
selectors:
  test_access.AccessTests.test_viewer_result_is_boolean
```

Reference development claim checks are separately declared:

```text
test_hidden_claim.HiddenClaimTests.test_admin_is_allowed
test_hidden_claim.HiddenClaimTests.test_viewer_is_denied
```

The paired design holds source and generic mutants constant while changing the selector profile. It does not make the reference checks a complete or independent oracle.

## 10. Future outcome taxonomy

No outcomes have been executed under this plan. A later, separately reviewed artifact may use only the frozen taxonomy:

```text
killed
survived
invalid
equivalent_review_required
indeterminate
```

The future execution contract currently fixes:

```text
execution_status               = not_implemented
retain_complete_mutant_table   = true
headline_score                 = null
universal_threshold            = null
merge_blocker_authorized       = false
```

The complete per-mutant table must precede any summary. A scalar must never hide surviving claim-violating mutants, invalid mutants, equivalent-review cases, or incomplete execution.

## 11. Integrity and fail-closed behavior

Plan and catalog verifiers do not trust stored labels or digests alone. They rebuild the complete canonical artifacts from fixed project-owned source and protocol constants.

After recomputing digests, the verifier still rejects changes to:

- source path, symbol, source or AST identity;
- operator order, ID, class, or target kind;
- selector profile or reference checks;
- known challenge-control status;
- generation outcome, duplicate relation, mutated identity, or summary;
- execution authorization, holdout selection, denominator eligibility, score, threshold, or merge policy.

Malformed roots, wrong container types, non-finite values, missing fields, and extra fields fail closed.

## 12. Direct baselines and prior-art boundary

Mutation testing, selective mutation, equivalent mutants, mutant subsumption, commit-relevant mutants, and AST transformations are established.

Direct implementation baselines for the later execution study include:

- **mutmut**, a maintained Python mutation-testing tool with a broad practical workflow;
- **Cosmic Ray**, which exposes explicit mutation operators and provider boundaries;
- a simpler fixed-mutant baseline;
- coverage-only evidence;
- current `M3_FOUR_STATE` plus declared-selector localization.

Primary research boundaries include:

- Jia and Harman, “An Analysis and Survey of the Development of Mutation Testing,” DOI `10.1109/TSE.2010.62`;
- Schuler and Zeller, “Covering and Uncovering Equivalent Mutants,” DOI `10.1002/stvr.1473`;
- Ojdanić et al., “On the use of commit-relevant mutants,” *Empirical Software Engineering* 2022.

No novelty claim is made for mutation operators, AST rewriting, duplicate-mutant detection, equivalent-mutant review, or paired test profiles.

The narrower DeltaWitness question is whether a predeclared, integrity-bound, claim-scoped mutant table adds useful evidence beyond exact state replay and selector provenance. That question remains unanswered until execution and calibration are separately reviewed and performed.

## 13. Safety and privacy boundary

This revision only:

- parses fixed project-owned Python bytes;
- applies fixed in-memory AST transformations;
- unparses generated syntax;
- compiles generated bytes without executing them;
- emits digests and typed generation records.

It adds no:

- mutant execution;
- test execution beyond existing unrelated CI tests;
- external repository or benchmark instance;
- package-manager or mutation-engine invocation;
- network access;
- telemetry or upload;
- repository permission;
- secret;
- containment claim.

Public artifacts exclude source and mutant bodies, raw output, tracebacks, absolute paths, usernames, credentials, environment values, and private endpoints. Digests can still fingerprint low-entropy values and are not a redaction or authentication mechanism.

## 14. Falsification and redesign

Narrow or abandon this design if:

- supported Python versions do not reproduce the exact plan, target, mutant, and catalog identities;
- AST round-tripping changes semantics outside the fixed target;
- target identity depends on unstable discovery order;
- duplicate, invalid, or not-applicable records cannot be retained deterministically;
- generic operators merely restate the known PR #34 control;
- operator choice dominates later results;
- a simpler fixed-mutant or established-tool baseline provides the same evidence at lower cost;
- later execution requires changing operators, profiles, labels, thresholds, or exclusions after outcomes are visible.

A negative calibration result is valid and must not trigger post-hoc operator repair.

## 15. Claim boundary

A valid plan and catalog establish only that one minimal operator set, paired selector-profile design, exact AST target, and six generation records were frozen and reproduced before mutation-test outcomes.

They do not establish:

- that any mutant is killed or survives under either profile;
- mutation adequacy, mutation score validity, or complete oracle strength;
- relevance to real coding-agent patches;
- quality of any model or agent;
- ecological effectiveness or superiority;
- merge-blocker authorization;
- containment or producer authentication;
- protocol freeze, holdout validity, independent reproduction, Gate 0 or Gate 1 completion;
- production readiness or scientific novelty.

## 16. Next gate

The next change may execute only these frozen generic mutants and the separately labeled known challenge control against the two frozen selector profiles and reference checks, retaining every typed outcome and cost.

That execution requires a new red-first result contract. This plan alone cannot authorize it.
