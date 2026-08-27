#!/usr/bin/env bash
# Quick Vapi analytics pull (POST /analytics).
# Usage:
#   vapi_analytics.sh [days] [timezone]
# Env:
#   VAPI_KEY or VAPI_API_KEY — private key
#   else: ~/.local/bin/op item get vapi --vault dev (SA only; no biometric)
# Examples:
#   vapi_analytics.sh           # last 7 days, America/Los_Angeles
#   vapi_analytics.sh 30 UTC
set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"

DAYS="${1:-7}"
TZ_NAME="${2:-America/Los_Angeles}"

if [[ -z "${VAPI_KEY:-${VAPI_API_KEY:-}}" ]]; then
  if command -v op >/dev/null 2>&1; then
    VAPI_KEY=<REDACTED>
  else
    echo "Set VAPI_KEY/VAPI_API_KEY or use SA op wrapper (~/.local/bin/op --vault dev)." >&2
    exit 1
  fi
else
  VAPI_KEY=<REDACTED>
fi

# Portable-ish start time (BSD date on macOS, GNU date elsewhere)
if date -u -v-"${DAYS}"d +%Y-%m-%dT%H:%M:%SZ >/dev/null 2>&1; then
  START="$(date -u -v-"${DAYS}"d +%Y-%m-%dT%H:%M:%SZ)"
else
  START="$(date -u -d "${DAYS} days ago" +%Y-%m-%dT%H:%M:%SZ)"
fi
END="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

BODY=$(cat <<EOF
{
  "queries": [
    {
      "table": "call",
      "name": "by_ended_reason",
      "groupBy": "endedReason",
      "timeRange": {
        "step": "day",
        "start": "${START}",
        "end": "${END}",
        "timezone": "${TZ_NAME}"
      },
      "operations": [
        {"operation": "count", "column": "id", "alias": "calls"},
        {"operation": "sum", "column": "duration", "alias": "sumDuration"},
        {"operation": "sum", "column": "cost", "alias": "sumCost"},
        {"operation": "avg", "column": "cost", "alias": "avgCost"}
      ]
    },
    {
      "table": "call",
      "name": "totals",
      "timeRange": {
        "start": "${START}",
        "end": "${END}",
        "timezone": "${TZ_NAME}"
      },
      "operations": [
        {"operation": "count", "column": "id", "alias": "calls"},
        {"operation": "sum", "column": "duration", "alias": "sumDuration"},
        {"operation": "sum", "column": "cost", "alias": "sumCost"}
      ]
    }
  ]
}
EOF
)

echo "range: ${START} → ${END} (${TZ_NAME}, last ${DAYS}d)" >&2
curl -sS -X POST "https://api.vapi.ai/analytics" \
  -H "Authorization: Bearer <REDACTED>" \
  -H "Content-Type: application/json" \
  -d "${BODY}" | python3 -m json.tool
