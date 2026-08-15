# DeltaWitness

[![CI](https://github.com/rdemb/delta-witness/actions/workflows/ci.yml/badge.svg)](https://github.com/rdemb/delta-witness/actions/workflows/ci.yml)

**Counterfactual verification for AI-generated code changes.**

DeltaWitness is an open research prototype that checks whether a candidate patch produced the behavioral change claimed by its tests. It does not trust a green final-state run by itself.

**Current status:** pre-alpha research software (`v0.0.2`). It is not a formal proof system, a security certification product, or a sandbox for untrusted code.

## The problem

A coding agent can modify production code, modify tests, run the resulting suite, and report success. That workflow can become self-confirming. A final test run does not establish that:

- the candidate test would have detected the original defect;
- the implementation change caused the observed improvement;
- the original suite still passes against the candidate implementation;
- the agent did not weaken, skip, or replace the relevant oracle;
- a nonzero test-runner exit came from an assertion rather than collection, import, setup, or infrastructure failure.

DeltaWitness moves the first layer of this decision out of the agent's narrative and into deterministic Git replay and typed execution evidence.

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

DeltaWitness calls the resulting artifact a **change witness**. It is bounded evidence about declared commits, paths, commands, and observations. It is not proof of full correctness, security, completeness, or causal necessity.

## Two observer modes

### Exit-code observer

`exit-code-v1` is the backward-compatible default. Exit code `0` is classified as `pass`, exit code `1` as `fail`, and every other result as an execution error unless the claim declares different disjoint code sets.

A raw exit code cannot establish why the runner failed. This mode is appropriate only when the command has documented, unambiguous exit semantics or when the limitation is acceptable.

### Typed outcome receipt

`outcome-receipt-v1` requires a cooperating test adapter to write a strict, bounded JSON receipt bound to the exact claim, command, specification, matrix state, tree, and commit.

Only two dual-channel combinations become normal matrix observations:

```text
receipt passed       + configured pass exit code -> pass
receipt test_failure + configured fail exit code -> fail
```

Import errors, discovery failures, no tests, all-skipped execution, unexpected successes, malformed or missing receipts, binding mismatches, and receipt/exit contradictions become `error`, making the report incomplete rather than creating a false regression witness.

The first built-in producer supports Python's standard-library `unittest`:

```bash
deltawitness-unittest --start-directory tests
```

Read the complete protocol and its non-claims in [Outcome Receipt Protocol v1](docs/OUTCOME_RECEIPT_V1.md).

## What is technically recorded

Each run records:

- immutable base and candidate commit IDs;
- exact tree IDs for all four states;
- deterministic synthetic commit IDs for the two hybrid states;
- the specification digest and explicit path classification;
- every expected and observed state result;
- exit codes, timeout status, durations, and output digests;
- observer identifier and deterministic invocation binding;
- typed receipt outcome, producer, aggregate counts, digest, and stable observer error code when enabled;
- a stable witness digest over the semantic outcome;
- a report digest over the complete JSON document.

The hybrid states are represented as synthetic commits rather than dirty worktrees. Commands that inspect `HEAD` therefore see the recorded commit identity. Git subprocesses use a reduced environment that rejects process-level repository redirection and replacement-object overrides. Changed submodule and changed symbolic-link entries are rejected before hybrid-state materialization. Repository-local attributes and filters remain a documented limitation of the current materialization layer.

Raw command output is excluded by default. Local absolute repository and specification paths are not written to the report. The command array, claim descriptions, environment-variable names, output digests, and receipt metadata are recorded; treat a report as review-required before publication.

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

A receipt-aware `unittest` claim:

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
observer = "outcome-receipt-v1"
command = ["deltawitness-unittest", "--start-directory", "tests"]
timeout_seconds = 300

# The receipt and process exit must agree.
pass_exit_codes = [0]
fail_exit_codes = [1]

[claim.expect]
base_base = "pass"
base_candidate = "fail"
candidate_base = "pass"
candidate_candidate = "pass"
```

Every changed path must match exactly one declared category. Every matrix expectation must be explicit. Pass and fail exit-code sets must be disjoint. Timeouts, unclassified return codes, invalid receipts, and inconclusive receipt outcomes produce `INCOMPLETE`, even when an expectation is `any`. Ambiguous configuration fails closed.

Projects that do not use a receipt adapter may omit `observer`; `exit-code-v1` remains the default. A project-specific adapter should derive results from a structured framework API rather than terminal text and must follow the protocol's privacy and consistency rules.

CLI exit codes:

- `0`: every declared expectation matched within scope;
- `1`: the harness completed, but at least one claim was unsupported;
- `2`: configuration, Git, execution, observer, or report error.

## Safety model

DeltaWitness executes commands from the specification without a shell, with a sanitized environment and isolated temporary home and cache directories. It still runs with the current user's filesystem permissions and does not isolate the network.

Use it only with code and commands you trust. Never place secrets directly in a command array. Values passed through `execution.pass_env` are not written to the report, but a command can still print or otherwise expose them. Output digests can fingerprint low-entropy sensitive values and are not a safe substitute for review.

A receipt binding prevents accidental cross-state reuse; it does not authenticate the producer. A malicious command can read its binding and forge a syntactically valid receipt. Producer signing, environment provenance, and containment remain separate future layers.

For untrusted repositories, use a disposable virtual machine or a separately secured container without production credentials. Read [THREAT_MODEL.md](THREAT_MODEL.md) before use.

## Research boundary

Fail-to-pass validation is established prior art, including TDD-Bench Verified. Test and code co-evolution, oracle quality, mutation testing, patch coverage, and execution provenance are active research areas. DeltaWitness does not currently claim scientific novelty.

The provisional contribution under evaluation is narrower: a Git-native four-state replay for post-change verification, exact hybrid-state identities, strict claim boundaries, typed and invocation-bound test outcomes, sanitized execution, and a portable integrity-verifiable witness artifact. The prior-art boundary and falsification criteria are maintained in [Research Note 000](docs/RESEARCH_NOTE_000.md).

## Current limitations

The prototype intentionally supports a narrow case:

- test changes must be separable by repository path;
- candidate test changes are required;
- changed submodule and changed symbolic-link entries are rejected;
- dependency, toolchain, generated-file, unchanged-submodule, unchanged-symbolic-link, and cross-repository state are not yet modeled or cryptographically bound;
- repository-local Git attributes, filters, checkout transformations, and the shared object database can still affect the materialized worktrees;
- commands can still access the host filesystem and network;
- nondeterministic tests are observed only once;
- `exit-code-v1` can still confuse assertion failure with collection, import, setup, teardown, or infrastructure failure;
- `outcome-receipt-v1` requires a cooperating producer and does not authenticate it;
- the built-in typed producer currently supports only standard-library `unittest` discovery;
- typed outcomes do not establish oracle relevance or strength;
- weak assertions, excessive mocking, semantic overfitting, and patch minimality are not yet detected;
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
