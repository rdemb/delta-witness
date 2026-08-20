# DW-001 Claim-Relevant Path Divergence Red-First Record v1

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
