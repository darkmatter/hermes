# MARV market direction report (cron)

## Purpose

Every **4 hours**, Slack Cooper a short read on:
- holders / concentration
- liquidity + pool SOL
- mcap / flow
- whether things are going the **right direction**: pool/liq growth **beyond** our bot deploy

Expires after **10 days** from first snapshot (state `expires_at`). Script no-ops after that; remove cron when done.

## Paths

| Piece | Path |
|-------|------|
| Report | `~/git/darkmatter/sol-dip-buyer/scripts/market_direction_report.py` |
| State | `runs/.market_direction_state.json` |
| Hermes wrapper | `~/.hermes/scripts/marv_direction_report.sh` |
| Cron | `0 */4 * * *`, `no_agent=true`, deliver `slack:D0AK02MKFRP`, workdir repo |
| Job name | `MARV direction report (10d)` |

**Never** pass absolute repo scripts to Hermes cron — use the `~/.hermes/scripts/` wrapper.

## Secrets

Alchemy via himitsu (do not paste keys):

```bash
himitsu exec alchemy-api-key -- .venv/bin/python scripts/market_direction_report.py
# wrapper does this; injects ALCHEMY_API_KEY
```

Env accepted by report:
- `ALCHEMY_API_KEY` (raw key **or** full `https://…alchemy…/v2/…` URL)
- `ALCHEMY_SOLANA_NETWORK` optional (default `solana-mainnet`)
- `SOLANA_RPC_URL` / `ALCHEMY_SOLANA_URL` override full URL

Public Solana RPC 429s easily — always for this job.

## Data sources

| Source | Used for |
|--------|----------|
| Dexscreener | price, fdv/mcap, pool SOL/USD liq, vol, buy/sell counts |
| GeckoTerminal `/info` | `holders.count`, top10 distribution % |
| Alchemy RPC | our wallets' SOL+MARV, mint supply, top token accounts + owner labels |

Our wallets labeled for exclusion narrative / inventory share:
`mrv` AZYsGo…, `dip` PWbrhU…, `mrv2` A3KwFS…, `padre` GKzKZW…

## Direction score (high level)

From last snapshot → now:
- **+** holders up, external pool SOL up (Δpool − our_net_deploy), liq/mcap up, 6h buy-heavy, less extreme top10
- **−** reverse

`our_net_deploy ≈ Δspent_sol − Δsell_received` from bot heartbeats/state.
External ≈ `Δpool_sol − our_net_deploy`. If pool only rose because we bought, do **not** call it organic liq growth.

## First run / baseline

First successful print is **t0** (no score). Subsequent runs score vs prior. History capped ~120 samples.

## Manual once

```bash
cd ~/git/darkmatter/sol-dip-buyer
himitsu exec alchemy-api-key -- .venv/bin/python scripts/market_direction_report.py
# or
~/.hermes/scripts/marv_direction_report.sh
```

## Pitfalls

- `himitsu exec` requires `REF... -- COMMAND` — e.g. `himitsu exec alchemy-api-key -- …`
- Expiry is script-side; cron `repeat forever` is fine. Empty/expiry message is quiet intentional.
- Gecko holder count can lag; Alchemy top bags show **our** share of supply (often dominant post-accumulation — call that out, don't spin as "organic holders").
- Graduated coins leave Pump.fun launch homepage mechanics — this report is **post-grad market health**, not KoTH rank.
