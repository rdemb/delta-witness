# Security Policy

## Supported versions

DeltaWitness is pre-alpha research software. Only the latest commit on `main` is maintained during this phase.

## Reporting a vulnerability

Do not open a public issue for an unpatched vulnerability that could place users or third parties at risk.

Use the repository's private GitHub security-advisory channel. Include:

- the affected version or commit;
- reproduction steps using a safe fixture;
- expected and observed behavior;
- security impact and preconditions;
- a suggested mitigation when available.

The maintainer will acknowledge a complete report as soon as practical, coordinate remediation and disclosure, and credit the reporter unless anonymity is requested.

## Research boundary

DeltaWitness executes declared commands. A specification and repository must therefore be treated as executable code. The current version is not a sandbox and must not be used to evaluate hostile code on a workstation or server containing valuable credentials.

Security testing must remain within systems owned by the researcher, purpose-built fixtures, or targets covered by explicit authorization.
