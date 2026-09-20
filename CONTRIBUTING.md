# Contributing

Thanks for wanting to improve autodev. The whole skill is Markdown, so contributions are cheap to review — and the constraint that matters most is size.

## What is most useful

1. **Real transcripts.** A short before/after from an actual run is worth more than any amount of prose: a contract from Define, a Ratchet log with rejections in it, an attempt where the agent tried to game its own benchmark. Open an issue with the prompt, the agent, and what happened.
2. **Unanswered rationalizations.** If a model talked its way past the gate with an excuse not in the rationalization table, that is a bug. Include the exact wording.
3. **Unfrozen variables.** A scenario where the Ratchet accepted an "improvement" that came from something the contract failed to freeze — new hardware, a warmer cache, a smaller eval set. These are the highest-value reports, because each one becomes an anti-gaming invariant.
4. **Missing anti-patterns.** New mock or test smells the reference file does not cover.
5. **Language and clarity fixes.** Tighter wording beats more rules. The skill is followed more often when it stays short.

## The token budget is a feature

Progressive disclosure is load-bearing here, not decoration. A skill that injects 9k tokens into every request gets uninstalled, so:

- **Keep `SKILL.md` within 5,500 UTF-8 bytes.** It holds mode selection, Define → Anchor → Ratchet → Prove, both gates, essential verdicts and safeguards, and load routing. Details belong in references, not duplicated in the core.
- **Keep the full skill within 24,000 bytes and the ordinary development path (`SKILL.md` + `gate.md`) within 10,000.** Moving prose between files must reduce the relevant load path, not merely hide growth.
- **Every reference needs a direct Markdown link and a specific trigger in the core's "Reference files" table.** Do not preload the directory. Keep examples optional and references self-contained within the installed skill.
- **Use README terminology:** four stages, the TDD **correctness gate**, and the ratchet **progress gate**. A gate is not another workflow.
- **Measure before and after:**

```bash
for f in autodev/SKILL.md autodev/references/*.md; do
  printf '%-50s ' "$f"
  wc -l -w -c < "$f"
done
python3 -B -m unittest discover -s tests -p test_terminology.py -v
```

The checks cover byte budgets, load triggers, local links, terminology, required safeguards, and both README inventories. Bytes are reproducible; bytes/4 is only a rough token estimate, not a tokenizer measurement.

## Editing the skill

- **The correctness gate is not negotiable.** The Iron Law, both mandatory verification steps (verify RED, verify GREEN), the rationalization table, the red flags list, and the pre-completion checklist all stay. Loosening the tests to make the Ratchet look more productive is the failure mode this project exists to prevent.
- **The verdict stays mechanical.** No rule may be added that lets the agent judge its own improvement in prose. If a change cannot be expressed as a comparison a script could run, it does not belong in the Ratchet.
- **Keep it language- and framework-agnostic.** No "run `npm test`" requirements beyond illustrative examples, no Jest or pytest templates. The moment the skill knows one framework, it stops applying to the others.
- **Preserve the freeze reasoning.** The rule is "freeze whatever could be traded for a better measurement", not "freeze time". Any per-scenario protected list must say which variable it is protecting against.
- **Prefer imperative, testable instructions.** "Run the test and confirm it fails for the expected reason" is executable; "consider testing first" is not.

## What is out of scope

- Framework-specific instructions or templates.
- Coverage targets, test counts, or score thresholds. Those are outcome metrics, not mechanisms.
- Adding a second skill to this repository. It maintains one skill on purpose.
- Making the Ratchet require dependencies. The contract is generated during Define and the verdict reuses the project's own commands.

## Editing the READMEs

`README.md` (English) and `README_ZH.md` (Chinese) are translations of each other. Change both and keep the tables in sync. Both READMEs use one diagram each, in `docs/assets/`. They are generated with [Archify](https://github.com/tt-a1i/archify) from a typed JSON source, not hand-drawn: the four groups (Define, Anchor, Ratchet, Prove) each hold their own sub-flow. Regenerate rather than edit the PNG, and keep the two language versions in step:

```bash
# from a checkout of https://github.com/tt-a1i/archify
node bin/archify.mjs deliver architecture <repo>/docs/diagrams/autodev.workflow.json /tmp/out.html --quality showcase --json
```

The JSON sources live in `docs/diagrams/`. `meta.quality_profile` must stay `showcase`, and a change is only done when `validate` reports all nine artifact checks passing with zero warnings.

## Evaluating behavior

Behavior changes need a regression case in `evals/cases.json`. Keep existing prompts stable unless their intended behavior changes, and validate the corpus and scorer with:

```bash
python3 -m unittest discover -s tests -v
```

For model runs, use `python3 evals/run.py run`, review the ignored artifacts, and attach the scored report with the agent, model, and skill revision. Remove reviewed artifacts with `python3 evals/run.py clean`.

## Before you open a PR

- [ ] Core, full skill, and ordinary development path meet their byte budgets
- [ ] Every reference has a direct link and conditional load trigger
- [ ] The correctness gate, progress gate, and anti-gaming rules remain intact
- [ ] Both README inventories and load descriptions match the skill
- [ ] The full unit suite passes; behavior changes have an evaluation regression case
- [ ] The change improves agent behavior or reduces context cost, not just repository prose

## Commits

See [`AGENTS.md`](AGENTS.md) for the full convention. In short: one commit does one thing, and the message is that one line —

```
feat: add the convergence stop condition
docs: document the protected files per scenario
```

## License

By contributing you agree that your contributions are licensed under the [MIT License](LICENSE).
