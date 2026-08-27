#!/usr/bin/env bash
# Probe local chrome-mcp-bridge listeners and optional CDP readiness.
set -euo pipefail

echo "== listeners =="
lsof -nP -iTCP:12306,12307 -sTCP:LISTEN 2>/dev/null || echo "(none)"

echo
echo "== bridge processes =="
pgrep -fl mcp-chrome-bridge || echo "(none)"

echo
echo "== CDP /json/version on common ports =="
for p in 9222 9229 9333 12306 12307; do
  code=$(curl -sS -m 1 -o "/tmp/cdp_$p.json" -w "%{http_code}" "http://127.0.0.1:$p/json/version" 2>/dev/null || echo fail)
  head=$(head -c 120 "/tmp/cdp_$p.json" 2>/dev/null || true)
  echo ":$p -> $code ${head}"
done

echo
echo "== MCP initialize smoke (12307 then 12306) =="
for port in 12307 12306; do
  if ! lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
    echo ":$port not listening"
    continue
  fi
  # Minimal check: Accept headers required; may 500 if transport already held
  resp=$(curl -sS -m 3 -X POST "http://127.0.0.1:$port/mcp" \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json, text/event-stream' \
    -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"0"}}}' \
    2>&1 | head -c 240 || true)
  echo ":$port POST /mcp -> ${resp}"
done
