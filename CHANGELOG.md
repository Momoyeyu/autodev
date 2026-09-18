# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.0.3] - 2026-09-18

### Changed

- The READMEs now carry **one diagram instead of two**. The banner and the flow diagram were saying the same thing twice, so they are merged into a single image that serves as both.
- The diagram is generated with [Archify](https://github.com/tt-a1i/archify) from a typed JSON source instead of hand-authored SVG. Each of the four phases — contract, baseline, loop, review — is now a **dashed group containing its own sub-flow** with real nodes, arrows, and a return edge. The previous version drew each phase as one box holding a sentence, which carried no more information than the sentence itself.
- Both language versions have their own diagram: the Chinese README renders Chinese node labels, the English README renders English ones.

### Removed

- `docs/assets/autodev-hero.svg`, `autodev-hero.zh.svg`, `autodev-flow.svg`, and `autodev-flow.zh.svg`, replaced by `autodev-overview.png` and `autodev-overview.zh.png`.

## [3.0.2] - 2026-09-18

### Changed

- The flow diagram now covers the whole process instead of only the loop. It starts at the contract, shows the tests or the benchmark being written and the baseline measured, and ends at review. Previously a reader could not see where the first test came from.
- The diagram reads top to bottom. The old one ran left to right for the main path but looped back leftward on a second line, so the eye had to reverse direction mid-flow. The loop is now a vertical cycle with a single return edge on the right.
- Phase descriptions in the README table now say what actually happens. "Full test suite from a clean state, then refactor" never explained what a clean state was or why refactoring came last; it now reads "Re-run all tests on the final code, then refactor, then report."
- TDD is explained where it first appears. Both READMEs used the abbreviation without ever saying it stood for test-driven development or what it required, so it read as jargon rather than a mechanism.

### Removed

- `docs/assets/autodev-loop.svg` and `docs/assets/autodev-loop.zh.svg`, replaced by `autodev-flow.svg` and `autodev-flow.zh.svg`.

## [3.0.1] - 2026-09-18

### Changed

- The two verdicts are now **accept** and **reject**, replacing *keep* / *revert*. `revert` is a git command and `keep` is not, so the pair never read as a pair. The actions are **commit** and **roll back**, both of which are git operations. The experiment log's verdict column now holds one of `baseline`, `accept`, `reject`, or `fail` — four values of the same kind, instead of a mix of outcomes and causes.
- Every diagram label fits on one line. The loop boxes previously broke phrases across two lines to fit their width — "Run the frozen / benchmark" — which read as arbitrary line breaks. Boxes are sized to their text now.
- Removed the remaining invented phrases: *frozen benchmark* became simply "the benchmark", and the phase called **Land** is now **Review**.
- Chinese wording follows Chinese developer usage rather than mirroring the English: 回滚 instead of 回退, 实际耗时 instead of the calque 墙钟时间, 复盘 instead of 落地, and headings no longer translate the English ones word for word.

## [3.0.0] - 2026-09-18

### Changed

- The repository is named `autodev` (was `Ratchet`). Ratchet was only one phase of the loop, so naming the whole project after it was misleading. "Ratchet" survives as the name of the keep-or-revert rule itself.
- Both READMEs rewritten in plain language. Invented vocabulary gave way to terms developers already use: **benchmark** replaces *yardstick*, **experiment log** replaces *ledger*, **mode** replaces *lane*, **protected files** replaces *frozen set*, and **the correctness gate** replaces *gate layer*. The same pass was applied to `SKILL.md` and `references/contracts.md`.
- Diagrams moved to the top of both READMEs, directly under the one-line pitch, so the loop is the first thing a new visitor sees.
- The Chinese README no longer reads as a translation: it uses the vocabulary Chinese developers actually use (`feature`, `loop`, `benchmark`, `revert`), and its headings are no longer literal renderings of the English ones.

### Added

- Chinese diagrams, `docs/assets/autodev-hero.zh.svg` and `docs/assets/autodev-loop.zh.svg`. Both READMEs now show images in their own language.

### Removed

- `docs/assets/ratchet-*.svg`, replaced by the `autodev-*` assets.

## [2.0.0] - 2026-09-18

### Added

- `autodev` skill: a goal-gated development loop — contract, baseline, loop, land — with a four-line mechanical verdict, a cross-context experiment log, objective stop conditions, and seven anti-gaming rules.
- `references/contracts.md`: choosing a metric, protected files per scenario, worked contracts, and how to build a benchmark under TDD.
- `AGENTS.md`: commit message and code comment conventions for this repository.

### Changed

- Test-Driven Development became the **correctness gate** of the loop instead of the whole skill. Every prior rule is preserved in `references/gate.md`; nothing was dropped.
- The skill is named `autodev` (was `tdd`).
- Requests now route by shape: development work to TDD only, optimization to TDD plus a benchmark. The user is never asked to name a mode.
- Optimization budgets come from a clarify flow with concrete options and a custom answer, and always show a cost estimate. Development work has no budget at all.
- Progressive disclosure: `SKILL.md` is the ~2.5k-token core, and longer material moved into three reference files loaded on demand. A typical feature request loads ~5k tokens instead of ~8.7k.

## [1.0.0] - 2026-09-18

### Changed

- The repository maintains a single skill, **Test-Driven Development**, published as `Momoyeyu/test-driven-development`.
- README rewritten around that single skill: the problem it solves, the RED → GREEN → REFACTOR loop with its verification steps, install paths, and the rationalizations it pre-answers. English became the primary README with a Chinese translation at `README_ZH.md`.

### Removed

- `gen-images`, `deepseek-cc`, and `consistent-commit` skills.
- `skills.json` registry — with one skill, the repository root *is* the registry.
- `README_en.md`, superseded by the English-primary `README.md`.

[Unreleased]: https://github.com/Momoyeyu/autodev/compare/v3.0.3...HEAD
[3.0.3]: https://github.com/Momoyeyu/autodev/compare/v3.0.2...v3.0.3
[3.0.2]: https://github.com/Momoyeyu/autodev/compare/v3.0.1...v3.0.2
[3.0.1]: https://github.com/Momoyeyu/autodev/compare/v3.0.0...v3.0.1
[3.0.0]: https://github.com/Momoyeyu/autodev/compare/v2.0.0...v3.0.0
[2.0.0]: https://github.com/Momoyeyu/autodev/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/Momoyeyu/autodev/releases/tag/v1.0.0
