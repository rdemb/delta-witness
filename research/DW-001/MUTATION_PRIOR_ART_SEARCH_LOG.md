# DW-001 Claim-Scoped Mutation Prior-Art Search Log

**Search date:** 2026-08-16  
**Status:** reproducible initial search log for the pre-execution mutation-design prerequisite; not an exhaustive systematic review and not evidence of novelty.

## 1. Search question

The search was scoped to the immediate engineering and methodological question:

> Before executing any mutation campaign, what existing Python tooling and mutation-testing literature are the nearest baselines for a deterministic operator plan, exact mutant identity, duplicate/invalid/not-applicable retention, and paired oracle-profile calibration?

The search did not attempt to establish that DeltaWitness is the first system to combine these ideas. It did not cover every mutation-testing implementation, language ecosystem, dissertation, workshop paper, commercial tool, or unpublished system.

## 2. Search channels and queries

### GitHub repository search

Queries:

```text
mutmut Python mutation testing
Cosmic Ray Python mutation testing
```

The search was restricted to public repositories and followed the apparent upstream projects rather than forks.

### Literature identifiers and topics

Queries and title-level review covered:

```text
mutation testing survey equivalent mutants
selective mutation mutant subsumption
commit-relevant mutants mutation testing
Python ast NodeTransformer fix_missing_locations unparse
```

Primary starting references:

- Jia and Harman, “An Analysis and Survey of the Development of Mutation Testing,” IEEE Transactions on Software Engineering, DOI `10.1109/TSE.2010.62`;
- Schuler and Zeller, “Covering and Uncovering Equivalent Mutants,” Software Testing, Verification and Reliability, DOI `10.1002/stvr.1473`;
- Ojdanić et al., “On the use of commit-relevant mutants,” Empirical Software Engineering, 2022;
- Python standard-library `ast` documentation for `NodeTransformer`, `fix_missing_locations`, `unparse`, and compiler-location requirements.

The references above were selected because they directly bound mutation operators, equivalent/redundant mutants, commit relevance, and the chosen AST implementation mechanism. They are not a complete bibliography for Gate 1.

## 3. Direct implementation baselines

### mutmut

```text
repository     = boxed/mutmut
default branch = main
reviewed SHA   = 5cb006d3ddeec39d40fb1f2398a77728268b7812
reviewed tree  = fc3c56793f3e9b961daeae1c482aee4f6a1daf7b
README blob    = 1e76b4fda0d281371d577cb63fdb49690e55253d
```

Observed baseline properties from the reviewed upstream README:

- practical Python mutation-testing workflow;
- mutant execution through pytest;
- incremental result persistence;
- test selection intended to reduce execution cost;
- parallel execution and an interactive result browser;
- optional coverage-based mutation filtering;
- optional type-checker filtering of generated mutants;
- use of external runtime dependencies and a fork-based execution model.

Direct relevance:

- mutmut is the strongest practical Python baseline for a later executable mutation campaign;
- its coverage and type-checker filtering demonstrate that mutant inclusion policy materially changes the resulting population;
- its cached, selected, and executable workflow is broader than the present DeltaWitness pre-execution identity problem.

Why it was not integrated in this prerequisite:

- issue #37 must freeze source scope, operator order, profiles, identities, and generation-status semantics before any outcomes;
- importing mutmut now would also import its own operator catalog, selection, cache, execution, pytest, dependency, and platform assumptions;
- the present result must remain a no-execution, standard-library-only design artifact;
- later issue #35 execution must compare against a pinned mutmut baseline rather than silently treating a custom implementation as the only baseline.

### Cosmic Ray

```text
repository     = sixty-north/cosmic-ray
default branch = master
reviewed SHA   = caf9a3193606ddd90cc37126b7fa95acefc47695
reviewed tree  = 217a503aee4b981bbd305eff2d602265f641a0b3
README blob    = 3289214724ae7b03106dcb702b03a879334a9096
```

Observed baseline properties from the reviewed upstream README and repository organization:

- Python mutation testing by applying small source changes and running the suite for each change;
- an explicit standalone mutation-testing tool rather than a patch-witness subsystem;
- a broader execution and orchestration concern than the current pre-execution catalog.

Direct relevance:

- Cosmic Ray is a direct executable Python mutation-testing baseline;
- its operator/provider architecture is relevant to future adapter and operator-version boundaries;
- its execution semantics and dependencies must be pinned explicitly before a fair comparison.

Why it was not integrated in this prerequisite:

- this change must not execute tests or mutants;
- the current contract evaluates whether exact generation identities can be frozen independently of an execution engine;
- later calibration should compare one pinned Cosmic Ray configuration against the frozen custom catalog where operator correspondence is meaningful.

## 4. Standard-library AST baseline

The implementation baseline selected for issue #37 is Python's standard-library `ast` module:

```text
parse
    -> locate one exact return expression
    -> replace a fixed AST node/operator
    -> fix_missing_locations
    -> unparse
    -> compile
    -> reparse
```

Reasons for selection:

- no new runtime or development dependency;
- exact control over the three predeclared generic operators;
- generation can be completed without importing or executing tested code;
- compile-invalid and not-applicable records can be retained explicitly;
- the small fixed source makes target cardinality and cross-version identities testable on Python 3.11–3.14.

Limitations:

- `ast.unparse` is not a source-preserving renderer;
- AST classes and optional fields can evolve across Python versions;
- AST equality is not program equivalence;
- compile success is not behavioral validity;
- the implementation is intentionally source-specific and is not a general Python mutation engine.

To reduce avoidable version drift, DeltaWitness uses a versioned semantic-AST representation that records node types and non-empty declared fields while excluding locations and empty optional fields. Exact source bytes and target locations remain separate identities. This compatibility rule is tested only for the fixed source and supported Python matrix.

## 5. Nearest conceptual baselines

| Concern | Established baseline | Current DeltaWitness difference under issue #37 |
|---|---|---|
| Mutation generation | mutmut, Cosmic Ray, other mutation engines | exactly three frozen generic operators over one fixed owned-synthetic source; no test execution |
| AST rewriting | Python `ast.NodeTransformer` and related APIs | versioned semantic-AST, exact target identity, deterministic catalog relation |
| Equivalent/redundant mutants | equivalent-mutant and mutant-subsumption literature | one duplicate generation control retained explicitly; no equivalence claim |
| Selective mutation | selective and commit-relevant mutation research | outcome-blind fixed source/symbol scope; no claim that the scope is optimal |
| Mutation score | standard killed/total summaries | deliberately absent; full future per-mutant table required first |
| Oracle comparison | mutation testing under one suite | paired strong/weak selector profiles over identical source and generic mutant identities |
| Known challenge mutant | hand-designed counterexample | retained separately and excluded from generic operator generalization |
| Integrity | tool databases, files, or logs | canonical plan/catalog digests plus semantic reconstruction; still unkeyed and unauthenticated |

## 6. Exact difference under test

The issue #37 contribution is not “mutation testing for Python.”

The narrower pre-execution difference under test is:

1. freeze one source scope and exact AST target;
2. freeze an outcome-blind operator order before execution;
3. derive exact source, semantic-AST, target, and mutant identities;
4. retain generated, duplicate, invalid, and not-applicable records;
5. keep a previously observed challenge mutant outside generic operator evidence;
6. freeze paired strong/weak selector profiles over identical generic mutants;
7. prohibit scores, thresholds, blockers, holdout selection, and mutation execution;
8. semantically reconstruct the committed plan and catalog across Python 3.11–3.14.

Whether this adds useful evidence over mutmut, Cosmic Ray, a fixed-mutant baseline, or coverage-only evidence remains an open empirical question for issue #35.

## 7. Falsification and update rule

This log must be expanded or corrected if:

- a direct public tool already provides the same pre-execution source/target/operator/profile relation and deterministic cross-artifact verification with lower complexity;
- a reviewed mutmut or Cosmic Ray version exposes a directly reusable exact operator identity and catalog contract;
- the selected three operators are later found to have been chosen using hidden mutation outcomes;
- Python 3.11–3.14 cannot reproduce the committed identities;
- additional prior art materially narrows the claimed engineering difference.

Future searches must append dates, queries, exact source revisions, and changes in interpretation. They must not rewrite this log to conceal earlier omissions.

## 8. Claim boundary

This search log supports only an initial direct-baseline boundary for issue #37.

It does not establish:

- an exhaustive systematic review;
- scientific novelty;
- superiority over mutmut, Cosmic Ray, or any other tool;
- correctness or completeness of the operator set;
- mutation adequacy;
- execution feasibility on real repositories;
- ecological or held-out effectiveness.
