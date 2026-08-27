# Sell response: liquidity-proportional (`--sell-response liq`)

Cooper preference: **sell size tracks pool liquidity, not price TP bag%.**

## Model

| | `tp` (legacy) | `liq` (preferred) |
|--|---------------|-------------------|
| When | gain ≥ TP rungs vs sell-ref | gain ≥ `--sell-min-gain` (**intended** default 0 ⇒ spot ≥ ref) |
| How much | `bag × ladder_frac` then caps | **target SOL = `pool_sol × sell_liq_frac`**, then caps |
| Continuous drip | needs `--tp-repeat` | natural (no tp_hits) |
| Fat bag risk | high without SOL cap | much lower **per clip** if liq_frac small |

### Size ≠ rate (say this when Cooper says “it was supposed to sell relative to liquidity”)

**Liq only sets per-clip SOL.** It does **not**:

- stop selling when the book is weak / mcap dumps
- track external buy flow
- cap daily inventory as % of pool
- pause when sister buy hots are dry

**Rate** still comes from `--cooldown` (+ jitter) × **`--max-per-hour` (absolute SOL)**. Clips correctly shrink as `pool` falls while the hour faucet keeps pulling ~N SOL/h until bag empty or process stop. Unopposed drip over many hours **will** own the tape.

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

At pool ~197 SOL → clip ≈ **0.98 SOL** before other caps. At pool ~52 SOL → clip ≈ **0.26 SOL** (size tracked; cumulative drain did not stop).

**Until gain-floor bug is fixed in `dip_buyer.py`:** do **not** arm live with `--sell-min-gain 0` if you need under-ref idle. Use e.g. `--sell-min-gain 0.001` or stop the sell run below ref.

## Caps still apply (order of shrink)

1. Probe up to `sell_frac_cap` of bag (quote)
2. Shrink to `min(max_sell_sol, liq_target, hour_left, pool×max_pool_frac)`
3. Impact guard via `max_sell_impact`

## Price gate — intended vs shipped (CRITICAL)

**Intended (docs / Cooper):** `--sell-min-gain 0` ⇒ sell only when spot ≥ sell-ref; under ref → wait.

**Shipped (bug, confirmed live 2026-08-07):**

```python
# dip_buyer.py ~1405
gain = max(0.0, (spot - ref) / ref) if ref > 0 else 0.0
# ~1809
if not stop_hit and gain + 1e-12 < min_gain:
    # wait …
```

Under ref, `gain` is floored to **0.0**. With `min_gain=0`, `0 < 0` is false → **gate never blocks**. Live log pattern:

```text
gain=0.0% dd=89.5% mcap=$18k | SIGNAL sell … (liq pool=51.58*0.0050=0.2579SOL…)
```

No `liq-sell waiting` lines while deep under 175k sell-ref.

| Reality | computed `gain` | `min_gain=0` | result |
|---------|-----------------|--------------|--------|
| spot ≪ ref | **0.0** (floored) | need `gain < 0` | **never blocks** |
| spot ≪ ref | **0.0** | `min_gain=0.001` | **blocks** (temp workaround) |

**Code fix (when editing bot):** gate on signed `(spot-ref)/ref` **or** `spot + eps < ref * (1.0 + min_gain)` — do not floor before the comparison. Heartbeat can still display non-negative `gain_pct` if desired.

**Ops prove gate works:** under ref must log `liq-sell waiting (gain … < min …)`; must **not** `SIGNAL … liq`.

## Prove sizing

- Boot: `SELL MODE=liq: clip SOL ~= pool_sol * 0.0050`
- Run log: `sell_response=liq sell_liq_frac=0.005`
- Signal: `liq pool=196.68*0.0050=0.9834SOL` (+ optional `+solcap` / `+impcap`)
- Heartbeat: `sell_response=liq`, `sell_liq_frac=0.005`
- **Not** stuck on `below first TP rung` when armed and gate passes

## Geometry with buy ramp

Typical: buys ramp 200→250k / 24h; sell fixed 175k + liq.

- Below sell-ref: buys may paint; sells **should** idle (`liq-sell waiting`) — **broken at min_gain=0 until fix**
- At/above sell-ref: liq drips proportional to pool
- Between sell-ref and buy-ref: possible two-sided if buys still see dd vs higher buy-ref

## Diagnosing “what crushed mcap?”

1. `botctl list` + powder on buy hots + sell `received_sol` / last fill age.
2. Aggregate `runs/<m8>/*/trades.csv` by day and hour: `buy_sol` vs `sell_sol`, `price_usd`, `pool_sol`.
3. Direction cron state `runs/.market_direction_state.json` → `last_report`: Δpool vs fleet net deploy.
4. If fleet sell ≈ pool SOL lost and buys = 0 after `wallet_low` → **self-drain**. Lead with that; external second.
5. Separate in the answer: **sizing worked (clips ∝ pool)** vs **rate + dead bids + noop gate crashed mcap**.

## Incident: MARV unopposed liq drip (2026-08-06 → 07)

| | |
|--|--|
| Peak (trade) | ~2026-08-06T08:18Z · spot ~2.25e-4 · pool ~222 SOL |
| Last buy fill | ~2026-08-06T08:24Z · buy hots emptied (~0.1–0.3 SOL) |
| Next ~28h | buy_sol=0 · padre liq ~5.5–6 SOL/h every hour |
| Last 24h sells | ~397 fills · ~139 SOL out |
| Direction @ 11:00Z | pool −70.6 SOL · fleet net −69.4 · external ≈ −1 |
| Outcome | mcap ~200k → ~18k · pool ~222 → ~52 · clips 0.98→0.26 SOL (size OK) |
| Gate | `gain=0.0% dd~89%` + continuous `SIGNAL … liq` under sell-ref 175k |

**Response order:** `botctl stop` sell run → fix/workaround min-gain → only then consider buy top-ups (sticky deep dd vs raised buy-ref will arm hard if funded).

## When not to use liq

- Cooper wants explicit price take-profit schedule → `tp` + ladder
- Emergency full dump → stop-loss / manual, not gentle liq
- Need “only sell into strength” while `min_gain=0` bug ships → stop process or arm `min_gain>0` after fix proof

## Incident lesson (older)

TP 4% of ~600M bag → ~35 SOL / ~20% impact. Liq mode exists so “gentle” cannot mean bag% of a whale free ATA.

## Incident lesson (newer)

Liq prevents **per-clip** chalk; it does **not** prevent **multi-hour unopposed inventory drip**. Pair with a **working** under-ref gate, awareness of buy-side powder, and/or hour caps that shrink with pool — or stop the sell bot when bids die.
