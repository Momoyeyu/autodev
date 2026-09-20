# Loop

Read after Clarify is complete. Apply the shared rules and the section for the current scenario. Loop implements the agreement; it does not redefine success.

## Shared rules

- Work only within the permitted impact or editable-file boundary.
- Keep the approved test version, workload, and measuring conditions comparable with baseline.
- Save actual command output and source identities. Do not turn skips, setup errors, crashes, or unrun checks into passing results.
- Return to [Clarify](clarify.md) if intent, test meaning, or scope changes. A test defect also needs repair and a comparable baseline, not a silent adjustment during implementation.
- Preserve unrelated user work. Restoring an attempt never authorizes resetting the whole repository or rewriting shared history.

## Feature development

1. Read the approved impact, tests, and baseline failures.
2. Implement a focused change within that impact.
3. Run relevant tests for feedback and the complete agreed test set at checkpoints.
4. Record remaining failures and repeat until **all agreed tests pass**.

A still-failing new case does not require discarding useful partial development. Fix the implementation and regressions rather than weakening tests or accepting only a passing subset. Do not impose an optimization timeout or an arbitrary attempt count on feature work.

Once the complete agreed set passes, verify the delivered state and enter [Handoff](handoff.md#feature-development-one-table).

## Performance optimization

Keep the original baseline separate from the best verified candidate. Initialize the best candidate to baseline.

1. Check the target and remaining time before each attempt. Bound long-running commands by the remaining budget.
2. Modify only allowed implementation files, keeping a recoverable best-state snapshot.
3. Run the same benchmark with the agreed inputs, repetitions, aggregation, and formula.
4. Check file boundaries and measurement identities. Crashes, invalid outputs, or tampering invalidate the result regardless of its reported score.
5. Keep a verified improvement under the agreed direction and variability treatment; otherwise restore only that attempt's changes to the best valid state.
6. Record the outcome and repeat until **the target is met or the time budget expires**.

Do not add convergence, rejection-count, or attempt-count exits. Do not extend the budget silently. At timeout, discard any unverified in-flight candidate and retain the best verified one. If no improvement was verified, retain baseline and say so.

Do not shrink workloads, hardcode answers, retune weights, or change benchmark conditions to game the score.

## Record the optimization process for the chart

Record baseline and every attempt, including rejected and failed ones. Each record needs an attempt ID or elapsed time, source identity, actual score when valid, retained/rejected/failed status, and a link to raw output.

A crash or timeout has no numeric score: mark it invalid, not zero. Preserve enough history to distinguish measured attempts from the best-so-far state. Record which measured candidate is ultimately delivered, even if it is not the last attempt.

Reserve final verification inside the agreed budget. Then enter [Handoff](handoff.md#performance-optimization-one-chart); do not replace the process chart with only a before/after number.

If permissions, dependencies, or the environment block either loop, report the blockage and last verified state rather than spinning indefinitely or claiming completion.
