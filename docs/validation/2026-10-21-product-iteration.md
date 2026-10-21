# Product iteration checks — 2026-10-21

This record distinguishes implementation checks from product-effectiveness evidence. No production user study or SWE-bench experiment was executed in this iteration. The next product trials are proposed in [the evaluation plan](../evaluation.md).

## Skill instruction-following probes

Two isolated agent contexts read the old and revised guidance and produced abbreviated actions and developer-facing artifacts for the same three situations. These were qualitative action/artifact probes, not executed coding tasks, a controlled effectiveness experiment, or industrial validation.

| Situation | Old guidance application | Revised guidance application |
|---|---|---|
| Obvious one-file UI typo, no explicit invocation | Broad feature/bugfix trigger permitted the full Clarify/worktree/approval sequence | Direct local edit and proportionate existing check; no autodev contract or diagram ceremony |
| Approved billing retry change; only persistence changed and full regression fails | Commit/check/status required, but partial diagrams were optional until completion | Actual partial flow, failing ledger path, unchanged API/worker, AI review notes, progress snapshot, and next diagnostic step; no checkpoint approval |
| Diagram claims complete and unit command green; production-critical DB concurrency untested | Honesty rules existed, but the mechanical exit and final-only drawings could overstate coverage | Explicit incomplete delivery, missing integration evidence, actual-code review, and a proposed acceptance change if needed; matching topology is not a defect |

The revised probe correctly kept a prior ledger failure unresolved when no new passing evidence was supplied, and did not invent a commit, command result, or report path. It also identified an ambiguity between diagnostic checks and new acceptance checks. The verification reference now states that diagnostics may run within the existing agreement; a changed acceptance command, target, frozen input, or scope returns to Clarify.

## Tool regression checks

New behavior was tested with temporary Git repositories and real subprocesses. Tests were first observed failing before implementing the new paths. Important cases include:

- Progress snapshots expose current source, actual recorded outcomes, review limits, and the next action.
- Partial as-built state can be shown while development remains incomplete.
- Snapshot generation leaves the approved handoff HTML, chart, caption, contract, and approval unchanged.
- A custom progress output cannot overwrite the protected handoff packet or chart evidence.
- Dirty or unjudged working changes are explicitly distinguished from recorded checks.
- A measured baseline can be inspected before Loop starts.
- Stable component IDs and a matching target/as-built topology are allowed; element claims, dependencies, configured checks, and semantic review remain required.
- Regenerating a final packet requests review rather than repeating its previous approval or suggesting immediate merge.
- No-check manual delivery asks for review/approval directly; an unsupported verify call preserves its report.
- The preceding quick fixes remain covered: command-side frozen modifications/deletions, rerun drift, failed verification, stale approval, and report/source provenance.

Final command:

```sh
python3 -m unittest discover -s tests -q
```

Final result: **155 tests passed** (75.680 seconds). `git diff --check` passed. The SVG generator reproduced the current assets without changes, all 12 SVG assets parsed as XML, and the checked local Markdown links resolved. Script tests verify tool behavior in their fixtures; they do not show that AI choices, real task outcomes, or industrial workflows are correct.

## Visual and documentation checks

The ten bilingual README SVGs were parsed as XML, rendered at README width, and visually inspected. The current Archify comparison, renderer receipts, and English/Chinese captures are documented in [visuals.md](../visuals.md). Existing measured MoE and cann2026 SVGs are unchanged.

An actual `report --progress` page was generated from a partial, failing tool-test fixture and inspected at desktop width and a true 430px browser viewport. The page visibly distinguishes agent-authored review, recorded checks, pending claims, target/current views, and next action. Its fixture is labeled a tool smoke test, not a production case. Diagrams and wide tables intentionally scroll within their sections on narrow screens; the page itself had 430px scroll width at a 430px viewport, and review text wrapped inside its section.

Local Markdown links were checked for the READMEs, contribution guide, installed references, evaluation plan, and visual documentation. Bilingual heading/table parity, documented flags, standard-library rendering, and whitespace checks were also run.

## Independent review

A fresh reviewer examined optional selection, retained Clarify detail, source provenance, progress/final separation, manual verification, and evidence limits. It found a real takeover issue: once a manual-check packet existed, `status` still suggested an unsupported `verify`, and that failed invocation cleared the packet. Regression tests demonstrated both failures before the fix. The next action now requests review/approval once evidence is current, and the unsupported command exits before invalidating manual evidence.

## What remains unproven

- Whether developers voluntarily choose autodev for consequential changes and avoid it for routine work.
- Whether actual system views stay accurate and help reviewers detect misunderstandings earlier.
- Whether the all-in cost of clarification, visual updates, checks, and review is worthwhile.
- Whether takeover and follow-up changes improve across maintained production projects.

These questions require real task use and maintainer feedback. Benchmark scores, a polished image, or this regression suite cannot replace that evidence.
