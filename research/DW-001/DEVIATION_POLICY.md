# DW-001 Deviation Policy

**Status:** development-pilot contract; not frozen; no held-out execution authorized.

This document defines the fail-closed boundary for protocol deviations recorded in a DW-001 result artifact. It prevents a change made after method outcomes became visible from remaining in the confirmatory denominator merely because an operator approved the change and recomputed the artifact digest.

## Terms

A deviation is **applied** when execution or analysis used a rule different from the frozen rule recorded by `rule_id`.

`results_visible` is `true` when any operator who participates in the deviation decision had access to a method outcome, state observation, failure category, exclusion-relevant result, or aggregate result from the affected execution before the replacement action was fixed.

An approval reference records review history. It does not restore confirmatory independence after results were visible.

## Normative rules

| Status | Results visible | Allowed confirmatory impact | Primary denominator consequence |
|---|---:|---|---|
| `rejected` | either | `none` | no consequence from the rejected action |
| `applied` | `false` | `none`, `exploratory_only`, or `excluded` | follows the declared impact |
| `applied` | `true` | `exploratory_only` or `excluded` | confirmatory eligibility is removed |

The combination below is invalid and must fail before digest acceptance:

```text
status = applied
results_visible = true
confirmatory_impact = none
```

A results-visible applied deviation cannot retain confirmatory eligibility even when `approval_reference` is present. The operator must classify the affected result as exploratory-only or excluded and preserve the original frozen rule and deviation record.

## Verification order

For a result artifact, the public verifier:

1. validates the versioned result structure and exact field sets;
2. recomputes exclusion, deviation, cost, method, and denominator invariants;
3. rejects results-visible applied deviations with `confirmatory_impact = none`;
4. recomputes the unkeyed result digest;
5. when source artifacts are supplied, checks manifest, projection, result, and denominator correspondence.

The builder applies the same post-unblinding guard before sealing a new result artifact.

## Claim boundary

This policy prevents one specified post-unblinding eligibility path in DeltaWitness result artifacts. It does not establish that every deviation was disclosed, that `results_visible` is truthful, that approvals are authentic, that the protocol is frozen, or that any development, pilot, or held-out result is valid. Unkeyed digests remain integrity fields, not producer authentication.
