---
name: dune
description: "Dune CLI for querying blockchain and on-chain data via DuneSQL, searching decoded contract tables, managing saved queries, managing visualizations, managing dashboards, monitoring credit usage on Dune, and real-time wallet/token lookups via the Sim API. Use when user asks about blockchain data, on-chain analytics, token transfers, DEX trades, smart contract events, wallet balances, Ethereum/EVM chain queries, DuneSQL, visualizations, charts, dashboards, wallet balances, token prices, NFT holdings, DeFi positions, transaction history, token holders, stablecoins, or any real-time on-chain data for a specific address. Triggers: 'query Dune', 'search Dune datasets', 'run a Dune query', 'create a dashboard', 'manage dashboard', 'check wallet', 'token balance', 'NFT holdings', 'DeFi positions', 'transaction history', 'token holders', 'token price', 'stablecoin balance', 'wallet activity', or any request involving a blockchain address (0x... or Solana base58)."
compatibility: Requires network access and the Dune CLI (auto-installed on first use). Works on macOS, Linux, and Windows.
allowed-tools: Bash(dune:*) Bash(curl:*) Read
metadata:
  author: duneanalytics
  version: "1.0.0"
  cli_version: "0.1"
---

## Prerequisites

Assume the Dune CLI is already installed and authenticated. **Do not** run upfront install or auth checks. Just execute the requested `dune` command directly.

If a `dune` command fails, inspect the error to determine the cause and follow the recovery steps in [install-and-recovery.md](references/install-and-recovery.md):

- **"command not found"** → CLI not installed. See [CLI Not Found Recovery](references/install-and-recovery.md#cli-not-found-recovery).
- **401 / "unauthorized" / "missing API key"** → Auth failure. See [Authentication Failure Recovery](references/install-and-recovery.md#authentication-failure-recovery).
- **Unknown subcommand or flag / unexpected output** → Possible version mismatch. See [Version Compatibility](references/install-and-recovery.md#version-compatibility).

# Dune CLI

A command-line interface for [Dune](https://dune.com) -- the leading blockchain data platform. Use it to write and execute DuneSQL queries against on-chain data, discover datasets, search documentation, and monitor credit usage.

## Authentication

All commands except `docs search` require authentication via a Dune API key. The key is resolved in this priority order:

```bash
# 1. Flag (highest priority -- overrides everything)
dune query run 12345 --api-key <key>

# 2. Environment variable
export DUNE_API_KEY=<REDACTED>
dune query run 12345

# 3. Saved config file (lowest priority)
dune auth --api-key <key>        # saves to ~/.config/dune/config.yaml
dune query run 12345              # uses saved key
```

To save your key interactively (prompted from stdin):

```bash
dune auth
```

Config file location: `~/.config/dune/config.yaml`

## Global Flags

| Flag | Description |
|------|-------------|
| `--api-key <KEY>` | Dune API key (overrides `DUNE_API_KEY` env var and saved config) |

### Output Format (per-command flag)

Most commands support `-o, --output <FORMAT>` with values `text` (default, human-readable tables) or `json` (machine-readable).

> **Always use `-o json`** on every command that supports it. JSON output contains more detail than `text` (full API response objects vs. summarized tables) and is unambiguous to parse. The `text` format is for human terminal use and drops fields.

## DuneSQL

Dune uses **DuneSQL**, a Trino-based SQL dialect, as its query engine. Key points:

- All SQL passed to `--sql` flags or saved queries must be valid DuneSQL
- DuneSQL supports standard SQL with extensions for blockchain data types (addresses, hashes, etc.)
- See [dunesql-cheatsheet.md](references/dunesql-cheatsheet.md) for common types, functions, patterns, and pitfalls
- Use `dune docs search --query "DuneSQL functions"` to look up syntax and functions
- Reference docs: [Writing Efficient Queries](https://docs.dune.com/query-engine/writing-efficient-queries), [Functions and Operators](https://docs.dune.com/query-engine/Functions-and-operators)

## Key Concepts

### Performance Tiers

Available tiers: `small`, `medium`, `large`. **Do not pass `--performance` by default** — omit it and the API auto-selects. Only provide it when:

- The user explicitly requests a tier
- The query is clearly complex (heavy joins, large aggregations)
- A previous run returned a timeout or resource-limit error

### Execution States

After submitting a query, the execution progresses through these states:

| State | Meaning | Action |
|-------|---------|--------|
| `QUERY_STATE_PENDING` | Queued for execution | Wait |
| `QUERY_STATE_EXECUTING` | Currently running | Wait |
| `QUERY_STATE_COMPLETED` | Results available | Fetch results |
| `QUERY_STATE_FAILED` | Execution failed | Check error message; fix SQL and retry |
| `QUERY_STATE_CANCELLED` | Cancelled by user or system | Re-execute if needed |

### Dataset Categories

| Category | Description |
|----------|-------------|
| `canonical` | Core blockchain data (blocks, transactions, traces, logs) |
| `decoded` | ABI-decoded contract data (events and function calls) |
| `spell` | Dune Spellbook transformations (curated, higher-level tables like `dex.trades`) |
| `community` | Community-contributed datasets |

### Dataset Types

| Type | Description |
|------|-------------|
| `dune_table` | Core Dune-maintained tables |
| `decoded_table` | Contract ABI-decoded tables |
| `spell` | Spellbook transformation tables |
| `uploaded_table` | User-uploaded CSV/data tables |
| `transformation_table` | Materialized transformation tables |
| `transformation_view` | Virtual transformation views |

### Query Parameters

Parameters let you create reusable queries with variable inputs. Pass them as `--param key=value` (repeatable). The API auto-detects the type, but parameters support these types: `text`, `number`, `datetime`, `enum`.

```bash
dune query run 12345 --param wallet=0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 --param days=30 -o json
```

## Command Overview

| Command | Description | Auth |
|---------|-------------|------|
| `dune auth` | Save API key to config file | No |
| `dune query create` | Create a new saved query | Yes |
| `dune query get <id>` | Fetch a saved query's SQL and metadata | Yes |
| `dune query update <id>` | Update an existing query | Yes |
| `dune query archive <id>` | Archive a saved query | Yes |
| `dune query run <id>` | Execute a saved query and wait for results | Yes |
| `dune query run-sql` | Execute raw DuneSQL directly (no saved query needed) | Yes |
| `dune execution results <id>` | Fetch results of a previous execution | Yes |
| `dune dataset search` | Search the Dune dataset catalog | Yes |
| `dune dataset search-by-contract` | Find decoded tables for a contract address | Yes |
| `dune viz create` | Create a visualization on a saved query | Yes |
| `dune viz get <id>` | Fetch visualization details and options | Yes |
| `dune viz list` | List all visualizations for a query | Yes |
| `dune viz update <id>` | Update an existing visualization | Yes |
| `dune viz delete <id>` | Permanently delete a visualization | Yes |
| `dune docs search` | Search Dune documentation | No |
| `dune usage` | Show credit and resource usage | Yes |
| `dune dashboard create` | Create a new dashboard | Yes |
| `dune dashboard get <id>` | Fetch a dashboard's metadata and widgets | Yes |
| `dune dashboard update <id>` | Update an existing dashboard | Yes |
| `dune dashboard archive <id>` | Archive a dashboard | Yes |

## Common Workflows

### Ad-hoc SQL Analysis

```bash
# Run a one-off query directly
dune query run-sql --sql "SELECT block_number, block_time FROM ethereum.blocks ORDER BY block_number DESC LIMIT 5" -o json
```

### Discover Tables, Then Query

```bash
# 1. Find relevant tables with column schemas
dune dataset search --query "uniswap swaps" --categories decoded --include-schema -o json

# 2. Write and execute SQL using discovered table/column names
dune query run-sql --sql "SELECT * FROM uniswap_v3_ethereum.evt_Swap LIMIT 10" -o json
```

### Find Contract Tables, Then Query

```bash
# 1. Find decoded tables for a specific contract
dune dataset search-by-contract --contract-address 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984 --include-schema -o json

# 2. Query the discovered tables
dune query run-sql --sql "SELECT * FROM uniswap_v3_ethereum.evt_Transfer LIMIT 10" -o json
```

### Save and Execute a Reusable Query

```bash
# 1. Create a saved query with parameters
dune query create --name "Top Wallets" --sql "SELECT address, balance FROM ethereum.balances WHERE balance > {{min_balance}} LIMIT {{row_limit}}" -o json

# 2. Run it with parameter values
dune query run <returned-id> --param min_balance=1000 --param row_limit=50 -o json
```

### Long-Running Query (Submit and Poll)

```bash
# 1. Submit without waiting
dune query run 12345 --no-wait --performance large -o json
# Output: {"execution_id": "01ABC...", "state": "QUERY_STATE_PENDING"}

# 2. Check results later
dune execution results 01ABC... -o json
```

### Build a Dashboard from Scratch

```bash
# 1. Create queries for each section
QUERY_ID=$(dune query create --name "Daily Volume" --sql "SELECT date_trunc('day', block_time) AS day, SUM(amount) AS volume FROM trades GROUP BY 1 ORDER BY 1" -o json | jq -r '.query_id')

# 2. Execute to verify data
dune query run $QUERY_ID -o json

# 3. Create visualizations for each query
VIZ_ID=$(dune viz create --query-id $QUERY_ID --name "Daily Volume Chart" --type chart --options '{"globalSeriesType":"line","columnMapping":{"day":"x","volume":"y"}}' -o json | jq -r '.id')

# 4. Assemble the dashboard
dune dashboard create --name "Trading Dashboard" \
  --text-widgets '[{"text":"# Trading Dashboard\nDaily volume and metrics"}]' \
  --visualization-ids $VIZ_ID -o json
```

### Update a Dashboard (Preserve Existing Widgets)

```bash
# 1. Fetch current state
dune dashboard get 12345 -o json > dashboard.json

# 2. Modify as needed (add a new visualization widget)
# 3. Pass the complete widget state back
dune dashboard update 12345 \
  --visualization-widgets '[{"visualization_id":111},{"visualization_id":222},{"visualization_id":333}]' \
  -o json
```

## labels.ens Table (ENS Name Resolution)

The `labels.ens` table maps Ethereum addresses to ENS names (~1.2M rows). Key pitfalls:

- **Only second-level .eth names are reliably indexed** — subdomains like `*.drkmttr.dev` or `sub.example.eth` are often NOT in this table. Only names like `vitalik.eth`, `drkmttr.eth` appear. Always verify before relying on subdomain patterns.
- **Always include a name filter** — `SELECT * FROM labels.ens LIMIT N` returns 0 rows. Use `WHERE name LIKE 'vitalik%'` or similar to get results.
- **`blockchain` column behavior is inconsistent** — some filtered queries return empty results even with matching data. If a query with `WHERE blockchain = 'ethereum'` returns 0 rows, try removing the blockchain filter or restructuring the query.
- **Schema:** `blockchain, address, name, category, contributor, source, created_at, updated_at, model_name, label_type`

When you need to resolve wallets by ENS subdomain pattern, ask the user for a specific address list or check if they maintain an address book elsewhere (dbt seed, CSV, etc.).

## JSON Result Structure

When using `-o json` with `dune query run-sql`, result rows are at **`result.rows`** in the JSON output, NOT top-level `rows`. The full structure is:

```json
{
  "query_id": 0,
  "state": "QUERY_STATE_COMPLETED",
  "result": {
    "metadata": { "column_names": [...], "row_count": N },
    "rows": [ { "col_a": "val", ... }, ... ]
  }
}
```

Always parse `data["result"]["rows"]` when programmatically consuming output.

## Darkmatter Labs dbt Pipeline

When working in the darkmatter context, prefer querying the team's dbt pipeline tables over raw decoded events. These tables are in the `dune` catalog:

```
dune.darkmatterlabs.stg_address_book     -- Known wallet labels, types, notes
dune.darkmatterlabs.fct_matched_txs      -- Full classified LP transaction ledger
dune.darkmatterlabs.fct_earnings_by_pool -- Per-pool PnL, earnings, APR
```

**Catalog prefix is mandatory** — queries must use `dune.darkmatterlabs.{table}` (three-part naming). Two-part names like `darkmatterlabs.fct_matched_txs` will not resolve. The `information_schema` may not list these tables, but direct `SELECT` queries work.

The address book (sourced from `seeds/address_book.csv` in the dbt project at `~/git/darkmatter/dune/`) tracks ~20 wallets with labels like `alpha.drkmttr.eth`, `orbit.drkmttr.eth`, etc. Use `stg_address_book WHERE type = 'wallet'` to filter to LP wallets.

### LP Position Tracking Digest Pattern

When building a daily LP activity digest for tracked wallets:

1. **Show performance per wallet per day, NOT per pool.** Group by `wallet_label` and `blockchain`, aggregating deposits, withdrawals, fees, rewards, gas, and net flow. Users think about their wallets first, pools second.
2. Use `fct_matched_txs` for activity events (filtered by `stg_address_book` wallets, excluding `UNKNOWN`/`internal_transfer`/`transfer` actions).
3. Use `fct_earnings_by_pool` only as supplementary context for specific pools a wallet is active in — never as the primary digest grouping.
4. Filter on `block_date >= CURRENT_DATE - INTERVAL '1' DAY` for 24h windows.
5. See [darkmatter-labs-pipeline.md](references/darkmatter-labs-pipeline.md) for full table schemas.

## Sim API (Real-Time Wallet & Token Lookups)

The `dune sim` subcommand provides instant, pre-indexed blockchain data via
the [Dune Sim API](https://sim.dune.com). Unlike DuneSQL (which runs custom
SQL queries), Sim returns current-state data for specific wallets or tokens
without executing a query.

### When to Use Sim vs DuneSQL

| Use Case | Tool | Why |
|----------|------|-----|
| Wallet token balances | `dune sim evm balances` | Instant, multi-chain, includes USD prices |
| Recent wallet activity | `dune sim evm activity` | Pre-decoded, classified (sends, swaps, etc.) |
| Token price / metadata | `dune sim evm token-info` | Real-time pricing from DEX pools |
| NFT holdings | `dune sim evm collectibles` | Includes spam filtering and metadata |
| Token holder leaderboard | `dune sim evm token-holders` | Pre-ranked by balance |
| DeFi positions | `dune sim evm defi-positions` | Cross-protocol aggregation |
| Solana wallet balances | `dune sim svm balances` | SPL token balances with USD values |
| Custom SQL analytics | `dune query run-sql` | Full DuneSQL power, historical data, aggregations |
| Cross-table joins | `dune query run-sql` | Sim API returns single-entity data |
| Historical time-series | `dune query run-sql` | Sim API returns current state, not historical |

**Rule of thumb:** If the user wants current data about a specific wallet or
token address, use `dune sim`. If they need custom analytics, historical
trends, or aggregations across many addresses, use `dune query run-sql`.

### Sim API Authentication

Sim API commands require a **Sim API key** (separate from the Dune API key).
Resolution priority: `--sim-api-key` flag → `DUNE_SIM_API_KEY` env var →
saved config (`dune sim auth`). Never pass `--sim-api-key` on the command line.

For Sim API auth recovery, see [sim-install-and-recovery.md](references/sim-install-and-recovery.md).

### Sim Command Overview

| Command | Description | Auth |
|---------|-------------|------|
| `dune sim auth` | Save Sim API key to config | No |
| `dune sim evm supported-chains` | List supported EVM chains | No |
| `dune sim evm balances <addr>` | Native + ERC20 balances with USD values | Yes |
| `dune sim evm balance <addr>` | Single-token balance on one chain | Yes |
| `dune sim evm stablecoins <addr>` | Stablecoin-only balances | Yes |
| `dune sim evm activity <addr>` | Decoded activity feed (transfers, swaps, approvals) | Yes |
| `dune sim evm transactions <addr>` | Raw transaction history with optional ABI decoding | Yes |
| `dune sim evm collectibles <addr>` | ERC721/ERC1155 NFT holdings with spam filtering | Yes |
| `dune sim evm token-info <addr>` | Token metadata, price, supply, market cap | Yes |
| `dune sim evm token-holders <addr>` | Top holders of an ERC20 token ranked by balance | Yes |
| `dune sim evm defi-positions <addr>` | DeFi positions across lending, AMM, vault protocols | Yes |
| `dune sim evm supported-protocols` | DeFi protocol families and chains supported | Yes |
| `dune sim svm balances <addr>` | SPL token balances on Solana/Eclipse (beta) | Yes |
| `dune sim svm transactions <addr>` | Solana transaction history (beta) | Yes |

Always use `-o json` for machine-readable output. Most commands support
pagination via `--offset` using the `next_offset` field from the previous response.

### Sim Reference Documents

| Task | Reference |
|------|-----------|
| Sim CLI install, Sim auth recovery, version checks | [sim-install-and-recovery.md](references/sim-install-and-recovery.md) |
| Token balances (multi-token, single-token, stablecoins) | [evm-balances.md](references/evm-balances.md) |
| Wallet activity feed (transfers, swaps, approvals, calls) | [evm-activity.md](references/evm-activity.md) |
| Raw transaction history and ABI decoding | [evm-transactions.md](references/evm-transactions.md) |
| NFT collectibles and spam filtering | [evm-collectibles.md](references/evm-collectibles.md) |
| Token metadata, pricing, and holder leaderboards | [evm-tokens.md](references/evm-tokens.md) |
| DeFi positions (lending, AMM, vaults) | [evm-defi.md](references/evm-defi.md) |
| SVM (Solana, Eclipse) balances and transactions | [svm-commands.md](references/svm-commands.md) |

### Sim Limitations

Sim provides **pre-indexed, real-time data** for specific endpoints. It does
**not** support: custom SQL queries (use `dune query run-sql`), historical
time-series (Sim returns current state only), cross-address aggregations
(Sim queries one address at a time), or write operations (Sim is read-only).

## Limitations

The following capabilities are available via the Dune MCP server or web UI but **not** via the CLI:

- **Blockchain listing** (list all indexed blockchains with table counts)
- **Table size analysis** (storage size of specific tables)

## Security

- **Never** output API keys or tokens in responses. Before presenting CLI output to the user, scan for strings that look like API keys (e.g. long alphanumeric tokens, strings prefixed with `dune_`, or values from `DUNE_API_KEY`). Redact them with `[REDACTED]`.
- **Always** confirm with the user before running write commands (`query create`, `query update`, `query archive`, `viz create`, `viz update`, `viz delete`, `dashboard create`, `dashboard update`, `dashboard archive`)
- **Always** use `-o json` on every command -- JSON output is more detailed and reliably parseable
- Use `--temp` when creating throwaway queries to avoid cluttering the user's saved queries
- **Never** pass `--api-key` on the command line when other users might see the terminal history. Prefer `dune auth` or the `DUNE_API_KEY` environment variable.

## Reference Documents

Load the relevant reference when you need detailed command syntax and flags:

| Task | Reference |
|------|-----------|
| Create, get, update, or archive saved queries | [query-management.md](references/query-management.md) |
| Execute queries (run, run-sql) or fetch execution results | [query-execution.md](references/query-execution.md) |
| Search datasets or find tables for a contract address | [dataset-discovery.md](references/dataset-discovery.md) |
| Search documentation or check account usage | [docs-and-usage.md](references/docs-and-usage.md) |
| DuneSQL types, functions, common patterns, and pitfalls | [dunesql-cheatsheet.md](references/dunesql-cheatsheet.md) |
| Create, get, update, delete, or list visualizations on saved queries | [visualization-management.md](references/visualization-management.md) |
| Create, get, update, or archive dashboards | [dashboard-management.md](references/dashboard-management.md) |
| CLI install, authentication, and version recovery | [install-and-recovery.md](references/install-and-recovery.md) |
| Darkmatter Labs dbt pipeline tables and schemas | [darkmatter-labs-pipeline.md](references/darkmatter-labs-pipeline.md) |
