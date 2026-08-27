# Endpoints for Solana memecoin DD

Prefer these over Cloudflare-gated explorers from datacenter/server IPs.

## HTTP
| Use | URL |
|---|---|
| Pump coin | `GET https://frontend-api-v3.pump.fun/coins/{mint}` |
| DexScreener | `GET https://api.dexscreener.com/latest/dex/tokens/{mint}` |
| Rugcheck report | `GET https://api.rugcheck.xyz/v1/tokens/{mint}/report` |
| Streamflow UI (human) | `https://app.streamflow.finance/contract/solana/mainnet/{metadata}` |
| Pump.fun page | `https://pump.fun/coin/{mint}` |

### Often broken / avoid as primary
- `frontend-api-v3` paths: `/holders`, `/trades/all/...`, `/coins/user-created-coins/...`, `/replies/...` → 404
- GMGN quotation APIs → Cloudflare 403 from many server IPs
- Solscan HTTP API → Cloudflare block without browser cookies
- Birdeye public without key → 401
- `api.pump.fun` legacy host → flaky

## RPC methods (public mainnet OK with backoff)
- `getAccountInfo(mint|metadata|lpMint, jsonParsed|base64)`
- `getTokenAccountsByOwner(creator, {mint})`
- `getTokenAccountBalance(ata)`
- `getTokenLargestAccounts(mint)` — rate-limited on public RPC
- `getSignaturesForAddress(creator|mint|pool, {limit})`
- `getTransaction(sig, {encoding: jsonParsed, maxSupportedTransactionVersion: 0})`

Default RPC: `https://api.mainnet-beta.solana.com` (or `$SOLANA_RPC_URL`). On 429, sleep ≥0.5–1s between tx fetches.

## Rugcheck fields that matter
- `token.mintAuthority` / `freezeAuthority`
- `token_extensions` (transfer fee, permanent delegate, nonTransferable)
- `topHolders[].owner` + `pct` (pool vs wallets)
- `markets[].marketType` + `lp.lpLockedPct` / `lpUnlocked` / LP mint supply
- `lockers` / `lockerOwners` — **may be empty even when Streamflow exists**; always scan creator txs
- `rugged`, `risks`, `score_normalised`

## Pump-native program ids (recognition only)
- Pump bonding: `6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P`
- Pump AMM (post-grad): `pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA`
- Token-2022: `TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb`
- Streamflow: `strmRqUCoQUgGUan5YhzUZa6KqdzwX5L6FpUxfmKg5m`

Pump CreateV2 often seeds creator with **10_000_000** UI tokens (1% of 1B).
