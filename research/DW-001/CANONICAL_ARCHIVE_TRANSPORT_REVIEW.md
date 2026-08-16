# DW-001 Canonical Archive Transport Review

**Status:** completed historical exception. The one-day artifact transport was used once for the public-safe owned-synthetic development archive, the downloaded bytes were independently checked, and the upload step was removed. No continuing upload capability remains.

This approval did not and does not apply to real repositories, private corpora, holdout material, credentials, raw logs, or future runs.

## Decision

A short-lived GitHub Actions artifact transported one self-verified file:

```text
dw001-development-pilot-archive.v1.json
```

The artifact was used only to recover and independently inspect canonical JSON bytes from the GitHub-hosted runner while designing permanent repository retention.

This was a narrow exception to the default no-external-upload boundary. It added no DeltaWitness product feature, network API, telemetry path, remote-execution capability, secret, or repository write permission.

## Executed mechanism

- action: `actions/upload-artifact`;
- pinned action commit: `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` (`v7.0.1`);
- workflow run: `31952593720`;
- artifact ID: `9265084676`;
- exact upload path: one JSON file in `RUNNER_TEMP`;
- retention: one day;
- workflow permissions:

```yaml
permissions:
  contents: read
```

No OIDC token, secret, cloud credential, external endpoint, write permission, or directory glob was configured.

## Data boundary

The transported file was produced exclusively from project-owned synthetic fixtures and contained:

- versioned descriptor, identity, manifest, binding, report, projection, declaration, localization, result, plan, and index JSON documents;
- repository-relative synthetic paths;
- synthetic Git object identities;
- commands, observer identifiers, aggregate counts, digests, and development-only costs;
- no real repository source or private corpus.

The archive and privacy verifiers reject or exclude:

- absolute local paths;
- usernames and home directories;
- credentials, tokens, secrets, and environment values;
- private endpoints;
- raw stdout, stderr, and tracebacks;
- arbitrary extra files and non-JSON payloads;
- holdout or primary-denominator eligibility.

## Threats and mitigations

### Accidental disclosure

**Threat:** a broad path uploads unrelated runner files.

**Mitigation:** one exact reviewed filename was uploaded; the source archive self-verified before transport.

### Action substitution

**Threat:** a moving action tag changes behavior.

**Mitigation:** the immutable action commit was pinned.

### Archive substitution or corruption

**Threat:** transported bytes differ from the verified archive.

**Mitigation:** the archive contained per-document digests, `archive_sha256`, `index_semantic_sha256`, the exact plan digest, and a verifier that reconstructs and re-verifies the complete directory bundle. The downloaded ZIP and embedded archive were inspected outside the runner.

### Retention and access ambiguity

**Threat:** GitHub retains a second copy or account access exposes it.

**Mitigation:** content was public-safe and synthetic, retention was one day, the workflow upload step was removed, and GitHub storage was treated as untrusted transport rather than canonical evidence.

### False provenance interpretation

**Threat:** artifact hosting is mistaken for producer authentication, timestamp proof, or immutable transparency.

**Mitigation:** the artifact was transport-only. GitHub hosting, run metadata, and unkeyed digests do not authenticate the producer, prove creation time, establish non-repudiation, or make the study confirmatory.

## Completion record

- [x] source bundle self-verified before upload;
- [x] file contained only owned-synthetic public-safe JSON evidence;
- [x] action pinned to an exact commit;
- [x] workflow permissions remained `contents: read`;
- [x] retention limited to one day;
- [x] downloaded artifact and embedded archive independently inspected;
- [x] canonical archive subsequently committed and covered by regression tests;
- [x] upload step removed;
- [x] no continuing upload capability remains.

Final repository archive:

```text
research/DW-001/development-pilot-archive.v1.json
archive_sha256 = 3b992d67281693143a4e7bea920d1829f9b675eda592993db0e234239fcf4b06
```

## Claim boundary

This record documents one completed transport exception. It does not authorize network access from DeltaWitness, routine artifact uploads, real-repository evidence export, holdout publication, telemetry, producer authentication, signed attestations, containment, empirical-effectiveness claims, or reuse of this mechanism without a new review.
