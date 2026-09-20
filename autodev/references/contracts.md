# Define: the contract

Read during **Define** for optimization or contract-design questions. The contract supplies both gates.

## Contract fields

| Field | Required content |
|---|---|
| `goal` | One falsifiable outcome |
| `criterion` | One gate command and tests; optimization also specifies metric, direction, target, repeats, statistic, minimum improvement, noise calculation, tie-break |
| `budget` | Optimization: attempts and wall clock; development: none |
| `frozen` | Protected paths and measurement conditions |
| `surface` | Explicit editable paths, including new tests needed before Anchor |
| `reset` | Exact command restoring only this attempt's implementation changes |

Verify the command before confirmation. It must fail for a failed criterion; printing a number is not a verdict. Protect existing tests. Declare additive tests in Define, verify RED, then freeze them in Anchor. Changing the gate later requires a new confirmed contract, not an optimization attempt.

Ask only for missing inputs: usually none for development; at most ambiguous metric/target and absent budget for optimization. Offer choices, a recommendation, and a custom answer, never a mode question. Confirm all fields and limits once before Anchor.

## Choosing a metric

- Pick one number and direction; make other requirements correctness constraints.
- Normalize what varies: use model quality per byte, not per token, when vocabularies can change.
- Deterministic size/count: `repeats: 1`, noise `0`. Noisy latency/throughput/memory: fixed `repeats ≥ 5`, median, measured noise.
- Choose the noise calculation before Anchor. Require clean reproduction on the same machine.

For “faster homepage”, choose latency, interactivity, or shipped bytes by the bottleneck, not ease of improvement.

## Frozen inputs

Freeze whatever could be traded for the number: benchmark, tests, dataset, runner configuration, lockfile, and scenario-specific conditions.

| Scenario | Hold fixed | Prevents |
|---|---|---|
| Model training | training wall clock, machine, validation split | longer training or easier data |
| Page load | CPU quota, dataset, cache warm-up and cold/warm definition | more resources or warmer caches |
| Database queries | rows, index state, hardware, concurrency | different workloads |
| Build time | cores, concurrency, cache state | a different runner |
| Cost | request volume, traffic shape, price table | less work or different prices |
| Test runtime | suite, parallelism, machine | skipped work |
| Bundle size | build config, target browsers | dropped output |

Freeze time only when it defines the objective: “best model trainable in 300s”, not page latency. This measurement constraint is distinct from the overall optimization budget.

## Worked contracts

These examples assume a repository-provided `./gate` that tests and applies the comparison. Substitute a verified command, never assume this script exists.

Development:

```yaml
goal:      "export filtered transactions as CSV"
criterion: { command: "./gate", tests: "focused RED then GREEN; whole suite green" }
budget:    none
frozen:    ["existing tests", "test runner configuration"]
surface:   ["src/export/**", "new export tests before Anchor"]
reset:     "git checkout <accepted> -- src/export"
```

Optimization:

```yaml
goal: "API p95 below 200ms"
criterion:
  command:   "./gate"                            # assertion count may not drop
  metric:    { name: p95_ms, direction: lower, repeats: 5, statistic: median }
  noise:     "max absolute deviation from median, in ms"
  accept:    "improvement > max(5% of baseline, measured noise in ms)"
  target:    200
  tie_break: "smaller diff at equal metric during Prove"
budget:  { attempts: 15, wall_clock: "8m" }
frozen:  ["bench/**", "tests/**", "lockfile", "runner configuration"]
surface: ["src/api.py"]
reset:   "git checkout <accepted> -- src/api.py"
```

Resolve `<accepted>` to the last accepted commit. Plan explicitly for new implementation files: restoring tracked paths does not remove them. Preserve user changes and verified tests.

## Building a benchmark

No benchmark? Build it as development work before optimizing:

1. **RED:** observe a failing test that distinguishes a known worse case from a better one.
2. **GREEN:** implement the benchmark until that test passes.
3. Reproduce a known real difference; constant or random output is not proof.
4. Confirm the optimization contract, freeze the benchmark, then **Anchor** baseline and noise.

For docs/config, agree on a validator/schema-check exception rather than silently skipping TDD. A subjective refactor still needs a measurable goal, such as preserved behavior with lower complexity.
