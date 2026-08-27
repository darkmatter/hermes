# OpenClaw → Hermes Migration Reference

Cooper migrated from OpenClaw to Hermes Agent. This reference captures the
mapping between the two systems so future sessions can find old configs,
recreate jobs, and adapt prompts without rediscovering the differences.

## Where OpenClaw Configs Live

OpenClaw configs are scattered across local and Dropbox-synced paths.
**Always check both** — the Dropbox backups often have more complete data
than the local copy.

| Location | Contents |
|----------|----------|
| `~/.openclaw/` | Local openclaw home (may be stale/partial) |
| `~/.openclaw/cron/jobs.json` | Local cron job definitions |
| `~/.openclaw/openclaw.json` | Main config (gateway, agents, channels) |
| `~/.openclaw/agents/<name>/` | Per-agent configs and session logs |
| `~/Dropbox (Personal)/usr/<machine>/openclaw/` | Per-machine backup (coopers-mac-studio, macpro, coopers-mac-pro) |
| `~/Dropbox (Personal)/usr/<machine>/openclaw/cron/jobs.json` | Per-machine cron backup — **often the most complete source** |
| `~/Dropbox (Personal)/var/backup/backups/openclaw/` | Full config backup snapshot |

### Discovery pattern

```bash
# Local cron jobs
cat ~/.openclaw/cron/jobs.json

# All machine backups in Dropbox
find ~/Dropbox\ \(Personal\)/usr -path "*/openclaw/cron/jobs.json" 2>/dev/null

# All openclaw config files
find ~/Dropbox\ \(Personal\) -path "*/openclaw/openclaw.json" 2>/dev/null
```

**Key lesson:** The Mac Studio backup had 11 jobs while the local machine only had 3. Always check all machine backups.

## Hermes Cron Schedule Format — Pitfalls

| You type | What happens | What you probably wanted |
|----------|-------------|------------------------|
| `"0 9 * * *"` | Daily at 9am (5-field cron) ✅ | Daily at 9am |
| `"every 2h"` | Every 2 hours, recurring ✅ | Every 2 hours |
| `"30m"` | **ONE-SHOT** — fires once in 30 min, then done ❌ | Every 30 min |
| `"every 30m"` | Every 30 min, recurring ✅ | Every 30 min |

**Rule:** For recurring interval schedules, ALWAYS use the `every` prefix.

## Secret/Path/Service Mapping

| OpenClaw | Hermes | Notes |
|----------|--------|-------|
| `/run/agenix/<key>` | `himitsu read <key>` | agenix → himitsu (key names differ) |
| `~/` | `~/` | Home dir changed |
| `~/.openclaw/workspace/` | `~/git/darkmatter/` or `~/.hermes/` | Workspace relocated |
| `~/.openclaw/workspace/scripts/` | `~/git/darkmatter/.scripts/` | Scripts moved (some GONE) |
| `~/.openclaw/workspace/memory/` | `~/.hermes/data/` | Daily notes relocated |
| Raw `xoxb-` Slack bot token | Composio Slack bot | Slack delivery via Composio |
| Raw Telegram Bot API `sendMessage` | Cron `deliver` mechanism | Let Hermes handle delivery |
| `/run/agenix/github_token` | `gh` CLI or `himitsu read personal/github-personal-access-token` | GitHub token |
| `/run/agenix/dune-api-key` | `himitsu read dune-api-key` | Dune API key (hyphen, not slash) |

### Himitsu Key Names — Verified June 2026

Himitsu keys use **hyphens, not slashes**. Verified keys:

| Key | Status |
|-----|--------|
| `dune-api-key` | ✅ exists |
| `composio-api-key` | ✅ exists |
| `linear-api-key` | ✅ exists (also `personal/linear-api-key`) |
| `personal/github-personal-access-token` | ✅ exists |
| `github/darkmatter-bot/app-id` | ✅ exists (GitHub App) |
| `github/darkmatter-bot/private-key` | ✅ exists |
| `todoist/api-key` | ❌ does NOT exist |
| `slack/bot-token` | ❌ does NOT exist (use Composio) |
| `telegram/bot-token` | ❌ does NOT exist (use Hermes `deliver`) |

**Rule:** Always run `himitsu search <term>` to verify a key exists.

### GOG CLI — Account Flag Required

GOG CLI requires the `-a <email>` flag for all commands.
- `cooper@darkmatter.io` — ✅ Gmail + Calendar + Drive authed
- `me@cm.xyz` — ❌ Gmail NOT authed

## Migration Workflow

1. **Find all jobs** — check local AND all Dropbox machine backups.
2. **Map each job** — apply the secret/path/service substitutions above.
3. **Create via `cronjob` tool** — use `action="create"` with adapted prompt.
4. **Pause immediately** — use `action="pause"` right after creation.
5. **Verify paths** — check referenced scripts exist at new locations.
6. **Resume individually** — unpause one at a time after verification.

## OpenClaw Agents

OpenClaw had multiple agents: `main`, `assistant`, `coach`, `coder`, `lobster`,
`lp-team`, `pm`, `qa`, `translator`, `openclaw-dev`.

In Hermes, these map to:
- **Profiles** (`~/.hermes/profiles/<name>/`) for fully isolated agents
- **Skills** for task-specific capabilities
- **Cron jobs with `workdir`** for workspace-scoped agent runs

## Full Cron Job Inventory

See `references/openclaw-cron-jobs.md` for the complete inventory of 11 jobs
migrated in June 2026, with schedules, Hermes job IDs, and adaptation notes.
