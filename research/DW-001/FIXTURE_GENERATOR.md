# DW-001 Deterministic Synthetic Fixture Generator v1

**Status:** development-pilot infrastructure; not frozen; no pilot or held-out execution authorized.

The generator converts one strict DW-001 fixture descriptor into an owned-synthetic Git repository and a public-safe fixture identity. It exists to make a small set of controlled scenario mechanisms reproducible and auditable before a development pilot.

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

Schemas:

```text
research/DW-001/schema/fixture-descriptor.schema.json
research/DW-001/schema/fixture-identity.schema.json
research/DW-001/schema/fixture-manifest-binding.schema.json
```

Implementation:

```text
src/deltawitness/_dw001_scenarios.py
src/deltawitness/_dw001_wrong_reason.py
src/deltawitness/dw001_scenarios.py
```

The original internal generator implements the first three fixed families. The separate wrong-reason adapter implements one paired observer probe without accepting arbitrary code or test bytes. The public module dispatches by verified family identifier, binds specification bytes to the descriptor, and applies fail-closed destination checks.

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

Expected method decisions are recomputed from expected state semantics. Recomputing the descriptor digest cannot make inconsistent state or method labels valid.

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

The supported family registry is implementation-controlled. During pre-freeze development, adding a family expands the v1 schema enum but does not reinterpret existing artifacts. Older verifiers may reject newer-family artifacts. Every study result must therefore retain the exact generator, schema, and implementation commit; version strings alone do not authenticate code or freeze semantics.

## Supported fixed families

Generator v1 currently supports:

- `valid-discriminating-regression`;
- `non-discriminating-candidate-test`;
- `candidate-regression-against-base-tests`;
- `wrong-reason-base-import-failure`.

The first three families use one fixed role-check template and have observer-independent pass/fail state patterns, with failure-cause precision changing between `O0` and `O1` where applicable.

The wrong-reason family uses a fixed candidate symbol and fixed candidate tests that import that symbol before any intended assertion executes. Its source and test bytes, family, control role, paths, timeout, generator, template, and scenario identity are held constant across observer arms. Observer, observer ID, command, derived state semantics, derived method semantics, descriptor digest, and the resulting specification/Git identity differ as required by the observer contract.

### Wrong-reason observer pair

Under `exit-code-v1`:

```text
BB / BC / CB / CC = pass / fail / pass / pass
failure cause BC  = test_failure_untyped
M0 / M1 / M2 / M3 = accept / accept / accept / accept
```

Under `outcome-receipt-v1`:

```text
BB / BC / CB / CC = pass / error / pass / pass
ground-truth BC cause = import_error
receipt BC outcome    = test_error
M0 / M1 / M2 / M3 = accept / indeterminate / indeterminate / indeterminate
```

`import_error` is fixed pre-execution ground truth for the exact synthetic bytes. Receipt v1 records only the generic runtime class `test_error`; it does not claim import/setup/collection subtype attribution.

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
10. records SHA-256 of the specification bytes derived from the descriptor;
11. requires a clean generated repository;
12. emits an identity without absolute destination, username, host environment, or raw command output.

Two materializations of the same descriptor in separate clean directories must emit byte-equivalent identities and identical Git objects under the supported Git object model.

The paired observer probe intentionally generates different specification bytes because the command and observer differ. Therefore its complete commit identities need not match across observer arms. Normative tests compare the underlying base/candidate source and test blobs directly and require them to be byte-identical.

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

- is a literal directory rather than a symlink;
- is clean;
- has the recorded candidate `HEAD`;
- contains the recorded base and candidate trees;
- retains base ancestry;
- contains specification bytes matching the recorded digest.

## Matrix and observer integration

Normative integration does not project an in-memory report representation directly. It:

1. runs the generated repository through `verify_repository`;
2. writes the matrix report into private Git metadata;
3. reloads it through the strict UTF-8 JSON loader;
4. verifies semantic and full-report digests;
5. projects `M0` through `M3` from the decoded artifact;
6. compares observed states and method decisions with descriptor ground truth.

For the wrong-reason pair, integration additionally requires:

- the same scenario ID across `O0` and `O1`;
- byte-identical source and test mechanisms;
- `O0` to expose a complete canonical-looking witness;
- `O1` to record `test_error`, zero assertion failures, at least one error, and incomplete evidence;
- `M0` to remain unchanged while `M1`–`M3` become indeterminate;
- valid descriptor, identity, materialized repository, manifest, binding, report, and projection artifacts under each arm.

## Destination safety

The public materializer accepts only:

- an absent final path whose immediate parent is trusted and writable; or
- an existing literal empty directory.

It rejects files, non-empty directories, symbolic-link destinations, and unsupported descriptors before materialization. It never deletes pre-existing destination content.

A failed Git or filesystem operation may leave newly created synthetic content in a previously absent or empty destination. Callers must use a disposable location and remove it after review.

The boundary does not prove that every ancestor directory is free of links, mount redirection, namespace changes, or hostile filesystem behavior. Destination ancestry remains an operator trust assumption.

## Environment and residual trust

The generator is shell-free but still trusts:

- the `git` executable resolved from `PATH`;
- Python runtime behavior;
- operating-system and filesystem semantics;
- SHA-1 object-format support in the installed Git;
- the operator-supplied destination ancestry;
- the current unsandboxed process and host.

The identity does not hash or attest Git, Python, dependencies, kernel, filesystem, locale, hardware, or container image. Equivalent Git identities are not complete environment equivalence.

The built-in unittest adapter executes inside tested Python import semantics. A malicious repository can influence it. The receipt binding is visible and unsigned.

## Privacy and publication

The generator uses only project-owned synthetic source and test bytes. Public fixture artifacts omit:

- absolute paths;
- usernames and home directories;
- credentials and environment values;
- raw process output and tracebacks;
- private repository names;
- external endpoints.

Scenario IDs, family labels, paths, commands, Git identities, observer metadata, and digests remain publication metadata requiring review.

The typed wrong-reason report may contain output digests and aggregate counts, but raw traceback remains excluded by default.

## Non-goals

Generator v1 does not:

- support arbitrary source blobs or caller-provided executable code;
- model every issue #2 family;
- infer import-error subtype from receipt v1;
- generate realistic multi-package dependency environments;
- estimate mechanism prevalence or observer accuracy;
- establish cross-platform Git identity equivalence;
- authenticate producer, reviewer, or agent identity;
- provide containment;
- authorize pilot or holdout execution.

## Claim boundary

A valid fixture identity shows that one supported descriptor was deterministically materialized into recorded synthetic Git and specification identities and can be checked through the binding, matrix, and projection pipeline.

The paired wrong-reason fixture establishes one controlled example where preserving generic test-error evidence changes nested-method decisions relative to exit-code-only classification. It does not show that the scenario is representative, that receipt v1 identifies every failure cause, that typed receipts are generally superior, or that any empirical or confirmatory conclusion is warranted.
