# DW-001 Deterministic Synthetic Fixture Generator v1

**Status:** development research infrastructure; not frozen; no held-out execution authorized.

The generator converts one strict DW-001 fixture descriptor into an owned-synthetic Git repository and a public-safe fixture identity. It exists to make a small set of controlled scenario mechanisms and known limitations reproducible and auditable before ecological execution.

## Artifact chain

```text
fixture descriptor
    -> deterministic synthetic repository
    -> fixture identity
    -> fixture-manifest binding
    -> four-state matrix report
    -> strict report decoding and digest verification
    -> DW-001 nested-method projection
```

Optional later development layers may consume the verified chain:

```text
claim-witness declaration and localization
weak-oracle mutation-control challenge
```

Schemas:

```text
research/DW-001/schema/fixture-descriptor.schema.json
research/DW-001/schema/fixture-identity.schema.json
research/DW-001/schema/fixture-manifest-binding.schema.json
research/DW-001/schema/weak-oracle-challenge.schema.json
```

Implementation:

```text
src/deltawitness/_dw001_scenarios.py
src/deltawitness/_dw001_wrong_reason.py
src/deltawitness/_dw001_weak_proxy.py
src/deltawitness/dw001_scenarios.py
src/deltawitness/dw001_oracle_challenge.py
```

The original internal generator implements the first three fixed families. The wrong-reason adapter implements import-error and unrelated-assertion probes. The weak-proxy adapter implements one oracle-strength negative control. None accepts arbitrary code, test, prompt, or mutant bytes.

The public module dispatches by verified family identifier, binds specification bytes to the descriptor, and applies fail-closed destination checks.

## Descriptor contract

A descriptor binds:

- study, schema, scenario, family, and control-role identifiers;
- generator and template IDs and versions;
- observer protocol and observer-arm identifier;
- exact command array and timeout;
- exact code, test, documentation, and specification paths;
- expected applicability, semantic outcome, and failure-cause class for every matrix state;
- expected decision and reason for every nested method;
- `descriptor_sha256` over the complete descriptor with that field normalized to `null`.

Expected method decisions are recomputed from expected state semantics. Recomputing the descriptor digest cannot make inconsistent state, failure-cause, observer, or method labels valid.

## Generator and template identities

Generator v1:

```text
id      = deltawitness-synthetic-python
version = 1
```

Template v1:

```text
id      = python-role-check
version = 1
```

The supported-family registry is implementation-controlled. During pre-freeze development, adding a family expands the v1 schema enum but does not reinterpret existing artifacts. Older verifiers may reject newer-family artifacts. Every study result must retain the exact generator, schema, and implementation commit; version strings alone do not authenticate code or freeze semantics.

The committed ten-arm development mechanism pilot remains fixed to the five families in its sealed plan. The later weak-proxy family is not silently added to that historical archive.

## Supported fixed families

Generator v1 currently supports:

- `valid-discriminating-regression`;
- `non-discriminating-candidate-test`;
- `candidate-regression-against-base-tests`;
- `wrong-reason-base-import-failure`;
- `wrong-reason-unrelated-assertion`;
- `weak-proxy-oracle`.

The first three families use one fixed role-check template and have observer-independent pass/fail state patterns, with failure-cause precision changing between `O0` and `O1` where applicable.

The two wrong-reason families are fixed observer or oracle-relevance controls. The weak-proxy family is a fixed oracle-strength control. They accept no caller-provided source, test, claim, prompt, collateral behavior, hidden check, or mutant bytes.

## Wrong-reason import observer pair

The import family uses a fixed candidate-introduced symbol and candidate tests that import that symbol before any intended assertion executes. Source and test bytes, family, control role, paths, timeout, generator, template, and scenario identity are held constant across observer arms. Observer-derived specification and Git identities may differ.

Under `exit-code-v1`:

```text
BB / BC / CB / CC  = pass / fail / pass / pass
failure cause BC   = test_failure_untyped
M0 / M1 / M2 / M3 = accept / accept / accept / accept
```

Under `outcome-receipt-v1`:

```text
BB / BC / CB / CC  = pass / error / pass / pass
ground-truth cause = import_error
receipt outcome    = test_error
M0 / M1 / M2 / M3 = accept / indeterminate / indeterminate / indeterminate
```

`import_error` is fixed pre-execution ground truth for the exact synthetic bytes. Receipt v1 records only generic `test_error`; it does not claim import, setup, collection, dependency, or infrastructure subtype attribution.

## Unrelated-assertion oracle-relevance negative control

The unrelated-assertion family uses fixed source and test bytes with two behavior dimensions:

```text
claim-facing behavior: is_admin(viewer)
collateral behavior:   version_label()
```

Base code keeps the buggy authorization rule and returns `v1` from `version_label()`. Candidate code repairs the authorization rule and returns `v2`.

Candidate tests include:

1. a claim-facing viewer test that asserts only that the result is a Boolean and therefore passes on both implementations;
2. a separate assertion that `version_label() == "v2"`, which fails only on the base.

Normative direct controls require:

- the claim-facing test to pass against both source versions;
- the complete candidate suite to fail against base code;
- the same suite with the exact collateral assertion removed to pass against base code;
- the collateral assertion to be the sole source of `BC = fail`;
- byte-identical source and test mechanism across observer arms.

Expected under `exit-code-v1`:

```text
BB / BC / CB / CC  = pass / fail / pass / pass
failure cause BC   = test_failure_untyped
M0 / M1 / M2 / M3 = accept / accept / accept / accept
```

Expected under `outcome-receipt-v1`:

```text
BB / BC / CB / CC  = pass / fail / pass / pass
failure cause BC   = assertion_failure
receipt outcome    = test_failure
receipt failures  >= 1
receipt errors      = 0
M0 / M1 / M2 / M3 = accept / accept / accept / accept
```

This is a negative control for suite-level failure provenance. Declared-selector localization later identifies that the claim-facing selector is not the source of fail-to-pass discrimination.

## Weak-proxy oracle-strength negative control

The weak-proxy family fixes a task prompt, base, candidate, candidate tests, one claim-violating mutant, and one hidden development claim check.

Base implementation:

```python
def is_admin(user):
    return user.get("role")
```

Candidate implementation:

```python
def is_admin(user):
    return user.get("role") == "admin"
```

Declared selector:

```text
test_access.AccessTests.test_viewer_result_is_boolean
```

Declared assertion:

```python
self.assertIsInstance(is_admin({"role": "viewer"}), bool)
```

This selector genuinely fails on base and passes on candidate, so both the canonical matrix and declared-selector localization accept it.

Fixed mutant:

```python
def is_admin(user):
    return bool(user.get("role"))
```

The mutant also returns a Boolean and therefore survives the declared selector while authorizing a viewer. A separately fixed hidden development check requires viewer denial and rejects the mutant.

Expected current evidence under both observers:

```text
BB / BC / CB / CC  = pass / fail / pass / pass
M0 / M1 / M2 / M3 = accept / accept / accept / accept
localization       = supported / discriminating
```

Expected fixed mutation controls:

```text
base      + declared selector = fail
candidate + declared selector = pass
mutant    + declared selector = pass
candidate + hidden claim      = pass
mutant    + hidden claim      = fail
```

The challenge executes the five controls through `outcome-receipt-v1`, binds exact source/test digests and invocation semantics, and emits a deterministic integrity-verifiable artifact.

Complete boundary:

```text
research/DW-001/WEAK_ORACLE_CHALLENGE.md
research/DW-001/schema/weak-oracle-challenge.schema.json
src/deltawitness/dw001_oracle_challenge.py
```

The hidden check is fixed mechanism evidence, not a general oracle. One surviving mutant does not define mutation adequacy, a mutation score, or ecological agent quality.

## Deterministic Git construction

For a validated supported descriptor, the generator:

1. requires an explicitly supplied absent or empty destination;
2. rejects a symbolic-link destination before any write;
3. initializes a SHA-1 Git repository with branch `main`;
4. disables system and global Git configuration for generator subprocesses;
5. disables line-ending conversion, file-mode sensitivity, signing, hooks, and Git LFS smudging relevant to this path;
6. writes fixed UTF-8 source, test, and TOML bytes;
7. stages literal known paths without a shell;
8. creates base and candidate commits with fixed author, committer, timestamps, and deterministic messages;
9. records exact base/head commit and tree IDs;
10. records SHA-256 of descriptor-derived specification bytes;
11. requires a clean generated repository;
12. emits an identity without absolute destination, username, host environment, or raw command output.

Two materializations of the same descriptor in separate clean directories must emit byte-equivalent identities and identical Git objects under the supported Git object model.

Paired observer probes intentionally generate different specification bytes because command and observer differ. Complete commit identities therefore need not match across observer arms. Normative tests compare underlying source and test blobs directly where observer-only equivalence is claimed.

## Fixture identity

The public identity binds:

- exact descriptor digest;
- generator, template, family, observer, and control role;
- base and candidate commit and tree IDs;
- Git object format;
- specification path and SHA-256;
- declared path categories;
- expected state and method semantics;
- `identity_sha256` over the complete identity with that field normalized to `null`.

`verify_fixture_identity_document` checks structure, family-specific semantic bindings, descriptor-derived specification bytes, and identity digest.

`verify_materialized_fixture` additionally checks that the supplied repository:

- is a literal directory rather than a symbolic link;
- is clean;
- has the recorded candidate `HEAD`;
- contains the recorded base and candidate trees;
- retains base ancestry;
- contains specification bytes matching the recorded digest.

## Matrix, localization, and challenge integration

Normative matrix integration:

1. runs the generated repository through `verify_repository`;
2. writes the report into private Git metadata;
3. reloads through strict UTF-8 JSON decoding;
4. verifies semantic and complete-report digests;
5. projects `M0` through `M3`;
6. compares observed states and decisions with descriptor ground truth.

The import-error pair additionally checks the O0/O1 failure/error contrast and indeterminate precedence.

The unrelated-assertion pair additionally checks direct collateral ablation and declared-selector mismatch.

The weak-proxy challenge additionally checks:

- canonical matrix support under both observer arms;
- typed assertion failure under O1;
- exact selector localization as `supported` and `discriminating`;
- five fixed mutation-control executions;
- candidate/mutant/test/hidden-check digests;
- deterministic semantic challenge bytes across clean runs;
- rejection of source, mutant, control, finding, or denominator substitution after digest recomputation.

## Packaged smoke boundary

CI executes complete fixture and challenge paths from the editable installation and after force-reinstalling the built wheel on Python 3.11–3.14.

The weak-proxy smoke reconstructs:

```text
descriptor
    -> repository and identity
    -> manifest and binding
    -> matrix report
    -> projection
    -> declaration and localization
    -> fixed mutation controls
    -> challenge verification
```

Packaged smoke confirms installation and public API reachability. It is not independent reproduction because it uses the same repository, fixtures, workflow, and development process.

## Destination safety

The public materializer accepts only:

- an absent final path whose immediate parent is trusted and writable; or
- an existing literal empty directory.

It rejects files, non-empty directories, symbolic-link destinations, and unsupported descriptors before materialization. It never deletes pre-existing destination content.

A failed Git or filesystem operation may leave newly created synthetic content in a previously absent or empty destination. Callers must use a disposable location and remove it after review.

The boundary does not prove that every ancestor is free of links, mount redirection, namespace changes, or hostile filesystem behavior. Destination ancestry remains an operator trust assumption.

## Environment and residual trust

The generator and challenge are shell-free but still trust:

- the `git` and Python executables resolved from `PATH`;
- Python and unittest semantics;
- operating-system and filesystem behavior;
- SHA-1 object-format support in installed Git;
- operator-supplied destination ancestry;
- the unsandboxed host process.

Fixture identity does not hash or attest Git, Python, dependencies, kernel, filesystem, locale, hardware, or container image. Equivalent Git identities are not complete environment equivalence.

The receipt binding is visible to tested code and receipts are unsigned. A malicious repository could influence the adapter. The fixed challenge uses only project-owned bytes; it does not make the runner safe for external code.

## Privacy and publication

Public fixture and challenge artifacts omit:

- absolute paths;
- usernames and home directories;
- credentials and environment values;
- raw process output and tracebacks;
- private repository names;
- external endpoints;
- model credentials or private prompts.

Scenario IDs, family labels, prompts, selectors, paths, commands, Git identities, observer metadata, aggregate counts, and digests remain publication metadata requiring review.

Raw failure narratives remain excluded by default. Output digests can still fingerprint low-entropy values and are not a redaction mechanism.

## Prior-art boundary

Structured test reports, framework-native result objects, fail-to-pass validation, the test-oracle problem, mutation testing, mutation adequacy, weak and partial oracles, hidden tests, assertion quality, coverage, and coincidental correctness are established.

No novelty claim is made for distinguishing failure from error, localizing a test selector, constructing a weak assertion, or killing and surviving mutants. The narrower purpose is to place positive evidence and known limitations inside one deterministic, Git-native, typed, integrity-bound study pipeline.

Whether that integration is scientifically novel or practically superior remains unestablished.

## Non-goals

Generator v1 and the weak-oracle challenge do not:

- support arbitrary source blobs, tests, prompts, or mutants;
- model every issue #2 family;
- infer import-error subtype from receipt v1;
- infer claim relevance or strength from assertion failure;
- define a mutation score or coverage criterion;
- generate realistic multi-package dependency environments;
- estimate mechanism prevalence, observer accuracy, or oracle-analysis accuracy;
- establish cross-platform environment equivalence;
- authenticate producer, reviewer, model, or agent identity;
- provide containment;
- authorize ecological or held-out execution.

## Claim boundary

A valid fixture identity shows only that one supported descriptor was deterministically materialized into recorded synthetic Git and specification identities.

The import-error pair establishes one controlled observer-classification difference. The unrelated-assertion pair establishes one suite-level oracle-relevance limitation. The weak-proxy challenge establishes one case where current typed, four-state, and declared-selector evidence accepts a selector that one fixed claim-violating mutant survives.

These results do not establish representativeness, prevalence, complete failure diagnosis, oracle adequacy, mutation adequacy, general observer or method superiority, protocol freeze, ecological effectiveness, or any confirmatory conclusion.