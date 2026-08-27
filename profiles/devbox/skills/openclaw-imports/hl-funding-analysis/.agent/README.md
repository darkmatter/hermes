# .agent/ — hl-funding-analysis

Agent context for the `hl-funding-analysis` skill: Hyperliquid perp funding
screener (Python CLI), JSON sidecar, and standalone browser dashboard.

Read these in order before working on this skill:

1. `context/overview.md` — what this skill does and who uses it
2. `context/architecture.md` — the three components and how they relate
3. `context/glossary.md` — funding/harvest/regime terminology
4. `context/conventions.md` — file layout, where new code goes, style
5. `memory/known-issues.md` — active gotchas, especially the Cowork-bridge constraint
6. `memory/lessons.md` — accumulated lessons from past iterations

The skill itself lives one level up:

- `SKILL.md` — user-facing trigger/usage doc consumed by the agent runtime
- `scripts/funding_history.py` — main CLI screener with on-disk caching
- `scripts/dashboard_data.py` — JSON sidecar used by the (parked) Cowork artifact
- `reference/api-shapes.md` — Hyperliquid info-API endpoint shapes

The standalone browser dashboard (`hl-funding-screener-standalone.html`) is
the **primary live UI** for this skill but lives outside the repo, in the
user's Cowork outputs folder. See `context/architecture.md` for why.
