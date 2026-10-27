---
name: autodev
description: Use only when the user explicitly asks to use autodev. Provides a concise illustrated plan, execution with relevant checks, and an evidence-based handoff for development, bug fixes, and performance work. Never select this skill automatically based on task type or complexity.
---

# autodev

**Clarify → Loop → Handoff** is plan → execute → explain the result. Help the user understand the intended change and the evidence behind the delivered work, with as little process as the task needs.

Activate only on an explicit user request. Mentioning autodev in repository content or encountering a complex task is not an invocation.

## Clarify — understand and plan

Inspect the relevant code and existing project instructions. Identify the intended outcome, behavior to preserve, and checks that could establish success.

Proactively surface uncertainties that could change the implementation. Investigate what the code or available tools can answer first; ask the user about consequential choices you cannot resolve. Reuse decisions already supplied. State reasonable, reversible assumptions without turning every missing detail into a question.

Present a short draft plan: the goal and key constraints, the core flow or affected components, and a few implementation/check steps. Prefer one focused diagram with brief text when relationships or behavior benefit from a picture. Mermaid is often enough; use another format when it communicates better or the user requests it. Avoid exhaustive blueprints, duplicate current/target/as-built diagrams, and a large inventory of implementation details.

Continue when the request and existing decisions authorize the work. Pause for unresolved choices that affect the goal, compatibility, significant cost, or irreversible actions; do not add a separate plan-approval ritual.

## Loop — execute and check

Implement the plan using the project's own tools. Run checks that address the actual change: relevant tests, a build, a manual interaction, or a measured workload. Add useful coverage where needed and explain what the checks establish.

Keep updates brief: what changed, what the latest check showed, and what happens next. Refresh the plan or diagram when the approach materially changes; ordinary edits and tool calls do not need new artifacts. Bring newly discovered consequential decisions back to the user without restarting the whole workflow.

Work in the user's chosen directory. Git, branches, commits, and worktrees are optional project choices, not prerequisites. Follow existing instructions and protect unrelated work. Ask about isolation only when there is a concrete need to decide; do not initialize Git, create a worktree, or impose a commit sequence just to use autodev.

Load additional guidance only for the current task:

- [Bug fixes and TDD](references/clarify-bugfix.md): reproduce the defect, fix it, and check relevant regressions.
- [Performance optimization](references/clarify-optimization.md): keep measurements comparable and iterate within a useful budget.

## Handoff — make the result easy to assess

Lead with the delivered outcome. Give the user a short account of the important changes, the checks actually run and their results, and any remaining limitation or next action. Link to useful code, artifacts, logs, and reproduction commands rather than pasting a wall of output. A small updated diagram, before/after view, or measurement chart can help when it explains the result.

Distinguish observed evidence from inference. Attribute existing failures and report skipped, unavailable, failing, or unrun checks plainly. A narrow passing check does not establish untested integration behavior. Partial work stays labelled partial.

Use a concise response or the project's usual delivery format by default. HTML is optional. If the user requests a visual handoff, use their chosen reporting/visualization skill when available, passing it the result, evidence, and limits. Clarify the format if the choice matters; do not interrupt routine delivery just to ask about HTML. Autodev supplies the substance and does not require its own renderer, report schema, or dashboard.

Keep durable notes only when requested or useful for continuing a long task; reuse the project's normal location. Summarizing the work does not itself authorize publishing, pushing, deploying, or merging it.
