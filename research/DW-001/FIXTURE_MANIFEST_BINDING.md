# DW-001 Fixture–Manifest Binding v1

**Status:** implemented contract for owned-synthetic development artifacts. The DW-001 protocol remains draft and unfrozen. No development pilot or held-out execution is authorized by this document.

## Purpose

DW-001 uses independently versioned artifacts for different responsibilities:

```text
fixture descriptor
    -> deterministic generator
    -> fixture identity

scenario manifest
    -> pre-execution study ground truth and governance
```

Scenario-manifest v1 predates the deterministic fixture generator. It records exact base and candidate commit IDs, path categories, execution semantics, ground truth, partition ownership, and review, but it has no dedicated fixture-identity digest.

Changing scenario-manifest v1 in place would silently alter an issued schema and its digest semantics. The binding record therefore adds a separate versioned relation:

```text
deltawitness.dw001-fixture-manifest-binding.v1
```

The record establishes only that one verified descriptor, one verified fixture identity, and one verified scenario manifest agree on the fields they actually share.

## Source artifacts

The builder accepts exactly three supplied artifacts:

1. a `deltawitness.dw001-fixture-descriptor.v1` document;
2. a `deltawitness.dw001-fixture-identity.v1` document;
3. a `deltawitness.dw001-scenario-manifest.v1` document.

Each source is independently semantically verified before any relation is constructed. Digest validity alone is insufficient.

The builder derives every binding field from the verified sources. Callers cannot provide duplicated relation values as free-form input.

## Verified relations

Binding v1 verifies:

- study and scenario identity;
- descriptor digest recorded by the fixture identity;
- descriptor-to-identity family, control-role, generator, template, observer, path, state, and method agreement;
- synthetic provenance and owned-synthetic authorization basis in the manifest;
- manifest base and candidate commits against fixture identity commits;
- exact code, test, and documentation path categories;
- observer and observer-arm identity;
- command and timeout equality;
- expected state applicability, outcomes, and failure-cause classes;
- expected nested-method decisions and reason codes;
- false-assurance family identity;
- membership of the fixture specification path in the declared documentation paths;
- descriptor-derived specification bytes against the fixture identity SHA-256.

The verifier independently repeats source verification, validates the binding structure, recomputes `binding_sha256`, derives the canonical binding again from the supplied sources, and requires byte-equivalent canonical content.

A recomputed binding digest cannot hide a relation mismatch.

## Explicit scope separation

The binding includes a machine-readable `relation_scope` object with three ordered lists.

### Verified relations

These are direct correspondences checked across the source artifacts.

### Manifest-owned fields

These remain controlled by the scenario manifest and are not inferred from the generator:

- partition and partition lock;
- source, license, authorization, and publication metadata;
- repository identifier;
- exit-code classes and environment declarations;
- environment assumptions;
- review identity, independence disclosure, decision, and rationale.

A valid fixture binding cannot make a development manifest primary-denominator eligible and cannot replace the manifest review or holdout commitment process.

### Fixture-only fields

The following are retained from fixture evidence but have no exact field in scenario-manifest v1:

- family and control-role identifiers;
- generator and template identities;
- Git object format;
- base and candidate tree IDs;
- specification SHA-256.

The binding does not pretend that scenario-manifest v1 contains or independently verifies these values.

## Git and specification boundary

The manifest's base and head commit IDs must equal the fixture identity's commit IDs. The binding also carries the fixture tree IDs, but it does not independently reconstruct Git objects.

Tree-to-commit correspondence requires the separately verified materialized fixture repository. The binding is not a replacement for `verify_materialized_fixture`.

Fixture-identity verification additionally recomputes the exact specification bytes derived from the descriptor and compares their SHA-256 with the recorded fixture identity. This closes a prior gap in which a changed specification digest could remain internally digest-valid after recomputation.

## Structural schema

Schema:

```text
research/DW-001/schema/fixture-manifest-binding.schema.json
```

Semantic implementation:

```text
src/deltawitness/dw001_fixture_binding.py
```

The JSON Schema defines:

- exact root and nested object fields;
- `additionalProperties: false` for every object boundary;
- source schema identities and digest forms;
- canonical state and method tuple order;
- safe repository-relative path forms;
- explicit relation-scope lists;
- lexical Git object and SHA-256 forms.

The Python verifier remains authoritative for cross-artifact relations and semantic equality.

## Integrity and authentication

`binding_sha256` is an unkeyed integrity field over canonical binding bytes with that field normalized to `null`.

It can detect modification only when compared with separately trusted source artifacts or an expected digest. An actor able to replace the descriptor, identity, manifest, binding, and all expected digests can replace the complete chain.

The binding does not provide:

- producer authentication;
- non-repudiation;
- proof of creation time;
- append-only logging;
- signature verification;
- delegation identity;
- transparency registration.

DSSE, in-toto predicates, Sigstore, SCITT, and other attestation or transparency mechanisms remain separate future layers. Adding an envelope would not make incorrect source semantics true.

## Privacy and publication

A binding can expose:

- scenario and family identifiers;
- commands and repository-relative paths;
- Git commit and tree identities;
- generator and template versions;
- observer-arm identity;
- specification and artifact digests;
- expected state and method semantics.

It must not contain:

- absolute local paths;
- usernames;
- credentials or tokens;
- environment values;
- private endpoints;
- raw command output;
- reviewer identities or rationales;
- confidential repository material.

Every published binding and its linked artifacts require privacy and claim-boundary review.

## Prior-art boundary

Content-addressed provenance, manifest linking, W3C PROV relations, in-toto subjects and predicates, SLSA provenance, DSSE envelopes, and research-data lineage are established approaches.

No novelty claim is made for digest-linked relation records. The narrow engineering purpose is to preserve issued DW-001 v1 artifacts while rejecting a semantically incompatible fixture/manifest pairing.

## Non-claims

A valid binding does not establish:

- patch correctness, security, or completeness;
- correctness of ground truth or reviewer declarations;
- taxonomy realism or representativeness;
- complete environment reproducibility;
- producer authenticity;
- timely preregistration or holdout commitment;
- authorization to execute a development pilot or holdout;
- empirical effectiveness or superiority;
- independent reproduction;
- Gate 0 completion;
- production readiness or scientific novelty.

It establishes only deterministic correspondence among the supplied verified artifacts within the explicit v1 relation scope.
