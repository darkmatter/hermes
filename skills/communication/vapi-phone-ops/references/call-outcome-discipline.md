# Call outcome discipline (Levi / Vapi)

## Rule (Cooper)
- **Success** may be declared early when hard evidence already exists (digits/ticketed conf present in live transcript).
- **Failure must not** be declared until full call log is checked.

## Required check before any failure verdict
For **every** relevant call id (including ones you later deleted/killed):

```bash
curl -sS -H "Authorization: Bearer <REDACTED>" \
  "https://api.vapi.ai/call/<id>" | jq '{status,endedReason,messages:(.messages//[])|length, transcript:(.transcript//.summary//null)}'
```

Inspect `messages[]` / full transcript / analysis — not only:
- `watch_call.sh` summary
- bare `endedReason` (`silence-timed-out`, `customer-ended-call`, …)
- empty mid-call message count while still `in-progress`
- a later VM-only redial

## Kill / replace anti-pattern
If call A is live or just ended and call B (VM) is placed:
1. **GET full artifact for A before deleting A or declaring A a miss**
2. Digits spoken on A still count even if agent DELETE'd A thinking it was "interactive wrong path"
3. Example lesson: ticket candidate captured on interactive call while agent only trusted VM leave-behind

## Spoken ticket numbers
Treat spoken `001…` as **candidates** until aa.com / email confirms. STT mutates digits; wrong stigma example `0012342708964` failed clean AA credit lookup.

## Transport
POST `/call` via **curl** (Python urllib often Cloudflare 1010).
