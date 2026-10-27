# Performance optimization

Optimize an observed workload, not a score detached from useful work. Keep the original baseline and make each experiment answer a concrete hypothesis.

## Establish a useful comparison

- Identify the primary metric, unit, improvement direction, and correctness constraints. Record secondary effects such as memory or tail latency when they matter. Reuse an existing benchmark where possible.
- Fix the workload, inputs, command, environment, cache/warmup conditions, repetitions, and aggregation. Check that the workload does the intended work and validates its output.
- Measure the unchanged implementation. Keep raw samples and enough source/configuration information to reproduce them. Repeat as needed to understand variability; two readings alone do not guarantee a reliable noise bound.
- Reuse the user's target and resource limits. For an open-ended search, propose a bounded time/attempt budget before expensive work. A small comparison need not acquire a formal target or a new approval step. If the baseline already satisfies the requested goal, report it rather than forcing an unnecessary attempt.

## Iterate with evidence

For each attempt, state the hypothesis, make a coherent change, check correctness, and measure under comparable conditions. Retain improvements supported by the measurements; restore only your own rejected changes using a method appropriate to the project. Git is optional. Do not discard unrelated work.

Keep a lightweight record of the change, samples/result, validity, and retention decision. Include rejected ideas, compile failures, crashes, and timeouts. Invalid or unavailable runs have no fabricated score. A noisy apparent win needs confirmation before it becomes a claimed improvement.

Keep the ruler comparable. Changing the workload, scoring formula, environment, or resource limits calls for a new baseline and a clear explanation, not an improvement claim across incompatible runs. Do not reduce the required work, weaken output validation, or pick favorable samples to manufacture a gain.

Stop when the goal is met, the agreed budget ends, the user redirects the work, or further attempts lack a useful hypothesis. Reserve enough time for a final correctness check and remeasurement of the retained state. Report an unmet target plainly.

At handoff, show baseline and retained measurements with their conditions and limitations. Use a compact table for a short comparison or a chart for a longer history; preserve failures and rejected attempts in the underlying record. A process chart is useful evidence, not a mandatory report format.
