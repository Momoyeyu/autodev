# Clarify

Read at task entry or when an agreement changes. Clarify turns natural-language intent into a shared, executable understanding before implementation.

It includes inspecting code, maintaining or building tests, trial runs, human review, and baseline measurement. It is not a questions-only or read-only phase.

## Choose the scenario

- A requested behavior or bug fix uses [Clarify: development](clarify-development.md).
- A performance goal uses [Clarify: optimization](clarify-optimization.md).

Read only the applicable branch. For a combined request, establish the feature behavior first, then optimize it with its own approved benchmark and baseline.

## Human-in-the-loop means agreement on runnable tests

Show what each test exercises, the input or workload, and the expected behavior or numeric output. Prepare and run the tests, discuss corrections with the human, and repeat until the human confirms the actual executable acceptance basis.

Approval of a feature description or a test plan is not a substitute for confirming the runnable tests. Reuse explicit decisions already supplied; do not ask the human to repeat them, impose a fixed question count, or interpret silence as consent.

Keep test changes tied to the intended behavior. An obsolete expectation may be removed or revised; an inconvenient failure alone is not a reason to discard it. Preserve still-relevant coverage.

## Ready for Loop

Before implementation, record:

- the request and the human's confirmed test agreement;
- test files/version, exact command, working directory, and necessary execution conditions;
- the original source state and actual baseline output;
- for development, the approved architecture and workflow impact;
- for optimization, the baseline-informed target, editable files, and time budget.

Keep this evidence in the repository's normal artifact location so the next person can distinguish agreements from assumptions. Do not overwrite the original baseline with the latest successful attempt.

A setup failure is not useful baseline evidence. Repair it before proceeding. If a test defect is found later, repair it here and rerun on the original source state; if its meaning changes, obtain renewed approval. Keep old and new test versions distinct instead of presenting incomparable results as progress.

Continue to [Loop](loop.md) only after the selected branch's agreement and baseline are ready.
