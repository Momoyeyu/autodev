# Reading History — Signal Interpretation

Load this when Step 2 of the workflow needs detail. How to read each signal, with worked examples and edge cases.

## Contents
- Identity signal
- Length signal
- Co-author signal
- Fixed-format signal
- Edge cases
- Worked examples

## Identity signal

```bash
git log -20 --format='%an <%ae>' | sort | uniq -c | sort -rn
```
Output is a frequency table. The top line is usually the convention.

- **One dominant line** (e.g. `18 momoyeyu <momoyeyu@outlook.com>`) → use it verbatim, including letter case (`momoyeyu`, not `Momoyeyu`).
- **HEAD differs from the dominant** → HEAD is suspect. A prior agent may have committed with a wrong identity or a `Co-Authored-By`/`noreply` address. Follow the dominant, not HEAD.
- **`%an`/`%ae` (author) vs `%cn`/`%ce` (committer)** can differ on rebased/cherry-picked repos. Match the **author** unless the repo clearly standardizes the committer too.
- **Bot/no-reply addresses** (`...@users.noreply.github.com`, `noreply@`) appearing once or twice are usually noise — ignore them unless they dominate.

## Length signal

Read bodies with:
```bash
git log -15 --format='%n=== %s%n%b'
```

- **Subject-only** (no text after the subject line) across the group → write subject only. Do NOT add a body.
- **Subject + body** consistently → write a body in the same shape (paragraph vs bullet list, wrap width, imperative vs past tense).
- **Mixed** → match the most recent *consistent run*. If the last 8 are subject-only, go subject-only even if older ones had bodies.

Subject style to copy: capitalization, trailing period or not, imperative ("add X") vs descriptive ("added X"), max length, scope prefixes.

## Co-author signal

Search explicitly — it is the highest-risk default to get wrong:
```bash
git log -30 --format='%b' | grep -i 'co-authored-by'
```

- **Zero matches** → the repo does not use co-author trailers. Add NONE. Adding `Co-Authored-By: Claude ...` here is pollution.
- **Consistent matches** → the repo expects them. Match the exact trailer format and email used.

Default bias: when unsure, OMIT the trailer. It is easier to add one later than to rewrite history to remove it.

## Fixed-format signal

Scan subjects and trailers for a mandatory structure:
```bash
git log -20 --format='%s'        # subjects: prefixes, language, casing
git log -20 --format='%b' | grep -iE 'signed-off-by|change-id|refs?|closes|#[0-9]+'
```

Look for:
- **Conventional Commits**: `feat:`, `fix:`, `chore:`, `feat(scope):` — if present, match type+scope grammar.
- **`Signed-off-by: Name <email>`** (DCO): if the group has it, every commit needs it (`git commit -s` reproduces it). If absent, don't add it.
- **`Change-Id:`** (Gerrit), **issue refs** (`Closes #123`, `JIRA-456`): reproduce only if the group consistently uses them.
- **Language**: if subjects are in 中文, write 中文; if EN, write EN. Don't switch.

## Edge cases

| Case | Handling |
|------|----------|
| Brand-new repo / <3 commits | No convention exists yet. ASK the user for identity + style. |
| First commit ever | Ask; or use the user's known identity from `git config` after confirming. |
| Monorepo with many contributors | Sample is split. Match the identity tied to the current user; for style, match the most common pattern in the touched subtree's recent commits. |
| Squash/merge commits dominate | Read non-merge commits: `git log --no-merges -15 --format='%n=== %s%n%b'`. |
| Reflog/amend in progress | Identity for an amend should match the original commit's author unless the user says otherwise. |

## Worked examples

**Example A — terse, solo, lowercase identity**

Step 1 output:
```
  19 momoyeyu <momoyeyu@outlook.com>
   1 Momoyeyu <momoyeyu@outlook.com>
```
Step 2 subjects: `add skills registry`, `require config path`, `update skill` — all subject-only, lowercase, imperative, no trailers.

→ Author `momoyeyu <momoyeyu@outlook.com>`, subject-only lowercase imperative message, NO body, NO co-author. The single `Momoyeyu` line is noise; ignore it.

**Example B — HEAD is the noise**

Step 1 output:
```
  14 Jane Dev <jane@corp.com>
   1 claude <noreply@anthropic.com>
```
HEAD is the `claude <noreply...>` commit.

→ A prior agent committed with the wrong identity. Use `Jane Dev <jane@corp.com>`. Had you copied HEAD, you'd have compounded the error.

**Example C — Conventional Commits + sign-off**

Subjects: `feat(api): add pagination`, `fix(db): handle null rows`. Bodies all end with `Signed-off-by: Jane Dev <jane@corp.com>`.

→ Use `type(scope): summary` format and commit with `-s`. No co-author trailer (none present).
