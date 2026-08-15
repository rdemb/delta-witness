# AI-Assisted Development Policy

AI tools may assist with implementation, tests, literature discovery, documentation, and review. Their output is not accepted as evidence by default.

## Maintainer responsibility

The human maintainer remains responsible for:

- the problem definition and public claims;
- understanding critical code paths and trust assumptions;
- reviewing generated changes;
- running and interpreting tests;
- deciding what can be published;
- vulnerability handling and coordinated disclosure;
- correcting or retracting unsupported statements.

## Required practice

Material AI assistance should be disclosed in pull-request descriptions when it affects design, code, tests, or research interpretation. Generated code must meet the same review and regression-test requirements as human-authored code.

No model output may be cited as independent confirmation of a result produced by the same model or agent workflow. Deterministic checks, primary sources, independent reproduction, or human review must carry the relevant evidentiary weight.

## No affiliation claim

Use of a commercial model, API, access program, or development tool does not imply sponsorship, certification, partnership, or endorsement of DeltaWitness by its provider.
