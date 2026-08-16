# DW-001 Development Mechanism Pilot v1

**Status:** executed, retained, and independently re-verifiable within the repository. Development-only mechanism evidence. Not a holdout, effectiveness study, ecological sample, protocol freeze, or independent external reproduction.

## 1. Question answered

The pilot tested one deliberately narrow engineering question:

> Can the five fixed owned-synthetic DW-001 families, under both supported observer arms, execute through the complete retained evidence chain without manual artifact repair, hidden denominator changes, or post-result relabeling?

It did **not** estimate how often any mechanism occurs in real coding-agent patches.

## 2. Frozen execution inputs

The exact pre-execution plan is retained at:

```text
research/DW-001/development-pilot-plan.v1.json
```

Pinned identities:

```text
study_id                   = DW-001
pilot_id                   = DW-001-DEV-PILOT-V1
partition                  = development
protocol_commit_sha        = 732f829e25ea994858fffb0678892048617155c3
implementation_commit_sha  = 4ef67e0e7a20c7de03be825720dfb2d1da8e64fc
plan_sha256                = 48a98f01c740862c91056841a7f96e6c98f1ae9641b7b364590a45d458ae3bcc
```

`implementation_commit_sha` pins the evidence-producing matrix, fixture, localization, runner, and semantic-verification implementation used when the plan was sealed. Archive packaging and reviewed transport were subsequently exercised at workflow head:

```text
82890485c9b992e3db24dc4519aa6e7af08b0408
```

The one-time workflow run was:

```text
workflow run  = 31953455595
run number    = 195
conclusion    = success
```

The archive-only generated commit was:

```text
4a34d15e005b051fe5a5aa957bb056c1692ac9d2
```

The temporary write capability was removed before final review. The normal workflow again has only:

```yaml
permissions:
  contents: read
```

## 3. Retained canonical evidence

Canonical archive:

```text
research/DW-001/development-pilot-archive.v1.json
```

Exact identities:

```text
archive_sha256         = 3b992d67281693143a4e7bea920d1829f9b675eda592993db0e234239fcf4b06
index_semantic_sha256  = bd3c40d62e3d5695271db06f3bec476b4b9cd94442fd7171e1a03c70a74db5ef
Git blob SHA           = 65f3034b56dc2eb523018d68ff09d0e2e4cd54e4
embedded JSON files    = 84
case arms               = 10
matrix states executed  = 40
selector states         = 12
commands                = 52
```

The archive contains, as applicable for each arm:

```text
fixture descriptor
fixture identity
scenario manifest
fixture-manifest binding
matrix report
M0-M3 projection
claim-witness declaration
claim-witness localization
result record
```

It also retains the sealed plan and complete pilot index.

The archive verifier:

1. strict-decodes every embedded JSON object;
2. checks sorted unique safe relative paths;
3. verifies every per-document digest;
4. reconstructs the complete directory bundle;
5. reruns all artifact-specific semantic verifiers;
6. reruns all cross-artifact relation verifiers;
7. rematerializes every synthetic fixture from its descriptor;
8. verifies the pilot index and five controlled contrasts;
9. requires every method to remain outside the primary denominator.

## 4. Exact case results

| Order | Case arm | Observer | `M0 / M1 / M2 / M3` | Declared-witness localization |
|---:|---|---|---|---|
| 1 | `dev-v1-valid-o0` | `O0_EXIT_CODE` | `accept / accept / accept / accept` | `supported` |
| 2 | `dev-v1-valid-o1` | `O1_TYPED_RECEIPT` | `accept / accept / accept / accept` | `supported` |
| 3 | `dev-v1-nondiscriminating-o0` | `O0_EXIT_CODE` | `accept / reject / reject / reject` | `not_applicable` |
| 4 | `dev-v1-nondiscriminating-o1` | `O1_TYPED_RECEIPT` | `accept / reject / reject / reject` | `not_applicable` |
| 5 | `dev-v1-candidate-regression-o0` | `O0_EXIT_CODE` | `accept / accept / reject / reject` | `not_applicable` |
| 6 | `dev-v1-candidate-regression-o1` | `O1_TYPED_RECEIPT` | `accept / accept / reject / reject` | `not_applicable` |
| 7 | `dev-v1-import-error-o0` | `O0_EXIT_CODE` | `accept / accept / accept / accept` | `indeterminate` |
| 8 | `dev-v1-import-error-o1` | `O1_TYPED_RECEIPT` | `accept / indeterminate / indeterminate / indeterminate` | `indeterminate` |
| 9 | `dev-v1-unrelated-assertion-o0` | `O0_EXIT_CODE` | `accept / accept / accept / accept` | `unsupported` |
| 10 | `dev-v1-unrelated-assertion-o1` | `O1_TYPED_RECEIPT` | `accept / accept / accept / accept` | `unsupported` |

Every stored method decision is concordant with the sealed plan.

Every method record contains:

```text
primary_denominator_eligible = false
```

## 5. Controlled contrasts

The machine-derived analysis retained full case tables and produced no headline score.

| Contrast | Observed evidence | Status |
|---|---|---|
| Candidate-test discrimination | Non-discriminating family: `M0 accept -> M1 reject` under both observers | `observed_as_expected` |
| Original-test preservation | Candidate-regression family: `M1 accept -> M2 reject` under both observers | `observed_as_expected` |
| Typed import error | Import family: `M1 accept` under O0, `M1 indeterminate` under O1 | `observed_as_expected` |
| Declared-witness mismatch | Unrelated-assertion family: `M3 accept`, localization `unsupported` under both observers | `observed_as_expected` |
| Valid positive control | Valid family: every method accepts and localization is supported under both observers | `observed_as_expected` |

The index fixes:

```text
headline_score                = null
ecological_inference_allowed  = false
retain_case_tables             = true
```

## 6. What the result establishes

Within the exact five-family owned-synthetic population, the result establishes that:

- the complete descriptor-to-result artifact chain can execute without manual repair;
- exact state-set baselines remain distinguishable;
- typed outcome evidence preserves the import-error case as incomplete rather than semantic failure;
- declared logical-test localization detects the broad-suite/unrelated-assertion mismatch;
- the valid positive control remains supported under both observers;
- the retained archive can reconstruct and reverify the complete bundle;
- repeated clean executions preserve the semantic index digest;
- all inspected evidence remains development-only and denominator-ineligible.

## 7. What the result does not establish

The result does not establish:

- prevalence of false assurance in real coding-agent patches;
- accuracy, precision, recall, superiority, or operational utility on an ecological corpus;
- that `M3_FOUR_STATE` adds value beyond `M2_F2P_P2P` in real repositories;
- test-oracle adequacy or semantic relevance beyond the declared selector transition;
- mutation adequacy, coverage adequacy, or resistance to adversarial test design;
- native runtime costs for `M0`, `M1`, or `M2`;
- measured human review burden;
- complete environment reproducibility;
- containment or safe execution of untrusted code;
- producer authentication, immutable timestamping, or non-repudiation;
- protocol freeze or holdout readiness;
- independent reproduction or Gate 0 completion;
- production readiness, scientific novelty, or award-level significance.

## 8. Cost boundary

The archive retains per-case wall-clock, CPU, state, selector, command, artifact-count, and public-byte fields for the exact runner environment.

These values are development diagnostics only:

- the ten arms are not independent samples;
- full-matrix projection cost is not native `M0`, `M1`, or `M2` cost;
- human review time is explicitly `unmeasured` with a missingness reason;
- no population-level cost inference is permitted.

## 9. Safety and transport record

The runner used only fixed project-owned synthetic repositories in disposable GitHub-hosted directories. Raw stdout, stderr, tracebacks, absolute paths, usernames, credentials, and environment values are excluded from the archive.

Two temporary transport mechanisms were separately reviewed:

1. one-day `actions/upload-artifact` transport under `contents: read`;
2. one exact branch-scoped archive write under `contents: write`.

Both capabilities were removed before final PR validation. They are historical process evidence, not product features or continuing permissions.

Review records:

```text
research/DW-001/CANONICAL_ARCHIVE_TRANSPORT_REVIEW.md
research/DW-001/CANONICAL_ARCHIVE_BRANCH_WRITE_REVIEW.md
```

## 10. Reproduction

From an exact checkout containing the archive:

```bash
python -m unittest tests.test_dw001_pilot_committed_archive -v
python scripts/smoke_dw001_development_pilot.py
```

The smoke:

- verifies the committed archive;
- executes a fresh ten-arm development pilot;
- requires the fresh semantic digest to equal the committed digest;
- constructs a fresh archive;
- verifies archive round-trip reconstruction.

This is a reproducibility check by the same repository and workflow. It does not satisfy the independent-operator requirement in issue #4.

## 11. Decision

The fixed synthetic **mechanism pilot is complete**.

The broader empirical program is not complete. The next research step must move from hand-designed mechanism probes to a preregistered sampling, review, measurement, and uncertainty design for an authorized development corpus, followed only later by a committed holdout.

No additional assurance layer should be treated as a substitute for that evidence gap.
