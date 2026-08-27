---
last_updated: 2026-05-05
---

# Lessons

Accumulated lessons from past iterations on this skill. Append entries with
date + short header + body. Don't rewrite history — newer entries can
contradict older ones, that's fine.

## 2026-05 — Probe MCP tool shapes before building an artifact around them

Building a Cowork artifact that depends on `mcp__Desktop_Commander__start_process`
took two iterations to discover that the artifact runtime can't reach local
MCP servers at all. The bridge returns a *string* `"Tool call failed: 400"`
rather than throwing, which masked the issue until the user reported it.

Lesson: **before building a UI that depends on a tool category, verify the
*runtime* permits that category, not just the tool's individual schema.** For
artifacts specifically, the test is "is this tool a registered connector?"
(see `mcp__mcp-registry__list_connectors`).

Recovery here was a standalone HTML file — same UX, no Cowork dependency,
fetches the HL API directly from the browser.

## 2026-05 — Headline APR is misleading; rank by realized harvest PnL

Early versions of the screener ranked by absolute APR. Result: top of the
list was always the most extreme funding rates, which were extreme precisely
because the underlying was moving violently against the harvest side.

Lesson: **the metric that matters is `funding_collected − price_drift`, not
funding alone.** The screener now ranks by `harvest_pnl × sign_consistency`.
Keep this property when refactoring; don't bring back a "sort by APR"
default ranking.

## 2026-05 — Sparklines beat numbers for regime intuition

The first version of the screener tables had only numeric columns. Adding a
70×18 SVG sparkline of the 7d funding rate per row dramatically improved
"is this stable or noisy?" recognition. Cheap to compute, valuable in
context.

Lesson: **for any tabular dashboard, ask whether a tiny inline chart would
encode something hard to read from the number alone.** Funding stability,
price trend, OI trajectory are all good candidates.

## 2026-05 — Keep series data out of localStorage snapshots

Storing the full per-coin time series in the day-over-day snapshot blew
past localStorage quotas after a few days. Stripping `series` before
`JSON.stringify` keeps snapshots at ~20-50 KB.

Lesson: **distinguish "what's needed in memory for this render" from
"what's needed for tomorrow's diff."** Most live-render data is throwaway.
