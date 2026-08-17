# DeltaWitness

[![CI](https://github.com/rdemb/delta-witness/actions/workflows/ci.yml/badge.svg)](https://github.com/rdemb/delta-witness/actions/workflows/ci.yml)

**Counterfactual verification and bounded test-integrity evidence for AI-generated code changes.**

DeltaWitness is an open research prototype for checking whether a software patch produced the behavioral change claimed by its tests. It combines deterministic Git replay, typed execution evidence, exact declared-selector localization, bounded mutation and statement-coverage controls, integrity-verifiable artifacts, and exhaustive path-level intervention analysis.

**Current status:** pre-alpha research software (`v0.0.3` plus unreleased DW-001 infrastructure). It is not a formal proof system, a security certification product, a complete oracle analyzer, a validated mutation or coverage system, a code-review replacement, or a sandbox for untrusted code.

## Why final-state green is not enough

A coding agent can change implementation code, change tests, run the resulting suite, and report success. That workflow can become self-confirming. A green candidate state does not establish that:

- candidate tests would have detected the original defect;
- the implementation change caused the observed transition;
- original tests still pass against the candidate implementation;
- a nonzero exit came from an assertion rather than import, setup, discovery, dependency, or infrastructure failure;
- the failing assertion belongs to the test declared for the claim;
- a genuinely discriminating selector expresses the intended behavior;
- a selector is strong enough to reject plausible incorrect implementations;
- a mutation set, coverage scope, threshold, or exclusion was fixed before outcomes were visible;
- unexpected results were retained instead of being suppressed as harness errors;
- summary counts and policy fields were recomputed from the complete result table;
- every changed implementation path contributed to the declared witness.

DeltaWitness moves the first layers of this decision out of an agent's narrative and into explicit, recomputable evidence.

## Evidence layers

```text
exact Git state identity
    -> process execution
    -> typed outcome semantics
    -> four-state change witness
    -> declared selector provenance
    -> oracle-relevance controls
    -> oracle-strength controls
    -> frozen mutation design
    -> typed mutation-result table
    -> statement-coverage direct baseline
    -> exact path-level intervention influence
    -> future containment, authentication, policy, and ecological evaluation
```

The layers do not substitute for one another. A stronger lower-level artifact does not silently imply a stronger semantic claim.

## Four-state change witness

For a base commit and descendant candidate commit, DeltaWitness constructs four exact Git states:

| | Base tests | Candidate tests |
|---|---:|---:|
| **Base implementation-side tree** | `base_base` | `base_candidate` |
| **Candidate implementation-side tree** | `candidate_base` | `candidate_candidate` |

A conventional regression fix often expects:

```text
base_base            pass
base_candidate       fail
candidate_base       pass
candidate_candidate  pass
```

Hybrid states are deterministic synthetic commits rather than dirty worktrees. Reports retain exact commit and tree identities, explicit path classification, every observation, a stable semantic witness digest, and a complete report digest.

This is a **change witness** under declared commits, paths, commands, observers, and expectations. It is not proof of full correctness, security, completeness, minimality, or deployment safety.

## Typed outcome semantics

### `exit-code-v1`

The default observer maps process return codes through explicit disjoint pass and fail classes. Timeout or every unclassified code makes execution incomplete.

This mode cannot distinguish assertion failure from multiple failure mechanisms sharing the same exit code.

### `outcome-receipt-v1`

A cooperating adapter writes a strict, bounded receipt bound to the exact claim, command, specification, observer, state, tree, and commit.

Only these combinations become normal pass/fail observations:

```text
receipt passed       + configured pass exit -> pass
receipt test_failure + configured fail exit -> fail
```

Missing, malformed, stale, contradictory, or non-assertion error receipts make the state incomplete. The built-in producer supports standard-library `unittest` discovery and exact logical-test selection.

A receipt is cooperating-producer evidence, not authentication. Tested code can see the binding.

Read [Outcome Receipt Protocol v1](docs/OUTCOME_RECEIPT_V1.md).

## Declared witness-test localization

DW-001 can bind a claim to exact predeclared standard-library unittest selectors and replay them under reconstructed `base_candidate` and `candidate_candidate` states.

Per-selector classification is:

```text
discriminating
non_discriminating
candidate_invalid
indeterminate
```

A valid `discriminating` result means the exact selector produced typed assertion failure in `BC` and pass in `CC`. It does not establish semantic relevance or oracle strength.

## Development negative controls

### Unrelated assertion

A fixed owned-synthetic case produces a canonical four-state matrix and genuine typed assertion failure, but the suite fails only because of a collateral assertion. The claim-facing selector passes under base and candidate implementations.

```text
typed suite failure
    + canonical four-state witness
    != claim-oracle relevance
```

### Weak but genuinely discriminating selector

A separate fixed selector genuinely fails on base and passes on candidate, but checks only that `is_admin(viewer)` returns a Boolean. A fixed claim-violating mutant also passes that selector while failing a separately fixed development claim check.

```text
typed assertion failure
    + canonical four-state witness
    + exact selector fail-to-pass
    != sufficient oracle strength
```

Read [DW-001 Weak-Proxy-Oracle Challenge v1](research/DW-001/WEAK_ORACLE_CHALLENGE.md).

## Frozen claim-scoped mutation design

The mutation path is deliberately staged:

```text
freeze source, target, operators, profiles, and identities
    -> execute one bounded typed result table
    -> compare with simpler direct baselines
    -> only later consider broader calibration or policy
```

The committed development plan fixes one project-owned candidate predicate, one exact AST return-expression target, and this outcome-blind generic operator order:

```text
return-constant-false-v1
return-constant-true-v1
comparison-eq-to-ne-v1
```

The deterministic catalog retains:

```text
3 generated
1 duplicate
1 not_applicable
1 invalid
```

Duplicate, invalid, and not-applicable records cannot disappear or enter killed/survived denominators. The historical `nonempty-role-boolean-v1` challenge mutant remains outside generic-operator evidence.

Read [DW-001 Claim-Scoped Mutation Calibration Plan v1](research/DW-001/MUTATION_CALIBRATION_PLAN.md).

## Typed mutation result

The bounded result runner verifies the exact plan and catalog, then executes only:

```text
candidate baseline
3 generic generated mutants
1 separately labelled historical control
```

Every implementation runs two strong selectors, one weak selector, and two reference selectors:

```text
5 implementations × 5 selectors = 25 typed commands
```

Expected and observed evidence remain separate:

```text
expected_observed
observed
concordant
```

The same separation is retained at profile, reference, and record levels. A complete invocation-bound observation that contradicts preregistration remains a valid negative result with `analysis.status = unexpected`; malformed or contradictory evidence still fails closed.

For the exact current owned-synthetic table:

```text
all 3 generic mutants:
    strong authorization profile -> killed
    weak Boolean-proxy profile   -> survived
    reference checks             -> claim_violation_observed
```

This is bounded mechanism evidence only. It is not mutation adequacy or an ecological result.

Read [DW-001 Claim-Scoped Mutation Result v1](research/DW-001/MUTATION_RESULT_V1.md).

## Statement-coverage direct baseline

Before expanding the mutant set, DeltaWitness compares the frozen mutation result with a substantially simpler dynamic baseline.

The `stdlib-statement-trace-v1` adapter:

- executes only the exact fixed candidate and three frozen selectors;
- emits the usual typed outcome receipt plus a separate invocation-bound statement-trace receipt;
- filters current-thread `sys.settrace` events to one exact relative source path, symbol, and target-line set;
- retains target-function calls, covered-line sets, and per-line hit counts;
- treats missing, malformed, unavailable, or failed tracing as `indeterminate`, never as empty coverage;
- retains complete preregistration-divergent signatures as negative results.

The fixed workload is three typed child commands.

Current bounded observation:

```text
strong profile union/intersection = [2] / [2]
weak profile union/intersection   = [2] / [2]

statement coverage distinguishes profiles = false
frozen mutation table distinguishes them  = true
```

The strong profile has two selectors and the weak profile one, so raw hit-count magnitude is diagnostic only. The primary comparison uses exact covered-line sets.

This establishes one narrow incremental observation:

```text
same claim-target statement set
    != same behavior under the frozen claim-scoped mutants
```

It does not establish general inadequacy of coverage or general superiority of mutation testing.

Read [DW-001 Claim-Scoped Statement-Coverage Baseline v1](research/DW-001/STATEMENT_COVERAGE_BASELINE_V1.md).

## Exact patch influence

For patches with at most eight changed code paths, `deltawitness influence` exhaustively evaluates every path coalition under base and candidate test worlds.

A coalition is:

- `supported` when every claim produces valid pass evidence under both test worlds;
- `unsupported` when execution is complete and valid failure evidence exists;
- `indeterminate` when any required execution is incomplete.

Exact metrics are released only when the complete `2^n` table exists and endpoint anchors remain consistent with the canonical matrix.

Available outputs include:

- every inclusion-minimal witness-sufficient coalition;
- global and full-context necessity;
- standalone sufficiency;
- positive and negative marginal swings;
- exact rational Shapley allocation;
- normalized Banzhaf influence;
- pairwise Banzhaf interaction;
- monotonicity diagnostics.

The metrics describe one declared Boolean witness over whole changed paths. They are not correctness, blame, severity, ownership, oracle strength, or universal causality.

Read [Exact Patch Influence v1](docs/PATCH_INFLUENCE_V1.md) and [Research Note 002](docs/RESEARCH_NOTE_002_EXACT_PATCH_INFLUENCE.md).

## Integrity model

Current artifacts use strict schemas, canonical JSON, semantic reconstruction, and unkeyed SHA-256 digests.

Two digest classes are commonly separated:

- a stable semantic digest that normalizes timestamps and selected runtime diagnostics;
- a complete report digest that binds the entire document.

Unkeyed digests detect modification only against separately trusted sources or expected values. An actor able to replace a complete evidence chain can recompute every digest. Signing, producer identity, DSSE, in-toto, Sigstore, transparency, and immutable timestamping remain future layers.

## Quick start

Requirements:

- Python 3.11 or later;
- Git;
- a clean repository;
- a base commit that is an ancestor of the candidate commit.

Install from a local checkout:

```bash
python -m pip install --no-deps -e .
deltawitness doctor
```

Run the self-contained public demo:

```bash
./scripts/demo.sh
```

Verify a repository:

```bash
deltawitness verify \
  --repo /path/to/repository \
  --base origin/main \
  --head HEAD \
  --spec deltawitness.toml
```

Analyze exact path influence:

```bash
deltawitness influence \
  --repo /path/to/repository \
  --base origin/main \
  --head HEAD \
  --spec deltawitness.toml
```

Verify generated reports:

```bash
deltawitness verify-report /reviewed/path/report.json
```

The DW-001 selector-localization, challenge, mutation, and coverage APIs are development research contracts. They are not general CLI policy and do not authorize execution of external repositories.

## Safety model

DeltaWitness executes commands without a shell under a reduced environment and excludes raw output by default. It still runs with the current user's filesystem permissions and does not isolate the network, process tree, CPU, memory, storage, or external services.

Use only trusted repositories and commands, or a separately secured disposable environment without credentials. Never use a credential-bearing VPS as an ad hoc sandbox.

The current mutation and coverage development controls execute only fixed project-owned Python bytes in temporary directories. They do not make external code safe.

Read [THREAT_MODEL.md](THREAT_MODEL.md).

## Research boundary

Fail-to-pass validation, selector execution, mutation testing, selective mutation, equivalent-mutant analysis, statement and branch coverage, delta debugging, patch minimization, program slicing, test-code co-evolution, cooperative-game attribution, weak or partial oracles, and hidden tests are established areas.

DeltaWitness does not currently claim scientific novelty. The provisional combination under evaluation is narrower: deterministic Git-native four-state replay, typed invocation-bound outcomes, exact selector provenance, bounded negative controls, frozen mutation identities, complete expected-or-unexpected mutation evidence, an invocation-bound statement-coverage direct baseline, exact dual-test-world path interventions, and portable integrity-verifiable artifacts.

The project still requires broader prior-art review, fair direct tooling baselines, larger frozen calibration, equivalent-mutant review, authorized ecological data, containment, held-out evaluation, independent reproduction, and external technical review.

See:

- [Architecture](docs/ARCHITECTURE.md)
- [Threat model](THREAT_MODEL.md)
- [Roadmap](ROADMAP.md)
- [DW-001 protocol](research/DW-001/PROTOCOL.md)
- [Statement-Coverage Baseline v1](research/DW-001/STATEMENT_COVERAGE_BASELINE_V1.md)

## Current limitations

- test and implementation changes must be separable by repository path;
- candidate test changes are required for the core matrix;
- changed submodules and symbolic links are rejected;
- environment, dependencies, toolchain, kernel, hardware, network, and external services are not cryptographically bound;
- typed receipts require cooperating producers and are unsigned;
- exact selector localization currently supports standard-library unittest;
- typed outcomes and exact selector transitions do not establish semantic relevance or strength;
- the mutation result covers one fixed source, three generic mutants, and one historical control;
- the statement baseline covers one fixed source, one symbol, one executable target line, three selectors, and current-thread Python trace events;
- current-thread tracing does not represent other threads, native code, subprocesses, or behavior outside the exact target scope;
- equivalent-mutant adjudication and population-level warning rates remain unresolved;
- exact influence uses whole paths and is capped at eight changed code paths;
- nondeterministic tests currently execute once;
- independent reproduction remains incomplete.

## Project principles

1. Deterministic checks precede model judgment.
2. Ambiguous trust boundaries fail closed.
3. Public claims remain narrower than evidence.
4. Incomplete execution is not negative evidence.
5. Complete unexpected results are retained rather than suppressed.
6. Exact and approximate results are never conflated.
7. Reproduction matters more than branding.
8. Material AI assistance is disclosed while responsibility remains human.

## Development

```bash
python scripts/validate_public_tree.py
python -m compileall -q src tests scripts
python -m unittest discover -s tests -v
./scripts/demo.sh
python -m pip wheel --no-deps . --wheel-dir dist
```

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), [AI_USAGE.md](AI_USAGE.md), and [PUBLICATION_POLICY.md](docs/PUBLICATION_POLICY.md).

## Author and license

DeltaWitness is an independent open research project created by **Rafal Dembski**. It is licensed under Apache License 2.0.
