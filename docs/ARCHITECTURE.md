# Architecture

## Layered assurance model

DeltaWitness separates questions often collapsed into one green check:

```text
state identity
    -> process execution
    -> outcome semantics
    -> executable change witness
    -> declared witness-test provenance
    -> oracle relevance
    -> oracle strength
    -> frozen mutation design
    -> calibrated mutation evidence
    -> bounded intervention influence
    -> broader patch causality
    -> environment provenance
    -> producer authenticity
    -> policy decision
```

Version `0.0.3` advances through bounded path-level intervention influence. Unreleased DW-001 infrastructure adds deterministic study contracts, declared-selector localization, development-only negative controls for oracle relevance and strength, and a frozen pre-execution mutation plan/catalog. The mutation plan currently generates and compiles fixed project-owned mutants but executes none of them. None of these layers establishes complete patch correctness, mutation adequacy, environment reproducibility, producer authentication, ecological effectiveness, or deployment authorization.

No LLM judge appears in the trust path. Models may help design claims or fixtures outside that path, but current decisions are derived from explicit configuration, immutable Git objects, process observations, strict receipts, deterministic state projections, declared selectors, fixed negative controls, frozen mutation identities, exact coalition enumeration, and versioned contracts.

## Canonical four-state trust path

DeltaWitness receives a repository, base ref, candidate ref, and TOML specification.

1. Resolve refs to immutable commits.
2. Require base ancestry and a clean repository.
3. Enumerate changed paths through NUL-delimited Git output.
4. Classify every changed path exactly once and reject unsafe, overlapping, submodule, or changed-link entries.
5. Create detached state worktrees.
6. Materialize `BB`, `BC`, `CB`, and `CC` with exact trees and deterministic hybrid commits.
7. Restore and clean each state before every claim.
8. Derive an invocation binding over claim, command, specification, observer, state, tree, and commit.
9. Execute without a shell under a reduced environment.
10. Classify the process through explicit exit classes or a typed outcome receipt.
11. Require receipt/process agreement when typed observation is enabled.
12. Preserve timeout, unknown exit, missing receipt, inconclusive receipt, or contradiction as incomplete execution.
13. Record state identities, observer evidence, output digests, and integrity digests.

## Canonical state semantics

| State | Narrow observation |
|---|---|
| `base_base` | Does the declared baseline behave as expected under base tests? |
| `base_candidate` | Do candidate tests distinguish base implementation behavior? |
| `candidate_base` | Does candidate implementation preserve base-test behavior? |
| `candidate_candidate` | Does the final candidate satisfy candidate tests? |

A matching matrix is evidence within the declared command and test scope. It does not establish which test caused failure, oracle relevance, oracle strength, implementation minimality, absence of untested regressions, or production safety.

## Observer architecture

### `exit-code-v1`

The default observer maps process return codes through each claim's disjoint `pass_exit_codes` and `fail_exit_codes`. A timeout or every other exit code makes the observation incomplete.

This mode cannot distinguish multiple causes sharing the same nonzero code. Assertion, import, setup, dependency, or harness failure can collapse into one configured `fail` class.

### `outcome-receipt-v1`

A receipt-aware command receives:

```text
DELTAWITNESS_RECEIPT_PATH
DELTAWITNESS_RECEIPT_BINDING
```

The binding covers claim, command, specification, observer, state, tree, and commit. A cooperating producer writes one bounded strict JSON receipt.

DeltaWitness accepts only:

```text
receipt passed       + configured pass exit -> pass
receipt test_failure + configured fail exit -> fail
```

Every other receipt outcome or receipt/exit contradiction becomes `error` and makes the observation incomplete.

Receipt validation checks exact fields, strict UTF-8 JSON, duplicate keys, bounded regular-file semantics, binding equality, producer syntax, count bounds, count totals, and outcome/count consistency.

Receipt v1 distinguishes assertion failure from generic test error. It does not distinguish every error subtype, identify the assertion relevant to a claim, measure assertion strength, or authenticate the producer. The binding is visible to the tested process.

## Declared witness-test localization

DW-001 can bind one claim to exact standard-library unittest selector identities and replay those selectors under exact `BC` and `CC` Git states.

A declaration fixes:

- source specification and claim identity;
- adapter and adapter version;
- ordered unique logical-test selectors;
- adapter-derived commands;
- aggregate rule;
- declaration digest.

The localization runner reconstructs the exact states from the source report, executes each selector with typed receipts, and records one classification:

```text
discriminating
non_discriminating
candidate_invalid
indeterminate
```

A valid `discriminating` classification means the exact predeclared selector produced typed assertion failure in `BC` and pass in `CC`. It does not establish that the selector expresses the intended behavior or rejects plausible incorrect implementations.

Architecturally:

```text
suite-level failure provenance
    != exact selector provenance
    != semantic oracle relevance
    != oracle strength
```

## Controlled wrong-reason import pair

DW-001 includes the fixed owned-synthetic observer probe:

```text
wrong-reason-base-import-failure
```

Candidate tests import a candidate-introduced symbol before assertions. Under exit-code observation, `BC` appears as semantic fail and all state-set methods accept. Under typed observation, `BC` is preserved as generic test error and methods requiring it become indeterminate.

```text
O0: BB / BC / CB / CC = pass / fail  / pass / pass
O1: BB / BC / CB / CC = pass / error / pass / pass
```

`import_error` is fixed fixture ground truth; receipt v1 reports only `test_error`. The pair isolates one observer distinction and does not estimate prevalence.

## Controlled unrelated-assertion negative control

The fixed family:

```text
wrong-reason-unrelated-assertion
```

contains claim-facing and collateral behaviors. A claim-facing viewer assertion passes on both implementations, while a separate collateral `version_label == "v2"` assertion is the sole source of `BC = fail`.

Both observer arms produce a canonical complete matrix and all `M0`–`M3` methods accept. Typed observation correctly records a genuine assertion failure. Declared-selector localization then classifies the claim-facing selector as non-discriminating.

This establishes one limitation:

```text
real assertion failure
    + typed outcome
    + canonical four-state witness
    != claim-oracle relevance
```

## Controlled weak-proxy-oracle negative control

The fixed family:

```text
weak-proxy-oracle
```

moves beyond suite-level provenance. Its declared selector is itself genuinely fail-to-pass and is localized as `discriminating`.

Base implementation returns the raw role value; candidate returns whether role equals `admin`. The declared viewer test asserts only that the result is a Boolean:

```python
self.assertIsInstance(is_admin({"role": "viewer"}), bool)
```

Current evidence under both observer arms is canonical:

```text
BB / BC / CB / CC  = pass / fail / pass / pass
M0 / M1 / M2 / M3 = accept / accept / accept / accept
localization       = supported / discriminating
```

A fixed claim-violating mutant:

```python
def is_admin(user):
    return bool(user.get("role"))
```

also passes the declared selector while authorizing a viewer. A separately fixed hidden development claim check passes on candidate and fails on the mutant.

The challenge executes five shell-free typed controls and binds exact source/test bytes, selector commands, invocation bindings, receipt evidence, current matrix/projection/localization sources, and two integrity digests.

Architecturally:

```text
exact declared-selector fail-to-pass
    != sufficient oracle strength
```

This is one development-only counterexample. It is not a mutation score, hidden-test benchmark, ecological agent evaluation, or general oracle-strength detector.

Complete boundary:

```text
research/DW-001/WEAK_ORACLE_CHALLENGE.md
research/DW-001/schema/weak-oracle-challenge.schema.json
src/deltawitness/dw001_oracle_challenge.py
```

## Frozen claim-scoped mutation design

The next Gate 1 layer is split deliberately into **design/generation** and **execution/calibration**. The current implementation completes only the first half.

```text
fixed owned-synthetic candidate source
    -> semantic AST identity
    -> exact return-expression target
    -> frozen outcome-blind operator set
    -> deterministic generated/duplicate/invalid/not-applicable records
    -> paired selector profiles
    -> future result contract (not implemented)
```

Canonical artifacts:

```text
research/DW-001/claim-scoped-mutation-plan.v1.json
research/DW-001/claim-scoped-mutant-catalog.v1.json
research/DW-001/schema/claim-scoped-mutation-plan.schema.json
research/DW-001/schema/claim-scoped-mutant-catalog.schema.json
src/deltawitness/dw001_mutation_plan.py
```

### Fixed source and target

The plan binds one project-owned candidate source by SHA-256 and a versioned semantic-AST digest. The adapter requires exactly one top-level function named `is_admin` and exactly one return-expression target.

Source identity and target identity remain distinct:

- source identity binds exact UTF-8 source bytes;
- semantic AST identity binds node kinds and non-empty declared fields while excluding source locations and empty optional fields;
- target identity binds source digest, path, symbol, node kind, cardinality, and exact source positions.

This compatibility rule is intentionally narrow. It is tested across Python 3.11–3.14 for the fixed source and is not a universal cross-version Python AST canonicalization claim.

### Frozen generic operators

The exact order is:

```text
return-constant-false-v1
return-constant-true-v1
comparison-eq-to-ne-v1
```

These operators are selected before mutation outcomes. They represent only a minimal Boolean/relational design and do not claim completeness or ecological realism.

Three separate generation controls require the catalog to retain:

```text
duplicate-false-control-v1          -> duplicate
not-applicable-addition-control-v1  -> not_applicable
invalid-render-control-v1           -> invalid
```

Duplicate, invalid, and not-applicable records cannot be silently discarded or counted as generated generic mutants.

### Historical challenge-control separation

The known `nonempty-role-boolean-v1` mutant from the weak-proxy challenge is retained as a separate historical control:

```text
included_in_generic_operator_set      = false
counts_toward_operator_generalization = false
```

This prevents a later calibration from claiming generic operator success by reusing the exact mutant that motivated the experiment.

### Paired profiles

The plan freezes two selector profiles over the same source and generic mutant catalog:

```text
strong-authorization-oracle-v1
weak-boolean-proxy-v1
```

Reference development claim checks are declared separately before execution. The paired design isolates selector-profile differences, but the reference checks are not assumed complete or independent.

### No execution semantics yet

The current adapter parses, transforms, unparses, reparses, and compiles fixed project-owned bytes. It does not run mutants or tests against mutants.

The future taxonomy is frozen as:

```text
killed
survived
invalid
equivalent_review_required
indeterminate
```

but no record currently carries one of those execution outcomes. The plan fixes:

```text
execution_authorized       = false
headline_score             = null
universal_threshold        = null
merge_blocker_authorized   = false
holdout_selected           = false
primary_denominator_eligible = false
```

A later result layer requires a separate red-first contract and cannot rewrite this plan after outcomes are visible.

Architecturally:

```text
frozen operator and mutant identity
    != mutant execution
    != mutation evidence
    != mutation adequacy
    != merge policy
```

## Exact patch-influence trust path

`deltawitness influence` first runs the canonical matrix and proceeds only from a complete supported canonical witness.

For sorted changed-code paths `N = [p0, ..., p(n-1)]`, the current protocol requires `1 <= n <= 8` and evaluates every `2^n` coalition under base and candidate test worlds.

For each coalition:

1. restore base;
2. hold candidate documentation constant;
3. overlay candidate code only for selected paths;
4. write exact implementation tree and deterministic commit;
5. execute base tests;
6. overlay candidate tests;
7. write exact candidate-test tree and commit;
8. execute candidate tests;
9. classify `supported`, `unsupported`, or `indeterminate`.

Any timeout, observer error, import/setup/infrastructure failure, missing receipt, or unknown exit makes a coalition indeterminate. Incomplete execution is never negative evidence.

## Endpoint anchors and exact game

Four endpoint anchors compare empty/full influence states with canonical `BB`, `BC`, `CB`, and `CC` semantics. Full trees must match canonical candidate-side trees. Empty tree equality is additionally required when no documentation changed.

Any incomplete coalition or inconsistent anchor withholds all exact metrics.

When release conditions hold, DeltaWitness computes:

- every inclusion-minimal supported coalition;
- necessity and standalone sufficiency;
- positive and negative marginal swings;
- exact rational Shapley allocation;
- normalized Banzhaf influence;
- pairwise Banzhaf interaction;
- monotonicity diagnostics.

These metrics describe one declared Boolean witness over whole changed paths. They do not establish semantic correctness, blame, severity, ownership, oracle relevance, oracle strength, or universal causality.

## State and environment lifecycle

Canonical hybrids and intervention states are local Git objects without refs. Each claim begins from reset/clean state. Deterministic metadata makes identical state construction reproducible within the same Git object model.

The runner preserves only a small platform environment, uses isolated temporary homes/caches, and passes additional variables only when explicitly listed. Git subprocesses disable external repository/index/object overrides, replacement objects, global configuration, prompts, and LFS smudging.

Repository-local configuration, attributes, filters, unchanged links, the shared object database, operating system, binaries, dependencies, kernel, hardware, clock, network, and external services remain outside the bound state model.

This is not a filesystem, network, process, or resource sandbox.

## DW-001 research artifact path

```text
fixture descriptor
    -> deterministic owned-synthetic repository
    -> fixture identity
    -> scenario manifest
    -> fixture-manifest binding
    -> strict matrix report
    -> nested-method projection
    -> result record
```

Optional development evidence may extend that path:

```text
claim-witness declaration
    -> selector localization
    -> fixed weak-oracle mutation challenge
```

A separate pre-execution research path freezes future mutation inputs:

```text
claim-scoped mutation plan
    -> deterministic mutant catalog
    -> future typed result table (not implemented)
```

### Fixture descriptor and identity

The descriptor fixes supported family, control role, observer arm, command, timeout, paths, expected states, failure causes, and expected `M0`–`M3` decisions. Method labels are recomputed from states.

The generator creates fixed source/test/specification bytes and exact Git objects. Identity records descriptor, generator, observer, Git, path, state, method, and specification identities. Public identity verification recomputes descriptor-derived specification bytes. Repository correspondence remains a separate materialized-fixture check.

The pre-freeze supported-family registry contains six fixed probes. Existing v1 artifacts remain valid, but older verifiers may reject newer-family artifacts. Exact schema and implementation commits are required until freeze. The historical ten-arm pilot remains fixed to its sealed five-family population.

### Scenario manifest and fixture binding

The scenario manifest owns partition, provenance, authorization, ground truth, environment assumptions, reviewer declarations, and denominator eligibility.

Because manifest v1 predates fixture identity, the separate binding verifies common study, scenario, Git commit, path, observer, command, state, method, family, and specification relations without repurposing manifest fields.

`relation_scope` distinguishes verified relations, manifest-owned governance values, and fixture-only tree/specification identities.

A valid binding cannot authenticate sources, prove creation time, validate reviewer claims, establish oracle relevance or strength, or make development material confirmatory.

### Projection, localization, challenge, mutation design, and result

The projection exposes each nested method only to its declared state slice while retaining verified source identities.

Localization exposes exact selector outcomes under `BC` and `CC`, but not semantic intent.

The weak-oracle challenge adds one fixed mutation counterexample over verified current evidence, but not a calibrated mutation analysis.

The mutation plan/catalog freeze one source, target, operator set, selector-profile design, and deterministic generation table. They contain no mutation-test outcomes.

The result binds expected/observed method decisions, source digests, exclusions, deviations, denominator membership, and explicit cost or missingness.

These are research controls and development evidence, not ecological effectiveness results.

## DW-001 development mechanism pilot lifecycle

The sealed five-family synthetic pilot extends the per-case artifact path with one population plan and one retained index/archive:

```text
committed ten-arm plan
    -> derive exact descriptors and declarations
    -> execute each case in a disposable repository
    -> verify every per-case artifact and relation
    -> derive method/localization summaries
    -> derive controlled contrasts
    -> construct complete development index
    -> self-verify staged bundle
    -> publish only after complete success
    -> pack canonical JSON archive
    -> reconstruct and reverify archive before acceptance
```

The plan fixes exact case identities, family and observer arms, expected states and methods, selectors, localization status, analysis contrasts, cost fields, denominator exclusion, and prohibitions on headline scoring and ecological inference.

The runner accepts no free-form fixture code, tests, commands, selectors, expected labels, exclusions, or denominator decisions.

### Staging and publication

The public pilot runner requires an absent final output path. It stages adjacent to the destination, verifies every case and the exact file set, and publishes through one same-filesystem rename only after complete success. Failure leaves the final output absent.

This does not establish trust in destination ancestors, mounts, operating system, Python, Git, or the runner image.

### Canonical archive

The text-only archive records sorted unique relative JSON paths, every embedded object, per-file digests, semantic index digest, and complete archive digest. Verification requires the exact sealed file set, reconstructs the bundle, and reruns artifact-specific and cross-artifact checks.

The canonical fixed-pilot archive is retained at:

```text
research/DW-001/development-pilot-archive.v1.json
```

The pilot emits:

```text
headline_score                = null
ecological_inference_allowed  = false
```

All method records remain development-only and primary-denominator ineligible. The pilot validates the evidence pipeline for fixed mechanisms; it does not estimate effectiveness on real patches.

## Report and artifact schemas

Matrix schema `0.3` records observer protocol, invocation binding, receipt digest/outcome, producer, counts, stable observer error, exact state objects, witness digest, and report digest.

Influence schema records path order, canonical matrix reference, anchors, every coalition, exact Git objects, observations, statuses, and exact metrics where release conditions hold.

DW-001 adds strict schemas and semantic verifiers for:

- projection;
- fixture descriptor and identity;
- fixture-manifest binding;
- scenario manifest and result;
- claim-witness declaration and localization;
- weak-oracle challenge;
- claim-scoped mutation plan and deterministic mutant catalog;
- development-pilot plan, index, and archive;
- design-only ecological source universe.

Schemas define structural interoperability. Python verifiers remain authoritative for semantic recomputation and cross-artifact relations.

## Integrity model

Current artifacts use unkeyed canonical digests, including:

- matrix witness and report digests;
- influence semantic and report digests;
- descriptor, identity, binding, projection, manifest, result, declaration, localization, and weak-oracle challenge digests;
- mutation-plan and mutant-catalog digests;
- pilot-plan, pilot-index, pilot-archive, and ecological source-universe digests.

The mutation adapter also derives exact source, semantic-AST, target, mutated-source, mutated-AST, and mutant identities. These identify one frozen design; they do not authenticate who selected it or prove its adequacy.

All current digests detect modification only against separately trusted sources or expected values. An actor able to replace an entire chain can recompute every digest.

Signing, producer identity, DSSE, in-toto, Sigstore, SCITT, immutable timestamping, and transparency registration remain separate future layers. A signature authenticates bytes, not semantic truth.

## Remaining separation of concerns

DeltaWitness intentionally refuses substitution among evidence layers:

- process failure does not imply assertion failure;
- generic typed error does not imply a precise error subtype;
- typed assertion failure does not imply claim relevance;
- exact selector provenance does not imply oracle strength;
- one surviving mutant does not define mutation adequacy;
- a frozen or compiled mutant catalog does not establish mutation outcomes;
- duplicate, invalid, or not-applicable records cannot be silently discarded;
- a canonical four-state matrix does not prove patch correctness;
- exact coalition enumeration does not prove complete causality;
- a fixture identity does not prove environment reproducibility;
- a fixture-manifest binding does not validate governance declarations;
- a verified synthetic pilot does not establish ecological effectiveness;
- an unkeyed digest does not authenticate a producer;
- a matching witness does not authorize deployment;
- controlled synthetic cases do not establish general observer or method superiority.

Future work may add a separate typed mutation-result table over the frozen plan, calibrated mutation and coverage evidence, assertion-delta analysis, over-mocking controls, repeated stochastic execution, reproducible containment, signed provenance, ecological baselines, external policy evaluation, and independent reproduction. Each layer must retain its own claim boundary and explicit positive and negative controls.
