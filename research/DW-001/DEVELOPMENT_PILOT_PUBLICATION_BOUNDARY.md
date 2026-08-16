# DW-001 Development Pilot Publication Boundary

**Status:** normative boundary for the development-only mechanism-pilot runner and retained archive. This document does not authorize a holdout, establish external review, or create confirmatory evidence.

## Atomic final-directory publication

`run_development_pilot()` accepts only a final output path that does not exist.

The runner:

1. verifies the sealed ten-arm plan before creating output;
2. creates a sibling staging directory under the trusted output parent;
3. executes all cases into staging;
4. self-verifies the index, complete artifact chain, controlled contrasts, privacy boundary, and exact retained file set;
5. publishes the complete staging directory through one same-filesystem rename to the previously absent final path.

An existing destination is rejected even when it is an empty literal directory. This intentionally narrows an earlier pre-merge behavior. Moving children individually into an existing directory could leave a partially visible bundle if a later move failed. Rejecting every existing final path preserves a single supported publication transition:

```text
absent final path
    -> one verified staging tree
    -> one final rename
```

If final rename fails, the public final path remains absent. The runner removes the private staging directory during failure cleanup. A valid index is never published incrementally.

This boundary assumes that the output parent, filesystem, process namespace, and rename implementation are trusted. It does not establish crash consistency across filesystems, hostile parent-directory resistance, durable storage flush, or operating-system containment.

Archive materialization has its own staged reconstruction and verification path. It does not permit pre-existing output content to be merged with the retained evidence set.

## Exact retained object

The sealed plan mechanically derives the complete bundle file set:

- `plan.json`;
- `index.json`;
- seven mandatory artifacts for every case arm;
- declaration and localization artifacts only for the six arms that require them.

The canonical development archive therefore contains exactly 84 JSON documents.

Directory and archive verification treats this as an exact set, not a minimum. It rejects:

- missing artifacts;
- duplicate archive paths;
- unexpected JSON or non-JSON files;
- unexpected directories;
- absolute, traversal, backslash, linked, or special entries;
- an archive entry with a valid recomputed digest but an undeclared path.

This prevents a separately unreviewed note, log, result, or sensitive file from being attached to an otherwise valid evidence chain and implicitly inheriting its publication status.

## Synthetic review metadata

Each owned-synthetic scenario manifest contains the deterministic reviewer record:

```text
reviewer_id = owned-synthetic-contract-review-v1
```

That record means only that the expected state and method labels are fixed by the repository's reviewed synthetic family contract and direct executable controls. It is schema-valid metadata used to exercise review and denominator invariants.

It is **not** evidence that:

- a person independent of the project performed an external review;
- the fixture author and implementation reviewer were organizationally independent;
- issue #4 independent reproduction is satisfied;
- a holdout ground-truth review has occurred;
- the declarations are authenticated or non-repudiable;
- the mechanism labels generalize to real coding-agent patches.

All pilot methods remain:

```text
partition = development
primary_denominator_eligible = false
```

The synthetic reviewer field cannot change either value and cannot be cited as external confirmation.

## Claim boundary

Atomic publication establishes only that the supported public runner does not expose a partially moved final directory under its trusted-parent assumptions.

Exact-file-set verification establishes only that the retained directory or archive contains exactly the documents derived from the sealed plan.

Synthetic review metadata establishes only internal contract consistency for fixed project-owned fixtures.

None of these properties establishes patch correctness, oracle adequacy, empirical effectiveness, producer authenticity, immutable timestamping, external peer review, independent reproduction, containment, protocol freeze, holdout authorization, production readiness, scientific novelty, or award-level significance.
