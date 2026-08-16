# DW-001 Ecological Design Trust Boundary

**Status:** design-only research metadata. No repository or dataset execution capability is added.

## Protected statement

A valid `deltawitness.dw001-ecological-source-universe.v1` document supports only this narrow statement:

> At one exact DeltaWitness `main` revision, the two recorded benchmark implementation repositories, repository-level licenses, provisional artifact classes, known biases, and unresolved design blockers matched the fixed initial source review, while ecological execution, sampling-frame freeze, holdout selection, and holdout inspection remained disabled.

It does not support:

- instance-level license or execution authorization;
- immutable dataset identity;
- sampling validity or representativeness;
- environment feasibility or containment;
- accepted reviewers or ground truth;
- corpus or holdout membership;
- empirical effectiveness or superiority.

## Assets

The contract protects:

- exact reviewed DeltaWitness `main` identity;
- exact reviewed benchmark implementation-repository commits;
- repository-level SPDX license identifiers;
- separation of implementation repository from dataset release;
- separation of repository license from instance authorization;
- complete candidate-source ordering;
- known-bias and blocking-question retention;
- explicit pending/unfrozen/unaccepted states;
- root and per-source execution prohibition;
- absence of holdout selection or inspection;
- canonical source-universe digest and exact reconstruction.

## Adversaries and failure modes

The design considers:

- treating a moving repository branch as an immutable dataset release;
- treating a benchmark implementation license as every underlying project's license;
- treating public availability as authorization to execute historical code;
- deleting blockers after seeing favorable feasibility information;
- changing `pending` to `authorized` and recomputing the digest;
- changing `unfrozen` to `frozen` without a new accepted protocol;
- selecting or inspecting a holdout through an apparently harmless source-table update;
- replacing a repository commit with a newer implementation and retaining the same narrative;
- removing known biases or clustering concerns;
- adding a candidate source without a reviewed source record;
- embedding local paths, credentials, environment values, or sensitive holdout material;
- citing the source-universe artifact as evidence that benchmark instances are representative or safe.

## Invariants

1. The root field set is exact.
2. `status` is `design_only`.
3. `execution_authorized` is `false`.
4. `holdout_selected` is `false`.
5. `holdout_inspected` is `false`.
6. The decision object is reconstructed exactly and keeps all design states pending, unfrozen, or unaccepted.
7. Every source has `execution_authorized = false`.
8. Every source has `dataset_reference_status = unpinned`.
9. Every source has `authorization_review_status = pending`.
10. Every source has `containment_status = unaccepted`.
11. Every source retains non-empty known-bias and blocking-question lists.
12. Source order, repository identity, commit, license, paper reference, artifact scope, and target-population relation are fixed.
13. `universe_sha256` covers the complete canonical document with its own field normalized to `null`.
14. Semantic verification reconstructs the complete canonical document from code; a recomputed digest cannot authorize or freeze the design.
15. No function in this contract downloads datasets, clones repositories, executes code, selects instances, or constructs a holdout.

## Compatibility boundary

The initial source universe is intentionally exact rather than extensible. Adding a source, pinning a dataset, completing authorization, accepting containment, or freezing a sampling frame changes the research meaning and requires:

- a new versioned artifact or explicitly reviewed schema revision;
- red-first semantic tests;
- updated source and literature review;
- updated protocol, threat, privacy, and publication boundaries;
- exact immutable references;
- retained history of the design-only v1 artifact.

Do not mutate the existing artifact in place and describe the change as a routine refresh.

## License and authorization boundary

The recorded `MIT` and `Apache-2.0` identifiers describe only the reviewed benchmark implementation repositories at the pinned commits.

They do not establish:

- license compatibility of every underlying repository;
- redistribution rights for every issue, patch, test, image, or generated artifact;
- authorization to execute historical project code;
- authorization to publish reconstructed vulnerabilities or sensitive outputs;
- permission to create a derived holdout.

Instance-level review remains mandatory.

## Containment boundary

The contract records `containment_required = true` and `containment_status = unaccepted`.

It does not create or approve:

- containers, virtual machines, sandboxes, seccomp profiles, namespaces, or network policies;
- resource limits;
- trusted images or dependency provenance;
- artifact export controls;
- safe execution of malicious test code.

No ecological code may execute under this artifact.

## Privacy boundary

The public artifact may contain:

- public repository names;
- immutable public commit IDs;
- repository-level SPDX identifiers;
- public paper identifiers;
- high-level artifact classes, biases, and blockers.

It must not contain:

- absolute local paths;
- usernames, credentials, tokens, or environment values;
- private repository or endpoint identifiers;
- selected instance or holdout membership;
- raw source, test, issue, or vulnerability content;
- reviewer identities or unpublished legal analysis.

## Residual risks

- Repository and license metadata may later be corrected upstream.
- Public commit identities authenticate neither the authors nor the truth of documentation.
- An unkeyed digest does not authenticate the producer or creation time.
- The two candidate sources may omit a better direct baseline.
- Known-bias lists may be incomplete.
- Benchmark papers and repositories do not resolve instance-level authorization.
- A future reviewer may misinterpret `candidate source` as `accepted corpus` despite explicit wording.

## Claim boundary

A valid source-universe artifact establishes only exact internal correspondence with the initial design review.

It does not establish authorization, safety, representativeness, corpus readiness, ecological execution, a holdout, empirical effectiveness, independent reproduction, production readiness, scientific novelty, or award-level significance.
