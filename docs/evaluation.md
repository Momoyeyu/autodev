# Product evaluation

The first question is whether people choose to use autodev again because it helps them understand and assess real changes. The three stage names, a diagram, or a passing command are not evidence of productivity or novelty.

## Observe actual work

Use real tasks that users explicitly bring to the skill: a feature with an important open choice, a difficult defect, or a measured optimization. Include small tasks to detect unnecessary ceremony. Record the skill/model version and relevant task context; keep historical observations tied to the version used.

Look for concrete outcomes:

- Did clarification catch an assumption that would otherwise change the implementation? Were questions useful or avoidable?
- Could the user understand the draft quickly? Did the core diagram answer a question better than prose, or did they ignore it?
- Did the checks exercise the relevant behavior? Were failures and unavailable evidence reported accurately?
- Could the user assess or continue the work from the handoff? Did an optional HTML page help enough to justify preparing and reading it?
- How much investigation, user attention, model/compute cost, waiting, and rework did the workflow require? Would the user choose it for a similar task again?

Keep failures, abandoned tasks, and requests to bypass the workflow. Do not score document length, diagram counts, commits, or approval events as success. These are process costs unless they produce a useful result.

## Compare only what the evidence can support

If making a comparative claim, use a credible normal-agent workflow that can already inspect code, clarify, plan, test, debug, and summarize. Keep model, tools, information, starting state, and all-in budgets comparable. Avoid letting the same person solve the same problem again after seeing its solution. Preserve unsuccessful runs and explain missing data.

Automatic correctness checks can measure bounded task outcomes, but they do not measure whether a human understood the plan or could use the handoff. Preference alone also does not establish correctness. Keep these questions distinct, report the cost as well as the benefit, and limit conclusions to the tasks and people actually observed.

Research remains optional. A useful skill is the goal; a publication requires its own defensible question and study, rather than extra mechanisms in the runtime workflow. This document proposes evaluation practices and makes no completed-study or performance claim.
