# Loop

Read after the human has approved a complete Clarify pass. Apply the shared rules and the section for the current scenario. Loop implements the agreed target; it does not redefine it.

## Shared rules

- Work only within the permitted impact or editable-file boundary.
- Keep the approved target — blueprint, test set, or benchmark — fixed and comparable with baseline.
- Save actual command output and source identities. Do not turn skips, setup errors, crashes, or unrun checks into passing results.
- Return to [Clarify](clarify.md) for a new full pass if intent, the target's meaning, or scope changes. A defect in the agreed artifact also needs repair and a comparable baseline, not a silent adjustment during implementation.
- Work in the dedicated worktree described below. Never reset, clean, or rewrite the user's own checkout or shared history.
- Judge every round with `scripts/autodev_verify.py`, not by hand. It performs the scope check, frozen-surface check, command run, direction-bound comparison, rollback, and logging described below, and leaves the raw output that Handoff cites. Its exit code is the verdict: `0` accepted or green, `1` rejected, failing, or checkpoint, `2` invalid, `3` precondition not met.

## Isolate the loop in a git worktree

Loop runs in a **separate git worktree on a dedicated branch**, created when Loop starts, for all scenarios. Git is the snapshot mechanism: a commit is the only accepted form of "state", and git reset is the only form of rollback. Do not maintain snapshots by hand.

1. If the project is not a git repository, `git init` and commit the current state first.
2. Note the user's current branch; Handoff merges back into it. Create the loop branch and worktree outside the repository, for example `git worktree add -b autodev/<task> ../<repo>-autodev-<task> HEAD`.
3. If the user has uncommitted changes that belong to the starting point, apply them in the worktree and commit them there as the baseline commit. The user's checkout and branch stay untouched.
4. Prepare the runtime in the worktree yourself (dependencies, `.env`, local data). Then bind the judge to the worktree: `python3 <skill>/scripts/autodev_verify.py --home <contract dir> start --worktree <path>`. It records `best = HEAD`, starts the time budget, and runs a smoke test that deliberately edits a frozen file and adds an out-of-scope file, requiring both to be rejected and the rollback to leave no residue. Do not begin attempts if the smoke test fails.
5. Commit every attempt or checkpoint on the loop branch before evaluating it. Write logs and raw outputs to the agreed artifact location, which must be outside the worktree or git-ignored, since rollback runs `git clean -fd`; never into editable paths.

Ignored build products left in the worktree are acceptable; the worktree is removed after Handoff. Prefer idempotent checks so a previous attempt's external side effects do not distort the next measurement.

## Feature development

The target is the approved blueprint: every element realized in the delivered code.

1. Read the approved blueprint, its element IDs, the scope, and which test files are frozen or editable.
2. Implement blueprint elements in focused commits within the editable surface.
3. At each checkpoint, commit and run `autodev_verify.py --home <contract dir> attempt --note "<what changed>"`. With a regression `--check-cmd` it exits `0` (green) or `1` (failing); without one it records a `checkpoint`. All three keep the commit. An `invalid` verdict — frozen file edited or out-of-scope change — is rolled back.
4. When the blueprint is implemented, draw the **as-built** diagrams from the delivered code — architecture and flows in Mermaid at the agreed `--asbuilt` path, addressing every blueprint element ID — and commit. Then run `autodev_verify.py --home <contract dir> status`: it reports `handoff` only when the regression check is green and every element ID is covered by the as-built file.
5. Coverage is mechanical; semantic agreement is your judgment. If the as-built state does not actually realize the blueprint — a missing responsibility, a rewired flow — the development is wrong; keep looping instead of exiting.

Do not weaken tests, skip the regression check, or claim coverage the diagrams do not show. Do not impose an optimization timeout or an arbitrary attempt count on feature work.

Once `status` reports `handoff`, enter [Handoff](handoff.md#feature-development-as-built-diagrams).

## Bug fix

The target is the agreed test set passing.

1. Read the approved impact, tests, and baseline failures — the reproduction case first.
2. Implement a focused fix within that impact.
3. Run relevant tests for feedback. At each checkpoint, commit and run `autodev_verify.py --home <contract dir> attempt --note "<what changed>"`: it rejects the checkpoint as invalid if it touches frozen test files or paths outside the approved impact, runs the complete agreed test set, and logs the result. A failing checkpoint is kept (exit `1`); an invalid one is rolled back (exit `2`).
4. Record remaining failures and repeat until `attempt` exits `0`, meaning **all agreed tests pass**; `status` then reports `handoff`.

A still-failing case does not require discarding a partial fix. Fix the implementation and regressions rather than weakening tests or accepting only a passing subset. Do not impose an optimization timeout or an arbitrary attempt count on bug-fix work.

Once the complete agreed set passes, verify the delivered state and enter [Handoff](handoff.md#bug-fix-the-passing-test-set).

## Performance optimization

Keep the original baseline separate from the best verified candidate. Initialize the best candidate to the baseline commit; `best` is always a commit on the loop branch.

Use a **do-while** loop: execute an attempt before evaluating the normal exit conditions.

1. Modify only allowed implementation files and commit the attempt.
2. Run `autodev_verify.py --home <contract dir> attempt --note "<what changed>"`. It runs the same benchmark with the agreed command inside the remaining budget and saves the raw output as `raw/attempt-NNN.log`.
3. Before judging the score, the same command checks that the diff from `best` touches only editable files and that the frozen surface (benchmark, inputs, weights, scoring) still matches the hashes recorded in Clarify. A score measured with a tampered ruler is invalid regardless of its value, as are crashes, timeouts, and output without a score.
4. It accepts the attempt only under the direction-bound rule from Clarify (lower: `score < best - δ`; higher: `score > best + δ`); accepted means the attempt commit becomes `best`.
5. It logs the outcome to `attempts.jsonl`: attempt number, commit, your note, score or invalid reason, verdict, and raw-output path. Then, unless accepted, it rolls back with `git reset --hard <best>` followed by `git clean -fd` in the worktree, which removes modified, added, deleted, and staged changes alike. Rejected code is not kept; the log is what the chart and the human need.
6. Run `autodev_verify.py --home <contract dir> status`. It reports whether **the retained best verified score meets the target under the same direction and the agreed equality rule, or the time budget has expired**. A rejected or invalid attempt cannot establish target achievement. If `decision` is `continue`, return to step 1; if `handoff`, enter Handoff with the best verified state.

`attempt` bounds the benchmark run by the remaining wall-clock budget and refuses to start once the deadline has passed (exit `3`); the in-flight commit is then rolled back the same way and `status` reports `time budget exhausted`. Post-testing does not authorize work after the deadline. Do not edit the contract, the log, or the raw outputs; a changed agreement means a new Clarify pass and `init --renew`.

Do not add convergence, rejection-count, or attempt-count exits. Do not extend the budget silently. At timeout, roll back any unverified in-flight candidate the same way and retain `best`. If no improvement was verified, retain baseline and say so.

Do not shrink workloads, hardcode answers, retune weights, or change benchmark conditions to game the score.

## Record the optimization process for the chart

`attempts.jsonl` already records baseline and every attempt, including rejected and failed ones, with attempt number, commit, actual score when valid, verdict, and the raw-output path. Add nothing to it by hand; write your own notes elsewhere.

A crash or timeout has no numeric score: mark it invalid, not zero. Preserve enough history to distinguish measured attempts from the best-so-far state. Record which measured candidate is ultimately delivered, even if it is not the last attempt.

Reserve final verification inside the agreed budget. Then enter [Handoff](handoff.md#performance-optimization-one-chart); do not replace the process chart with only a before/after number.

If permissions, dependencies, or the environment block any loop, report the blockage and last verified state rather than spinning indefinitely or claiming completion.
