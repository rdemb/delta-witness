# Public Research and Disclosure Boundary

DeltaWitness is developed in a public repository, but public-by-default does not mean publish-everything-by-default.

## Material suitable for public release

The repository may contain:

- source code for the verification harness;
- synthetic or explicitly licensed test fixtures;
- research protocols and preregistrations;
- threat models and architectural decisions;
- released benchmark cases that no longer create operational risk;
- reproducible aggregate results and documented negative findings;
- sanitized traces, digests, and attestations;
- reviewed public-safe statement, arc, branch-stat, and context relations derived from fixed owned-synthetic fixtures;
- exact reviewed third-party package metadata, artifact filenames, source revisions, licenses, and published artifact digests;
- limitations, failed hypotheses, and correction notices.

## Material that must remain private or embargoed

Do not commit or publish:

- credentials, tokens, private keys, cookies, or session material;
- private workspace identifiers or privileged access configuration;
- absolute paths or topology details that expose private infrastructure;
- customer, employer, or third-party confidential data;
- unpatched vulnerability details that create material risk;
- operational exploit chains against systems not built as safe research fixtures;
- private model prompts, logs, or outputs containing sensitive data;
- reports generated with `--include-output` until they have been reviewed manually;
- command arrays containing credentials, signed URLs, private endpoints, or other secret material;
- output digests derived from sensitive low-entropy values unless their disclosure risk has been reviewed;
- proprietary code or datasets without explicit permission;
- raw `.coverage` SQLite databases or other third-party measurement data files;
- unreviewed absolute measured filenames, source roots, configuration-file locations, plug-in identities, environment values, or auto-start state;
- unreviewed Coverage.py contexts, selectors, command arrays, arcs, branch statistics, source/test digests, invocation bindings, runtime identities, or costs when they describe a non-synthetic repository;
- downloaded dependency wheels, source distributions, Sigstore bundles, or package-manager caches unless a separate artifact-retention review explicitly authorizes them.

## Coverage.py direct-baseline boundary

The fixed DW-001 Coverage.py result may publish only the reviewed public-safe JSON projection and its documentation. The raw in-memory or persistent Coverage.py data model is not a public artifact.

For the current fixed owned-synthetic result, the public projection may retain:

- the exact relative path `src/access.py`;
- the exact public selector and static-context identities;
- reviewed source, test, distribution, semantic, and report digests;
- executable, executed, missing, target, arc, branch-stat, and context-partition relations;
- finite nonnegative runtime and cost diagnostics;
- exact expected, unexpected, and indeterminate analysis semantics;
- explicit null policy fields and false authorization fields.

Before applying this publication shape to another repository, review whether relative paths, selectors, contexts, commands, digests, arcs, costs, or equality relations expose confidential structure or low-entropy content. A field that is safe for the owned-synthetic fixture is not automatically safe for an external or private repository.

Do not present the current result as evidence that coverage is generally insufficient, Coverage.py is weak, mutation testing is generally superior or sufficient, oracle strength is complete, a merge blocker is justified, external execution is safe, or an ecological or production result exists.

## Authorization rule

Security research must use one of the following:

1. systems owned and controlled by the researcher;
2. synthetic or intentionally vulnerable research environments;
3. targets covered by explicit written authorization or a clearly applicable security policy.

A tool capability, model capability, or trusted-access program never replaces authorization from the system owner.

## Coordinated disclosure

Potentially harmful findings should be reported privately through the affected project's security process. Public release should follow remediation, an agreed disclosure date, or a documented risk review.

## Publication review

Before a public release:

1. run `python scripts/validate_public_tree.py`;
2. inspect the complete Git diff, including generated and deleted files;
3. search for credentials, command-line secrets, local paths, private identifiers, raw logs, raw `.coverage` data, and sensitive output fingerprints;
4. verify licenses, package provenance, artifact digests, and data authorization;
5. verify that contexts, selectors, commands, measured paths, arcs, branch statistics, bindings, runtimes, and costs are safe to disclose;
6. separate observed facts from interpretation and hypothesis;
7. state what the evidence does not establish;
8. verify that scores, thresholds, blockers, holdout status, ecological inference, method-superiority claims, release authorization, and deployment authorization remain absent unless separately approved and evidenced;
9. obtain a second review for security-sensitive material when practical.

If uncertainty remains, do not publish the material until the boundary is resolved.

## Selector-context interaction-lattice result boundary

The fixed DW-001 selector-context interaction-lattice execution is restricted to the exact project-owned synthetic source, tests, selectors, profiles, generated mutants, Coverage.py distribution, merged preregistration, and separately authorized execution protocol recorded by the result contract.

The default release artifact is the dependency-free **public checkpoint**. It may retain only reviewed stable relations needed to reproduce the bounded interpretation, including:

- preregistration, protocol, catalog, prior-art, baseline-result, result-semantic, and checkpoint digests;
- exact profile identities and truth-table membership;
- reviewed statement and arc aggregate relations;
- anonymous path-multiset identities with multiplicity semantics;
- complete mutant-incidence outcomes and stable expected/unexpected/indeterminate analysis;
- explicit null score and threshold fields and false blocker, holdout, ecological, external-execution, release, and deployment authorizations.

The **diagnostic-only full result** is not the default public artifact. Retaining or publishing it requires a separate privacy and boundary review because it contains exact selector commands, static contexts, invocation bindings, typed and Coverage.py receipt metadata, path shapes, runtime identity, output digests, and measured costs. Raw `.coverage` data, raw stdout or stderr, tracebacks, absolute paths, environment values, credentials, source or test bodies excluded by the contract, and unreviewed low-entropy fingerprints remain prohibited.

A publication-safe shape for this owned-synthetic fixture is not automatically safe for an external, private, employer, customer, or third-party repository. Reuse requires a new authorization, privacy, license, containment, and boundary review. External repository execution remains unauthorized.

Do not present this result or checkpoint as evidence of general statement, branch, path, condition, MC/DC, combinatorial, checked-coverage, mutation, or oracle adequacy; method superiority; coding-agent or ecological effectiveness; a score, threshold, or merge blocker; containment or authentication; Gate completion; production readiness; scientific novelty; or award-level significance.
