# Gmail triage label taxonomy (Cooper)

Live labels on both Gmail accounts used for agent triage. Prefer this over legacy Superhuman labels.

Canonical DoD / autonomy contract: `~/.hermes/email-triage-dod-framework.md`
Kanban board: `email-triage`
Archived operational skill (still useful): `~/.hermes/skills/.archive/email-triage-autonomy/`

## Accounts

| Account | Role |
|---|---|
| `cooper@darkmatter.io` | Work / primary |
| `me@cm.xyz` | Personal (same mailbox family as `me@cooperm.com` aliasing patterns) |

Always pass `-a <account>` on every gog command. Query accounts separately and merge.

## Core labels (both accounts)

These are the **primary agent taxonomy**. Apply with name strings (gog resolves IDs).

| Label | Meaning | Typical side effects |
|---|---|---|
| `Triage/Needs-Action` | Requires Cooper or agent follow-up | Keep in inbox (or leave until acted); exclude from bulk mute |
| `Triage/Done` | Handled / closed | Often archive after label (`--remove-labels INBOX`) |
| `Triage/Delegated` | Someone else owns the thread | Optional archive if no Cooper action left |
| `Triage/Waiting` | Blocked on external reply / third party | Keep findable; do not archive as mute |
| `Muted/Bulk` | Bulk / marketing / noise not worth daily triage | Safe to archive after mute label |
| `Muted/Unsubscribe` | Unsubscribe candidate or completed mute path | Pair with unsubscribe workflow when acting |
| `Blocked` | Ignore / blocked sender path | Do not surface in daily action lists |

### Apply / verify (EXECUTE-SAFE)

Label + optional archive is reversible inbox work → **EXECUTE-SAFE** under the DoD framework. Still verify with a read-back query.

```bash
export GOG_KEYRING_PASSWORD=<REDACTED>

# List labels (confirm spelling / presence)
gog -a cooper@darkmatter.io gmail labels list
gog -a me@cm.xyz gmail labels list

# Apply triage labels to thread IDs (batch OK)
gog -a <account> gmail labels modify <id1> <id2> \
  --add "Triage/Needs-Action" -y --no-input

# Mute bulk + archive
gog -a <account> gmail labels modify <id1> <id2> \
  --add "Muted/Bulk" --remove INBOX -y --no-input

# Mark done + archive
gog -a <account> gmail labels modify <id1> \
  --add "Triage/Done" --remove "Triage/Needs-Action,INBOX" -y --no-input

# Verify
gog -a <account> gmail list 'label:"Triage/Needs-Action" newer_than:7d' --max 20 --json
gog -a <account> gmail list 'label:"Muted/Bulk" in:inbox newer_than:1d' --max 5 --json
# Expected after mute+archive: muted threads should not remain in inbox
```

**Done evidence examples**
- labeled: `label:"Triage/Needs-Action" <selector>` returns expected count
- archived: `in:inbox <selector>` returns 0
- never treat the agent assertion alone as proof

## Account-specific helper labels

### Personal only (`me@cm.xyz`)

| Label | Use |
|---|---|
| `Action Required` | Personal action bucket (often with star historically) |
| `Security Alert` | Auth / device / account-security notices |
| `Notes` | Self-notes / captures |

### Work only (`cooper@darkmatter.io`)

| Label | Use |
|---|---|
| `Cold outreach` | Inbound sales / cold pitches |
| `Later` | Intentionally defer (not the same as Waiting on someone else) |
| `no-op` | Acknowledged, no action |
| `dispatch-processed` / `dispatch-error` | Automation dispatch bookkeeping |
| `[Notion]` | Notion-related routing |
| `Sentry (voy)` | Voy/Sentry noise bucket |

## Legacy — do not prefer

`[Superhuman]/AI/*` labels still exist on both accounts (`Respond`, `Waiting`, `News`, `Marketing`, `Meeting`, `Social`, `Pitch`, `Login`, …). They are **legacy Superhuman classification**, not the current agent taxonomy. Do not invent new Superhuman labels. When labeling from triage automation, write the `Triage/*` and `Muted/*` set above.

## Daily Comms Triage cron expectations

Job: `Daily Comms Triage (Email + Slack)` · id `969ec44641bf` · ~9am PT.

Minimum email coverage in the prompt (both accounts, separate queries):

```bash
gog -a cooper@darkmatter.io gmail list "in:inbox newer_than:1d" --max 50 --json
gog -a me@cm.xyz gmail list "in:inbox newer_than:1d" --max 50 --json
```

**Summarize-only is incomplete** relative to the label system. A full triage pass should:

1. Pre-flight both accounts (auth doctor + list).
2. Classify threads into action / waiting / bulk / done buckets.
3. **Actually apply** the corresponding labels (at least `Triage/Needs-Action` and `Muted/Bulk`).
4. Optional EXECUTE-SAFE archive of pure noise after mute.
5. Produce the human digest + `~/.hermes/feed/cron-json/comms-triage.json`.
6. Gate: no send, no delete, no money movement without Cooper approval.

If the cron prompt still says “only check cooper@darkmatter.io” or “me@cm.xyz not configured,” that text is stale and must be fixed before relying on the job.

## Classification shortcuts

Map digest categories → labels:

| Digest bucket | Label |
|---|---|
| 🔴 Action needed | `Triage/Needs-Action` (+ personal `Action Required` / `Security Alert` when appropriate) |
| Waiting on someone else | `Triage/Waiting` |
| Delegated outbound ownership | `Triage/Delegated` |
| Handled | `Triage/Done` (+ archive) |
| Noise / marketing / receipts you won’t act on | `Muted/Bulk` (+ archive) |
| Unsubscribe path | `Muted/Unsubscribe` |

Always-flag domain heuristics still apply (Brex, Gusto, Apple certs, security alerts, accountant mail) → `Triage/Needs-Action`, not mute.

## Safety

- Labeling and archiving: EXECUTE-SAFE with verifying query.
- Sending mail / deleting / paying / rotating credentials: EXECUTE-GATED or HANDOFF (see DoD framework).
- Prefer `gog --gmail-no-send …` during read-only investigation.
- Always load keyring password in non-interactive shells before gog.
