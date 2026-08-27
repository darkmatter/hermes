# Live call control + warm transfer

## When you have a live call

From `POST /call` or `GET /call/{id}`:

- `status`: `queued` → `ringing` → `in-progress` → `ended`
- `monitor.controlUrl` — HTTP control plane for this call only
- `monitor.listenUrl` — websocket listen (optional)

Control requests: `POST controlUrl` with JSON body. No Vapi Bearer <REDACTED> required on the control host (it is call-scoped).

## Control message types (proved)

### Speak immediately

```json
{
  "type": "say",
  "message": "Brief spoken correction...",
  "endCallAfterSpoken": false
}
```

Use sparingly on hold — interrupts hold music / IVR audio path from the assistant side.

### Silent policy inject (preferred mid-call)

```json
{
  "type": "add-message",
  "message": {
    "role": "system",
    "content": "PRIORITY UPDATE: prefer date X; when LIVE human answers, transfer to +1..."
  },
  "triggerResponseEnabled": false
}
```

Returns `{"status":"ok"}`. Does not force an immediate spoken turn when `triggerResponseEnabled` is false.

### Forward / warm transfer

```json
{
  "type": "transfer",
  "destination": {
    "type": "number",
    "number": "+12065550100"
  }
}
```

Effects:
- Vapi call **ends** almost immediately
- `endedReason`: **`assistant-forwarded-call`**
- Response/call object gains `forwardedPhoneNumber` and `destination`
- **No further Vapi transcript** of the bridged third-party ↔ airline leg
- Cost stops accruing on Vapi for the bridged portion (Twilio may still bill transfer-side separately depending on config)

Other experimented shapes (`{"type":"transfer","phoneNumber":"+1..."}`, `hand-off`) either duplicate or 400 once the call is already inactive after the first successful transfer.

## Operational pattern: transfer-to-user when agent picks up

**Do this in the initial assistantOverrides system prompt**, not only mid-call:

```
When a LIVE human American Airlines (or callee) agent answers — not IVR, not hold music —
briefly introduce yourself and the passenger/booking, then immediately warm-transfer /
connect the call to +1XXXXXXXXXX so that person can speak with the agent. Do not wait for
Cooper. Stay silent on hold until then.
```

Also set date preference order and fee authority in that same initial prompt:

```
Preferred new date: Sunday Aug 2, 2026 if available; else Aug 1. Accept reasonable change
fee + fare difference. If full card needed and not on hand: callback Cooper (310) 989-7067 /
me@cooperm.com; do not invent PAN/CVV.
```

### Why bake it in

Mid-call transfer while still in IVR was accepted by the control API and forwarded successfully — but the **human destination landed in the airline queue**, not on a live agent. Report that honestly. The AI may only have gotten through the “change flight” IVR intent utterance before forward.

### After transfer — handoff brief in chat

Always restate for the person at the transfer number:

- Airline + queue status (IVR vs human)
- Passenger full name + DOB
- PNR(s) cleanly (AA + operating carrier if any)
- Flight number / route / original datetime
- Desired new date order + fee authority
- Callback contacts if payment needed

Assume they heard a mangled or partial AI intro.

## IVR / first-message pitfall

Without `"firstMessageMode": "assistant-waits-for-user"`, Levi greets over the airline recording (“Hello this is Cooper’s assistant”) and burns the first turn. Always set for outbound support lines.

## Airline-specific crumbs (AA)

- Public reservations line used successfully: `+1-800-433-7300`
- Codeshare example: AA conf + BA op record both useful; start with AA conf on AA’s line
- When shooting DTMF/pathing, prefer “change flight” / existing reservation language the IVR offers explicitly

## Watch + report

```bash
scripts/watch_call.sh <call_id>   # ends with reason, cost, summary, transcript[:8000]
# or analytics get:
scripts/vapi_analytics.sh get <call_id>
```

For forwarded calls, summary often only covers pre-transfer IVR dialogue; `successEvaluation` may be `false` even when the handoff itself succeeded — judge success by `endedReason` + whether the third party actually connected.
