# Outcome Receipt Protocol v1

## Status

This document specifies the experimental `outcome-receipt-v1` observer introduced in DeltaWitness `0.0.2`.

The protocol is designed to distinguish a test assertion failure from execution states that share the same process exit code, such as discovery, import, setup, teardown, dependency, or producer errors. It is a local machine-readable observation protocol. It is **not** a signed attestation, a remote-verification protocol, or proof that a test is relevant to a claim.

## Motivation

A raw process result is often too coarse for counterfactual verification.

```text
exit code 1
```

may mean:

- a relevant assertion detected the old defect;
- test collection failed;
- an import was missing;
- setup raised an exception;
- the test runner failed internally;
- a wrapper returned an undocumented status.

Only the first case is a candidate regression witness. DeltaWitness therefore supports a cooperating producer that reports a typed semantic outcome in addition to its process exit code.

## Claim configuration

A claim opts into the protocol explicitly:

```toml
[[claim]]
id = "authorization-regression"
observer = "outcome-receipt-v1"
command = [
  "python",
  "-m",
  "deltawitness.unittest_probe",
  "--start-directory",
  "tests"
]
pass_exit_codes = [0]
fail_exit_codes = [1]
```

The default observer remains `exit-code-v1` for backward compatibility.

## Invocation binding

Before executing a claim in one matrix state, DeltaWitness computes a deterministic SHA-256 binding over canonical JSON containing:

- protocol identifier `deltawitness.invocation.v1`;
- claim identifier;
- matrix state;
- exact state tree ID;
- exact state commit ID;
- observer identifier;
- declared command array;
- specification SHA-256.

The child process receives:

```text
DELTAWITNESS_RECEIPT_PATH
DELTAWITNESS_RECEIPT_BINDING
```

The receipt must echo the exact binding. A mismatch makes the observation incomplete. The binding prevents accidental reuse of a receipt from another claim, state, command, specification, tree, or commit. It does not stop a malicious process that can read the environment from forging a matching receipt.

## Receipt document

The receipt is strict UTF-8 JSON with exactly five top-level fields:

```json
{
  "schema_version": "deltawitness.outcome-receipt.v1",
  "binding": "64-lowercase-hex-characters",
  "producer": {
    "name": "deltawitness-unittest",
    "version": "0.0.2"
  },
  "outcome": "test_failure",
  "counts": {
    "tests_run": 2,
    "passed": 1,
    "failures": 1,
    "errors": 0,
    "skipped": 0,
    "expected_failures": 0,
    "unexpected_successes": 0
  }
}
```

Unknown fields, missing fields, duplicate JSON keys, non-integer counts, Boolean counts, negative counts, inconsistent totals, unsupported schemas, and semantically inconsistent outcomes are rejected.

## Count invariant

The category counts must satisfy:

```text
tests_run
=
passed
+ failures
+ errors
+ skipped
+ expected_failures
+ unexpected_successes
```

The built-in `unittest` producer classifies one final category per logical test object. Multiple failing subtests therefore count as one logical test failure rather than making category totals exceed the number of logical tests.

## Outcome semantics

| Outcome | Required semantic condition | DeltaWitness matrix observation |
|---|---|---|
| `passed` | At least one logical test passed; no failure, error, or unexpected success | `pass` only when the process exit code is in `pass_exit_codes` |
| `test_failure` | At least one logical assertion failure; no test error or unexpected success | `fail` only when the process exit code is in `fail_exit_codes` |
| `test_error` | At least one error-class outcome | `error` / incomplete |
| `no_tests` | No logical test outcome was observed | `error` / incomplete |
| `no_effective_tests` | Tests existed, but none passed or failed because all were skipped or expected failures | `error` / incomplete |
| `unexpected_success` | At least one expected failure unexpectedly passed | `error` / incomplete |
| `producer_error` | The producer could not construct a reliable result | `error` / incomplete |

Error-class outcomes take precedence over assertion failures. A mixed run containing both a failure and an error is `test_error`, not a valid regression witness.

## Dual-channel consistency

The process exit code and the receipt must agree:

```text
receipt passed       + declared pass exit code -> pass
receipt test_failure + declared fail exit code -> fail
all other combinations                       -> error
```

This prevents a receipt that says `passed` while the process exits with a configured failure code, or a receipt that says `test_failure` while the process exits successfully, from being accepted as evidence.

## File handling

The current implementation applies the following controls:

- one private receipt path per process invocation;
- maximum encoded size of 65,536 bytes;
- regular-file requirement;
- symbolic-link rejection;
- `O_NOFOLLOW` where the operating system provides it;
- strict UTF-8 decoding;
- duplicate-key rejection;
- atomic writes by the built-in producer;
- owner-only permissions on POSIX;
- canonical JSON SHA-256 stored in the final report.

A missing or invalid receipt is represented by a stable error code rather than by a local path or raw parser exception.

## Witness binding

Schema `0.3` reports bind the following receipt fields into `witness_sha256`:

- observer identifier;
- invocation binding;
- receipt SHA-256;
- typed outcome;
- producer name and version;
- aggregate counts;
- stable observation error code.

Changing any bound semantic field invalidates the witness digest. The report digest additionally covers the entire report document.

Both digests are unkeyed. A party able to rewrite a report can recompute them. Producer authentication, DSSE, in-toto statements, Sigstore signing, and SLSA-aligned provenance remain separate future work.

## Privacy boundary

A receipt must not contain:

- raw stdout or stderr;
- exception text;
- source code;
- local absolute paths;
- test identifiers;
- credentials;
- environment values;
- customer or repository-private data.

The protocol intentionally records aggregate counts and producer identity only. The normal DeltaWitness report still contains the declared command array and output digests, so commands must never embed secrets and every exported report remains review-required.

## Built-in unittest producer

The reference producer is available as:

```bash
deltawitness-unittest --start-directory tests
```

or:

```bash
python -m deltawitness.unittest_probe --start-directory tests
```

It uses Python's standard-library discovery and records one conservative final category per logical test object. Its output stream is buffered in memory and is not copied into the receipt.

The producer is designed for cooperating, trusted-code research runs. A repository may still shadow modules, alter interpreter behavior, access the host, or forge a receipt. Run unknown code only inside a separately secured disposable environment.

## Adapter requirements

A future adapter for another test framework should:

1. derive outcomes from a structured framework API rather than terminal text;
2. distinguish assertion or expectation failure from collection, setup, teardown, and infrastructure errors;
3. emit exactly one valid receipt after execution;
4. write atomically to the supplied absolute path;
5. echo the exact invocation binding;
6. exclude raw failure content and local identifiers;
7. return a documented pass or fail exit code only for `passed` or `test_failure`;
8. return an error-class exit code for every inconclusive outcome;
9. include adversarial fixtures for missing, malformed, stale, mismatched, and contradictory receipts.

## Non-claims

A valid receipt does not establish that:

- the producer is honest or uncompromised;
- the failing test is relevant to the requested behavior;
- the oracle is strong;
- the patch caused the result;
- the candidate is correct, secure, minimal, or complete;
- the execution environment is reproducible or contained.

Those questions require additional layers: four-state replay, oracle analysis, mutation testing, causal ablation, environment provenance, containment, signed attestations, and independent reproduction.
