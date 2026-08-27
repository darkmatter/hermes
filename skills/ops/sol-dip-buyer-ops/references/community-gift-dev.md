# Community gift to MARV dev (no drop dictatorship)

## When this path applies

Cooper wants to **gift unlocked MARV to the project dev** so *the dev* can airdrop to community. Experiment mindset, **not expecting return**. Agent does **not** dictate drop rules/eligibility — only needs a proved receive wallet.

## Public identity of dev

| Field | Value |
|-------|--------|
| Creator / developer | `T5kYFsDUowtUunXsQYRxF9vNVApryD2wcFQZuRPuq5c` |
| Telegram | `@pepedevsolana` / https://t.me/pepedevsolana |
| X | `@puffbear_` (launch posts) |
| Mint | `6xycyGrZRxXcsAoX722kZwvy9evQEJ69d36puN15pump` (Token-2022) |

## Identity / throwaway

- Desktop Telegram on Studio is often **personal** (`Telegram @ Coop`) — **never** DM project transportation from that account.
- MySudo is **phone-only** (no Mac app in Applications). Flow: MySudo number → Telegram **Add Account** (or second client) on phone → blank profile → DM dev.
- Personal X/TG = doxx. Burner TG is the default when Cooper says stay anon **except** when he explicitly allows revealing top-holder + Streamflow lock (on-chain truth, not legal name).

## On-chain proof before/without social

Proves top holder can pay creator without TG identity:

```bash
PROG=TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb
MINT=6xycyGrZRxXcsAoX722kZwvy9evQEJ69d36puN15pump
DEV=T5kYFsDUowtUunXsQYRxF9vNVApryD2wcFQZuRPuq5c
RPC=$(himitsu exec alchemy-api-key -- sh -c 'k="$ALCHEMY_API_KEY"; case "$k" in http*) echo "$k";; *) echo "https://solana-mainnet.g.alchemy.com/v2/$k";; esac')

spl-token transfer --program-id "$PROG" \
  --owner ~/wallets/padre-sol-1.json --fee-payer ~/wallets/padre-sol-1.json \
  --url "$RPC" --fund-recipient --allow-unfunded-recipient \
  "$MINT" 1 "$DEV"
# report sig + solscan only; never dump keys
```

Example succeeded sig (session): `2zhy5kVPqzPKTzxNWs8m5rRXJR2Vx7D8tQ3yQoVuq5dmt1ZoWowHh9sGhrhLGoS7eVUrVDphfxCoxkFSDj1Uoj4E`.

If full gift follows, optional test **1 MARV** then remainder from unlocked inventory only. Creator may already hold a bag — balance after +1 is not “exactly 1.”

## Message framing (no airdrop terms)

Keep short. Allowed to state: top holder, Streamflow-locked portion (stability signal), experiment / no expected return, gift unlocked MARV for **him** to drop however he wants, agent/user will not run the drop. Sole ask = prove receive wallet (creator OK if he controls it).

Do **not** attach: eligibility lists, vesting schemes, marketing copy, “you must airdrop X way,” bot operational detail, full fleet map.

## What not to build

- Multi-wallet dust holder inflation.
- Open claim farms.
- Agent-driven mass airdrop from Cooper wallets “to grow holders” as a bot feature.

## Related

- Holders ≠ paint bot effect — see SKILL.md “Holders / airdrops / contact”
- Pump homepage is pre-grad; MARV post-grad — `pumpfun-homepage-visibility.md`
