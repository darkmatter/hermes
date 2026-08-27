# iMessage identity + HITL receive

## Hard identity rule

| | |
|---|---|
| **Send as** | Mac Studio BlueBubbles **cooperton42391@gmail.com** · `https://bb-api.cm.xyz` |
| **Never send as** | Mac Pro Messages **koutaroum@icloud.com** (self-chat / loops) |
| Guard | `server/info` → `detected_imessage` / `detected_icloud` must contain `cooperton42391@gmail.com` or **refuse send** |

User correction: HITL that mails from the Pro iMessage account “messages itself.” Fail closed.

## Send ladder

1. REST `POST /api/v1/message/text` on `bb-api.cm.xyz`
2. Body: `chatGuid`, **`message`**, **`tempGuid`**, `method` ∈ `private-api` | `apple-script` (no invalid `auto`)
3. Prefer private-api when `helper_connected: true`; else apple-script (may hang)
4. **No** Pro `osascript` / local Messages fallback — even on timeout

If helper disconnected: fix Private API on Studio; use Slack HITL until Studio can send.

## Inbound for HITL answers

- Studio BB webhook → `https://bb-hook.cm.xyz/bb/webhook?secret=…`
- Inbox: Pro `bb_webhook_server.py` `:8790` · `GET /messages?secret=`
- HITL polls inbox; allowlist `+13109897067` (+ optional `+12069542027`)
- One open ask: plain text reply OK; multiple open: include `[req_id]`

## Durable DNS

- `bb-api.cm.xyz` → Studio named tunnel
- `bb-hook.cm.xyz` → Pro hook `:8790`
- `ask-cooper.cm.xyz` → Pro HITL `:8788` (same Pro CF tunnel second hostname)

## Darwin flake host attrs

Rebuild targets are **hostnames** (`Coopers-Mac-Studio`, `Coopers-Mac-Pro`), not hostIds. Set `~/.config/darwin/host` accordingly. Quote `${cloudflaredBin}` in launchd ProgramArguments.
