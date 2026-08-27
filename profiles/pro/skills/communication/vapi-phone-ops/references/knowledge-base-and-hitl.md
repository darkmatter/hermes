# Knowledge base + HITL (session-hardened)

## Knowledge base (`query-cooper-records`)

Local copies (re-upload when facts change): `~/.hermes/vapi/kb/`

| File | Purpose |
|---|---|
| `cooper-contacts-addresses.md` | phones, emails, home Apt 715 billing, condo 1810 AT&T |
| `cooper-payment-methods.md` | Amex Platinum primary + Coinbase One backup (full fields) |
| `levi-tools-and-ops.md` | tool when/don't + IVR habits |
| `manifest.json` | file IDs + query tool id |

Upload MIME must be explicit `type=text/markdown` — bare `.md` becomes `application/octet-stream` → 400.

Standing system prompt MUST name the tool, e.g. call `query-cooper-records` before inventing address/email/card/ZIP. Standing TOOLS section explains what/when/dont — never name-only lists.

Default billing home: **1111 S Grand Ave Apt 715, LA 90015**. Condo AT&T only: **1155 S Grand Unit 1810**.

Payment: Platinum first; Coinbase backup only after 2 hard platinum declines or explicit brief; stop after 2 declines; cardholder name may be Koutarou Maruyama → call Cooper (310) 989-7067.

## HITL (`ask_cooper`)

| Piece | Value |
|---|---|
| Public tools URL | `https://ask-cooper.cm.xyz/vapi/tools` |
| Local | `:8788` LaunchAgent `dev.hermes.ask-cooper` |
| Slack | hermes_bot DM `D0BG4HJ47GE` |
| iMessage from | **Studio only** `cooperton42391@gmail.com` via `bb-api.cm.xyz` |
| iMessage to | Cooper `+13109897067` (never loop via Pro `koutaroum@icloud.com`) |
| Reply | iMessage thread (BB inbox poll) · Slack · `POST /reply` |

`extract_tool_calls` must read `toolCallList` / `toolCalls` from **both** `message` and top-level body.

Quick tunnels rot — prefer named CF hostnames (`ask-cooper.cm.xyz`, `bb-hook.cm.xyz`, `bb-api.cm.xyz`).

If Studio `helper_connected: false`, private-api fails; apple-script may hang. Fail loud; do not fall back to Pro Messages.

## Airline anti-thrash

- Cap **2 failed dial-out outcomes** then stop for review.
- AA **callback queued** is NOT a free greenlight to redial — wait on callback #.
- Phonetic conf codes; after ~3 IVR fails → DTMF 0/rep.
- Twilio SMS from Vapi long code → often **30034**; use BB/iMessage or Slack.

## 1Password non-interactive

```bash
himitsu exec op-service-account/token -- bash -lc \
  'OP_SERVICE_ACCOUNT_TOKEN=$TOKEN op item get <id> --vault <vault> --format json'
```

Service accounts require `--vault`. Never bare biometric `op` in automation.
