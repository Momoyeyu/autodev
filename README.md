<p align="center">
  <strong>English</strong> · <a href="./README_ZH.md">简体中文</a>
</p>

<p align="center">
  <img src="docs/assets/autodev-brand.svg" alt="autodev — clarify, execute, hand off the evidence" width="720">
</p>

**autodev is an explicitly invoked Agent Skill for concise illustrated plans, execution with relevant checks, and clear handoffs.**

**Clarify → Loop → Handoff** means plan → execute → explain the result. Clarify important uncertainties, show the core flow rather than an exhaustive blueprint, implement with the project's own tools, and make the verification evidence easy to assess.

```bash
npx skills add Momoyeyu/autodev -g
```

Ask your agent to use autodev when you want this workflow. It should never activate merely because a task is complex or matches a development category. Codex additionally disables implicit invocation through [its skill policy](autodev/agents/openai.yaml).

## When to use it

Use it when you want help understanding a change before implementation and assessing the result afterward: an ambiguous feature, a difficult regression, or a measured optimization. Production changes across modules often benefit from that conversation. A small task that you explicitly bring to autodev should still get a small plan and proportionate checks.

| What you need | What autodev contributes |
|---|---|
| A feature with important open choices | Focused clarification and a short illustrated plan |
| A bug fix with credible evidence | Reproduction before the fix and relevant regression checks |
| A performance improvement | Comparable baseline, measured attempts, and an honest retained result |

## The working experience

![Clarify, Loop, Handoff: a focused plan, implementation and checks, concise evidence](docs/assets/autodev-overview.svg)

| Stage | What happens | What the user sees |
|---|---|---|
| **Clarify** | Inspect the relevant context, resolve consequential uncertainties, draft a plan | Key choices, one core flow where useful, and a few implementation/check steps |
| **Loop** | Implement and verify using the project's own tools | Brief updates when progress, evidence, or direction changes |
| **Handoff** | Explain the delivered outcome and supporting evidence | Important changes, actual check results, remaining limits, and useful links |

Existing instructions and decisions carry forward. An authorized task can proceed after planning; there is no additional approval gate for its own sake. If a newly discovered choice changes the goal, compatibility, significant cost, or an irreversible action, the agent brings that choice back to you.

Work happens in your chosen directory. Git, branches, commits, and worktrees are optional project choices. Autodev has no contract engine, frozen-file registry, mandatory report schema, or special runtime setup.

### Feature development

![Feature development: concise plan, implementation, focused checks](docs/assets/autodev-development.svg)

Start with a draft you can scan: the goal, key constraints, a small flow or component diagram, and a few steps. Mermaid is often enough; the format stays flexible. The agent investigates what the code can answer and asks about consequential uncertainties. It updates the picture when the approach changes, rather than maintaining three complete architecture documents.

Verification follows the change's risks. A billing retry fix may need a duplicate-request check and ledger integration evidence; a small UI change may need a quick interaction check. A diagram explains the intended behavior; observed checks support the implementation claims.

### Bug fix

![Bug fix: reproduce the failure, fix it, check regressions](docs/assets/autodev-bugfix.svg)

Prefer a focused failing reproduction before changing the implementation, then make the fix and check relevant regressions. Use a documented manual reproduction when automation is impractical. Distinguish the reported defect from fixture or environment failures, and explain any changed test expectations. See [bug fixes and TDD](autodev/references/clarify-bugfix.md).

### Performance optimization

![Performance optimization: fixed workload, comparable attempts, retained measurements](docs/assets/autodev-optimization.svg)

Measure a meaningful baseline, keep workload and conditions comparable, and make each attempt test a hypothesis. Retain supported improvements and preserve failed or rejected attempts in the record. Reuse the user's budget; bound open-ended searches and stop when the goal is met or further work is no longer useful. A short comparison can use a table; longer histories may benefit from a chart. See [performance optimization](autodev/references/clarify-optimization.md).

## Recorded cases

These histories were recorded with an earlier version of the optimization workflow. The measured charts are preserved; they do not establish that the current skill improves every task or has general industrial effectiveness.

**MoE Transformer — English→French translation (PyTorch, single RTX 4090D).** Target: BLEU ≥ 28.87 (the dense reference), baseline 24.97, only `src/train.py` editable, a fixed wall-clock budget per run. Re-running the benchmark on the unchanged source moved the score by 0.62, so the improvement margin was set at 0.8. Thirty-one attempts, thirty named routes, four retained — `top1-n4`, `batch-up`, `dropout-down`, `cosine-sched` — reached 31.25; the verify re-run scored 30.91. The other routes (torch.compile, EMA, fused AdamW, capacity and depth variants…) all measured under the margin and were rolled back.

![Score trajectory of the MoE optimization loop: 31 attempts, 4 retained improvements, target exceeded](docs/assets/autodev-case-moe.svg)

**cann2026 — rotary position embedding kernel (AscendC, CANN 9.0).** Six rounds on one editable kernel file, shown as one continuous history: attempts 1–16 follow the initial baseline at 0. All scores are recomputed from the 15 per-case raw latencies against the same fixed reference vector used in rounds 3–6, giving one shared y axis from 19.7026 to the retained 0.7168. Historical accept/reject decisions are preserved; baseline remeasurements are not counted as attempts. The dashed line marks the final round's target, 0.680, not a target shared by all six rounds. Four rounds met their own targets; rounds 2 and 6 did not. In round 6, three ideas measured under the keep margin, one attempt failed to compile and was rolled back invalid, and the retained contiguous-token change scored 0.7168 against a 0.680 target; the final verify then hit a judge-service outage, which the report records as an outage, not a number.

![Continuous cann2026 optimization history: baseline followed by 16 cumulative attempts on one fixed-reference scale](docs/assets/autodev-case-cann2026.svg)


## Get started

```text
Use $autodev for the billing retry change. Preserve payment compatibility.
Clarify the important open questions, show a concise core-flow plan,
then implement and check it. Keep the final handoff short and make
missing integration evidence explicit.
```

The agent loads [SKILL.md](autodev/SKILL.md), plus bug-fix or performance guidance only when needed. It uses existing project instructions, tests, and tools. Durable notes are useful for long tasks or takeover, but a separate artifact directory is not required.

## Optional HTML handoff

The default handoff is a concise response or your project's usual delivery format: what changed, what was checked, and what remains uncertain, with useful links. It should be easy to read without opening a report.

If you prefer a visual page, request it and choose a rendering skill. [Archify's explainer](https://github.com/tt-a1i/archify/blob/main/archify/SKILL.md) supports conclusion-first HTML pages; [visual-explainer](https://github.com/nicobailon/visual-explainer) covers visual explanations, change reviews, and project recaps. Autodev supplies the verified substance and can hand it to the selected skill. Neither is a required dependency.

```text
Use $autodev to implement this change. For the final handoff,
use Archify to turn the result, actual checks, and limitations
into a concise HTML explainer.
```

## What the evidence means

Report commands and outcomes that actually occurred. Keep measured observations separate from AI inference. Label existing failures, skipped or unavailable checks, and partial work plainly. Passing unit tests do not establish an integration property that was never checked.

The skill guides judgment; it does not mechanically prove correctness or guarantee faster development. [Product evaluation](docs/evaluation.md) focuses on whether the clarification, visuals, and handoff help people enough to justify their cost.

## Skill structure

| File | Purpose |
|---|---|
| [SKILL.md](autodev/SKILL.md) | Explicit invocation and the complete Clarify → Loop → Handoff workflow |
| [Bug fixes and TDD](autodev/references/clarify-bugfix.md) | Reproduction, regression coverage, and evidence limits |
| [Performance optimization](autodev/references/clarify-optimization.md) | Comparable measurements and bounded experimentation |
| [Codex policy](autodev/agents/openai.yaml) | Disable implicit invocation |

## Contributing

Keep the skill, bilingual READMEs, and visual sources consistent. See [CONTRIBUTING.md](CONTRIBUTING.md) for regeneration and checks. Report concrete usage friction and evidence when proposing changes.

## License

[MIT](LICENSE)
