# Contracts

Read this during Define when drafting the contract, and any time an optimization starts.

A contract has six fields: `goal`, `criterion`, `budget`, `frozen`, `surface`, `reset`. Three of them are easy to get wrong, which is why they get the detail here.

## Choosing the metric

The metric decides whether the ratchet can work at all. Choose badly and it either chases noise or optimizes something nobody wanted.

- **One number, one direction.** `p95_ms` lower, `requests_per_sec` higher, `bundle_kb` lower. Two metrics means one of them is really a test.
- **Normalize against what varies.** Model quality is measured per byte rather than per token, so a vocabulary change stays comparable. Ask: if the agent changes the shape of the thing, does the number still mean the same thing?
- **Deterministic metrics need no repetition.** Bundle bytes, test count, binary size: `repeats: 1`, noise `0`.
- **Noisy metrics need measured noise.** Latency, throughput, memory, anything timed: `repeats ≥ 5`, median, and the noise measured during Anchor rather than assumed.
- **Someone else must be able to reproduce it** on the same machine from a clean checkout.

When the request admits several metrics, offer the two or three that fit the codebase and mark a recommendation. "优化首页刷新速度" could mean any of:

| Candidate | What it measures | Pick it when |
|---|---|---|
| `p95_ms` (navigation timing) | server + network + parse + paint | the page takes too long to become usable |
| Time to interactive | main-thread work, hydration | the page paints fast but responds late |
| `bundle_kb` (gzipped) | shipped bytes | the payload is the suspected cause |

## Freezing what could be traded for the number

Freeze the things that, if changed, would make two attempts incomparable.

| Scenario | Must be frozen | Is the clock part of it? |
|---|---|---|
| Model training | **Training wall clock** (e.g. 300s) | Yes — training longer wins otherwise |
| Page load | Machine and CPU quota, dataset, cache warm-up, cold/warm definition | **No** — measuring faster doesn't make a page faster |
| Database queries | Row counts, index state, hardware, concurrency | No |
| Build time | Core count, concurrency, cache state | No |
| Cost | Request volume, traffic shape, price table | No |
| Test runtime | Suite contents, parallelism, machine | No |

The model-training row is the one that proves the rule: there, the fixed budget *is* the objective — "the best model trainable in five minutes." Nothing else on the list works that way, and freezing the clock for a web page would be meaningless.

Beyond the scenario-specific list, `frozen` normally includes:

- the benchmark itself
- the tests and their runner config
- the dependency lockfile

## Worked contracts

Feature — development mode, no budget:

```yaml
goal:      "export a filtered transaction list as CSV"
criterion: { tests: "the new test fails, then passes; whole suite green" }
frozen:    ["tests/** (existing)", "vitest.config.ts"]
surface:   ["src/export/**", "tests/export/**"]
reset:     "git checkout <accepted> -- src/export"
```

Optimization:

```yaml
goal:      "GET / first paint p95 under 200ms"
criterion:
  tests:     ["npm test"]                        # assertion count may not drop
  metric:    { name: p95_ms, direction: lower, repeats: 5, statistic: median }
  accept:    "metric < baseline - max(5%, noise)"
  target:    200
  tie_break: "smaller diff wins at equal metric"
budget:    { attempts: 15, wall_clock: "8m" }
frozen:    ["bench/**", "tests/**", "package-lock.json", "vite.config.ts"]
surface:   ["src/home/**"]
reset:     "git checkout <accepted> -- src/home"
```

Model training — the case where the clock is part of the objective:

```yaml
goal:      "lowest validation loss trainable in 300s on this machine"
criterion:
  tests:     ["run completes without crashing or producing NaN"]
  metric:    { name: val_loss, direction: lower, repeats: 1 }
budget:    { attempts: 100, wall_clock: "10h" }
frozen:    ["prepare.py", "validation split", "training time budget constant"]
surface:   ["train.py"]
reset:     "git checkout <accepted> -- train.py"
```

## Building the benchmark

When no benchmark exists, Define spawns a task to write one. That is "make something exist and work correctly", so it runs under TDD like any other implementation work:

1. **RED** — write a test asserting the benchmark *discriminates*: a deliberately slow case must measure slower than a fast one. A benchmark that reports the same number for both is broken, and this test is the only thing that catches it.
2. **GREEN** — implement the benchmark until that test passes.
3. **Check it against reality** — confirm it reproduces a difference you already know exists, such as a before/after you measured by hand.
4. **Anchor** — only now measure the current state and record the baseline and noise.

A benchmark that has never been shown to tell two cases apart is not a benchmark. It is a random number generator with good manners.

## Scenarios

The same two layers, recombined. No new machinery for any of these.

| Scenario | Tests | Metric | Frozen |
|---|---|---|---|
| Feature | new test fails → passes, suite green | — | existing suite |
| Bug fix | reproduction test fails → passes | — | the reproduction test |
| Refactor | behavior suite green | complexity ↓ / coverage ↑ | behavior spec |
| Performance | suite green | p95 ↓ | bench script, dataset, hardware |
| Build time | suite green | build seconds ↓ | core count, concurrency, cache state |
| Bundle size | suite green | bytes ↓ | build config, target browsers |
| Cost | suite green | $/request ↓ | traffic shape, price table |
| Model quality | no crash, no NaN | val loss ↓ | harness, validation set, **time budget** |
| Docs / config | validator or schema check passes | — | the validator |
