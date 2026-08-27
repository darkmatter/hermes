# Vapi API — ops cheatsheet (Cooper)

Stack: **Vapi** → Twilio → ElevenLabs. Permanent assistant **Personal Concierge** (persona **Levi**).

## Auth

1Password item `vapi`:

| Field | Use |
|---|---|
| `credential` | **Private** key → `Authorization: Bearer <REDACTED> on `api.vapi.ai` |
| `username` | Public key only — REST with this → 401 “public vs private” |
| `vapi-assistant-id` | Standing assistant (do not PATCH per call) |
| `twilio-number` | Often masked in 1P — resolve via API |

```bash
export VAPI_KEY=<REDACTED>
curl -sS -H "Authorization: Bearer <REDACTED>" https://api.vapi.ai/phone-number
curl -sS -H "Authorization: Bearer <REDACTED>" "https://api.vapi.ai/assistant/$ASSISTANT_ID"
```

Standing IDs (re-verify if rotated):

- `phoneNumberId`: `68092f67-e7eb-4df9-8a39-e930eb99270d` (Twilio Primary)
- `assistantId`: `86a092df-2332-4092-bf2d-2cd02c66ac4a`

## Calls

```bash
curl -sS -X POST https://api.vapi.ai/call \
  -H "Authorization: Bearer <REDACTED>" -H "Content-Type: application/json" \
  -d @payload.json
# → id, status=queued, monitor.listenUrl, monitor.controlUrl

curl -sS -H "Authorization: Bearer <REDACTED>" 'https://api.vapi.ai/call?limit=20'
curl -sS -H "Authorization: Bearer <REDACTED>" "https://api.vapi.ai/call/$CALL_ID"
```

Create body essentials:

- `phoneNumberId`, `customer.number` (E.164)
- `assistantId` + `assistantOverrides` (system prompt, hold-proofing)
- Outbound overrides:
  - `firstMessageMode: "assistant-waits-for-user"`
  - `maxDurationSeconds: 7200`
  - `silenceTimeoutSeconds: 3600`

## Live control (`controlUrl`)

`POST` JSON to `monitor.controlUrl` from the create/get response.

```json
{"type":"say","message":"…","endCallAfterSpoken":false}
{"type":"add-message","message":{"role":"system","content":"…"},"triggerResponseEnabled":false}
{"type":"transfer","destination":{"type":"number","number":"+12065551212"}}
```

Observed end state after successful transfer: `endedReason=assistant-forwarded-call`, plus `destination` / `forwardedPhoneNumber`. **Vapi transcript stops at forward** — the bridged leg is outside Vapi.

**Do not** fire bare `transfer` the moment the user names a callback number if they meant “when a human agent answers.” Encode that condition in the system prompt up front; use control transfer for an **immediate** bridge or after a human greeting is heard.

## Analytics

`POST https://api.vapi.ai/analytics` (not GET). Required wrapper:

```json
{
  "queries": [
    {
      "table": "call",
      "name": "calls_by_end_reason",
      "groupBy": "endedReason",
      "timeRange": {
        "step": "day",
        "start": "2026-07-01T00:00:00Z",
        "end": "2026-07-29T23:59:59Z",
        "timezone": "America/Los_Angeles"
      },
      "operations": [
        {"operation": "count", "column": "id", "alias": "calls"},
        {"operation": "sum", "column": "duration", "alias": "sumDuration"},
        {"operation": "sum", "column": "cost", "alias": "sumCost"},
        {"operation": "avg", "column": "cost", "alias": "avgCost"}
      ]
    }
  ]
}
```

- **Tables:** `call`, `subscription`
- **groupBy:** `type` | `assistantId` | `endedReason` | `analysis.successEvaluation` | `status`
- **operations:** `sum` | `avg` | `count` | `min` | `max` | `history`
- **columns:** `id`, `cost`, `duration`, `costBreakdown.*`, concurrency/minutes fields
- Default time range if omitted: last **7 days** UTC
- HTTP **201** with result array = success
- Docs: https://docs.vapi.ai/api-reference/analytics/get

```bash
scripts/vapi_analytics.sh           # 7d
scripts/vapi_analytics.sh 30 UTC    # N days, tz
```

## Official CLI (optional)

```bash
curl -sSL https://vapi.ai/install.sh | bash   # or: npm i -g @vapi-ai/cli
vapi login   # or export VAPI_API_KEY=<private>
vapi call list | vapi call get <id>
vapi assistant list
vapi logs list
```

CLI helps CRUD/logs; **structured aggregates** still go through `POST /analytics`. Docs: https://docs.vapi.ai/cli

## Ended reasons we surface often

| Reason | Meaning |
|---|---|
| `assistant-forwarded-call` | Transfer/bridge executed; Vapi leg done |
| `customer-ended-call` | Far side hung up |
| `assistant-ended-call` | Bot hung up (wrap-up) |
| `silence-timed-out` | Silence cap hit — raise `silenceTimeoutSeconds` for holds |
| `max-duration-reached` | Hit `maxDurationSeconds` |

## Airline / third-party change calls

- Prefer airline that owns the PNR shown in the booking app (AA conf primary → AA desk even if BA metal).
- Spell record locators slowly / NATO; bots garble letter conf codes.
- If passenger ≠ Cooper: DOB + “assistant authorized by booking manager”; if refused, extract exact process + note on PNR.
- Payment: authorize fee class in prompt (“reasonable change fee + fare diff OK”) but never invent PAN/CVV; fall back to callback (310) 989-7067 / me@cooperm.com.
