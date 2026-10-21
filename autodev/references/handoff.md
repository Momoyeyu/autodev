# Handoff

Read when preparing delivery, including an incomplete or blocked result. The required primary artifact depends on the scenario: **as-built diagrams** for feature development, **the passing test set** for a bug fix, or **one optimization process chart**. Show unresolved failures and missing evidence without claiming completion.

Each artifact is checked against the approved target — blueprint, test set, or benchmark — and the original baseline. Add only the reproduction details and context needed for the human to verify, understand, and take over the result.

## Review the claim before presenting it

Read [Verification](verification.md) and compare the actual code and important paths with the approved target and preserved behavior. Update `review.md` with what the checks establish, AI assessment, unverified conditions, and takeover instructions. The report displays these notes separately from recorded command outcomes. Missing required evidence means incomplete or blocked delivery; a green command or complete diagram coverage cannot substitute for this review.

## Present the artifact

The review packet is `report`'s output: run `autodev_verify.py --home <contract dir> report`, which writes a self-contained `handoff.html` — every scenario's deliverable rendered inside one page — and prints a manifest with its absolute path and an `open` command. Put it in front of the human, not in prose:

- if the platform has a preview mechanism, open `handoff.html` with it (or pass `report --open` to let the judge try `open`/`xdg-open`);
- otherwise print the absolute path and the manifest's `open` command verbatim in the final message.

A summary without the opened page or the path-plus-command is an incomplete handoff. The same rule applies to blocked or partial results — the page shows real state either way.

A generated `handoff.html` is evidence awaiting review, not a delivery. When a check or guard is configured, run a successful `verify` on the retained commit, then `report`. The page shows the latest verification outcome, including failures. Without a check or guard it says verification is not configured; review remains manual.

Once the human has seen the packet and agrees, record it with `autodev_verify.py --home <contract dir> approve` — a timestamped contract entry, a protocol marker like the Clarify review, not a cryptographic proof. The command requires a clean worktree at `best`, unchanged frozen files and constitution, successful current verification when configured, and a current report. Approval binds the commit, verification record, and report hash. A kept attempt, new verification, or regenerated or changed report invalidates approval. Failed verification blocks approval; reports of incomplete results can still be generated for inspection. `status` names the next missing step and only suggests merge-back after a valid approval.

Reports capture the actual source commit and cleanliness when generated. A packet drawn from dirty or unjudged code remains ineligible for approval even if the worktree is later reset to `best`; regenerate it from the retained state.

## Feature development: as-built diagrams

Deliver the architecture and flow diagrams **drawn from the delivered state**, as diagram JSON at the agreed `--asbuilt` path, updated from the actual code throughout Loop. The blueprint describes the agreed target; the as-built diagrams describe what was actually built. Matching topology is legitimate when code inspection supports it; do not redraw or rename elements merely to make the files differ. If the two disagree, the development is wrong: return to [Loop](loop.md#feature-development) instead of handing off.

`report` renders both diagrams side by side in `handoff.html`: the element-coverage table with each element's dependencies, the commit that realized it, and whether the as-built file covers it; the build order; and a dependency graph colored by progress.

Explain meaningful divergences the human approved along the way — an element realized differently, a boundary moved — rather than hiding them. A silent mismatch means the loop exited early; a documented, approved one belongs in the handoff text. Include the regression check's final raw output and the rerun command.

## Bug fix: the passing test set

Deliver the agreed test set passing on the delivered state: the reproduction case and every agreed regression case green, under the same test version and comparable conditions as baseline.

`report` writes `handoff.html` with a baseline → final stat strip and one row per run — baseline plus every attempt — each linking its raw log. Expand on it in your message with stable case IDs or agreed groups from those logs: distinguish failed, skipped, blocked, and unrun cases. Every agreed test must pass to claim the bug is fixed.

Compare the same test version. Outdated-test removal happened in Clarify and must not be counted as a fix gain. Summarize relevant changes and provide the exact rerun command.

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

`report` renders the chart from `attempts.jsonl` with exactly these elements — inline in `handoff.html` plus a standalone `process.svg` — and writes `caption.json` with headline values and each route's accepted, rejected, and invalid tallies; keep the source data. If execution was blocked before any attempt or no attempt produced a valid new score, show the real baseline and annotate that outcome instead of fabricating progress. If chart generation is blocked, preserve the data and report the handoff as incomplete rather than silently falling back to a table.

Chart scores and headline values describe the recorded best. The report separately shows final verification, and `caption.json` includes `score_basis` and the verification record, so a failed rerun cannot be mistaken for a reproduced result.

Verify the delivered candidate within the reserved time with `autodev_verify.py --home <contract dir> verify`, which reruns the agreed command on `best` and records `raw/verify.log`. If only a prior measurement is available, reuse it only when source state, test version, and conditions match, and explicitly say it was not freshly rerun. Otherwise mark verification incomplete.

In the handoff text, give baseline/final values, actual time spent, target status, absolute/relative improvement, and the rerun command. For lower-is-better, improvement is `baseline - final`; for higher-is-better, it is `final - baseline`. Divide by the absolute baseline for a percentage; at zero baseline, report the absolute change and no percentage.

Summarize which routes worked and which were ruled out, so the human does not retry dead ends.

For a weighted score, include the fixed formula and retain component readings with the evidence. They explain the one score, not additional optimization objectives. A timeout can end the work without meeting the target; state that plainly.

## Merge back and remove the worktree

Only after `approve` is recorded. The delivered state is the loop branch's final commit: the completed blueprint state for a feature, the passing checkpoint for a bug fix, `best` for an optimization. Verify it there, then merge the loop branch into the branch the user was on when Loop started, with a regular merge so the attempt history stays visible. If the merge conflicts with work the user did meanwhile, stop and report; do not resolve it by force or rewrite the user's branch. After a clean merge, remove the worktree and the loop branch. Ignored build products disappear with the worktree.

If the human is not satisfied with a handoff, the follow-up is a new autodev round — typically a bug fix against the concrete problem — not a resume of the closed loop.

## Progress snapshots are not delivery packets

`report --progress` writes `progress.html` and separate progress chart files without changing the handoff packet or approval. It is for observing partial work. A final delivery still requires `verify`, `report` without the progress flag, human review, and `approve` as described above. Snapshot generation alone does not establish completion.

## Keep the handoff trustworthy

If a constraint had to be agreed again that an earlier round also needed, propose adding it to the [constitution](constitution.md); the human decides.

Tie the artifact to raw results, source identities, execution conditions, and the delivered changes. Every verdict in `attempts.jsonl` points to its `raw/attempt-NNN.log`; `handoff.html` links them so the human can trace each round. Note limitations and any unresolved next action concisely. Never use fabricated measurements or a polished visual to conceal missing verification.
