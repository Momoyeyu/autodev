---
name: autodev
description: Use for features, bug fixes, refactoring, and optimization of latency, throughput, size, memory, cost, build time, or model quality. Prove correctness with TDD and improvement against frozen benchmarks.
---

# autodev

TDD is the **correctness gate**; the ratchet is the **progress gate**. Follow **Define → Anchor → Ratchet → Prove** and deliver evidence the user can run again.

## Three rules

1. **Measure first.** Establish a runnable criterion and verify the starting state before implementation.
2. **Protect the ruler.** Edit only the agreed `surface`; keep tests, benchmarks, and other `frozen` inputs protected.
3. **The script decides.** Accept verified progress; otherwise restore the last accepted state. Prose cannot override a verdict.

## Two modes

| Request | Mode | Success | Budget |
|---|---|---|---|
| add / implement / fix X | development | relevant test RED → GREEN; suite green | none |
| make X faster / smaller / cheaper | optimization | tests green; metric beats baseline beyond noise | required |
| add X with a measurable limit | optimization | both gates pass | required |
| make X “better” without a runnable criterion | stop and ask | agree on a measurable outcome before editing | — |

Infer the mode; never ask the user to choose it. Both modes require TDD for new behavior. Split large development tasks into verifiable units, not timed attempts.

## Reference files

Do not preload references. Read only the file needed for the next action; paths are relative to this skill directory.

| Read | When |
|---|---|
| [Correctness gate](references/gate.md) | Before changing production code or tests, in either mode |
| [Define: the contract](references/contracts.md) | During Define for optimization, or when contract design needs detail |
| [Progress gate](references/progress-gate.md) | Before Anchor in optimization; use through Ratchet and Prove |
| [Testing anti-patterns](references/testing-anti-patterns.md) | Only when adding or changing mocks, test utilities, or test-only APIs |
| [Worked testing examples](references/testing-examples.md) | Only when the TDD sequence needs an example; read the relevant section |

## Phase 0 — Define

Confirm six fields: `goal` (falsifiable outcome), `criterion` (one gate command), `budget` (optimization attempts/time; none for development), `frozen` (protected files/conditions), `surface` (editable paths), `reset` (exact scoped restore).

Ask only for missing information: at most two questions, then one contract confirmation. In optimization, ask ambiguous metric/target and absent budget. Offer concrete choices, a recommendation, and a custom option; include attempt/time limits. Never ask what you can infer or measure.

Wait for confirmation before Anchor or implementation. If the gate is missing, build and verify it with TDD first, then confirm the optimization contract.

## Phase 1 — Anchor

Hash `frozen` files. Development: verify RED for the expected missing behavior. Optimization: record a fixed-repeat median baseline and measured noise. Deterministic metrics: `repeats: 1`, noise `0`; noisy metrics: `repeats ≥ 5`.

Keep one untracked root-level TSV with contract, hashes, and starting evidence. Columns: `attempt, commit, tests, metric, delta, verdict, note`; metric/delta stay blank in development. Freeze verified acceptance tests before implementation; never weaken assertions.

## Phase 2 — Ratchet

Read the log, choose an idea, edit only `surface`, and run the gate. Save output to artifacts. Check frozen hashes before/after every attempt; log every verdict, including failures.

| Result after implementation | Verdict |
|---|---|
| crash, failing tests, or changed frozen inputs | reject and restore |
| development: verified RED → GREEN and full suite passes | accept |
| optimization: improvement exceeds `δ = max(minimum improvement, measured noise)` | accept; advance baseline |
| optimization: improvement does not exceed δ | reject and restore |

Commit accepted states. Normalize improvement so positive means better; compare it and δ in the same units. Restore only the attempt's implementation paths, preserving tests, log, and pre-existing user work. Never use `git reset --hard`.

**Anti-gaming:** assertion count must not fall; no `.skip`, `xfail`, or loosened tolerances. No new dependencies, network calls, or hardware branches. No smaller workload, cached answers, memoized benchmark inputs, or undeclared cache warming. Fix repetitions and use medians, never best-of-N.

**Optimization stops** at the first of: attempt/time limit, target met, three improvements below measured noise in a row, or four consecutive restorations. Report and offer to continue; do not ask mid-budget or exceed it. Development has no attempt/time budget.

## Phase 3 — Prove

Rerun the full gate from clean conditions. Refactor only while green, then remeasure. Equal metric with a simpler diff wins only under the agreed tie-break; restore regressions.

Deliver runnable evidence: tests, baseline/final metric and noise, accepted/rejected attempts, net improvement, actual cost, stop reason, and near-misses. Omit metric fields for development.
