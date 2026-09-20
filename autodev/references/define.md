# Define

Read when turning the request into a shared acceptance definition. The exit is a human-approved test specification, not an implementation or an assumed benchmark result.

## Feature development

### Confirm impact before designing tests

Inspect the relevant code and architecture, then make these decisions explicit:

| Boundary | Confirm with the human |
|---|---|
| Architecture | Which modules and interfaces are affected? May modules be added or removed? Which boundaries must remain? |
| Existing workflows | Which user or system flows are affected? May their sequence, outputs, or side effects change? Which behavior must remain compatible? |

Show the proposed change alongside what stays unchanged. Do not interpret a feature request as unrestricted permission to redesign the project. Record the approved impact and any explicit prohibitions.

### Agree on tests with the human

Translate the requirement into reviewable acceptance cases: stable case ID, starting state/input, action, expected outcome, and relevant error or boundary cases. Include affected behavior that must remain unchanged.

Show the cases to the human, address corrections, and repeat until the human confirms them. Explain what the tests do not cover. Approval of a vague goal or of a coding plan is not approval of the tests.

The approved cases describe behavior; their executable implementation and reconciliation with existing tests happen in Anchor. If the human already supplied complete cases and explicitly approved them, record that decision instead of asking again.

**Exit:** approved architecture/workflow impact and approved acceptance cases. Next: [Anchor](anchor.md#feature-development).

## Performance optimization

### Agree on exactly one test

Turn the optimization request into one benchmark with one finite numeric output and one direction of improvement. Several benchmarks are allowed only as components of one fixed weighted score.

Agree on:

- the workload, input data, and valid output being measured;
- the command or benchmark implementation to prepare;
- the output's name, unit, and lower-is-better or higher-is-better direction;
- repetition, aggregation, environment/cache conditions, and treatment of variability;
- for a composite score, the components, weights, normalizations, and resulting direction.

Expose trade-offs in a composite score. Do not add separate competing optimization tests or choose weights after seeing which candidate wins. Use [test design](test-design.md#performance-optimization) when a metric or aggregation needs detail.

Review this test definition with the human until confirmed. Record any supplied target or restrictions, but do not skip measurement: the target, editable files, and time budget are confirmed against the baseline in Anchor.

**Exit:** one approved benchmark definition. Next: [Anchor](anchor.md#performance-optimization).

## Preserve the agreement

Keep a durable record of the approved scope, test specification, and the human's decision using the repository's normal task or artifact location. It must be possible to distinguish an approved decision from an agent's assumption after a handover.

If the request changes, revise the affected scope and tests with the human. Do not hide a new requirement inside an implementation attempt. For work containing both scenarios, establish feature behavior first, then optimize that behavior against its own benchmark baseline.
