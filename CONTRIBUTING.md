# Contributing

Thanks for wanting to improve the TDD skill. This repository is deliberately tiny — one skill, two Markdown files — so contributions are cheap to review and easy to ship.

## What is most useful

1. **Real transcripts.** A short before/after from an actual session where an agent ignored the skill (or where it visibly changed the agent's behavior) is worth more than any amount of prose. Open an issue with the prompt, the agent, and what happened.
2. **Unanswered rationalizations.** If a model talked its way around the skill with an excuse that is not in the rationalization table, that is a bug. Include the exact wording it used.
3. **Missing anti-patterns.** New mock or test smells that the reference file does not cover yet.
4. **Language and clarity fixes.** Tighter wording beats more rules. The skill is followed more often when it is short enough to stay in context.

## What is out of scope

- Framework-specific instructions. The skill must work whether the project uses Jest, Vitest, pytest, RSpec, `go test`, or a custom harness. No "run `npm test`" style requirements beyond illustrative examples.
- Coverage targets and test-count metrics. Those are outcome metrics, not the mechanism this skill protects.
- Adding a second skill to this repository. It maintains one skill on purpose.

## Editing the skill

- `tdd/SKILL.md` is the entry point. Keep the `name` field as `tdd` and keep the `description` keyword-rich, because that field is what makes an agent load the skill at all.
- `tdd/testing-anti-patterns.md` is the reference loaded when tests or mocks are touched. Every anti-pattern keeps the same four-part shape: the violation, why it is wrong, a gate function, and the fix.
- Preserve the structure that makes the skill enforceable: the Iron Law, the two mandatory verification gates (verify RED, verify GREEN), the rationalization table, the red flags list, and the pre-completion checklist.
- Prefer imperative, testable instructions over advice. "Run the test and confirm it fails for the expected reason" is editable by an agent; "consider testing first" is not.

## Editing the READMEs

`README.md` (English) and `README_ZH.md` (Chinese) are translations of each other. Change both, and keep the tables in sync. Assets live in `docs/assets/`.

## Before you open a PR

- [ ] Both READMEs updated when behavior or instructions changed
- [ ] Skill instructions stay language- and framework-agnostic
- [ ] No new dependencies or scripts added to the skill itself
- [ ] `CHANGELOG.md` updated under `## [Unreleased]`
- [ ] The change would actually change what an agent does — not just how the repo reads

## Commits

Write commit messages in the imperative mood with a short scope prefix when it helps, for example:

```
skill: answer the "the test is hard to write" rationalization
readme: add the Codex CLI install path
```

## License

By contributing you agree that your contributions are licensed under the [MIT License](LICENSE).
