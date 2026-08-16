# DW-001 Projection Integrity Boundary

**Status:** implementation note for the development-pilot projection artifact. The DW-001 protocol remains draft, unfrozen, and unauthorized for held-out execution.

## Why a digest is insufficient

`projection_sha256` binds the serialized projection object, but it does not prove that the decisions inside the object follow the declared DW-001 predicates. A modified projection can carry a recomputed unkeyed digest.

The verifier must therefore perform two independent checks:

1. recompute the deterministic semantic constraints of the projection;
2. recompute `projection_sha256` over the complete object with that field normalized to `null`.

A projection is accepted only when both checks succeed.

## Semantic checks

`verify_projection_document` validates, fail-closed:

- exact root and nested field sets;
- study and schema identifiers;
- source observer-to-observer-ID mapping;
- canonical applicability partition and state ordering;
- the fixed ordered method set `M0_FINAL` through `M3_FOUR_STATE`;
- each method's exact required-state set;
- combined method identifiers;
- method-specific non-applicability reasons;
- claim identity consistency across applicable methods;
- canonical expected outcomes for every exposed state;
- consistency of `matched`, contradicted-state, and indeterminate-state fields;
- claim decisions and reason codes recomputed from their exposed states;
- method decisions and reason codes recomputed from their claims;
- byte-equivalent shared state observations across nested methods.

This prevents a caller from changing a decision or one method's view of a shared observation and then restoring apparent integrity merely by recomputing the projection digest.

## Source binding

The projection records the source matrix report and witness digests. The standalone projection verifier checks that these values are well formed and integrity-bound into the projection; it does not possess the source report bytes and therefore cannot independently prove correspondence with them.

A study pipeline must retain the strict-decoded source report, verify its matrix digests, and compare its trusted digest with the projection's recorded source digest. Unkeyed digests do not authenticate either producer and do not prevent coordinated replacement of both artifacts.

## Claim boundary

A valid projection establishes only that one serialized artifact is internally consistent with the deterministic nested DW-001 decision contract and its recorded source identities. It does not establish:

- patch correctness or security;
- oracle relevance or strength;
- empirical effectiveness of any method;
- environment reproducibility;
- producer authenticity;
- independent reproduction;
- authorization to execute the held-out study, merge, or deploy.
