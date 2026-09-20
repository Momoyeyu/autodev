# Prove

Read when the feature test set passes or optimization reaches its target or deadline. Deliver an inspectable result and enough context for the human to understand, verify, and take over the work.

## Feature development

Run the complete agreed test set on the delivered source state under comparable conditions. Compare with the baseline recorded after test reconciliation, using the same test version and case IDs.

| Approved case / behavior | Baseline | Final | Evidence |
|---|---|---|---|
| stable case ID and expected outcome | recorded pass/fail | recorded pass/fail | command output or artifact |

Report passed, failed, and unexecuted cases; identify relevant regressions and explain which approved behaviors changed. All agreed tests must pass to claim completion. A skipped, blocked, or unrun required case is not a pass.

Include the test-reconciliation record so removed or changed tests are explained by approved requirements, not mistaken for implementation gains. Do not compare raw totals from different suites as evidence of feature completion.

## Performance optimization

Verify the best candidate with the approved benchmark inside the reserved time. If no rerun fits the budget, use its existing valid measurement only when the source state, test version, and conditions still match; clearly state that no fresh rerun was performed. Otherwise mark verification incomplete.

| Measure | Baseline | Delivered result |
|---|---|---|
| approved score and unit | recorded value | recorded value |
| test and workload identity | version / hash | same identity |
| measurement conditions | recorded conditions | comparable conditions |

Report the target, direction, absolute and relative change, actual time spent, and whether the stop was **target reached** or **time budget exhausted**. Keep the original baseline as the comparison point, not the previous best attempt.

Positive improvement is `baseline - final` for lower-is-better and `final - baseline` for higher-is-better. Relative improvement divides by the absolute baseline; at a zero baseline, report the absolute change and mark the percentage not applicable. Preserve raw samples and any uncertainty instead of presenting noise as a demonstrated gain.

For a weighted benchmark, show the fixed formula and component readings for transparency. They explain the one score; they are not additional optimization verdicts. If nothing improved, say so and deliver the unchanged best verified state.

## Verifiable, measurable, visible handover

Deliver:

1. **Outcome:** what was requested, what is complete, and what remains unmet.
2. **Verification:** approved test definition/version, exact commands, working directory, necessary environment/data, and raw baseline/final results.
3. **Impact:** changed files and modules, architecture or workflow changes, and how they match the approved scope. State explicitly when those boundaries stayed unchanged.
4. **Visible comparison:** a case matrix for features; a score table and, when useful, an attempt trend for optimization. Use an architecture or before/after flow diagram when it clarifies the impact.
5. **Takeover:** entry points, operational steps, relevant decisions and rejected approaches, limitations, and the next unresolved action.

Use existing reporting tools when available; readable Markdown tables are sufficient. Charts must come from recorded results and share their source data. Label illustrative examples as examples; never present them as measured evidence.

Do not hide a changed test, scope exception, unfinished check, or missed target behind a polished summary. If final verification contradicts the claim, return to implementation within its approved limits or deliver an explicit incomplete result.
