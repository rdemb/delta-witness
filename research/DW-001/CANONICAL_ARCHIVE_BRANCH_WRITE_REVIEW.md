# DW-001 Canonical Archive One-Time Branch Write Review

**Status:** completed historical exception. One exact archive-only write was made to draft PR #29, the resulting commit was reviewed and verified, and the temporary `contents: write` job was removed. No continuing repository-write capability remains.

This approval does not authorize a reusable DeltaWitness feature, main-branch write, release publication, holdout execution, or real-repository evidence upload.

## Problem

The canonical development-pilot archive is a large UTF-8 JSON document produced and self-verified by the sealed ten-arm runner. Moving its exact bytes through manually segmented API calls created unnecessary transcription and assembly risk.

A one-time same-repository PR job therefore rendered, verified, and committed exactly one canonical archive file to the existing branch.

## Executed capability

Temporary job permission:

```yaml
permissions:
  contents: write
```

Executed constraints:

- event: same-repository pull request;
- authorized branch: `research/dw-001-development-pilot-v1`;
- main-branch writes explicitly rejected;
- checkout used the PR head branch, not the synthetic merge ref;
- exact output path:

```text
research/DW-001/development-pilot-archive.v1.json
```

- exact committed plan used;
- archive passed complete archive and reconstructed-bundle verification before staging;
- staged-path allowlist permitted only the archive addition and deletion of the abandoned segmented-transport manifest;
- no force push, tag, release, issue mutation, PR metadata mutation, secret, OIDC token, cloud credential, or external endpoint;
- fixed commit message.

Execution record:

```text
workflow run       = 31953455595
run number         = 195
workflow head      = 82890485c9b992e3db24dc4519aa6e7af08b0408
write job          = 95180639759
generated commit   = 4a34d15e005b051fe5a5aa957bb056c1692ac9d2
archive Git blob   = 65f3034b56dc2eb523018d68ff09d0e2e4cd54e4
archive_sha256     = 3b992d67281693143a4e7bea920d1829f9b675eda592993db0e234239fcf4b06
semantic_sha256    = bd3c40d62e3d5695271db06f3bec476b4b9cd94442fd7171e1a03c70a74db5ef
```

Final pre-merge validation before this checklist closure:

```text
workflow run       = 31955828629
run number         = 212
validated head     = ab5f3cb44dae83f0b213e503c14fff0c8413d2b3
Python 3.11 tests  = 223 / 223
Python matrix      = 3.11, 3.12, 3.13, 3.14 success
```

## Threat-model amendment

### Temporary threat

The GitHub-hosted runner received a token able to write repository contents on the PR branch. A compromised workflow, dependency, or command could have attempted another tracked modification.

### Applied mitigations

1. **Branch and event pinning:** only the exact same-repository PR branch was accepted.
2. **Minimal write job:** the write token was not used by the ordinary matrix-test jobs. The write job performed checkout, Python setup, project install, fixed-plan archive rendering, archive verification, exact diff review, commit, and push.
3. **Fixed path allowlist:** staged files were restricted to the canonical archive and deletion-only cleanup of the abandoned transport manifest.
4. **No free-form source generation:** output came from fixed project-owned fixtures and the committed plan.
5. **Self-verification:** archive verification reconstructed the full bundle and reran every semantic and cross-artifact verifier.
6. **No main write:** the push target was the exact PR head ref.
7. **No persistence:** the write job and `contents: write` were removed after the generated commit.
8. **Audit trail:** workflow, generated commit, archive digest, semantic digest, and exact changed paths are retained.
9. **Exact retained file set:** final bundle and archive verification derives all 84 allowed files from the sealed plan and rejects missing, duplicate, unsafe, linked, special, or unexpected JSON and non-JSON entries.

## Residual risks

- GitHub Actions, the runner image, checkout/setup actions, Git, Python, package build backend, and token handling were trusted for the one operation.
- `GITHUB_TOKEN` authenticated the workflow to GitHub but did not authenticate the scientific truth of the archive.
- Workflow and commit timestamps do not prove that every semantic input existed at an earlier claimed time.
- A malicious branch modification could have influenced rendering; fixed bytes, the sealed plan, semantic verification, exact diff review, committed-archive tests, and final clean CI reduce but do not cryptographically eliminate that risk.
- Archive digests remain unkeyed and are not non-repudiation or transparency receipts.

## Privacy boundary

The committed archive contains only project-owned synthetic evidence. Archive and public-tree tests exclude:

- absolute paths;
- usernames and home directories;
- credentials, tokens, and environment values;
- private endpoints;
- raw stdout, stderr, and tracebacks;
- real repository source;
- holdout identifiers and confirmatory eligibility.

## Completion record

- [x] archive committed by the exact branch-scoped job;
- [x] generated commit changed only allowlisted paths;
- [x] committed archive passed strict archive and bundle verification;
- [x] archive and semantic digests recorded;
- [x] abandoned segmented-transport manifest removed;
- [x] committed-archive regression and complete packaged smoke added;
- [x] temporary write job and `contents: write` removed;
- [x] final PR CI passed on Python 3.11–3.14 after all substantive documentation updates;
- [x] final PR diff, changed-file list, comments, reviews, and unresolved review threads were checked before merge.

## Current permission state

The final workflow has returned to:

```yaml
permissions:
  contents: read
```

There is no archive upload job and no branch-write job.

## Claim boundary

This record documents one completed repository transport operation. It does not establish producer authenticity, immutable timestamping, legal admissibility, containment, empirical effectiveness, external reproduction, protocol freeze, holdout authorization, production readiness, scientific novelty, or permission to repeat the mechanism without a new review.