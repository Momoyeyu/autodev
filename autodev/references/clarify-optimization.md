# Clarify: performance optimization

Read for a performance goal, alongside the shared [Clarify](clarify.md) rules. The order is test agreement, baseline, then execution limits.

## 1. Co-create one numeric test until the human confirms

Prepare an executable benchmark with the human, show what it measures, run it to verify meaningful execution, and revise until the human approves it.

The test must be:

- **Quantifiable:** produce a finite numeric result with a named unit and an explicit improvement direction.
- **Single:** exactly one benchmark, or several benchmarks combined into one fixed weighted score. Component readings are diagnostics, not independent optimization targets.

Agree on workload, input data, valid output, command, execution environment/cache conditions, repetition, aggregation, and treatment of measurement variability. The benchmark must perform the intended work and reject invalid results; a constant or fabricated score is not evidence.

For a composite benchmark, fix the formula before baseline:

```text
score = sum(weight_i * normalize_i(measurement_i))
```

Explain the weights, normalization, directions, and permitted trade-offs. Do not average away invalid output or choose weights after seeing which implementation wins. Preparation and trial execution belong to this human review, not to the optimization loop.

## 2. Capture baseline

Run the confirmed test on the unchanged implementation using the agreed conditions. Save the original numeric result, raw samples, aggregation, variability where relevant, and test/source identities. For a composite score, retain its component readings too.

This is the original baseline for the handoff chart. Later improvements must not overwrite it.

## 3. Confirm the limits using the baseline

| Limit | Required agreement |
|---|---|
| Optimization target | Threshold on the one score, direction, and whether equality counts; reaching it permits early exit |
| Editable files | Explicit implementation paths the agent may change; benchmark, inputs, weights, and scoring logic remain outside this surface |
| Time budget | A wall-clock limit, loop start and deadline; include attempt measurements and reserve time for final verification |

Reuse values already supplied by the human, but do not silently invent missing permissions or an unlimited budget. Confirm the limits against the measured starting point before entering Loop.

Record hashes or equivalent identities for the benchmark and measurement inputs. Changing the ruler, reducing work, or warming an undeclared cache is not an implementation improvement. A change in the agreed measurement requires renewed Clarify and a new baseline.

If baseline already meets the confirmed target, no optimization attempt is necessary. Handoff still requires a chart that honestly shows the baseline result and zero attempts; do not invent a trajectory.

**Exit:** one executable test is approved, baseline is recorded, and target, editable files, and time budget are confirmed. Continue to [Loop: optimization](loop.md#performance-optimization).
