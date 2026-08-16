# DW-001 Claim-Scoped Mutation Result v1

**Status:** development-only owned-synthetic calibration result. The plan and catalog are frozen; the result runner executes only those exact inputs. This is not a mutation-adequacy result, ecological coding-agent evaluation, merge policy, holdout, protocol freeze, or production-safety claim.

## 1. Question

PR #38 froze one minimal outcome-blind Python mutation design before any mutation-test result:

```text
plan_id         = DW-001-CLAIM-SCOPED-MUTATION-PLAN-V1
plan_sha256     = 0ebf64e1de76849050c86d8a4d53d72d8067561ab48b4bd5a4083495dc99fe37
catalog_sha256  = 7b3e405bd3893f532c0ccfa16e9cc208422bbdd20dfe82a002c99342a04201c0
operator_set_id = python-boolean-predicate-minimal-v1
```

The result layer asks:

> Under the exact frozen source, target, mutants, selectors, and reference checks, do the strong authorization profile and weak Boolean-proxy profile produce different typed outcomes, and can every expected or unexpected result be retained without replacing the complete table with a scalar score?

## 2. Fixed execution population

The runner executes five implementation identities:

1. the unmutated candidate baseline;
2. `return-constant-false-v1`;
3. `return-constant-true-v1`;
4. `comparison-eq-to-ne-v1`;
5. the separately labeled historical control `nonempty-role-boolean-v1` from PR #34.

The historical control remains excluded from generic-operator generalization.

Three generation-only catalog records remain visible but never execute:

```text
duplicate       -> not_executed_duplicate
not_applicable  -> not_executed_not_applicable
invalid         -> not_executed_invalid
```

They cannot enter killed, survived, or indeterminate execution denominators.

## 3. Frozen selector profiles

### Strong authorization profile

```text
test_access.AccessTests.test_admin_is_allowed
test_access.AccessTests.test_viewer_is_denied
```

### Weak Boolean-proxy profile

```text
test_access.AccessTests.test_viewer_result_is_boolean
```

### Reference development claim checks

```text
test_hidden_claim.HiddenClaimTests.test_admin_is_allowed
test_hidden_claim.HiddenClaimTests.test_viewer_is_denied
```

The reference checks are fixed development controls. They are not a complete, independent, or ecological oracle.

## 4. Execution contract

Every executed implementation runs exactly five selectors:

```text
2 strong-profile selectors
1 weak-profile selector
2 reference selectors
```

The complete fixed run therefore contains:

```text
5 implementations × 5 selectors = 25 typed commands
```

Every selector executes shell-free through `outcome-receipt-v1`. The invocation binding covers:

- result, plan, and catalog identities;
- implementation identity;
- profile and selector identity;
- exact command;
- source and test SHA-256;
- observer and producer identity.

A normal `pass` or `fail` requires receipt/process agreement. Error or timeout evidence is retained as incomplete and takes precedence over killed/survived interpretation.

## 5. Expected and observed evidence are separate

The artifact stores, for every selector:

```text
expected_observed
observed
concordant
```

Every profile and reference group stores:

```text
expected_outcome
outcome
concordant
```

Every executed implementation stores record-level `concordant`.

This distinction is normative:

```text
complete unexpected observation
    != malformed evidence
    != harness failure
```

A complete typed observation that diverges from preregistration remains a valid negative result. The artifact sets:

```text
analysis.status = unexpected
```

and retains the exact observation, derived profile/reference outcomes, changed summary, and affected record IDs.

Malformed structure, source substitution, wrong commands or selectors, invalid bindings, inconsistent receipts, impossible stored aggregates, NaN or infinite costs, or recomputed-digest tampering still fail closed.

## 6. Predeclared expected table

### Candidate baseline

```text
strong profile   = baseline_passed
weak profile     = baseline_passed
reference checks = reference_passed
```

### `return-constant-false-v1`

```text
strong selectors = fail / pass
weak selector    = pass
reference checks = fail / pass

strong profile   = killed
weak profile     = survived
reference        = claim_violation_observed
```

### `return-constant-true-v1`

```text
strong selectors = pass / fail
weak selector    = pass
reference checks = pass / fail

strong profile   = killed
weak profile     = survived
reference        = claim_violation_observed
```

### `comparison-eq-to-ne-v1`

```text
strong selectors = fail / fail
weak selector    = pass
reference checks = fail / fail

strong profile   = killed
weak profile     = survived
reference        = claim_violation_observed
```

### Historical `nonempty-role-boolean-v1`

```text
strong selectors = pass / fail
weak selector    = pass
reference checks = pass / fail

strong profile   = killed
weak profile     = survived
reference        = claim_violation_observed
```

The historical-control outcomes overlap PR #34 evidence and do not count as independent generic-operator evidence.

## 7. Summary and analysis

The result retains the complete table and derives counts such as:

- candidate baseline validity;
- generic strong-profile killed, survived, and indeterminate counts;
- generic weak-profile killed, survived, and indeterminate counts;
- reference claim violations observed;
- unexpected observation, profile, reference, and record counts.

The following remain fixed:

```text
mutation_score                         = null
headline_score                         = null
universal_threshold                    = null
merge_blocker_authorized               = false
ecological_inference_allowed           = false
holdout_selected                       = false
primary_denominator_eligible           = false
generic_operator_generalization_allowed = false
```

A scalar may not replace the per-mutant table or hide surviving claim-violating mutants, invalid records, not-applicable records, or incomplete execution.

## 8. Integrity model

The result has two unkeyed digests.

### `semantic_sha256`

Binds stable evidence while normalizing:

- creation time;
- runtime metadata;
- wall-clock and CPU timing;
- per-command durations;
- stdout and stderr digests.

It retains source, plan, catalog, selector, command, binding, receipt, observed outcome, expected outcome, concordance, analysis, summary, and policy semantics.

### `report_sha256`

Binds the complete document, including runtime and cost diagnostics.

The verifier independently recomputes:

- exact plan and catalog relations;
- record order and role;
- source, AST, target, operator, and mutant identities;
- selector commands and invocation bindings;
- typed pass/fail consistency;
- profile, reference, record, summary, and analysis derivations;
- non-execution status for generation-only records;
- denominator and policy fields;
- semantic and complete-report digests.

Recomputing both digests cannot make a source, selector, command, binding, receipt, outcome, aggregate, score, policy, or denominator substitution valid.

The digests do not authenticate a producer. An actor able to replace the complete trusted source and expected-digest chain can replace the evidence chain.

## 9. Security and privacy boundary

The runner executes only fixed project-owned Python source and test bytes in disposable temporary directories.

It adds no:

- external repository or benchmark execution;
- network access;
- package-manager or third-party mutation-engine invocation;
- upload or telemetry;
- secret or new repository permission;
- remote execution service;
- containment claim.

The host Python runtime, operating system, filesystem, process environment, and unittest adapter remain trusted. The runner is not a sandbox.

Public artifacts omit:

- source, mutant, and test bodies;
- raw stdout, stderr, and tracebacks;
- absolute temporary paths;
- usernames, credentials, and environment values;
- private endpoints and private prompts.

Selectors, commands, source/test digests, invocation bindings, receipt metadata, mutant identities, outcomes, and costs remain publication metadata requiring review.

## 10. Prior-art boundary

Mutation testing, selective mutation, equivalent-mutant analysis, mutation scores, test adequacy, and Python mutation engines are established. Direct implementation baselines remain mutmut and Cosmic Ray, together with fixed-mutant and coverage-only comparisons.

No novelty claim is made for killing mutants, retaining surviving mutants, using AST transformations, comparing test profiles, or recording typed test results.

The narrower DeltaWitness contribution under evaluation is the integration of a predeclared mutation design and complete expected-or-unexpected typed result table into the existing Git-native, selector-localized, integrity-verifiable evidence chain.

Whether this integration provides useful evidence beyond simpler baselines remains unestablished.

## 11. Falsification and redesign

Narrow or abandon this layer if:

- complete unexpected observations cannot be retained without being treated as harness errors;
- malformed or contradictory evidence is accepted as a negative result;
- Python 3.11–3.14 disagree on stable semantic outcomes;
- generation-only records leak into execution denominators;
- the candidate baseline is invalid;
- errors or timeouts are counted as killed;
- the historical control is treated as generic evidence;
- summaries can drift from the complete table;
- a scalar hides surviving claim violations;
- a simpler fixed table or direct baseline provides the same guarantees at lower complexity.

Unexpected outcomes are results. They must not trigger post-result changes to operators, selectors, reference checks, expected labels, or denominators without a recorded deviation.

## 12. Claim boundary

A valid result establishes only the typed selector outcomes, derived profile/reference classifications, concordance, and measured execution costs of the exact frozen owned-synthetic population.

It does not establish:

- complete oracle relevance or strength;
- mutation adequacy or mutation-score validity;
- equivalence of arbitrary mutants;
- representativeness of the three generic operators;
- prevalence among real coding agents;
- ecological effectiveness or superiority;
- authorization to block merges or execute external repositories;
- containment, producer authentication, protocol freeze, holdout validity, independent reproduction, Gate 0 or Gate 1 completion;
- production readiness or scientific novelty.
