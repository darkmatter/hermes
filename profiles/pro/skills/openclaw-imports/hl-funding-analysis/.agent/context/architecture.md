---
last_updated: 2026-05-05
---

# Architecture

Three components, deliberately decoupled. They share the funding history
cache on disk; nothing else couples them at runtime.

```
┌──────────────────────────┐     ┌─────────────────────────────┐
│ funding_history.py       │ ─▶  │ /tmp/hl_funding_cache.json  │
│  (CLI screener, --sync)  │     │ /tmp/hl_price_cache.json    │
└──────────────────────────┘     └──────────────┬──────────────┘
                                                │
                                                ▼
                                  ┌─────────────────────────────┐
                                  │ dashboard_data.py           │
                                  │  reads caches + live API,   │
                                  │  emits one JSON blob        │
                                  └─────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ hl-funding-screener-standalone.html   (primary live UI)        │
│                                                                │
│   Browser fetch ──▶ api.hyperliquid.xyz/info                   │
│       (does NOT call dashboard_data.py — fully self-contained) │
│                                                                │
│   Renders: snapshot table, 7d windows for top-N, sparklines,   │
│            click-to-expand detail chart (Chart.js),            │
│            account panel from clearinghouseState               │
└────────────────────────────────────────────────────────────────┘
```

## funding_history.py — the CLI screener

The original tool. Authoritative for deep historical analysis. Maintains a
local cache so `--report` is offline-fast after the first `--deep-sync 90`.
Computes windows 7/30/60/90d with realized harvest PnL.

Lifecycle: run `--deep-sync 90` once. Then `--sync` daily (cron, launchd,
manual, or eventually a Cowork scheduled task). Then `--report` whenever you
want a table.

## dashboard_data.py — the JSON sidecar

A thin adapter. Reads the same on-disk caches as `funding_history.py`,
combines with a live `metaAndAssetCtxs` call, and emits a single JSON blob to
stdout. Originally written so a Cowork artifact could spawn it via Desktop
Commander and render the output. That artifact path is parked (see known
issues), but the sidecar is still useful from the terminal if you want a
machine-readable snapshot, or if a future agent wants to plug it into a
different pipeline.

Default writes to stdout. No `--out` flag today; add one if you need atomic
file writes for a producer/consumer setup.

## hl-funding-screener-standalone.html — the live UI

A self-contained HTML file the user opens in any browser. **Does not need
either Python script to be running.** It calls Hyperliquid's public info API
directly with `fetch()`.

On each load:

1. `metaAndAssetCtxs` → universe snapshot (mark, OI, vol, current APR, day Δ).
2. For top-N by absolute current APR + watchlist coins: paired `fundingHistory`
   + `candleSnapshot` calls over the last 7d. Concurrency capped at 4, with
   exponential backoff on 429s. Stores both aggregate stats and the raw
   series per coin so sparklines and the detail chart can use them.
3. If a wallet address is configured (localStorage): `clearinghouseState`
   for the positions panel.

Persistent state in localStorage:

- `hl-dash:filters` — min OI, min vol, depth, watchlist, exclude, auto-refresh.
- `hl-dash:wallet` — public wallet address (read-only).
- `hl-dash:snapshot:YYYY-MM-DD` — yesterday's snapshot (aggregates only,
  series stripped) for the day-over-day diff and regime summary.

Why standalone, not a Cowork artifact: see `memory/known-issues.md` — the
Cowork artifact runtime only proxies `callMcpTool` to registered connectors,
not local MCP servers, and there is no Hyperliquid connector. Direct `fetch()`
from the browser is the cleanest path; Hyperliquid's public info endpoints
are CORS-open.

## Data flow at a glance

| Surface                 | Where data comes from                          | When fresh        |
|-------------------------|------------------------------------------------|-------------------|
| `--report` (CLI)        | on-disk caches (synced by `--sync`)            | As of last `--sync` |
| dashboard_data.py JSON  | live `metaAndAssetCtxs` + on-disk funding cache | Snapshot live, 7d as fresh as cache |
| Standalone HTML         | live API only — no cache dependency             | Live each load    |

## Extending the standalone HTML

Common changes a future agent might make:

- **New filter**: extend `defaultFilters` and `bindFilters`, wire into
  `fetchData` filtering.
- **New column**: append to `cols` in `renderGrid` and to the `data` array.
  Keep tabular-nums formatting consistent.
- **New chart**: pick a coin's series from `marketByCoin[coin].series`. The
  detail modal is the natural home; add a second tab or panel if needed.
- **Different window**: change the `startMs` math in `fetchData`. For windows
  longer than ~20 days, you'll need to paginate `fundingHistory` (500-record
  cap per call) — copy the pagination loop from `funding_history.py`.

Don't break:

- The per-coin series shape `{ funding: [{t,r}], candles: [{t,c}] }`.
  Sparklines and the detail chart both read this.
- Day-over-day snapshot stripping — only aggregates persist, never the
  series, otherwise localStorage bloats fast.
- Light-mode assumptions in the modal styles — the file is dark-mode only.
