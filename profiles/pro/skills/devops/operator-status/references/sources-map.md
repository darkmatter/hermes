# Weekly Review — Sources Map

Condensed map of the connected sources used to compile a weekly review, what each contains, where it lives, and which report section it feeds. Adapt to whatever sources exist at run time; these are the durable ones observed in this environment.

## Source → report section

| Source | Location | Contains | Feeds section |
|---|---|---|---|
| Session DB (recent cron runs) | `session_search(limit=15, sort=newest)` | Titles + tool output of this week's cron runs | All three (freshest signal of what happened) |
| Obsidian Weekly files | `<team-vault>/20-work/weekly-updates/2026-NN-NN.md` | Synthesized weekly team status: engineering, data, product, notes | ✅ Accomplished (primary) |
| Daily Feed Builder recommendations | `~/.hermes/feed/recommendations.json` | Blocked kanban tasks with `why_blocked` + `actions[].label` | ⏳ Still open (blocked tasks) |
| Daily Briefing session | `session_search(session_id=…)` of latest "Daily Briefing" run | Live PR/Linear/Gmail snapshot minutes old | ⏳ Still open (PRs, issues, alerts) |
| Tweet Drafts cadence | `<personal-vault>/Tweet Drafts/2026-NN-NN.md` | One file per day | ✅ Accomplished (content cadence) |

## Cron session titles → content type

The session DB is the spine of the review. Each recurring cron has a known content type:

| Title prefix | Content | What to extract |
|---|---|---|
| Daily Briefing | Gmail + Linear + GitHub PRs/issues for the org | Open PRs awaiting review, unassigned Linear issues, security/infra Gmail alerts |
| Daily Comms Triage | Email + Slack triage summary | Anything needing human ack; mostly noise |
| Weekly Dark Matter Team Update | Full weekly synthesis saved to Obsidian | Pointer to the `20-work/weekly-updates/` file it produced — read that file, not the session |
| Daily Feed Builder | Recommendations for blocked kanban tasks | `recommendations.json` (blocked tasks) |
| LP Position Tracker Daily Digest | LP position deltas | Usually [SILENT] unless positions moved |
| Daily AMM Pool Report | AMM pool state | Usually [SILENT] unless pools moved |
| Feed Signal Collector (X + HN) | Social/news signal batch | Content-cadence signal only |

Read the **Daily Briefing** and **Weekly Dark Matter Team Update** sessions first — they carry the densest state. Skip sessions that returned `[SILENT]`.

## recommendations.json shape

```json
{
  "t_<id>": {
    "why_blocked": "<string — the root cause>",
    "category": "decision|secret|...",
    "actions": [
      { "kind": "choice|secret", "label": "<human-readable choice>",
        "options": [ { "label": "...", "recommended": true|false, "prompt": "..." } ] }
    ]
  }
}
```
- Top level is an **object keyed by task id**, not an array. Iterate with `.items()`.
- `why_blocked` is the one-line blocker; `actions[].label` / `actions[].options[].label` are the human-readable choices.
- **Surface recurring root causes once.** If many tasks share a blocker (e.g. a single expired gog OAuth token for `me@cm.xyz`), group them and state the single fix that unblocks the batch.

## Obsidian vault resolution (applies to sources 2 and 5)

This environment has **multiple** Obsidian vaults — a personal vault (`~/personal`) and a team/project vault (`~/git/<org>/obsidian`). `OBSIDIAN_VAULT_PATH` is often unset and the documented fallback (`~/Documents/Obsidian Vault`) often missing. Resolve per the `obsidian` skill's pitfall: `find ~ -maxdepth 4 -name '.obsidian' -type d`, then pick by content (`20-work/weekly-updates/` → team vault; `Tweet Drafts/` → personal vault).

## No calendar source — date-bound extraction

No Calendar tool and no `Calendar/` folder is typical. Do not fabricate dates. Extract date-bound items from the sources you *do* have:
- **Email tracking notices** — USPS/USIS "Expected Delivery by <Day>, <Date>" lines in Gmail snippets carry real delivery dates.
- **Deadline strings** in recommendations.json — e.g. "before July 1"; flag as overdue if past.
- **Month-cumulative billing alerts** — "exceeded 85% Free Tier for <Month>" accrues further; worth a Monday-morning look.
- **Recurring cron cadence** — note the daily/weekly jobs that will run next week.

Label the section honestly ("date-bound items + obvious follow-through"), not "calendar". Offer to wire a real calendar source at the end.

## Synthesis rules

- One bullet per real item; group by area. Lead each area with the dominant story.
- Don't re-enumerate every commit — the `20-work/weekly-updates/` file already collapsed them.
- Don't re-run live `gh`/Linear/`gog` queries if the Daily Briefing session already captured them minutes ago.
- Keep the whole report tight ("keep it tight" is the task brief). Action arrows (→) for items needing attention.
