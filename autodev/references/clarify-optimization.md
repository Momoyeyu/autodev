# Clarify: performance optimization

Read for a performance goal, alongside the shared [Clarify](clarify.md) rules. The target of this scenario is a **numeric score reaching an agreed threshold**. One pass runs steps 1–3 in order; the human reviews the whole pass in step 4. Do not optimize during Clarify.

## 1. Prepare the benchmark

Prepare an executable benchmark, make explicit what it measures, and trial-run it to verify meaningful execution.

The benchmark must be:

- **Quantifiable:** produce a finite numeric result with a named unit and an explicit improvement direction.
- **Single:** exactly one benchmark, or several benchmarks combined into one fixed weighted score. Component readings are diagnostics, not independent optimization targets.

Fix workload, input data, valid output, command, execution environment/cache conditions, repetition, aggregation, and treatment of measurement variability. The benchmark must perform the intended work and reject invalid results; a constant or fabricated score is not evidence.

For a composite benchmark, fix the formula before baseline:

```text
score = sum(weight_i * normalize_i(measurement_i))
```

Explain the weights, normalization, directions, and permitted trade-offs. Do not average away invalid output or choose weights after seeing which implementation wins.

## 2. Capture baseline

Run the prepared benchmark on the unchanged implementation using the fixed conditions. Save the original numeric result, raw samples, aggregation, variability where relevant, and benchmark/source identities. For a composite score, retain its component readings too.

This is the original baseline for the handoff chart. Later improvements must not overwrite it.

## 3. Propose the limits using the baseline

| Limit | Propose for the human's confirmation |
|---|---|
| Optimization target | Threshold on the one score and whether equality counts, taken from how the human phrased it; reaching it permits early exit |
| Editable files | Explicit implementation paths the agent may change; benchmark, inputs, weights, and scoring logic remain outside this surface |
| Time budget | A mandatory wall-clock limit (`--budget-minutes`); `--reserve-minutes` marks its tail, during which `attempt` refuses new runs so `verify` and Handoff fit inside the budget |

Reuse values already supplied by the human, but do not silently invent missing permissions or an unlimited budget. State the proposal relative to the measured starting point.

Write the proposal as a contract with the judge script, from the user's checkout, into a directory outside the repository (pass `--home` as an absolute path; every later command uses the same value):

```bash
python3 <skill>/scripts/autodev_verify.py --home ../<repo>.autodev init \
  --scenario optimization --editable src/api \
  --frozen bench/ --test-cmd "python bench/run.py" \
  --score-regex "p95=([0-9.]+)" --unit ms --direction lower \
  --delta-pct 5 --target 200 --exclusive --budget-minutes 20 --reserve-minutes 3
```

`init` runs the benchmark once more to record the baseline and its raw output, converts `δ`, hashes the frozen paths, and prints the contract. That printed contract is what the human reviews in step 4; the same fields drive every Loop verdict, so nothing agreed here depends on the agent remembering it.

Bind both Loop comparisons to the approved `direction`. `best` is the retained best verified score and starts at baseline; `δ` is the improvement margin:

| direction | Attempt is accepted | Target is met |
|---|---|---|
| lower | `score < best - δ` | `score ≤ target`, or `score < target` if the human excluded equality |
| higher | `score > best + δ` | `score ≥ target`, or `score > target` if the human excluded equality |

Acceptance compares with `best`, not baseline, so a retained result is never replaced by a worse one. Fix `δ` in the score's unit before Loop: `--delta-pct` converts once against baseline, `δ = pct × |baseline|`, and is not recomputed against later `best` values; `--delta` gives it directly, for example as an agreed noise floor. Read equality from the human's wording — "at least 90%" includes 90%, "below 100 ms" excludes 100 ms (`--exclusive`) — and record the choice; do not default it.

Examples: latency baseline 200 ms, `δ` 10 ms, lower — 180 ms is accepted, 220 ms is rejected, and a later 185 ms is rejected because `best` is already 180 ms. Throughput target "at least 1000 req/s", higher — 800 req/s has not met the target; 1000 req/s has.

## 4. Human review of the whole pass

Show the benchmark and its conditions, the baseline score with its samples, and the proposed target, editable files, and time budget, together. The human decides:

- **Revise:** apply the feedback and repeat from step 1. A changed benchmark, workload, or formula needs a new baseline before the next review; rerun `init --renew`, which archives the previous contract.
- **Approve:** record the approved benchmark, baseline, and limits, then enter Loop.

Record hashes or equivalent identities for the benchmark and measurement inputs. Changing the ruler, reducing work, or warming an undeclared cache is not an implementation improvement. A change in the approved measurement requires renewed Clarify and a new baseline.

Once approved, enter the do-while Loop with an optimization attempt, then evaluate the target and deadline after measurement and retention. A baseline that already meets the target does not bypass that first attempt. The approved wall-clock budget remains a hard limit.

**Exit:** the human has approved one complete pass — the executable benchmark, its baseline, and the target, editable files, and time budget. Continue to [Loop: optimization](loop.md#performance-optimization).
