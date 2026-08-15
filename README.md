# DeltaWitness

[![CI](https://github.com/rdemb/delta-witness/actions/workflows/ci.yml/badge.svg)](https://github.com/rdemb/delta-witness/actions/workflows/ci.yml)

**Counterfactual verification for AI-generated code changes.**

DeltaWitness is an open research prototype that checks whether a candidate patch produced the behavioral change claimed by its tests. It does not trust a green final-state run by itself.

**Current status:** pre-alpha research software (`v0.0.1`). It is not a formal proof system, a security certification product, or a sandbox for untrusted code.

## The problem

A coding agent can modify production code, modify tests, run the resulting suite, and report success. That workflow can become self-confirming. A final test run does not establish that:

- the candidate test would have detected the original defect;
- the implementation change caused the observed improvement;
- the original suite still passes against the candidate implementation;
- the agent did not weaken, skip, or replace the relevant oracle.

DeltaWitness moves the first layer of this decision out of the agent's narrative and into deterministic Git replay.

## The four-state witness

Given a base commit and a descendant candidate commit, DeltaWitness separates changed test paths from the remaining candidate tree and constructs four exact Git states:

| | Base tests | Candidate tests |
|---|---:|---:|
| **Base implementation-side tree** | `base_base` | `base_candidate` |
| **Candidate implementation-side tree** | `candidate_base` | `candidate_candidate` |

For a conventional regression fix, the expected pattern is usually:

```text
base_base            pass
base_candidate       fail
candidate_base       pass
candidate_candidate  pass
```

This pattern is consistent with the candidate witness exposing the old behavior, the candidate implementation satisfying that witness, and the original suite remaining valid against the candidate implementation. The interpretation is only as strong as the declared command and its outcome classification.

By default, exit code `0` is classified as `pass`, exit code `1` as `fail`, and every other result as an execution error. Projects with different test-runner semantics must declare `pass_exit_codes` and `fail_exit_codes`. A nonzero exit is not automatically treated as evidence of the intended regression.

DeltaWitness calls the resulting artifact a **change witness**. It is bounded evidence about declared commits, paths, commands, and observations. It is not proof of full correctness, security, completeness, or causal necessity.

## What is technically recorded

Each run records:

- immutable base and candidate commit IDs;
- exact tree IDs for all four states;
- deterministic synthetic commit IDs for the two hybrid states;
- the specification digest and explicit path classification;
- every expected and observed state result;
- exit codes, timeout status, durations, and output digests;
- a stable witness digest over the semantic outcome;
- a report digest over the complete JSON document.

The hybrid states are represented as synthetic commits rather than dirty worktrees. Commands that inspect `HEAD` therefore see the recorded commit identity. Git subprocesses use a reduced environment that rejects process-level repository redirection and replacement-object overrides. Repository-local attributes and filters remain a documented limitation of the current materialization layer.

Raw command output is excluded by default. Local absolute repository and specification paths are not written to the report. The command array, claim descriptions, environment-variable names, and output digests are recorded; treat a report as review-required before publication.

## Quick start

Requirements:

- Python 3.11 or later;
- Git;
- a clean repository;
- a base commit that is an ancestor of the candidate commit.

Install from a local checkout:

```bash
python -m pip install --no-deps -e .
deltawitness doctor
```

Run the self-contained demo:

```bash
./scripts/demo.sh
```

Verify another repository:

```bash
deltawitness verify \
  --repo /path/to/repository \
  --base origin/main \
  --head HEAD \
  --spec deltawitness.toml
```

By default, the report is written inside the repository's private Git metadata directory so that a second run does not dirty the working tree. The command prints the exact location. Verify its integrity with:

```bash
deltawitness verify-report "$(git rev-parse --git-path deltawitness/report.json)"
```

Use `--output /reviewed/path/report.json` when a report must be exported deliberately.

## Specification

```toml
[paths]
code = ["src/**", "pyproject.toml"]
tests = ["tests/**"]
documentation = ["README.md", "docs/**"]

# Host environment variables are not inherited unless named here.
[execution]
pass_env = []

[[claim]]
id = "security-regression"
description = "The candidate witness must expose the defect before the patch and pass after it."
command = ["python", "-m", "pytest", "-q", "tests"]
timeout_seconds = 300

# Defaults are [0] and [1]. Other exit codes make the run incomplete.
pass_exit_codes = [0]
fail_exit_codes = [1]

[claim.expect]
base_base = "pass"
base_candidate = "fail"
candidate_base = "pass"
candidate_candidate = "pass"
```

Every changed path must match exactly one declared category. Every matrix expectation must be explicit. Pass and fail exit-code sets must be disjoint. Timeouts and unclassified return codes produce `INCOMPLETE`, even when an expectation is `any`. Ambiguous configuration fails closed.

DeltaWitness does not know whether a test runner's failure came from the intended assertion, test collection, dependency resolution, or another cause when those conditions share an exit code. For high-assurance use, call a project-specific wrapper that emits distinct, documented exit codes or emits a separately validated machine-readable result.

CLI exit codes:

- `0`: every declared expectation matched within scope;
- `1`: the harness completed, but at least one claim was unsupported;
- `2`: configuration, Git, execution, or report error.

## Safety model

DeltaWitness executes commands from the specification without a shell, with a sanitized environment and isolated temporary home and cache directories. It still runs with the current user's filesystem permissions and does not isolate the network.

Use it only with code and commands you trust. Never place secrets directly in a command array. Values passed through `execution.pass_env` are not written to the report, but a command can still print or otherwise expose them. Output digests can fingerprint low-entropy sensitive values and are not a safe substitute for review.

For untrusted repositories, use a disposable virtual machine or a separately secured container without production credentials. Read [THREAT_MODEL.md](THREAT_MODEL.md) before use.

## Research boundary

Fail-to-pass validation is established prior art, including TDD-Bench Verified. Test and code co-evolution is also an active research area. DeltaWitness does not currently claim scientific novelty.

The provisional contribution under evaluation is narrower: a Git-native four-state replay for post-change verification, exact hybrid-state identities, strict claim boundaries, sanitized execution, and a portable integrity-verifiable witness artifact. The prior-art boundary and falsification criteria are maintained in [Research Note 000](docs/RESEARCH_NOTE_000.md).

## Current limitations

The first prototype intentionally supports a narrow case:

- test changes must be separable by repository path;
- candidate test changes are required;
- changed submodule entries are rejected;
- dependency, toolchain, generated-file, unchanged-submodule, and cross-repository state are not yet modeled or cryptographically bound;
- repository-local Git attributes, filters, checkout transformations, and the shared object database can still affect the materialized worktrees;
- commands can still access the host filesystem and network;
- nondeterministic tests are observed only once;
- a declared test-failure exit code can still represent collection, import, setup, or infrastructure failure unless a project-specific wrapper distinguishes them;
- weak assertions, excessive mocking, and semantic overfitting are not yet detected;
- synthetic hybrid commits are local Git objects and are not pushed automatically;
- a matching matrix can still support a misleading or incomplete claim.

## Project principles

1. Deterministic checks precede model judgment.
2. Ambiguous trust boundaries fail closed.
3. Public claims remain narrower than the evidence.
4. Negative results and failed hypotheses are publishable outcomes.
5. Reproduction matters more than branding.
6. Material AI assistance is disclosed, while responsibility remains human.

## Public research boundary

The repository may contain safe test fixtures, protocols, code, released results, and reproducible evidence. Unpatched vulnerabilities, credentials, private infrastructure details, customer data, access configuration, and operational exploit material remain private or under coordinated disclosure. See [PUBLICATION_POLICY.md](docs/PUBLICATION_POLICY.md).

## Development

```bash
python -m unittest discover -s tests -v
./scripts/demo.sh
python scripts/validate_public_tree.py
```

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [AI_USAGE.md](AI_USAGE.md).

## Author and license

DeltaWitness is an independent open research project created by **Rafal Dembski**. It is licensed under Apache License 2.0.
