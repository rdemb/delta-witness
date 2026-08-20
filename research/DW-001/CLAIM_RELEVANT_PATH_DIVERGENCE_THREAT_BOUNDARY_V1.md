# DW-001 Claim-Relevant Path Divergence Threat Boundary v1

## Protected properties

- exact source, AST, test, influence-control, plan, catalog, and prior-art identity;
- separation of claim-facing and collateral-reference observations;
- separation of design artifacts from execution results;
- preservation of `unexpected` and `indeterminate` outcomes;
- inability to promote scores, novelty, deployment, release, or production claims through document substitution;
- absence of Coverage.py and fixture execution during import, build, verification, and smoke reproduction.

## Adversary model

The verifier assumes an attacker may edit JSON fields, reorder lists, add or remove keys, recompute self-digests, substitute selector roles, alter expected outcomes, inject an execution result, promote novelty language, supply duplicate JSON keys, use malformed UTF-8, or replace a regular path with a symbolic link or directory.

## Controls

- exact reviewed-identity constants independent of document self-digests;
- semantic reconstruction rather than schema-only acceptance;
- fail-closed regular-file inspection before parsing;
- canonical JSON duplicate-key rejection;
- exact list order and cardinality;
- fixed false/null policy fields;
- no `exec` or `eval` primitive in the preregistration module;
- dependency-free import and wheel smoke with Coverage.py absent;
- public-tree validation unchanged.

## Residual risk

The fixed influence graph is project-owned and may be an inadequate model of true assertion influence. The fixture is intentionally small and non-representative. Python parser behavior can differ across supported versions. A future execution adapter introduces a larger trust boundary and requires a new threat-model review. These limitations prohibit a general safety, causal, slicing, oracle-quality, production-readiness, or novelty claim.
