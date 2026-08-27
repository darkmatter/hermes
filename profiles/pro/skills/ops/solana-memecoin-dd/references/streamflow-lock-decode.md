# Streamflow lock decode (Solana)

Program (mainnet timelock): `strmRqUCoQUgGUan5YhzUZa6KqdzwX5L6FpUxfmKg5m`

Layout source: [streamflow-finance/js-sdk `packages/stream/solana/layout.ts`](https://github.com/streamflow-finance/js-sdk/blob/master/packages/stream/solana/layout.ts) — `streamLayout`.

## Create ix accounts (in order)
From `createStreamInstruction`:
0. sender (signer)
1. sender_tokens
2. recipient
3. metadata (stream account; often also signer when keypair)
4. escrow_tokens
5. recipient_tokens
6. streamflow_treasury
7. streamflow_treasury_tokens
8. withdrawor
9. partner
10. partner_tokens
11. mint
12. fee_oracle
13. rent
14. timelock program
15. token program
16. associated token program
17. system program

Pump "dev lock" self-vest: **sender == recipient == creator wallet**. Still a real lock if cancel/transfer flags are 0.

## Create instruction data (after 8-byte Anchor disc)
Little-endian `u64` then bools (see js-sdk `CreateStreamData`):
- `start`
- `depositedAmount` / net
- `period` (seconds)
- `amountPerPeriod`
- `cliff` (unix ts)
- `cliffAmount`
- then bools: `cancelableBySender`, `cancelableByRecipient`, `automaticWithdrawal`, `transferableBySender`, `transferableByRecipient`, `canTopup`, … + name + `withdrawFrequency`

Example (MARV-style 30d full cliff):
- period = 2_592_000 (30d)
- amountPerPeriod = net
- cliff = start + period
- cliffAmount = net
→ single unlock at cliff, not linear drip.

## Metadata account `streamLayout` (packed; version is 1 byte so multi-byte fields after it are **unaligned**)
| Field | Size | Notes |
|---|---|---|
| magic | 8 | often `4` |
| version | 1 | e.g. `4` |
| created_at | 8 | |
| withdrawn_amount | 8 | raw token amount |
| canceled_at | 8 | 0 = not canceled |
| end_time | 8 | |
| last_withdrawn_at | 8 | |
| sender | 32 | |
| sender_tokens | 32 | |
| recipient | 32 | |
| recipient_tokens | 32 | |
| mint | 32 | |
| escrow_tokens | 32 | |
| streamflow_treasury | 32 | |
| streamflow_treasury_tokens | 32 | |
| streamflow_fee_total/withdrawn | 8+8 | |
| streamflow_fee_percent | f32 | |
| partner / partner_tokens | 32+32 | |
| partner_fee_total/withdrawn | 8+8 | |
| partner_fee_percent | f32 | |
| start_time | 8 | |
| net_amount_deposited | 8 | |
| period | 8 | |
| amount_per_period | 8 | |
| cliff | 8 | |
| cliff_amount | 8 | |
| cancelable_by_sender | u8 | **must be 0** |
| cancelable_by_recipient | u8 | **must be 0** |
| automatic_withdrawal | u8 | |
| transferable_by_sender | u8 | prefer 0 |
| transferable_by_recipient | u8 | |
| can_topup | u8 | |
| stream_name | 64 | |
| withdraw_frequency | 8 | |
| ghost | 4 | |
| pausable | u8 | prefer 0 |
| can_update_rate | u8 | prefer 0 |
| … padding / closed / pause fields … | | |

Do **not** interpret offsets as if everything were 8-byte aligned after `magic` — `version` is 1 byte.

## Escrow check
`getTokenAccountBalance(escrow_tokens)` should equal `net_amount_deposited - withdrawn_amount` (raw). If escrow empties early while `canceled_at=0` and before cliff, re-read metadata (withdraw vs cancel).

## Deep links
- Solscan account: `https://solscan.io/account/<metadata>`
- Solscan tx: `https://solscan.io/tx/<sig>`
- Streamflow UI: `https://app.streamflow.finance/contract/solana/mainnet/<metadata>`

## Minimal decode strategy (no solders required)
1. `getSignaturesForAddress(creator)` → find ix to Streamflow program
2. `getTransaction(sig, jsonParsed)` → pull metadata + escrow pubkeys + token transfer amount
3. `getAccountInfo(metadata, base64)` → walk layout with unaligned `u64`/`pubkey` reads
4. `getTokenAccountBalance(escrow)` → confirm funds still locked
5. Report flags explicitly; never summarize inventively as "locked" if cancelable
