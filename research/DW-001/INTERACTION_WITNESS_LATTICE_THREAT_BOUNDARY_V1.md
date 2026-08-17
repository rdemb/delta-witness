# DW-001 Interaction-Witness Lattice Design Threat Boundary v1

## Status

This document covers the **pre-execution design and generation boundary** for the selector-context interaction-witness lattice.

The current branch may parse, transform, unparse, reparse, compile, serialize, and verify fixed project-owned bytes. It does not execute the new candidate, tests, Coverage.py measurement, or mutants. It does not authorize external repositories, a holdout, a score, a threshold, a merge blocker, or any public result claim.

A later result layer requires a separate threat-model update from a merged preregistration commit.

## Protected statement

> Before the new owned-synthetic source, selectors, Coverage.py evidence, or mutant outcomes are executed or inspected through the authorized result workflow, DeltaWitness publicly fixes exact source/test identities, truth-table quadrants, selector profiles, expected statement/arc path shapes, anonymous path-multiset semantics, condition-independence relations, mutation operators, generation controls, expected mutant incidence, direct baselines, falsification criteria, and non-policy fields.

This statement is an integrity and sequencing claim about committed design metadata. It is not an observed coverage, path, mutation, oracle-strength, ecological, novelty, or production result.

## Assets

The design aims to protect:

- exact candidate source bytes and SHA-256;
- exact semantic-AST identity and compatibility rule;
- exact test bytes and SHA-256;
- exact target symbol, node kind, source position, operands, target lines, and target digest;
- exact truth-table inputs, expected decisions, quadrant order, selector order, and selector identities;
- exact profile identities, roles, memberships, cardinalities, and order;
- exact per-quadrant expected statement, missing-statement, arc, and branch-statistic relations;
- exact path-shape and anonymous path-multiset digest semantics;
- order independence of anonymous path multisets;
- explicit preservation of path multiplicity;
- separation of anonymous path shapes from selector, quadrant, context, and invocation identities;
- exact truth-table condition-independence relations;
- exact generic operator order, transformation semantics, target identity, mutant identities, and outcome-blind selection declaration;
- explicit duplicate, invalid, and not-applicable generation controls;
- complete expected mutant/profile incidence before execution;
- separation of generation identity from runtime outcome;
- exact prior-art sources, closest baselines, planned difference, falsification criteria, and novelty boundary;
- explicit execution, holdout, denominator, scoring, threshold, blocker, superiority, production, and novelty non-authorizations;
- plan, catalog, and prior-art semantic reconstruction and digests;
- preservation of the PR #46 source, selectors, result, and digests;
- public artifacts from source/test body disclosure where the artifact contract excludes those bodies;
- future negative and preregistration-divergent results from suppression or post-outcome repair.

## Adversaries and failure sources

The model includes:

- a researcher or agent changing source, tests, selectors, profiles, operators, path hypotheses, expected outcomes, or exclusions after observing results;
- private or local execution occurring before the public merge and not being disclosed;
- a chat narrative or timestamp treated as proof that no earlier outcome inspection occurred;
- a new commit presented as the original preregistration after design drift;
- selector names, quadrant labels, profile cardinality, context strings, or invocation bindings leaking directly into the anonymous path key;
- selector reordering changing a supposedly order-independent path signature;
- duplicate path shapes silently collapsed into a set when multiplicity matters;
- different path shapes made equal by an under-specified canonicalization;
- semantically equivalent paths made different only by unstable representation or interpreter formatting;
- statement or arc hit-count magnitude substituted for exact set or multiset comparison;
- a profile aggregate trusted instead of being reconstructed from exact quadrant paths;
- truth-table condition-independence labels edited independently from profile membership;
- expected mutant outcomes edited independently from the fixed truth table and transformations;
- a known outcome-targeted mutant relabeled as an outcome-blind generic operator;
- duplicate, invalid, or not-applicable controls omitted, executed, or counted as runtime evidence;
- mutant survival presented as equivalent-mutant proof;
- successful compilation presented as runtime, semantic, or mutation evidence;
- source, test, target, selector, profile, operator, mutant, prior-art, or prior-result substitution followed by recomputed digests;
- reordered normative arrays, duplicate JSON keys, wrong types, extra fields, NaN, infinity, or negative values accepted as equivalent design metadata;
- JSON Schema treated as the sole semantic verifier;
- one exact preregistration presented as a systematic literature review or novelty proof;
- established Coverage.py, path-coverage, MC/DC, combinatorial-testing, checked-coverage, mutation, or oracle concepts relabeled as new;
- public path, selector, input, mutant, or digest metadata exposing sensitive structure in a later non-synthetic use;
- malicious or defective Python AST, `ast.unparse`, compiler, filesystem, Git, CI, or package behavior;
- coordinated replacement of the complete repository and every expected digest;
- a merged preregistration treated as authorization to execute untrusted or external code.

## Trust boundaries

### Git history

A merged commit creates a durable public ordering relation between the committed preregistration and later authorized result commits.

It does not prove that no person, tool, local checkout, private branch, or external environment executed the design before the merge. The project therefore treats public merge ordering as a reproducible workflow control, not a cryptographic proof of non-inspection.

Any known pre-merge execution or outcome inspection must be disclosed as a protocol deviation. If material outcomes were inspected before freeze, the result must be labeled exploratory or the experiment redesigned with new untouched bytes.

### Fixed source and test bytes

Source and test bodies are project-owned and embedded as private module constants for deterministic reconstruction. Public plan and catalog JSON retain their identities but not their bodies.

The design trusts the repository source, Python UTF-8 decoding, SHA-256 implementation, AST parser, and fixed constants. Digest identity is integrity metadata, not authorship or provenance authentication.

### Python AST and compiler

Parsing, transforming, unparsing, reparsing, and compiling establish deterministic design identities for the fixed source on supported Python versions. They do not establish runtime behavior, semantic equivalence, mutation validity, or cross-language applicability.

`ast.unparse` output and AST fields can vary across interpreter versions. The compatibility claim is restricted to the fixed source, adapter, and supported Python 3.11–3.14 matrix.

### Prior-art log

The log records authoritative primary sources and explicit boundaries. It is not a complete systematic review, citation-count analysis, patent search, or proof of novelty absence or presence.

Primary-source titles, DOI metadata, and URLs are trusted as bibliographic inputs. Their inclusion does not establish that the planned representation is useful.

### Future execution boundary

The plan records expected outcomes so later complete disagreements can be retained as `unexpected`. The current design does not implement or authorize the runner.

A later result PR must independently verify that it begins from the exact merged plan, catalog, prior-art log, source/test bytes, and Coverage.py dependency boundary.

## Invariants

1. The plan status is `pre_execution_frozen_design`.
2. Future execution status is `not_implemented`.
3. Execution authorization is false.
4. Holdout selection and primary-denominator eligibility are false.
5. Score, headline score, and universal threshold are null.
6. Merge-blocker, ecological-inference, MC/DC-certification, coverage-superiority, mutation-superiority, scientific-novelty, award-level-significance, method-superiority, and production-readiness claims are false.
7. The PR #46 merge commit and frozen semantic/report digests are exact and separately verified.
8. The new source and selectors are not the PR #46 source or selectors.
9. Source and test SHA-256 identities are recomputed from exact fixed bytes.
10. The semantic-AST digest is recomputed from a versioned location-free representation.
11. Exactly one top-level `is_authorized` function and one final `role_gate and mfa_gate` target exist.
12. Target path, symbol, node kind, cardinality, source position, operands, target lines, and target digest are exact.
13. The truth table contains exactly ordered `TT`, `TF`, `FT`, and `FF` entries with exact inputs, decisions, selectors, and selector IDs.
14. Selectors and selector IDs are unique.
15. Profiles appear in exact order and contain exact quadrant, selector, and selector-ID memberships.
16. Three equal-cardinality profiles remain available to test cardinality-only explanations.
17. Per-quadrant expected statement and arc arrays are sorted, unique, and digest-bound.
18. Every expected profile statement/arc union and intersection is reconstructed from its quadrant records.
19. All profile aggregate statement signatures are preregistered equal.
20. All profile aggregate arc signatures are preregistered equal.
21. Anonymous path shapes contain only exact executed statement and arc sets.
22. Anonymous path keys exclude selector, selector ID, quadrant, context, invocation binding, and hit magnitude.
23. Selector/context/binding identities remain retained separately in the future result contract.
24. Anonymous path multisets are order-independent and preserve multiplicity.
25. The five profile path-multiset digests are exact; the three equal-cardinality profile digests are distinct.
26. MFA and role independence witnesses are reconstructed only from fixed truth-table pair membership.
27. Exactly five generic operators are selected outcome-blind before execution.
28. Exactly one duplicate, one not-applicable, and one invalid generation control are retained.
29. Catalog records contain generation identities and no observed runtime outcome.
30. The complete expected mutant/profile matrix is reconstructed from the fixed truth table and transformations.
31. Later tool error, timeout, missing receipt, context ambiguity, candidate invalidity, invalid mutant, or unavailable measurement cannot become killed, survived, or empty complete evidence.
32. Later complete divergence from any path, aggregate, independence, or mutation hypothesis remains `unexpected` rather than being hidden or repaired.
33. Plan, catalog, and prior-art digests are recomputed, and complete semantic structures are independently reconstructed.
34. Recomputed digests cannot hide normative array reorder, source/test/target/profile/operator/mutant substitution, policy escalation, or novelty-claim substitution.
35. Editable and installed-wheel smokes reconstruct the same design on Python 3.11–3.14 without importing Coverage.py.
36. Removing Coverage.py leaves design verification and the base product functional.
37. No candidate, selector, mutant, Coverage.py, external repository, or holdout execution is added by the preregistration PR.

## Residual risks

### Public freeze is not proof of no prior inspection

Git establishes public commit ordering, not the full private history of human or tool activity. The strongest honest claim is that the public, reproducible workflow freezes the design before the authorized result implementation.

### Expected structural evidence can be wrong

Line tables, branch arcs, entry/exit sentinels, module-import timing, and Coverage.py behavior may differ from the preregistration. A complete difference is an expected research possibility and must not be corrected after observation.

### Anonymous path identity can be representation-sensitive

Exact statement and arc sets are more stable than raw traces, but source formatting, compiler line tables, interpreter changes, and instrumentation behavior can still alter identities without a meaningful semantic change.

### Path partitions are not oracle slices

Per-selector path co-occurrence does not show that executed values reach an assertion. Checked coverage and dynamic slicing remain closer baselines for oracle influence.

### Truth-table controls are narrow

The fixed two-condition conjunction makes condition independence and mutant incidence auditable. It is not representative of general predicates, short-circuit expressions, stateful systems, exceptions, loops, concurrency, or real authorization policies.

### Mutant controls are not a calibrated mutation system

Five fixed transformations can illustrate asymmetric detection but cannot estimate mutation adequacy, operator quality, fault prevalence, false-warning rates, missed-warning rates, or equivalent-mutant frequency.

### Integrity is not authentication

All digests are unkeyed. An actor who replaces the complete trusted source chain can recompute them. No signed-attestation claim is made.

### Publication metadata can be sensitive

Although the current case is synthetic, truth-table labels, selector names, paths, source positions, mutant identities, digests, and future contexts can expose structure in another repository.

## Safe operation

- Merge the preregistration before creating the authorized result branch.
- Do not execute or inspect the new candidate, selectors, Coverage.py measurements, or mutants through the project workflow before merge.
- Disclose any known pre-freeze execution or outcome inspection.
- If material outcomes were inspected, mark the case exploratory or create new untouched bytes and a new preregistration.
- Verify plan, catalog, prior-art, schema, and PR #46 identities before later execution.
- Keep source, tests, profiles, operators, expected paths, expected mutant outcomes, exclusions, and comparison rules unchanged after observation.
- Preserve complete unexpected and indeterminate evidence.
- Keep anonymous path shapes independent of selector names and cardinality artifacts.
- Preserve path multiplicity.
- Prefer a simpler truth-table or MC/DC baseline if it captures the same complete relation.
- Never present path partitions as checked coverage, dynamic slicing, general MC/DC, or mutation adequacy.
- Execute only fixed project-owned synthetic bytes in a later separately reviewed result PR.
- Keep external repositories, holdout, score, threshold, blocker, release, deployment, and ruleset disabled.

## Claim boundary

A valid merged preregistration establishes only that the exact design, direct baselines, hypotheses, controls, falsification criteria, and non-policy fields are publicly reconstructable before the authorized result implementation.

It does not establish any observed coverage, path, branch, condition, mutation, oracle, ecological, coding-agent, policy, production, novelty, or award-level result.
