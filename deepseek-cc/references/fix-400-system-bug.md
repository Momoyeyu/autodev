# Fixing the `messages[].role: unknown variant system` 400 error

## Cause

Anthropic's Messages API spec: `messages[].role` may only be `user` or
`assistant`; system content goes in the top-level `system` field.

Claude Code **>= 2.1.154** additionally injects `role: "system"` entries into the
`messages` array (built-in skills list at index 1, SessionStart hook context).
Anthropic's own endpoint tolerates this; DeepSeek's Anthropic-compatible endpoint
validates strictly and rejects it at JSON-parse time:

```
API Error: 400 Failed to deserialize the JSON body into the target type:
messages[1].role: unknown variant `system`, expected `user` or `assistant`
```

Last known-good version: **2.1.153**. This is a Claude Code regression, not a
config error. Upstream tracking: deepseek-ai/awesome-deepseek-agent#167.

Things that do NOT fix it: disabling plugins (built-in skills still inject it),
clean config dir, `autoUpdates: false` (not a valid key), `minimumVersion`
(doesn't block upgrades).

---

## Option B — local proxy (recommended)

Keeps Claude Code at the latest version. A tiny stdlib-only Python proxy listens
on `127.0.0.1:8787`, hoists every `messages[].role == "system"` entry into the
top-level `system` field, then forwards to `https://api.deepseek.com/anthropic`.
Streams SSE through and passes upstream errors back unchanged.

Wiring: point `ANTHROPIC_BASE_URL` at the proxy
(`http://127.0.0.1:8787/anthropic`) instead of DeepSeek directly. The bundled
`assets/claude-ds.zsh` launcher auto-starts the proxy on demand, so the user
never manages it manually.

- Pros: latest Claude Code everywhere; DeepSeek fully isolated from the user's
  Anthropic usage; no global changes; trivially reversible (stop proxy, repoint
  URL).
- Cons: one extra local background process (~few MB); one extra hop.
- Requirement: `python3` (3.10+; stdlib only, no pip).

The proxy is `assets/proxy.py`. Audit it — it only rewrites JSON and forwards;
binds to loopback only; stores/uploads nothing.

---

## Option A — downgrade to 2.1.153 + disable auto-update

Simplest, but affects the **global** `claude` binary, so the user's Anthropic
Claude Code is also rolled back, and updates are frozen.

**macOS / Linux / WSL:**
```bash
claude install 2.1.153 --force
claude --version   # expect 2.1.153
```

**Windows (PowerShell):**
```powershell
& ([scriptblock]::Create((irm https://claude.ai/install.ps1))) 2.1.153
```

Block auto-update in `~/.claude/settings.json` (Windows:
`%USERPROFILE%\.claude\settings.json`):
```json
{ "env": { "DISABLE_UPDATES": "1" } }
```

Notes: use `DISABLE_UPDATES` in the `env` block (the documented switch).
`DISABLE_AUTOUPDATER` alone still lets `claude update` upgrade back to the broken
build. With this option, `ANTHROPIC_BASE_URL` can point directly at
`https://api.deepseek.com/anthropic` — no proxy needed.

When the user later wants the newest Claude Code, they remove `DISABLE_UPDATES`
and update, but then must switch to Option B to use DeepSeek again.

---

## Decision guide

- User actively uses Anthropic Claude Code at the latest version, or wants to
  keep updating → **Option B**.
- User rarely touches Anthropic Claude Code and wants the absolute simplest setup
  → **Option A** is acceptable.
- User is on <= 2.1.153 already → neither; connect directly to DeepSeek.
