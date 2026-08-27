---
name: weekly-review
description: Compile a human-readable weekly status review (accomplished / still-open / next-week calendar) by triangulating connected sources. Use for the recurring weekly-review cron job or any "what was accomplished this week" request.
platforms: [linux, macos, windows]
---

# Weekly Review

Compile a tight, human-readable weekly status report covering **what was accomplished this week**, **still-open items**, and **next week's calendar**. Pull from connected sources — do not ask the user for data you can reach yourself.

## Trigger

- A recurring cron job asking for a weekly review, OR
- A user request like "what did we do this week", "weekly status", "catch me up on this week".

## Sources to triangulate

The report is strongest when assembled from **multiple** independent sources, not one. Pull what exists; skip what doesn't. See `references/sources-map.md` for the full source → report-section mapping, file paths, and the shape of each artifact.

1. **Session DB** (`session_search`, sort=newest) — recent cron runs are the freshest signal of what actually happened this week. Titles like "Daily Briefing", "Daily Comms Triage", "Weekly Dark Matter Team Update", "Daily Feed Builder", "LP Position Tracker", "Daily AMM Pool Report" each correspond to a known content type; `session_search` with the session_id dumps their tool output (PR lists, Linear issues, Gmail alerts, blocked tasks).
2. **Obsidian `20-work/weekly-updates/` files** — synthesized weekly team updates (e.g. `20-work/weekly-updates/2026-NN-NN.md`) are the richest single artifact for accomplished-work. Prefer these over re-deriving from git logs. Load the `obsidian` skill to resolve the vault path (mind the multi-vault pitfall). Note: the team vault is `~/git/darkmatter/obsidian`; the canonical weekly-updates folder is `20-work/weekly-updates/` with plain `YYYY-MM-DD.md` naming (no suffix). Do NOT use the flat legacy `Weekly/` folder at vault root.
3. **`~/.hermes/feed/recommendations.json`** — blocked kanban tasks from the Daily Feed Builder. Each entry has `why_blocked` + `actions[].label`; these are your "still-open / awaiting human decision" items.
4. **Prior Daily Briefing session** — the live PR/Linear/Gmail snapshot taken closest to report time. Re-read it rather than re-running the queries.
5. **Personal vault `Tweet Drafts/`** — daily content cadence (one file per day); a quick `find -mtime -7` confirms whether daily drafts shipped.

## Output shape

Three sections, tight, action-arrows (→) for items needing attention:
- **✅ Accomplished this week** — group by area (infra, product repo, data, content). Lead with the dominant story; one bullet per real item. Skip noise.
- **⏳ Still open** — open PRs awaiting review, unassigned Linear issues, stale GH issues, security/infra alerts needing acknowledgement, and blocked kanban tasks (group the latter, surface recurring root causes like a single expired OAuth token gating many tasks).
- **📅 Next week's calendar** — date-bound items surfaced from the data (USPS deliveries, overdue deadlines, month-cumulative billing alerts) plus naturally-following work (unblock X, merge Y, triage Z).

## Pitfalls

- **No calendar source is typical.** There is no Calendar tool and often no `Calendar/` folder. Do not invent dates. Surface date-bound items from the sources you *do* have (email tracking notices, deadline strings like "before July 1", month-cumulative alerts) and label the section honestly as "date-bound items + obvious follow-through", not a real calendar. Offer to wire a real calendar source at the end.
- **`20-work/weekly-updates/` files vs `drafts/`-weekly files.** Both are named with weekly-ish patterns. The `20-work/weekly-updates/` files (`YYYY-MM-DD.md`) are the synthesized team status reports (what you want); `drafts/NN-NN-weekly.md` are Twitter draft batches (content, not status). Don't confuse them.
- **Don't re-run live queries if a recent session already did.** The Daily Briefing / Daily Comms Triage cron runs captured the PR/Linear/Gmail state minutes ago. Read that session's tool output instead of re-calling `gh` / Linear / `gog gmail`.
- **Recommendations.json shape.** Top level is `{task_id: {why_blocked, category, actions: [...]}}` — iterate the object, not an array. `actions[].label` is the human-readable choice.
- **Keep it tight.** The task says "keep it tight." One bullet per real item, group blocked tasks, surface recurring root causes once. Don't re-enumerate every commit.

- **Two-cron coupling — this skill reads, a sibling cron writes.** This skill is the *consumer*: it reads `20-work/weekly-updates/` files + session DB + recommendations.json and emits a chat report. The `20-work/weekly-updates/` files are produced by a *separate* writer cron ("Weekly Dark Matter Team Update", `91271c7fd0f3`). If those files go missing or land in the wrong folder, the bug is in the **writer cron's save path**, not in this skill — fix the writer's prompt, then move any stray files into `20-work/weekly-updates/` with plain `YYYY-MM-DD.md` naming. Do not add a save instruction to this skill's consumer cron.
- **Don't conclude "it was never a writer" without scanning sibling crons.** If a user reports "the weekly review cron isn't writing to the vault", the named cron may be the consumer (no save instruction by design). Before declaring "it was never instructed to write", list the other weekly-named crons and read the one whose prompt says "save it to the Obsidian vault" — that's the writer, and its hardcoded path is the likely culprit.
- **Cron delivery target must resolve.** When updating the cron that runs this skill, verify `deliver` is set to a working target. `deliver: "origin"` fails for CLI-created crons with `last_delivery_error: "no delivery target resolved for deliver=origin"` — the report is produced but vanishes. Use `deliver: "local"` (silent, no delivery) or a specific platform target like `slack:<DM_channel_id>` to send to the user. See `references/cron-delivery.md` for how to resolve the Hermes bot's Slack DM channel.

## Related

- `daily-feed` builds/maintains the feed dashboard (JSON + UI); this skill is the human-readable weekly review, not the dashboard. The dashboard's `recommendations.json` is an *input* here.
- `obsidian` for vault path resolution (mind its env-var-unset + multi-vault pitfall) and in-vault placement (PARA layout; see its `references/team-vault-layout.md` for the darkmatter team vault).
- **Weekly Dark Matter Team Update cron** (`91271c7fd0f3`, Mon 9am) is the *writer* that saves `20-work/weekly-updates/YYYY-MM-DD.md`; this skill is the *consumer* that reads them. Their paths are coupled — keep them aligned.
