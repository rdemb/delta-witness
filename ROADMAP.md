# Roadmap

The roadmap is gated by evidence rather than dates.

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
- [x] Report-integrity verification command
- [x] Self-contained integration demo
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
- [ ] Trusted adapter invocation that cannot be shadowed by repository modules

## Gate 4: Verifiable attestations

- [ ] DSSE or in-toto-compatible statement format
- [ ] Sigstore signing
- [ ] SLSA-aligned provenance
- [ ] Producer identity and environment binding
- [ ] GitHub Action with a required status check
- [ ] Policy evaluation independent of report generation

## Gate 5: Empirical evaluation

- [ ] Reproducible literature-review protocol
- [ ] Public corpus of real and adversarial agent-authored patches
- [ ] Frozen protocol and held-out evaluation set
- [ ] Baselines against final-state CI, fail-to-pass validation, raw exit codes, and mutation testing
- [ ] Confidence intervals and hierarchical analysis where appropriate
- [ ] Independent reproduction and external technical review
- [ ] Publication-quality research report
