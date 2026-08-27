---
name: gog
description: >
  Google Workspace CLI (`gog`) — auth/keyring, Gmail ops, multi-account search,
  triage labels, batch unsubscribe, and cron verification. Use for any gog/Gmail/
  Google Workspace CLI task, keyring decryption failures, OAuth re-auth, inbox
  triage labeling, or multi-account email jobs. Supersedes gog-cli-troubleshooting.
version: 2.0.0
metadata:
  hermes:
    tags: [gog, gmail, google, oauth, keyring, email, triage]
    category: ops
    related_skills: [messaging, financial-operations]
---

# gog — Google Workspace CLI

Class-level skill for the `gog` CLI (Gmail, Calendar, Drive, Chat, and related Google APIs). Covers day-to-day operations **and** auth/keyring troubleshooting — one skill for the whole tool surface.

**Binary:** `gog` (Nix/home-manager, currently v0.29) · **Config gog actually reads:** `~/Library/Application Support/gogcli/config.json` · **File keyring:** `~/Library/Application Support/gogcli/keyring/` · **Password:** himitsu `gog/keyring-password` (also `GOG_KEYRING_*` in `~/.hermes/.env`)

`~/.config/gogcli/config.json` is a stale/ignored path on this machine. Writing `keyring_backend` there does nothing.

---

## Quick start

```bash
# Always pin the account in agent/cron sessions
export GOG_KEYRING_PASSWORD=<REDACTED>
gog -a <email> auth doctor
# Query is POSITIONAL (gog ≥0.27). --query / --limit are wrong → use --max.
gog -a <email> gmail list 'in:inbox newer_than:7d' --max 20 --json
```

- Always use `gog -a <account>`.
- Prefer `terminal()` over `execute_code` subprocesses — env/keyring does not inherit cleanly into nested Python.
- Full Gmail command reference: `references/email-operations.md`.
- Compliance Form 40 / CFTC code hunt: `references/email-triage-compliance.md` (do not stop at Coinbase forwards).

---

## Auth & keyring

### Corrupted tokens / refresh-client failures

**AES unwrap error shape:** `read token: ... aes.KeyUnwrap(): integrity check failed`.

1. `gog -a <email> auth doctor`
2. Restore OAuth client credentials if needed:
   ```bash
   himitsu read google/oauth-client-secret-darkmatter-drive.json > /tmp/client_secret.json
   gog auth credentials set /tmp/client_secret.json -y --no-input
   rm -f /tmp/client_secret.json
   ```
3. `gog auth remove <email> -y` then re-auth (CDP or two-step remote below).

**Refresh failure shape:** Gmail requests fail with `oauth2: "unauthorized_client" "Unauthorized"` even though `auth doctor` says the tokens are readable. Readable tokens do not prove that the current OAuth client can refresh them. First force a real exchange:

```bash
export GOG_KEYRING_BACKEND=file
export GOG_KEYRING_PASSWORD=<REDACTED>
gog -a cooper@darkmatter.io auth doctor --check
```

If `--check` fails with `unauthorized_client`, re-store the protected OAuth client JSON using step 2, then rerun `auth doctor --check` for **each** Gmail account before resuming Gmail mutations. Do not remove/re-auth the account token unless this repair fails; a successful `--check` is the required evidence that normal Gmail reads can resume.

### Backend mismatch (tokens exist, `gog auth list` empty)

Default macOS backend = **Keychain**. Env or config may force **file**. Mismatch is the #1 recurring re-auth loop.

```bash
gog --help 2>&1 | grep -i "keyring backend"
env | grep GOG_KEYRING
ls -la ~/Library/Application\ Support/gogcli/keyring/ 2>/dev/null
ls -la ~/.local/share/gogcli/keyring/ 2>/dev/null
security dump-keychain 2>/dev/null | grep -i gogcli | grep -i token
env -u GOG_KEYRING_BACKEND -u GOG_KEYRING_PASSWORD gog auth list
```

**Live setup (2026-08):** file backend is pinned in `~/Library/Application Support/gogcli/config.json` (`gog auth keyring file`). Tokens for `cooper@darkmatter.io` and `me@cm.xyz` live in the file keyring. `me@cooperm.com` is **keychain-only** and will not appear until re-authed into the file backend. Password is himitsu `gog/keyring-password` — export it before every gog command in non-interactive shells (Hermes `.env` should already inject it).

**macOS Keychain unlock spam:** unlocking items in Keychain Access does **not** stick. `gog` is a Nix-store binary; every home-manager switch changes `/nix/store/<hash>-…/bin/gog`, so macOS treats it as a new app and re-prompts. Agent subprocesses also often fail the Keychain ACL. Do **not** try to "Always Allow" — keep the file backend pinned and never let gog fall back to `auto`/`keychain`.

**Wrong-path trap:** `~/.config/gogcli/config.json` is ignored by gog ≥0.29. Confirm with `gog auth status` → `config_path` / `keyring_backend_source`. If source is `default` and backend is `auto`, you are on Keychain and will get prompts.

**Fix order:** (1) `gog auth keyring file` so the Application Support config exists, (2) supply password from himitsu / uncomment `GOG_KEYRING_*` in `~/.hermes/.env`, (3) `gog auth doctor --check` must show `keyring.backend file` and readable tokens, (4) only then consider deleting leftover `gogcli` Keychain items.

### Re-auth via live Chrome CDP

Use Cooper's live Chrome (port 9222). Full CDP reference: `financial-operations` → `references/live-chrome-cdp.md`.

1. Start `gog auth add <email>` in background; capture the OAuth URL.
2. `~/.hermes/scripts/live-chrome-cdp.js newtab "<OAUTH_URL>"`
3. Verify `gog -a <email> auth doctor` → `status: ok`.

OAuth URLs are single-use (port + state). Stale URLs fail silently. If CDP is down, `browser_navigate` against the current URL also works.

### Re-auth via two-step remote (preferred when user is present)

```bash
gog login <email> --services=gmail --gmail-scope=full --force-consent --remote --step 1
# user authorizes, pastes redirect URL
gog login <email> --services=gmail --gmail-scope=full --force-consent \
  --remote --step 2 --auth-url "<paste-redirect-url>"
gog -a <email> auth doctor
```

Multi-account chooser: verify `hd=` on the redirect matches the intended account before step 2.

### Agent caveats

- `gog auth add --no-input` prints the URL and exits instead of hanging.
- Prefer `terminal(background=true)` over shell `&`.
- `gog auth doctor --check` forces a full token refresh.

---

## Gmail operations

See `references/email-operations.md` for list/read/archive/send, MFA retrieval, and triage workflow.

### Multi-account search

When mail is not in the primary account, search all authed accounts. Alias-vs-token pitfalls and `--plain` body truncation workarounds: `references/multi-account-search.md`.

### Triage labels (Cooper)

Live taxonomy is `Triage/{Needs-Action,Done,Delegated,Waiting}` + `Muted/{Bulk,Unsubscribe}` (+ account helpers) — **not** Superhuman `AI/*`. Map and commands: `references/gmail-triage-labels.md`.

Interactive full-inbox triage ("triage my emails"): multi-pass list→classify→batch-label→re-list until inbox is mostly NA, always-flag money/domain heuristics, critical digest shape. Runbook: `references/interactive-triage-pass.md`.

Recent triage hardening: in noninteractive shells export `GOG_KEYRING_PASSWORD="$(himitsu read gog/keyring-password 2>/dev/null)"` before searches or mutations. Use `gog gmail thread modify <thread-id> -a <account>` for thread-level labels. For high-confidence verification, fetch each changed thread with `gog gmail thread get <id> -j` and inspect `messages[].labelIds` after resolving label IDs through `gog gmail labels list -j`; a broad Gmail search by sender/subject can match separate historical threads and is not sufficient evidence. Treat Gmail `rateLimitExceeded` as a pacing signal: avoid parallel full-inbox `--all` fetches; list small pages (for example `--max 10`) serially, pause between calls, archive safe buckets, then re-list so older messages advance. Treat security/OAuth alerts, registrar transfers, failed payments, compliance filings, failed production deploys, and account migrations as `Triage/Needs-Action`; obvious marketing/pitches/coupons as `Muted/Bulk` plus archive; clear receipts/deliveries as `Triage/Done` plus archive, but leave ambiguous operational mail in `Needs-Action`. If a paginated/stale ID returns Gmail 404, continue the batch and re-search rather than retrying indefinitely. If the user says a category is always ignorable (for example, Vercel), suppress it consistently in future triage rather than resurfacing it as an action item. If an expected transfer/payment/compliance item still needs human follow-up, create a Kanban task with the proposed action and keep the external approval/submission blocked. Never send, delete, click links, alter security settings, or approve permissions during triage.

**Triage presentation rule:** never present a large action queue in one user-facing response. Report at most **five action-needed items** per update, each with a body-based summary, deadline/consequence, uncertainty, and proposed next action. Put all low-risk/no-action items into one compact list; leave remaining actionable threads labeled for the next pass and/or create Kanban cards.

**Compliance/financial escalation:** for a compliance or regulatory notice, inspect attachments locally when possible and distinguish the provider's claim from independently verified facts. For a Form 40-style notice, extract the deadline and registration steps, verify sender/authentication and the relevant account/entity, and recommend confirming the reporting basis, code number, and extension options through a known official provider channel before portal registration or filing. **Do not stop at a Coinbase forward** — the 9-digit CFTC code is usually on the direct CFTC notice subject and/or the named personal PDF attachment, not the generic portal-instructions PDF. Multi-account search; portal OTPs often hit a different inbox than the notice. See `references/email-triage-compliance.md`.

### Batch unsubscribe

Extract `List-Unsubscribe` headers; hit HTTP/mailto per platform: `references/batch-unsubscribe.md`.

### Multi-account scale jobs (cron)

Verify each account with `gog -a … auth doctor --check` **and** a real read-only Gmail query. Encode every account in the cron prompt. Checklist: `references/multi-account-cron-verification.md`.

---

## Pitfalls

| Symptom | Cause / fix |
|---|---|
| Constant Keychain unlock prompts | gog is on `auto`/`keychain` (Nix path changes invalidate ACL). Pin file backend in `~/Library/Application Support/gogcli/config.json`, not `~/.config/gogcli/` |
| `aes.KeyUnwrap()` | Missing `GOG_KEYRING_PASSWORD` or corrupted file token — doctor → remove → re-auth |
| `accounts: []` but user did auth | Backend mismatch Keychain vs file — diagnose before re-auth |
| Auth works in terminal, fails in cron | Cron force-file without password, or reverse |
| Nested `execute_code` subprocess | Does not inherit keyring env — use `terminal()` |
| OAuth "authorized as wrong account" | Account chooser / `hd=` mismatch |
| `unknown flag --query` / `--limit` | gog ≥0.27: query is positional; use `--max` not `--limit` |
| `gmail read --plain` cuts mid-forward | Use `gmail thread get <id> --full --download --out-dir … --json` for compliance/long mail |
| Labels stuck after "Done" | `--remove "Triage/Needs-Action,INBOX,UNREAD"` (comma-separated) + `archive --thread` + `mark-read`; verify count 0 |
| "No CFTC code" after Coinbase forward only | Search direct `from:cftc.gov` / named PDF attachments; OTP is on `portalmail.cftc.gov` (often business inbox) |
| `cron-json` digest files got clobbered during triage | `~/.hermes/feed/cron-json/*.json` is load-bearing for other crons and the feed builder — never overwrite with a minimal stub; write the full `{source, run_time, items[]}` shape or leave alone |

---

## Related

- `communications` — Himalaya + BlueBubbles + phone; routes Gmail-API deep work here.
- `financial-operations` — live Chrome CDP for OAuth and bank flows.
- Archived predecessors: `gog-cli-troubleshooting` (content absorbed here).
