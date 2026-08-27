# Darkmatter Labs dbt Pipeline

> Tables in the `dune.darkmatterlabs` schema, managed by the dbt project at `~/git/darkmatter/dune/`.
> Always use the three-part name `dune.darkmatterlabs.{table}` — two-part names will not resolve.

---

## Address Book: `stg_address_book`

Known addresses with labels, types, and notes. Sourced from `seeds/address_book.csv`.

| Column | Type | Description |
|--------|------|-------------|
| `address` | VARBINARY | Wallet/contract address |
| `label` | VARCHAR | Human-readable label (e.g., `alpha.drkmttr.eth`) |
| `type` | VARCHAR | `wallet`, `cex`, `router`, `bridge`, `token`, `vault`, `scam`, `funding`, `multisig` |
| `notes` | VARCHAR | Free-text description |

Filter to LP wallets: `WHERE type = 'wallet'`. The `owned_by_us` column exists in the CSV seed but is not propagated to the staging model.

### Wallet Types in the Address Book

- **wallet**: LP positions and personal wallets (`alpha.drkmttr.eth`, `orbit.drkmttr.eth`, `hot.drkmttr.eth`, etc.)
- **cex**: Centralized exchange deposit addresses (Coinbase, Bybit)
- **router**: Protocol routers (Uniswap V3Utils, Velodrome, CoW Swap)
- **bridge**: Cross-chain bridges (Across, Bungee, Circle CCTP, Mayan/Wormhole)
- **token**: Known token contracts (WETH, USDC, AERO)
- **vault**: Lending/staking vaults (Aave, EtherFi, Revert)
- **multisig**: Gnosis Safes (`drkmttr.eth`)
- **funding**: Payable/receivables nexus (`nexus.drkmttr.eth`)

---

## LP Transaction Ledger: `fct_matched_txs`

Full classified LP transaction ledger with USD values, balance deltas, and deposit pricing.

| Column | Type | Description |
|--------|------|-------------|
| `blockchain` | VARCHAR | Chain (e.g., `base`, `ethereum`) |
| `block_date` | DATE | Partition column — always filter on this |
| `block_time` | TIMESTAMP | Block timestamp |
| `tx_hash` | VARBINARY | Transaction hash |
| `tx_url` | VARCHAR | Dune URL for the transaction |
| `evt_index` | BIGINT | Event index (NULL for native ETH transfers) |
| `token_address` | VARBINARY | Token contract address |
| `token_symbol` | VARCHAR | Token symbol |
| `address_from` | VARBINARY | Sender |
| `address_to` | VARBINARY | Recipient |
| `direction` | VARCHAR | `in` or `out` |
| `amount_raw` | UINT256 | Raw token amount |
| `amount_usd` | DOUBLE | USD value at time of event |
| `wallet_address` | VARBINARY | Tracked wallet (from address book) |
| `pool` | VARBINARY | Pool contract address |
| `protocol` | VARCHAR | Protocol name (e.g., `aerodrome`, `uniswap_v3`) |
| `position` | VARCHAR | Position identifier |
| `action` | VARCHAR | **Key field** — see action types below |
| `subtype` | VARCHAR | Sub-classification |
| `from_label` | VARCHAR | Label of sender (from address book) |
| `to_label` | VARCHAR | Label of recipient (from address book) |
| `token_label` | VARCHAR | Label of token (from address book) |
| `pool_label` | VARCHAR | Pool pair label (e.g., `WETH/USDC (1)`) |
| `token_id` | VARCHAR | NFT position token ID |
| `deposit_price_per_raw` | DOUBLE | Price per raw unit at deposit time |
| `balance_usd` | DOUBLE | Signed balance delta (deposits positive, withdrawals negative) |
| `balance_usd_at_cost` | DOUBLE | Balance delta using deposit cost basis |
| `running_balance` | DOUBLE | Cumulative portfolio balance (NULL in incremental; use `--full-refresh`) |
| `running_balance_at_cost` | DOUBLE | Same, at cost basis |

### Action Types

| Action | balance_usd sign | Description |
|--------|-----------------|-------------|
| `deposit` | Positive | Adding liquidity |
| `withdraw` | Negative | Removing liquidity |
| `fee_collect` | Positive | Claiming trading fees |
| `reward_claim` | Positive | Claiming incentive rewards |
| `swap` | Varies (out=negative, in=positive) | Token swap within position |
| `gas` | Negative | Gas costs |
| `transfer` | Zero/neutral | Internal transfers between own wallets |
| `UNKNOWN` | Varies | Unclassified |
| `internal_transfer` | Neutral | Transfer between own addresses |

### Key Query Patterns

```sql
-- Per-wallet daily performance (PREFERRED for digests)
SELECT
  w.label AS wallet_label,
  m.blockchain,
  COUNT(*) AS event_count,
  ROUND(SUM(CASE WHEN m.action = 'deposit' THEN ABS(m.balance_usd) ELSE 0 END), 2) AS deposited_usd,
  ROUND(SUM(CASE WHEN m.action = 'withdraw' THEN ABS(m.balance_usd) ELSE 0 END), 2) AS withdrawn_usd,
  ROUND(SUM(CASE WHEN m.action = 'fee_collect' THEN ABS(m.balance_usd) ELSE 0 END), 2) AS fees_collected_usd,
  ROUND(SUM(CASE WHEN m.action = 'reward_claim' THEN ABS(m.balance_usd) ELSE 0 END), 2) AS rewards_usd,
  ROUND(SUM(m.balance_usd), 2) AS net_flow_usd
FROM dune.darkmatterlabs.fct_matched_txs m
INNER JOIN dune.darkmatterlabs.stg_address_book w ON m.wallet_address = w.address
WHERE w.type = 'wallet'
  AND m.block_date >= CURRENT_DATE - INTERVAL '1' DAY
  AND m.action NOT IN ('UNKNOWN', 'internal_transfer', 'transfer')
GROUP BY w.label, m.blockchain
ORDER BY net_flow_usd DESC;
```

---

## Pool Earnings: `fct_earnings_by_pool`

Per-pool PnL summary with TWAP-based APR calculations.

| Column | Type | Description |
|--------|------|-------------|
| `blockchain` | VARCHAR | Chain |
| `protocol` | VARCHAR | Protocol name |
| `pool` | VARBINARY | Pool address |
| `pool_name` | VARCHAR | Pool pair label (e.g., `USDC/AERO (2000)`) |
| `deposited_usd` | DOUBLE | Total deposited |
| `withdrawn_usd` | DOUBLE | Total withdrawn |
| `fees_usd` | DOUBLE | Total fees collected |
| `rewards_usd` | DOUBLE | Total rewards claimed |
| `gas_usd` | DOUBLE | Total gas spent |
| `swap_usd` | DOUBLE | Net swap value |
| `net_pnl_usd` | DOUBLE | Net PnL (withdrawals - deposits + fees + rewards + swaps) |
| `earnings_usd` | DOUBLE | Fees + rewards only |
| `first_event` | TIMESTAMP | First recorded event |
| `last_event` | TIMESTAMP | Most recent event |
| `days_active` | INTEGER | Days between first and last event |
| `avg_position_usd` | DOUBLE | Time-weighted average position size |
| `days_deployed` | DOUBLE | Days with capital deployed |
| `gross_apr_pct` | DOUBLE | Annualized earnings / avg position |
| `net_apr_pct` | DOUBLE | Annualized net PnL / avg position |

### Important Notes

- `?/?` pool_name means the pool could not be resolved — check the raw `pool` address.
- `gross_apr_pct` and `net_apr_pct` can be NULL if `avg_position_usd` is 0 or `days_deployed` is 0.
- Use as **supplementary** context for specific pools — never as the primary grouping for a digest (group by wallet first).

---

## dbt Project Conventions

- **Catalog prefix**: Always `dune.darkmatterlabs.{table}` for queries from Dune App/API.
- **Incremental models**: `fct_matched_txs` uses delete+insert strategy with a 14-day lookback window.
- **`information_schema`**: May not list `darkmatterlabs` tables, but direct `SELECT` queries work.
- **Running the pipeline**: `cd ~/git/darkmatter/dune && source env.sh && uv run dbt run --target prod`
- **Full refresh**: Only when `running_balance` / `running_balance_at_cost` recomputation is needed. Expensive.
- **Address book updates**: Edit `seeds/address_book.csv`, then `uv run dbt seed --select address_book`.
