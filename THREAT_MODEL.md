# Threat Model

## Protected claim

DeltaWitness attempts to support or reject a narrow statement:

> Under declared commands and exact Git states, the candidate implementation-side tree changes the observed behavior relative to the base tree, while the candidate test-side tree acts as a counterfactual witness.

When a typed observer is enabled, the statement is further bounded by the semantic outcome reported by a cooperating test adapter.

This statement does not establish full program correctness or security.

## Assets

The current design aims to protect:

- the integrity of state construction;
- the binding between state observations and exact Git objects;
- explicit claim boundaries and expectations;
- typed test outcomes from accidental cross-claim or cross-state reuse;
- report integrity after generation;
- host environment variables from accidental inheritance;
- raw command output from accidental publication by default;
- separation between consecutive claims in the same run.

## Adversaries and failure sources

The initial model includes:

- an AI coding agent that unintentionally creates a misleading patch or weak test;
- a contributor that deliberately weakens, skips, or replaces a relevant test;
- stale, unrelated, or incorrectly selected Git refs;
- hostile process-level Git environment overrides and replacement objects;
- unclassified files that influence execution;
- filenames that break line-delimited Git parsing;
- changed submodule entries with unresolved external state;
- changed symbolic-link entries whose targets do not preserve the declared path boundary;
- commands that return success without meaningful assertions;
- test runners that reuse the same nonzero exit code for assertion failures, collection errors, and setup failures;
- missing, stale, malformed, oversized, contradictory, or state-mismatched outcome receipts;
- a malicious command that reads its invocation binding and forges a syntactically valid receipt;
- nondeterministic tests and environment drift;
- one claim contaminating a later claim through generated files;
- command output containing credentials or private data;
- tampering with a generated report;
- sensitive command arguments or low-entropy output being exposed through a report;
- unrecorded toolchain, dependency, or external executable drift;
- malicious repository content or commands executed with the operator's privileges.

## Security invariants in v0.0.2

1. Base and candidate resolve to different immutable commits.
2. The base commit is an ancestor of the candidate commit.
3. The repository is clean before verification.
4. Git subprocesses ignore external repository, index, object-directory, global-config, and replacement-object overrides.
5. Git paths are read through a NUL-delimited interface and unsafe cross-platform paths are rejected.
6. Every changed path is classified exactly once.
7. Changed Git submodule entries are rejected.
8. Changed symbolic-link entries are rejected before hybrid-state materialization.
9. Each matrix state has an exact tree ID and commit ID.
10. Hybrid states use deterministic synthetic commits.
11. Each claim begins from a reset and cleaned state commit.
12. Commands execute without a shell.
13. The full host environment is not inherited.
14. Raw output is excluded unless explicitly requested.
15. Absolute repository and specification paths are excluded from reports.
16. Pass and fail exit-code classes are explicit and disjoint.
17. Timeouts and unclassified return codes mark the run incomplete.
18. Receipt-aware claims receive a deterministic binding over claim, command, specification, state, tree, and commit.
19. Outcome receipts must be bounded regular files with strict UTF-8 JSON, exact fields, duplicate-key rejection, internally consistent counts, and an exact binding match.
20. A typed `pass` or `fail` is accepted only when receipt semantics and configured process exit codes agree.
21. Missing, malformed, inconclusive, or contradictory receipts mark the observation incomplete.
22. Receipt outcome, producer, counts, digest, binding, and observer error code are included in the witness digest.
23. The default report is stored in private Git metadata rather than the working tree.
24. Ambiguous configuration and harness errors stop the run.
25. Report and witness digests are independently verifiable.

## Residual risks

The current runner is not a security sandbox. Repository-local Git configuration, attributes, generic clean/smudge filters, platform checkout rules, unchanged symbolic-link entries, and the shared object database can still influence materialization or execution.

Rejecting changed symbolic-link entries prevents the current prototype from constructing a counterfactual overlay across a modified link boundary. It does not prove that every unchanged path reachable by a command is a regular file, nor does it prevent commands from following links already present in the repository or elsewhere on the host filesystem.

A command can still:

- read or modify files accessible to the current operating-system user;
- access the network;
- start background processes;
- consume excessive resources until external operating-system limits intervene;
- inspect and modify the shared Git object store or refs through the linked worktree;
- exploit the interpreter, Git, kernel, or another local dependency;
- generate nondeterministic or misleading output;
- deliberately forge a receipt that matches the binding exposed in its environment.

The sanitized environment reduces accidental credential exposure. It does not prevent a malicious process from searching the filesystem for credentials.

The report records the declared command, output digests, observer metadata, and aggregate receipt counts. Command arguments must not contain secrets. Output and receipt digests can reveal equality and can be brute-forced when the underlying value has low entropy.

The current witness does not bind the complete operating-system image, executable binaries, dependencies, locale data, kernel, or network responses. Equivalent outcomes across different environments do not establish equivalent execution.

`exit-code-v1` remains a coarse operational observation and cannot establish that the intended assertion failed when the runner reuses one code for collection, import, setup, teardown, or infrastructure errors.

`outcome-receipt-v1` improves semantic precision for a cooperating adapter, but the binding is not secret and the receipt is not signed. It prevents accidental reuse and detects malformed or contradictory results; it does not authenticate the producer, establish adapter integrity, or prove that a failing assertion is relevant to the claimed defect. The built-in `unittest` producer can also be influenced by interpreter import resolution and repository code because it executes inside the tested environment.

The report digests detect modification only when compared with a separately trusted expected digest. Because they are unkeyed, an attacker who can rewrite the report can also recompute both values. They do not authenticate the producer. Signing, standard attestations, and environment provenance remain future work.

## Safe operation

Run DeltaWitness only on repositories and commands you trust. Use an isolated, disposable environment without production credentials for all other code. Review every report before publication, and apply additional scrutiny to reports generated with `--include-output`.

Prefer `outcome-receipt-v1` when a trusted adapter exists, but do not treat a receipt as an authorization decision or an attestation. Validate oracle relevance, patch causality, and environment provenance through separate controls.

Never interpret `SUPPORTED_IN_SCOPE` as proof that a patch is correct, secure, complete, minimal, or free from overfitting.
