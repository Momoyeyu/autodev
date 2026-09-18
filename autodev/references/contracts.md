# Contracts

Read this when drafting a contract — that is, at Phase 0 of any run, and any time the improvement lane starts.

A contract has six fields: `goal`, `criterion`, `budget`, `frozen`, `surface`, `reset`. Three of them are easy to get wrong, so they get the detail here.

## Choosing the metric

The metric decides whether the loop can work at all. Get it wrong and the ratchet either accepts noise or optimizes something nobody wanted.

- **One scalar, one direction.** `p95_ms` lower, `requests_per_sec` higher, `bundle_kb` lower. Two metrics means one of them is a gate.
- **Normalized against what varies.** Model quality is measured per byte, not per token, so a vocabulary change stays comparable. Ask: if the agent changes the shape of the thing, does the number still mean the same thing?
- **Deterministic metrics need no repetition.** Bundle bytes, test count, binary size: `repeats: 1`, noise floor `0`.
- **Noisy metrics need a measured floor.** Latency, throughput, memory, anything timed: `repeats ≥ 5`, median statistic, and the floor measured in Phase 1 rather than assumed.
- **The metric must be reproducible by someone else** on the same machine from a clean checkout.

When the goal admits several metrics, offer the two or three that fit this codebase and mark a recommendation. "优化首页刷新速度" could mean any of:

| Candidate | Measures | Good when |
|---|---|---|
| `p95_ms` (navigation timing) | server + network + parse + paint | the page is slow to become usable |
| Time-to-interactive | main-thread work, hydration | the page paints fast but responds late |
| `bundle_kb` (gzipped) | shipped bytes | the payload is the suspected cause |

## Freezing the fungible resource

Freeze **whatever could be exchanged for a better measurement**. The test is simple: if changing it would make two attempts incomparable, it belongs in `frozen`.

| Scenario | Must be frozen | Is time part of it? |
|---|---|---|
| Model training | **Training wall clock** (e.g. 300s) | Yes — longer training wins otherwise |
| Page load speed | Machine and CPU quota, dataset, cache warm-up, cold/warm definition | **No** — measuring faster does not make a page faster |
| Database queries | Row counts, index state, hardware, concurrency | No |
| Build time | Core count, concurrency, cache state | No |
| Cost | Request volume, traffic shape, price table | No |
| Test runtime | Suite contents, parallelism, machine | No |

The model-training row is the one that proves the rule. There, the fixed budget *is* the objective: "the best model trainable in five minutes." Everything else on the list has no such property, and freezing the clock would be meaningless.

`frozen` normally includes, beyond the scenario-specific list:

- the benchmark or measurement harness itself
- the gate — the existing test suite and its runner config
- the dependency lockfile

## Worked contracts

Feature — correctness lane, no budget:

```yaml
goal:      "export a filtered transaction list as CSV"
criterion: { gate: "the new test fails, then passes; whole suite green" }
surface:   ["src/export/**", "tests/export/**"]
frozen:    ["tests/** (existing)", "vitest.config.ts"]
reset:     "git checkout <accepted> -- src/export"
```

Optimization — improvement lane:

```yaml
goal:      "GET / first paint p95 under 200ms"
criterion:
  gate:      ["npm test"]                        # assertion count may not decrease
  metric:    { name: p95_ms, direction: lower, repeats: 5, statistic: median }
  accept:    "metric < baseline - max(5%, noise_floor)"
  target:    200
  tie_break: "smaller diff wins at equal metric"
budget:    { attempts: 15, wall_clock: "8m" }
frozen:    ["bench/**", "tests/**", "package-lock.json", "vite.config.ts"]
surface:   ["src/home/**"]
reset:     "git checkout <accepted> -- src/home"
```

Model training — improvement lane where the clock is part of the objective:

```yaml
goal:      "lowest validation loss trainable in 300s on this machine"
criterion:
  gate:      ["run completes without crashing or producing NaN"]
  metric:    { name: val_loss, direction: lower, repeats: 1 }
budget:    { attempts: 100, wall_clock: "10h" }
frozen:    ["prepare.py", "validation split", "training time budget constant"]
surface:   ["train.py"]
reset:     "git checkout <accepted> -- train.py"
```

## Building the yardstick

When no measurement harness exists, Phase 0 spawns a sub-task to write one. That sub-task is "make something exist and work correctly", so it is pure correctness lane and runs under TDD like any other implementation work:

1. **RED** — write a test asserting the harness *discriminates*: a deliberately slow case must measure slower than a fast one. A benchmark that reports the same number for both is broken, and this test is the only thing that catches it.
2. **GREEN** — implement the harness until that test passes.
3. **Verify against reality** — confirm it reproduces a difference you already know exists, such as a before/after you measured by hand.
4. **Baseline** — only now measure the current state and record the noise floor.

A harness that has never been shown to discriminate is not a yardstick; it is a random number generator with good manners.

## Scenarios

The same two layers, recombined. No new mechanism for any of these.

| Scenario | Gate | Ratchet metric | Frozen |
|---|---|---|---|
| Feature | new test false → true, suite green | — | existing suite |
| Bug fix | reproduction test false → true | — | the reproduction test |
| Refactor | behavior suite green | complexity ↓ / coverage ↑ | behavior spec |
| Performance | suite green | p95 ↓ | bench script, dataset, hardware |
| Build time | suite green | build seconds ↓ | core count, concurrency, cache state |
| Bundle size | suite green | bytes ↓ | build config, target browsers |
| Cost | suite green | $/request ↓ | traffic shape, price table |
| Model quality | no crash, no NaN | val loss ↓ | training harness, validation set, **time budget** |
| Docs / config | validator or schema check passes | — | the validator |
