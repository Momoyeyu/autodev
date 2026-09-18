# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-09-18

### Changed

- The repository now maintains a single skill, **Test-Driven Development**, and is published as `Momoyeyu/test-driven-development`.
- README rewritten around the single skill: what problem it solves, the RED → GREEN → REFACTOR loop with its verification gates, install paths, and the rationalizations it pre-answers. English is now the primary README (`README.md`) with a Chinese translation at `README_ZH.md`.
- `tdd/SKILL.md` frontmatter description rewritten to carry the trigger keywords (feature, bugfix, refactor, test-first, red-green-refactor) so agents actually load the skill.

### Removed

- `gen-images`, `deepseek-cc`, and `consistent-commit` skills.
- `skills.json` registry — with one skill, the repository root *is* the registry.
- `README_en.md`, superseded by the English-primary `README.md`.

[Unreleased]: https://github.com/Momoyeyu/test-driven-development/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Momoyeyu/test-driven-development/releases/tag/v1.0.0
