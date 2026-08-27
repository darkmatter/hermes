# Warm-transfer + HITL (session notes)

## Warm-transfer-experimental

- Mode on destination `transferPlan.mode = "warm-transfer-experimental"`.
- Transfer assistant tools: `transferSuccessful` / `transferCancel`.
- Auto-cancel on VM/no-answer; parent call `request-failed` must **not** hang up AA (`endCallAfterSpokenEnabled: false`).
- Prompt Levi: try warm transfer **once** after human greets; then finish task yourself.
- Cold live-control `type:transfer` ends Levi immediately — no fallback.

## What cold forward cannot do

- Stay on after merge, re-dial a dropped leg, or inject after `assistant-forwarded-call`.
- True stay-on/rejoin needs Twilio Conference + leave webhook.

## ask_cooper

- Server: `communications/scripts/ask_cooper_server.py` (+ optional `text_cooper` iMessage).
- Slack channel: **D0BG4HJ47GE** (hermes_bot IM with Cooper). Openclaw DM IDs will fail `channel_not_found` for hermes_bot.
- Tool `server.url` points at public tunnel `…/vapi/tools`. Quick tunnels rotate — PATCH tool after restart.
- Reply: Slack thread/DM or `POST /reply` `{id,answer}`.

## DTMF / keypad

- Outbound tones = assistant **dtmf** tool (`keys` param).
- SIP INFO toggle = transport for SIP trunks only; Twilio PSTN leave off.
- `keypadInputPlan` = listen for human typing *to* Levi — off for outbound airline work.
