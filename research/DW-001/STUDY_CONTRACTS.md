# DW-001 Study Contracts v1

**Status:** implementation note for development artifacts. The fixed owned-synthetic development mechanism pilot has executed and is retained; the broader DW-001 protocol remains draft, unfrozen, and unauthorized for ecological or held-out execution.

DW-001 separates generated fixture identity, pre-execution ground truth, execution evidence, post-execution results, and pilot-level retention through independently verified artifact classes:

```text
fixture descriptor
    -> deterministic synthetic repository
    -> fixture identity
    -> fixture-manifest binding
    -> scenario manifest
    -> strict source matrix report
    -> DW-001 nested-method projection
    -> claim-witness localization, when declared
    -> result record
    -> development pilot index
    -> canonical pilot archive
```

A digest-valid object is not sufficient. Every artifact is accepted only after deterministic semantic invariants and represented cross-artifact relations are recomputed.

## Synthetic fixture descriptor and identity

Schemas:

```text
research/DW-001/schema/fixture-descriptor.schema.json
research/DW-001/schema/fixture-identity.schema.json
```

Semantic implementation:

```text
src/deltawitness/_dw001_scenarios.py
src/deltawitness/_dw001_wrong_reason.py
src/deltawitness/dw001_scenarios.py
```

A fixture descriptor binds:

- study, scenario, family, and control-role identifiers;
- generator and template IDs and versions;
- observer arm, command, timeout, and exact path contract;
- expected applicability, semantic outcome, and failure-cause class for every matrix state;
- expected decision and reason code for every nested method;
- `descriptor_sha256` over the complete descriptor with that field normalized to `null`.

Stored expected method labels are not trusted. The descriptor verifier recomputes them from ordered expected states and fixed family/observer semantics.

For the intentionally small supported family subset, the deterministic generator emits a public-safe fixture identity containing:

- the exact descriptor digest;
- generator, template, observer, family, and control-role identities;
- exact base and candidate commit and tree IDs;
- Git object format;
- specification path and SHA-256;
- exact path categories and expected state/method semantics;
- `identity_sha256` over the complete identity with that field normalized to `null`.

Public fixture-identity verification recomputes exact specification bytes derived from the descriptor and requires their SHA-256 to equal the recorded value. A recomputed identity digest cannot hide a substituted specification digest.

`verify_materialized_fixture` separately compares identity with the supplied generated repository, including cleanliness, candidate `HEAD`, base ancestry, exact trees, and specification bytes.

Complete generator and taxonomy boundaries are documented in:

```text
research/DW-001/SCENARIO_TAXONOMY.md
research/DW-001/FIXTURE_GENERATOR.md
```

## Fixture-manifest binding

Scenario-manifest v1 predates fixture identity and has no dedicated `fixture_identity_sha256` field. Changing that schema in place would change an issued contract and its digest semantics.

Binding schema:

```text
research/DW-001/schema/fixture-manifest-binding.schema.json
```

Semantic implementation:

```text
src/deltawitness/dw001_fixture_binding.py
```

The builder first verifies descriptor, identity, and scenario manifest independently. It then derives a binding record and verifies exact agreement for fields represented by both sources, including:

- study and scenario identity;
- descriptor-to-identity family, generator, template, observer, path, state, and method semantics;
- synthetic provenance and authorization basis;
- exact base and candidate commits;
- path categories;
- command, observer arm, and timeout;
- state applicability, expected outcomes, and failure causes;
- expected nested-method decisions and reason codes;
- false-assurance family;
- specification path membership and descriptor-derived specification digest.

The binding contains an explicit `relation_scope` separating:

- relations verified across source artifacts;
- partition, review, authorization, environment, and other manifest-owned fields;
- tree IDs, specification digest, generator metadata, and other fixture-only fields absent from manifest v1.

A valid binding cannot change partition, reviewer decision, or denominator eligibility. Development scenarios remain outside the primary denominator.

The verifier independently re-verifies all sources, checks strict structure, recomputes `binding_sha256`, derives the canonical relation again, and requires exact canonical equality. Malformed objects fail closed with typed diagnostics.

Complete boundary details:

```text
research/DW-001/FIXTURE_MANIFEST_BINDING.md
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

Stored method labels are not trusted. The verifier derives each expected method decision from ordered state ground truth:

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

The manifest digest binds this declaration, but an unkeyed digest does not prove that commitment predates execution. The frozen protocol must record the commitment in an independently timestamped immutable location before any held-out command runs.

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

Exclusion never removes the record. It changes denominator eligibility while preserving the result and decision trail.

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

A measured method cost requires finite, nonnegative values for wall-clock time, CPU time, executed states, commands, and review time.

A `not_run` or `unavailable` method cost requires quantitative fields to be `null` and a non-empty missing reason. Missing measurements are not silently encoded as zero.

## Result cross-artifact verification

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

The public verifier preflights each source before relational checks. Malformed inputs return typed invalid diagnostics rather than being dereferenced after structural failure.

The verifier does not possess source matrix-report bytes. The source report must still be strict-decoded and verified separately, and its trusted digest compared with projection and result.

## Development pilot plan contract

Schema:

```text
research/DW-001/schema/development-pilot-plan.schema.json
```

Semantic implementation:

```text
src/deltawitness/_dw001_pilot_plan.py
src/deltawitness/dw001_pilot.py
```

The sealed plan fixes:

- study, pilot, protocol, and evidence-producing implementation identities;
- exact ten-arm order and case/scenario IDs;
- five fixed families under both observer arms;
- control roles and development partition;
- descriptor and specification digests;
- expected state and `M0`–`M3` tables;
- required declared-witness selectors and expected localization status;
- analysis contrast IDs and release policy;
- cost fields and missingness policy;
- permanent primary-denominator ineligibility.

All executable and expected case fields are derived from existing fixed generators and declaration builders. Callers provide only the two exact commit identities when constructing a plan.

The semantic verifier reconstructs the complete canonical plan. Recomputing `plan_sha256` cannot hide a changed family, selector, order, expected label, cost policy, or denominator field.

The executed plan is retained at:

```text
research/DW-001/development-pilot-plan.v1.json
```

## Development pilot runner and index

Index schema:

```text
research/DW-001/schema/development-pilot-index.schema.json
```

Implementation:

```text
src/deltawitness/_dw001_pilot_execution.py
src/deltawitness/dw001_pilot.py
```

The runner:

1. verifies the complete plan before creating final output;
2. materializes each fixed fixture in a disposable repository;
3. verifies descriptor, identity, repository, manifest, binding, matrix report, projection, localization, and result artifacts;
4. rejects any method or localization mismatch against the plan;
5. records finite nonnegative automated cost fields and explicit unmeasured human review time;
6. derives five controlled contrasts from verified case tables;
7. withholds aggregate release when any case or contrast is invalid;
8. emits no headline score and forbids ecological inference;
9. stages the complete bundle, self-verifies it, and publishes only after success;
10. removes staging output on failure.

The public index contains:

- exact plan and revision identities;
- ten ordered case summaries;
- stable semantic evidence and volatile complete-report evidence;
- method decisions and denominator status;
- localization result and concordance;
- development diagnostics and explicit review-time missingness;
- five machine-derived controlled contrasts;
- `semantic_sha256` over non-volatile pilot meaning;
- `index_sha256` over the complete index.

The semantic digest is the repeated-run comparison field. Complete index digests can vary with timestamp and timing fields.

## Development pilot archive

Schema:

```text
research/DW-001/schema/development-pilot-archive.schema.json
```

Implementation:

```text
src/deltawitness/_dw001_pilot_archive.py
src/deltawitness/dw001_pilot.py
```

The archive is a text-only retention format over one verified bundle. It contains:

- sorted unique safe relative JSON paths;
- every embedded object-valued JSON document;
- one digest per embedded file record;
- exact plan and pilot semantic digests;
- `archive_sha256` over the complete archive with its own field normalized to `null`.

Archive verification:

1. verifies the supplied sealed plan;
2. verifies archive structure, path safety, ordering, uniqueness, and per-file digests;
3. materializes embedded documents into a temporary directory;
4. reconstructs and verifies the complete pilot bundle;
5. rematerializes fixed fixtures and requires exact identity equality;
6. compares the embedded index semantic digest;
7. rejects missing or substituted documents even after digest recomputation.

The canonical archive is retained at:

```text
research/DW-001/development-pilot-archive.v1.json
```

Exact identities:

```text
plan_sha256            = 48a98f01c740862c91056841a7f96e6c98f1ae9641b7b364590a45d458ae3bcc
archive_sha256         = 3b992d67281693143a4e7bea920d1829f9b675eda592993db0e234239fcf4b06
index_semantic_sha256  = bd3c40d62e3d5695271db06f3bec476b4b9cd94442fd7171e1a03c70a74db5ef
```

A complete archive digest is expected to vary across equivalent reruns when embedded timestamps, timings, or complete-report digests vary. The semantic index digest must remain stable under equivalent fixed inputs and outcomes.

## JSON Schema boundary

The JSON Schemas define structural interoperability:

- exact property names and required fields;
- primitive types and enumerations;
- canonical tuple order for matrix states and methods;
- strict `additionalProperties: false` boundaries;
- digest and Git-object lexical forms;
- pilot plan/index/archive root and nested structures.

They do not express every relational invariant. Python semantic verifiers remain authoritative for observer mappings, path relations, state/cause consistency, method recomputation, partition/review effects, exclusions, deviations, costs, generated repository identity, pilot analysis, archive reconstruction, and cross-artifact correspondence.

No third-party schema dependency is added to the core package.

## Integrity and authentication

`descriptor_sha256`, `identity_sha256`, `binding_sha256`, `manifest_sha256`, `result_sha256`, `plan_sha256`, `semantic_sha256`, `index_sha256`, and `archive_sha256` are unkeyed integrity fields. They detect modification only when compared with separately trusted sources or expected values.

An attacker able to replace a complete artifact chain and every expected digest can replace the complete evidence chain.

Signing, producer identity, immutable timestamping, DSSE, in-toto, Sigstore, SCITT, and complete environment provenance remain separate future layers.

GitHub workflow, artifact, and commit metadata used during the one-time archive transport are historical process evidence, not producer authentication or non-repudiation.

## Privacy and publication

Fixture, binding, scenario, result, pilot-index, and archive artifacts can expose scenario and family identifiers, repository-relative paths, commands, test selectors, Git identities, generator and observer metadata, specification and artifact digests, authorization references, reviewer data, exclusions, deviations, counts, timings, and cost data.

Public artifacts must contain only public-safe identifiers and authorized material. Credentials, private endpoints, absolute local paths, environment values, confidential code, raw sensitive output, and unpublished vulnerability details remain prohibited.

The canonical pilot archive contains only fixed project-owned synthetic material. It does not authorize publication of analogous archives from real repositories.

## Non-claims

A valid fixture-to-result chain, complete pilot index, or verified pilot archive does not establish:

- patch correctness or security;
- test-oracle relevance or strength;
- taxonomy completeness or representativeness;
- ecological or held-out empirical effectiveness;
- prevalence, precision, recall, superiority, or production utility;
- native runtime cost for projected weaker methods;
- measured human review burden;
- scientific novelty;
- complete environment reproducibility;
- producer authenticity or timely preregistration;
- independent reproduction;
- authorization to execute an ecological development corpus or holdout;
- Gate 0 completion.

The contracts prevent specific fixture, relation, metadata, execution, retention, and denominator ambiguities. They do not substitute for protocol freeze, external review, sampling design, holdout commitment, containment, authentication, or independent reproduction.
