---
last_updated: 2026-05-05
review_by: 2026-08-05
---

# hl-funding-analysis — overview

## What this is

A Hyperliquid funding-rate analysis skill aimed at identifying carry-trade
opportunities — short-harvest (collect positive funding) and long-harvest
(collect negative funding). The skill answers "what would this harvest trade
have actually returned over the last N days, net of price drift in the
underlying?" — not just the headline APR, which is misleading on its own.

## Current state (May 2026)

Shipped:

- `scripts/funding_history.py` — terminal screener with on-disk caching at
  `/tmp/hl_funding_cache.json` and `/tmp/hl_price_cache.json`. Daily `--sync`
  pulls latest funding + price data; `--report` produces SHORT-HARVEST and
  LONG-HARVEST tables ranked by realized harvest PnL over 7/30/60/90d windows.
- `scripts/dashboard_data.py` — JSON sidecar that piggybacks on the same
  caches and emits a single JSON blob (market snapshot + 7d windows +
  optional account state from `clearinghouseState`).
- `hl-funding-screener-standalone.html` — browser-based live dashboard. Calls
  `api.hyperliquid.xyz` directly via `fetch`. Dark mode. Per-row sparklines
  for the 7d funding rate. Click-to-expand detail chart (Chart.js) showing
  hourly funding bars + price line over 7d. Account panel with positions,
  uPnL, liquidation distance. Watchlist + exclude filters persisted in
  localStorage. Day-over-day diff + deterministic regime summary.

Parked:

- The Cowork-artifact version of the dashboard (`hl-funding-screener` id).
  Replaced with a stub explaining the constraint — see
  `memory/known-issues.md`.

Planned (not started):

- Scheduled sync via Cowork's scheduled-tasks MCP so the funding cache stays
  fresh without a manual `--sync` step.
- A real Hyperliquid MCP connector that would unlock a live Cowork artifact.

## People

Cooper (cooper@darkmatter.io) is the primary user and owner. Future agents
should treat the dashboard as a personal-use tool for carry-trade scouting,
not a shared trading dashboard. No team review process for changes here.

## Adjacent projects

- The broader `darkmatter/agents` repo: this skill is one of several. The
  template at `template/.agent/` is the canonical shape for `.agent/` dirs.
- No upstream/downstream dependencies on other skills today.

## How to verify state

- **Funding cache freshness**: `ls -la /tmp/hl_funding_cache.json`. The
  dashboard's footer also reports cache coverage and age.
- **API connectivity**: `python3 scripts/dashboard_data.py | head` — should
  emit JSON within ~2s.
- **Dashboard health**: open the standalone HTML in a browser. The header
  shows market count and refresh timestamp; the errors panel (red) appears
  if any per-coin call failed.
- **Hyperliquid API status**: <https://api.hyperliquid.xyz/info> with body
  `{"type":"meta"}` from any HTTP client.
