---
name: autodev
description: Goal-gated development loop — freeze the yardstick, bound the edit surface, keep only what beats the baseline. Use for implementation work (feature, bugfix, refactor) where Test-Driven Development is the correctness gate, and for optimization work (latency, bundle size, memory, cost, build time, model quality).
---

# autodev

Develop and optimize under a goal-gated loop: **frozen yardstick + bounded edit surface + mechanical verdict + a ratchet that only keeps improvements.**

## Three invariants

1. **Measurement precedes modification.** No touching the artifact until an objective way to judge the change exists and has been run.
2. **The measured may not edit the yardstick.** Whatever reports the number is off limits to whoever chases the number.
3. **The verdict is mechanical, never narrated.** A script decides. Read its output; do not argue with it.

## Route on the goal — never ask the user to pick a method

| The goal | Criterion | Lane | Budget |
|---|---|---|---|
| implement / add / support / fix X | binary predicate: a test goes false → true | gate only (**TDD**) | **none** — done or not done |
| optimize / speed up / reduce / shrink X | scalar + direction, against a measured baseline | gate **+ ratchet** | **required** |
| both ("add X, and it must be fast") | both | gate + ratchet | required |
| neither ("make it cleaner") | none | **stop and clarify** | — |

- **The correctness lane never skips TDD.** TDD is the gate layer, and both lanes carry it. The improvement lane stacks a scalar on top; it does not replace the gate.
- **The user never needs to know either name.** Feature-shaped goals route to gate-only, improvement-shaped goals route to gate + ratchet. Naming the lane is a convenience, not an input.

## Phase 0 — the contract

Six fields. The loop may not start until all six exist.

| Field | Meaning |
|---|---|
| `goal` | One sentence, falsifiable |
| `criterion` | The gate (must be true) and, in the improvement lane, the metric with direction, target, repeats, tie-break |
| `budget` | Improvement lane only: attempts and wall clock |
| `frozen` | Paths you must not edit — the yardstick |
| `surface` | Paths you may edit — explicit allowlist |
| `reset` | The exact command that undoes an attempt |

**If the criterion cannot be written as a one-command script, the goal is not ready.** Write the yardstick first.

### Freeze what could be traded for the number

Do not reflexively freeze wall-clock time. Freeze **whatever could be exchanged for a better measurement** — the things whose change would make the comparison meaningless. For most software work that is the environment and the workload: hardware, dataset, cache state, concurrency. Model training is the exception that proves the rule, because there the clock *is* the objective. Per-scenario sets: `references/contracts.md`.

### The clarify flow

Ask only what the goal does not determine. Never ask what you can infer; never ask what you can measure yourself.

- **At most two questions**, then one contract confirmation — the only mandatory human interaction in the loop.
- **Every question offers concrete options plus a custom one.** Never present a blank prompt when a good default exists.
- **Never ask about the method.** TDD versus loop is your inference, not their decision.
- **Show the cost estimate with the contract** ("~15 rounds / about 8 minutes"). The human is buying wall-clock time and must see the price.

**Correctness lane: usually zero questions.** The failing test *is* the criterion, and writing it is the first act of work. Clarify only when "done" is genuinely ambiguous or the request is a TDD exception (throwaway prototype, generated code, config). **Scope is not a budget** — when a feature is too large for one done/not-done unit, split it into units and finish them one at a time; never cap the rounds of correctness work.

**Improvement lane: exactly two questions.** First the metric and target, and only when the goal admits several — offer the two or three that fit this codebase, mark your recommendation, allow a custom answer. Then the budget, always, because the human is buying time: offer attempts and wall clock as pairs with estimates attached, plus a custom option.

### Building the yardstick is gate-lane work

When no benchmark exists, Phase 0 spawns one sub-task: write the measurement harness. That is "make something exist and work correctly", so it runs under TDD — first assert the harness distinguishes a 100ms case from a 200ms case, then build it, then verify it reproduces a known baseline difference.

**Building the yardstick is gate work; using the yardstick is ratchet work.** That recursion is why no new mechanism is needed for any new scenario.

## Phase 1 — baseline

1. Hash the `frozen` set and record it.
2. Improvement lane: run the metric `repeats` times, take the median, and **measure the noise floor — never assume it.** If run-to-run spread is ±3%, an accept threshold below 3% makes the ratchet accept randomness.
3. Correctness lane: the baseline is **RED** — the test exists, fails, and fails for the expected reason.
4. Write the contract and the baseline into the ledger.

Deterministic metrics (bundle bytes, test count) take `repeats: 1` and a zero floor. Noisy ones (latency, throughput, memory) take `repeats ≥ 5` and a measured floor.

## Phase 2 — the ratchet loop

```
1. Read the ledger, pick a hypothesis
   (order: combine near-misses → simplify → try something new)
2. Edit only within `surface`
3. Run the frozen yardstick exactly as the contract specifies
   (redirect output to a file; never flood your context with logs)
4. Apply the verdict mechanically
5. Append one row to the ledger
6. Repeat
```

### The verdict

```
crash                  → log crash, revert, next
gate fail              → log gate-fail, revert, next      ← correctness is not tradeable
metric ≤ baseline + δ  → log discard, revert, next
metric > baseline + δ  → KEEP: commit, baseline = metric
```

δ is the larger of the contract's minimum delta and the measured noise floor. Never compare one run against one run when the metric is noisy.

### Revert the surface, not the repository

```bash
git checkout <accepted-commit> -- <surface paths>
```

`git reset --hard` destroys the ledger and the yardstick along with the attempt. The ledger and the frozen set survive every revert — that is the entire point of the ratchet.

### The ledger

One untracked TSV at the repo root. It is the loop's memory across context windows: a fresh session reads it and resumes without re-deriving anything.

```
attempt	commit	gate	metric	delta	verdict	note
1	a1b2c3d	pass	184.2	—	baseline	initial state
2	b2c3d4e	pass	171.5	-12.7	keep	preload hero image
3	c3d4e5f	fail	—	—	gate-fail	inline critical css broke tests
4	d4e5f6g	pass	183.9	+12.4	revert	memoized fetch, no real gain
```

Log failures as carefully as successes: the rejected attempts are the record of what has been ruled out, and they are what stops the loop from retrying the same idea.

### Stop conditions are objective

There is no "this looks good enough."

- **Budget exhausted** — attempts or wall clock, whichever binds first
- **Target met** — `metric ≤ target`
- **Converged** — three consecutive attempts improving by less than the noise floor
- **Stuck** — four consecutive reversals; the hypothesis space is exhausted at this ambition

On any of these: **stop, report the ledger, and offer to continue.** Never interrupt mid-budget to ask whether to keep going; never continue past the budget because momentum feels good.

## Phase 3 — land

- Re-run the full gate from a clean state on the frozen yardstick.
- **Now** refactor if it helps — the metric is locked in and the gate protects it. A refactor that breaks the gate or worsens the metric is reverted like any other attempt. Equal metric with a smaller diff is a win, not a tie.
- Report accepted, rejected, net improvement, cost, and the near-misses worth revisiting.
- The human iterates on the **contract** next time, not on the artifact.

## Anti-gaming invariants

Without these, an agent optimizes the measurement instead of the code.

1. **Hash the frozen set** before and after every attempt; a changed hash fails the attempt outright.
2. **The gate only gets stronger.** The assertion count may increase or stay equal, never decrease — this makes "fix the code, not the test" mechanically checkable.
3. **No new dependencies, network calls, or hardware branches.**
4. **No shrinking the workload to fake a gain** — fewer eval samples, cached results, memoized benchmark inputs, unrequested warm caches.
5. **No best-of-N.** Fixed `repeats`, median statistic. Re-running until a lucky sample lands is cheating.
6. **No `.skip`, `xfail`, or loosened tolerances** to turn the gate green.
7. **At equal metric, simpler wins.** A metric is not a complete objective function; without a tie-break the ratchet accumulates complexity.

## The gate layer: TDD

Mandatory in both lanes.

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

- **RED** — one minimal test for one behavior, against real code. Run it. Confirm it fails because the feature is missing, not from a typo. A test that passes immediately is testing existing behavior: fix the test.
- **GREEN** — the simplest code that passes that one test. No speculative options, no extra features. Run it. Confirm it passes and the suite stays green.
- **REFACTOR** — clean up only while green.

Code written before its test is deleted, not kept as reference and not adapted while writing tests. The ratchet enforces this mechanically: an unverified edit is not the accepted state, so it gets reverted like anything else.

## Reference files

| Read | When |
|---|---|
| `references/gate.md` | Before writing production code or touching tests — the full Iron Law, both verification gates, the rationalization table, red flags, the pre-completion checklist |
| `references/testing-anti-patterns.md` | When adding mocks or test utilities |
| `references/contracts.md` | When drafting a contract — metric selection, frozen sets per scenario, worked examples |
