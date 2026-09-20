# Contributing

Thanks for wanting to improve autodev. The whole skill is Markdown, so contributions are cheap to review — and the constraint that matters most is size.

## What is most useful

1. **Real transcripts.** A short before/after from an actual run is worth more than any amount of prose: a contract the loop produced, an experiment log with rejections in it, an attempt where the agent tried to game its own benchmark. Open an issue with the prompt, the agent, and what happened.
2. **Unanswered rationalizations.** If a model talked its way past the gate with an excuse not in the rationalization table, that is a bug. Include the exact wording.
3. **Unfrozen variables.** A scenario where the loop accepted an "improvement" that came from something the contract failed to freeze — new hardware, a warmer cache, a smaller eval set. These are the highest-value reports, because each one becomes an anti-gaming invariant.
4. **Missing anti-patterns.** New mock or test smells the reference file does not cover.
5. **Language and clarity fixes.** Tighter wording beats more rules. The skill is followed more often when it stays short.

## The token budget is a feature

Progressive disclosure is load-bearing here, not decoration. A skill that injects 9k tokens into every request gets uninstalled, so:

- **`SKILL.md` is the always-loaded core and stays around 2.5k tokens.** It holds only what every run needs: the three rules, the two modes, the four phases, the verdict, reverting, the experiment log, stop conditions, and the anti-gaming rules.
- **Everything else goes in `references/`.** Long tables, worked examples, per-scenario detail, and anything read conditionally belong there.
- **Every reference file needs an entry in the "Reference files" table in `SKILL.md`** stating when to read it. A reference with no trigger never gets loaded, which makes it dead weight.
- **Check the cost before and after a change:**

```bash
for f in autodev/SKILL.md autodev/references/*.md; do
  printf '%-46s ~%s tok\n' "$f" "$(( $(wc -c < "$f") / 4 ))"
done
```

If a change to `SKILL.md` pushes it past roughly 2.8k tokens, move something out rather than accepting the growth.

## Editing the skill

- **The correctness gate is not negotiable.** The Iron Law, both mandatory verification steps (verify RED, verify GREEN), the rationalization table, the red flags list, and the pre-completion checklist all stay. Loosening the tests to make the loop look more productive is the failure mode this project exists to prevent.
- **The verdict stays mechanical.** No rule may be added that lets the agent judge its own improvement in prose. If a change cannot be expressed as a comparison a script could run, it does not belong in the loop.
- **Keep it language- and framework-agnostic.** No "run `npm test`" requirements beyond illustrative examples, no Jest or pytest templates. The moment the skill knows one framework, it stops applying to the others.
- **Preserve the freeze reasoning.** The rule is "freeze whatever could be traded for a better measurement", not "freeze time". Any per-scenario protected list must say which variable it is protecting against.
- **Prefer imperative, testable instructions.** "Run the test and confirm it fails for the expected reason" is executable; "consider testing first" is not.

## What is out of scope

- Framework-specific instructions or templates.
- Coverage targets, test counts, or score thresholds. Those are outcome metrics, not mechanisms.
- Adding a second skill to this repository. It maintains one skill on purpose.
- Making the loop require dependencies. The contract is generated at runtime and the verdict reuses the project's own commands.

## Editing the READMEs

`README.md` (English) and `README_ZH.md` (Chinese) are translations of each other. Change both and keep the tables in sync. Both READMEs use one diagram each, in `docs/assets/`. They are generated with [Archify](https://github.com/tt-a1i/archify) from a typed JSON source, not hand-drawn: the four dashed groups (contract, baseline, loop, review) each hold their own sub-flow. Regenerate rather than edit the PNG, and keep the two language versions in step:

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

- [ ] `SKILL.md` still near 2.5k tokens, with new detail pushed into `references/`
- [ ] Every new reference file has a trigger in the "Reference files" table
- [ ] The correctness gate is intact and no rule was weakened
- [ ] Both READMEs updated, including the size column in "What's inside"
- [ ] `CHANGELOG.md` updated under `## [Unreleased]`
- [ ] The change would actually change what an agent does — not just how the repo reads

## Commits

See [`AGENTS.md`](AGENTS.md) for the full convention. In short: one commit does one thing, and the message is that one line —

```
feat: add the convergence stop condition
docs: document the protected files per scenario
```

## License

By contributing you agree that your contributions are licensed under the [MIT License](LICENSE).
