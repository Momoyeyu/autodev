# Handoff

Read when preparing delivery, including an incomplete or blocked result. The required primary artifact depends on the scenario: **as-built diagrams** for feature development, **the passing test set** for a bug fix, or **one optimization process chart**. Show unresolved failures and missing evidence without claiming completion.

Each artifact is checked against the approved target — blueprint, test set, or benchmark — and the original baseline. Add only the reproduction details and context needed for the human to verify, understand, and take over the result.

## Feature development: as-built diagrams

Deliver the architecture and flow diagrams **drawn from the delivered state**, in Mermaid at the agreed `--asbuilt` path — not the Clarify blueprint copied over. The blueprint describes the agreed target; the as-built diagrams describe what was actually built. If the two disagree, the development is wrong: return to [Loop](loop.md#feature-development) instead of handing off.

Start from `autodev_verify.py --home <contract dir> report`, which writes `blueprint-handoff.md`: the agreed blueprint and the as-built diagrams side by side, plus the element-coverage table showing every blueprint element ID found in the as-built file. Keep that structure and fill in anything the human needs to compare the two.

Explain meaningful divergences the human approved along the way — an element realized differently, a boundary moved — rather than hiding them. A silent mismatch means the loop exited early; a documented, approved one belongs in the handoff text. Include the regression check's final raw output and the rerun command.

## Bug fix: the passing test set

Deliver the agreed test set passing on the delivered state: the reproduction case and every agreed regression case green, under the same test version and comparable conditions as baseline.

Start from `autodev_verify.py --home <contract dir> report`, which writes `comparison.md` with the baseline and final runs of the agreed command and their raw-output paths. Expand it with stable case IDs or agreed groups from those logs, include totals, and link to the full execution evidence. A suitable structure is:

| Test / expected behavior | Baseline result | Final result | Evidence |
|---|---|---|---|
| case ID or agreed group | recorded outcome | recorded outcome | output or artifact location |

Populate it with actual results, not illustrative passes. Distinguish failed, skipped, blocked, and unrun cases. Every agreed test must pass to claim the bug is fixed.

Compare the same test version. Outdated-test removal happened in Clarify and must not be counted as a fix gain. Summarize relevant changes and provide the exact rerun command alongside the table.

## Performance optimization: one chart

Deliver a rendered chart showing **baseline → optimization attempts → final delivered result**. A table, final score, prose summary, or unrendered chart source does not substitute for this chart.

The chart must:

- use attempt order or elapsed time on the horizontal axis;
- use the one approved numeric score, its unit, and improvement direction on the vertical axis;
- identify the original baseline, valid measured attempts, and the delivered result;
- show the target and state whether the stop was target reached or time budget exhausted;
- distinguish rejected measurements from retained progress, so the last attempt is not mistaken for the delivered candidate;
- mark failed or timed-out attempts without inventing numeric values.

A best-so-far line may accompany the measured attempts, but label it as derived retained state. Do not hide regressions by plotting only favorable samples, smooth away failures, or join results from different test versions.

`autodev_verify.py --home <contract dir> report` renders `process.svg` from `attempts.jsonl` with exactly these elements and writes `caption.json` with the values below; use it unless the human asked for another format, and keep the source data. If execution was blocked before any attempt or no attempt produced a valid new score, show the real baseline and annotate that outcome instead of fabricating progress. If chart generation is blocked, preserve the data and report the handoff as incomplete rather than silently falling back to a table.

Verify the delivered candidate within the reserved time with `autodev_verify.py --home <contract dir> verify`, which reruns the agreed command on `best` and records `raw/verify.log`. If only a prior measurement is available, reuse it only when source state, test version, and conditions match, and explicitly say it was not freshly rerun. Otherwise mark verification incomplete.

In the chart caption or accompanying short text, give baseline/final values, actual time spent, target status, absolute/relative improvement, and the rerun command. For lower-is-better, improvement is `baseline - final`; for higher-is-better, it is `final - baseline`. Divide by the absolute baseline for a percentage; at zero baseline, report the absolute change and no percentage.

For a weighted score, include the fixed formula and retain component readings with the evidence. They explain the one score, not additional optimization objectives. A timeout can end the work without meeting the target; state that plainly.

## Merge back and remove the worktree

The delivered state is the loop branch's final commit: the completed blueprint state for a feature, the passing checkpoint for a bug fix, `best` for an optimization. Verify it there, then merge the loop branch into the branch the user was on when Loop started, with a regular merge so the attempt history stays visible. If the merge conflicts with work the user did meanwhile, stop and report; do not resolve it by force or rewrite the user's branch. After a clean merge, remove the worktree and the loop branch. Ignored build products disappear with the worktree.

If the human is not satisfied with a handoff, the follow-up is a new autodev round — typically a bug fix against the concrete problem — not a resume of the closed loop.

## Keep the handoff trustworthy

Tie the artifact to raw results, source identities, execution conditions, and the delivered changes. Every verdict in `attempts.jsonl` points to its `raw/attempt-NNN.log`; hand over the contract directory so the human can trace each round. Note limitations and any unresolved next action concisely. Never use fabricated measurements or a polished visual to conceal missing verification.
