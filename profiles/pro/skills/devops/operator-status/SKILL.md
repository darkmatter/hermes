---
name: operator-status
description: >
  Cooper's operator status surfaces — daily feed dashboard (localhost:8654
  blocked-kanban + digests + recommendations) and human-readable weekly review
  (accomplished / still-open / next-week). Use for feed rebuilds, dashboard
  layout, weekly status reports, "what happened this week", or cron wiring for
  either surface. Supersedes daily-feed and weekly-review as separate skills.
version: 1.0.0
metadata:
  hermes:
    tags: [feed, weekly-review, dashboard, status, cron, recommendations]
    category: devops
    related_skills: [obsidian, kanban-worker, gog]
---

# Operator Status (Daily Feed + Weekly Review)

One class for Cooper's status-reporting surfaces. Two modes share data
(`recommendations.json`, cron outputs, session DB) but different outputs:

| Mode | When | Output |
|---|---|---|
| **Daily feed dashboard** | Build/fix the UI at http://localhost:8654/, edit layout, regenerate feed data | React app in `~/feed/` |
| **Weekly review** | Cron or "what did we do this week" | Tight chat report: ✅ / ⏳ / 📅 |

Load this skill for either. Jump to the matching section below.

---

## Modes at a glance

```
Sources ──► ~/.hermes/feed/* + session DB + Obsidian weekly-updates
              │
              ├─ Daily Feed Builder cron ──► recommendations.json + feed-data.json ──► dashboard UI
              └─ Weekly review consumer  ──► chat report (reads the same artifacts; does NOT write vault)
```

Writer/consumer split (weekly): **Weekly Dark Matter Team Update** cron (`91271c7fd0f3`) *writes* `20-work/weekly-updates/YYYY-MM-DD.md`; weekly-review *reads* it. Do not add a save path to the consumer.

---

# Mode A — Daily feed dashboard

Cooper's command-center: blocked kanban + cron digests + recommended unblock actions, dark mode.

## Architecture

- **Project:** `~/feed/` — Vite + React + TypeScript + Tailwind + shadcn/ui
- **Block:** @shadcnblocks `dashboard9`
- **Server:** launchd `ai.cooper.feed-server` → `~/feed/dist/` on port **8654**
- **Data sources:**
  - `email-triage` kanban board (blocked tasks)
  - Cron outputs under `~/.hermes/cron/output/<job_id>/`
  - `~/.hermes/feed/recommendations.json`
  - Cron JSON under `~/.hermes/feed/cron-json/*.json` (see `references/cron-json-schema.md`)
- **Build:** `python3 ~/.hermes/scripts/build-feed.py` → `src/feed-data.json` → `bun run build`
- **Crons:** Daily Feed Builder `9acdbe616b8f` (9:30am PT); Feed Signal Collector `8f134b8a1a93` (7am PT); Daily Comms Triage `969ec44641bf`; Daily Todo Scan `8176f001451b`

## Key files

| File | Purpose |
|------|---------|
| `~/.hermes/scripts/build-feed.py` | Data collector + build runner |
| `~/feed/src/components/dashboard9.tsx` | Main dashboard component |
| `~/feed/src/feed-data.json` | Generated data |
| `~/.hermes/feed/recommendations.json` | Per-task recommendations (copy/secret/choice) |
| `~/feed/components.json` | shadcn + @shadcnblocks registry |
| `~/Library/LaunchAgents/ai.cooper.feed-server.plist` | Persistent HTTP server |

## Recommendation format

```json
{
  "t_XXXXX": {
    "why_blocked": "short reason",
    "category": "secret|decision|draft|confirmation",
    "actions": [
      {"kind": "copy", "label": "Copy prompt…", "prompt": "…", "recommended": true},
      {"kind": "secret", "label": "…", "placeholder": "where to find secret", "prompt_template": "…{{SECRET}}…"},
      {"kind": "choice", "label": "Choose:", "options": [{"label": "A", "recommended": true, "prompt": "…"}]}
    ]
  }
}
```

## Manual rebuild & server

```bash
python3 ~/.hermes/scripts/build-feed.py
launchctl list | grep feed-server
curl -s -o /dev/null -w "%{http_code}" http://localhost:8654/
# restart:
launchctl unload ~/Library/LaunchAgents/ai.cooper.feed-server.plist
launchctl load  ~/Library/LaunchAgents/ai.cooper.feed-server.plist
tail -20 ~/.hermes/logs/feed-server.log
```

## shadcnblocks

- Key: `himitsu read shadcnblocks-api-key`
- Install: `cd ~/feed && bunx --bun shadcn@latest add @shadcnblocks/<name> --overwrite --yes`
- Direct API without MCP: `references/shadcnblocks-api.md`
- Present 3–4 layout options via `clarify` before installing — Cooper chooses.

## Feed pitfalls

- Must use HTTP on 8654 — `file://` breaks ES modules.
- Always dark mode (`class="dark"` on `<html>`).
- Feed freshness = last `build-feed.py` run (cron 9:30am or manual); page meta-refreshes every 10 min.
- Raw `~/.hermes/cron/jobs.json` uses field **`id`**, not `job_id` (API returns `job_id`).
- Auxiliary vision needs `base_url` + `api_key`, not just provider/model.
- Broad digest (messages, X, HN, crons) — not a pure todo list. Cards and sidebar should be clickable.

## Interactive UI contracts

- Sidebar → `scrollIntoView` on `section-overview|blocked|messages|xposts|hn|ready|digests`
- `FeedItemCard` links open in a new tab when `item.link` is set
- Copy actions → clipboard + toast; comments/digests use Collapsible

---

# Mode B — Weekly review (human report)

Tight report: **what was accomplished**, **still open**, **next week**. Pull connected sources; do not ask the user for data you can reach.

## Triggers

- Recurring weekly-review cron, OR
- User: "what did we do this week", "weekly status", "catch me up"

## Sources (triangulate; skip missing)

Full map: `references/sources-map.md`.

1. **Session DB** (`session_search`, sort=newest) — Daily Briefing, Comms Triage, Weekly Dark Matter Team Update, Feed Builder, LP/AMM digests.
2. **Obsidian** `20-work/weekly-updates/YYYY-MM-DD.md` (team vault `~/git/darkmatter/obsidian`) — primary accomplished-work artifact. Load `obsidian` skill (multi-vault pitfall). Never the legacy flat `Weekly/` root folder. Don't confuse with personal `drafts/*-weekly.md` tweet batches.
3. **`~/.hermes/feed/recommendations.json`** — blocked kanban → still-open.
4. **Latest Daily Briefing session** — re-read instead of re-querying gh/Linear/gog.
5. **Personal vault `Tweet Drafts/`** — content cadence (`find -mtime -7`).

## Output shape

- **✅ Accomplished** — by area; one bullet per real item; lead with dominant story.
- **⏳ Still open** — PRs, unassigned Linear, alerts, blocked kanban (group; surface shared root causes once).
- **📅 Next week** — date-bound items from sources + obvious follow-through. No invented calendar — there is often no Calendar tool.

## Weekly pitfalls

- Two-cron coupling: consumer vs writer (`91271c7fd0f3`). Missing vault files → fix the **writer** path, not this consumer.
- Don't declare "never a writer" without listing sibling weekly crons.
- `deliver: "origin"` fails for CLI-created crons (`no delivery target resolved`). Use `local` or `slack:<DM_channel_id>` — see `references/cron-delivery.md`.
- Keep it tight.

---

## Shared references

| File | Topic |
|------|--------|
| `references/cron-json-schema.md` | Feed cron JSON shape |
| `references/shadcnblocks-api.md` | shadcnblocks without MCP |
| `references/sources-map.md` | Weekly source → section map |
| `references/cron-delivery.md` | Slack DM deliver target resolution |
| `references/daily-feed-skill.md` | Full pre-merge daily-feed body (archive copy) |
| `references/weekly-review-skill.md` | Full pre-merge weekly-review body (archive copy) |

## Related

- `obsidian` — vault path + PARA placement
- `gog` / `communications` — mail sources feeding digests
- `kanban-worker` / `kanban-orchestrator` — blocked task lifecycle the feed surfaces
