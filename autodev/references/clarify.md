# Clarify

Read at task entry or when an agreement changes. Clarify turns natural-language intent into a shared, executable **target** before implementation.

The target takes a different form per scenario: a blueprint for feature development, a test set for a bug fix, a numeric benchmark for performance optimization. Clarify includes inspecting code, drawing diagrams, maintaining or building tests, trial runs, baseline measurement, and a scope proposal. It is not a questions-only or read-only phase.

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
