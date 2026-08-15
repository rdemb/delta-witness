# DW-001 Prior-Art Search Log

**Status:** exploratory search log; not a systematic review; not preregistered.

**Search date:** 2026-08-15.

**Repository anchor:** `a29eb1476bec42bfcbfe6758f05bb70667b056c7`.

**Purpose:** identify direct baselines, nearest adjacent methods, source-identity defects, and missing comparison dimensions before freezing DW-001.

No novelty or superiority conclusion may be drawn from this log. A single-reviewer exploratory search can miss relevant work, misclassify methods, and overrepresent easily discoverable English-language publications.

## 1. Sources searched

- arXiv title, identifier, and abstract records;
- ACM Digital Library and DOI landing pages;
- official GitHub repositories and exact source commits where available;
- publisher or institutional records when the version of record was not directly indexed;
- official Python `unittest` and pytest documentation for outcome semantics;
- NIST program pages for agent-evaluation evidence principles.

Search-engine snippets, secondary summaries, and repository issue reports were used only for discovery. Technical claims in the baseline map should be checked against papers, official documentation, or source code before protocol freeze.

## 2. Search strings executed

The following strings record the exploratory queries used during this review. They are not yet a complete database-specific search strategy.

| ID | Query |
|---|---|
| `Q01` | `site:arxiv.org 2412.02883 TDD-Bench Verified` |
| `Q02` | `site:arxiv.org 2310.06770 SWE-bench` |
| `Q03` | `FAIL_TO_PASS PASS_TO_PASS get_eval_report` within `SWE-bench/SWE-bench` |
| `Q04` | `fail_to_pass coverage evaluation` within `IBM/TDD-Bench-Verified` |
| `Q05` | `"10.1145/3715760"` |
| `Q06` | `"ChangeGuard" "Validating" program changes` |
| `Q07` | `"10.1145/3763145"` |
| `Q08` | `"P³" "Reasoning about Patches via Product Programs"` |
| `Q09` | `site:dl.acm.org automated patch assessment generated tests RGT 2019 software patches` |
| `Q10` | `site:arxiv.org 1909.13694 automated patch assessment` |
| `Q11` | `site:arxiv.org 2301.01113 Invalidator patch correctness` |
| `Q12` | `"10.1145/3106237.3106274"` |
| `Q13` | `"Opad" patch correctness assessment FSE 2017` |
| `Q14` | `PATCH-SIM automated patch correctness assessment paper DOI` |
| `Q15` | `DiffTGen identifying test-suite-overfitted patches test case generation DOI` |
| `Q16` | `"Identifying Patch Correctness in Test-Based Automatic Program Repair" DOI` |
| `Q17` | `weighted delta debugging arxiv 2411.19410` |
| `Q18` | `RETRACE patch verification arxiv 2608.08950` |
| `Q19` | `FixedBench arxiv 2605.07769` |
| `Q20` | `coding agent generated tests oracle signals arxiv 2606.18168` |

## 3. Provisional inclusion criteria

A record was retained when it addressed at least one of:

- final-state or fail-to-pass evaluation of software patches;
- regression preservation or pass-to-pass validation;
- detection of plausible but incorrect or overfitted patches;
- relational execution of pre- and post-patch programs;
- systematic isolation or attribution of changed program elements;
- distinction between semantic test failure and execution/infrastructure failure;
- test-oracle quality for agent-authored tests;
- independent, machine-readable, or integrity-bound software evidence;
- unnecessary changes by coding agents.

## 4. Provisional exclusion criteria

A record was excluded from the nearest-neighbor table when:

- it concerned code generation without patch evaluation;
- it evaluated only model preference or human style without executable behavior;
- no stable paper, specification, official documentation, or source artifact could be identified;
- the apparent match was caused by an incorrect identifier or unrelated title;
- it duplicated a retained version of the same work;
- it addressed deployment authorization without patch-evidence evaluation.

An excluded executable baseline still requires a reason in the frozen protocol. This exploratory log does not authorize exclusion by itself.

## 5. Source-identity audit

Three material citation defects were found in the pre-review `docs/RESEARCH_NOTE_000.md`.

| Prior entry | Finding | Corrected identity |
|---|---|---|
| `https://github.com/kanishkamisra/tdd-bench-verified` | repository lookup did not resolve; not the official artifact | `https://github.com/IBM/TDD-Bench-Verified` |
| ChangeGuard linked as arXiv `2405.01594` | identifier did not identify ChangeGuard | DOI `https://doi.org/10.1145/3715760`; title *ChangeGuard: Validating Code Changes via Pairwise Learning-Guided Execution* |
| product-program work linked as arXiv `2501.13158` | identifier was unrelated to software patch analysis | DOI `https://doi.org/10.1145/3763145`; title *P³: Reasoning about Patches via Product Programs* |

These corrections change source identity, not DeltaWitness functionality. The defect demonstrates why the systematic review must retain exact identifiers and title verification rather than relying on remembered or nearby links.

## 6. Screened nearest-neighbor set

### `S01` — SWE-bench

- paper: https://arxiv.org/abs/2310.06770
- official repository: https://github.com/SWE-bench/SWE-bench
- reviewed grading source: https://github.com/SWE-bench/SWE-bench/blob/128cbd1a5759694874e6bd56624cb2fd6fb079e2/swebench/harness/grading.py
- relation: direct benchmark reference for issue-resolution evaluation, including `FAIL_TO_PASS` and `PASS_TO_PASS` groups;
- DW-001 role: direct semantic reference and implementation audit target;
- boundary: its grading/test-world construction is not identical to DeltaWitness's four exact Git states.

### `S02` — TDD-Bench Verified

- paper: https://arxiv.org/abs/2412.02883
- official repository: https://github.com/IBM/TDD-Bench-Verified
- relation: direct benchmark for tests intended to fail before a repair and pass after it, with separate coverage-adequacy analysis;
- DW-001 role: direct fail-to-pass and oracle-adequacy reference;
- boundary: test generation and coverage are broader than typed outcome classification.

### `S03` — Delta debugging

- Andreas Zeller and Ralf Hildebrandt, *Simplifying and Isolating Failure-Inducing Input*: https://doi.org/10.1109/32.988498
- relation: established minimization of failure-inducing inputs or changes;
- DW-001 role: adjacent to path intervention, not the primary H0 state-set baseline;
- follow-up role: direct comparator for H2 exact influence.

### `S04` — Change/cause localization

- Holger Cleve and Andreas Zeller, *Locating Causes of Program Failures*: https://doi.org/10.1145/1062455.1062522
- relation: systematic search over program changes associated with failure;
- DW-001 role: adjacent causal-debugging prior art;
- boundary: does not by itself define the DeltaWitness four-state witness or typed receipt protocol.

### `S05` — Weighted Delta Debugging

- preprint: https://arxiv.org/abs/2411.19410
- relation: improves search ordering or efficiency for delta debugging;
- DW-001 role: later H2 efficiency comparator;
- boundary: exact exhaustive coalition enumeration and one minimizing search answer different questions.

### `S06` — PATCH-SIM / behavior-similarity patch assessment

- paper: https://arxiv.org/abs/1706.09120
- relation: uses execution-behavior similarity between original and patched programs to assess patch correctness;
- DW-001 role: candidate secondary dynamic patch-assessment baseline;
- unknown: current artifact availability, language support, and safe reproducibility must be verified before inclusion.

### `S07` — DiffTGen

- paper: https://doi.org/10.1145/3092703.3092718
- relation: generates tests that expose semantic differences between faulty, patched, and reference behavior;
- DW-001 role: candidate secondary test-generation baseline for scenarios with trusted reference patches;
- boundary: reference-patch and Java-oriented assumptions may limit direct comparability.

### `S08` — Opad

- paper: https://doi.org/10.1145/3106237.3106274
- relation: generates tests and uses crash and memory-safety oracles to filter overfitted patches;
- DW-001 role: candidate secondary baseline on compatible native-code scenarios;
- boundary: its oracle and target ecosystem differ from declared Python test witnesses.

### `S09` — Random testing with Ground Truth patch assessment

- paper/preprint: https://arxiv.org/abs/1909.13694
- version-of-record DOI: https://doi.org/10.1007/s10664-020-09920-w
- relation: generates tests from human-written reference patches for automated patch assessment;
- DW-001 role: candidate secondary baseline when trusted reference patches exist;
- boundary: reference-patch ground truth is unavailable for some agent-authored or synthetic scenario designs.

### `S10` — Invalidator

- paper: https://arxiv.org/abs/2301.01113
- relation: combines inferred invariants and syntactic representation for automated patch-correctness assessment;
- DW-001 role: adjacent semantic/static classifier;
- boundary: a learned or inferred correctness classifier is not a controlled test-state ablation.

### `S11` — ChangeGuard

- version of record: https://doi.org/10.1145/3715760
- relation: pairwise learning-guided execution for validating intended behavior-preserving code changes;
- DW-001 role: candidate secondary comparator for preservation/refactoring scenarios;
- boundary: its intended relation is usually behavior preservation, while DW-001 includes intended behavior changes exposed by tests.

### `S12` — P³

- version of record: https://doi.org/10.1145/3763145
- relation: constructs product programs for relational analysis of pre- and post-patch C programs;
- DW-001 role: closest relational-program-analysis neighbor identified in this pass;
- boundary: requires a relational patch specification and currently targets a different execution/analysis model.

### `S13` — RETRACE

- preprint: https://arxiv.org/abs/2608.08950
- relation: reconstructs the problem implied by a patch and compares it with the reported issue;
- DW-001 role: complementary independent semantic-alignment verifier;
- boundary: semantic issue alignment and executable test-state evidence are different questions.

### `S14` — FixedBench

- preprint: https://arxiv.org/abs/2605.07769
- relation: evaluates coding tasks whose reported problem is already resolved and observes undesirable unnecessary changes;
- DW-001 role: motivates no-op/already-resolved negative controls;
- boundary: motivation and scenario source, not an equivalent verification method.

### `S15` — Oracle signals in agent-authored tests

- preprint: https://arxiv.org/abs/2606.18168
- relation: large-scale analysis of explicit oracle signals in coding-agent test patches;
- DW-001 role: motivates retaining oracle quality outside the current typed-execution claim;
- boundary: does not validate the four-state matrix or receipt protocol.

### `S16` — Python framework outcome semantics

- `unittest` documentation: https://docs.python.org/3/library/unittest.html
- pytest exit-code documentation: https://docs.pytest.org/en/stable/reference/exit-codes.html
- relation: official evidence that test frameworks expose outcomes richer than one generic process failure;
- DW-001 role: direct source for `O0_EXIT_CODE` versus `O1_TYPED_RECEIPT` semantics;
- boundary: DeltaWitness's receipt binding and fail-closed policy remain project-specific implementation hypotheses.

### `S17` — NIST agentic-AI evaluation probes

- program page: https://www.nist.gov/programs-projects/building-evaluation-probes-agentic-ai
- relation: supports machine-readable evidence and claim-to-evidence traceability as evaluation principles;
- DW-001 role: evidence-design reference;
- boundary: DeltaWitness is not a NIST standard, certification, or reviewed implementation.

## 7. Direct-baseline conclusion from this pass

### FACT

Fail-to-pass and regression-preservation evaluation are established. DeltaWitness cannot claim contribution merely for checking that a new test fails before a fix and passes afterward, or for checking that prior tests remain green.

### OBSERVATION

The closest fair controlled comparator is not only final-state CI or two-state fail-to-pass. It is a three-state method containing:

```text
base implementation + candidate tests
candidate implementation + base tests
candidate implementation + candidate tests
```

The incremental H0 question is therefore whether the remaining `base implementation + base tests` endpoint and full matrix consistency add useful evidence after the stronger three-state comparator.

### DECISION

Typed receipts must be crossed as a separate factor. Otherwise execution-error detection would be incorrectly attributed to the matrix state set.

## 8. Artifact and implementation review still required

Before protocol freeze, each candidate executable baseline needs:

- exact repository and commit or release identity;
- license and permitted-use review;
- installation and dependency procedure;
- language/ecosystem compatibility;
- expected inputs and ground-truth assumptions;
- output semantics and error handling;
- containment and network requirements;
- maintained/unmaintained status;
- smallest reproducible smoke case;
- reason for inclusion or exclusion.

No external artifact should be executed in an environment containing credentials or sensitive data.

## 9. Systematic-review work still missing

This exploratory pass did not perform:

- database-specific exhaustive queries across ACM DL, IEEE Xplore, Scopus, Web of Science, SpringerLink, or DBLP;
- backward and forward citation snowballing for every nearest neighbor;
- independent duplicate screening;
- calibrated title/abstract and full-text inclusion decisions;
- inter-reviewer agreement measurement;
- complete artifact-availability verification;
- risk-of-bias or evidence-quality assessment;
- public excluded-record table with reasons;
- external review of the nearest-neighbor set.

## 10. Proposed systematic-review protocol skeleton

Before any novelty statement:

1. freeze review questions and comparison dimensions;
2. define database-specific query strings and date ranges;
3. export records with identifiers and metadata;
4. deduplicate by DOI, arXiv identifier, normalized title, and version relationship;
5. screen titles/abstracts against frozen criteria;
6. screen full texts and artifacts;
7. extract method, target, oracle, state model, outcome semantics, environment, report integrity, cost, and evaluation design;
8. record all close exclusions with reasons;
9. conduct backward and forward snowballing;
10. obtain an independent review of the nearest-neighbor set;
11. version the evidence table and correction history.

## 11. Claim boundary

This log establishes only what was searched and screened in one exploratory pass. It does not establish completeness, scientific novelty, absence of equivalent methods, or superiority over any retained work.
