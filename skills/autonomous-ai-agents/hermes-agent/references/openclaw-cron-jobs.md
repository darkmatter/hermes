# OpenClaw Cron Jobs — Full Inventory (June 2026 Migration)

Source: `~/Dropbox (Personal)/usr/coopers-mac-studio/openclaw/cron/jobs.json`
(Most complete copy — local machine only had 3 of 11 jobs)

## Current Status (updated 2026-06-19)

11 jobs were migrated from openclaw to Hermes on 2026-06-19. After review,
4 were removed, leaving 7 active (all still paused pending fixes).

**Removed:** Jobs 1 (telavaya check-in), 2 (vivian check-in), 3 (Cooper 1:1), 9 (Workspace Auto-Push)
**Remaining (paused):** Jobs 4, 5, 6, 7, 8, 10, 11

## Verification Results (June 2026)

### Scripts
- `daily-pool-report.sh` — **GONE**. Not found at `~/git/darkmatter/.scripts/` or `~/.openclaw/workspace/scripts/`. Job 4 cannot run until recreated.
- `auto-push.sh` — Exists at `~/.openclaw/workspace/scripts/auto-push.sh`. NOT at `~/git/darkmatter/.scripts/`. (Job 9 removed.)

### Paths
- `~/git/darkmatter/obsidian/` — ✅ exists
- `~/git/darkmatter/obsidian/drafts/` — ❌ missing (needs creation for Job 11)
- `~/git/darkmatter/obsidian/Weekly/` — ❌ missing (needs creation for Job 7)
- `~/.hermes/data/` — ❌ missing (needs creation for Jobs 5, 10)
- `~/.openclaw/workspace/inbox/` — ✅ exists, 1 file (Job 10)

### Secrets (verified via `himitsu search`)
- `dune-api-key` — ✅ (Job 4, 5)
- `composio-api-key` — ✅ (all Slack-sending jobs)
- `linear-api-key` — ✅ (Job 5, 6)
- `personal/github-personal-access-token` — ✅ (Job 7)
- `todoist/api-key` — ❌ does NOT exist (Job 5 Todoist sync will fail)
- `slack/bot-token`, `slack/app-token` — ❌ do NOT exist (use Composio)
- `telegram/bot-token` — ❌ does NOT exist (use Hermes `deliver`)

### GOG Accounts
- `cooper@darkmatter.io` — ✅ Gmail + Calendar + Drive authed (requires `-a` flag)
- `me@cm.xyz` — ❌ Gmail NOT authed (Job 8 references this account)

---

## Remaining Paused Jobs

### 4. Daily AMM Pool Report
- **Hermes Job ID:** `fb616c8fe033`
- **Schedule:** `0 7 * * 1-5` (Mon–Fri 7:00 AM PT)
- **BLOCKER:** `daily-pool-report.sh` is GONE.

### 5. Daily Todo Scan & Audit
- **Hermes Job ID:** `8176f001451b`
- **Schedule:** `0 8 * * *` (Daily 8:00 AM PT)
- **Issues:** `todoist/api-key` not in himitsu. `~/.hermes/data/` dir needs creation.

### 6. FYI Farhan — Daily Briefing
- **Hermes Job ID:** `27bbec739500`
- **Schedule:** `0 8 * * *` (Daily 8:00 AM PT)

### 7. Weekly Dark Matter Team Update
- **Hermes Job ID:** `91271c7fd0f3`
- **Schedule:** `0 9 * * 1` (Mon 9:00 AM PT)
- **Issues:** `~/git/darkmatter/obsidian/Weekly/` needs creation.

### 8. Daily Comms Triage (Email + Slack)
- **Hermes Job ID:** `969ec44641bf`
- **Schedule:** `0 9 * * *` (Daily 9:00 AM PT)
- **Issues:** Only `cooper@darkmatter.io` is authed with gog.

### 10. Inbox Processor
- **Hermes Job ID:** `ddc8ab692f83`
- **Schedule:** `30 7 * * *` (Daily 7:30 AM PT)

### 11. Weekly Content Ghostwriter
- **Hermes Job ID:** `3b9e0a9018c6`
- **Schedule:** `0 9 * * 0` (Sun 9:00 AM PT)
- **Issues:** `~/git/darkmatter/obsidian/drafts/` needs creation.

---

## Removed Jobs

1. Daily check-in — telavaya (LP Managers) — removed by Cooper 2026-06-19
2. Daily check-in — vivian (LP Managers) — removed by Cooper 2026-06-19
3. Daily 1:1 — Cooper (LP Managers lead) — removed by Cooper 2026-06-19
9. Workspace Auto-Push — removed by Cooper 2026-06-19

## OpenClaw failure state

All jobs were failing due to model resolution errors: `@preset/kimi`,
`@preset/deepseek`, `@preset/gpt-oss-120b` all returned `model_not_found`.
