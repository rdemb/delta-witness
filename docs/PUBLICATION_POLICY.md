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
- proprietary code or datasets without explicit permission.

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
3. search for credentials, command-line secrets, local paths, private identifiers, raw logs, and sensitive output fingerprints;
4. verify licenses and data provenance;
5. separate observed facts from interpretation and hypothesis;
6. state what the evidence does not establish;
7. obtain a second review for security-sensitive material when practical.

If uncertainty remains, do not publish the material until the boundary is resolved.
