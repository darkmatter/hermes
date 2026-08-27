# Live reference retarget (example)

## When

User: "increase the reference value on both to 150K" (or any new mcap/price) while dual live buys are already running under the same mint.

## What the bot does

On start, if `state.json` already has `ref_price_usd` **and** CLI passes `--ref-mcap` / `--ref-price`:

- `resolve_ref_price` recomputes from live supply
- state + heartbeat updated
- log line: `ref overridden -> price=… mcap=…`
- **spent_sol / fills / level_hits preserved** (no reset)

If neither flag is passed, existing state ref is kept.

## Procedure used (MARV dual paint, 2026-07-30)

Mint: `6xycyGrZRxXcsAoX722kZwvy9evQEJ69d36puN15pump` (`runs/6xycyGrZ/`)

| run_id | keypair | sell-wallet (other hot) |
|--------|---------|-------------------------|
| `buy-paint-padre` | `~/wallets/padre-sol-1.json` → `GKzKZW…` | `PWbrhU…` (marv) |
| `buy-paint-marv` | `~/wallets/marv-dip-buyer.json` → `PWbrhU…` | `GKzKZW…` (padre) |

Before: `--ref-mcap 100000`, dd ~7–8% at mcap ~92k.
After: `--ref-mcap 150000` → ref_px ≈ `0.0001523563`, dd ~38%, both bots **immediately SIGNAL** `-25%` / 4.5 SOL paint clips (spent 88.5→93 and 75→79.5).

Flags kept constant across retarget: `--side buy --style paint --live --confirm-live YES --budget 99 --prefer-dex pumpswap --budget-mode wallet`.

## Verify

```bash
./scripts/botctl list
# heartbeat/state ref_mcap_usd == 150000 on both run dirs
tail -n 30 runs/<m8>/<run_id>/bot.log | rg "ref overridden|SIGNAL|SENT"
```

## User-facing expectation

Always warn: higher ref vs current spot re-arms deeper ladder rungs; paint may fill size on restart before you finish status-checking the second bot. Restart **both** before declaring done when user said "both".
