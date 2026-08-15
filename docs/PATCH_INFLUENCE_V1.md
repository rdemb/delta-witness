# Exact Patch Influence v1

## Status

This document specifies the experimental `deltawitness.patch-influence.v1` analysis introduced in DeltaWitness `0.0.3`.

The analysis measures how changed code paths influence one declared software-change witness under exact, controlled Git interventions. It does not establish full program correctness, semantic intent, vulnerability removal, production safety, or universal causality.

## Preconditions

Exact patch influence runs only after the canonical four-state matrix completes and supports every claim with this expectation pattern:

```text
base_base            pass
base_candidate       fail
candidate_base       pass
candidate_candidate  pass
```

The current protocol additionally requires:

- one base commit and one descendant candidate commit;
- a clean repository;
- at least one changed path classified as code;
- no more than eight changed code paths;
- at least one changed path classified as tests;
- every changed path classified exactly once as code, tests, or documentation;
- no changed submodule or symbolic-link entry;
- explicit command and observer semantics for every claim.

If any precondition fails, no influence report is produced.

## Intervention units

Let the deterministic sorted changed-code path order be:

```text
N = [p0, p1, ..., p(n-1)]
```

Each path is one intervention unit. A coalition is represented by an integer mask `m` in `[0, 2^n - 1]`. Path `pi` is selected when bit `i` is set.

The current unit is a complete Git path, not a hunk, function, statement, AST node, dependency edge, or semantic feature. Attribution therefore depends on path grouping.

## Controlled state construction

For every coalition `S ⊆ N`, DeltaWitness constructs two exact states.

### Base-test state

```text
base implementation-side tree
+ candidate documentation changes held constant
+ candidate versions of code paths in S
+ base tests
```

### Candidate-test state

```text
same intervened implementation-side tree
+ candidate tests
```

Every state receives an exact tree ID and either an endpoint commit ID or a deterministic synthetic commit ID. The command observer is bound to the exact claim, command, specification, state, tree, and commit.

Candidate documentation changes are held constant so the full coalition reproduces the final candidate tree. Because paths classified as documentation may still affect execution, endpoint anchors are mandatory.

## Coalition predicate

For one claim, a coalition is supported only when both states produce a valid `pass` observation:

```text
base tests on intervened implementation       -> pass
candidate tests on intervened implementation  -> pass
```

For multiple claims, every claim must satisfy both observations.

The coalition status is:

| Status | Definition |
|---|---|
| `supported` | Every claim produces a valid pass under both test worlds |
| `unsupported` | Execution is complete and at least one claim produces a valid fail |
| `indeterminate` | Any timeout, missing or malformed receipt, import/setup/infrastructure error, unknown exit code, or other incomplete observation occurs |

`indeterminate` is not converted to `unsupported`. Incomplete execution is not negative evidence.

## Endpoint anchors

The exact table is interpreted only when four anchors remain consistent with the canonical matrix:

| Influence endpoint | Canonical matrix state |
|---|---|
| Empty coalition under base tests | `base_base` |
| Empty coalition under candidate tests | `base_candidate` |
| Full coalition under base tests | `candidate_base` |
| Full coalition under candidate tests | `candidate_candidate` |

Outcome signatures compare:

- observed semantic class;
- process return code;
- timeout status;
- observer protocol;
- typed receipt outcome;
- receipt producer identity;
- aggregate receipt counts;
- stable observation error.

The two full-coalition trees must exactly match the canonical candidate-side trees. Empty-coalition tree equality is required when there are no candidate documentation changes. When candidate documentation changes exist, empty tree equality is not expected, but semantic outcomes must still match.

Any anchor inconsistency withholds all exact attribution metrics.

## Exact enumeration

The current implementation evaluates every coalition:

```text
coalitions = 2^n
command observations = 2 * claims * 2^n
```

The canonical four-state matrix runs before this table.

The hard cap is eight code paths:

```text
2^8 = 256 coalitions
```

No sampling, pruning, monotonicity assumption, surrogate model, or model-generated importance estimate is used in v1.

## Boolean witness game

When every coalition is complete and anchors are consistent, define:

```text
f(S) = 1  when coalition S is supported
f(S) = 0  when coalition S is unsupported
```

The table is not created when any coalition is indeterminate.

The protocol requires:

```text
f(empty) = 0
f(full)  = 1
```

Otherwise the attribution is degenerate and no metric is released.

## Inclusion-minimal witness-sufficient coalitions

A supported coalition `S` is inclusion-minimal when no proper subset is supported:

```text
f(S) = 1
and
for every T proper subset of S: f(T) = 0
```

The exact table permits reporting every such coalition rather than one order-dependent result.

A path may therefore be:

- present in every supported coalition;
- present in some but not all minimal coalitions;
- absent from every minimal coalition;
- locally necessary only in the full coalition;
- individually sufficient;
- influential only through interaction.

## Full-context necessity

Path `i` is full-context necessary when removing it from the complete candidate makes the witness unsupported:

```text
f(N) = 1
and
f(N without i) = 0
```

This is a leave-one-path-out result in the context of every other candidate path. It is not global necessity when alternative coalitions exist.

## Global necessity

Path `i` is globally necessary for the exact witness table when every supported coalition contains it:

```text
for every S with f(S) = 1: i belongs to S
```

This claim is bounded to the enumerated path units, tests, observers, and environment.

## Standalone sufficiency

Path `i` is standalone sufficient when:

```text
f({i}) = 1
```

This does not mean the path is a complete production patch. It means that, with candidate documentation held constant and under the declared test worlds, that one candidate path is sufficient for the Boolean witness.

## Marginal swings

For every coalition not containing path `i`, the exact marginal is:

```text
Delta_i(S) = f(S union {i}) - f(S)
```

A positive swing is `+1`. A negative swing is `-1`.

Negative swings are retained rather than forced to zero. They can reveal antagonistic, compensating, or non-monotonic behavior.

## Shapley allocation

The exact Shapley allocation for path `i` is:

```text
phi_i = sum over S subset of N without i
        [ |S|! * (n-|S|-1)! / n! ]
        * [ f(S union {i}) - f(S) ]
```

DeltaWitness computes this value with rational arithmetic and serializes numerator, denominator, and a rounded decimal rendering.

For a complete exact game, the efficiency property is checked:

```text
sum_i phi_i = f(N) - f(empty)
```

The report includes the exact residual. A nonzero residual indicates an implementation or report-integrity defect.

The Shapley value allocates the endpoint change across the chosen path units. It does not establish legal responsibility, author contribution, semantic correctness, or universal code importance.

## Normalized Banzhaf influence

For path `i`:

```text
beta_i = (1 / 2^(n-1))
         * sum over S subset of N without i
         [ f(S union {i}) - f(S) ]
```

This is the mean signed marginal effect under uniformly weighted coalitions. It can be negative.

## Pairwise Banzhaf interaction

For paths `i` and `j`:

```text
I_ij = (1 / 2^(n-2))
       * sum over S subset of N without i,j
       [ f(S union {i,j})
         - f(S union {i})
         - f(S union {j})
         + f(S) ]
```

A positive value indicates positive interaction in the declared witness game. A negative value can indicate substitutability, redundancy, or antagonism. Interpretation requires the full coalition table and domain review.

## Monotonicity

The protocol does not assume that adding a candidate path can only improve the witness.

The report marks the game as monotone non-decreasing only when there is no edge:

```text
f(S) = 1
and
f(S union {i}) = 0
```

All negative edges are counted through path marginal swings.

## Integrity model

The report includes:

- `influence_sha256`: a digest over stable semantic inputs, exact Git identities, observer evidence, anchors, coalition statuses, and metrics;
- `report_sha256`: a digest over the complete report document with its own field normalized to `null`.

`deltawitness verify-report` recalculates both values.

The digests are unkeyed. They detect modification only when compared with a separately trusted expected value. They do not authenticate the producer. Signing and standard attestations remain future work.

## Privacy boundary

The report does not include source code or raw command output by default. It does include:

- changed repository paths;
- command arrays;
- claim descriptions;
- exact commit and tree IDs;
- process and receipt metadata;
- output digests;
- coalition structure and metrics.

Every exported report must be reviewed before publication. Command arguments must not contain secrets.

## Computational and operational risks

Exact enumeration multiplies execution. At eight paths and one claim, coalition analysis can invoke up to 512 test commands after the initial matrix.

The current runner is not a sandbox. Every coalition command can access the filesystem and network using the current operating-system user's permissions. Run trusted code only, or use a separately secured disposable environment without production credentials.

Synthetic intervention states may be invalid even when both endpoints are valid. Such failures remain `indeterminate` and withhold exact attribution.

## Prior-art boundary

Delta debugging already provides systematic methods for isolating failure-inducing inputs and changes. The foundational work includes:

- Andreas Zeller and Ralf Hildebrandt, "Simplifying and Isolating Failure-Inducing Input," IEEE Transactions on Software Engineering, 2002: https://doi.org/10.1109/32.988498
- Holger Cleve and Andreas Zeller, "Locating Causes of Program Failures," ICSE 2005: https://doi.org/10.1145/1062455.1062522

Patch minimization, automated program repair assessment, mutation testing, program slicing, and cooperative-game attribution are also established areas.

DeltaWitness currently claims only an implementation-backed research hypothesis: exact Git-native path interventions, two test worlds, typed outcome semantics, endpoint anchors, non-monotonic coalition metrics, and integrity-verifiable reports may provide useful evidence for agent-authored patches.

Scientific novelty and empirical superiority have not been established.

## Non-claims

Exact Patch Influence v1 does not establish that:

- the patch is correct, secure, complete, or minimal;
- tests cover the intended production behavior;
- the observer or test adapter is honest;
- the execution environment is reproducible or contained;
- file paths are the correct semantic units;
- a zero influence value proves that code is useless outside the witness;
- a high influence value proves that code is desirable;
- a positive interaction identifies one human-understandable mechanism;
- results transfer to another test suite, environment, patch grouping, or deployment.

## Falsification and redesign criteria

The protocol should be narrowed, redesigned, or removed if:

- invalid intermediate states dominate realistic patches;
- exact path grouping yields unstable or misleading attribution;
- incomplete coalition tables are too common to support useful metrics;
- the cost is not justified by incremental findings;
- equivalent refactorings produce materially incompatible conclusions;
- existing methods provide the same evidence more rigorously;
- external operators cannot reproduce the state construction or metrics.
