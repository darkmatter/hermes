# Dip entry sizing (Pump graduates)

## When this applies
User says TWAP / absorb dips / scale in / paint green / "eventually spend the whole bag" on a thin Solana meme after Pump graduation.

## First numbers
From DexScreener PumpSwap pair (not pumpfun bonding-curve pair after migrate):
- `liquidity.quote` ≈ **pool SOL**
- `liquidity.usd`, `marketCap`, `priceUsd`, m5/h1 `priceChange`, buy/sell txns

Jupiter sanity quote (0.1 SOL clips):
```
https://lite-api.jup.ag/swap/v1/quote?inputMint=So11111111111111111111111111111111111111112&outputMint=<MINT>&amount=100000000&slippageBps=300
```
Route label often `Pump.fun Amm`.

## Impact rule of thumb
Constant-product with quote reserve `R` SOL: a market buy of `x` SOL moves marginal price by roughly `(R+x)/R − 1` on the quote side (ignore fees). Paint impact-target sizing uses:
```text
x ≈ R * (sqrt(1 + i) - 1)   # i = target_impact, e.g. 0.06
```

| Clip vs pool SOL | Typical result |
|---:|---|
| ≤ 1–2% | small impact — fine probe |
| ~3% | noticeable; absorb/normal ceiling |
| ~10% | you are the candle (paint default pool-frac) |
| ≥ 100% | nonsensical as a single TWAP notional |

Always recompute live `R` — LP on new grads oscillates hard (session saw ~77 → ~55 → ~18 SOL in minutes).

## TWAP vs dip ladder
| Blind TWAP | Dip absorb / paint |
|---|---|
| Fires on a schedule into strength | Fires only when spot ≤ drawdown from ref |
| Pulls price up on your own flow | Adds on weakness (paint = louder add) |
| Large budget vs thin LP = inventory you can’t exit | Budget can sit unspent as SOL |

**Default recommendation:** drawdown ladder from current fix or user-pinned mcap ref — not wall-clock TWAP — unless they explicitly want path-independent accrual and accept impact.

## Clip size (glossary)
- **Budget** — max SOL the bot may spend over the whole run.
- **Clip** — SOL spent on **one** fill when a ladder level fires.
- **Actual clip** —
  ```text
  min(ladder_base, max_clip, pool_sol * max_pool_frac,
      [paint: max(base, impact_target_sol, min_clip)],
      remaining_budget, hour_room)
  ```
- On ~20 SOL pools, paint clips land near **1.5–3 SOL** even when ladder base says 8.

## Reference price
- Default: live USD spot at arm.
- **MC target:** prefer `--ref-mcap 100000` (bot converts via live supply = mcap/price; fallback 1B UI). Mental math: `ref_usd ≈ mcap / 1e9` on standard pump 1B supply.
- If live mcap ≪ ref, deepest rung stays hot → buys every cooldown until caps. Confirm before live.

## Style lever: absorb vs paint
User may explicitly accept impact so dip defenses **print green**. Name the mode out loud.

| Mode | Intent | Default knobs (scaffold) |
|---|---|---|
| **absorb** | Quiet scale-in | pool-frac ~2%; max_clip 3; hour 8; cooldown 120s; target impact ~1.5% |
| **normal** | Balanced | pool-frac ~4%; max_clip 6; hour 15; cooldown 90s; target ~3% |
| **paint** | Visible green recovery | pool-frac **~10%**; max_clip 8; hour 35; cooldown 45s; slip 500 bps; **impact-target** ~6%; earlier first rung (−8%) |

Paint still **dip-gated** — not wall-clock full-budget TWAP.

### Levers that actually move the candle harder
When user says "it should be moving price up a bit":

1. **Process must be LIVE and running** (`botctl status`). Stopped/paper → zero price effect.
2. **Below first rung** under ref? (paint = −8%). If above, ladder waits (correct).
3. Raise paint force (in order of usual ask):
   - `--target-impact 0.08..0.12` (primary “how green”)
   - `--max-pool-frac 0.12..0.20`
   - `--max-clip` up
   - `--cooldown` down / `--max-per-hour` up (frequency)
4. Do **not** invent multi-wallet wash to fake more volume.

This bot is **not** a continuous bid. Always-on staircase needs a different mode.

## Detached ops (required for live)
Path: `~/git/darkmatter/sol-dip-buyer/`

```bash
# multi-mint: --mint REQUIRED
./scripts/botctl start \
  --mint <MINT> \
  --live --confirm-live YES \
  --style paint --ref-mcap 100000 --budget 99 \
  --prefer-dex pumpswap

./scripts/botctl status --mint <MINT>
./scripts/botctl logs   --mint <MINT> -f
./scripts/botctl stop   --mint <MINT>
./scripts/botctl list

# cron / external supervise
.venv/bin/python scripts/monitor_check.py --mint <MINT> --json
# exit 0 ok; exit 1 stale heartbeat / dead pid / error status
```

Per-run dir `runs/<first8(mint)>/`:
| File | Purpose |
|------|---------|
| `bot.pid` | process id |
| `bot.lock` | exclusive flock (no double-start) |
| `heartbeat.json` | liveness + spot/dd/spent |
| `bot.log` | append log |
| `state.json` | durable spent/ref/fills (mint-guarded) |
| `trades.csv` | fill ledger |

**Why:** live trading must not embed in an agent turn/shell that can be interrupted. `botctl` uses `nohup`/`setsid`.

## Refuse: multi-wallet wash / spoof tooling
Do **not**: generate temp funder + N wallets, split SOL, and run coordinated multi-wallet buys to fake organic demand or beautify the chart. Offer single-wallet ladder/paint only.

## Wallet path (Cooper)
1. Padre for UI / initial funding / export — **any funded wallet is fine**; no requirement to use a scaffold deposit address.
2. Prefer export Padre → bot keyfile if funds already sit there.
3. Himitsu `sol-1` (czxtm/secrets):
   ```bash
   export DIP_BUYER_KEYPAIR=~/wallets/padre-sol-1.json
   himitsu exec sol-1 -- python - <<'PY'
   # env key matching sol-1 / SOL_1; base58 64-byte → Keypair
   # write list(bytes(kp)) chmod 600; print pubkey only
   PY
   ```
4. `getBalance` on derived pubkey before `--live --confirm-live YES`.
5. Never paste keys/seeds into chat or logs.

## Scaffold CLI (v2)
`~/git/darkmatter/sol-dip-buyer/dip_buyer.py`
- **`--mint` required** (portable across coins)
- `--ref-price` / `--ref-mcap`, `--style`, impact/pool/clip/hour/cooldown overrides
- `--run-dir` default `runs/<mint8>/`
- Paper default; `--live --confirm-live YES` + keypair for sends
- Jupiter lite quote/swap; DexScreener pair pick (`--prefer-dex pumpswap`)
- Prefer paid RPC (Helius) over public mainnet for live sends

## What not to encode as “safe”
- Dev Streamflow lock on ~1% creator bag
- LP burn after migration
- High session volume with micro LP
- Paint-style impact “working” as alpha — risk style, not DD clearance

Those are risk markers / DD facts, not permission to size like a major book.
