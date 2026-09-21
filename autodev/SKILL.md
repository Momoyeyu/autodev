---
name: autodev
description: A clarify-first Agent Skill for feature development and performance optimization. Align human intent, runnable tests, baselines, and allowed changes before implementation; then iterate and hand off a feature comparison table or an optimization progress chart.
---

# autodev

Align the agent and the human to reduce natural-language misunderstanding and rework. Improve delivery quality, stability, and overall efficiency while helping the human understand and take over the project.

**Verifiable & measurable & visible:** the result must be easy to verify, possible to measure, and clear to inspect.

## Clarify → Loop → Handoff

User input starts the workflow; it is not another stage. Clarify is the core capability: test preparation, baseline measurement, scope proposal, and human review belong here, not in the implementation loop.

| Stage | Feature development | Performance optimization |
|---|---|---|
| **Clarify** | Prepare runnable tests; record baseline; propose architecture/workflow impact; the human reviews the whole pass | Prepare one runnable numeric test; record baseline; propose target, editable files, and time budget; the human reviews the whole pass |
| **Loop** | Develop until all agreed tests pass | Optimize until the target is met or the time budget expires |
| **Handoff** | One table comparing baseline and final test results | One chart showing the process from baseline through attempts to the final result |

## Read only what is needed now

| Reference | Load when |
|---|---|
| [Clarify](references/clarify.md) | Starting a task or revisiting its agreement |
| [Clarify: development](references/clarify-development.md) | Clarifying a feature request; do not load the optimization branch |
| [Clarify: optimization](references/clarify-optimization.md) | Clarifying a performance goal; do not load the development branch |
| [Loop](references/loop.md) | Agreement and baseline are ready; read shared rules and the relevant scenario |
| [Handoff](references/handoff.md) | Preparing the required result table or chart |

Do not preload the directory. Follow the current stage and scenario, keeping shared instructions with the selected branch.

## Clarify

Clarify is a human-in-the-loop cycle around the **whole pass**, not around each sub-step. Run one complete pass, present everything it produced, and let the human decide: revise and repeat Clarify, or enter Loop.

For features, one pass is: query existing tests, remove or update outdated ones, add missing ones, and verify they can execute; run them to record the baseline; then propose the architecture and workflow impact, including whether modules may be added or removed and existing flows changed.

For optimization, the test is exactly one numeric benchmark or one fixed weighted sum of benchmarks. One pass is: prepare and trial-run the test; measure baseline; then propose the target, editable implementation files, and wall-clock limit against that baseline.

The human reviews the runnable tests, the baseline result, and the proposed scope together. Use decisions already supplied; do not impose a question count or assume approval. Tests that can execute may still fail because the requested feature is absent. Preparing tests and measuring baseline are not permission to implement the requested change early.

## Loop

Change the implementation within the agreed boundaries and run the same test. Feature work ends only when all agreed tests pass. Optimization uses do-while order: optimize, measure and retain the best valid state, then check the target or time limit. Record every attempt for the final chart; do not bypass the first attempt merely because baseline meets the target.

Do not weaken tests, shrink workloads, alter benchmark weights, or change the measuring conditions to manufacture progress. Changes to intent, test meaning, or permitted scope return to Clarify and require a comparable new baseline.

## Handoff

The primary deliverable is mandatory: **a comparison table for a feature; a progress chart for an optimization**. A final number, prose summary, or table alone does not replace the optimization chart.

Use actual recorded results, the original baseline, and the delivered source state. Include concise reproduction details and relevant changes so the human can verify and take over. Report missed targets, blocked checks, and missing evidence honestly; do not label an incomplete handoff complete.
