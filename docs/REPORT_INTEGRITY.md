# Report Integrity and Strict JSON Decoding

**Status:** architecture note for matrix and exact patch-influence reports.

DeltaWitness computes semantic and complete-report digests over decoded JSON objects. The byte-to-object conversion is therefore part of the report trust boundary.

## Accepted encoding

`deltawitness verify-report` accepts only:

- valid UTF-8 bytes;
- one JSON value whose root is an object;
- object keys that occur exactly once at every nesting level.

Duplicate keys are rejected before any semantic or complete-report digest is calculated. This prevents the same accepted byte sequence from acquiring first-value-wins and last-value-wins interpretations in different consumers.

The loader does not normalize or repair malformed input. Invalid UTF-8, invalid JSON, a duplicate key, or a non-object root produces a fail-closed `ReportError`.

## Digest sequence

For an accepted report:

1. decode strict UTF-8 JSON with recursive duplicate-key rejection;
2. require an object root;
3. reconstruct the schema-specific semantic payload;
4. recompute `witness_sha256` or `influence_sha256`;
5. recompute `report_sha256` over the complete decoded document with `report_sha256` replaced by `null`;
6. require both recorded digests to match.

Valid reports emitted by DeltaWitness retain their existing schema, canonical representation, and digest values. Strict decoding changes only which external byte sequences are accepted as unambiguous report documents.

## Interoperability requirement

External producers and consumers should reject duplicate object keys rather than selecting an arbitrary occurrence. A consumer that applies different numeric, Unicode, or schema semantics may still disagree with DeltaWitness even when it rejects duplicates. Cross-language implementations therefore need compatibility fixtures and schema tests before claiming equivalent verification.

## Claim boundary

Strict decoding prevents duplicate-key parser ambiguity in DeltaWitness report loading. It does not:

- authenticate the report producer;
- prevent replacement of a report and all unkeyed digests;
- prove that an external parser has equivalent semantics;
- bind the execution environment;
- make a supported witness proof of patch correctness or deployment safety.

A report digest remains meaningful only when compared with a separately trusted value.
