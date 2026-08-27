# Sell response: liquidity-proportional (`--sell-response liq`)

Cooper preference: **sell size tracks pool liquidity, not price TP bag%.**

## Model

| | `tp` (legacy) | `liq` (preferred) |
|--|---------------|-------------------|
| When | gain ≥ TP rungs vs sell-ref | gain ≥ `--sell-min-gain` (default 0 ⇒ spot ≥ ref) |
| How much | `bag × ladder_frac` then caps | **target SOL = `pool_sol × sell_liq_frac`**, then caps |
| Continuous drip | needs `--tp-repeat` | natural (no tp_hits) |
| Fat bag risk | high without SOL cap | much lower if liq_frac small |

## Live padre profile (MARV example)

```bash
--side sell --style absorb --run-id sell-absorb-padre \
  --ref-mcap 175000 \
  --sell-response liq --sell-liq-frac 0.005 --sell-min-gain 0 \
  --sell-frac-cap 0.05 \
  --max-sell-sol 2.0 --max-sell-impact 0.02 --max-pool-frac 0.01 \
  --max-per-hour 6 --cooldown 180 --cooldown-jitter 0.30 \
  --start-cooldown 60 --slippage-bps 300
```

At pool ~197 SOL → clip ≈ **0.98 SOL** before other caps.

## Caps still apply (order of shrink)

1. Probe up to `sell_frac_cap` of bag (quote)
2. Shrink to `min(max_sell_sol, liq_target, hour_left, pool×max_pool_frac)`
3. Impact guard via `max_sell_impact`

## Prove

- Boot: `SELL MODE=liq: clip SOL ~= pool_sol * 0.0050`
- Run log: `sell_response=liq sell_liq_frac=0.005`
- Signal: `liq pool=196.68*0.0050=0.9834SOL` (+ optional `+solcap` / `+impcap`)
- Heartbeat: `sell_response=liq`, `sell_liq_frac=0.005`
- **Not** stuck on `below first TP rung` when gain ≥ min-gain

## Geometry with buy ramp

Typical: buys ramp 200→250k / 24h; sell fixed 175k + liq.

- Below sell-ref: buys may paint; sells idle (`liq-sell waiting` if min-gain>0, or gain<0)
- At/above sell-ref: liq drips proportional to pool
- Between sell-ref and buy-ref: possible two-sided if buys still see dd vs higher buy-ref

## When not to use liq

- Cooper wants explicit price take-profit schedule → `tp` + ladder
- Emergency full dump → stop-loss / manual, not gentle liq

## Incident lesson

TP 4% of ~600M bag → ~35 SOL / ~20% impact. Liq mode exists so “gentle” cannot mean bag% of a whale free ATA.
