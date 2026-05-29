---
name: consistent-commit
description: Use when about to create a git commit in any repo — before running git commit — to match the author identity, email, and message style to the repo's existing history instead of guessing or using defaults.
---

# Git Commit Consistency

## Overview

A new commit must look like it belongs to the repo. Match the **author/email** and the **message style** to what the history already shows — never to your defaults, and never to HEAD alone.

**Core principle:** The latest commit may be noise an agent introduced last time. Read a *group* of commits to find the real convention. When the group disagrees, ask — don't guess.

## When to Use

- Before EVERY `git commit` (or amend/rebase that authors commits).
- Triggers: "commit this", "提交", "make a commit", squashing, cherry-picking.

Skip only when the user gave an explicit identity/format for this commit.

## The Iron Law

```
NO COMMIT BEFORE INSPECTING A GROUP OF PAST COMMITS
```

Inspecting only HEAD is not inspecting. One commit is not a sample.

## Mandatory Workflow

**Step 1 — Sample identity across a group (not HEAD):**
```bash
git log -20 --format='%an <%ae>' | sort | uniq -c | sort -rn
```
Pick the **dominant** human identity. Use that exact name + email for `--author` / `user.name` / `user.email`.

**Step 2 — Read message style across a group:**
```bash
git log -15 --format='%n=== %s%n%b'
```
Determine each signal below from what you see — see [reading-history.md](reading-history.md) for how to read each one:
- **Length:** terse subject-only vs. subject + explanatory body?
- **Co-author:** is there a `Co-Authored-By:` trailer? If history has NONE, add NONE.
- **Fixed format:** `Signed-off-by:`, Conventional Commits (`feat:`/`fix:`), issue refs, language (EN/中文), capitalization?

**Step 3 — Write the commit to match.** Mirror the dominant pattern exactly. No body if history has none. No trailer if history has none.

## Decision Rules (strict)

| Situation | Action |
|-----------|--------|
| Group shows ONE dominant identity | Use it. |
| Group is split across several humans | Use the one matching the current user (email/contact); if still unclear, **ASK**. |
| HEAD identity differs from the rest of the group | Treat HEAD as suspect noise. Follow the group, not HEAD. |
| Style is mixed (some bodies, some not) | Match the most recent *consistent* run; if no clear pattern, **ASK**. |
| Repo has <3 commits, or you are unsure of anything | **ASK the user** before committing. Do not invent. |

When in doubt, asking costs one sentence. Guessing wrong pollutes history permanently.

## Red Flags — STOP

- "HEAD says X, I'll just copy HEAD" → one commit is not a sample. Run Step 1.
- "I'll add a `Co-Authored-By: Claude` trailer to be helpful" → only if history already has it.
- "I'll write a nice detailed body" → only if history has bodies. Match length.
- "My git config identity is probably fine" → verify against the group first.
- "Close enough" → identity/format is binary. Match exactly or ask.

## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "The last commit shows the convention" | The last commit may be a prior agent's mistake. Sample ≥15. |
| "Adding co-author is standard / polite" | It's noise if the repo never uses it. Match the repo. |
| "A detailed body is always better" | Inconsistent style is worse than terse. Match length. |
| "I'll use the session email" | The repo's history defines identity, not the session. |
| "Asking is annoying" | Wrong author/format in history is far more annoying and is permanent. |

## Verification Checklist

Before `git commit`:
- [ ] Ran Step 1 across ≥15 commits; chose the dominant identity.
- [ ] Confirmed author + email match that identity exactly.
- [ ] Read ≥10 message bodies; identified length, co-author, fixed format.
- [ ] Message matches: no body unless history has bodies; no trailer unless history has trailers; same prefix/format/language.
- [ ] If ANY signal was ambiguous, asked the user instead of guessing.

Can't check all boxes? Don't commit yet.
