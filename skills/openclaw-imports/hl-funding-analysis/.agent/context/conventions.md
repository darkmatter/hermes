---
last_updated: 2026-05-05
---

# Conventions

## File layout

```
skills/hl-funding-analysis/
├── SKILL.md                       # user-facing trigger/usage doc
├── scripts/
│   ├── funding_history.py         # CLI screener
│   └── dashboard_data.py          # JSON sidecar
├── reference/
│   └── api-shapes.md              # HL info-API endpoint shapes
└── .agent/                        # agent context (this directory)
    ├── README.md
    ├── context/
    │   ├── overview.md
    │   ├── architecture.md
    │   ├── glossary.md
    │   └── conventions.md
    └── memory/
        ├── known-issues.md
        └── lessons.md
```

The standalone HTML lives in the user's Cowork outputs folder, not the repo.
See `architecture.md` for why.

## Python style

- Standard library only. The CLI scripts deliberately avoid `requests`,
  `aiohttp`, `httpx`, etc. — they ship as zero-dep tools that work in any
  environment with Python 3.10+. Use `urllib.request` for HTTP.
- Type hints where they aid readability. `from __future__ import annotations`
  at the top of new files.
- Dataclasses for structured records (see `WindowStats` in
  `funding_history.py`).
- Backoff: exponential with `2 ** attempt` seconds, max 3-6 attempts. HL
  rate-limits aggressively on 429 and on 503 with "DNS cache overflow" body.
- Concurrency: `ThreadPoolExecutor(max_workers=3)` is the safe ceiling for
  HL's info API; the dashboard browser side uses 4 because it's coming from
  a different IP. Don't raise either default casually.
- Checkpoint long syncs every 20 coins (see `sync_funding` /
  `sync_prices`).

## JS / browser style

- Vanilla JS. No build step, no bundler. The standalone HTML is one file.
- Load from CDN only what's listed in the template's allowed libraries.
  Today: Grid.js, Chart.js.
- Persistent UI state in `localStorage` under the `hl-dash:` namespace.
- CSS variables for color theming. Dark-mode-only; the modal and chart
  configs assume a dark canvas.

## Naming

- Coins are referenced by HL's universe name (e.g. `BTC`, `HYPE`, `kPEPE`).
  Some have a `k` prefix on HL — pass them through as-is, don't normalize.
- Side names: `SHORT` and `LONG` (uppercase). The screener splits its output
  into SHORT-HARVEST and LONG-HARVEST tables; keep the same casing.
- Funding rate is signed; always preserve the sign. APR is signed too.

## Cache locations

`/tmp/hl_funding_cache.json` and `/tmp/hl_price_cache.json`. These are
ephemeral by design — losing them costs one `--deep-sync` run. Don't move
them to `~/.cache/` or similar without coordinating with both scripts.

## When to update `.agent/`

- `context/` — when a real-world fact changes (a new tool ships, a script
  is renamed, an API endpoint we depend on moves).
- `memory/known-issues.md` — when you hit a gotcha that cost time to debug.
  Append entries with a short header + date + cause + workaround.
- `memory/lessons.md` — when a class of decisions becomes clear in
  retrospect.

Don't update `.agent/` for code style nits or one-off refactors.

## Versioning

No formal versioning — this is a personal-use skill. Significant breaking
changes (e.g., rewriting the cache format) should bump the cache filename
(`hl_funding_cache_v2.json`) so old caches don't get loaded by new code.
