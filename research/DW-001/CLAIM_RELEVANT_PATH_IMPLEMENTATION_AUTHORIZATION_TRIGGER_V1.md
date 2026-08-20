# DW-001 Claim-Relevant Path Executor Implementation Authorization v1

## Decision

Executor **implementation** is authorized only if this commit's parent contains a valid `CLAIM_RELEVANT_PATH_EXECUTION_PROTOCOL_GATE_V1.md` produced after terminal green exact-head protocol CI.

The authorization is deliberately narrower than result execution:

```text
executor implementation: AUTHORIZED
static manifest / schema / verifier tests: AUTHORIZED
candidate execution: NOT AUTHORIZED
selector execution: NOT AUTHORIZED
Coverage.py measurement: NOT AUTHORIZED
fault execution: NOT AUTHORIZED
influence observation: NOT AUTHORIZED
synthetic target execution: NOT AUTHORIZED
result aggregation: NOT AUTHORIZED
publication: BLOCKED
```

## Authorized implementation scope

The next implementation commit may add only:

- a shell-free spawned-worker interface;
- exact owned-byte and command-identity preflight checks;
- independent typed dimensions for execution, evidence availability, path conformance, and aggregate relation;
- bounded timeout and reduced-environment construction;
- canonical receipt, run-index, and result schemas;
- semantic verifiers and regular-file fail-closed loaders;
- static, malformed-input, substitution, timeout-laundering, omission, duplication, and policy-promotion tests;
- documentation and read-only CI that keep runtime invocation disabled.

Tests in this phase may inspect and reconstruct documents and source identities, but may not invoke the candidate, selectors, Coverage.py, generated controls, faults, influence filter, or synthetic target.

## Safety boundary

No external repository, untrusted code, secret, credential-bearing environment, network operation, telemetry, upload, remote execution, package publication, release, deployment, holdout, score, threshold, merge blocker, production claim, scientific-novelty claim, breakthrough claim, agent-effectiveness claim, or award-level claim is authorized.

The worker remains explicitly **not a sandbox**. A later separately reviewed authorization commit and green exact-head CI are required before any result-bearing command may execute.
