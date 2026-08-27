---
name: gog
description: Google workspace CLI (gog) for Gmail, Calendar, Drive, Chat, and more. Auth, email triage, and day-to-day Google operations.
version: 0.1.0
triggers:
  - gog
  - gmail
  - google mail
  - google calendar
  - google drive
  - email digest
  - email triage
---

# gog — Google Workspace CLI

## Overview

**gog** (v0.29.0, Nix profile) is a full-featured CLI for Google services: Gmail, Calendar, Drive, Chat, Contacts, Tasks, Sheets, Docs, YouTube, and more.

**Binary:** `gog` (Nix profile at `/etc/profiles/per-user/cm/bin/gog`)
**Account:** `cooper@darkmatter.io`
**OAuth client:** stored in himitsu as `google/oauth-client-secret-darkmatter-drive.json`
**Config:** `~/.config/gogcli/config.json`
**Credentials:** `~/.local/share/gogcli/credentials.json` + keyring

## Authentication

### Status check
```bash
gog status          # Shows account, client, keyring backend, credential paths
```

### Re-authorize (add scopes)
When you get `unauthorized_client` errors, the refresh token lacks the needed scope. Re-auth with:
```bash
gog login cooper@darkmatter.io --services=gmail,calendar,drive --gmail-scope=full --force-consent
```

### Headless / CLI-agent auth flow

When no interactive browser popup works (e.g. in a terminal agent session), use the two-step remote flow:

**Step 1 — print the auth URL:**
```bash
gog login cooper@darkmatter.io --services=gmail,calendar,drive --gmail-scope=full --force-consent --remote --step 1
```
This outputs a URL. The user opens it in their browser and authorizes.

**Step 2 — exchange the redirect code:**
After authorization, the browser redirects to a `127.0.0.1` URL that won't load. The user copies that full URL and provides it:
```bash
gog login cooper@darkmatter.io --services=gmail,calendar,drive --force-consent --remote --step 2 --auth-url "<redirect-url-from-browser>"
```

**Alternative: manual flow** (paste redirect URL inline):
```bash
gog login cooper@darkmatter.io --services=gmail --gmail-scope=full --force-consent --manual
```
This prints a URL and waits for you to paste the redirect URL back.

### Services and scopes

- `--services=gmail` — Gmail only
- `--services=gmail,calendar,drive` — Multiple services at once
- `--services=all-user` — All user OAuth services
- `--gmail-scope=full` — Read + modify + send
- `--gmail-scope=readonly` — Read only
- `--drive-scope=full|readonly|file` — Drive scope modes
- `--readonly` — Use read-only scopes for all services
- `--force-consent` — Required when re-authing to add new scopes

## Gmail

```bash
# List / search messages
gog gmail list "in:inbox newer_than:1d" -j --max 20       # Recent inbox (JSON)
gog gmail list "from:someone@example.com" -j --max 10      # From a sender
gog gmail list "subject:urgent is:unread" -j               # Unread with subject

# Read a message
gog gmail read <message-id> -j                              # Full message (JSON)
gog gmail read <message-id> -p                              # Plain text

# Send email
gog gmail send --to "user@example.com" --subject "Subject" --body "Body text"
gog gmail send --help                                       # All send options

# Labels
gog gmail labels list -j                                    # List all labels

# Threads
gog gmail thread <thread-id> -j                             # Read a thread

# Modify
gog gmail modify <message-id> --add-labels IMPORTANT --remove-labels INBOX
gog gmail trash <message-id>
```

### Safety flag
```bash
--gmail-no-send    # Block Gmail send operations (agent safety)
```

## Calendar

```bash
gog calendar list -j --max 10                              # Upcoming events
gog calendar today -j                                      # Today's events
gog calendar create --summary "Meeting" --start "2025-07-15T10:00:00" --end "2025-07-15T11:00:00"
```

## Drive

```bash
gog drive ls -j                                            # List files
gog drive search "query" -j                                # Search files
gog drive download <file-id>                               # Download a file
gog drive upload <local-path>                              # Upload a file
gog open <file-id>                                         # Open in browser
```

## Output formats

- `-j` / `--json` — JSON output (best for scripting)
- `-p` / `--plain` — TSV/plain text (parseable, no colors)
- `--results-only` — JSON mode: emit only primary result (drop envelope fields)
- `--select=field1,field2` — JSON mode: select specific fields

## Common patterns

### Email triage digest

For full triage query patterns and agent workflow, see `references/email-triage.md`.

```bash
# Today's unread inbox
gog gmail list "in:inbox is:unread newer_than:1d" -j --max 50

# Last 30 days unread primary inbox
gog gmail list "in:inbox is:unread category:primary newer_than:30d" -j --max 100

# Low-signal bulk (promotions + social, older than 7 days)
gog gmail list "(category:promotions OR category:social) older_than:7d" -j --max 100
```

When triaging, always use `--gmail-no-send` to prevent accidental sends:
```bash
gog --gmail-no-send gmail list "in:inbox newer_than:30d" -j --max 100
```

### Quick profile check
```bash
gog whoami -j       # Show authenticated user profile
```

## Pitfalls

- **Scope errors appear as `unauthorized_client`/`Unauthorized`** — the refresh token was granted for different scopes. Fix with `gog login ... --force-consent` and include all needed `--services`.
- **Browser auth may time out in agent sessions** — use `--remote --step 1` / `--step 2` flow instead.
- **`--force-consent` is required** when adding new scopes to an existing token; without it Google returns the old token with its original scopes.
- **`--gmail-no-send`** is a safety flag that blocks send operations — useful for read-only triage agents.
- **`gog gmail list` requires a query argument** — it's not `gog gmail list` but `gog gmail list "in:inbox"`.
- **`gog gmail labels`** is not a valid subcommand — use `gog gmail labels list` instead.
- **Gmail API must be enabled on the GCP project** — even after successful auth, Gmail commands fail with "Gmail API is not enabled for this OAuth project" if the API isn't activated. Fix: direct user to `https://console.cloud.google.com/apis/api/gmail.googleapis.com/overview?project=<PROJECT_ID>` to enable it. This is a prerequisite distinct from auth/scope errors. Same applies for other services (Calendar, Drive, etc.) — each API must be enabled separately in the GCP console.
- **`--manual` auth flow does NOT work in agent sessions** — it opens a PTY that blocks waiting for stdin input and cannot be satisfied programmatically. Always use `--remote --step 1` / `--step 2` instead. Never fall back to `--manual` in agent contexts.
- **Agent-session auth: present the URL once and wait** — when auth fails in a non-interactive session, run `--remote --step 1`, give the user the URL, and stop. Don't re-try or chain `--manual` as a fallback; each attempt generates a new state and confuses the flow. One clear ask, one response.
- **`--remote --step 2` can hang/timeout, and the auth code is single-use** — sometimes the step-2 exchange blocks (>20s) and does NOT persist the token. Symptoms: command times out, then `gog gmail list -a <email>` reports "No auth for gmail <email>". The redirect `code=` is consumed by the failed attempt, so you CANNOT just re-run step 2 with the same URL. Recovery: run `--remote --step 1` again to mint a fresh URL+state, have the user re-authorize, and exchange the new redirect. ALWAYS verify success with `gog auth list -p` (shows account, client, services, token timestamp) before declaring auth done — don't trust a silent/timed-out step 2.
- **Adding a second account reuses the same OAuth client** — `gog login <other@email> --services=gmail ...` works fine for multi-account; each account gets its own token bucket under the shared `default` client. The Gmail API enable step (below) is per-GCP-project, so once enabled it covers all accounts on that client.
- **Non-interactive sessions need `GOG_KEYRING_PASSWORD`** — when running `gog auth credentials` or any command that accesses the keyring in a non-TTY session (e.g. agent terminal), the keyring backend will fail with "no TTY available for keyring file backend password prompt". Export `GOG_KEYRING_PASSWORD` from himitsu (`gog/keyring-password`) before any gog command that touches credentials. See `references/fresh-auth-setup.md` for the full flow.

## Cross-references

- OAuth client secret lives in himitsu: `google/oauth-client-secret-darkmatter-drive.json`
- See `references/fresh-auth-setup.md` for full auth-from-clean-state (config creation, keyring password, remote OAuth)
- See the `himitsu` skill for reading/writing that secret
