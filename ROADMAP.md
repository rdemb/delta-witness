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

Implemented mechanism, design, and owned-synthetic result controls:

- [x] Exact predeclared unittest selector localization under bound `BC` and `CC` states
- [x] Controlled suite-level unrelated-assertion negative control
- [x] Controlled weak-but-discriminating selector with one fixed surviving claim-violating mutant
- [x] Controlled typed-receipt versus raw-exit comparison for a fixed import-error mechanism
- [x] Controlled `M0`–`M3` comparison on fixed synthetic discrimination and regression mechanisms
- [x] Frozen outcome-blind minimal stdlib-AST mutation operator set
- [x] Exact mutation target and deterministic mutant identities
- [x] Explicit duplicate, invalid, and not-applicable generation records
- [x] Paired strong-oracle and weak-proxy profiles over identical source and generic mutants
- [x] Historical weak-proxy mutant excluded from generic-operator generalization
- [x] Exact frozen catalog executed under both frozen selector profiles
- [x] Complete typed per-selector, per-profile, reference, and per-mutant result table
- [x] Generation-only duplicate, invalid, and not-applicable records retained without execution
- [x] Complete preregistration-divergent mutation observations retained as negative results rather than harness errors
- [x] Stable mutation-result semantic digest separated from complete runtime and cost digest
- [x] Invocation-bound statement-trace receipt for one exact source, symbol, and target-line set
- [x] Exact statement-line union/intersection comparison for the frozen strong and weak selector profiles
- [x] Direct comparison of statement coverage with the frozen mutation-result table
- [x] Complete preregistration-divergent coverage signatures retained as negative results
- [x] Missing, malformed, or unavailable trace evidence retained as indeterminate rather than empty coverage
- [x] Hit-count magnitude kept diagnostic and excluded from the primary profile comparison
- [x] Editable and installed-wheel mutation-result and statement-coverage smokes on Python 3.11–3.14
- [x] Coverage.py `7.15.2` provenance review with one exact hash-locked universal wheel and research-extra-only dependency boundary
- [x] Exact Coverage.py executable-statement, arc, branch-stat, and static-context evidence for every frozen selector
- [x] Independent selector-context partition and cross-contamination verification
- [x] Exact Coverage.py statement and arc union/intersection comparison for the frozen profiles
- [x] Direct comparison among stdlib statement, Coverage.py statement, Coverage.py branch/arc, and frozen mutation evidence
- [x] Complete Coverage.py `expected`, `unexpected`, and `indeterminate` result semantics with measured-empty separation
- [x] Frozen Coverage.py semantic and complete-report digests with adversarial reconstruction tests
- [x] Editable, installed-wheel, clean offline research-extra, and dependency-removal reproduction on Python 3.11–3.14
- [x] Pre-execution selector-context interaction-lattice source, test, truth-table, profile, path-shape, operator, and mutant identities frozen before result execution
- [x] Exact interaction-lattice statement/arc aggregate hypotheses, anonymous path-multiset contract, condition-independence controls, and mutant-incidence table preregistered
- [x] Reproducible interaction-lattice prior-art boundary with scientific novelty, award-level significance, method superiority, score, threshold, blocker, holdout, and execution claims disabled

Unresolved analysis layers:

- [ ] Execute the selector-context interaction-lattice result only from a merged preregistration commit
- [ ] Test whether exact anonymous path multisets retain interaction evidence lost by aggregate statement and arc union/intersection
- [ ] Test the preregistered agreement between truth-table condition-independence witnesses and dropped-conjunct mutant incidence
- [ ] Expand calibration beyond one fixed source and three generic operators
- [ ] Calibrate mutation evidence against a broader set of valid, weak, ambiguous, invalid, and equivalent-review controls
- [ ] Expand claim-boundary coverage beyond one fixed owned-synthetic target
- [ ] Add frozen conditional-control-flow cases where branch evidence can exercise actual branch points
- [ ] Compare Coverage.py condition/branch evidence and mutation evidence on a broader frozen control population
- [ ] Detect empty and assertion-free test deltas
- [ ] Detect skipped, disabled, and weakened assertions
- [ ] Compare one fixed mutant, the three-mutant catalog, coverage-only, and changed-symbol mutation sets on a larger frozen control population
- [ ] Compare against pinned mutmut and Cosmic Ray configurations where semantics are directly comparable
- [ ] Define an independent equivalent-mutant review procedure
- [ ] Identify excessive mocking around the claimed boundary
- [ ] Repeat flaky tests and report uncertainty
- [ ] Support framework-specific selector and result adapters beyond stdlib unittest
- [ ] Quantify false positives, false negatives, applicability, and cost before any blocker or score

A checked negative control, pre-execution plan, or owned-synthetic result documents one limitation or validates one bounded evidence path. It does not complete Gate 1, validate oracle adequacy, establish mutation or coverage adequacy, prove method superiority, or authorize a merge policy.

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

- [x] Reproducible initial literature-search log and explicit prior-art boundaries for DW-001 source design
- [x] Sealed and retained owned-synthetic development mechanism pilot
- [x] Design-only ecological source universe with execution authorization fixed false
- [ ] Immutable dataset releases and instance manifests reviewed
- [ ] Per-instance license, authorization, and environment feasibility review
- [ ] Accepted ecological unit-of-analysis and sampling-frame contract
- [ ] Independent ground-truth review and disagreement procedure
- [ ] Accepted containment environment for external repositories
- [ ] Development corpus of authorized synthetic and curated public patches
- [ ] Agent-authored patch sampling protocol
- [ ] Frozen protocol and held-out evaluation set
- [ ] Baselines against final-state CI, two-state fail-to-pass, raw exit codes, leave-one-out, delta debugging, mutation testing, coverage, and independent semantic verification
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
