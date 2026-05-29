# Configuration reference

## Environment variables

The launcher sets these only for the `claude` process it spawns (they don't
leak into the user's shell):

| Variable | Value | Meaning |
| --- | --- | --- |
| `ANTHROPIC_BASE_URL` | `http://127.0.0.1:8787/anthropic` (Option B) or `https://api.deepseek.com/anthropic` (Option A / CC ≤2.1.153) | Where requests go |
| `ANTHROPIC_AUTH_TOKEN` | the DeepSeek API key | Auth |
| `ANTHROPIC_MODEL` | `deepseek-v4-pro` | Main model |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | `deepseek-v4-pro` | Opus tier → |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | `deepseek-v4-pro` | Sonnet tier → |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | `deepseek-v4-flash` | Haiku tier → |
| `CLAUDE_CODE_SUBAGENT_MODEL` | `deepseek-v4-flash` | Subagents (cheaper/faster) |
| `CLAUDE_CODE_EFFORT_LEVEL` | `max` | Reasoning effort |

## Models

- `deepseek-v4-pro` — strongest, pricier. `deepseek-v4-flash` — faster, cheaper.
- Both ~1M context, up to 384K output. Legacy names `deepseek-chat` /
  `deepseek-reasoner` still work.
- To minimize cost, set every `deepseek-v4-pro` above to `deepseek-v4-flash`.
- DeepSeek's own mapping when a Claude name is passed: `claude-opus*` →
  `deepseek-v4-pro`; `claude-sonnet*` / `claude-haiku*` / unknown →
  `deepseek-v4-flash`. The explicit env vars above override this.

## Known limitations of DeepSeek's Anthropic endpoint

- Not supported: image input, document input, search-result and redacted-thinking
  content types, **MCP**, container upload.
- Ignored fields: `anthropic-beta`, `anthropic-version`, `top_k`,
  `cache_control`, `disable_parallel_tool_use`, thinking `budget_tokens`.
- Supported: streaming, tool use, thinking mode, `temperature` 0.0–2.0.

Practical effect: MCP servers don't work under `claude-ds`. Use plain `claude`
(Anthropic) when the user needs MCP / image / document features.

## Other shells / platforms

- **bash:** same launcher works; source it from `~/.bashrc`. `claude-ds.zsh` uses
  only POSIX-ish sh plus `lsof`; rename if you prefer.
- **fish / nushell:** translate the function, or just export the env vars inline
  before `claude`.
- **Windows:** there's no `lsof`-based auto-proxy launcher here. Either use
  Option A (downgrade, no proxy), or start `proxy.py` manually
  (`python proxy.py`) and set the env vars in PowerShell:
  ```powershell
  $env:ANTHROPIC_BASE_URL="http://127.0.0.1:8787/anthropic"
  $env:ANTHROPIC_AUTH_TOKEN="<key>"
  $env:ANTHROPIC_MODEL="deepseek-v4-pro"
  # ... (remaining vars from the table) ...
  claude
  ```

## Variant: make plain `claude` default to DeepSeek

If the user wants `claude` itself (not a separate command) to use DeepSeek, put
the env block in `~/.claude/settings.json` instead of using the launcher:

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:8787/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "<key>",
    "ANTHROPIC_MODEL": "deepseek-v4-pro",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "deepseek-v4-pro",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "deepseek-v4-pro",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "deepseek-v4-flash",
    "CLAUDE_CODE_SUBAGENT_MODEL": "deepseek-v4-flash",
    "CLAUDE_CODE_EFFORT_LEVEL": "max"
  }
}
```

Tradeoff: ALL Claude Code usage goes to DeepSeek (MCP/login/image break), and the
proxy must be running. Reversible by deleting the `env` block. Most users are
better served by the separate `claude-ds` launcher.

## Uninstall

Remove the source line from the shell rc, delete `~/.config/claude-deepseek/`,
and `claude-ds-stop` (or kill the proxy on port 8787). For Option A, remove
`DISABLE_UPDATES` and update Claude Code.
