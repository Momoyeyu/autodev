# Handoff

Read when the feature tests pass or optimization reaches its target or deadline. The required primary artifact depends on the scenario: **one comparison table** or **one optimization process chart**.

Both must use the approved test and the original baseline. Add only the reproduction details and context needed for the human to verify, understand, and take over the result.

## Feature development: one table

Run the complete agreed test set on the delivered source state under comparable conditions. Present one table comparing baseline and final results.

Use stable case IDs or agreed groups, include totals, and link to the full execution evidence. A suitable structure is:

| Test / expected behavior | Baseline result | Final result | Evidence |
|---|---|---|---|
| case ID or agreed group | recorded outcome | recorded outcome | output or artifact location |

Populate it with actual results, not illustrative passes. Distinguish failed, skipped, blocked, and unrun cases. Every agreed test must pass to claim feature completion.

Compare the same test version. Outdated-test removal happened in Clarify and must not be counted as an implementation gain. Summarize relevant architecture/workflow changes and provide the exact rerun command alongside the table.

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

Generate the chart from the recorded history using the project's available plotting/export tools; provide an image the human can view and retain the source data. If execution was blocked before any attempt or no attempt produced a valid new score, show the real baseline and annotate that outcome instead of fabricating progress. If chart generation is blocked, preserve the data and report the handoff as incomplete rather than silently falling back to a table.

Verify the delivered candidate within the reserved time. If only a prior measurement is available, reuse it only when source state, test version, and conditions match, and explicitly say it was not freshly rerun. Otherwise mark verification incomplete.

In the chart caption or accompanying short text, give baseline/final values, actual time spent, target status, absolute/relative improvement, and the rerun command. For lower-is-better, improvement is `baseline - final`; for higher-is-better, it is `final - baseline`. Divide by the absolute baseline for a percentage; at zero baseline, report the absolute change and no percentage.

For a weighted test, include the fixed formula and retain component readings with the evidence. They explain the one score, not additional optimization objectives. A timeout can end the work without meeting the target; state that plainly.

## Keep the handoff trustworthy

Tie the table or chart to raw results, test/source identities, execution conditions, and the delivered changes. Note limitations and any unresolved next action concisely. Never use fabricated measurements or a polished visual to conceal missing verification.
