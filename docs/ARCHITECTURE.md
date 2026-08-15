# Architecture

## Trust path

DeltaWitness receives a repository, a base ref, a candidate ref, and a TOML specification. The current trust path is intentionally small:

1. resolve both refs to immutable commits;
2. require the base to be an ancestor of the candidate;
3. enumerate changed paths using NUL-delimited Git output with rename heuristics disabled;
4. require every changed path to match exactly one declared category;
5. reject changed Git submodule entries;
6. create four detached worktrees;
7. overlay candidate tests onto the base tree and base tests onto the candidate tree;
8. write exact Git trees for all states;
9. create deterministic synthetic commits for hybrid states;
10. restore each state before each claim to prevent cross-claim contamination;
11. execute the command without a shell and with a sanitized environment;
12. map only explicitly declared return codes to `pass` or `fail`;
13. mark timeouts and unclassified return codes as incomplete execution;
14. record observations, output digests, state identities, and report digests.

## State semantics

`base_base` and `candidate_candidate` are the original commits. `base_candidate` and `candidate_base` are synthetic local commits whose parent is the base commit.

The synthetic commits are deterministic for a given base, candidate, state name, and tree. They are stored as local Git objects without creating refs. DeltaWitness records their IDs in the report.

Files classified as tests are crossed between versions. Code and documentation remain on the implementation side of the matrix. Dependency manifests and build configuration should normally be classified as code because they influence execution.

A command result is classified through each claim's disjoint `pass_exit_codes` and `fail_exit_codes`. The defaults are `[0]` and `[1]`. A timeout or any other exit code makes the report incomplete instead of being silently interpreted as a test failure. This still cannot distinguish multiple failure causes that a test runner reports with the same code; high-assurance integrations should use a wrapper with explicit result semantics.

## Environment handling

The command runner does not inherit the full host environment. It preserves a small set of platform variables, creates isolated temporary home, cache, configuration, and temporary directories, and passes additional variables only when listed in `[execution].pass_env`.

DeltaWitness Git subprocesses also use a reduced environment. External `GIT_DIR`, work-tree, index, object-directory, replacement-object, global-config, and credential-prompt overrides are not inherited. System and global Git configuration are disabled for the harness, replacement objects are disabled, and Git LFS smudging is skipped. Repository-local configuration and repository attributes can still affect checkout behavior and remain part of the residual trust boundary.

This reduces accidental credential exposure but does not create a filesystem or network sandbox. The child process still has the current user's operating-system permissions. Command arguments are recorded in the report and therefore must not contain secrets.

The current environment record is deliberately incomplete. It does not hash the operating-system image, executables found through `PATH`, dependency trees, kernel, locale database, or network responses. Reproducible containment and toolchain binding are roadmap items rather than properties of `v0.0.1`.

## Integrity model

The report carries two digests:

- `witness_sha256` covers stable semantic inputs and exit-status outcomes, excluding volatile durations, timestamps, and output digests;
- `report_sha256` covers the complete JSON document with its own field normalized to `null` during hashing.

`deltawitness verify-report` recalculates both values. Detection is meaningful only when a digest is compared with a separately trusted value. An attacker who can replace the document can recompute its unkeyed hashes. The digests do not authenticate who produced the report. Signing and standard attestations are future work.

Output digests are included in the exact report, but they can fingerprint low-entropy sensitive values. They are evidence fields, not a redaction mechanism.

The default report path is resolved with `git rev-parse --git-path` and stored under private Git metadata. Exporting a report into the working tree requires an explicit `--output` path.
