# DW-001 Claim-Relevant Path Divergence Architecture v1

## FACT — bounded components

1. **Owned fixture bytes.** The source and test strings are synthetic, immutable inputs with byte and semantic-AST identities.
2. **Design builder.** A dependency-free module parses, compiles, transforms, hashes, and returns defensive copies. It does not execute the fixture.
3. **Canonical artifacts.** Plan, catalog, and prior-art documents use canonical JSON and self-digests normalized through one null digest field.
4. **Exact verifiers.** Verification compares types, keys, list order, values, reviewed identities, and recomputed self-digests. A correctly resealed substitute is still rejected.
5. **Regular-file loaders.** Loaders reject symbolic links, non-regular files, duplicate JSON keys, malformed UTF-8, malformed roots, and semantic substitutions.
6. **Exact schemas.** Draft 2020-12 schemas close every object boundary and fix every array's length, order, and item schema.
7. **Tests and smoke.** Regression tests cover reconstruction, policy boundaries, substitutions, loader attacks, schema closure, and dependency-free wheel reproduction.

## Trust boundaries

The preregistration module trusts only reviewed constants in its own installed distribution and canonical artifacts that reproduce those constants exactly. Git metadata, filenames alone, caller-provided digests, schema validity alone, and a green final-state test run are insufficient identity evidence.

The temporary branch-maintenance job used to reconstruct the files is not part of the research architecture. It is retained only in Git history and PR evidence, removes itself from the final tree, receives no repository secrets, and cannot authorize research execution or publication claims.

## Non-goals

This layer is not a Python sandbox, dynamic slicer, checked-coverage implementation, mutation-testing framework, general causality engine, production policy engine, remote executor, or release gate.
