---
name: ai-phone-calls
description: "Make outbound AI voice phone calls on Cooper's behalf via Vapi (Twilio transport + ElevenLabs voice). Use when the user asks to 'call' a business/support line, 'wait on hold', negotiate a refund, gather info by phone, or handle any task requiring a real phone conversation. Covers credentials, one-time assistant overrides, hold-proofing, IVR navigation, and call monitoring."
tags:
  - phone
  - vapi
  - twilio
  - elevenlabs
  - voice
---

# AI Phone Calls (Vapi)

Make outbound AI voice calls on Cooper's behalf. The stack is **Vapi** (call orchestration + LLM brain) → **Twilio** (telephony) → **ElevenLabs** (voice). All three are already wired together in Cooper's Vapi org.

**Important distinction:** the `sag` CLI / ElevenLabs TTS only produces audio files — it CANNOT make phone calls. Phone calls go through Vapi.

## Standing infrastructure

- **1Password item `vapi`** (fetch with `op item get "vapi" --format=json > /tmp/vapi_item.json` then parse):
  - `username` = Vapi **public** key
  - `credential` = Vapi **PRIVATE** key — this is the one for `api.vapi.ai` server API calls
  - `twilio-sid` / `twilio-token` = Twilio account credentials
  - `vapi-assistant-id` = permanent assistant ID
  - `twilio-number` = **stored masked** (`+131****3667`) — 1Password won't reveal it; get the real `phoneNumberId` from `GET https://api.vapi.ai/phone-number` instead
- **Permanent assistant:** "Personal Concierge" (persona name **Levi**), ElevenLabs voice, Claude Haiku model, Deepgram transcriber. It has a standing system prompt for inbound calls — do not overwrite it.

### Pitfall: 401 "Invalid Key. Hot tip…"

If the API returns `401 Invalid Key. Hot tip, you may be using the private key instead of the public key, or vice versa` — you used the `username` field. Server-side REST calls require the `credential` (private key) as `Authorization: Bearer <REDACTED>

## Workflow

1. **Gather from the user** (ask if missing): callee phone number, the goal, all facts the agent will need (names, booking/account refs, dates, amounts, card last-4), and explicit guardrails (what NOT to share/commit to).
2. **Verify infra** — `GET /phone-number` with the private key: confirms auth works and returns the `phoneNumberId` and `assistantId`.
3. **Build the call payload** — see `templates/vapi_call.json`. Key principle: use **`assistantOverrides`** to inject a call-specific system prompt. This is a one-time override; the permanent assistant config is untouched. Never PATCH the assistant itself for a single call.
4. **Fire the call** — `POST https://api.vapi.ai/call` with the payload. HTTP 201 + `"status":"queued"` = success. Response includes `id`, plus `monitor.listenUrl` (live audio websocket) and `monitor.controlUrl`.
5. **Monitor in background** — run `scripts/watch_call.sh <call_id> <private_key>` via `terminal(background=true, notify_on_complete=true)`. It polls every 30s until `status=ended`, then prints ended reason, cost, summary, and transcript.
6. **Report back** — after the call ends, relay outcome, case/reference numbers, and next steps to the user.

## Hold-proofing & outbound settings

For support lines with hold queues, set in `assistantOverrides`:

- `"firstMessageMode": "assistant-waits-for-user"` — outbound calls should let the callee (IVR or human) speak first; the default first message ("Hello, this is Cooper's assistant") is designed for inbound.
- `"maxDurationSeconds": 7200` — default call cap is much shorter; long holds need 1–2h.
- `"silenceTimeoutSeconds": 3600` — hold music gaps/silence must not end the call.

## System prompt structure for the call

Include these sections (see the worked example in `templates/vapi_call.json`):

1. **Identity & authority** — who the agent is (Levi), who it calls on behalf of, who authorized it.
2. **GOAL** — one sentence, in caps.
3. **Facts block** — booking refs, names, dates, routes, card last-4. Only give facts you actually have.
4. **What happened** — numbered factual narrative for disputes/refunds.
5. **IVR handling** — tell it to listen to menus and use DTMF keypad; "existing reservations" or 0-for-agent as fallback.
6. **Hold handling** — wait SILENTLY through hold music, do NOT hang up, greet when a human joins.
7. **Negotiation rules** — e.g. decline vouchers, insist on refund to original payment method, cite DOT rules for airline denied-boarding; if told "only the passenger can request," extract the exact process + get it noted on the account anyway.
8. **DO NOT list** — no SSN, no full card numbers, no payment credentials, no commitments/purchases; unknown facts → "I don't have that in front of me," offer the reference number instead; give Cooper's callback (310) 989-7067 / me@cooperm.com.
9. **WRAP-UP** — always capture case/reference number (ask agent to spell it), amount, timeline; summarize back; hang up after goodbye without re-engaging.

## Third-party consent caveat

If the call concerns someone else's booking/account (e.g. a passenger who isn't Cooper), the business may insist on speaking to that person. Prompt the agent to extract the exact required process (form URL, direct line) and get the request documented on the account regardless — the call still produces a concrete next step.

## Reference files

- `templates/vapi_call.json` — known-good outbound call payload (French Bee refund call, July 2026): copy and modify.
- `scripts/watch_call.sh` — poll a call until it ends and print summary + transcript. Usage: `watch_call.sh <call_id> <private_key>`.
