# Timed ref ramp + restart cooldown

## Why

Cooper wants buy (or sell) reference to **start at one mcap and rise to another by a future time**, without babysitting stepped restarts. Also: every bare restart was **instantly buying** because cooldown history died with the PID.

## Flags (`dip_buyer.py`)

| Flag | Meaning |
|------|---------|
| `--ref-mcap START` | Ramp **start** (also plain fixed ref if no ramp) |
| `--ref-mcap-end END` | Ramp **finish** mcap |
| `--ref-ramp-end SPEC` | When finish: `12h`, `2d`, `1w`, or ISO `2026-08-01T12:00:00Z` |
| `--ref-price` / `--ref-price-end` | Same in absolute USD (prefer mcap ramp) |
| `--start-cooldown SEC` | On boot, pretend a fill SEC ago (blocks instant clip) |
| `--honor-last-fill` | Default **on** — seed CD from `state.last_fill_at` |
| `--no-honor-last-fill` | Cold-start fire allowed |

Requires **both** an end value and `--ref-ramp-end`. Past end → end value immediately (logs warning).

## Mechanics

- State stores `ref_ramp: {t0, t1, start_mcap, end_mcap, start_price, …}`.
- Each poll: `current_ref()` linear-interpolates; heartbeat exposes live `ref_mcap_usd` plus `ref_ramping`, `ref_ramp_progress`, `ref_mcap_start/end`, `ref_ramp_end_ts`.
- Mcap ramp converts to price via live supply (`mcap/spot`) so supply drift doesn’t freeze a stale px.

## Live example (MARV)

```bash
FREQ='0.15:150,0.25:90,0.40:60,0.55:40,0.70:25'

# buys: 175k → 200k over 12h
./scripts/botctl start --mint $MINT --side buy --style paint --run-id buy-paint-mrv2 \
  --live --confirm-live YES --keypair ~/wallets/mrv2.json \
  --sell-wallet "$(solana-keygen pubkey ~/wallets/padre-sol-1.json)" \
  --ref-mcap 175000 --ref-mcap-end 200000 --ref-ramp-end 12h \
  --start-cooldown 90 \
  --budget 500 --prefer-dex pumpswap --budget-mode wallet \
  --buy-response freq --base-clip 1.0 --min-cooldown 20 --ladder "$FREQ" \
  --cooldown 180 --cooldown-jitter 0.30 --poll-jitter 0.5 \
  --max-clip 1.2 --max-pool-frac 0.025 --target-impact 0.02 \
  --max-per-hour 12 --slippage-bps 400

# sell: fixed 175k (no ramp) — idle until ~189k for +8% first TP
./scripts/botctl start --mint $MINT --side sell --style absorb --run-id sell-absorb-padre \
  … --ref-mcap 175000 --tp-repeat --max-sell-sol 1.0 --max-sell-impact 0.02 …
```

Prove ramp: boot `ref RAMP armed: start_mcap=175000 end_mcap=200000 ends_in=43200s`; heartbeat `ramping=True`, `ref_mcap` ticking up.

Prove no restart clip: `seeded cooldown from last_fill_at=…` and/or `start-cooldown active: 90s`; first status often `above first ladder rung — wait` if dd shallow.

## Why restart always bought a clip

```text
last_trade_ts = 0  →  cooldown check false  →  if dd arms rung → SIGNAL buy
```

Raising buy-ref makes current spot look deeper → restart fire **more** likely, not less. Cooldown seed is mandatory on ref retargets.

## Buy vs sell ref geometry (quick)

| sell vs buy | Spot between refs |
|-------------|-------------------|
| sell < buy | **Both can fire** (overlap churn) |
| sell = buy | Hinge — one side only |
| sell > buy | Hold gap — neither |

Asymmetric live preference often: buy ramps toward higher target; sell fixed lower so distribution waits for strength without matching every buy dip.
