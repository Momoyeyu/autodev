# Clarify: feature development

Read for a feature request, alongside the shared [Clarify](clarify.md) rules. Complete these steps in order before implementing the feature.

## 1. Confirm the impact

Inspect the relevant code and make the proposed changes and preserved behavior explicit.

| Boundary | Confirm with the human |
|---|---|
| Overall architecture | Which modules and interfaces are affected? May modules be added or removed? Which architectural boundaries must remain? |
| Existing workflows | Which user/system flows are affected? May their sequence, outputs, or side effects change? Which behavior must remain compatible? |

Record the permitted impact. A feature request is not unrestricted permission to redesign the project.

## 2. Co-create runnable tests until the human confirms

Test maintenance is inside this review cycle, not a task postponed until after approval:

1. **Query existing tests.** Map coverage to the intended behavior and identify outdated expectations and missing cases.
2. **Remove or update outdated tests.** Explain how each change follows from the requested behavior. Keep still-relevant tests and regressions; do not discard a test merely because it fails.
3. **Add missing tests.** Give cases stable IDs and observable outcomes. Cover meaningful inputs, boundaries, errors, and behavior that must remain unchanged, using the project's existing tools.
4. **Verify the tests can run.** Check discovery, dependencies, fixtures, and execution. Trial runs must produce meaningful results; failure caused by an unimplemented requested behavior is valid, while unrelated setup errors need repair.
5. **Review with the human.** Show the runnable tests, their meaning, maintenance reasons, trial results, and any coverage gaps. Revise and rerun as needed until the human confirms the test set.

“Can run” does not mean “already passes.” Do not implement the feature merely to obtain a green trial run. The agreed set includes retained coverage as well as updated and new cases; approval is not limited to the easiest passing subset.

## 3. Capture baseline

After confirmation, run the agreed test set on the pre-implementation source state. Record case IDs, actual outcomes, failure reasons, totals, the command, and test/source identities.

This baseline uses the reconciled suite. Removing outdated tests is preparation, not a development gain. Use the same approved test version and comparable conditions for the final results.

If every agreed test already passes, verify that the requested behavior genuinely exists. Avoid unnecessary implementation changes, but still follow [Handoff](handoff.md#feature-development-one-table): verify the delivered state and provide the baseline/final comparison table. Return to test review if the agreement missed part of the requirement.

**Exit:** impact is confirmed, executable tests are approved, and baseline results are preserved. Continue to [Loop: development](loop.md#feature-development).
