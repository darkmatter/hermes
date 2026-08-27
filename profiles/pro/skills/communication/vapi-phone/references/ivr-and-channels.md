# IVR, DTMF, channels, HITL — hard-won notes

## AA IVR (Jul 2026 session)

What failed:

- Free speech only on 6-letter conf → bot invented neighbors (`w s v t v r`, `w f z t v r`) then: "call back once you have the record locator."
- Over-engineered PHASE-heavy prompts without fixing the acoustic input path.
- Warm transfer never reached — stuck in IVR.

What helped next attempts:

1. Short opener: "change flight"
2. Phonetic conf once asked (whiskey/sierra/zulu/tango/victor/romeo), pauses between letters
3. dtmf tool for press-1/2 yes-no and 0-for-rep
4. Light prompt (Cooper: no overboard imperative conditionals)
5. Escape hatch: ask representative; try BA operating-carrier conf if AA tree keeps dying

Sample failed conf spoken forms: bare `WSZ TVR`, rushed letter groups without NATO.

## Tool packing gotchas

```
400 more than one tool of type 'dtmf'
```

Cause: dashboard `toolIds` includes dtmf **and** inline `tools:[{type:dtmf}]`. Use one path.

```
Invalid Configuration ... groupBy must be an array
```

Analytics `groupBy` is array-only.

Assistant PATCH with only `{model:{toolIds:[...]}}` can fail provider enum — send full model block (`provider`, `model`, `messages`, `toolIds`).

dtmf dashboard tool created with **empty parameters** — PATCH:

```json
{
  "function": {
    "name": "dtmf",
    "description": "Send DTMF keypad tones…",
    "parameters": {
      "type": "object",
      "properties": {
        "keys": {"type": "string", "description": "Digits e.g. \"1\", \"0\", \"123#\""}
      },
      "required": ["keys"]
    }
  },
  "messages": []
}
```

`sipInfoDtmfEnabled`: leave false on Twilio PSTN. Only some BYO SIP trunks want SIP INFO.

`keypadInputPlan.enabled: true` = **inbound human types digits to Levi**. Turn off for outbound IVR work. Unrelated to dial-out dtmf tool.

## Status ping channel matrix

| Channel | Result in session | Note |
|---|---|---|
| Twilio SMS from Vapi long code | **undelivered 30034** | A2P 10DLC / unregistered |
| BlueBubbles private-api | 500 helper off | Tahoe often `private_api: false` |
| BlueBubbles apple-script API | needs `message` + `tempGuid` | easy 400 without tempGuid |
| osascript Messages | rc 0 | Prefer for critical handoff pings |

## HITL ask_cooper

- Local server `:8788` + cloudflared quick tunnel (ephemeral hostname).
- Tool must stay **sync** so Vapi waits; server timeout ≤ tool `timeoutSeconds` (120).
- Slack post target: open IM via Hermes bot auth; Cooper user `U092MDGBK0R` → channel **`D0BG4HJ47GE`**. Memory openclaw DM id failed (`channel_not_found` / wrong app).
- Reply paths: MS-poll non-bot messages in that IM, or `POST /reply`.
- On Slack failure, tool should still return a safe fallback string so the call continues under guardrails.

Restart recipe:

```bash
$SCRIPTS/start_ask_cooper_hitl.sh
cloudflared tunnel --url http://127.0.0.1:8788
# PATCH ask_cooper tool server.url to new host/vapi/tools
```

## Transfer / control quick map

- Mid-call only and status=`in-progress`: `controlUrl` say / add-message / cold transfer.
- After cold transfer: call ended for Vapi; no further control.
- Want "try human then keep Levi": warm-transfer-experimental only.
- Want "reconnect if phone drops mid human-human": not Vapi stock — Twilio Conference + webhooks.

## Analytics helper

`$SCRIPTS/vapi_analytics.sh` — summary / ends / cost / calls / get. Default timezone America/Los_Angeles.
