---
name: messaging
description: "Terminal-based messaging — email via Himalaya CLI (IMAP/SMTP) and iMessage via BlueBubbles API or osascript fallback. Use when reading/sending email from terminal, or sending iMessages when the imsg CLI is unavailable."
version: 1.0.0
metadata:
  hermes:
    tags: [email, imessage, messaging, CLI, IMAP, SMTP, BlueBubbles]
---

# Terminal Messaging

Two messaging channels operated from the terminal:

1. **Email (Himalaya CLI)** — IMAP/SMTP email client for reading, listing,
   searching, composing, and managing emails. Separate from the Hermes Email
   gateway adapter.

2. **Email (gog CLI)** — alternative Gmail access via Google API. Use when
   Himalaya is not installed or OAuth-based Gmail access is needed. See the
   `gog` skill (ops) for full command reference, auth/keyring, triage labels,
   and batch operations. **Keyring unlock:** when gog's file backend is
   config-forced (`~/.config/gogcli/config.json` sets `keyring_backend:
   "file"`), load the password from himitsu before every gog command:
   `export GOG_KEYRING_PASSWORD="$(himitsu read gog/keyring-password 2>/dev/null)"`.
   Without this, `gog auth list` reports 0 accounts in non-interactive shells.

3. **iMessage (BlueBubbles / osascript)** — sending iMessages when the `imsg`
   CLI is unavailable. BlueBubbles API (preferred), osascript fallback.

---

## Mail Source Connectivity Check

Before attempting to read or send email, verify that at least one mail
source is connected. This is especially important for cron jobs and
automated tasks that should fail fast with a clear message rather than
attempt operations that will hang or error.

Check all three possible sources in order of preference:

```bash
# 1. Hermes Email gateway (configured via `hermes setup`)
hermes status 2>&1 | grep -A1 "Email"

# 2. Himalaya CLI (IMAP/SMTP)
which himalaya && ls ~/.config/himalaya/config.toml 2>/dev/null

# 3. gog CLI (Gmail API)
which gog && gog auth list
#   If this returns "No tokens stored" / {"accounts":[]} but the user has
#   authenticated before, do NOT declare "no source connected" — the tokens
#   may be in a different keyring backend (macOS Keychain vs file). See the
#   "Backend mismatch" section in the `gog` skill (ops) for the diagnostic
#   flow and fix before recommending re-auth.

If none are connected, report this to the user with setup instructions
(see Part 1 for Himalaya, the `gog` skill for gog OAuth). Do NOT silently
produce `[SILENT]` — that is for "no new mail in a connected inbox," not
"no inbox connected."

### gog auth state

`gog auth list` returns "No tokens stored" when OAuth hasn't been
completed, even if client credentials exist at
`~/Library/Application Support/gogcli/credentials.json`. The presence
of credentials ≠ authenticated. Always check `gog auth list` (or
`gog -a <email> auth doctor` for a specific account) to confirm tokens
are stored and valid.

---

## Part 1: Email via Himalaya CLI

Himalaya is a CLI email client that manages emails from the terminal using
IMAP, SMTP, Notmuch, or Sendmail backends.

### Prerequisites

1. Himalaya CLI installed (`himalaya --version` to verify)
2. Config at `~/.config/himalaya/config.toml`
3. IMAP/SMTP credentials configured

```bash
# Install
brew install himalaya  # macOS
# Or: curl -sSL https://raw.githubusercontent.com/pimalaya/himalaya/master/install.sh | PREFIX=~/.local sh
```

For full configuration (Gmail, iCloud, OAuth2, folder aliases) see
`references/himalaya-configuration.md`.

> **Critical folder alias pitfall:** Use `folder.aliases.X` (plural, dotted
> keys) in v1.2.0+. The old `[accounts.NAME.folder.alias]` (singular) form is
> silently ignored, causing save-to-Sent failures and duplicate emails on
> retry. See configuration reference for details.

### Hermes Integration Notes

- **Reading, listing, searching, moving, deleting** — work directly through the terminal tool
- **Composing/replying/forwarding** — piped input (`cat << EOF | himalaya template send`) is recommended for reliability
- Use `--output json` for structured output
- The `himalaya account configure` wizard requires interactive input — use PTY mode: `terminal(command="himalaya account configure", pty=true)`

### Common Operations

```bash
# List folders
himalaya folder list

# List emails in INBOX
himalaya envelope list

# Search
himalaya envelope list from john@example.com subject meeting

# Read email by ID
himalaya message read 42

# Write new email (non-interactive — use this from Hermes)
cat << 'EOF' | himalaya template send
From: you@example.com
To: recipient@example.com
Subject: Test Message

Hello from Himalaya!
EOF

# Reply
himalaya template reply 42 | sed 's/^$/\nYour reply text here\n/' | himalaya template send

# Move to folder
himalaya message move 42 "Archive"

# Delete
himalaya message delete 42

# Attachments
himalaya attachment download 42 --dir ~/Downloads
```

For rich emails with attachments, inline images, and multipart messages,
see `references/himalaya-message-composition.md` (MML syntax).

### gog CLI (Gmail API) — attachments, replies, multi-account

When using gog instead of himalaya, key capabilities beyond basic send:

- **Attachments:** `--attach /path/file1,/path/file2` (comma-separated)
- **Reply in thread:** `--thread-id <id> --reply-all --body "..."` or `--reply-to-message-id <id>`
- **Send-as alias:** `--from me@cm.xyz` (requires verified Gmail alias)
- **Reading long emails:** `--plain` truncates bodies at ~700 chars. Use `--json` + base64 decode for full body. See `gog` skill → `references/multi-account-search.md`.
- **Multi-account search:** When an email isn't in the primary account, search all authed accounts. See `gog` skill → `references/multi-account-search.md`.
- **Triage labels:** Cooper's Gmail state machine is `Triage/{Needs-Action,Done,Delegated,Waiting}` + `Muted/{Bulk,Unsubscribe}` (+ account helpers). Full map, apply/verify commands, and Daily Comms Triage expectations live in `gog` → `references/gmail-triage-labels.md`. Prefer those over Superhuman `AI/*`. Summarize-only is incomplete when labeling is in scope.

### Multiple Accounts

```bash
himalaya --account work envelope list
```

---

## Part 2: iMessage via BlueBubbles / osascript

When the `imsg` CLI is not installed, use BlueBubbles API (preferred) or
osascript (fallback) to send iMessages.

### Method 1 — BlueBubbles API (preferred)

BlueBubbles runs locally and exposes a REST API. The server persists its
config in a SQLite database; the API password lives there.

```bash
# 1. Verify BlueBubbles is running (default port 1234)
lsof -iTCP -sTCP:LISTEN -P -n | grep -i bluebubbles

# 2. Get the API password from the SQLite config DB
#    NOTE: path is "bluebubbles-server" (lowercase, hyphenated), NOT "BlueBubbles"
#    NOTE: the column is "name", NOT "key"
sqlite3 ~/Library/Application\ Support/bluebubbles-server/config.db \
  "SELECT value FROM config WHERE name='password'"

# 3. Check server health / Private API status
curl -s "http://127.0.0.1:1234/api/v1/server/info?password=<PASSWORD>" | python3 -m json.tool
#   Look for "helper_connected" and "private_api" — both should be true.
#   If false on macOS 26+, see "macOS Tahoe (26) Private API breakage" below.

# 4. List recent chats (POST with JSON body — GET returns 404)
curl -s -X POST "http://127.0.0.1:1234/api/v1/chat/query?password=<PASSWORD>" \
  -H "Content-Type: application/json" \
  -d '{"limit": 15, "sort": "lastmessage", "with": ["lastMessage"]}' -o /tmp/chats.json
#   Each chat object has: guid, displayName/chatIdentifier, style (43=group, 45=DM),
#   lastMessage.{text, handle.address, dateCreated (epoch ms)}

# 5. Send a message
curl -s "http://127.0.0.1:1234/api/v1/message/text?password=<PASSWORD>" \
  -X POST -H "Content-Type: application/json" \
  -d '{"chatGuid":"iMessage;-;+131****7076","text":"Hello!","ddwc":true,"subject":"","method":"private-api"}'
```

The port number may vary — check `lsof` output for the actual port.

> **API shape pitfall:** `chat/query` and `message/query` are **POST**
> endpoints that accept a JSON body. Sending GET requests returns 404 with a
> misleading "Chat does not exist!" error. This is the #1 gotcha when
> exploring the BlueBubbles API cold.

#### macOS Tahoe (26) Private API breakage

macOS 26 (Tahoe) broke BlueBubbles' Private API helper injection. The server
itself runs fine (messages are readable/sendable via fallback), but
`helper_connected` and `private_api` will be `false`. Without Private API you
lose: typing indicators, tapback reactions, reply threading, and reliable
sends (falls back to AppleScript, which is also flaky on Tahoe).

**Fix — two parts (both may be needed):**

1. **NVRAM boot-args** (disable AMFI so the dylib can inject):
   ```bash
   sudo nvram boot-args="amfi_get_out_of_my_way=1 amfi_allow_any_signature=1 -arm64e_preview_abi ipc_control_port_options=0"
   # Then reboot
   ```

2. **Patched dylib** — Tahoe's `_newChatItems` returns
   `IMMessageAcknowledgmentChatItem` objects; the stock helper calls `-index`
   on them and crashes. Community fix:
   - Release: `https://github.com/willsigmon/bluebubbles-helper/releases/tag/v0.0.22-tahoe`
   - Backup old dylib, swap in new one, reopen BlueBubbles:
   ```bash
   cp "/Applications/BlueBubbles.app/Contents/Resources/appResources/private-api/macos11/BlueBubblesHelper.dylib" \
      "/Applications/BlueBubbles.app/Contents/Resources/appResources/private-api/macos11/BlueBubblesHelper.dylib.bak"
   cp ~/Downloads/BlueBubblesHelper.dylib \
      "/Applications/BlueBubbles.app/Contents/Resources/appResources/private-api/macos11/BlueBubblesHelper.dylib"
   ```

If still failing after both steps, some users needed the full stack:
`csrutil disable` + ad-hoc code-sign the dylib
(`codesign -s - <path-to-dylib>`).

**Known remaining Tahoe regressions (as of mid-2026):**
- Inbound iMessages may be delayed (APNs drops) — BB server issue #779
- Reply-threaded Private API sends stall; plain sends work — #814
- AppleScript `sendMessage` fallback fails with error -1700 — #777

See `references/bluebubbles-tahoe-fix.md` for the full issue links and
reproduction details.

### Method 2 — osascript (fallback)

Use AppleScript to drive Messages.app directly. **Critical** — you must
reference the iMessage service by its `service type`, NOT by name.

```bash
osascript -e '
tell application "Messages"
    set theService to 1st service whose service type = iMessage
    set theBuddy to buddy "+155****1212" of theService
    send "message text" to theBuddy
end tell'
```

### Pitfalls

- **`Invalid key form (-10002)`** — Caused by referencing the service by string name instead of `service type`. Use `1st service whose service type = iMessage`.
- **BlueBubbles port mismatch** — The default port is 1234 but may differ. Always check `lsof` output first.
