---
name: ai-phone-calls
description: >-
  Outbound AI voice calls via Vapi (Twilio transport + ElevenLabs voice) on Cooper's
  behalf — reservations changes, support holds, warm transfer to a human, live call
  control, and analytics. Use when placing/monitoring phone calls, transferring a
  live Vapi leg, querying call analytics, or installing/using the Vapi CLI.
version: 1.0.0
metadata:
  hermes:
    tags: [phone, vapi, twilio, elevenlabs, voice, analytics, transfer]
    category: communication
    related_skills: [communications, sag]
---

# AI phone calls (Vapi)

Class-level ops skill for **real phone calls**. Complements `communications` Mode C (email/iMessage/phone umbrella). Prefer this skill when the task is Vapi-heavy (live control, transfer, analytics, CLI).

**Not this skill:** `sag` / ElevenLabs TTS alone — those only make audio files.

## Standing infrastructure

- **1Password item `vapi`**
  - `credential` = **private** key for `Authorization: Bearer` on `api.vapi.ai`
  - `username` = public key only (REST with this → 401 public/private mixup)
  - `vapi-assistant-id`, `twilio-sid` / `twilio-token`
  - `twilio-number` often **masked** — resolve `phoneNumberId` via API
- **Permanent assistant:** "Personal Concierge" (persona **Levi**). Standing inbound prompt — **never PATCH for one-offs**; use `assistantOverrides`.
- Confirm each session:
  ```bash
  export VAPI_KEY=<REDACTED>
  curl -sS -H "Authorization: Bearer <REDACTED>" https://api.vapi.ai/phone-number
  ```

Known-good standing IDs (re-verify if auth/list drifts):

| Resource | Id / value |
|---|---|
| `phoneNumberId` | `68092f67-e7eb-4df9-8a39-e930eb99270d` (Twilio Primary +1310…3667) |
| `assistantId` | `86a092df-2332-4092-bf2d-2cd02c66ac4a` |

## Outbound workflow

1. Gather: E.164 callee, goal, facts (names, conf codes, DOB, dates, amounts, last-4), guardrails, **who speaks to the human agent** (Levi stays vs warm-transfer number), fee authority.
2. **Bake critical instructions into the initial system prompt** (preferred + fallback dates, transfer rule, payment limits). Do **not** depend on mid-call `add-message` for anything that must shape the first IVR turn — late updates often arrive after the bot already spoke the old plan.
3. Build payload from `templates/outbound_call.json` or `templates/flight_change_call.json`.
4. Hold-proof `assistantOverrides`:
   - `firstMessageMode: "assistant-waits-for-user"`
   - `maxDurationSeconds: 7200`
   - `silenceTimeoutSeconds: 3600`
5. `POST https://api.vapi.ai/call` → 201 + `status: queued`. Save `id`, `monitor.controlUrl`, `monitor.listenUrl`.
6. Monitor: `scripts/watch_call.sh <call_id> "$VAPI_KEY"` with `terminal(background=true, notify_on_complete=true)`.
7. Report outcome. If `endedReason=assistant-forwarded-call`, Vapi’s leg ended at bridge — **post-transfer audio is not in the Vapi transcript.**

## Live control (`monitor.controlUrl`)

While `in-progress`, `POST` JSON to `controlUrl` (capability URL; no separate Bearer <REDACTED> that host):

| type | Body sketch | Use |
|---|---|---|
| `say` | `{"type":"say","message":"…","endCallAfterSpoken":false}` | Speak now |
| `add-message` | `{"type":"add-message","message":{"role":"system","content":"…"},"triggerResponseEnabled":false}` | Inject context |
| `transfer` | `{"type":"transfer","destination":{"type":"number","number":"+1…"}}` | Immediate bridge |

### Transfer pitfalls

- Bare `transfer` is **immediate**. If still on IVR/hold, the transfer target gets IVR/hold — not “when a human picks up.”
- For “connect +1… when the airline agent answers,” put that rule in the **initial** system prompt (transfer only after a live human greets). Fire control `transfer` only when the user wants an **instant** bridge or you have already heard a human.
- Success shape: `endedReason: assistant-forwarded-call`, `destination` / `forwardedPhoneNumber` set. Tell the user to confirm the far handset actually has the airline.
- Use E.164 (`+12065551212`).

## Analytics

No Hermes core tool — call Vapi:

```bash
# aggregates
scripts/vapi_analytics.sh           # last 7d
scripts/vapi_analytics.sh 30        # last 30d

# or raw:
curl -sS -X POST https://api.vapi.ai/analytics \
  -H "Authorization: Bearer <REDACTED>" -H "Content-Type: application/json" \
  -d '{"queries":[{"table":"call","name":"totals","operations":[{"operation":"count","column":"id"},{"operation":"sum","column":"cost"}]}]}'
```

- Endpoint is **POST** `/analytics` (GET → 404). Body must be `{ "queries": [ ... ] }`.
- Tables: `call`, `subscription`
- `groupBy`: `type` | `assistantId` | `endedReason` | `analysis.successEvaluation` | `status`
- Ops: `count` | `sum` | `avg` | `min` | `max` | `history`
- Columns include `id`, `cost`, `duration`, `costBreakdown.*`
- Default window if omitted: last 7 days UTC
- Per-call detail: `GET /call`, `GET /call/{id}` (transcript, analysis, artifacts)
- Dashboard: https://dashboard.vapi.ai/
- Full query shapes: `references/vapi-api.md`

## Official Vapi CLI (optional)

Not required for calls/analytics (curl + private key is enough).

```bash
curl -sSL https://vapi.ai/install.sh | bash   # or: npm i -g @vapi-ai/cli
vapi login   # or export VAPI_API_KEY=<private key>
vapi call list | vapi call get <id>
vapi assistant list
vapi logs list
```

CLI is weak for structured aggregates — prefer `POST /analytics` / `scripts/vapi_analytics.sh`. Docs: https://docs.vapi.ai/cli

## Prompt structure (override system message)

1. Identity & authority (Levi; on behalf of whom; Cooper authorized)
2. **GOAL** (one sentence, caps)
3. Facts only actually known (conf codes, DOB, times)
4. Preferred date **and** fallback date (rank explicitly)
5. IVR + DTMF; spell conf codes clearly (NATO if needed — bots garble `WSZTVR`-style codes)
6. Hold: silent
7. Warm-transfer rule **if any** (human only, not IVR)
8. Negotiation / fee authority
9. DO NOT (SSN, full PAN, inventing ticket numbers); callback (310) 989-7067 / me@cooperm.com
10. WRAP-UP (new itinerary, conf, $ spelled case #)

## Airline date-change notes

- Call the carrier that owns the primary conf in the booking UI (AA conf primary → AA reservations even on BA metal).
- AA reservations public line commonly `+18004337300` (re-check if IVR changes).
- Third-party passenger: have DOB ready; if refused, extract process + note on PNR.
- Fee language: “reasonable change fee + fare diff OK” in prompt; still no card numbers unless explicitly provided for that call.

## Files

| Path | Role |
|---|---|
| `templates/outbound_call.json` | Generic outbound skeleton |
| `templates/flight_change_call.json` | Airline change + optional warm transfer |
| `scripts/watch_call.sh` | Poll call to completion |
| `scripts/vapi_analytics.sh` | Cost/count/end-reason analytics |
| `references/vapi-api.md` | Auth, control, analytics schema, ended reasons |

## Pitfalls checklist

- [ ] Private key (`credential`), not public (`username`)
- [ ] Critical prefs in **initial** prompt, not only live `add-message`
- [ ] Don’t blind-transfer during IVR when user meant “on human pickup”
- [ ] Don’t PATCH permanent assistant for one call
- [ ] After forward, don’t promise Vapi still has the live leg
- [ ] Analytics = POST body with `queries` array
