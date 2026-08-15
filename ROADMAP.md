# Roadmap

The roadmap is gated by evidence rather than dates. A checked implementation item means that the mechanism and synthetic regression coverage exist; it does not imply independent validation, scientific novelty, production readiness, or empirical usefulness.

## Gate 0: Reproducible core

- [x] Four-state Git matrix
- [x] NUL-safe changed-path parsing
- [x] Reduced Git subprocess environment and replacement-object rejection
- [x] Unsafe cross-platform changed-path rejection
- [x] Explicit and exclusive path classification
- [x] Base-to-candidate ancestry check
- [x] Changed-submodule rejection
- [x] Changed symbolic-link rejection
- [x] Exact tree identities for every state
- [x] Deterministic synthetic commits for hybrid states
- [x] Per-claim state restoration
- [x] Sanitized command environment
- [x] Explicit pass/fail exit-code classification
- [x] Incomplete-run handling for timeouts and unknown return codes
- [x] Deterministic claim/state invocation bindings
- [x] Strict, bounded typed outcome receipt protocol
- [x] Dual-channel receipt and exit-code consistency checks
- [x] Built-in unittest producer distinguishing assertion failure from error states
- [x] Raw-output exclusion by default
- [x] Stable witness digest and exact report digest
- [x] Typed observer evidence bound into the witness digest
- [x] Matrix and influence report-integrity verification
- [x] Self-contained matrix and influence demonstration
- [ ] Independent reproduction by an external operator
- [ ] Independent receipt adapter implemented outside this repository

## Gate 1: Test-integrity analysis

- [ ] Detect empty and assertion-free test deltas
- [ ] Detect skipped, disabled, and weakened assertions
- [ ] Measure patch coverage around the claimed behavior
- [ ] Measure mutation score around the claimed behavior
- [ ] Identify excessive mocking around the claimed boundary
- [ ] Repeat flaky tests and report uncertainty
- [ ] Compare typed receipts against raw exit-code observation
- [ ] Compare the four-state matrix against two-state fail-to-pass validation

## Gate 2: Bounded intervention analysis

- [x] Exact exhaustive file-path coalitions up to eight changed code paths
- [x] Two test worlds for every coalition
- [x] Complete / unsupported / indeterminate coalition semantics
- [x] Canonical endpoint consistency checks
- [x] Exact Git tree and synthetic commit identities per intervention
- [x] Every inclusion-minimal witness-sufficient coalition
- [x] Global and full-context path necessity
- [x] Standalone sufficiency
- [x] Positive and negative marginal swing counts
- [x] Exact rational Shapley allocation
- [x] Exact normalized Banzhaf influence
- [x] Exact pairwise Banzhaf interaction
- [x] No-metrics policy for incomplete or inconsistent tables
- [x] Integrity-verifiable influence report
- [ ] Hunk-level intervention units
- [ ] AST- or semantic-unit intervention research
- [ ] Selective hunk ablation and minimal causal subset search
- [ ] Negative controls and placebo patches
- [ ] Exploit-before and exploit-after security witnesses
- [ ] Multiple claims with path-specific execution boundaries
- [ ] Repeated stochastic execution and attribution stability
- [ ] Explicit approximate mode with sampling and uncertainty for larger patches
- [ ] Quantify incremental findings over leave-one-out and delta debugging
- [ ] Quantify false assurance, over-refusal, and applicability

## Gate 3: Reproducible containment

- [ ] Container-backed runner
- [ ] Locked toolchain and dependency manifests
- [ ] Independent post-checkout tree verification
- [ ] Network and filesystem policy controls
- [ ] CPU, memory, process, storage, and time limits
- [ ] Background-process and external-side-effect controls
- [ ] Environment capture without credential leakage
- [ ] Safe handling of language package managers
- [ ] Trusted adapter invocation that cannot be shadowed by repository modules

## Gate 4: Verifiable attestations

- [ ] DSSE or in-toto-compatible statement format
- [ ] Sigstore signing
- [ ] SLSA-aligned provenance
- [ ] Producer identity and environment binding
- [ ] GitHub Action with a required status check
- [ ] Policy evaluation independent of report generation
- [ ] External verifier that does not depend on the report producer

## Gate 5: Empirical evaluation

- [ ] Reproducible systematic literature-review protocol
- [ ] Development corpus of synthetic and curated public patches
- [ ] Agent-authored patch sampling protocol
- [ ] Frozen protocol and held-out evaluation set
- [ ] Baselines against final-state CI, two-state fail-to-pass, raw exit codes, leave-one-out, delta debugging, mutation testing, and independent semantic verification
- [ ] Applicability and invalid-intervention analysis
- [ ] Confidence intervals and hierarchical analysis where appropriate
- [ ] Independent reproduction and external technical review
- [ ] Public negative-result and correction policy exercised in practice
- [ ] Publication-quality research report

## Gate 6: Ecosystem utility

- [ ] Stable machine-readable schemas with compatibility policy
- [ ] Pytest adapter derived from structured framework APIs
- [ ] Adapters for at least one non-Python ecosystem
- [ ] GitHub Action integration
- [ ] Reusable public fixture corpus
- [ ] External contributors maintaining adapters or scenarios
- [ ] Documented use in a repository not controlled by the original maintainer
- [ ] Performance profile and operational guidance
