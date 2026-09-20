<p align="center">
  <strong>English</strong> · <a href="./README_ZH.md">简体中文</a>
</p>

# autodev

**Align the agent and the human before implementation. Deliver work that is verifiable, measurable, and visible.**

```bash
npx skills add Momoyeyu/autodev -g
```

An Agent Skill for **feature development** and **performance optimization**. It works with agents that load `SKILL.md` and reuses the target project's test and benchmark tools.

## Why autodev exists

Natural-language agreement is easy to mistake for shared understanding. An agent can implement the wrong behavior, change a workflow the human wanted to preserve, or optimize a number that does not represent the actual goal.

autodev turns that uncertainty into a shared test definition before implementation. The human confirms what success means; the agent records a baseline, iterates against the agreed test, and shows the final difference. The purpose is less misunderstanding and rework, not simply more autonomous coding.

The intended result is better **quality, stability, and overall efficiency**, with a human who can **understand the project and take over the work**.

## Verifiable & measurable & visible

| Principle | What the agent delivers |
|---|---|
| **Verifiable** | Human-approved tests, exact reproduction commands, and actual execution evidence |
| **Measurable** | Comparable baseline and final results: acceptance-case outcomes or one numeric benchmark score |
| **Visible** | A readable comparison, the impact on architecture and workflows, and enough context for handover |

A passing test is useful only if it represents the human's intent. A better score is useful only if it measures the agreed work. A polished explanation is not a substitute for either.

## How it works

**Define → Anchor → Ratchet → Prove** organizes both the workflow and the skill's reference files. The two scenarios share the stages, not an identical sequence of decisions.

| Stage | Feature development | Performance optimization |
|---|---|---|
| **Define** | Confirm architecture/workflow impact; revise acceptance tests with the human until approved | Revise one numeric benchmark test with the human until approved |
| **Anchor** | Reconcile existing tests, verify execution, and record the baseline | Prepare and run the benchmark, record baseline, then confirm target, editable files, and time budget |
| **Ratchet** | Develop and run the agreed tests until all pass | Optimize and measure until the target is reached or time expires |
| **Prove** | Compare baseline and final test results; deliver the feature and handover | Compare baseline and final score; deliver the best verified result and stop reason |

### Feature development

```mermaid
flowchart TD
    subgraph D["Define"]
        F1["Feature request"] --> F2["Confirm architecture and workflow impact"]
        F2 --> F3["Draft acceptance tests with the human"]
        F3 --> F4{"Human confirms tests?"}
        F4 -- Revise --> F3
    end
    subgraph A["Anchor"]
        F5["Inspect existing tests"] --> F6["Update or remove outdated tests; add missing tests"]
        F6 --> F7["Verify tests can execute"]
        F7 --> F8["Run tests and record baseline"]
    end
    subgraph R["Ratchet"]
        F9{"All agreed tests pass?"}
        F10["Develop within approved scope"] --> F11["Run the agreed test set"]
        F11 --> F9
        F9 -- No --> F10
    end
    subgraph P["Prove"]
        F12["Verify final results and compare with baseline"] --> F13["Deliver feature, impact, and handover evidence"]
    end
    F4 -- Yes --> F5
    F8 --> F9
    F9 -- Yes --> F12
```

**Clarify impact first.** Confirm how the feature affects the overall architecture, whether modules may be added or removed, how existing workflows are affected, and whether those workflows may change. A feature request is not unrestricted redesign permission.

**Agree on tests, not just prose.** Review inputs, actions, expected outcomes, boundaries, and relevant regressions with the human. Revise until the human approves the test definition; there is no fixed question count.

**Maintain the suite before measuring.** After approval, inspect existing tests, update or delete outdated expectations, and add missing cases. Keep still-relevant coverage and record why each test changed. Capture the baseline only after this reconciliation, so baseline and final results use the same test set.

**Executable does not mean already passing.** The runner must produce meaningful outcomes; missing feature behavior may fail in the baseline. Broken setup is not baseline evidence. Implementation continues until all agreed tests pass, without changing acceptance to make the result look green.

### Performance optimization

```mermaid
flowchart TD
    subgraph D["Define"]
        O1["Optimization goal"] --> O2["Design one numeric benchmark test with the human"]
        O2 --> O3{"Human confirms test?"}
        O3 -- Revise --> O2
    end
    subgraph A["Anchor"]
        O4["Make the approved benchmark executable"] --> O5["Run benchmark and record baseline"]
        O5 --> O6["Confirm target, editable files, and time budget"]
    end
    subgraph R["Ratchet"]
        O7{"Target reached or time expired?"}
        O8["Optimize only allowed files"] --> O9["Run the same benchmark"]
        O9 --> O10["Record result and retain the best valid candidate"]
        O10 --> O7
        O7 -- No --> O8
    end
    subgraph P["Prove"]
        O11["Compare baseline with the delivered result"] --> O12["Deliver evidence, stop reason, and handover"]
    end
    O3 -- Yes --> O4
    O6 --> O7
    O7 -- Yes --> O11
```

**Quantifiable:** the test is a benchmark that produces a numeric result. Agree on what it measures, its workload, unit, direction, and measurement method before using it.

**Single objective:** there is exactly one optimization test. It can be one benchmark or a weighted sum of several benchmarks, but the result is one score. Weights, normalization, and aggregation are confirmed before the baseline and remain unchanged during iteration. Component readings explain the score; they are not independent optimization targets.

**Baseline before limits:** after running the approved test, confirm:

- **Target:** the score threshold that allows an early exit.
- **Editable files:** the implementation surface; benchmark, inputs, and scoring rules are not a way to game the result.
- **Time budget:** a wall-clock limit that bounds the loop, including measurements and reserved final verification time.

Reuse decisions the human already supplied. Optimize until the target is met or time expires, retaining the best valid measured candidate. Do not invent a convergence stop or silently extend the budget. If the baseline already meets the target, report that without unnecessary edits.

A timeout is a valid stopping reason, not proof that the target was met. If no improvement was verified, deliver that finding and the unchanged best state.

## What the human receives

| Deliverable | Feature development | Performance optimization |
|---|---|---|
| Approved definition | Architecture/workflow permissions and acceptance cases | One benchmark definition, then baseline-informed target, editable files, and time budget |
| Before / after | Same case IDs and test version, with baseline and final outcomes | Same workload and scoring formula, with baseline and final score |
| Runnable evidence | Commands, environment, raw results, and test-maintenance reasons | Command, measurement conditions, raw samples, and attempt history |
| Visible summary | Case matrix and relevant module/workflow changes | Score comparison, target status, elapsed time, and optional trend chart |
| Handover | Changed entry points, decisions, limitations, and remaining work | Delivered candidate, rejected approaches, limitations, and next steps |

Tables are sufficient when they explain the result clearly. Use diagrams for architectural or workflow changes and charts for measured trends when helpful. Every displayed result must trace back to recorded evidence, not an illustrative number.

A change in requirements, allowed impact, or test meaning requires renewed agreement and a new baseline. It must not be hidden inside an attempt or compared against results from a different test version.

## Get started

Install the skill with the command above, then describe the task normally:

```text
Add CSV export for the filtered transaction list.
```

```text
Bring API p95 latency below 200 ms. Limit implementation changes to src/api/ and use a 20-minute optimization budget.
```

The first request begins with architecture/workflow alignment and test review. The second begins with benchmark review and baseline measurement; supplied limits are reused rather than asked for again.

## Skill structure

| File | Load when |
|---|---|
| [`autodev/SKILL.md`](autodev/SKILL.md) | At entry: purpose, principles, scenario selection, and stage routing |
| [`references/define.md`](autodev/references/define.md) | Entering Define: scope alignment and human-approved test definitions |
| [`references/anchor.md`](autodev/references/anchor.md) | Entering Anchor: test preparation, baseline, and optimization limits |
| [`references/ratchet.md`](autodev/references/ratchet.md) | Entering Ratchet: scenario-specific loops and progress records |
| [`references/prove.md`](autodev/references/prove.md) | Entering Prove: comparisons, visible evidence, and handover |
| [`references/test-design.md`](autodev/references/test-design.md) | Only when acceptance cases or a composite benchmark need design detail |

Progressive disclosure follows the current stage. Do not load every reference at the start; within a stage, read its shared instructions and the applicable scenario. Visiting all four stages eventually does not require revealing all their detail up front.

This repository distributes the skill, not a bundled test runner or evaluation suite. The executable tests belong to the project where the skill is used and are defined with that project's human owner.

## Contributing

Keep the skill, stage references, and bilingual README flows consistent. See [CONTRIBUTING.md](CONTRIBUTING.md) for review and verification guidance and [AGENTS.md](AGENTS.md) for repository conventions.

## License

[MIT](LICENSE)
