# Loop

Read after the human has approved a complete Clarify pass. Apply the shared rules and the section for the current scenario. Loop implements the agreement; it does not redefine success.

## Shared rules

- Work only within the permitted impact or editable-file boundary.
- Keep the approved test version, workload, and measuring conditions comparable with baseline.
- Save actual command output and source identities. Do not turn skips, setup errors, crashes, or unrun checks into passing results.
- Return to [Clarify](clarify.md) for a new full pass if intent, test meaning, or scope changes. A test defect also needs repair and a comparable baseline, not a silent adjustment during implementation.
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

Use a **do-while** loop: execute an attempt before evaluating the normal exit conditions.

1. Modify only allowed implementation files, keeping a recoverable best-state snapshot.
2. Run the same benchmark with the agreed inputs, repetitions, aggregation, and formula.
3. Check file boundaries and measurement identities. Crashes, invalid outputs, or tampering invalidate the result regardless of its reported score.
4. Keep a verified improvement under the agreed direction and variability treatment; otherwise restore only that attempt's changes to the best valid state.
5. Record the outcome, including invalid or rejected attempts.
6. Check whether **the retained best verified score meets the target or the time budget has expired**. A rejected or invalid attempt cannot establish target achievement. If neither exit condition holds, return to step 1; otherwise enter Handoff with the best verified state.

Bound commands by the remaining wall-clock budget throughout each attempt. Post-testing does not authorize work after the deadline; interrupt an in-flight attempt when time runs out. If no execution time remains at entry, report budget exhaustion rather than starting unauthorized work.

Do not add convergence, rejection-count, or attempt-count exits. Do not extend the budget silently. At timeout, discard any unverified in-flight candidate and retain the best verified one. If no improvement was verified, retain baseline and say so.

Do not shrink workloads, hardcode answers, retune weights, or change benchmark conditions to game the score.

## Record the optimization process for the chart

Record baseline and every attempt, including rejected and failed ones. Each record needs an attempt ID or elapsed time, source identity, actual score when valid, retained/rejected/failed status, and a link to raw output.

A crash or timeout has no numeric score: mark it invalid, not zero. Preserve enough history to distinguish measured attempts from the best-so-far state. Record which measured candidate is ultimately delivered, even if it is not the last attempt.

Reserve final verification inside the agreed budget. Then enter [Handoff](handoff.md#performance-optimization-one-chart); do not replace the process chart with only a before/after number.

If permissions, dependencies, or the environment block either loop, report the blockage and last verified state rather than spinning indefinitely or claiming completion.
