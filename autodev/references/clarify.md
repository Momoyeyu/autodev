# Clarify

Read at task entry or when an agreement changes. Clarify turns natural-language intent into a shared, executable **target** before implementation.

The target takes a different form per scenario: a blueprint for feature development, a test set for a bug fix, a numeric benchmark for performance optimization. Clarify includes inspecting code, drawing diagrams, maintaining or building tests, trial runs, baseline measurement, and a scope proposal. It is not a questions-only or read-only phase.

If the repository has an `.autodev/` directory, read the [Constitution](constitution.md) first: its frozen paths, guard, and budget limits constrain the scope you may propose.

## Choose the scenario

- A new capability or feature uses [Clarify: development](clarify-development.md) — the target is a blueprint.
- A defect with a concrete failing case uses [Clarify: bug fix](clarify-bugfix.md) — the target is a passing test set.
- A performance goal uses [Clarify: optimization](clarify-optimization.md) — the target is one numeric score reaching an agreed threshold.

Read only the applicable branch. For a combined request, establish the behavior or design first, then optimize it with its own approved benchmark and baseline.

## Human-in-the-loop wraps the whole pass

All branches share one shape: **prepare the target artifact → capture baseline → propose the scope → human review**. Run the complete pass first, then present its results together. Do not stop for approval after each sub-step.

The human sees, in one review:

- the prepared artifact — as-is and blueprint diagrams, runnable tests, or the benchmark and its conditions;
- the actual baseline on the unchanged source — as-is diagrams, test outcomes, or the measured score;
- the proposed scope — editable files, and for optimization also the numeric target and time budget.

The human then decides: **revise**, which repeats Clarify with the feedback applied, or **approve**, which enters Loop. Seeing the baseline before deciding lets the human judge whether the target measures or describes the right thing and whether the proposed scope fits the starting point.

Approval of a description or a plan is not a substitute for confirming the prepared artifact. Reuse explicit decisions already supplied; do not ask the human to repeat them, impose a fixed question count, or interpret silence as consent.

Keep test changes tied to the intended behavior. An obsolete expectation may be removed or revised; an inconvenient failure alone is not a reason to discard it. Preserve still-relevant coverage.

## The contract

Write the proposal as a contract with the judge script, run in the working clone (`--repo`, default `.`):

```bash
python3 <skill>/scripts/autodev_verify.py --home "$PWD/.autodev/runs/<task>" init --scenario <scenario> ...
```

`.autodev/` belongs to the **working clone** — the long-lived clone the human edits, commits, and pushes from (their fork in a fork workflow), whatever branch it has checked out. When several clones of the project exist, `init` still runs in the working clone; mirrors and upstream clones stay pristine and accumulate no autodev state. Within that clone, run `init` in the clone's own worktree, not a linked worktree — the exclude entry would otherwise land in the wrong git directory, so `init` refuses.

`--home` must be a run directory under `<repo>/.autodev/runs/`, as an absolute path reused by every later command, and outside the loop worktree — `start` refuses one inside it. `init` adds `/.autodev/` to the clone's `.git/info/exclude`, so every autodev file — contract, logs, raw output, rendered previews, the constitution itself — stays inside the project yet never appears in `git status` or shared history.

The baseline runs in the working clone's checkout on purpose, so it measures the actual starting state including uncommitted changes; `init` records whatever the run left behind as `baseline.side_effects` and refuses outright if it touched a frozen path.

Run-artifact paths the agreed commands write are declared with `init --generated` (or the constitution's `generated` key): untracked files under them never block an attempt and rollback sweeps them, but committing one is invalid — run artifacts are never deliverables. A generated path must not overlap a frozen one.

`init` prints the contract for the human's review, and its fields drive every Loop verdict — nothing agreed here depends on the agent remembering it. The contract also records the starting branch (`--branch-from` overrides) so Handoff can merge back. `init` seals `contract.json` with an `agreement_sha`: every later command re-verifies it, so editing the agreement mid-loop is refused — a changed agreement means `init --renew`, which archives the previous contract.

If a run directory lands in the wrong clone, move the whole `.autodev/` tree into the working clone and run `autodev_verify.py --home <new run dir> relocate --repo <working clone>`: it re-binds the contract, excludes `.autodev/` in the new clone, and refuses unless a recorded constitution exists there unchanged — relocation is not a way to amend rules mid-loop. When the contract already holds a `best` commit, fetch the loop branch into the new clone first. A loop worktree is re-bound with `--worktree` and must be created from the new clone (`git worktree add`, at a commit containing `best`) — a worktree still owned by the old clone commits into the old clone's object store, which defeats the move.

## Ready for Loop

After approval, record:

- the request and the human's confirmed target agreement;
- for development, the as-is diagrams, the blueprint with its element IDs, and the approved scope;
- for a bug fix, the test files/version, exact command, working directory, and execution conditions;
- for optimization, the benchmark conditions, target, editable files, and time budget;
- the original source state and actual baseline output;
- the user's current branch and whether uncommitted changes belong to the starting point, so Loop can create its worktree and Handoff can merge back;
- the contract directory written by `scripts/autodev_verify.py init`, which holds the same agreement in the form the Loop judge executes.

Keep this evidence in the repository's normal artifact location so the next person can distinguish agreements from assumptions. Do not overwrite the original baseline with the latest successful attempt.

A setup failure is not useful baseline evidence. Repair it and rerun the pass before review. If a test defect is found later, repair it here and rerun on the original source state; if its meaning changes, obtain renewed approval. Keep old and new test versions distinct instead of presenting incomparable results as progress.

Continue to [Loop](loop.md) only after the human has approved a complete pass.
