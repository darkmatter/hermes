#!/bin/bash
# Poll a Vapi call until it ends, then print ended reason, cost, summary, and transcript.
# Usage: watch_call.sh <call_id> [vapi_private_key]
# If key omitted, loads via vapi_env.sh (1Password / ~/.vapi-cli.yaml / env).
# Run via terminal(background=true, notify_on_complete=true) so the agent gets pinged when the call ends.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CALL_ID="${1:?usage: watch_call.sh <call_id> [vapi_private_key]}"
if [[ -n "${2:-}" ]]; then
  KEY="$2"
else
  # shellcheck source=vapi_env.sh
  source "$SCRIPT_DIR/vapi_env.sh"
  KEY="$VAPI_API_KEY"
fi

while true; do
  RESP=$(curl -s "https://api.vapi.ai/call/$CALL_ID" -H "Authorization: Bearer <REDACTED>")
  STATUS=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','?'))" 2>/dev/null)
  echo "$(date '+%H:%M:%S') status=$STATUS"
  if [ "$STATUS" = "ended" ]; then
    echo "===CALL ENDED==="
    echo "$RESP" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('Ended reason:', d.get('endedReason'))
print('Duration:', d.get('startedAt'), '->', d.get('endedAt'))
print('Cost: $%.2f' % (d.get('cost') or 0))
print()
print('=== SUMMARY ===')
print((d.get('analysis') or {}).get('summary', d.get('summary', 'No summary')))
print()
print('=== TRANSCRIPT ===')
print((d.get('transcript') or 'No transcript')[:8000])
"
    break
  fi
  sleep 30
done
