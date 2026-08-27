#!/bin/bash
# Poll a Vapi call until it ends, then print ended reason, cost, summary, and transcript.
# Usage: watch_call.sh <call_id> <vapi_private_key>
# Run via terminal(background=true, notify_on_complete=true) so the agent gets pinged when the call ends.
# Note: if endedReason=assistant-forwarded-call, Vapi monitoring stops at the bridge — no post-transfer audio.

CALL_ID="${1:?usage: watch_call.sh <call_id> <vapi_private_key>}"
KEY="${2:?usage: watch_call.sh <call_id> <vapi_private_key>}"

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
print('Cost: \$%.2f' % (d.get('cost') or 0))
dest = d.get('destination') or d.get('forwardedPhoneNumber')
if dest:
    print('Forwarded/destination:', dest)
print()
print('=== SUMMARY ===')
print(d.get('analysis', {}).get('summary', d.get('summary', 'No summary')))
print()
print('=== TRANSCRIPT ===')
print(d.get('transcript', 'No transcript')[:8000])
"
    break
  fi
  sleep 30
done
