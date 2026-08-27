# Kill procedure, tool wiring, AA lessons

## Kill / stop

```bash
source ~/.hermes/skills/communication/communications/scripts/vapi_env.sh
CALL=<id>
CONTROL=$(curl -sS -H "Authorization: Bearer <REDACTED>" \
  "https://api.vapi.ai/call/$CALL" | python3 -c 'import sys,json;print((json.load(sys.stdin).get("monitor") or {}).get("controlUrl",""))')
PROVIDER=$(curl -sS -H "Authorization: Bearer <REDACTED>" \
  "https://api.vapi.ai/call/$CALL" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("phoneCallProviderId") or "")')

curl -sS -X POST "$CONTROL" -H 'Content-Type: application/json' -d \
 '{"type":"add-message","message":{"role":"system","content":"STOP. No cancel/rebook/pay. Brief goodbye if human, then end."},"triggerResponseEnabled":true}'
curl -sS -X POST "$CONTROL" -H 'Content-Type: application/json' -d '{"type":"end-call"}'
# still in-progress:
curl -sS -X DELETE -H "Authorization: Bearer <REDACTED>" "https://api.vapi.ai/call/$CALL"
# Twilio hard stop:
export PATH="$HOME/.local/bin:$PATH"
TWILIO_SID=$(OP_TIMEOUT=8 op item get vapi --vault dev --fields twilio-sid --reveal)
TWILIO_TOKEN=<REDACTED>
curl -sS -X POST "https://api.twilio.com/2010-04-01/Accounts/${TWILIO_SID}/Calls/${PROVIDER}.json" \
  -u "${TWILIO_SID}:${TWILIO_TOKEN}" --data-urlencode "Status=completed"

curl -sS -H "Authorization: Bearer <REDACTED>" 'https://api.vapi.ai/call?limit=10' \
 | python3 -c 'import sys,json;print([(c["id"],c["status"]) for c in json.load(sys.stdin) if c.get("status") in ("in-progress","ringing","queued")])'
pkill -f "watch_call.sh $CALL" 2>/dev/null || true
```

Note: `end-call` may return ok while status stays `in-progress` and transcript stays empty — escalate to DELETE + Twilio.

## Tool attach pattern (no duplicate dtmf)

```json
"model": {
  "provider": "anthropic",
  "model": "claude-haiku-4-5-20251001",
  "toolIds": [
    "c0849875-e579-454c-a1ee-95c969534fb8",
    "f30e31b9-f6ee-48f6-8bec-1d518a43e369"
  ],
  "tools": [ { "type": "transferCall", "...": "warm-transfer-experimental block" } ]
}
```

PATCH permanent assistant model must include full model object (provider/model/messages/toolIds) — bare `{toolIds}` alone can fail validation.

## HITL tunnel refresh

```bash
cloudflared tunnel --url http://127.0.0.1:8788
# copy https://….trycloudflare.com
curl -sS -X PATCH "https://api.vapi.ai/tool/f30e31b9-f6ee-48f6-8bec-1d518a43e369" \
  -H "Authorization: Bearer <REDACTED>" -H "Content-Type: application/json" \
  -d '{"server":{"url":"https://NEW.trycloudflare.com/vapi/tools","timeoutSeconds":120}}'
```

Slack channel for replies: `D0BG4HJ47GE` only.

## Analytics

`groupBy` is an **array**:

```json
{"queries":[{"table":"call","name":"ends","groupBy":["endedReason"],
 "operations":[{"operation":"count","column":"id","alias":"calls"}]}]}
```

Helper: `.../communications/scripts/vapi_analytics.sh`.

## Messaging

- SMS A2P **30034** undelivered from bare Twilio long code — use iMessage.
- `osascript` via temp `.scpt` file; BB private-api often false on macOS 26.

## AA / payment session (2026-07-29) — snapshot only

- Locator `WSZTVR`, BA `BRSK4R`, Telavaya Reynolds DOB 02/20/1991, Aug 2 LAX–LHR goal.
- Early IVR failures until phonetics + dtmf.
- Kim ~+$440 change then credit path; Hazel cancel→credit; unpaid tickets ~$906 then later ~$697 with credit.
- Payment call amex multi-decline; ask_cooper timed out; warm transfer unused; killed after ~$5 + prior ~$6 costs.
- Always re-read **live app/PNR** before assuming cancel/credit/booked state.
