# Clarify: performance optimization

Read for a performance goal, alongside the shared [Clarify](clarify.md) rules. One pass runs steps 1–3 in order; the human reviews the whole pass in step 4. Do not optimize during Clarify.

## 1. Prepare one numeric test

Prepare an executable benchmark, make explicit what it measures, and trial-run it to verify meaningful execution.

The test must be:

- **Quantifiable:** produce a finite numeric result with a named unit and an explicit improvement direction.
- **Single:** exactly one benchmark, or several benchmarks combined into one fixed weighted score. Component readings are diagnostics, not independent optimization targets.

Fix workload, input data, valid output, command, execution environment/cache conditions, repetition, aggregation, and treatment of measurement variability. The benchmark must perform the intended work and reject invalid results; a constant or fabricated score is not evidence.

For a composite benchmark, fix the formula before baseline:

```text
score = sum(weight_i * normalize_i(measurement_i))
```

Explain the weights, normalization, directions, and permitted trade-offs. Do not average away invalid output or choose weights after seeing which implementation wins.

## 2. Capture baseline

Run the prepared test on the unchanged implementation using the fixed conditions. Save the original numeric result, raw samples, aggregation, variability where relevant, and test/source identities. For a composite score, retain its component readings too.

This is the original baseline for the handoff chart. Later improvements must not overwrite it.

## 3. Propose the limits using the baseline

| Limit | Propose for the human's confirmation |
|---|---|
| Optimization target | Threshold on the one score, direction, and whether equality counts; reaching it permits early exit |
| Editable files | Explicit implementation paths the agent may change; benchmark, inputs, weights, and scoring logic remain outside this surface |
| Time budget | A wall-clock limit, loop start and deadline; include attempt measurements and reserve time for final verification |

Reuse values already supplied by the human, but do not silently invent missing permissions or an unlimited budget. State the proposal relative to the measured starting point.

## 4. Human review of the whole pass

Show the benchmark and its conditions, the baseline score with its samples, and the proposed target, editable files, and time budget, together. The human decides:

- **Revise:** apply the feedback and repeat from step 1. A changed benchmark, workload, or formula needs a new baseline before the next review.
- **Approve:** record the approved test, baseline, and limits, then enter Loop.

Record hashes or equivalent identities for the benchmark and measurement inputs. Changing the ruler, reducing work, or warming an undeclared cache is not an implementation improvement. A change in the approved measurement requires renewed Clarify and a new baseline.

Once approved, enter the do-while Loop with an optimization attempt, then evaluate the target and deadline after measurement and retention. A baseline that already meets the target does not bypass that first attempt. The approved wall-clock budget remains a hard limit.

**Exit:** the human has approved one complete pass — the executable test, its baseline, and the target, editable files, and time budget. Continue to [Loop: optimization](loop.md#performance-optimization).
