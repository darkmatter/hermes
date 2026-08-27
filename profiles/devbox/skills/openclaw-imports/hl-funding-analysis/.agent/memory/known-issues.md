---
last_updated: 2026-05-05
---

# Known issues

## Cowork artifacts can't call local MCP servers (2026-05)

**Symptom**: a Cowork artifact that calls
`window.cowork.callMcpTool('mcp__Desktop_Commander__start_process', ...)`
gets back the string `"Tool call failed: 400"`. The bridge silently rejects
the call rather than throwing.

**Cause**: the artifact runtime only proxies `callMcpTool` to **registered
connectors** (entries you'd see from `mcp__mcp-registry__list_connectors` —
e.g., Linear). Local stdio MCP servers like Desktop Commander, Control
Chrome, iMessage, etc. are not callable from artifacts, regardless of
whether they're listed in the artifact's `mcp_tools` parameter at creation
time.

**Workaround**: the live UI is a **standalone HTML file** opened directly in
the user's browser. It calls `api.hyperliquid.xyz` with `fetch()`, no Cowork
sandbox involved. The Cowork artifact slot is parked with an explainer stub.

**What would unblock the Cowork-artifact path**: a real Hyperliquid MCP
connector (registered like `mcp.linear.app`-style). Until then, don't try
to reroute through Desktop Commander, workspace bash, or Chrome control —
all hit the same 400.

## HL info API rate limits (ongoing)

**Symptom**: 429 or 503 with body "DNS cache overflow" after sustained
scraping.

**Workaround**: cap concurrency at 3 workers from a single IP (Python CLI),
4 from the browser. Use exponential backoff. Cache aggressively — funding
records older than yesterday almost never change.

## Funding cap pins many coins at exactly 10.95% APR

**Symptom**: SHORT-HARVEST table shows a long run of coins with identical
`Now APR` of ~10.95%.

**Cause**: HL caps hourly funding at ~0.00125%/h. Many coins sit at the cap
during persistent imbalance.

**Not a bug.** The 7d windows differentiate these — coins that have been
pinned all week vs. coins that just hit the cap show very different cum%
and harvest PnL.

## Empty funding cache on first artifact open

**Symptom**: 7d columns all show `—`. Dashboard footer says "no funding
cache yet" (when reading via dashboard_data.py).

**Cause**: `funding_history.py --deep-sync 90` hasn't been run.

**Workaround**: run it once. The standalone HTML bypasses this entirely by
fetching `fundingHistory` directly per coin, so the user-facing dashboard
doesn't need the cache.

## kPEPE (and other `k`-prefixed coins) confuse normalization

If you write any code that strips prefixes or "fixes" symbols, leave `k`
prefixes alone — HL uses them on its universe for tokens where the contract
unit is 1000× the base unit. Stripping them breaks `clearinghouseState`
lookups and funding-cache keys.

## Stale day-over-day snapshot when filters change mid-day

If the user changes `min OI` or `min vol` filters between snapshot saves,
the day-over-day diff compares an apple-yesterday to an orange-today
universe. The diff still computes (only coins present on both sides
contribute), but the "new" and "dropped" lists will be noisy with
filter-driven changes rather than real listings.

Not worth fixing today — the diff is informational, not decisional.
