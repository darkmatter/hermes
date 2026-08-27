# Warm transfer + mid-call HITL

## Transfer modes

| Mode | After connect | Levi resume if handoff misses? |
|---|---|---|
| Cold live-control `transfer` | AI exits (`assistant-forwarded-call`) | **No** |
| `warm-transfer-experimental` | Brief transfer assistant → merge or cancel | **Yes** on `transferCancel` |
| True conference reconnect-on-drop | Custom Twilio Conference | Build (not stock Vapi) |

## Skeleton (warm + fallback)

```json
{
  "type": "transferCall",
  "function": {
    "name": "warmTransferToHuman",
    "description": "ONLY after a live human agent greets. Never during IVR/hold.",
    "parameters": {
      "type": "object",
      "properties": {
        "destination": { "type": "string", "enum": ["+12069542027"] }
      },
      "required": ["destination"]
    }
  },
  "destinations": [{
    "type": "number",
    "number": "+12069542027",
    "transferPlan": {
      "mode": "warm-transfer-experimental",
      "transferAssistant": {
        "firstMessage": "Hi — I have [desk] on the line for [brief]. Can you take it?",
        "firstMessageMode": "assistant-speaks-first",
        "maxDurationSeconds": 75,
        "silenceTimeoutSeconds": 25,
        "model": {
          "provider": "openai",
          "model": "gpt-4o",
          "messages": [{
            "role": "system",
            "content": "Confirm live human. Yes → transferSuccessful. No/VM/busy → transferCancel. Under 30s."
          }],
          "tools": [
            { "type": "transferSuccessful", "function": { "name": "transferSuccessful", "description": "Connect" } },
            { "type": "transferCancel", "function": { "name": "transferCancel", "description": "Return to Levi" } }
          ]
        }
      }
    }
  }],
  "messages": [
    { "type": "request-start", "content": "One moment — connecting someone on our side." },
    { "type": "request-failed", "content": "They're not available. I'll continue.", "endCallAfterSpokenEnabled": false }
  ]
}
```

Prompt: attempt warm transfer **once** after human; if fails, finish task yourself.

## ask_cooper (blocking)

1. Tool hits HITL server `POST /vapi/tools`
2. Server Slack-posts Cooper DM `D0BG4HJ47GE` with question + id
3. Cooper replies in DM or `curl -X POST localhost:8788/reply -d '{"id":"...","answer":"..."}'`
4. Tool returns `Cooper replied: …` or `NO_REPLY_TIMEOUT` (~90s)
5. On timeout: no new spend authority; use pre-briefed guardrails only

Keep tool `server.url` pointed at a reachable tunnel (named preferred over trycloudflare).

## Live control (while in-progress)

```bash
curl -sS -X POST "$CONTROL_URL" -H 'Content-Type: application/json' \
  -d '{"type":"add-message","message":{"role":"system","content":"…"},"triggerResponseEnabled":true}'
# also: say | end-call | transfer
```

Stuck empty-transcript `in-progress` after `end-call`: Vapi DELETE/force-end; confirm zero live calls.
