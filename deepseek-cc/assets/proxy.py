#!/usr/bin/env python3
"""DeepSeek <-> Claude Code 兼容代理。

CC >=2.1.154 把 role=system 塞进 messages,DeepSeek 严格校验报 400。
本代理把这些 system 上提到顶层 system 字段再转发,响应(含 SSE)原样回传。
纯标准库,只监听 127.0.0.1。用法: [PROXY_PORT=8787] python3 proxy.py
"""
import json
import os
import sys
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UPSTREAM = "https://api.deepseek.com/anthropic"
HOST = "127.0.0.1"
PORT = int(os.environ.get("PROXY_PORT", "8787"))

# 转发时需要丢弃的逐跳(hop-by-hop)请求头 / 由 urllib 自行处理的头
DROP_REQ = {"host", "content-length", "connection", "accept-encoding"}
# 回传时需要丢弃的头(我们用 connection: close 自己界定响应边界)
DROP_RESP = {"transfer-encoding", "connection", "content-length", "content-encoding"}


def _as_text(content):
    """把 system 内容统一成字符串。content 可能是 str,也可能是 Anthropic 的
    content block 列表(如 [{"type":"text","text":"..."}]),做尽量保真的提取。"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for blk in content:
            if isinstance(blk, dict) and blk.get("type") == "text":
                parts.append(blk.get("text", ""))
            else:
                parts.append(json.dumps(blk, ensure_ascii=False))
        return "\n".join(parts)
    return json.dumps(content, ensure_ascii=False)


def fix_body(raw: bytes) -> bytes:
    """把 messages 里 role=system 的内容上提到顶层 system。"""
    try:
        data = json.loads(raw)
    except Exception:
        return raw  # 不是 JSON 就原样放行
    if not isinstance(data, dict) or "messages" not in data:
        return raw

    system_parts = []
    if data.get("system"):
        system_parts.append(_as_text(data["system"]))

    kept = []
    for msg in data.get("messages", []):
        if isinstance(msg, dict) and msg.get("role") == "system":
            system_parts.append(_as_text(msg.get("content", "")))
        else:
            kept.append(msg)

    data["messages"] = kept
    if system_parts:
        data["system"] = "\n\n".join(p for p in system_parts if p)
    elif "system" in data:
        del data["system"]
    return json.dumps(data, ensure_ascii=False).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _proxy(self, method: str):
        length = int(self.headers.get("Content-Length", 0) or 0)
        body = self.rfile.read(length) if length else b""
        # 只在 messages 接口上做改写,其它接口原样转发
        if "/messages" in self.path and body:
            body = fix_body(body)

        headers = {
            k: v for k, v in self.headers.items() if k.lower() not in DROP_REQ
        }
        url = UPSTREAM + self.path[len("/anthropic"):] if self.path.startswith("/anthropic") else UPSTREAM + self.path
        req = urllib.request.Request(url, data=body or None, method=method, headers=headers)

        try:
            resp = urllib.request.urlopen(req, timeout=600)
        except urllib.error.HTTPError as e:
            # 把 DeepSeek 的错误码 + 错误体原样回传
            err = e.read()
            self.send_response(e.code)
            self.send_header("Content-Type", e.headers.get("Content-Type", "application/json"))
            self.send_header("Content-Length", str(len(err)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(err)
            return
        except Exception as e:
            msg = json.dumps({"type": "error", "error": {"type": "proxy_error", "message": str(e)}}).encode()
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(msg)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(msg)
            return

        # 流式透传:不声明 Content-Length,用 Connection: close 界定边界
        self.send_response(resp.status)
        for k, v in resp.headers.items():
            if k.lower() not in DROP_RESP:
                self.send_header(k, v)
        self.send_header("Connection", "close")
        self.end_headers()
        try:
            while True:
                chunk = resp.read(8192)
                if not chunk:
                    break
                self.wfile.write(chunk)
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            resp.close()

    def do_POST(self):
        self._proxy("POST")

    def do_GET(self):
        self._proxy("GET")

    def log_message(self, *args):
        pass  # 静默,避免污染日志


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    sys.stderr.write(f"[deepseek-proxy] listening on http://{HOST}:{PORT}/anthropic -> {UPSTREAM}\n")
    sys.stderr.flush()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
