# Clarify

Read at task entry or when an agreement changes. Clarify turns natural-language intent into a shared, executable understanding before implementation.

It includes inspecting code, maintaining or building tests, trial runs, baseline measurement, and a scope proposal. It is not a questions-only or read-only phase.

## Choose the scenario

- A requested behavior or bug fix uses [Clarify: development](clarify-development.md).
- A performance goal uses [Clarify: optimization](clarify-optimization.md).

Read only the applicable branch. For a combined request, establish the feature behavior first, then optimize it with its own approved benchmark and baseline.

## Human-in-the-loop wraps the whole pass

Both branches share one shape: **prepare the test → capture baseline → propose the scope → human review**. Run the complete pass first, then present its results together. Do not stop for approval after each sub-step.

The human sees, in one review:

- the runnable tests, what each exercises, the input or workload, and the expected behavior or numeric output;
- the actual baseline result of those tests on the unchanged source;
- the proposed scope: permitted architecture/workflow impact for a feature, or target, editable files, and time budget for an optimization.

The human then decides: **revise**, which repeats Clarify from test preparation with the feedback applied, or **approve**, which enters Loop. Seeing the baseline before deciding lets the human judge whether the tests measure the right thing and whether the proposed scope fits the measured starting point.

Approval of a feature description or a test plan is not a substitute for confirming the runnable tests. Reuse explicit decisions already supplied; do not ask the human to repeat them, impose a fixed question count, or interpret silence as consent.

Keep test changes tied to the intended behavior. An obsolete expectation may be removed or revised; an inconvenient failure alone is not a reason to discard it. Preserve still-relevant coverage.

## Ready for Loop

After approval, record:

- the request and the human's confirmed test agreement;
- test files/version, exact command, working directory, and necessary execution conditions;
- the original source state and actual baseline output;
- for development, the approved architecture and workflow impact;
- for optimization, the approved target, editable files, and time budget;
- the user's current branch and whether uncommitted changes belong to the starting point, so Loop can create its worktree and Handoff can merge back.
- the contract directory written by `scripts/autodev_verify.py init`, which holds the same agreement in the form the Loop judge executes.

Keep this evidence in the repository's normal artifact location so the next person can distinguish agreements from assumptions. Do not overwrite the original baseline with the latest successful attempt.

A setup failure is not useful baseline evidence. Repair it and rerun the pass before review. If a test defect is found later, repair it here and rerun on the original source state; if its meaning changes, obtain renewed approval. Keep old and new test versions distinct instead of presenting incomparable results as progress.

Continue to [Loop](loop.md) only after the human has approved a complete pass.
