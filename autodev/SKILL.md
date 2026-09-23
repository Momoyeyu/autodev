---
name: autodev
description: A clarify-first Agent Skill for feature development, bug fixes, and performance optimization. Align the human on a target — blueprint, passing test set, or benchmark threshold — before implementation; then iterate inside a judged loop and hand off as-built diagrams, the passing tests, or a progress chart.
---

# autodev

Align the agent and the human to reduce natural-language misunderstanding and rework. Improve delivery quality, stability, and overall efficiency while helping the human understand and take over the project.

**Verifiable & measurable & visible:** the result must be easy to verify, possible to measure, and clear to inspect.

## Clarify → Loop → Handoff

User input starts the workflow; it is not another stage. Clarify is the core capability: agreeing on the **target**, capturing the baseline, proposing the scope, and human review belong here, not in the implementation loop. The target differs per scenario:

- **Feature development** — a blueprint: agreed architecture and flow diagrams.
- **Bug fix** — a passing test set: reproduction plus regression cases.
- **Performance optimization** — a numeric score reaching an agreed threshold.

| Stage | Feature development | Bug fix | Performance optimization |
|---|---|---|---|
| **Clarify** | Draw as-is diagrams; draft the blueprint; propose editable scope; the human reviews the whole pass | Prepare runnable tests; record baseline; propose impact; the human reviews the whole pass | Prepare one runnable benchmark; record baseline; propose target, editable files, and time budget; the human reviews the whole pass |
| **Loop** | Implement until the as-built state realizes every blueprint element and checks stay green | Fix until all agreed tests pass | Optimize until the target is met or the time budget expires |
| **Handoff** | As-built architecture and flow diagrams, checked against the blueprint | The agreed test set passing | One chart showing the process from baseline through attempts to the final result |

## Read only what is needed now

| Reference | Load when |
|---|---|
| [Clarify](references/clarify.md) | Starting a task or revisiting its agreement |
| [Clarify: development](references/clarify-development.md) | Clarifying a feature request; do not load other branches |
| [Clarify: bug fix](references/clarify-bugfix.md) | Clarifying a defect report; do not load other branches |
| [Clarify: optimization](references/clarify-optimization.md) | Clarifying a performance goal; do not load other branches |
| [Loop](references/loop.md) | Agreement and baseline are ready; read shared rules and the relevant scenario |
| [Handoff](references/handoff.md) | Preparing the required artifact |

Do not preload the directory. Follow the current stage and scenario, keeping shared instructions with the selected branch.

`scripts/autodev_verify.py` (Python 3, standard library) is the judge for the Loop. Clarify writes the agreement into it with `init`; Loop runs `start`, then `attempt` and `status` every round; Handoff runs `report`. It enforces the frozen surface, the editable scope, the time budget, the direction-bound comparison, blueprint-element coverage, and the rollback, and it keeps the raw output for every verdict. The rules below describe what it does and what remains your responsibility.

## Clarify

Clarify is a human-in-the-loop cycle around the **whole pass**, not around each sub-step. Run one complete pass, present everything it produced, and let the human decide: revise and repeat Clarify, or enter Loop.

For a feature, one pass is: draw the as-is architecture and flow diagrams from the actual code; draft the to-be blueprint in Mermaid with stable element IDs; then propose the editable scope, including whether existing tests stay frozen or the blueprint may change them.

For a bug fix, one pass is: write the reproduction test that fails on the unchanged source, query existing tests, remove or update outdated ones, add missing regressions, and verify the set executes; run it to record the baseline; then propose the impact.

For optimization, the benchmark is exactly one numeric measure or one fixed weighted sum. One pass is: prepare and trial-run the benchmark; measure baseline; then propose the target, editable implementation files, and wall-clock limit against that baseline.

The human reviews the prepared artifact, the baseline, and the proposed scope together. Use decisions already supplied; do not impose a question count or assume approval. Tests that can execute may still fail because the bug is present. Preparing artifacts and measuring baseline are not permission to implement the change early.

## Loop

Work in a dedicated git worktree and branch created at Loop entry; every attempt is a commit judged by `autodev_verify.py attempt`, and an invalid attempt is rolled back with `git reset --hard` to the best commit. For a feature, implement the blueprint element by element, then draw the as-built diagrams at the agreed path covering every element ID; `status` reports `handoff` only when coverage is complete and the regression check is green — and if the as-built state does not truly match the blueprint, keep looping. For a bug fix, develop until all agreed tests pass. For optimization, use do-while order: optimize, measure and retain the best valid state, then check the target or time limit. Record every attempt for the final artifact; do not bypass the first attempt merely because baseline meets the target.

Do not weaken tests, shrink workloads, alter benchmark weights, change the measuring conditions, or copy the blueprint into the as-built file to manufacture progress. Changes to intent, target meaning, or permitted scope return to Clarify and require a comparable new baseline.

## Handoff

The primary deliverable is mandatory: **as-built diagrams for a feature, the passing test set for a bug fix, a progress chart for an optimization**. A final number, prose summary, or table alone does not replace them.

Use actual recorded results, the original baseline, and the delivered source state. Merge the loop branch back into the branch the user started from, then remove the worktree. Include concise reproduction details and relevant changes so the human can verify and take over. Report missed targets, blocked checks, and missing evidence honestly; do not label an incomplete handoff complete.
