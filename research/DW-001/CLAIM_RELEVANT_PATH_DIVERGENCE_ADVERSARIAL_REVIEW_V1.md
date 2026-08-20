# DW-001 Claim-Relevant Path Divergence Adversarial Review v1

## Review target

The review covers the design-only builder, canonical artifacts, exact schemas, loaders, tests, retained read-only workflow, and documentation. It excludes all future candidate, selector, Coverage.py, fault, influence, and target execution.

## Required attacks

The regression suite must reject each attack even when the attacker recomputes the affected document self-digest:

- decision-route membership substitution;
- claim/collateral selector-role substitution;
- cell or prior-art source reordering;
- influence-edge substitution;
- expected-matrix substitution;
- catalog status substitution and result injection;
- duplicate-implementation rebinding;
- novelty promotion;
- extra, missing, and wrong-type fields;
- symbolic-link, directory, duplicate-key, and malformed-UTF-8 loader inputs.

It must also confirm that the neutral-diversion control preserves declared outputs, profiles remain overlapping and denominator-ineligible, all execution/publication policy fields remain false or null, Coverage.py is absent from imports, and no `exec`/`eval` primitive exists in the module.

## Merge decision rule

The PR is mergeable only if the targeted attacks, complete repository regression suite, public-tree validator, compilation, design-only smoke, build, editable/wheel equivalence, supported-Python matrix, final-head CI, and post-merge validation are all green with no unresolved review thread or head movement. Otherwise the result is a named blocker, not an inferred success.
