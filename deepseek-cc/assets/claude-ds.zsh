# claude-ds: 用 DeepSeek 启动 Claude Code。claude-ds-stop: 停代理。`claude` 仍走 Anthropic。
# 代理存在是因为 CC >=2.1.154 会把 system 塞进 messages,DeepSeek 严格校验报 400;proxy.py 掰正后转发。

claude-ds() {
  local cfgdir="$HOME/.config/claude-deepseek"
  local keyfile="$cfgdir/key.env" proxy="$cfgdir/proxy.py" port="${DS_PROXY_PORT:-8787}"

  [ -f "$keyfile" ] && source "$keyfile"
  if [ -z "$DEEPSEEK_API_KEY" ] || [ "$DEEPSEEK_API_KEY" = "sk-xxxx" ]; then
    echo "❌ 未填 DeepSeek API Key: $keyfile" >&2; return 1
  fi

  if ! lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
    [ -f "$proxy" ] || { echo "❌ 缺少代理脚本: $proxy" >&2; return 1; }
    echo "↻ 启动 DeepSeek 代理 (127.0.0.1:$port)" >&2
    PROXY_PORT="$port" nohup python3 "$proxy" >/tmp/claude-ds-proxy.log 2>&1 &
    disown 2>/dev/null
    local i=0
    while ! lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; do
      sleep 0.2; i=$((i+1))
      [ "$i" -ge 15 ] && { echo "❌ 代理启动失败,见 /tmp/claude-ds-proxy.log" >&2; return 1; }
    done
  fi

  ANTHROPIC_BASE_URL="http://127.0.0.1:$port/anthropic" \
  ANTHROPIC_AUTH_TOKEN="$DEEPSEEK_API_KEY" \
  ANTHROPIC_MODEL="deepseek-v4-pro" \
  ANTHROPIC_DEFAULT_OPUS_MODEL="deepseek-v4-pro" \
  ANTHROPIC_DEFAULT_SONNET_MODEL="deepseek-v4-pro" \
  ANTHROPIC_DEFAULT_HAIKU_MODEL="deepseek-v4-flash" \
  CLAUDE_CODE_SUBAGENT_MODEL="deepseek-v4-flash" \
  CLAUDE_CODE_EFFORT_LEVEL="max" \
  claude "$@"
}

claude-ds-stop() {
  local port="${DS_PROXY_PORT:-8787}" pids
  pids=$(lsof -nP -iTCP:"$port" -sTCP:LISTEN -t 2>/dev/null)
  [ -n "$pids" ] && { echo "$pids" | xargs kill 2>/dev/null && echo "✅ 已停代理 (port $port)"; } || echo "(代理未运行)"
}
