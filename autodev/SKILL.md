---
name: autodev
description: Use when consequential changes in an existing codebase need explicit scope alignment, visible execution, and reviewable verification, such as cross-module features, high-impact fixes, or constrained performance work. Usually skip obvious local edits and quick fixes unless explicitly requested.
---

# autodev

Make consequential changes understandable before implementation, inspectable during execution, and verifiable at handoff. Keep a shared picture of **what changes, what stays intact, and what evidence supports the result**.

## Choose deliberately

Use for changes whose misunderstandings or regressions are expensive: interacting services, compatibility constraints, stateful flows, migrations, or costly optimization. Repository size alone is not the trigger; a small authorization change may warrant this workflow while a typo in a large application does not. Follow explicit invocation; otherwise handle routine local work directly without adding this ceremony.

AI inspects code, interprets failures, judges whether checks cover the intended behavior, and explains uncertainty. The bundled tools check recorded constraints and execution facts. Neither a diagram nor a green command proves the whole feature correct.

## Clarify → Loop → Handoff

| Stage | Work | What the human sees |
|---|---|---|
| **Clarify** | Inspect the affected system, prepare the target, measure baseline, propose scope, then review the whole pass once | Current state, intended change, preserved behavior, baseline, and consequential open decisions |
| **Loop** | Implement inside the agreement, check each attempt, and keep the visible state current at meaningful checkpoints | Actual partial state, observed results, failures or gaps, and next action |
| **Handoff** | Review the delivered code against the agreement, rerun checks, and present evidence for approval | What was built, what was verified, what remains unverified, and how to reproduce or take over |

The target is a blueprint for development, an agreed test set for a bug fix, or one numeric benchmark for optimization. Keep the full scenario-specific clarification; do not replace it with a generic planning conversation. Reuse decisions the human has already supplied. Clarify prepares concrete artifacts and baseline before asking for review; it does not ask for approval after each substep.

## Load only what is needed

| Reference | Read when |
|---|---|
| [Clarify](references/clarify.md) | Starting a task or revisiting its agreement |
| [Development](references/clarify-development.md), [bug fix](references/clarify-bugfix.md), or [optimization](references/clarify-optimization.md) | Read only the selected Clarify branch |
| [Visualization](references/visualization.md) | Preparing the first system view; updating it at a meaningful checkpoint |
| [Verification](references/verification.md) | Choosing checks in Clarify; judging evidence before handoff |
| [Loop](references/loop.md) | Executing the approved change or taking over a run |
| [Handoff](references/handoff.md) | Preparing the delivery for human review |
| [Constitution](references/constitution.md) | The project has `.autodev/`, or standing rules are requested |

## Execution contract

Use `scripts/autodev_verify.py` with Python 3: `init` records the agreement and baseline, `start` binds an isolated worktree, `attempt` judges committed checkpoints, and `status` names the next action. Read the current reference and use command help for flags. The judge reuses the project's tools; it is not a test framework or a semantic oracle.

Keep tests, benchmarks, and the agreed blueprint fixed; enforce scope and project rules. A changed goal or scope returns to Clarify. Keep failed checks, rejected ideas, and blocked runs visible. Interpret their causes before choosing the next attempt; never turn environment failure, skipped checks, or missing evidence into success.

At a meaningful checkpoint, update the affected architecture or flow from the actual code, including unfinished paths. Record a concise `review.md` in the contract directory separating AI assessment from observed checks, then run `report --progress` and show its `progress.html`. This is an inspectable snapshot, not continuous streaming; update when behavior, evidence, risk, or direction changes. Routine tool calls do not need a new diagram or human approval.

## Delivery

Deliver **as-built diagrams for development, the agreed test results for a bug fix, or the measured process chart for optimization**, with the review notes and reproducible evidence. A final number or prose claim does not replace the artifact.

When checks are configured, run `verify` on the retained commit, then `report`; show the actual `handoff.html` using a preview or its absolute path and open command. Before claiming completion, compare the user's target with the code and evidence, not only with diagram IDs. State exactly which behavior is checked and what remains unverified. Missing required evidence means an incomplete or blocked result, even if a mechanical gate is green.

Record the human's approval with `approve` only after review. It binds the retained commit, verification record, and report hash; changed evidence invalidates it. Merge back and remove the worktree only after approval. No configured check means manual verification, explicitly disclosed. Preserve the last verified state when blocked and give a concrete next step.
