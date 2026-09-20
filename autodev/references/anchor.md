# Anchor

Read after the human approves the test definition. Turn that definition into an executable measuring tool and record the starting state before feature implementation or performance changes.

## Feature development

Follow this order:

1. **Inspect existing tests.** Map relevant cases to the approved behavior. Identify retained coverage, outdated expectations, and missing cases.
2. **Update or remove outdated tests.** Change tests whose expectations are superseded by the approved requirement; record each reason. Keep tests for unchanged behavior and affected regressions. A failing test is not automatically outdated.
3. **Add missing tests.** Implement uncovered approved cases using the repository's existing tools. Match the specification, not a guessed implementation.
4. **Verify execution.** Confirm discovery, fixtures, dependencies, and the command produce meaningful results. Failures caused by absent requested behavior are valid; broken setup is not useful baseline evidence. Do not implement the feature just to make the baseline green.
5. **Run the agreed test set and record baseline.** Save per-case results, totals, failure reasons, command, environment, and starting source revision or snapshot.

The baseline uses the reconciled test set, not the obsolete suite. Test removal is preparation, not a claimed improvement. Use this same version for the final comparison.

Keep a compact reconciliation record:

| Case | Existing coverage | Action | Reason tied to approved behavior |
|---|---|---|---|
| approved case ID | test path or missing | keep / update / remove / add | requirement or compatibility decision |

If reconciliation exposes an unapproved behavior change, return to Define. Do not broaden the approved requirement to justify removing a test.

**Exit:** approved cases are executable, their baseline is recorded, and the implementation scope is clear. Next: [Ratchet](ratchet.md#feature-development).

## Performance optimization

### Measure before confirming loop limits

1. Locate the agreed benchmark or implement its approved definition. This is measurement preparation, not an optimization attempt.
2. Verify it performs the intended workload, rejects invalid results, and produces the agreed numeric output. Check that it can distinguish a known meaningful difference; a constant or fabricated score is not a benchmark.
3. Run the unchanged implementation under the approved measurement conditions. Record the baseline score, raw samples, aggregation, and variability where relevant. For a composite, retain component readings alongside the one score.
4. Show the measured baseline, then confirm the limits below. Reuse values already explicitly supplied; do not silently fill missing permissions or budgets.

| Limit | Required agreement |
|---|---|
| Target | Threshold on the approved score, including direction and whether equality counts; reaching it ends optimization early |
| Editable files | Explicit paths allowed to change; benchmark, scoring logic, data, weights, and other measurement inputs remain outside the optimization surface |
| Time budget | Wall-clock limit and loop start/deadline; include attempt measurements and reserve time for final verification |

Do not start the optimization loop without these limits. An attempt cap or a guess about convergence is not a substitute for the time budget. If the baseline already meets the confirmed target, no optimization attempt is needed.

Record hashes or equivalent version identities for the benchmark and measurement inputs. Keep workload, aggregation, weights, and environment comparable; do not improve the score by changing the ruler.

**Exit:** a valid numeric baseline and confirmed target, editable files, and deadline. Next: [Ratchet](ratchet.md#performance-optimization).

## Baseline record

Preserve the original baseline separately from later results. Include the approved test version, exact command and working directory, source state, inputs/environment, raw output, and interpreted result. Keep artifacts outside unrelated user work.

A test implementation defect requires repair in Anchor and a replay on the original source state; a change in test meaning requires renewed human approval in Define. In either case, retain the earlier record and identify the replacement baseline. Never compare results from different test versions as one continuous improvement.
