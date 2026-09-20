# Test design

Read from Define only when acceptance cases or a composite benchmark need more detail. This supports the four stages; it is not a separate workflow or an implementation checklist.

## Feature development

A test is a shared statement of intended behavior, not a screenshot of the current implementation. Give every approved case a stable ID and an observable outcome.

| Field | Question it answers |
|---|---|
| Requirement | Which human expectation does this case represent? |
| Starting state and input | What data, permissions, and preconditions apply? |
| Action | What operation or user interaction is performed? |
| Expected outcome | What returned value, state change, visible behavior, or error proves acceptance? |
| Preserved behavior | Which existing interaction or invariant must remain unchanged? |

For a filtered export feature, useful cases may cover honoring the filter, escaping special characters, empty results, denied access, and preservation of the existing list flow. These are design examples, not required cases for every project or claimed test results.

Cover happy paths, meaningful boundaries, and failures the human cares about. Avoid tests that merely assert a mock was called, duplicate implementation details, or always pass. When doubles are necessary, preserve the dependency behavior the case actually exercises.

Agree on behavior before reconciling existing tests in Anchor. An obsolete expectation can be removed when the approved requirement supersedes it; an inconvenient failure or low pass rate is not a reason. Neither test count nor a universal coverage threshold replaces the human-approved acceptance set.

## Performance optimization

The test must produce exactly one finite numeric score. Agree on the unit, improvement direction, workload, valid output, execution conditions, and aggregation before taking the baseline.

### One benchmark

Examples include latency in milliseconds, throughput in items/second, peak memory in bytes, or built artifact size in bytes. Choose what represents the user's objective, not what happens to be easiest to reduce.

The benchmark must perform the intended work and reject invalid results before emitting a score. Result validation is part of that one test, not another scored objective. Fix the repeat count and aggregation; do not select whichever run makes a candidate look best.

### A weighted sum

When several measurements represent the objective, expose one score:

```text
score = sum(weight_i * normalize_i(measurement_i))
```

Agree on the components, nonnegative weights, normalization constants, and direction. For a weighted average, weights sum to one. Normalize incompatible units and align directions before adding; never change the formula between baseline and final measurement.

An illustrative lower-is-better score is:

```text
score = 0.7 * (p95_ms / 200) + 0.3 * (peak_memory_mib / 100)
```

The constants and weights are examples to review with the human, not defaults. This score explicitly permits trade-offs between latency and memory. Non-negotiable valid-output requirements must not be averaged away by a faster component.

Retain component readings as diagnostics, but use only the one score for optimization's target and comparisons. Confirm the numeric target, editable files, and time budget after measuring the baseline in Anchor.

## Review until confirmed

Show concrete cases or formulas and explain their blind spots and trade-offs. Revise them with the human until explicitly approved. Reuse decisions already supplied; do not impose a fixed question count or treat silence as agreement.
