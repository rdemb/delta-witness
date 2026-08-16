# DW-001 Canonical Archive One-Time Branch Write Review

**Status:** approved for one temporary write on draft PR #29 only. This approval expires immediately after the exact canonical archive is committed and independently verified. It does not authorize a reusable DeltaWitness feature, main-branch write, release publication, holdout execution, or real-repository evidence upload.

## Problem

The canonical development-pilot archive is a 473,047-byte UTF-8 JSON document produced and self-verified by the sealed ten-arm runner. The connected GitHub API can inspect and edit ordinary source files, but moving this exact large file through repeated manually segmented API calls creates avoidable transcription and assembly risk.

GitHub Actions already produced and transported the same public-safe archive as a one-day artifact under the prior reviewed transport boundary. The least ambiguous remaining method is a one-time job that renders the archive from the committed plan, verifies it, commits exactly one canonical JSON file to the existing PR branch, and exits permanently once that path exists.

## Authorized capability

A temporary job may receive:

```yaml
permissions:
  contents: write
```

under all of the following constraints:

- event must be a pull request from the same repository;
- head ref must equal `research/dw-001-development-pilot-v1`;
- target ref must be that PR branch, never `main`;
- job checks out the PR head branch, not the synthetic merge ref;
- exact output path is:

```text
research/DW-001/development-pilot-archive.v1.json
```

- the renderer must use the already committed `development-pilot-plan.v1.json`;
- the archive must pass `verify_development_pilot_archive_document` before commit;
- only the archive file and removal of the abandoned segmented-transport directory may enter the generated commit;
- the job refuses to commit when any other tracked change exists;
- if the canonical archive path already exists, the job exits without writing;
- commit message is fixed;
- no force push, tag, release, issue change, PR metadata change, or main-branch update is permitted;
- no secret, OIDC token, cloud credential, external endpoint, or third-party upload action is used.

## Threat-model amendment

### New temporary threat

The GitHub-hosted runner receives a token capable of writing repository contents on the PR branch. A compromised workflow, dependency, or tested command could attempt to modify another tracked file or push an unauthorized commit.

### Mitigations

1. **Branch and event pinning:** the job runs only for the exact same-repository PR branch.
2. **Minimal job:** it does not run the ordinary repository test suite or untrusted repository targets under the write token. It performs only checkout, Python setup, editable install of this repository, canonical archive rendering, archive verification, exact diff review, commit, and push.
3. **Fixed path allowlist:** before commit, the staged path set must equal exactly:

```text
research/DW-001/development-pilot-archive.v1.json
research/DW-001/development-pilot-archive.v1/manifest.json  # deletion only, if present
```

No base64 payload part is required or permitted.
4. **No shell-generated source:** output is derived by the reviewed renderer from fixed project-owned fixtures and the committed plan.
5. **Self-verification:** the archive reconstructs the full bundle and reruns every semantic and cross-artifact verifier before the file is staged.
6. **No main write:** the push ref is the exact PR head ref and the job explicitly rejects `main`.
7. **No persistence:** the job and `contents: write` permission must be removed before PR merge; final CI must pass after removal.
8. **Audit trail:** the generated commit, workflow run, archive digest, semantic digest, and exact diff are retained in the PR evidence.

## Residual risks

- GitHub Actions, the runner image, checkout/setup actions, Git executable, Python runtime, package build backend, and repository token handling remain trusted for this one operation.
- `GITHUB_TOKEN` authenticates the workflow to GitHub but does not authenticate the scientific truth of the archive contents.
- The commit timestamp and GitHub workflow metadata do not prove that all semantic inputs were created at the claimed earlier time.
- A malicious modification already present in the branch could influence rendering; this is mitigated by the committed plan, fixed fixture bytes, semantic verifiers, final diff review, and post-write clean CI, not eliminated cryptographically.
- The archive digests remain unkeyed and are not non-repudiation or transparency receipts.

## Privacy boundary

The written archive contains only project-owned synthetic evidence. Existing archive and public-tree tests reject:

- absolute paths;
- usernames and home directories;
- credentials, tokens, or environment values;
- private endpoints;
- raw stdout, stderr, and traceback text;
- real repository source;
- holdout identifiers or confirmatory eligibility.

## Completion gates

- [ ] archive file committed by the exact branch-scoped job;
- [ ] generated commit changes only allowlisted paths;
- [ ] committed archive passes strict archive and bundle verification;
- [ ] committed archive digest and semantic digest recorded;
- [ ] abandoned segmented-transport manifest removed;
- [ ] temporary write job and `contents: write` removed;
- [ ] final PR CI passes on Python 3.11–3.14 after removal;
- [ ] PR diff and unresolved review threads checked before merge.

## Claim boundary

This review authorizes one repository transport operation. It does not establish producer authenticity, immutable timestamping, legal admissibility, containment, empirical effectiveness, external reproduction, protocol freeze, holdout authorization, production readiness, scientific novelty, or permission to repeat the mechanism in another workflow without a new review.
