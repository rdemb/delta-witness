# Agent Instructions

This repository is a security-sensitive research prototype.

## Non-negotiable rules

- Never describe a passing matrix as proof of full correctness, security, causality, or novelty.
- Never bypass a failing test, path-classification error, publication check, or threat-model requirement to make CI green.
- Prefer deterministic checks over LLM judgment.
- Add a regression test for every bug fix.
- Keep the command runner shell-free.
- Do not introduce network access, telemetry, credentials, remote execution, or third-party data without explicit design review.
- Do not commit raw reports that may contain sensitive output.
- Update `THREAT_MODEL.md` whenever a change adds a trust assumption or execution capability.
- Preserve exit-code semantics: `0` supported in scope, `1` unsupported claim, `2` harness or configuration error.
- Disclose limitations, negative results, and material AI assistance.
- Use only owned, synthetic, licensed, or explicitly authorized research targets.
