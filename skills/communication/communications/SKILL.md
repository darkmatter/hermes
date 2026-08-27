---
name: communications
description: >
  Terminal and voice outreach for Cooper — email (Himalaya IMAP/SMTP + gog Gmail API),
  iMessage (BlueBubbles / osascript), and outbound AI phone calls (Vapi/Twilio/ElevenLabs).
  Use when reading/sending email, sending iMessages without imsg, calling a business/support
  line, waiting on hold, negotiating by phone, or checking mail-source connectivity for cron.
version: 2.4.0
metadata:
  hermes:
    tags: [email, imessage, phone, vapi, messaging, himalaya, bluebubbles, gog]
    category: communication
    related_skills: [gog, financial-operations, yuanbao, vapi-phone-ops, bluebubbles-studio]
---

# Communications (email · iMessage · phone)

Class-level skill for outbound/inbound human outreach channels operated from the agent.
Three modes share "reach a human"; pick the section that matches the task.

| Mode | Channel | When |
|---|---|---|
| **Email** | Himalaya (IMAP/SMTP) or `gog` (Gmail API) | Read/send/search mail; triage labeling lives in `gog` |
| **iMessage** | BlueBubbles API or osascript | Send iMessages when `imsg` CLI unavailable |
| **Phone** | Vapi → Twilio → ElevenLabs | Real voice calls, hold queues, IVR, refunds |

`sag` / ElevenLabs TTS only produces audio files — it does **not** place phone calls. Phone = Vapi.

Yuanbao group @mentions are a separate gateway skill (`yuanbao`); do not fold them here.

---

# Mode A — Email

## Mail source connectivity check

Before read/send (especially cron), verify at least one source:

```bash
# 1. Hermes Email gateway
hermes status 2>&1 | grep -A1 "Email"
# 2. Himalaya
which himalaya && ls ~/.config/himalaya/config.toml 2>/dev/null
# 3. gog (Gmail API)
which gog && gog auth list
# If empty accounts but user authenticated before → keyring backend mismatch.
# See `gog` skill "Backend mismatch" before recommending re-auth.
```

No source connected → report setup steps. Do NOT emit `[SILENT]` for "no inbox"; that means "no new mail on a connected inbox."

### gog auth state

Credentials file presence ≠ authenticated. Confirm with `gog auth list` or `gog -a <email> auth doctor`.

When file backend is config-forced, load keyring password before every gog command (construction avoids interactive prompts):

```bash
export GOG_KEYRING_PASSWORD=<REDACTED>
```

Deep auth/keyring/OAuth/triage labels/multi-account/batch unsubscribe → load **`gog`** skill.

### Inbox Zero with gog

For autonomous Gmail triage, use a durable Kanban card and process **one thread/card at a time**. Labels, archive, mark-read, and filters are `EXECUTE-SAFE` only after a per-action Gmail query verifies the state change. Never send/delete mail, click financial or fraud email links, alter account security, or approve OAuth permissions without the correct gate.

Do not use `--all` on a large inbox as the first step: it can exhaust Gmail per-user query quota or time out. Enumerate with bounded `--max 10` pages, preserve each returned `nextPageToken`, and resume slowly if `403 rateLimitExceeded` occurs. A `gog auth doctor` client-credentials config warning is not evidence that email access is broken; prove access with `gog auth list` plus a small Gmail search before re-authentication.

Detailed checklist and recovery: `references/gog-inbox-zero.md`.

## Himalaya CLI (IMAP/SMTP)

Separate from the Hermes Email gateway adapter.

**Prereqs:** `himalaya --version`, `~/.config/himalaya/config.toml`, IMAP/SMTP creds.

```bash
brew install himalaya  # macOS
```

Full config (Gmail/iCloud/OAuth2/folder aliases): `references/himalaya-configuration.md`.

> **Folder alias pitfall:** use `folder.aliases.X` (plural, dotted) in v1.2.0+. Old `[accounts.NAME.folder.alias]` is silently ignored → save-to-Sent failures / duplicate sends.

### Integration notes

- List/read/search/move/delete via `terminal`
- Compose via pipe: `cat << EOF | himalaya template send`
- `--output json` for structure
- `himalaya account configure` needs PTY: `terminal(..., pty=true)`

### Common ops

```bash
himalaya folder list
himalaya envelope list
himalaya envelope list from john@example.com subject meeting
himalaya message read 42
cat << 'EOF' | himalaya template send
From: you@example.com
To: recipient@example.com
Subject: Test Message

Hello from Himalaya!
EOF
himalaya template reply 42 | sed 's/^$/\nYour reply text here\n/' | himalaya template send
himalaya message move 42 "Archive"
himalaya message delete 42
himalaya attachment download 42 --dir ~/Downloads
himalaya --account work envelope list
```

Rich/multipart/MML: `references/himalaya-message-composition.md`.

## gog shortcuts (when using Gmail API)

- Attachments: `--attach /path/a,/path/b`
- Reply thread: `--thread-id <id> --reply-all --body "..."` or `--reply-to-message-id <id>`
- Send-as: `--from me@cm.xyz` (verified alias)
- Long bodies: `--plain` truncates ~700 chars → use `--json` + base64. See `gog` → `references/multi-account-search.md`
- Multi-account search + triage labels: `gog` → those references

### Auth warning vs. actual mailbox access

`gog -a <account> auth doctor` can warn that the OAuth client-credentials config file is missing and suggest `gog auth credentials <file>`, while stored account tokens remain healthy. Do **not** reconfigure OAuth just to clear that warning. Verify the functional path first:

```bash
gog auth list
gog -a <account> gmail search "newer_than:1d" --max 1 -j
```

If the account appears in `auth list` and the live Gmail search succeeds, Gmail access is usable. Only run `gog auth credentials <credentials.json>` when intentionally registering/replacing the OAuth client credentials.

### Bulk unsubscribe fallback

For marketing cleanup, prefer the message `List-Unsubscribe` header. Some providers emit a literal truncated HTTPS token (`...`) that cannot be followed; look for the header's `mailto:` alternative and send an unsubscribe email instead. With `gog`, use flags rather than RFC-style headers on stdin:

```bash
gog -a <account> gmail send \
  --to 'leave-...@leave.vendor.example' \
  --subject 'Unsubscribe' \
  --body 'Please unsubscribe me from all email lists.'
```

A `List-Unsubscribe-Post: List-Unsubscribe=One-Click` header can often be actioned with a direct HTTP request; preference-center URLs may need a browser confirmation or a provider-specific POST. Record successful vs. pending links rather than assuming a 200 response confirms unsubscribed status.

---

# Mode B — iMessage (BlueBubbles / osascript)

When `imsg` is missing.

## BlueBubbles API (preferred)

```bash
lsof -iTCP -sTCP:LISTEN -P -n | grep -i bluebubbles
# password column is "name", path is lowercase hyphenated:
sqlite3 ~/Library/Application\ Support/bluebubbles-server/config.db \
  "SELECT value FROM config WHERE name='password'"
curl -s "http://127.0.0.1:1234/api/v1/server/info?password=<PASSWORD>" | python3 -m json.tool
# chat/query and message/query are POST (GET → misleading 404)
curl -s -X POST "http://127.0.0.1:1234/api/v1/chat/query?password=<PASSWORD>" \
  -H "Content-Type: application/json" \
  -d '{"limit": 15, "sort": "lastmessage", "with": ["lastMessage"]}' -o /tmp/chats.json
curl -s "http://127.0.0.1:1234/api/v1/message/text?password=<PASSWORD>" \
  -X POST -H "Content-Type: application/json" \
  -d '{"chatGuid":"iMessage;-;+1XXXXXXXXXX","text":"Hello!","ddwc":true,"subject":"","method":"private-api"}'
```

Port may differ — always check `lsof`.

### macOS Tahoe (26) Private API breakage

`helper_connected` / `private_api` false → lose typing indicators, tapbacks, reliable private-api sends.

1. NVRAM boot-args (AMFI) then reboot:
   ```bash
   sudo nvram boot-args="amfi_get_out_of_my_way=1 amfi_allow_any_signature=1 -arm64e_preview_abi ipc_control_port_options=0"
   ```
2. Patched dylib for `_newChatItems` crash:
   - Release: `https://github.com/willsigmon/bluebubbles-helper/releases/tag/v0.0.22-tahoe`
   - Backup + replace `BlueBubblesHelper.dylib` under app Resources `private-api/macos11/`.

May also need `csrutil disable` + ad-hoc `codesign -s - <dylib>`. Remaining regressions: APNs delay #779, reply-thread stall #814, AppleScript -1700 #777. Detail: `references/bluebubbles-tahoe-fix.md`.

## osascript fallback

Reference service by **service type**, not name:

```bash
osascript -e '
tell application "Messages"
    set theService to 1st service whose service type = iMessage
    set theBuddy to buddy "+1555121212" of theService
    send "message text" to theBuddy
end tell'
```

Pitfalls: `Invalid key form (-10002)` = wrong service reference; port mismatch.

---

# Mode C — AI phone calls (Vapi)

Stack: **Vapi** → **Twilio** → **ElevenLabs**. Standing assistant **Personal Concierge** (persona **Levi Okada**).

**Deep phone ops live in umbrella skill `vapi-phone-ops`** (outbound SOP, warm-transfer-experimental, DTMF/IVR, HITL ask_cooper, payment-on-call, hangup/runaway, analytics, call-outcome discipline). This Mode C is the multi-channel map entry + shared scripts/templates only.

## Standing infrastructure (quick)

- 1Password item **`vapi`**: `credential` = private Bearer <REDACTED> (not `username`/public)
- `phoneNumberId` / `assistantId`: resolve via API; known standing IDs in `vapi-phone-ops`
- Never PATCH permanent assistant for one-offs — `assistantOverrides` only
- Status to humans: **BlueBubbles Studio** (`bluebubbles-studio`), not Twilio SMS (**30034**)

## Shared scripts / templates (this package)

```bash
PKG=~/.hermes/skills/communication/communications
source $PKG/scripts/vapi_env.sh
$PKG/scripts/watch_call.sh <call_id>
$PKG/scripts/vapi_analytics.sh summary|ends|cost|calls|get
# templates: vapi_call*.json, vapi_warm_transfer_tool.json
# HITL: scripts/ask_cooper_server.py, start_ask_cooper_hitl.sh, bb_webhook_server.py
```

Hold-proof defaults, warm-transfer phases, ask_cooper loop, billing gates, kill sequence → **`vapi-phone-ops`**.

---

# Related

- **`gog`** — full Gmail API ops, auth, triage labels (canonical for gog)
- **`financial-operations`** — banks, cards, website payment repair (Studio CUA)
- **`vapi-phone-ops`** — Vapi phone umbrella (all call depth)
- **`bluebubbles-studio`** — Studio-only iMessage identity + hooks
- **`yuanbao`** — 元宝 group gateway @mentions (leave separate)
- **`operator-status`** — feed digests that consume mail triage outputs
- Archived predecessors: `messaging`, thin `vapi-phone*` / `ai-phone-calls` stubs (bodies under `vapi-phone-ops/references/absorbed-*`)
