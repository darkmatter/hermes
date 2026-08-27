# gog Email Operations

Common `gog gmail` command patterns for email triage, reading, and batch operations.

## List Unread Emails

```bash
# Query is a POSITIONAL arg (gog ≥0.27). Do NOT pass --query — unknown flag.
# Cap results with --max (not --limit).
gog -a cooper@darkmatter.io gmail list "is:unread in:inbox" --max 50 --json

# Extract compact TSV from JSON output
gog -a cooper@darkmatter.io gmail list "is:unread in:inbox" --max 50 --json | \
  jq -r '.threads[] | "\(.id)\t\(.date)\t\(.from)\t\(.subject)"'
```

Thread objects contain: `id`, `date`, `from`, `subject`, `labels`, `messageCount`.

`gmail search` / `find` / `ls` are aliases of `list`. Always pin `-a <account>`.

## Read a Thread

```bash
# Fast skim (human-readable). Prefer for short MFA / OTP messages.
gog -a cooper@darkmatter.io gmail read <threadId> --plain

# Full thread with bodies + optional attachment download (preferred for compliance)
gog -a cooper@darkmatter.io gmail thread get <threadId> --full --download --out-dir /tmp/mail --json

# Lossless single-message dump
gog -a cooper@darkmatter.io gmail raw <messageId> --json

# List / download one attachment
gog -a cooper@darkmatter.io gmail thread attachments <threadId> --json
gog -a cooper@darkmatter.io gmail attachment <messageId> <attachmentId> --out /tmp/file.pdf
```

**Pitfall: `gmail read --plain` truncates long bodies** (~700 chars). Forwarded
CFTC/Coinbase notices and Form 40 mail will cut off mid-forward. Use
`thread get --full` (or `raw` + base64 decode) for anything compliance-shaped.
See `references/multi-account-search.md` for decode snippets and
`references/email-triage-compliance.md` for Form 40 code hunting.

## Batch Archive / Label / Mark-read

```bash
# Labels: --add / --remove take comma-separated names (gog 0.27 thread modify)
gog -a <acct> gmail thread modify <threadId> \
  --add "Triage/Done" \
  --remove "Triage/Needs-Action,INBOX,UNREAD" \
  -y --no-input

# Archive by thread (not bare message IDs alone when you mean the whole thread)
gog -a <acct> gmail archive --thread <id1> <id2> ... -y --no-input

# Mark read
gog -a <acct> gmail mark-read <messageOrThreadId...> -y --no-input
```

**Pitfall: repeated bare `--remove FLAG` without commas can leave `INBOX` /
`Triage/Needs-Action` stuck.** Prefer one `--remove "A,B,C"` then explicit
`archive --thread` + `mark-read`, then verify with a list query.

## Send Email

```bash
gog -a cooper@darkmatter.io gmail send \
  --to "recipient@example.com" \
  --cc "cc@example.com" \
  --subject "Subject line" \
  --body "Email body text"
```

### Send with attachments

```bash
gog -a <email> gmail send \
  --to "recipient@example.com" \
  --subject "Subject line" \
  --body "Email body text" \
  --attach /path/to/file1.png,/path/to/file2.svg
```

`--attach` accepts a comma-separated list of file paths (repeatable flag).

### Reply within a thread

To reply to an existing Gmail thread (sets In-Reply-To/References headers):

```bash
# Reply to a specific message ID
gog -a <email> gmail send \
  --to "recipient@example.com" \
  --subject "Re: Original subject" \
  --body "Reply body" \
  --reply-to-message-id <gmailMessageId>

# Reply within a thread (uses latest message for headers)
gog -a <email> gmail send \
  --thread-id <threadId> \
  --reply-all \
  --body "Reply body"

# --reply-all auto-populates recipients from the original message
# --quote includes the quoted original message in the reply
```

### Send from a specific alias

```bash
gog -a <email> gmail send \
  --from "me@cm.xyz" \
  --to "recipient@example.com" \
  --subject "Subject" \
  --body "Body"
# --from requires a verified send-as alias in Gmail settings
```

## Pre-flight Check (before any triage or cron email scan)

Before attempting to list or read emails, verify a mail source is actually
connected. This avoids confusing auth-error output and lets you report the
setup path cleanly when nothing is configured.

```bash
# 1. Check if gog is installed and has at least one authenticated account
gog auth list --json
#   Returns {"accounts": []} when no accounts are configured — stop here
#   and report setup instructions (see gog-cli-troubleshooting SKILL.md:
#   "Re-authenticating gog via two-step remote flow" for the preferred
#   agent-driven method, or "Re-authenticating gog via live Chrome CDP"
#   for the CDP fallback).

# 2. If accounts exist, verify the target account's tokens are healthy
gog -a <email> auth doctor
#   status: ok  → proceed to triage
#   status: error → see "Keyring and Authentication Issues" in SKILL.md

# 3. (Fallback) If gog is not installed, check for himalaya
which himalaya && himalaya envelope list  # returns folders if configured
```

When no mail source is connected, report how to set one up (gog auth add
for Gmail, or brew install himalaya for generic IMAP/SMTP) and stop — do
not attempt triage against an unconfigured source.

## Email Triage Workflow

Label taxonomy (source of truth): `references/gmail-triage-labels.md`.
**Summarize-only is incomplete** — apply Gmail labels as part of triage when labeling is in scope.

0. **Pre-flight** — confirm gog auth + Gmail list works for **each** required account (`cooper@darkmatter.io`, `me@cm.xyz`). Empty inbox ≠ auth failure. See also `references/multi-account-cron-verification.md`.
1. **List** unread/recent inbox mail **per account**:
   ```bash
   gog -a cooper@darkmatter.io gmail list "in:inbox newer_than:1d" --max 50 --json
   gog -a me@cm.xyz gmail list "in:inbox newer_than:1d" --max 50 --json
   ```
2. **Categorize** by scanning sender + subject + existing labels:
   - **Action required** → `Triage/Needs-Action` (payroll, tax, compliance, security, Brex/financial, Apple cert expiry). On `me@cm.xyz`, security also gets `Security Alert`.
   - **Waiting on external reply** → `Triage/Waiting`
   - **Delegated** → `Triage/Delegated`
   - **Informational handled** → `Triage/Done` (archive after labeling when appropriate)
   - **Noise/Marketing** → `Muted/Bulk` then archive
3. **Read** action-required emails with `gog gmail read <id> --plain` for body details (use `thread get --full` for long/compliance mail)
4. **Label** (EXECUTE-SAFE) using the taxonomy above, then archive pure noise:
   ```bash
   gog -a <account> gmail thread modify <id> --add "Triage/Needs-Action" -y --no-input
   gog -a <account> gmail thread modify <id> --add "Muted/Bulk" --remove INBOX -y --no-input
   ```
5. **Verify** with read-back queries (`label:"Triage/Needs-Action" …`, `in:inbox <selector>` count 0 after archive). Paste counts as evidence — never close on the agent’s assertion alone.
6. **Summarize** remaining action items (sender, subject, deadline, key details). Do **not** stop at a digest if labeling was in scope.

### Gating

- Label / archive / mark-read: EXECUTE-SAFE with verifying query (`~/.hermes/email-triage-dod-framework.md`).
- Send / delete / money / credential rotation: EXECUTE-GATED or HANDOFF.
- Prefer `gog --gmail-no-send` during read-only investigation.
- Superhuman `AI/*` labels are legacy — write `Triage/*` / `Muted/*` instead.

### Triage Categories for cooper@darkmatter.io

- **Always mute+archive (`Muted/Bulk`)**: Coinbase tx notifications, Verda Cloud instance notices, marketing (1stDibs, Mobile IV Medics, PostHog, Morningstar, Brex marketing, Coinbase marketing, Google Cloud webinars, Latitude.sh, Reown, Shadcnblocks, Vast.ai receipts), Todoist reminders, Linear notifications, USPS Informed Delivery, WeWork announcements, Google Workspace account manager outreach, Hetzner/OVHcloud noise, Anthropic privacy policy notices, expected Google security sign-ins, GitHub OAuth app/token-added confirmations, Cloudflare setup incomplete, Nebius marketing, OpenAI usage threshold alerts
- **Always `Triage/Needs-Action`**: Brex (debits, transfer restrictions, compliance, account maintenance, draft bills), Gusto payroll, Apple Developer cert expiry, GitHub security / codespace deletion, accountant (Shurek/Kristy Chen), Temporal Cloud trial expiry, QuickBooks Capital, Brex Support account maintenance, CFTC/Form 40 / exchange compliance until filed
- **Informational / FYI** (label Done or leave after note): OpenAI usage alerts when already known, Anthropic notices, Nous Research announcements

## MFA Code Retrieval Pattern

When a portal sends an email verification code, fetch it via gog:

```bash
# Wait a few seconds for delivery, then fetch latest from sender — search ALL accounts
sleep 5
for a in cooper@darkmatter.io me@cm.xyz; do
  gog -a "$a" gmail list 'from:(portalmail.cftc.gov OR notifications@example.com) newer_than:1d (code OR verification OR security)' --max 5 --json
done
# Short OTP bodies are fine with --plain; long forwards are not
gog -a cooper@darkmatter.io gmail read <threadId> --plain
```

This pattern is critical for agent-driven authenticated portal access (e.g., Canopy Tax, banking portals, CFTC LTR portal).

**Known OTP senders**

| Sender | Account that usually receives it | Notes |
|---|---|---|
| `NOREPLY@portalmail.cftc.gov` | `cooper@darkmatter.io` | CFTC Portal registration/login OTP; separate from 9-digit Form 40 code |
| Canopy / Shurek | accountant threads | Often appends to same thread — read **last** message |

**Pitfall: MFA codes in existing threads.** Some senders (e.g., Shurek Accounting/Canopy Tax) append new verification emails to the *same* Gmail thread. The thread ID returned by `gmail list` stays the same, but the code is in the newest message. When reading, use `gog gmail read <threadId> --plain` / `thread get --full` and look at the **last** message — earlier messages contain expired codes.

**Pitfall: OTP account ≠ notice account.** CFTC Form 40 notices may land on personal mail while portal OTPs go to the business email used at registration. Always multi-account search before reporting "no code".

## Key Flags

- `-y` / `--force` — Skip confirmations (required for batch operations)
- `--no-input` — Never prompt; fail instead (essential for agent/CI use)
- `--json` — JSON output for scripting
- `--plain` — Human-readable text output (best for agent consumption; truncates long bodies — see pitfall above)
- `--max N` — Limit results (not `--limit`)
- `--attach FILE,...` — Attachment file paths (comma-separated, repeatable)
- `--reply-to-message-id ID` — Reply to a Gmail message (sets In-Reply-To/References)
- `--thread-id ID` — Reply within a Gmail thread (uses latest message for headers)
- `--reply-all` — Auto-populate recipients from original message (requires --reply-to-message-id or --thread-id)
- `--quote` — Include quoted original message in reply
- `--from EMAIL` — Send from a verified send-as alias
- `--body-file PATH` — Body from file (`-` for stdin)
- `--body-html` / `--body-html-file` — HTML body (optional, alongside plain text)
