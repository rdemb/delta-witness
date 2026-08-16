# DW-001 Development Mechanism Pilot v1 — Readiness and Completion Boundary

**Status:** the fixed owned-synthetic development mechanism pilot has executed and its canonical archive is retained and verified. This document does not authorize an ecological development corpus, protocol freeze, holdout, or confirmatory interpretation.

Canonical result:

```text
research/DW-001/DEVELOPMENT_PILOT_V1.md
```

Canonical artifacts:

```text
research/DW-001/development-pilot-plan.v1.json
research/DW-001/development-pilot-archive.v1.json
```

Exact digests:

```text
plan_sha256            = 48a98f01c740862c91056841a7f96e6c98f1ae9641b7b364590a45d458ae3bcc
archive_sha256         = 3b992d67281693143a4e7bea920d1829f9b675eda592993db0e234239fcf4b06
index_semantic_sha256  = bd3c40d62e3d5695271db06f3bec476b4b9cd94442fd7171e1a03c70a74db5ef
```

## Purpose

The mechanism pilot tested whether the complete DeltaWitness study-evidence chain could execute, retain, verify, and analyze five fixed positive and negative mechanisms under both observer arms without manual artifact repair, post-result relabeling, or denominator drift.

It asked:

> Can the current fixed owned-synthetic cases produce one complete, public-safe, internally consistent development bundle and machine-derived controlled-contrast analysis?

It did not ask how frequently these mechanisms occur in real coding-agent patches.

## Fixed population

The executed plan contains exactly ten ordered case arms:

| Order | Case arm | Family | Observer |
|---:|---|---|---|
| 1 | `dev-v1-valid-o0` | `valid-discriminating-regression` | `O0_EXIT_CODE` |
| 2 | `dev-v1-valid-o1` | `valid-discriminating-regression` | `O1_TYPED_RECEIPT` |
| 3 | `dev-v1-nondiscriminating-o0` | `non-discriminating-candidate-test` | `O0_EXIT_CODE` |
| 4 | `dev-v1-nondiscriminating-o1` | `non-discriminating-candidate-test` | `O1_TYPED_RECEIPT` |
| 5 | `dev-v1-candidate-regression-o0` | `candidate-regression-against-base-tests` | `O0_EXIT_CODE` |
| 6 | `dev-v1-candidate-regression-o1` | `candidate-regression-against-base-tests` | `O1_TYPED_RECEIPT` |
| 7 | `dev-v1-import-error-o0` | `wrong-reason-base-import-failure` | `O0_EXIT_CODE` |
| 8 | `dev-v1-import-error-o1` | `wrong-reason-base-import-failure` | `O1_TYPED_RECEIPT` |
| 9 | `dev-v1-unrelated-assertion-o0` | `wrong-reason-unrelated-assertion` | `O0_EXIT_CODE` |
| 10 | `dev-v1-unrelated-assertion-o1` | `wrong-reason-unrelated-assertion` | `O1_TYPED_RECEIPT` |

Every arm is permanently:

```text
partition = development
primary_denominator_eligible = false
```

The cases and all inspected derivatives are prohibited from a later confirmatory holdout.

## Completed pre-execution gates

Before the canonical run, the branch fixed and verified:

- exact protocol and evidence-producing implementation commits;
- one strict machine-readable ten-arm plan;
- exact family, observer, control-role, scenario, state, method, and localization expectations;
- exact claim-witness selectors where localization was required;
- a fixed localization aggregate rule;
- development-only denominator semantics;
- cost fields and missingness policy;
- strict plan, index, and archive schemas;
- semantic plan, index, archive, and full-bundle verifiers;
- staging → self-verification → publication runner semantics;
- red-first failure for the missing plan, runner, and archive capabilities;
- public-tree, compile, suite, demo, wheel, installed-package, privacy, and threat-boundary checks.

No runtime argument introduced free-form fixture code, tests, commands, selectors, expected labels, exclusions, or denominator decisions.

## Retained artifact chain

For each case arm, the archive retains and re-verifies:

```text
pilot plan entry
    -> fixture descriptor
    -> synthetic Git identity
    -> development scenario manifest
    -> fixture-manifest binding
    -> strict matrix report
    -> nested M0-M3 projection
    -> claim-witness declaration, when required
    -> claim-witness localization, when required
    -> development result record
    -> public-safe pilot index entry
```

The archive contains 84 JSON documents. A digest-valid object is insufficient: every existing semantic and cross-artifact verifier remains mandatory.

## Controlled contrasts

All five sealed contrasts were observed as expected:

| Contrast | Result |
|---|---|
| Candidate-test discrimination | Non-discriminating family changes `M0 accept` to `M1 reject` under both observers |
| Original-test preservation | Candidate-regression family changes `M1 accept` to `M2 reject` under both observers |
| Outcome-semantics contrast | Import-error family has `M1 accept` under O0 and `M1 indeterminate` under O1 |
| Broad-suite versus declared witness | Unrelated-assertion family has `M3 accept` but localization `unsupported` under both observers |
| Positive control | Valid family has all methods accept and localization `supported` under both observers |

The analysis retains the full per-case tables and fixes:

```text
headline_score                = null
ecological_inference_allowed  = false
retain_case_tables             = true
```

## Cost boundary

The archive records per-case:

- wall-clock seconds;
- CPU seconds;
- executed matrix states;
- executed selector states;
- command count;
- artifact count;
- public bundle byte count;
- human review time or missingness.

The canonical plan executes:

```text
40 matrix states
12 selector states
52 commands
```

Human review time is explicitly unmeasured. Projected `M0`, `M1`, and `M2` decisions from one full matrix are not their native runtime cost.

The values are implementation diagnostics for fixed synthetic cases, not population estimates.

## Reproducibility result

Repeated clean executions preserve:

- plan digest;
- ordered case IDs;
- fixture descriptors and identities;
- exact Git trees and commits;
- matrix witness semantics;
- expected method and localization tables;
- pilot semantic digest:

```text
bd3c40d62e3d5695271db06f3bec476b4b9cd94442fd7171e1a03c70a74db5ef
```

Timestamps, durations, complete report digests, result digests, index digests, and complete archive digests may vary where their contracts include volatile fields.

This does not bind the complete Python, Git, operating-system, dependency, kernel, hardware, filesystem, locale, network, or container environment.

## Safety and publication record

The pilot used only fixed project-owned synthetic material in disposable GitHub-hosted directories. The runner remains unsandboxed.

The public archive excludes:

- absolute paths;
- raw stdout, stderr, and tracebacks;
- usernames, credentials, and environment values;
- private endpoints;
- arbitrary source or test content outside fixed public fixtures;
- holdout and primary-denominator eligibility.

Git identities, relative paths, commands, test IDs, producer metadata, counts, timings, and digests remain publication metadata.

One-time archive transport and branch write capabilities were separately reviewed, used only for public-safe synthetic evidence, and removed before final validation. They are not continuing DeltaWitness capabilities.

## Completion decision

The following statement is now supported:

> The fixed DW-001 owned-synthetic development mechanism plan executed and produced an internally consistent, public-safe archive whose complete evidence chain and controlled contrasts can be regenerated and reverified.

The following statements remain unsupported:

- DeltaWitness is more effective than final-state or fail-to-pass validation on real patches;
- the five families represent coding-agent failure prevalence;
- the observer or localization layers have measured accuracy on an ecological corpus;
- `M3_FOUR_STATE` provides a justified operational benefit over `M2_F2P_P2P`;
- the protocol is frozen or holdout-ready;
- Gate 0 is complete;
- the result is independently reproduced, production-ready, scientifically novel, or award-level.

## Next readiness boundary

The next phase is **not another synthetic assurance feature**.

Before any ecological development execution, DW-001 needs a separate reviewed design for:

- corpus source and authorization;
- inclusion and exclusion rules;
- unit of analysis;
- sampling and partition procedure;
- independent ground-truth and oracle-relevance review;
- adjudication and disagreement retention;
- metric definitions and denominators;
- stochastic repetition and environment policy;
- pilot-informed precision target;
- privacy/publication review;
- immutable holdout commitment procedure.

Completion of the fixed mechanism pilot does not authorize those steps automatically.
