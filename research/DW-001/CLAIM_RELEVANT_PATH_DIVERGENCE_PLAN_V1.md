# DW-001 Claim-Relevant Path Divergence Plan v1

## Status

**FACT — design-only preregistration.** This work package freezes one synthetic Python target, sixteen typed selectors over eight owned cells, six overlapping diagnostic profiles, one fixed project-owned influence control, four planned execution controls, and a non-executed implementation catalog.

**DECISION — execution is not authorized.** Candidate, selector, Coverage.py, fault, influence, and target execution remain `not_implemented`. No score, threshold, holdout, merge blocker, release decision, deployment decision, or production claim is produced by this plan.

## Frozen identities

| Object | SHA-256 |
|---|---|
| synthetic source bytes | `8c1bdd26c2e98cd209f210630bfe4d274a3dcd7bbd042db8b8586c7750814327` |
| semantic source AST | `dabb7011748968f8d43d590ff843a91697a3344a2400d7cabaf926b79ca88e2d` |
| synthetic tests | `8a26d52fa7fbb4ab7fc6eab466d9051cd329b0da09a667b5e220fbbfd416d1e9` |
| fixed influence control | `7b068d2f71003fade4eca77e1aa9cdb3a0f2f526f89dbd4828d4f17fbf2bd4f5` |
| plan | `ff0403132c3424fc7309a15a05794eed93ac9eb526de172e17326f8409ca0888` |
| catalog | `f36fbe58c00cfb8ed0fd994f3bb1dcdb45040774f7ae4663563b9f40ac15daa5` |
| prior-art log | `5f697631a5ded7a413dd11f4da0606ee8809e2b0f5de257ecab53a7e2d7f790c` |

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
