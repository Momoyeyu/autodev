# AGENTS.md

Project conventions for agents working in this repository.

## Git

1. One commit does one thing. If you cannot say it in one line, split it.
2. The message is that line: `<type>: <what changed>`, imperative, lowercase, no
   period, `type` in `feat|fix|refactor|docs|chore|test|build`. No body.
3. Never force-push shared history. When rewriting unshared history, set
   `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE` on every rebuilt commit —
   otherwise the whole timeline collapses onto the moment of the rewrite.

## Comments

1. Readable code beats commented code. Needing a comment to be understood means
   refactor instead: names, smaller functions, fewer nested expressions.
2. A surviving comment must be short — a few words, abbreviations fine. English
   is required precisely because it is terse.
3. No block comments explaining code. A multi-line comment describing what a
   section does means rule 1 already failed.

Comments are for what code cannot say: a unit, an external constraint, the
non-obvious reason a choice is correct. Never restate logic, never record what
was tried or measured.
