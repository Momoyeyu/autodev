# Installing Claude Code (with network fallbacks)

Check first: `claude --version`. If it prints a version, skip this file.

Requires **Node.js 18+** for the npm path (`node --version`).

## Default

```bash
npm install -g @anthropic-ai/claude-code
```

Never use `sudo npm install -g` — it makes the global dir root-owned and causes
EACCES on every later npm op.

Verify, then run the official diagnostic:
```bash
claude --version
claude doctor
```

## If npm fails (timeouts / network, common in China)

Root cause: the npm package still downloads a binary from
`storage.googleapis.com`, which is unreliable from some networks. Options, in
rough order of preference:

**1. Native installer** (doesn't go through npm):
```bash
curl -fsSL https://claude.ai/install.sh | bash          # macOS / Linux / WSL
```
```powershell
irm https://claude.ai/install.ps1 | iex                 # Windows PowerShell
```

**2. npmmirror (Aliyun) registry:**
```bash
npm install -g @anthropic-ai/claude-code --registry=https://registry.npmmirror.com
```

**3. Homebrew (macOS/Linux) — doesn't depend on GCS:**
```bash
brew install claude-code
```
Note: Homebrew installs don't auto-update; `brew upgrade claude-code` manually.

**4. WinGet (Windows):** search for the Claude Code package, or use the native
installer above.

**5. Behind a proxy:** export `HTTP_PROXY` / `HTTPS_PROXY` before installing.

## Windows note

Install **Git for Windows** first — Claude Code depends on it.

## DeepSeek official references

- Claude Code integration: https://api-docs.deepseek.com/quick_start/agent_integrations/claude_code
- Anthropic-compatible API: https://api-docs.deepseek.com/guides/anthropic_api
