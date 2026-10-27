# Contributing

Keep autodev small and explicitly invoked. Its job is to help users clarify important uncertainties, scan a concise illustrated plan, and assess the evidence after execution. Useful real-world behavior comes before research framing.

## Preserve the lightweight workflow

- **Clarify:** investigate the relevant context, ask about consequential unknowns, and draft a short plan. Prefer one useful core diagram over exhaustive blueprints.
- **Loop:** implement with native project tools, check the actual risks, and update the user when the state or direction changes.
- **Handoff:** lead with the outcome, actual checks, and limitations. HTML is optional and can be delegated to a user-selected visualization skill.

Reuse existing authorization. Do not add mandatory approval stages, Git setup, worktrees, file freezes, commit sequences, or report schemas. Keep bug reproduction and comparable performance measurement useful without turning either into a separate infrastructure system. Project-specific instructions still apply.

`autodev/SKILL.md` contains the complete common workflow. The two references add only bug-fix and performance guidance. Codex's `agents/openai.yaml` disables implicit invocation. Descriptions and examples must preserve the explicit-only boundary on other hosts as well.

## Visuals and bilingual documentation

Keep English and Chinese README headings, tables, links, and evidence limits equivalent. Update the public website's copy when workflow behavior changes. Regenerate the README SVGs from their source:

```bash
python3 docs/visuals/generate.py
```

See [docs/visuals.md](docs/visuals.md) for the current visual design and review notes. Inspect both languages at normal reading width; XML checks do not replace visual inspection. Scenario diagrams are explanatory schematics, not measured results.

Preserve the recorded MoE and cann2026 charts and their measurement caveats. They are historical case evidence, not a demonstration of the current skill's effectiveness. Older validation records and design plans describe the versions tested at their dates.

## Verification

For documentation and packaging changes:

```bash
python3 -m unittest discover -s tests
node --test tests/story-motion.test.mjs
git diff --check
```

The Python checks cover resource links, bilingual structure, and invocation configuration. The motion tests cover the website's scrolling behavior. When changing website content or layout, run the browser checks described in [docs/website-redesign.md](docs/website-redesign.md).

Review the guidance against a small explicitly invoked task, an uninvoked complex task, a defect with an unavailable reproduction, and an optimization with noisy measurements. Check that the agent neither imposes ceremony nor overstates its evidence. Instruction review and browser tests do not establish industrial effectiveness; [product evaluation](docs/evaluation.md) describes useful observations from actual work.

## License

Contributions are licensed under [MIT](LICENSE).
