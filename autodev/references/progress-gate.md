# Progress gate: Anchor, Ratchet, Prove

Read before **Anchor** in optimization. Apply the contract from **Define** without weakening the [correctness gate](gate.md).

## Anchor: baseline and noise

1. Verify the confirmed gate. Record frozen-file hashes and fixed environment conditions.
2. Measure the unmodified baseline using the agreed workload, cache policy, and repeat count.
3. Record samples, median, and noise from the agreed spread calculation: one sample/zero noise for deterministic metrics; at least five samples for noisy ones.
4. Save the contract, accepted commit, hashes, baseline, and noise with the untracked experiment log.

A 3% noise floor cannot support a 1% improvement claim. Keep repeats and statistic fixed; never rerun for luck.

## Ratchet: one attempt

1. Read the log; prefer near-misses, simplification, then new ideas.
2. Edit only `surface`; new behavior needs verified RED first.
3. Check frozen hashes before/after. Run the agreed gate; save output.
4. Apply and log the verdict, including crashes and failures.
5. Accept: commit and advance baseline. Reject: restore the attempt.

### Mechanical verdict

Improvement is `baseline - result` for lower-is-better, `result - baseline` for higher-is-better. Convert percentage thresholds to metric units using the accepted baseline. Compare against `δ = max(minimum improvement, measured noise)` in the same units.

| Condition | Verdict |
|---|---|
| crash, tests fail, frozen hash changes, or anti-gaming violation | reject and restore, regardless of metric |
| improvement > δ | accept; baseline becomes result |
| improvement ≤ δ | reject and restore |

An equal-metric, simpler-diff tie-break applies only during Prove, never to a worse metric.

### Scoped restore

Use the confirmed `reset`, for example:

```bash
git checkout <accepted-commit> -- <implementation-paths>
```

Isolate the accepted state from pre-existing user changes first. Plan separately for newly created implementation files; this command restores tracked paths only. Preserve the log, frozen inputs, and verified tests. Never reset the whole repository.

A changed frozen hash invalidates the attempt. Undo only that attempt's tampering against the recorded frozen state before continuing; do not adopt a changed ruler.

### Experiment log

Keep one untracked root-level TSV with contract and Anchor evidence. Append every attempt; `commit` is the retained accepted state, positive delta is improvement.

```tsv
attempt	commit	tests	metric	delta	verdict	note
0	a1b2c3d	pass	184.2	0	baseline	initial state
1	b2c3d4e	pass	171.5	12.7	accept	preload hero image
2	b2c3d4e	fail	—	—	reject	inline CSS broke tests
3	b2c3d4e	pass	183.9	-12.4	reject	memoization regressed
```

Failures and near-misses prevent a resumed session from retrying discarded ideas.

### Stop conditions

Stop at the first condition reached:

| Condition | Trigger |
|---|---|
| **Budget spent** | attempt or wall-clock limit, whichever comes first |
| **Target met** | accepted metric crosses the target in its direction |
| **Converged** | three consecutive attempts improve below measured noise |
| **Stuck** | four consecutive restorations |

Report the log and offer to continue. Do not ask mid-budget or exceed the limit. Development has no attempt/time budget.

## Prove: clean verification

Rerun from clean conditions: tests, hashes, fixed repetitions, median, noise checks. Refactor while green, then remeasure; restore regressions. Equal metric with a simpler diff wins only under the confirmed tie-break.

Deliver command, contract, hashes, tests, baseline/final measurements, accepted/rejected attempts, actual attempt/time cost, stop reason, and near-misses. Identify missing or unrun checks.
