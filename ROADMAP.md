# Roadmap

The roadmap is gated by evidence rather than dates.

## Gate 0: Reproducible core

- [x] Four-state Git matrix
- [x] NUL-safe changed-path parsing
- [x] Reduced Git subprocess environment and replacement-object rejection
- [x] Unsafe cross-platform changed-path rejection
- [x] Explicit and exclusive path classification
- [x] Base-to-candidate ancestry check
- [x] Exact tree identities for every state
- [x] Deterministic synthetic commits for hybrid states
- [x] Per-claim state restoration
- [x] Sanitized command environment
- [x] Explicit pass/fail exit-code classification
- [x] Incomplete-run handling for timeouts and unknown return codes
- [x] Raw-output exclusion by default
- [x] Stable witness digest and exact report digest
- [x] Report-integrity verification command
- [x] Self-contained integration demo
- [ ] Independent reproduction by an external operator

## Gate 1: Test-integrity analysis

- [ ] Detect empty and assertion-free test deltas
- [ ] Detect skipped, disabled, and weakened assertions
- [ ] Measure mutation score around the claimed behavior
- [ ] Identify excessive mocking around the claimed boundary
- [ ] Repeat flaky tests and report uncertainty
- [ ] Compare against two-state fail-to-pass validation

## Gate 2: Causal patch analysis

- [ ] Selective hunk ablation
- [ ] Minimal causal subset search
- [ ] Negative controls and placebo patches
- [ ] Exploit-before and exploit-after security witnesses
- [ ] Multiple claims with path-specific commands
- [ ] Quantify false assurance and over-refusal

## Gate 3: Reproducible containment

- [ ] Container-backed runner
- [ ] Locked toolchain and dependency manifests
- [ ] Network and filesystem policy controls
- [ ] CPU, memory, process, and time limits
- [ ] Environment capture without credential leakage
- [ ] Safe handling of language package managers

## Gate 4: Verifiable attestations

- [ ] DSSE or in-toto-compatible statement format
- [ ] Sigstore signing
- [ ] SLSA-aligned provenance
- [ ] GitHub Action with a required status check
- [ ] Policy evaluation independent of report generation

## Gate 5: Empirical evaluation

- [ ] Reproducible literature-review protocol
- [ ] Public corpus of real and adversarial agent-authored patches
- [ ] Frozen protocol and held-out evaluation set
- [ ] Baselines against final-state CI, fail-to-pass validation, and mutation testing
- [ ] Confidence intervals and hierarchical analysis where appropriate
- [ ] Independent reproduction and external technical review
- [ ] Publication-quality research report
