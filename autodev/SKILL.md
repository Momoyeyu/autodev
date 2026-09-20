---
name: autodev
description: Align agents and humans through approved tests, measured baselines, and visible delivery evidence. Use for feature development, bug fixes, and performance optimization when requirements, allowed changes, and success must be made explicit before implementation.
---

# autodev

Reduce misunderstanding and rework between the human and the agent. Improve delivery quality, stability, and overall efficiency while making the project easier for the human to understand and take over.

**Verifiable & measurable & visible:** agree on what will be tested, record where the project starts, and make the final difference easy to inspect and reproduce.

## Two scenarios, four stages

| Stage | Feature development | Performance optimization |
|---|---|---|
| **Define** | Confirm architecture/workflow impact; iterate on tests with the human until approved | Iterate with the human until one numeric benchmark test is approved |
| **Anchor** | Inspect existing tests, update/remove outdated ones, add missing ones, verify execution, record baseline | Make the benchmark executable, record baseline, then confirm target, editable files, and time budget |
| **Ratchet** | Implement and run the agreed tests until all pass | Optimize and measure until the target is reached or time expires |
| **Prove** | Compare baseline and final test results; deliver the feature and handover evidence | Compare baseline and final score; deliver the best verified result and stop reason |

A feature test is an executable acceptance case; the feature may need a set of them. An optimization test is exactly one numeric objective: one benchmark or a fixed weighted sum of several benchmarks. Component readings are diagnostics, not separate acceptance targets.

## Progressive disclosure

Use the current stage as the reading key. On entry, read its shared instructions and the applicable scenario; do not preload later stages. Read [test design](references/test-design.md) only when acceptance cases or a composite benchmark need more detail.

## Define

Read [Define](references/define.md).

For a feature, establish whether modules may be added or removed and whether existing workflows may change. Then draft tests with the human and revise until the human confirms what they should prove.

For optimization, first agree on the single benchmark, its inputs, numeric output, direction, and measurement method. Do not substitute the easiest metric to improve.

Reuse explicit decisions already supplied by the human. Confirmation concerns test meaning, not merely permission to write code; there is no fixed question count. Do not begin implementation while acceptance remains ambiguous.

## Anchor

Read [Anchor](references/anchor.md).

For a feature, reconcile the existing suite with the approved behavior before recording the baseline. Outdated tests may be changed or removed; still-relevant tests stay. “Tests can run” means execution produces meaningful results, not that the unimplemented feature already passes.

For optimization, run the approved benchmark to obtain the baseline **before confirming loop limits**: target, editable files, and wall-clock budget. Separate benchmark preparation from optimization work.

Preserve the approved test version, command, conditions, and raw baseline results. Implementation starts only after this evidence and the required permissions exist.

## Ratchet

Read [Ratchet](references/ratchet.md).

Develop within the approved feature scope until all agreed tests pass. For optimization, keep the best valid measured candidate and stop when the target is met or the time budget expires; neither invent a convergence stop nor extend the budget silently.

Keep the measuring test stable during iteration. Never weaken assertions, shrink workloads, alter weights, or edit the benchmark to manufacture success. A changed requirement, scope, or test meaning returns to Define and requires a new baseline, not a rewritten history.

## Prove

Read [Prove](references/prove.md).

Deliver the actual baseline/final comparison, reproduction commands, changed modules and workflows, known limitations, and the evidence needed to continue the work. Use a readable test matrix or score/history table; add a diagram or chart when it explains the change better.

All feature tests must pass to claim completion. An optimization that times out must state whether its target was met and what improvement, if any, was verified. Never substitute an explanation or an illustrative chart for measured results.
