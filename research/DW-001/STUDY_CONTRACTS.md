# DW-001 Study Contracts v1

**Status:** implementation note for development-pilot artifacts. The DW-001 protocol remains draft, unfrozen, and unauthorized for held-out execution.

DW-001 separates generated fixture identity, pre-execution ground truth, and post-execution evidence through independently verified artifact classes:

```text
fixture descriptor
    -> deterministic synthetic repository
    -> fixture identity
    -> scenario manifest
    -> strict source matrix report
    -> DW-001 nested-method projection
    -> result record
```

A digest-valid object is not sufficient. Every artifact is accepted only after its deterministic semantic invariants are recomputed. A result is accepted for study use only after it is checked against the supplied manifest and projection.

## Synthetic fixture descriptor and identity

Schemas:

```text
research/DW-001/schema/fixture-descriptor.schema.json
research/DW-001/schema/fixture-identity.schema.json
```

Semantic implementation:

```text
src/deltawitness/_dw001_scenarios.py
src/deltawitness/dw001_scenarios.py
```

A fixture descriptor binds:

- study, scenario, family, and control-role identifiers;
- generator and template IDs and versions;
- observer arm, command, timeout, and exact path contract;
- expected applicability, semantic outcome, and failure-cause class for every matrix state;
- expected decision and reason code for every nested method;
- `descriptor_sha256` over the complete descriptor with that field normalized to `null`.

Stored expected method labels are not trusted. The descriptor verifier recomputes them from the ordered expected states.

For the intentionally small supported family subset, the deterministic generator emits a public-safe fixture identity containing:

- the exact descriptor digest;
- generator, template, observer, family, and control-role identities;
- exact base and candidate commit and tree IDs;
- Git object format;
- specification path and SHA-256;
- exact path categories and expected state/method semantics;
- `identity_sha256` over the complete identity with that field normalized to `null`.

`verify_materialized_fixture` separately compares the identity with the supplied generated repository, including repository cleanliness, candidate `HEAD`, base ancestry, exact trees, and specification bytes.

The current scenario-manifest schema predates the fixture identity and does not contain a dedicated `fixture_identity_sha256` field. A generated fixture can still populate the manifest's exact base/head, path, execution, and ground-truth fields, but that correspondence is not silently claimed as a new v1 manifest invariant. Until a versioned manifest amendment or separate binding record is accepted, the fixture identity and manifest must be retained and reviewed as adjacent pre-execution artifacts.

Complete generator and taxonomy boundaries are documented in:

```text
research/DW-001/SCENARIO_TAXONOMY.md
research/DW-001/FIXTURE_GENERATOR.md
```

## Scenario manifest

Schema:

```text
research/DW-001/schema/scenario-manifest.schema.json
```

Semantic implementation:

```text
src/deltawitness/dw001_contracts.py
```

The manifest is defined before scenario execution and records:

- study, schema, scenario, and partition identifiers;
- a development or committed-holdout partition lock;
- public-safe ownership, license, or authorization provenance;
- exact base and candidate Git object IDs;
- disjoint, prefix-free code, test, and documentation paths;
- command, observer arm, timeout, exit classes, environment names, and environment requirements;
- applicability, expected observation, and expected failure-cause class for every matrix state;
- expected decision for every nested state-set method;
- false-assurance mechanism and environment assumptions;
- reviewer identity, independence disclosure, decision, and rationale;
- `manifest_sha256` over the complete manifest with that field normalized to `null`.

### Ground-truth recomputation

Stored method labels are not trusted. The verifier derives each expected method decision from the ordered state ground truth:

```text
non-applicable required state -> not_applicable
applicable error or timeout    -> indeterminate
complete predicate mismatch    -> reject
complete predicate match       -> accept
```

The corresponding reason code is deterministic.

A holdout method is primary-denominator eligible only when:

- the partition is holdout and its external commitment lock is present;
- ground truth has an implementation-independent approving reviewer;
- every state required by that method is applicable.

Development scenarios are never primary-denominator eligible.

### Partition boundary

A development manifest must use:

```text
status = development_uncommitted
commitment_sha256 = null
commitment_scope = null
```

A holdout manifest must use:

```text
status = holdout_committed
commitment_sha256 = <64 lowercase hex characters>
commitment_scope = dw001-holdout-index-v1
```

The manifest digest binds this declaration, but an unkeyed digest does not prove that the commitment predates execution. The frozen protocol must record the commitment in an independently timestamped immutable location before any held-out command runs.

## Result record

Schema:

```text
research/DW-001/schema/result-record.schema.json
```

A result records:

- the exact scenario-manifest digest and partition;
- protocol, implementation, optional generator, and baseline-contract identities;
- matrix-report, witness, and projection digests;
- one homogeneous observer arm;
- exclusions and their decision references;
- every declared protocol deviation;
- expected and observed four-way decisions for all methods;
- decision concordance;
- exact primary-denominator membership and reason;
- method-specific execution and review cost, or explicit missingness;
- `result_sha256` over the complete result with that field normalized to `null`.

### Exclusions

An included result carries no exclusion metadata. An excluded result requires a code, reason, and decision reference.

Exclusion never removes the record. It changes denominator eligibility while preserving the result and the decision trail.

### Deviations

Every deviation records:

- a stable deviation ID and frozen-rule ID;
- the observed problem and applied or rejected action;
- whether results were visible;
- confirmatory impact;
- an approval reference when applied.

An applied deviation without approval fails closed. A rejected deviation cannot carry confirmatory impact or approval. Applied deviations marked `exploratory_only` or `excluded` remain recorded but cannot preserve primary-denominator eligibility. An applied deviation made after results were visible cannot use `confirmatory_impact = none`.

### Denominator precedence

The result verifier derives denominator membership in this order:

```text
development partition
expected not_applicable
explicit exclusion
applied deviation: excluded
applied deviation: exploratory_only
observed not_applicable
eligible
```

Cross-artifact verification additionally removes scenarios whose supplied manifest is not independently approved.

### Cost missingness

A measured cost requires finite, nonnegative values for:

- wall-clock seconds;
- CPU seconds;
- executed state count;
- command count;
- review seconds.

A `not_run` or `unavailable` cost requires all quantitative fields to be `null` and a non-empty missing reason. Missing measurements are not silently encoded as zero.

## Cross-artifact verification

`verify_result_against_sources` independently verifies:

1. scenario-manifest semantics and digest;
2. result-record semantics and digest;
3. projection semantics and digest;
4. scenario ID and partition equality;
5. manifest digest recorded by the result;
6. base, candidate, observer, applicability, and non-applicability agreement between manifest and projection;
7. matrix-report, witness, projection, and observer identities recorded by the result;
8. expected decisions from the manifest;
9. observed decisions and reason codes from the projection;
10. concordance and denominator membership across all supplied artifacts.

The public verifier preflights each source artifact before relational checks. Malformed inputs return typed invalid diagnostics rather than being dereferenced after structural failure.

The verifier does not possess source matrix-report bytes. The source report must still be strict-decoded and verified separately, and its trusted digest must be compared with the projection and result.

## JSON Schema boundary

The JSON Schemas define structural interoperability:

- exact property names;
- required fields;
- primitive types;
- enumerations;
- tuple order for matrix states and methods;
- strict `additionalProperties: false` boundaries;
- digest and Git-object lexical forms.

They do not express every relational invariant. The Python semantic verifier remains authoritative for:

- observer-to-observer-ID mapping;
- disjoint exit classes and path categories;
- prefix-free paths;
- state/cause consistency;
- method-decision recomputation;
- reviewer-derived status;
- partition-lock meaning;
- exclusion and deviation effects;
- cost missingness;
- generated-repository identity checks;
- cross-artifact identity and decision consistency.

Schema QA checks local references, strict object boundaries, supported family enums, and exact root fields against emitted descriptor and identity artifacts. No third-party schema dependency is added to the core package.

## Integrity and authentication

`descriptor_sha256`, `identity_sha256`, `manifest_sha256`, and `result_sha256` are unkeyed integrity fields. They can detect modification only when compared with separately trusted expected values.

An attacker able to replace an artifact can recompute its digest. An attacker able to replace the fixture descriptor, identity, manifest, projection, result, and expected digests can replace the complete evidence chain.

Signing, producer identity, immutable timestamping, DSSE, in-toto, Sigstore, and environment provenance remain separate future layers.

## Privacy and publication

Fixture, scenario, and result artifacts can expose:

- scenario, family, generator, and template identifiers;
- repository and Git identities;
- changed paths and specification digests;
- commands and environment-variable names;
- license or authorization references;
- reviewer identifiers and rationales;
- false-assurance mechanisms;
- exclusions, deviations, and cost data.

Public artifacts must contain only public-safe identifiers and authorized material. Credentials, private endpoints, absolute local paths, confidential code, raw sensitive output, and unpublished vulnerability details remain prohibited.

The synthetic generator identity intentionally excludes destination paths, usernames, environment values, and raw Git output. This is a privacy boundary, not producer authentication or complete environment provenance.

## Non-claims

A valid fixture, manifest, and result chain does not establish:

- patch correctness or security;
- test-oracle relevance or strength;
- taxonomy completeness or representativeness;
- empirical effectiveness of any method;
- scientific novelty or superiority;
- environment reproducibility;
- producer authenticity;
- independent reproduction;
- authorization to execute a development pilot or holdout;
- Gate 0 completion.

The contracts prevent specific fixture, metadata, and denominator ambiguities. They do not substitute for protocol freeze, external review, holdout commitment, containment, or independent reproduction.
