# Wallet roster + buy-run sell-wallet semantics

Re-verify with `solana-keygen pubkey` before ops.

## Active keys (`~/wallets/`)

| File | Pubkey | Role | Typical run_id |
|------|--------|------|----------------|
| `mrv2.json` | `A3KwFS1rnfkSLFtpEdBqryAdjZUSxJFQrJjwUuk1Es19` | soft-paint **buy** (main dry powder when sisters empty) | `buy-paint-mrv2` |
| `mrv.json` | `AZYsGo7nqXamo1PSvsCdsbyiQ2SNUrd2SVCiwTo22pyY` | soft-paint **buy** (may sit near fee dust) | `buy-paint-marv` |
| `marv-dip-buyer.json` | `PWbrhUi24NnCf1MieqTauJ8qH6wEqgjtjTAdupFis5U` | soft-paint **buy** (mid SOL) | `buy-paint-dip` |
| `padre-sol-1.json` | `GKzKZWPbCBZsSC22Neabbowiz5LdbBgs98uwticafXjy` | **sell** bag | `sell-absorb-padre` |

Import path: base58 in `/tmp/*` → 64-int JSON `600` → wipe `/tmp` source. Dedup by pubkey against existing files (same base58 hit twice as `/tmp/key` + `/tmp/mrv`). Name by source when Cooper says so (`/tmp/mrv2` → `mrv2.json`).

## Multi-buyer start for a new hot (`mrv2`-class)

Same profile as current fleet lead — do not invent a hotter paint:

```bash
FREQ='0.15:150,0.25:90,0.40:60,0.55:40,0.70:25'
./scripts/botctl start --mint $MINT --side buy --style paint --run-id buy-paint-mrv2 \
  --live --confirm-live YES --keypair ~/wallets/mrv2.json \
  --sell-wallet "$(solana-keygen pubkey ~/wallets/padre-sol-1.json)" \
  --ref-mcap 175000 --budget 500 --prefer-dex pumpswap --budget-mode wallet \
  --buy-response freq --base-clip 1.0 --min-cooldown 20 --ladder "$FREQ" \
  --cooldown 180 --cooldown-jitter 0.30 --poll-jitter 0.5 \
  --max-clip 1.2 --max-pool-frac 0.025 --target-impact 0.02 \
  --max-per-hour 12 --slippage-bps 400
```

Cross-wire `--sell-wallet` to **padre** (the seller), not to another buy sister, once padre is sell-only.

Drained sisters (`wallet_sol ≈ fee_reserve`) can stay up idle or be stopped for less log noise — either is fine; don't restart them hotter without asking.

## `--sell-wallet` is not a sell bot

On `--side buy` runs, `--sell-wallet <PUB>` is only:

1. Annotation for dual/cross-wire docs in heartbeat
2. Hard guard so buy pubkey ≠ annotated opposite

Proof you are **not** selling: `side=buy`, `tokens_sold=0`, no process with `--side sell`, `received_sol` not climbing from sells.

## Flip buy → sell same pubkey (padre)

1. `botctl stop --mint $M --run-id buy-paint-padre`
2. Null `wallet` on that run’s `heartbeat.json` — sibling scan includes **stopped** hearts
3. Start `sell-absorb-padre` with `--side sell --keypair padre --buy-wallet <active buyer pub>` (often mrv2 or mrv)
4. Prove: HB `side=sell`; buyers still `side=buy`

## Balance answers Cooper expects

Report **all hot addrs** unless asked for one:

1. On-chain SOL (`solana balance` / Alchemy RPC)
2. On-chain token UI for the mint
3. Per-run bot counters: `spent_sol`, `budget`, HB `wallet_sol`, status (`wallet_low` with SOL left = hard ceiling ≤ spent, not empty chain)

Don't equate “51 SOL on padre” with “can still buy” if `spent_sol >= budget` or side is sell. Run spoent survives keypair/ref swaps.
