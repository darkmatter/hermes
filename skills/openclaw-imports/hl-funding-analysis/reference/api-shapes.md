# Hyperliquid info API shapes used by this skill

Reference for the endpoints used by `funding_history.py`. Useful when extending the script or debugging.

## Base URL

`https://api.hyperliquid.xyz/info` (POST, JSON body)

## Endpoints

### `metaAndAssetCtxs`

Returns universe + current state for all perps.

**Request:** `{"type": "metaAndAssetCtxs"}`

**Response shape:**

```json
[
  { "universe": [{"name": "BTC", "szDecimals": 5, "maxLeverage": 40, ...}, ...] },
  [
    {
      "funding": "0.0000038602",       // hourly funding rate, signed decimal
      "openInterest": "25741.99",      // base asset units
      "prevDayPx": "74995.0",
      "dayNtlVlm": "2275771428.87",    // 24h volume in USD
      "premium": "-0.000447644",
      "oraclePx": "76400.0",
      "markPx": "76361.0",
      "midPx": "76360.5",
      "impactPxs": ["76360.0", "76365.8"],
      "dayBaseVlm": "30058.87"
    },
    ...
  ]
]
```

Indexed by position: `universe[i]` corresponds to `ctxs[i]`.

### `fundingHistory`

Hourly funding rate history per coin.

**Request:** `{"type": "fundingHistory", "coin": "BTC", "startTime": <ms>, "endTime": <ms>}`

**Response shape:**

```json
[
  {
    "coin": "BTC",
    "fundingRate": "-0.0000080086",   // hourly, signed
    "premium": "-0.0005640687",
    "time": 1776160800010              // ms epoch
  },
  ...
]
```

**Important constraints:**
- Maximum 500 records per call (~20.8 days hourly)
- Paginate by setting next call's `startTime` to `last_record.time + 1`
- Stop when chunk returns < 500 records

### `candleSnapshot`

Price candles per coin.

**Request:**
```json
{
  "type": "candleSnapshot",
  "req": {
    "coin": "BTC",
    "interval": "1d",       // or "1h", "5m", etc.
    "startTime": <ms>,
    "endTime": <ms>
  }
}
```

**Response shape:**

```json
[
  {
    "T": 1776160800000,    // close time
    "c": "76361.0",        // close
    "h": "76500.0",        // high
    "l": "76000.0",        // low
    "n": 1234,             // number of trades
    "o": "76200.0",        // open
    "s": "BTC",            // symbol
    "t": 1776157200000,    // open time
    "v": "100.5"           // volume
  },
  ...
]
```

### `clearinghouseState`

Account state for a user.

**Request:** `{"type": "clearinghouseState", "user": "0x..."}`

**Response shape:** see [HL docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint).

Key fields used by daily reports:
- `marginSummary.accountValue`
- `marginSummary.totalNtlPos`
- `marginSummary.totalMarginUsed`
- `assetPositions[].position.{coin, szi, entryPx, positionValue, unrealizedPnl, returnOnEquity, leverage, marginUsed, cumFunding}`
- `withdrawable`
- `crossMaintenanceMarginUsed`

### `portfolio`

Account NAV and PnL time series.

**Request:** `{"type": "portfolio", "user": "0x..."}`

**Response:** array of `[window_name, data]` pairs where window_name is "day", "week", "month", "allTime", and data contains `accountValueHistory`, `pnlHistory`, `vlm`.

### `spotMeta`

Spot market metadata. Use to verify whether a coin has spot trading.

**Request:** `{"type": "spotMeta"}`

## Rate limiting

- Generous but not infinite
- 3 parallel workers is the safe ceiling for sustained scraping
- Implement exponential backoff specifically for 429 (and 503 with "DNS cache overflow" body)
- Consider caching aggressively: funding history beyond yesterday almost never changes
