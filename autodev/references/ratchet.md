# Ratchet

Read after Anchor. Iterate against the approved test and recorded baseline, with visible progress and no silent changes to what success means.

## Feature development

1. Read the approved architecture/workflow scope, acceptance cases, and baseline failures.
2. Implement a focused change inside that scope.
3. Run the relevant tests for feedback, then the complete agreed test set at each implementation checkpoint.
4. Record case results and remaining failures; use them to choose the next change.
5. Repeat until all agreed tests pass, then enter [Prove](prove.md#feature-development).

Partial progress is not completion, but a still-failing new case does not require discarding all useful development work. Keep implementation coherent, investigate regressions, and continue fixing the code rather than weakening tests.

Do not stop at a passing subset, skip a required case, or invent an optimization time budget for feature work. If the baseline already passes every approved case and the requirement is genuinely satisfied, verify and deliver that finding instead of manufacturing a failing test or an unnecessary change.

If implementation needs a new module, module removal, or workflow change outside the approved scope, return to Define. If a test is incorrectly implemented, return to Anchor; do not quietly repair the ruler while reporting progress against its old baseline.

## Performance optimization

Keep two distinct records: the **original baseline** for delivery and the **best valid result** for choosing candidates. Initialize the best result to the baseline.

1. Check the target and remaining time before starting an attempt. Start the clock at the agreed loop entry and bound long-running commands by the remaining budget.
2. Change only the approved implementation files. Keep a recoverable snapshot of the best candidate and preserve unrelated user changes.
3. Run the same benchmark, using the approved workload, repetitions, aggregation, and scoring formula.
4. Check measurement identities and the changed-file list. Reject crashes, invalid output, out-of-scope edits, and measurement tampering regardless of the reported number.
5. Compare the one score with the best valid result using the agreed direction and variability treatment. Keep a verified improvement; otherwise restore only this attempt's changes to the best state.
6. Record the attempt and check the stop conditions again.

### Stop conditions

- **Target reached:** the best valid score satisfies the confirmed threshold.
- **Time budget exhausted:** stop starting or extending attempts; restore any unverified in-flight candidate and retain the best verified result.

Do not add automatic convergence, rejection-count, or attempt-count exits. Do not extend the budget to chase a target. A timeout is an honest stopping result, not permission to claim the target was reached.

Reserve verification time inside the agreed budget. A timed-out benchmark has no valid score. If there is no verified improvement, retain and report the baseline state rather than shipping an unmeasured change.

Next: [Prove](prove.md#performance-optimization).

## Keep progress visible

Maintain a compact record in the repository's normal artifact location:

| Attempt | Source state / changed files | Test result or score | Elapsed time | Decision / next action | Raw evidence |
|---|---|---|---|---|---|
| baseline or attempt ID | revision or snapshot | recorded result | measured duration | continue / keep / restore / deliver | output path |

Show current stage, relevant results, and unresolved decisions without flooding the conversation with raw logs. Keep successes, failures, and discarded candidates so another person can resume without repeating them.

Do not shrink inputs, hardcode answers, skip cases, retune weights, or change benchmark conditions to manufacture progress. Scope and test changes require a return to the appropriate earlier stage. Follow repository commit policy; checkpointing never authorizes overwriting user work, resetting the whole repository, or rewriting shared history.

If an external dependency, permission, or environment blocks execution, report the blockage and last verified state. Do not fabricate results, spin indefinitely, or label blocked work complete.
