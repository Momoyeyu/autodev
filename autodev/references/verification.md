# Verification

Read when preparing checks in Clarify and when judging the delivered result. The purpose is credible evidence for this change, using the project's tools. AI chooses and interprets the evidence; the judge records commands, source identities, constraints, and results.

## Choose checks from the change's risks

Inspect the actual callers, state transitions, data boundaries, and compatibility requirements before proposing commands. Start with existing checks and add a focused reproduction or regression where coverage is missing. For a production change, ask what a green local test would still fail to establish.

| Risk exposed by the change | Evidence to consider |
|---|---|
| Changed business behavior | Focused acceptance or reproduction cases with observable outcomes |
| Existing consumers or interfaces | Regression, contract, compatibility, or build checks already used by the project |
| Persistence, concurrency, retries, or migrations | Realistic integration cases around the affected invariant and failure/recovery path |
| Performance or resource use | Fixed workload and scoring, correctness guard, comparable conditions and rerun |
| Deployment or operations | The project's staging/smoke/rollback checks when available and authorized |

This is a reasoning aid, not a mandatory suite for every task. Use the checks that bear on the approved change. State missing environments or expensive checks in Clarify so the human can agree on what can actually be verified. Do not silently replace integration evidence with a unit test that cannot exercise the relevant boundary.

## Establish a meaningful baseline

Record the command, working directory, source/test versions, relevant environment, and raw output. For a bug fix, confirm that the intended case executed and failed for the reported reason. For optimization, confirm the workload and score are comparable. For development, record relevant existing checks as well as the as-is picture.

An arbitrary nonzero exit is not proof of reproduction. Investigate runner, collection, dependency, fixture, and application errors in context. A runtime exception may be the actual bug; do not classify all exceptions as environment problems. The judge cannot decide this from arbitrary shell output. Explain the judgment and repair unrelated setup failures before presenting baseline.

Retain pre-existing failures and coverage gaps. Do not erase them by editing tests or change the acceptance target after seeing a convenient result. If the agreed checks or target must change, return to Clarify with comparable evidence.

## Read results at their actual strength

At each checkpoint distinguish:

- **Observed:** a named command ran on a named commit with the recorded output.
- **AI assessment:** why the code and checks appear to satisfy the intended behavior.
- **Unverified:** a relevant behavior, environment, or operating condition that was not exercised.

A green regression command does not individually prove every blueprint element. Diagram coverage and dependency ordering document implementation claims, not semantic correctness. Inspect the code and important paths against the agreement. If the actual system disagrees with the target, continue Loop or reopen Clarify for an approved change.

Extra diagnostic checks may run inside Loop when they leave the agreed target, acceptance command, frozen inputs, and permitted scope unchanged. If a discovered gap requires a new acceptance command or a changed target or scope, propose that change in Clarify; do not silently promote an extra check into a new stopping rule.

Keep this assessment in `review.md` alongside exact logs and source references; [Visualization](visualization.md) describes its presentation. Do not require a universal test-report format or attempt to mechanically classify every possible defect.

## Final verification and delivery

1. Settle uncommitted or unjudged work and select the retained commit.
2. Rerun the agreed checks with `verify` under comparable conditions. Frozen inputs and project rules must still match.
3. Examine both raw output and adequacy: did intended cases execute, were any skipped, and what important behavior remains uncovered?
4. Review the delivered code and as-built view against the approved target, including preserved behavior. Name relevant supplementary checks separately from the agreed command.
5. Update `review.md`, run `report`, and show the actual packet. Only then request delivery approval.

For optimization, the current mechanical rerun rule requires `|fresh score - recorded best| < δ` and the same target-met outcome. This is a repeatability check using the agreed margin, not a confidence interval or proof that every observed improvement is real. Use the project's established repeated-measurement method when it has one and retain its raw observations.

If required verification is blocked, show the blockage, last verified state, and the exact next check. A report can be generated for inspection while incomplete. Current `approve` requires a successful recorded verification when checks are configured; an exception for unverified delivery is not implied. With no configured command, label verification manual and state its limits. Human approval acknowledges a reviewed artifact; it does not turn missing evidence into a verified fact.
