# Research Note 000: Problem Definition and Prior-Art Boundary

**Status:** living scoping note. This document does not make a novelty claim.

## Research question

Conventional continuous integration normally evaluates the final repository state. When an AI coding agent also authors or modifies the tests used to justify completion, final-state success can provide false assurance.

DeltaWitness studies a narrower question:

> Does a four-state replay across base and candidate implementation-side trees and base and candidate test trees provide useful additional evidence for post-change verification?

The first prototype does not claim to prove causality. It constructs an explicit, falsifiable change witness.

## Established prior art

The central fail-to-pass idea is not new.

- **TDD-Bench Verified** evaluates generated tests by applying them to old code, where at least one relevant test should fail, and to the resolved code, where the tests should pass. It provides a direct two-state baseline for the candidate-test portion of DeltaWitness. Ahmed et al., 2024: https://arxiv.org/abs/2412.02883
- **TestEvo-Bench** studies executable test and code co-evolution, including test generation and test update tasks anchored to real repository histories. Wang et al., 2026: https://arxiv.org/abs/2607.02469
- **All Smoke, No Alarm** reports that 80.2 percent of 86,156 studied agent-authored test patches contained weak or no explicit oracle signals. Banik et al., 2026: https://arxiv.org/abs/2606.18168
- **Are Coding Agents Generating Over-Mocked Tests?** reports that agent-authored test changes add mocks more frequently than non-agent changes in the studied repositories. Hora and Robbes, 2026: https://arxiv.org/abs/2602.00409
- **RETRACE** performs independent patch verification through bidirectional reconstruction and reconciliation. It is adjacent because it verifies agent patches, but its primary signal is semantic alignment rather than Git-native code/test replay. Li et al., 2026: https://arxiv.org/abs/2608.08950
- Automated program repair research has long documented plausible patches that pass available tests but overfit. A QuixBugs study classified 53.3 percent of 338 plausible patches as overfitting. Ye et al., 2018: https://arxiv.org/abs/1805.03454
- **INVALIDATOR** combines inferred invariants and learned syntax to identify overfitting patches. Le-Cong et al., 2023: https://arxiv.org/abs/2301.01113
- **UTBoost** reports that insufficient tests can label erroneous SWE-bench patches as successful and proposes automated test augmentation. Yu et al., 2025: https://arxiv.org/abs/2506.09289

## Provisional distinction

DeltaWitness currently combines the following elements:

1. post-change verification from two declared Git commits;
2. a four-state cross of implementation-side and test-side trees;
3. deterministic synthetic commits for hybrid states;
4. strict, explicit expectations and exit-code classes for each claim;
5. incomplete-run handling rather than treating every nonzero result as a valid witness failure;
6. model-free evaluation in the trust path;
7. sanitized command environments and output redaction by default;
8. a stable semantic witness digest and an exact report digest;
9. a future path toward patch ablation, mutation analysis, and signed attestations.

Individual elements have substantial prior art. The combination may still be unoriginal or operationally weak. No public claim of being first, unique, or scientifically novel should be made until a systematic review identifies direct baselines and an empirical study demonstrates additional value.

## Primary baseline

The immediate baseline is ordinary final-state CI:

```text
candidate implementation + candidate tests -> pass or fail
```

The second baseline is two-state fail-to-pass validation:

```text
base implementation + candidate tests      -> fail
candidate implementation + candidate tests -> pass
```

DeltaWitness adds two controls:

```text
base implementation + base tests           -> declared control
candidate implementation + base tests      -> regression-preservation control
```

The empirical question is not whether four executions are more verbose. It is whether the added controls detect materially important false-assurance cases at acceptable cost.

## Falsification criteria

The central approach should be narrowed, redesigned, or abandoned if evidence shows that:

- hybrid states are invalid or misleading for common real-world patches;
- the added states provide little detection value beyond two-state fail-to-pass validation;
- environment and dependency drift dominate the observations;
- existing tools already implement the same method more rigorously;
- false positives or over-refusal make the gate impractical;
- operational cost exceeds the security or review value;
- test changes cannot be separated from implementation changes without invalidating the build.

Negative findings will be documented as first-class research results.

## Next literature task

Before an empirical release, the project will publish a reproducible search protocol covering software patch validation, test co-evolution, test adequacy, mutation testing, automated program repair, coding-agent evaluation, software provenance, and assurance cases. The protocol will record databases, queries, inclusion criteria, exclusions, and review dates.
