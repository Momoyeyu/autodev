# Clarify: bug fix

Read for a defect report, alongside the shared [Clarify](clarify.md) rules. The target of this scenario is a **passing test set**: an agreed group of unit, integration, or smoke tests that reproduce the bug and guard the fix. One pass runs steps 1–3 in order; the human reviews the whole pass in step 4. Do not fix the bug during Clarify.

## 1. Prepare runnable tests

A bug report usually names the concrete failing case, which makes the tests easier to pin down than in feature work. Test maintenance happens here, before baseline, not after approval:

1. **Write the reproduction test first.** Turn the reported case into a test with a stable ID and an observable expected outcome. It must fail on the unchanged source — a reproduction that already passes does not capture the bug.
2. **Query existing tests.** Map coverage around the defect area and identify outdated expectations and missing regression cases.
3. **Remove or update outdated tests.** Explain how each change follows from the bug report. Keep still-relevant tests and regressions; do not discard a test merely because it fails.
4. **Add missing regression tests.** Cover the boundaries and adjacent behaviors the fix must not break, using the project's existing tools.
5. **Verify the tests can run.** Check discovery, dependencies, fixtures, and execution. Trial runs must produce meaningful results; failure caused by the bug is valid, while unrelated setup errors need repair.

"Can run" does not mean "already passes." Do not fix the bug merely to obtain a green trial run.

Judge test changes by what they still constrain. For every removed or changed test, show the old and new expectation side by side and state which behavior it constrained and where that behavior is now covered. Flag anything that widens accepted results, narrows inputs, adds skips or expected failures, or moves a check behind a condition. The reproduction test must fail against the unchanged source; regression cases must pass there. During Loop the test files are frozen and hash-checked, so this review is the only point at which weakening can enter.

## 2. Capture baseline

Run the prepared test set on the pre-fix source state. Record case IDs, actual outcomes, failure reasons, totals, the command, and test/source identities. The reproduction case should appear in the baseline as a failure.

This baseline uses the reconciled suite. Removing outdated tests is preparation, not a fix gain. Use the same test version and comparable conditions for the final results.

## 3. Propose the impact

Inspect the relevant code and make the proposed changes and preserved behavior explicit, informed by which baseline cases fail and why.

| Boundary | Propose for the human's confirmation |
|---|---|
| Editable files | Explicit paths the fix may change; the agreed test files stay outside them |
| Existing workflows | Which flows are affected? May their outputs or side effects change? Which behavior must remain compatible? |

A bug report is not unrestricted permission to redesign the surrounding code.

Write the proposal as a contract with the judge script, from the user's checkout, into a directory outside the repository (pass `--home` as an absolute path; every later command uses the same value):

```bash
python3 <skill>/scripts/autodev_verify.py --home ../<repo>.autodev init \
  --scenario bugfix --editable src/ --frozen tests/ \
  --test-cmd "pytest -q tests/"
```

`--editable` is the file-level form of the permitted impact; `--frozen` is the agreed test set, which Loop may not edit. `init` runs the tests once more to record the baseline and its raw output and prints the contract for the human to review in step 4.

## 4. Human review of the whole pass

Show the runnable tests, the old/new expectation for every changed or removed test, the baseline results with any coverage gaps, and the proposed impact, together. The human decides:

- **Revise:** apply the feedback and repeat from step 1. Rerun baseline on the updated suite; a changed test set needs a new baseline, so rerun `init --renew`.
- **Approve:** record the approved tests, baseline, and impact, then enter Loop.

If the reproduction test passes at baseline, say so in the review: either the bug is already fixed, the test does not capture it, or the environment differs. An approved all-green baseline still requires final verification and the passing test set in [Handoff](handoff.md#bug-fix-the-passing-test-set).

**Exit:** the human has approved one complete pass — runnable tests, their baseline, and the permitted impact. Continue to [Loop: bug fix](loop.md#bug-fix).
