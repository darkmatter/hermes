#!/usr/bin/env bash
# Start local ask_cooper HITL server (Slack-backed). Pair with cloudflared.
set -euo pipefail
export SLACK_BOT_TOKEN=<REDACTED>
export SLACK_CHANNEL="${SLACK_CHANNEL:-D0BG4HJ47GE}"
export HITL_TIMEOUT="${HITL_TIMEOUT:-90}"
export HITL_PORT="${HITL_PORT:-8788}"
exec python3 "$(cd "$(dirname "$0")" && pwd)/ask_cooper_server.py"
