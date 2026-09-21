# Loop

Read after the human has approved a complete Clarify pass. Apply the shared rules and the section for the current scenario. Loop implements the agreement; it does not redefine success.

## Shared rules

- Work only within the permitted impact or editable-file boundary.
- Keep the approved test version, workload, and measuring conditions comparable with baseline.
- Save actual command output and source identities. Do not turn skips, setup errors, crashes, or unrun checks into passing results.
- Return to [Clarify](clarify.md) for a new full pass if intent, test meaning, or scope changes. A test defect also needs repair and a comparable baseline, not a silent adjustment during implementation.
- Work in the dedicated worktree described below. Never reset, clean, or rewrite the user's own checkout or shared history.

## Isolate the loop in a git worktree

Loop runs in a **separate git worktree on a dedicated branch**, created when Loop starts, for both scenarios. Git is the snapshot mechanism: a commit is the only accepted form of "state", and git reset is the only form of rollback. Do not maintain snapshots by hand.

1. If the project is not a git repository, `git init` and commit the current state first.
2. Note the user's current branch; Handoff merges back into it. Create the loop branch and worktree outside the repository, for example `git worktree add -b autodev/<task> ../<repo>-autodev-<task> HEAD`.
3. If the user has uncommitted changes that belong to the starting point, apply them in the worktree and commit them there as the baseline commit. The user's checkout and branch stay untouched.
4. Prepare the runtime in the worktree yourself (dependencies, `.env`, local data); rerun the approved test there once and confirm it reproduces baseline before the first attempt.
5. Commit every attempt or checkpoint on the loop branch before evaluating it. Write logs and raw outputs to the agreed artifact location, not into editable paths.

Ignored build products left in the worktree are acceptable; the worktree is removed after Handoff. Prefer idempotent tests so a previous attempt's external side effects do not distort the next measurement.

## Feature development

1. Read the approved impact, tests, and baseline failures.
2. Implement a focused change within that impact.
3. Run relevant tests for feedback and the complete agreed test set at checkpoints; commit each checkpoint on the loop branch.
4. Record remaining failures and repeat until **all agreed tests pass**.

A still-failing new case does not require discarding useful partial development. Fix the implementation and regressions rather than weakening tests or accepting only a passing subset. Do not impose an optimization timeout or an arbitrary attempt count on feature work.

Once the complete agreed set passes, verify the delivered state and enter [Handoff](handoff.md#feature-development-one-table).

## Performance optimization

Keep the original baseline separate from the best verified candidate. Initialize the best candidate to the baseline commit; `best` is always a commit on the loop branch.

Use a **do-while** loop: execute an attempt before evaluating the normal exit conditions.

1. Modify only allowed implementation files and commit the attempt.
2. Run the same benchmark with the agreed inputs, repetitions, aggregation, and formula.
3. Before judging the score, check that the diff from `best` touches only editable files and that the frozen surface (benchmark, inputs, weights, scoring) still matches the identities recorded in Clarify. A score measured with a tampered ruler is invalid regardless of its value, as are crashes and invalid outputs.
4. Accept the attempt only under the direction-bound rule from Clarify (lower: `score < best - δ`; higher: `score > best + δ`); accepted means the attempt commit becomes `best`.
5. Log the outcome: attempt ID, one-line description of the change, score or invalid reason, and accepted/rejected/invalid. Then, unless accepted, roll back with `git reset --hard <best>` followed by `git clean -fd` in the worktree, which removes modified, added, deleted, and staged changes alike. Rejected code is not kept; the log is what the chart and the human need.
6. Check whether **the retained best verified score meets the target under the same direction and the agreed equality rule, or the time budget has expired**. A rejected or invalid attempt cannot establish target achievement. If neither exit condition holds, return to step 1; otherwise enter Handoff with the best verified state.

Bound commands by the remaining wall-clock budget throughout each attempt. Post-testing does not authorize work after the deadline; interrupt an in-flight attempt when time runs out. If no execution time remains at entry, report budget exhaustion rather than starting unauthorized work.

Do not add convergence, rejection-count, or attempt-count exits. Do not extend the budget silently. At timeout, roll back any unverified in-flight candidate the same way and retain `best`. If no improvement was verified, retain baseline and say so.

Do not shrink workloads, hardcode answers, retune weights, or change benchmark conditions to game the score.

## Record the optimization process for the chart

Record baseline and every attempt, including rejected and failed ones. Each record needs an attempt ID or elapsed time, source identity, actual score when valid, retained/rejected/failed status, and a link to raw output.

A crash or timeout has no numeric score: mark it invalid, not zero. Preserve enough history to distinguish measured attempts from the best-so-far state. Record which measured candidate is ultimately delivered, even if it is not the last attempt.

Reserve final verification inside the agreed budget. Then enter [Handoff](handoff.md#performance-optimization-one-chart); do not replace the process chart with only a before/after number.

If permissions, dependencies, or the environment block either loop, report the blockage and last verified state rather than spinning indefinitely or claiming completion.
