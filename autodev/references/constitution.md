# Constitution

Read when the repository has an `.autodev/` directory, or when the human wants rules that bind every autodev round. A constitution holds the project's standing rules, so they are agreed once instead of renegotiated in every Clarify pass.

## Files

| File | Read by | Content |
|---|---|---|
| `.autodev/constitution.json` | the judge, at `init` | mechanical rules, below |
| `.autodev/principles.md` | you, at the start of Clarify | optional prose: coding conventions, architectural boundaries, review expectations |

```json
{
  "frozen": ["migrations/", ".github/"],
  "guard_cmd": "pytest -q",
  "budget": {"default_minutes": 30, "max_minutes": 120, "reserve_minutes": 5}
}
```

| Key | Effect at `init` and after |
|---|---|
| `frozen` | Added to the round's frozen surface and hash-checked every attempt. A round whose `--editable` reaches into these paths is refused. Every listed path must exist. |
| `guard_cmd` | Must pass on the unchanged source, then runs before the agreed command in every `attempt` and again in `verify`. A failing guard makes the attempt invalid and rolls it back. |
| `budget.default_minutes`, `budget.reserve_minutes` | Used for optimization rounds that do not pass `--budget-minutes` or `--reserve-minutes`. Feature and bug-fix rounds stay untimed. |
| `budget.max_minutes` | Any round asking for a larger budget is refused. |

Unknown keys are refused, so a misspelled rule fails loudly instead of silently not applying. `init` records the constitution's path and hash in the contract and freezes the file itself for the whole round. Commit the constitution before Loop: the worktree is created from a commit, and `start` refuses a worktree whose frozen files, the constitution included, differ from what `init` recorded.

## Precedence

The constitution is a floor. A round may tighten it — freeze more, grant a smaller budget — but never loosen it. Loosening means amending the constitution: the human edits and commits the file outside any Loop, and the next round runs `init` against the new version. Do not amend it to unblock the current round.

## Choosing the guard

The guard is what must hold at every commit whatever the scenario: the build, the linter, or the existing suite. It can only invalidate an attempt, never accept one, so it adds no second target: optimization still has one score, and the guard is a validity condition like a crash. Keep it fast, because it runs on every attempt inside the time budget.

## Principles

Read `principles.md` before drafting the Clarify artifact and apply what bears on the task. When the proposed blueprint, tests, or limits depend on a principle, name it in the Clarify review so the human sees why. The judge does not check principles; they are the part of the constitution that stays prose.

## Growing a constitution

Do not create one unasked. At Handoff, if a constraint came up again that a previous round also had to agree — a path that must never change, a check that must never break, a budget ceiling — propose adding it to the constitution. The human decides and commits.
