# Clarify: feature development

Read for a feature request, alongside the shared [Clarify](clarify.md) rules. One pass runs steps 1–3 in order; the human reviews the whole pass in step 4. Do not implement the feature during Clarify.

## 1. Prepare runnable tests

Test maintenance happens here, before baseline, not after approval:

1. **Query existing tests.** Map coverage to the intended behavior and identify outdated expectations and missing cases.
2. **Remove or update outdated tests.** Explain how each change follows from the requested behavior. Keep still-relevant tests and regressions; do not discard a test merely because it fails.
3. **Add missing tests.** Give cases stable IDs and observable outcomes. Cover meaningful inputs, boundaries, errors, and behavior that must remain unchanged, using the project's existing tools.
4. **Verify the tests can run.** Check discovery, dependencies, fixtures, and execution. Trial runs must produce meaningful results; failure caused by an unimplemented requested behavior is valid, while unrelated setup errors need repair.

“Can run” does not mean “already passes.” Do not implement the feature merely to obtain a green trial run. The prepared set includes retained coverage as well as updated and new cases, not only the easiest passing subset.

## 2. Capture baseline

Run the prepared test set on the pre-implementation source state. Record case IDs, actual outcomes, failure reasons, totals, the command, and test/source identities.

This baseline uses the reconciled suite. Removing outdated tests is preparation, not a development gain. Use the same test version and comparable conditions for the final results.

## 3. Propose the impact

Inspect the relevant code and make the proposed changes and preserved behavior explicit, informed by which baseline cases fail and why.

| Boundary | Propose for the human's confirmation |
|---|---|
| Overall architecture | Which modules and interfaces are affected? May modules be added or removed? Which architectural boundaries must remain? |
| Existing workflows | Which user/system flows are affected? May their sequence, outputs, or side effects change? Which behavior must remain compatible? |

A feature request is not unrestricted permission to redesign the project.

Write the proposal as a contract with the judge script, from the user's checkout, into a directory outside the repository (pass `--home` as an absolute path; every later command uses the same value):

```bash
python3 <skill>/scripts/autodev_verify.py --home ../<repo>.autodev init \
  --scenario development --editable src/ --frozen tests/ \
  --test-cmd "pytest -q tests/"
```

`--editable` is the file-level form of the permitted impact; `--frozen` is the agreed test set, which Loop may not edit. `init` runs the tests once more to record the baseline and its raw output and prints the contract for the human to review in step 4.

## 4. Human review of the whole pass

Show the runnable tests, their meaning and maintenance reasons, the baseline results with any coverage gaps, and the proposed impact, together. The human decides:

- **Revise:** apply the feedback and repeat from step 1. Rerun baseline on the updated suite; a changed test set needs a new baseline, so rerun `init --renew`.
- **Approve:** record the approved tests, baseline, and impact, then enter Loop.

If every prepared test already passes at baseline, say so in the review; the human may confirm the behavior already exists or point out what the tests missed. An approved all-green baseline still requires final verification and the comparison table in [Handoff](handoff.md#feature-development-one-table).

**Exit:** the human has approved one complete pass — runnable tests, their baseline, and the permitted impact. Continue to [Loop: development](loop.md#feature-development).
