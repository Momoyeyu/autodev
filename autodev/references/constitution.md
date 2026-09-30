# Constitution

Read when the repository has an `.autodev/` directory, or when the human wants rules that bind every autodev round. A constitution holds the project's standing rules, so they are agreed once instead of renegotiated in every Clarify pass.

## Files

| File | Read by | Content |
|---|---|---|
| `.autodev/constitution.json` | the judge, at `init` and re-checked every attempt | mechanical rules, below |

Everything under `.autodev/` is local to this clone: `init` writes the directory into `.git/info/exclude`, so `git status` stays clean and collaborators who do not use autodev see nothing. Prose conventions belong in the project's `AGENTS.md`, not here — `.autodev/` holds only machine-read config and run evidence.

```json
{
  "frozen": ["migrations/", ".github/"],
  "guard_cmd": "pytest -q",
  "budget": {"default_minutes": 30, "max_minutes": 120, "reserve_minutes": 5},
  "generated": ["artifacts/", "build/"]
}
```

| Key | Effect at `init` and after |
|---|---|
| `frozen` | Added to the round's frozen surface and hash-checked every attempt. A round whose `--editable` reaches into these paths is refused. Every listed path must exist. |
| `guard_cmd` | Must pass on the unchanged source, then runs before the agreed command in every `attempt` and again in `verify`. A failing guard makes the attempt invalid and rolls it back. |
| `budget.default_minutes`, `budget.reserve_minutes` | Used for optimization rounds that do not pass `--budget-minutes` or `--reserve-minutes`. Feature and bug-fix rounds stay untimed. |
| `budget.max_minutes` | Any round asking for a larger budget is refused. |
| `generated` | Run-artifact paths the agreed commands write — build output, caches, generated reports. Untracked files under them never block an attempt and rollback sweeps them; committing one is invalid. Must not overlap `frozen`. |

Unknown keys are refused, so a misspelled rule fails loudly instead of silently not applying. `init` records the constitution's repo-side path and SHA-256 in the contract; `start` and every `attempt` re-hash that same file — editing it mid-round invalidates the attempt and `verify` refuses, so the rules cannot be amended silently under a running loop. The file does not need to be committed: the judge reads it in the original checkout, never in the worktree. To share rules with a team, `git add -f` the file deliberately; that is an opt-in, not a requirement.

## Precedence

The constitution is a floor. A round may tighten it — freeze more, grant a smaller budget — but never loosen it. Loosening means amending the constitution: the human edits the file outside any Loop, and the next round runs `init` against the new version. Do not amend it to unblock the current round.

## Choosing the guard

The guard is what must hold at every commit whatever the scenario: the build, the linter, or the existing suite. It can only invalidate an attempt, never accept one, so it adds no second target: optimization still has one score, and the guard is a validity condition like a crash. Keep it fast, because it runs on every attempt inside the time budget.

## Growing a constitution

Do not create one unasked. At Handoff, if a constraint came up again that a previous round also had to agree — a path that must never change, a check that must never break, a budget ceiling — propose adding it to the constitution. The human decides and saves.
