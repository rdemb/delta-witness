# DW-001 Canonical Archive Transport Review

**Status:** approved for one-time use on the public-safe owned-synthetic development archive in draft PR #29. This approval does not apply to real repositories, private corpora, holdout material, credentials, raw logs, or future runs.

## Decision

Use one short-lived GitHub Actions artifact to transport exactly one already self-verified file:

```text
dw001-development-pilot-archive.v1.json
```

The artifact exists only to recover the canonical JSON archive from the GitHub-hosted runner and commit that exact archive into the repository. After the committed archive is independently verified, the upload step must be removed before PR merge.

This is a narrow exception to the default no-external-upload boundary. It does not add a product feature, network API, telemetry path, remote execution capability, secret, or new repository permission.

## Data boundary

The uploaded file is produced exclusively from project-owned synthetic fixtures and contains:

- versioned descriptor, identity, manifest, binding, report, projection, declaration, localization, result, plan, and index JSON documents;
- repository-relative synthetic paths;
- synthetic Git object identities;
- commands, observer identifiers, aggregate counts, digests, and development-only costs;
- no real repository source code or private corpus.

The archive verifier and privacy tests reject or exclude:

- absolute local paths;
- usernames and home directories;
- credentials, tokens, or secrets;
- environment values;
- private endpoints;
- raw stdout, stderr, or traceback text;
- arbitrary extra files;
- non-JSON payloads;
- holdout or primary-denominator eligibility.

## Transport mechanism

- action: `actions/upload-artifact`
- pinned commit: `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` (`v7.0.1`)
- workflow permissions remain:

```yaml
permissions:
  contents: read
```

- no OIDC, token, secret, write permission, or external endpoint is configured;
- exact upload path is one file in `RUNNER_TEMP`, not a directory glob;
- retention is one day;
- missing file is a hard error;
- the artifact ZIP is downloaded through the connected GitHub API and the embedded archive is verified before use.

## Threats and mitigations

### Accidental disclosure

**Threat:** a broad path or directory glob uploads unrelated runner files.

**Mitigation:** upload one exact filename created by the reviewed renderer. The renderer emits only the canonical public-safe archive.

### Action substitution

**Threat:** a moving action tag changes behavior.

**Mitigation:** pin the immutable action commit SHA and record the upstream release mapping in the PR evidence.

### Archive substitution or corruption

**Threat:** transported bytes differ from the self-verified archive.

**Mitigation:** the archive contains per-document digests, `archive_sha256`, `index_semantic_sha256`, the exact plan digest, and a verifier that reconstructs and re-verifies the complete directory bundle. The downloaded file is rejected before commit if any check fails.

### Retention or access ambiguity

**Threat:** GitHub retains a second copy longer than intended or account access exposes it.

**Mitigation:** use one-day retention, public-safe synthetic content only, remove the workflow upload step after recovery, and treat GitHub storage as untrusted transport rather than canonical evidence.

### False provenance interpretation

**Threat:** artifact hosting is mistaken for producer authentication, timestamp proof, or immutable transparency.

**Mitigation:** the artifact is explicitly transport-only. GitHub hosting, run metadata, and unkeyed digests do not authenticate the producer, prove creation time, establish non-repudiation, or make the study confirmatory.

## Acceptance gates

The temporary upload may be used only when all are true:

- [x] the source bundle self-verifies before upload;
- [x] the file contains only owned-synthetic public-safe JSON evidence;
- [x] the action is pinned to an exact commit;
- [x] workflow permissions remain `contents: read`;
- [x] retention is limited to one day;
- [x] the exact downloaded archive is verified before commit;
- [ ] the exact archive is committed and covered by a committed-archive regression test;
- [ ] the upload step is removed before PR merge;
- [ ] final CI passes after removal.

## Claim boundary

This review authorizes only one transport operation for one public-safe development archive. It does not authorize network access from DeltaWitness, routine artifact uploads, real-repository evidence export, holdout publication, external telemetry, producer authentication, signed attestations, containment, or any empirical-effectiveness claim.
