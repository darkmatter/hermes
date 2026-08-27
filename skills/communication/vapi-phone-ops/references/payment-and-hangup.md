# Payment on-call + hangup discipline

Lessons from multi-hour AA rebook/payment sessions (Jul 2026).

## Before dialing with a card

- [ ] PNR/app/email state known (already canceled? open credit? unpaid hold?)
- [ ] Single goal sentence (ticket Aug 2 / pay remaining / restore Jul 30 — pick one)
- [ ] **One** card resolved from 1Password into override (prefer Amex Platinum / `cm` vault)
- [ ] Cardholder name matches what agent will hear; ZIP strategy set (90015 first)
- [ ] Max auto $ in prompt; ask_cooper above cap
- [ ] If cardholder must join: warm-transfer # and/or Cooper (310) 989-7067
- [ ] HITL server + tunnel healthy if ask_cooper may fire
- [ ] Payload file mode 600; delete after successful POST

## In-call payment behavior

1. Read and confirm quote **before** authorizing.
2. On card request: slow digit groups; Amex 15 + 4-digit CID.
3. On decline: one careful re-read max, then stop.
4. Do not switch to a second invent-ed number. Pull real alternate via Cooper/HITL.
5. Do not cancel remaining inventory because payment failed — document and callback.
6. Before irreversible **cancel** of a still-valid flight: ensure credit/rebook path + payment readiness, or ask_cooper.

## Observed failure modes

| Mode | Symptom | Fix |
|---|---|---|
| Wrong card memory | Inject didn't stick; Levi reuses earlier PAN | Short system inject + "discard prior card"; keep payment block high in prompt |
| Infinite decline loop | Agent retries, Levi re-speaks | Hard stop after 2; cardholder/issuer |
| Cancel then unpaid | PNR gutted, not ticketed | Verify before redial; person-on-phone preferred |
| Stuck API call | `in-progress`, empty transcript | DELETE call + Twilio completed |
| ask_cooper miss | Timeout, continues charging | Treat timeout as no-authority |

## Kill sequence (runaway Levi)

```bash
source ~/.hermes/skills/communication/communications/scripts/vapi_env.sh
CALL=<id>
CONTROL=$(curl -sS -H "Authorization: Bearer <REDACTED>" \
  "https://api.vapi.ai/call/$CALL" | python3 -c 'import sys,json;print((json.load(sys.stdin).get("monitor")or{}).get("controlUrl",""))')

curl -sS -X POST "$CONTROL" -H 'Content-Type: application/json' -d '{
  "type":"add-message",
  "message":{"role":"system","content":"STOP. No more cancel/rebook/payment. Brief goodbye if human present, then end."},
  "triggerResponseEnabled":true
}'
curl -sS -X POST "$CONTROL" -H 'Content-Type: application/json' -d '{"type":"end-call"}'
# if still in-progress:
curl -sS -X DELETE -H "Authorization: Bearer <REDACTED>" "https://api.vapi.ai/call/$CALL"
# Twilio if needed:
# TWILIO_SID/TOKEN from 1P vapi; CA… = phoneCallProviderId
# curl -X POST .../Calls/$CA.json -u sid:token --data Status=completed
```

## After a messy payment call

Report only what agents said + APIs show; **never claim ticketed** until Cooper/app confirms locators/emails/charges. Send handoff human a concise status iMessage (Studio BB preferred).
