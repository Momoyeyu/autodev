---
name: deepseek-cc
description: "Configure Claude Code to use DeepSeek models instead of Anthropic. Use this whenever the user wants to point Claude Code at DeepSeek (the DeepSeek Anthropic-compatible API), run Claude Code with deepseek-v4-pro or deepseek-v4-flash, set up a cheaper Claude Code, or fix the 400 'messages role unknown variant system' error that DeepSeek returns on recent Claude Code versions (2.1.154 and newer). Works for any coding agent (Claude Code, Cursor, Codex, Gemini CLI, etc.) executing the setup on the user's machine."
---

# DeepSeek for Claude Code

Point Claude Code at DeepSeek's Anthropic-compatible API. The design goal: a
separate `claude-ds` launcher that uses DeepSeek, leaving the default `claude`
command untouched on Anthropic — so the user's existing login, MCP servers, and
subscription keep working. Switching back is just running `claude`.

You (the agent running this) may be from any vendor. Use whatever shell/file
tools you have; the steps are tool-agnostic. Do not assume Claude Code itself is
the one running you.

## The one critical gotcha — read this first

Claude Code **>= 2.1.154** puts `role: "system"` messages inside the `messages`
array (built-in skills list, SessionStart hook context). DeepSeek's endpoint
strictly validates the Anthropic schema and rejects this:

```
API Error: 400 Failed to deserialize ... messages[1].role: unknown variant `system`
```

This is a Claude Code regression, **not** a misconfiguration. There are two
fixes — let the user choose. See `references/fix-400-system-bug.md` for the full
comparison. Short version:

- **Option B (proxy, recommended):** run a tiny local proxy that hoists `system`
  messages back to the top-level field. Keeps Claude Code at the latest version
  and fully isolates DeepSeek from the user's Anthropic usage. This skill bundles
  the proxy and the launcher wires it up automatically.
- **Option A (downgrade):** pin Claude Code to 2.1.153 and disable auto-update.
  Simplest, but rolls back the *global* `claude` binary — the user's Anthropic
  Claude Code goes back too, and updates get frozen.

If the user is on Claude Code <= 2.1.153, neither is needed — direct connection
works (set `ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic`).

## Steps

### 1. Ensure Claude Code is installed

Check: `claude --version`. If missing, or if `npm install` fails on network
issues (common in China — the npm package downloads a binary from
storage.googleapis.com), see `references/install-claude-code.md` for the install
paths and fallbacks (native installer, npmmirror, Homebrew/WinGet, proxy).

### 2. Get a DeepSeek API key

Ask the user to create one at https://platform.deepseek.com/api_keys . Never
print the key back, never commit it. Account needs balance (pay-as-you-go).

### 3. Confirm Claude Code version and pick the fix

Run `claude --version`. If >= 2.1.154, ask the user to pick Option A or B
(default B). Read `references/fix-400-system-bug.md` and follow the chosen path.

### 4. Lay down the config (Option B)

Create the config dir `~/.config/claude-deepseek/` and:

- Copy `assets/proxy.py` and `assets/claude-ds.zsh` there **verbatim — do not read
  their contents into your context; you don't need to understand them to install
  them.** Just copy the files. (If the skill's `assets/` are not on disk — e.g.
  you only have SKILL.md — fetch them raw instead, no need to print them:
  `curl -fsSLO` from
  `https://raw.githubusercontent.com/Momoyeyu/skills/master/deepseek-cc/assets/{proxy.py,claude-ds.zsh}`.)
- Copy `assets/key.env` there, then have the user fill their key. `chmod 600` it.
- Wire up the launcher: add ONE line to the user's shell rc (`~/.zshrc` / `~/.bashrc`):
  ```
  [ -f ~/.config/claude-deepseek/claude-ds.zsh ] && source ~/.config/claude-deepseek/claude-ds.zsh
  ```
  Keep the rc clean — one source line, not the whole function body. (The proxy
  defaults to port 8787; if that port is taken, set `DS_PROXY_PORT` to another
  value — otherwise the launcher's "already running?" check misfires on it.)

For non-zsh/bash shells, Windows, the env-var meanings, model choices, and the
`settings.json` "make `claude` default to DeepSeek" variant, see
`references/configuration.md`.

### 5. Verify

`python3` must be available (the proxy is stdlib-only, no pip). Reload the shell
(`source ~/.zshrc`) and run a real non-interactive check:

```
claude-ds -p "reply: ok"
```

A normal reply means the whole chain works (launcher → auto-started proxy →
DeepSeek). Confirm usage shows up at https://platform.deepseek.com/ . If you see
the 400 `system` error, the proxy isn't in the path — recheck `ANTHROPIC_BASE_URL`
points at `http://127.0.0.1:8787/anthropic`, not directly at DeepSeek.

### 6. Tell the user three things

1. **Where the key lives:** `~/.config/claude-deepseek/key.env`.
2. **How to use DeepSeek:** `claude-ds` (params identical to `claude`).
   `claude-ds-stop` stops the background proxy.
3. **How to switch back to Anthropic:** just run `claude`. It was never touched.

## Known limitations of DeepSeek's endpoint

No image/document input, no MCP, no container upload; `cache_control`,
`anthropic-beta`, `top_k`, thinking `budget_tokens` are ignored. So under
`claude-ds` the user's MCP servers won't work — that's expected; use `claude`
(Anthropic) when they need those. Details in `references/configuration.md`.
