# Gentle sell TP (padre bag)

## Stock facts

- TP: `gain:frac` of **current on-chain bag**; each gain key once (`tp_hits`).
- Default ladder `(0.25,0.25),(0.50,0.35),(1.0,0.40)` → ~29% residual if all fire.
- `--stop-loss` dumps remainder (priority over TP); not gentle.
- `bag_empty` only when wallet tokens ~0 — TP alone rarely gets there.
- Styles (`absorb`/`normal`/`paint`) mainly tune clip/hour/CD/impact metadata; **frac × bag** drives sell size.

## “Sell soon” + still gentle

Sell ref independent of buy ref. Example that fired immediately while buys sat on 150k:

```bash
./scripts/botctl start --mint $MINT --side sell --style absorb --run-id sell-absorb-padre \
  --live --confirm-live YES \
  --keypair ~/wallets/padre-sol-1.json \
  --buy-wallet AZYsGo7nqXamo1PSvsCdsbyiQ2SNUrd2SVCiwTo22pyY \
  --ref-mcap 120000 \
  --tp-ladder '0.08:0.04,0.15:0.05,0.25:0.06,0.40:0.08,0.60:0.10,1.0:0.12' \
  --sell-frac-cap 0.08 \
  --max-clip 3 --max-pool-frac 0.02 --target-impact 0.015 \
  --max-per-hour 8 --cooldown 120 --slippage-bps 300 \
  --min-sell-tokens 1000 --prefer-dex pumpswap
```

Lesson: **4% of ~600M MARV** still ~**20% quote impact** on ~170 SOL pool. For true gentle, start **1–2%** fracs (or lower) on fat bags; watch first quote `impact=` before walking away.

## Full exit options

| Approach | Fully exits? |
|----------|--------------|
| Default/gentle TP only | No |
| Final rung `…,X:1.0` (+ no tiny frac-cap) when gain tags | Yes once |
| Dense ladder grinding bag → dust | Effectively if every rung hits |
| `--stop-loss` dump | Yes on way down |
| Manual restart + dump rung/transfer | Yes with ops |

Tell Cooper residual remains unless one of the yes paths is chosen.
