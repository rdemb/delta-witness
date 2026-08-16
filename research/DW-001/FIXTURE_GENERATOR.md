# DW-001 Deterministic Synthetic Fixture Generator v1

**Status:** development-pilot infrastructure; not frozen; no pilot or held-out execution authorized.

The generator converts one strict DW-001 fixture descriptor into an owned-synthetic Git repository and a public-safe fixture identity. It exists to make the smallest scenario subset reproducible and auditable before a development pilot.

## Artifact chain

```text
fixture descriptor
    -> deterministic synthetic repository
    -> fixture identity
    -> four-state matrix report
    -> strict report decoding and digest verification
    -> DW-001 nested-method projection
```

Schemas:

```text
research/DW-001/schema/fixture-descriptor.schema.json
research/DW-001/schema/fixture-identity.schema.json
```

Implementation:

```text
src/deltawitness/_dw001_scenarios.py
src/deltawitness/dw001_scenarios.py
```

The internal module produces and validates deterministic descriptor and identity semantics. The public module adds fail-closed destination checks before any file or Git operation.

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

Expected method decisions are recomputed from expected state semantics. Recomputing the descriptor digest cannot make an inconsistent stored method decision valid.

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

Changing a family, observer, command, path contract, expected state, generator version, or template version changes the descriptor digest. The frozen protocol must also pin the exact DeltaWitness implementation commit; a semantic version string alone does not authenticate the generator code.

## Deterministic Git construction

For a validated supported descriptor, the generator:

1. requires an explicitly supplied absent or empty destination;
2. rejects a symbolic-link destination before any write;
3. initializes a SHA-1 Git repository with branch `main`;
4. disables system and global Git configuration for generator subprocesses;
5. disables `core.autocrlf`, file-mode sensitivity, commit signing, hooks, and Git LFS smudging relevant to this path;
6. writes fixed UTF-8 source, test, and TOML bytes;
7. stages literal known paths without a shell;
8. creates a base and candidate commit with fixed author, committer, timestamps, and deterministic messages;
9. records exact base/head commit and tree IDs;
10. records the SHA-256 digest of the unchanged specification bytes;
11. requires a clean generated repository;
12. emits an identity without an absolute destination, username, host environment, or raw command output.

Two materializations of the same descriptor in separate clean directories are required to emit byte-equivalent identities and identical Git objects under the supported Git object model.

## Fixture identity

The public identity binds:

- the exact descriptor digest;
- generator, template, family, observer, and control role;
- base and candidate commit and tree IDs;
- Git object format;
- specification path and SHA-256;
- declared path categories;
- expected state and method semantics;
- `identity_sha256` over the complete identity with that field normalized to `null`.

`verify_fixture_identity_document` checks structure, deterministic semantic bindings, and the identity digest.

`verify_materialized_fixture` additionally checks the supplied repository:

- exists as a literal directory rather than a symlink;
- is clean;
- has the recorded candidate `HEAD`;
- contains the recorded base and candidate trees;
- retains base ancestry;
- contains specification bytes matching the recorded digest.

## Matrix integration

The normative integration test does not project an in-memory Python dataclass directly. It:

1. runs the generated repository through `verify_repository`;
2. writes the matrix report into private Git metadata;
3. reloads the report through the strict UTF-8 JSON loader;
4. verifies both report digests;
5. projects the nested DW-001 methods from the decoded artifact;
6. compares observed states and method decisions with the descriptor contract.

This keeps the generator test on the same artifact boundary intended for study evidence.

## Destination safety

The public materializer accepts only:

- an absent final path whose immediate parent is trusted and writable; or
- an existing literal empty directory.

It rejects:

- files;
- non-empty directories;
- symbolic-link destinations;
- unsupported descriptors before materialization.

It never deletes pre-existing destination content. A failed Git or filesystem operation may leave newly created synthetic content in a previously absent or empty destination; callers should use a disposable location and remove it explicitly after review.

The current boundary does not prove that every ancestor directory is free of symlinks or mount redirection. The destination parent remains an operator-controlled trust assumption.

## Environment and residual trust

The generator is shell-free, but it still trusts:

- the `git` executable resolved from the supplied `PATH`;
- operating-system filesystem semantics;
- Python runtime behavior;
- repository object-format support in the installed Git version;
- the trusted operator-supplied destination parent;
- the current process and host, which are not sandboxed.

The emitted identity does not hash the Git binary, Python binary, kernel, filesystem, locale implementation, or container image. Environment capture and containment remain separate DW-001 prerequisites.

## Privacy and publication

The generator uses only synthetic source and test bytes owned by the project. Its identity intentionally omits:

- absolute paths;
- usernames and home directories;
- credentials and environment values;
- raw process output;
- private repository names;
- external endpoints.

The scenario ID, family, paths, commands, Git identities, and specification digest are still public metadata and require review before inclusion in a published study artifact.

## Non-goals

Generator v1 does not:

- support arbitrary source blobs or user-supplied executable code;
- generate realistic multi-package dependency environments;
- model every issue #2 family;
- estimate real-world prevalence;
- establish cross-platform Git identity equivalence beyond the tested environment;
- authenticate the generator or identity producer;
- provide a sandbox;
- authorize pilot or holdout execution.

## Claim boundary

A valid fixture identity shows that one supported descriptor was deterministically materialized into the recorded synthetic Git and specification identities and can be checked through the matrix/projection pipeline. It does not show that the scenario is realistic, representative, independently reviewed, empirically useful, secure to execute on a sensitive host, or suitable for confirmatory inference.
