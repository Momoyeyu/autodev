---
name: autodev
description: Develop and optimize code by measurement instead of opinion — agree on a benchmark first, edit only the files you are allowed to edit, and keep a change only when a script says it is better. Use for implementation work (feature, bugfix, refactor), where Test-Driven Development is the correctness gate, and for optimization work (latency, bundle size, memory, cost, build time, model quality).
---

# autodev

Write code and improve it by measurement, not by opinion: **agree on a benchmark first, touch only the files you are allowed to touch, and accept a change only when a script says it is better.**

Every attempt ends in one of two verdicts — accept and commit, or reject and roll back — so the accepted state only ever moves forward. That one-way rule is the ratchet.

## Three rules

1. **Measure before you change anything.** No editing until an objective way to tell whether the change helped exists, and has been run once.
2. **Whoever chases the number doesn't get to change how it's measured.** The benchmark, the tests, and the environment are off limits to the code being optimized.
3. **The script decides.** The verdict is a command's output. Reading it is fine; arguing with it is not.

## Two modes

| The request | How success is judged | Mode | Time budget |
|---|---|---|---|
| add / implement / support / fix X | a test goes from failing to passing | **development** (TDD) | **none** — it's done or it isn't |
| make X faster / smaller / cheaper | a number beats the baseline | **optimization** | **required** |
| both ("add X, and it has to be fast") | both | optimization | required |
| neither ("make it cleaner") | nothing measurable | **stop and ask** | — |

- **Development always runs TDD.** It isn't a mode you opt into.
- **Optimization adds a benchmark on top of TDD**, it does not replace it. Tests still pass, new code still gets tests first. A change that improves the number but breaks a test is reverted like any other failure.
- **Never ask the user which mode.** The shape of the request decides. Naming the mode is a convenience, not an input.
- Development work gets no time budget: a feature is not improved by being abandoned halfway. If it is too big for one done-or-not unit, split it into several.

## Phase 0 — the contract

Six fields, agreed before any code is written.

| Field | Meaning |
|---|---|
| `goal` | One sentence, and it must be possible to be wrong about it |
| `criterion` | The tests that must pass, plus — in optimization — the metric, its direction, target, and repeat count |
| `budget` | Optimization only: how many attempts, and how much wall clock |
| `frozen` | Files that must not change: the benchmark, the tests, the env |
| `surface` | Files that may change: an explicit list |
| `reset` | The exact command that undoes one attempt |

**If the criterion can't be run as a single command, the goal isn't ready.** Build the benchmark first.

### Freeze whatever could be traded for the number

Don't reflexively freeze wall-clock time. Freeze the things that, if changed, would make two attempts incomparable — for most software work that's the machine, the dataset, the cache state, and the concurrency. Training a model is the exception that proves the rule, because there the clock *is* the objective. Per-scenario lists: `references/contracts.md`.

### Asking the user

Ask only what the request doesn't already determine. Never ask what you can infer, and never ask what you can measure yourself.

- **Two questions at most**, then one confirmation of the whole contract — the only point where the loop needs a human.
- **Every question offers concrete options plus a custom one.** Never hand someone a blank prompt when a sensible default exists.
- **Never ask which mode.** That's your inference, not their decision.
- **Show the cost with the contract** ("~15 attempts, about 8 minutes"). In optimization the user is buying wall clock, and they should see the price before agreeing to it.

**Development: usually zero questions.** The failing test *is* the criterion, and writing it is the first piece of work. Ask only when "done" is genuinely ambiguous, or when the request is one of the TDD exceptions (throwaway prototype, generated code, config).

**Optimization: exactly two questions.** First the metric and the target, and only when the request admits more than one — offer the two or three that fit this codebase, mark your recommendation, allow a custom answer. Then the budget, always, since that is what the user is paying: offer attempts and wall clock as pairs, with the estimate attached, plus a custom option.

### Building the benchmark is TDD work

When no benchmark exists, Phase 0 spawns one task: write it. That is "make something exist and work correctly", so it runs under TDD — first assert that the benchmark tells a 100ms case apart from a 200ms case, then build it, then check it reproduces a difference you already know exists.

**Building the benchmark is development work. Using it is optimization work.** That recursion is why no new machinery is needed for a new kind of target.

## Phase 1 — baseline

1. Hash the `frozen` files and record the hash.
2. Optimization: run the metric `repeats` times, take the median, and **measure the noise — never assume it.** If run-to-run spread is ±3%, an accept threshold below 3% means you are measuring noise rather than progress.
3. Development: the baseline is **RED** — the test exists, fails, and fails for the right reason.
4. Write the contract and the baseline into the experiment log.

Deterministic metrics (bundle bytes, test count) need `repeats: 1` and a zero noise floor. Noisy ones (latency, throughput, memory) need `repeats ≥ 5` and a measured one.

## Phase 2 — the loop

```
1. Read the log, pick an idea
   (combine near-misses first, then simplify, then try something new)
2. Edit only inside `surface`
3. Run the benchmark exactly as the contract says
   (send output to a file; never flood your context with logs)
4. Apply the verdict
5. Append one row to the log
6. Repeat
```

### The verdict

```
crash                  → log it, roll back, next
tests fail             → log it, roll back, next     ← correctness is not tradeable
metric ≤ baseline + δ  → log it, roll back, next
metric > baseline + δ  → ACCEPT: commit, baseline = metric
```

δ is the larger of the contract's minimum improvement and the measured noise. Never compare one run against one run when the metric is noisy.

### Rolling back one attempt

```bash
git checkout <accepted-commit> -- <surface paths>
```

Roll back the files, not the repository. `git reset --hard` would throw away the log and the frozen files along with the attempt — and those are the two things that have to survive a rejection.

### The experiment log

One untracked TSV at the repo root. It is what survives a context reset: a new session reads it and continues without re-deriving anything.

```
attempt	commit	tests	metric	delta	verdict	note
1	a1b2c3d	pass	184.2	—	baseline	initial state
2	b2c3d4e	pass	171.5	-12.7	accept	preload hero image
3	c3d4e5f	fail	—	—	fail	inline critical css broke the suite
4	d4e5f6g	pass	183.9	+12.4	reject	memoized fetch, no real gain
```

Log failures as carefully as successes: they are the record of what has been ruled out, and they are what stops the next session from retrying a dead end.

### Stop conditions

All objective. There is no "this looks good enough."

- **Budget spent** — attempts or wall clock, whichever runs out first
- **Target met** — `metric ≤ target`
- **Converged** — three attempts in a row that improve by less than the noise
- **Stuck** — four reversals in a row; the ideas at this level of ambition are exhausted

On any of these: **stop, report the log, offer to continue.** Never interrupt mid-budget to ask whether to keep going, and never run past the budget because momentum feels good.

## Phase 3 — review

- Re-run the full test suite from a clean state against the benchmark.
- **Now** refactor if it helps. The metric is locked in and the tests protect it. A refactor that breaks a test or worsens the metric is rolled back like any other attempt, and the same metric in a smaller diff is a win rather than a tie.
- Report what was accepted, what was rejected, the net improvement, what it cost, and the near-misses worth another look.
- Next time, the human iterates on the **contract**, not on the code.

## Anti-gaming rules

Without these, the agent optimizes the measurement instead of the code.

1. **Hash the frozen files** before and after every attempt. A changed hash fails the attempt outright.
2. **The tests only get stronger.** The assertion count may rise or hold, never fall — "fix the code, not the test", made checkable.
3. **No new dependencies, network calls, or hardware branches.**
4. **No shrinking the workload to fake a gain** — fewer eval samples, cached results, memoized benchmark inputs, warm caches the contract didn't ask for.
5. **No best-of-N.** Fixed `repeats`, median statistic. Re-running until a lucky sample lands is cheating.
6. **No `.skip`, no `xfail`, no loosened tolerances** to turn a test green.
7. **At equal metric, the simpler change wins.** A metric is not a complete objective; without a tie-break the loop just accumulates complexity.

## The correctness gate: TDD

Required in both modes.

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

- **RED** — one minimal test for one behavior, against real code. Run it. Confirm it fails because the feature is missing, not because of a typo. A test that passes immediately is testing what already exists: fix the test.
- **GREEN** — the simplest code that passes that one test. No speculative options, no extra features. Run it. Confirm it passes and the rest of the suite stays green.
- **REFACTOR** — clean up, but only while green.

Code written before its test gets deleted, not kept as reference and not adapted while writing tests. The loop enforces this without anyone having to be disciplined about it: an unverified edit is simply not the accepted state, so it gets rolled back.

## Reference files

| Read | When |
|---|---|
| `references/gate.md` | Before writing production code or touching tests — the full Iron Law, both verification steps, the rationalization table, red flags, the pre-completion checklist |
| `references/testing-anti-patterns.md` | When adding mocks or test utilities |
| `references/contracts.md` | When drafting a contract — choosing a metric, frozen files per scenario, worked examples |
