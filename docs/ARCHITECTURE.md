# Architecture

## Layered assurance model

DeltaWitness separates questions often collapsed into one green check:

```text
state identity
    -> process execution
    -> outcome semantics
    -> executable change witness
    -> bounded intervention influence
    -> oracle relevance
    -> oracle strength
    -> broader patch causality
    -> environment provenance
    -> producer authenticity
    -> policy decision
```

Version `0.0.3` advances through bounded path-level intervention influence. It does not claim oracle relevance, complete patch causality, environment reproducibility, producer authentication, or deployment authorization.

DW-001 adds research controls around fixture identity, pre-execution ground truth, controlled observer arms, nested baseline projection, and artifact relations. Those controls make a future comparison auditable; they do not strengthen the underlying behavioral evidence beyond what the matrix and observer actually record.

No LLM judge appears in the trust path. Models may help design claims or fixtures outside that path, but decisions are derived from explicit configuration, immutable Git objects, process observations, strict receipts, deterministic state projections, exact coalition enumeration, and versioned contracts.

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

A matching matrix is evidence within the declared command and test scope. It does not establish oracle strength, implementation minimality, absence of untested regressions, or production safety.

## Observer architecture

### `exit-code-v1`

The default observer maps process return codes through each claim's disjoint `pass_exit_codes` and `fail_exit_codes`. A timeout or every other exit code makes the observation incomplete.

This mode cannot distinguish multiple causes sharing the same nonzero code. A test assertion, import error, setup error, dependency failure, or harness failure can therefore collapse into the same configured `fail` class.

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

Receipt v1 distinguishes assertion failure from generic test error. It does not distinguish every error subtype, identify the assertion relevant to a claim, or authenticate the producer. The binding is visible to the tested process.

## Controlled wrong-reason import pair

DW-001 includes the fixed owned-synthetic observer probe:

```text
wrong-reason-base-import-failure
```

The base implementation lacks `normalize_role`. Candidate tests import `normalize_role` before executing any intended assertion. Candidate implementation supplies the symbol and passes the tests. Base tests pass under both implementation worlds.

The pair holds constant:

- scenario identifier;
- family and control role;
- generator and template;
- base/candidate source bytes;
- base/candidate test bytes;
- path categories and timeout.

Only observer-derived descriptor fields differ: observer, observer ID, command, derived state semantics, derived method semantics, specification bytes, and resulting digests/Git identities.

### Exit-code arm

```text
BB / BC / CB / CC  = pass / fail / pass / pass
M0 / M1 / M2 / M3 = accept / accept / accept / accept
```

The nonzero import-error process is interpreted only through configured `fail` status. The matrix therefore looks canonical and complete even though the intended candidate assertion was never evaluated on the base.

### Typed-receipt arm

```text
BB / BC / CB / CC  = pass / error / pass / pass
M0 / M1 / M2 / M3 = accept / indeterminate / indeterminate / indeterminate
```

The unittest producer records zero assertion failures and at least one error, emitting `test_error`. DeltaWitness preserves incomplete evidence instead of treating it as semantic `fail`.

`import_error` is fixed fixture ground truth for the exact synthetic bytes. It is not inferred from the generic runtime receipt. This separation prevents a claim that receipt v1 diagnoses import, setup, or collection subtypes.

The pair is a development mechanism probe, not an effectiveness estimate.

## Controlled unrelated-assertion negative control

DW-001 also includes:

```text
wrong-reason-unrelated-assertion
```

The fixture contains two behavior dimensions:

```text
claim-facing: is_admin(viewer)
collateral:   version_label()
```

Base code keeps the buggy role rule and returns `v1` from `version_label()`. Candidate code repairs the role rule and returns `v2`.

Candidate tests contain:

- a viewer test that executes claim-facing behavior but asserts only that the result is a Boolean, so it passes on both implementations;
- an unrelated assertion that `version_label() == "v2"`, which is the sole `BC` failure source.

Normative direct controls execute the claim-facing test against both code versions and require both to pass. They then execute the complete candidate suite against base code, require failure, remove the exact collateral assertion, and require the remaining suite to pass.

Both observer arms produce:

```text
BB / BC / CB / CC  = pass / fail / pass / pass
M0 / M1 / M2 / M3 = accept / accept / accept / accept
```

The typed arm correctly records:

```text
receipt outcome = test_failure
failures >= 1
errors = 0
```

This is an intentional negative result. A real assertion failure and canonical four-state witness do not identify whether the failing assertion is relevant to the declared claim.

Architecturally:

```text
outcome semantics
    != oracle relevance
```

A future test-integrity layer must therefore remain separate, must be evaluated against this negative control, and cannot use an LLM explanation as an unverified authority.

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

These metrics describe one declared Boolean witness over whole changed paths. They do not establish semantic correctness, blame, severity, ownership, oracle relevance, or universal causality.

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

### Fixture descriptor and identity

The descriptor fixes supported family, control role, observer arm, command, timeout, paths, expected states, failure causes, and expected `M0`–`M3` decisions. Method labels are recomputed from states.

The generator creates fixed source/test/specification bytes and exact Git objects. Identity records descriptor, generator, observer, Git, path, state, method, and specification identities. Public identity verification recomputes descriptor-derived specification bytes. Repository correspondence remains a separate materialized-fixture check.

The pre-freeze supported-family registry contains five fixed probes. Existing v1 artifacts remain valid, but older verifiers may reject newer-family artifacts. Exact schema and implementation commits are required until freeze.

### Scenario manifest and fixture binding

The scenario manifest owns partition, provenance, authorization, ground truth, environment assumptions, reviewer declarations, and denominator eligibility.

Because manifest v1 predates fixture identity, the separate binding verifies common study, scenario, Git commit, path, observer, command, state, method, family, and specification relations without repurposing manifest fields.

`relation_scope` distinguishes verified relations, manifest-owned governance values, and fixture-only tree/specification identities.

A valid binding cannot authenticate sources, prove creation time, validate reviewer claims, establish oracle relevance, or make development material confirmatory.

### Projection and result

The projection exposes each nested method only to its declared state slice while retaining verified source identities. The result binds expected/observed decisions, source digests, exclusions, deviations, denominator membership, and explicit cost or missingness.

These are research controls, not empirical results.

## DW-001 development mechanism pilot lifecycle

The fixed synthetic development pilot extends the per-case artifact path with one sealed population plan and one retained corpus index/archive:

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

### Sealed plan

The plan fixes:

- protocol and evidence-producing implementation commits;
- exact ordered case IDs;
- family, observer, scenario, role, partition, and denominator fields;
- descriptor and specification digests;
- expected states and `M0`–`M3` decisions;
- declared logical-test selectors and expected localization status;
- analysis contrast IDs;
- cost fields and missingness policy;
- prohibition of headline scoring and ecological inference.

The runner accepts no free-form fixture code, tests, commands, selectors, expected labels, exclusions, or denominator decisions.

### Staging and publication

The runner uses a staging directory adjacent to the requested destination. It:

1. verifies the plan before creating final output;
2. executes and verifies every case;
3. refuses aggregate analysis when any case or relation is invalid;
4. writes only strict public-safe JSON documents;
5. verifies the complete staged bundle;
6. publishes the final directory only after self-verification;
7. removes staging output on failure.

A non-empty or symbolic-link destination is rejected. This does not establish trust in destination ancestors, mounts, the operating system, Python, Git, or the GitHub runner.

### Canonical archive

The archive is a text-only transport and retention format. It records:

- sorted unique relative JSON paths;
- every embedded JSON object;
- a digest for every embedded file record;
- plan and pilot semantic digests;
- a complete archive digest.

Archive verification reconstructs the directory bundle and reruns all per-artifact and cross-artifact checks. A recomputed archive digest cannot make a substituted path, document, plan, or relation valid.

The canonical fixed-pilot archive is retained at:

```text
research/DW-001/development-pilot-archive.v1.json
```

Its semantic index is stable across equivalent clean runs, while timestamps, durations, complete report/result/index digests, and complete archive digests may vary where contracts include volatile fields.

### Analysis boundary

The mechanism-pilot index retains full case tables and five exact controlled contrasts. It emits:

```text
headline_score                = null
ecological_inference_allowed  = false
```

All method records remain development-only and primary-denominator ineligible. The fixed mechanism pilot validates the evidence pipeline; it does not estimate method effectiveness on real patches.

## Report and artifact schemas

Matrix schema `0.3` records observer protocol, invocation binding, receipt digest/outcome, producer, counts, stable observer error, exact state objects, witness digest, and report digest.

Influence schema records path order, canonical matrix reference, anchors, every coalition, exact Git objects, observations, statuses, and exact metrics where release conditions hold.

DW-001 adds strict schemas and semantic verifiers for projection, fixture descriptor, fixture identity, fixture-manifest binding, scenario manifest, result record, development-pilot plan, development-pilot index, and development-pilot archive.

Schemas define structural interoperability. Python verifiers remain authoritative for semantic recomputation and cross-artifact relations.

## Integrity model

Current artifacts use unkeyed canonical digests:

- `witness_sha256` and matrix `report_sha256`;
- `influence_sha256` and influence `report_sha256`;
- descriptor, identity, binding, projection, manifest, result, pilot-plan, pilot-index, and pilot-archive digests.

They detect modification only against separately trusted sources or expected values. An actor able to replace an entire chain can recompute every digest.

Signing, producer identity, DSSE, in-toto, Sigstore, SCITT, immutable timestamping, and transparency registration remain separate future layers. A signature would authenticate bytes, not make false semantics true.

## Remaining separation of concerns

DeltaWitness intentionally refuses substitution among evidence layers:

- process failure does not imply assertion failure;
- generic typed error does not imply a precise error subtype;
- assertion failure does not imply claim-oracle relevance;
- a canonical four-state matrix does not prove oracle adequacy;
- exact coalition enumeration does not prove complete causality;
- a fixture identity does not prove environment reproducibility;
- a fixture-manifest binding does not validate governance declarations;
- a verified synthetic pilot does not establish ecological effectiveness;
- an unkeyed digest does not authenticate a producer;
- a matching witness does not authorize deployment;
- controlled synthetic pairs do not establish general observer or method superiority.

Future work may add assertion-integrity analysis, mutation or coverage evidence, broader error-taxonomy adapters, repeated stochastic execution, reproducible containment, signed provenance, ecological baselines, external policy, and independent reproduction. Each layer must retain its own claim boundary and explicit negative controls.
