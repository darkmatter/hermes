# sol-dip-buyer ops cheat sheet

Path: `~/git/darkmatter/sol-dip-buyer/`
Wallet (Padre / himitsu `sol-1`): materialize → `~/wallets/padre-sol-1.json`
Pubkey (do not rotate casually): `GKzKZWPbCBZsSC22Neabbowiz5LdbBgs98uwticafXjy`

## Detached only for live

```bash
cd ~/git/darkmatter/sol-dip-buyer
export DIP_BUYER_KEYPAIR=~/wallets/padre-sol-1.json
export SOLANA_RPC_URL="${SOLANA_RPC_URL:-https://api.mainnet-beta.solana.com}"

# stop first if already running
./scripts/botctl stop --mint <MINT>

./scripts/botctl start \
  --mint <MINT> \
  --live --confirm-live YES \
  --style paint \
  --ref-mcap 100000 \
  --budget <REMAINING_SOL> \
  --prefer-dex pumpswap \
  --keypair "$DIP_BUYER_KEYPAIR" \
  --rpc "$SOLANA_RPC_URL" \
  --target-impact 0.08 \
  --max-pool-frac 0.12 \
  --cooldown 30 \
  --poll 5

./scripts/botctl status --mint <MINT>
./scripts/botctl logs --mint <MINT> -f
./scripts/monitor_check.py --mint <MINT>   # cron: non-zero = bad
./scripts/botctl stop --mint <MINT>
```

Prelude shell (optional DX): `nix develop` then `menu` / `x bot:live-help`.

## Why price isn't moving (order)

1. Process stopped? `botctl status` / `pgrep -fl dip_buyer`
2. Mode paper? Must be `--live --confirm-live YES`
3. Spot still above first rung (−8% paint) relative to **ref**?
4. Cooldown / `--max-per-hour` / budget exhausted?
5. Impact too small? Raise `--target-impact`, `--max-pool-frac`, `--max-clip`; lower `--cooldown`

**Dip ladder ≠ continuous bid-up.** Above ref / first rung → idle by design.

## Clip vs budget vs paint

| Term | Meaning |
|------|---------|
| Budget | Max total SOL over the whole run |
| Clip | SOL in **one** swap |
| Paint size | `min(ladder_base, max_clip, pool×frac, impact_target_sol, remaining, hour_left)` |
| Impact target | `pool_sol * (sqrt(1+i) - 1)` approx |

Paint defaults (tunable): pool-frac 0.10–0.12, target-impact ~0.06–0.08, cooldown 30–45s, max-per-hour 35.

## Ref as mcap

`--ref-mcap 100000` → ref USD via live supply (`mcap/price`, else 1B).
If live mcap ≪ 100k, dd stays huge → deepest rung every cooldown until caps. Confirm with user.

## State layout

- New: `runs/<mint8>/{state,trades,bot.log,bot.pid,bot.lock,heartbeat.json}`
- Legacy root `live-state.json` / `live-trades.csv` may hold older fills — don't mix without intent
- Mint mismatch in state file → bot refuses; new mint = new run dir

## Refuse

Multi-wallet funder + split + coordinated buys. Single hot wallet only.

## Refresh market packets

```bash
curl -sS "https://frontend-api-v3.pump.fun/coins/$MINT"
curl -sS "https://api.dexscreener.com/latest/dex/tokens/$MINT"
curl -sS "https://api.rugcheck.xyz/v1/tokens/$MINT/report"
```
