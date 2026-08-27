---
last_updated: 2026-05-05
---

# Glossary

## Funding rate

Perpetual futures contracts use funding payments to tether mark price to
spot. Longs and shorts pay each other a small amount every funding interval
(hourly on Hyperliquid). Positive funding = longs pay shorts; negative
funding = shorts pay longs. Quoted by HL as a signed decimal per hour
(`0.0000125` = 0.00125%/h ≈ 10.95% APR).

## APR (annualized funding rate)

`hourly_rate × 24 × 365 × 100`. The number this skill quotes everywhere.
A coin paying `0.00125%/h` shows up as ~10.95% APR.

## Funding cap on HL

Hyperliquid caps the hourly funding rate (currently ~0.00125%/h, ≈10.95%
APR). Many coins sit pinned at this cap during persistent imbalance —
expect to see many ~10.95% rows in the screener output during such regimes.

## Funding harvest

Strategy of holding a position to collect funding payments. Two flavours:

- **Short-harvest**: short the asset to receive positive funding. Profitable
  when funding income exceeds price drift up.
- **Long-harvest**: long the asset to receive negative funding (shorts paying
  longs). Often risky — negative funding usually exists because the asset is
  declining or shorts have strong conviction.

## Harvest PnL (realized)

What the harvest trade actually earned over a window, unleveraged, per $100
notional held continuously. Defined in `funding_history.py`:

- Short PnL = cumulative funding collected − price change of the underlying.
- Long PnL  = price change of the underlying − cumulative funding paid (or
  equivalently `−cum_funding + price_change`).

A 200% APR short where the coin doubles is a catastrophe, not a win.
`harvest_pnl` is the only metric in this skill that captures that honestly.

## Realized vs. headline

- **Headline APR** — annualized current or average funding rate. Easy to
  show; misleading on its own.
- **Realized harvest PnL** — what you would have actually made/lost on the
  carry trade. The screener ranks by this, not headline APR.

## Window (7/30/60/90d)

A trailing time window over which we compute aggregate stats. 7d windows are
short-term, regime-sensitive; 90d windows wash out short-term noise. The
screener and dashboard show multiple windows so contradictions are visible
(e.g., 7d positive harvest, 30d negative — recent regime shift).

## Sign consistency

Fraction of funding intervals in a window where funding had the dominant
sign. High consistency (>0.8) means the regime has been stable; low
consistency (<0.5) means funding flips frequently and the harvest is choppy.

## Regime

The overall posture of the funding market across coins. "Short-harvest
regime" = many coins paying positive funding (longs paying shorts), typical
during euphoric rallies. "Long-harvest regime" = many coins paying negative,
typical during sustained selling. The dashboard's day-over-day summary
reports the count delta on each side.

## Universe filter

OI ≥ $X M and 24h volume ≥ $Y M. Default $3M / $0.3M. Trims tiny markets
where funding is noisy and order books are thin enough that you can't trade
the harvest at size.

## Carry vs. basis

We use **carry** in this skill (a fixed-income loanword): yield from holding
the position. **Basis** refers specifically to the perp–spot price gap; we
don't trade or compute that directly here.

## clearinghouseState

The HL info-API endpoint that returns account state for a wallet address.
Includes `marginSummary` (account value, total notional, margin used) and
`assetPositions` (open positions with entry, mark, uPnL, leverage, liq
price). Read-only, no auth — anyone can query any wallet's state. The
dashboard's account panel uses this; the wallet address is stored in
localStorage only.

## USDH

Hyperliquid's native stablecoin, the collateral for HL accounts. Outcome
markets (HIP-4) also settle in USDH. This skill doesn't deal with USDH
balances directly — `clearinghouseState` returns USD-denominated values.
