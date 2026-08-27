#!/usr/bin/env python3
"""
Emit a single JSON blob for the HL funding live-dashboard artifact.

Companion to ``funding_history.py``: reads the same on-disk cache
(``/tmp/hl_funding_cache.json``) and combines it with a fresh
``metaAndAssetCtxs`` call so the artifact can render a current
market snapshot plus 7d harvest stats without re-paginating the
full funding history on every page load.

Usage:
    python3 dashboard_data.py
    python3 dashboard_data.py --wallet 0xabc...
    python3 dashboard_data.py --min-oi 5 --min-vlm 1

Output: JSON to stdout with shape:
    {
        "asOf": <ms epoch>,
        "errors": [str, ...],
        "cacheCoverage": <int>,           # # of coins in funding cache
        "cacheStaleHours": <float|null>,  # age of newest funding record
        "markets": [
            {
                "coin": "BTC",
                "mark": 76361.0,
                "oiUsd": 1.96e9,
                "dayVlmUsd": 2.27e9,
                "currentApr": 12.4,       # annualized %, signed
                "dayChgPct": -0.7,
                "maxLeverage": 40,
                "window7d": {             # null if no cache
                    "n": 168,
                    "avgApr": 14.1,
                    "cumFundingPct": 0.27,
                    "priceChangePct": -1.2,
                    "shortHarvestPnl": 1.47,
                    "longHarvestPnl": -1.47,
                    "signPct": 0.83
                }
            },
            ...
        ],
        "account": {                       # null if no --wallet
            "wallet": "0x...",
            "value": 12345.67,
            "totalNtlPos": 25000.0,
            "totalMarginUsed": 3000.0,
            "withdrawable": 9000.0,
            "positions": [
                {
                    "coin": "ETH",
                    "side": "LONG",
                    "szi": 1.5,
                    "entry": 3200.0,
                    "mark": 3300.0,        # filled from market snapshot
                    "positionValue": 4950.0,
                    "unrealizedPnl": 150.0,
                    "roe": 0.046875,
                    "leverage": 5,
                    "leverageType": "cross",
                    "marginUsed": 990.0,
                    "cumFundingAllTime": -3.21,
                    "liquidationPx": 2900.0
                },
                ...
            ]
        }
    }
"""
from __future__ import annotations
import argparse
import json
import os
import statistics
import sys
import time
import urllib.request

API = "https://api.hyperliquid.xyz/info"
HOURS_PER_YEAR = 24 * 365
FUNDING_CACHE = "/tmp/hl_funding_cache.json"
PRICE_CACHE = "/tmp/hl_price_cache.json"


def post(payload: dict, retries: int = 4) -> dict | list:
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        API, data=body, headers={"Content-Type": "application/json"}
    )
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read())
        except Exception as e:  # noqa: BLE001
            last_exc = e
            if attempt == retries - 1:
                break
            time.sleep(2**attempt)
    raise RuntimeError(f"POST {payload.get('type')} failed: {last_exc}")


def load_cache(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return {}


def compute_window(
    funding_records: list[dict],
    price_records: list[dict],
    days: int,
    now_ms: int,
) -> dict | None:
    cutoff = now_ms - days * 86400 * 1000
    fw = [r for r in funding_records if r.get("t", 0) >= cutoff]
    if len(fw) < 24:
        return None
    rates = [r["r"] for r in fw]
    avg_apr = statistics.mean(rates) * HOURS_PER_YEAR * 100
    cum = sum(rates) * 100
    pos = sum(1 for r in rates if r > 0)
    neg = sum(1 for r in rates if r < 0)
    sign_pct = max(pos, neg) / len(rates) if rates else 0.0

    price_change_pct = None
    if price_records:
        pw = [p for p in price_records if p.get("t", 0) >= cutoff]
        if len(pw) >= 2:
            start_px, end_px = pw[0]["c"], pw[-1]["c"]
            if start_px:
                price_change_pct = (end_px - start_px) / start_px * 100

    short_pnl = None
    long_pnl = None
    if price_change_pct is not None:
        short_pnl = cum - price_change_pct
        long_pnl = -cum + price_change_pct

    return {
        "n": len(rates),
        "avgApr": avg_apr,
        "cumFundingPct": cum,
        "priceChangePct": price_change_pct,
        "shortHarvestPnl": short_pnl,
        "longHarvestPnl": long_pnl,
        "signPct": sign_pct,
    }


def cache_stale_hours(funding_cache: dict, now_ms: int) -> float | None:
    newest = 0
    for records in funding_cache.values():
        if records:
            t = records[-1].get("t", 0)
            if t > newest:
                newest = t
    if not newest:
        return None
    return (now_ms - newest) / 3_600_000


def build_markets(
    meta_ctx,
    funding_cache: dict,
    price_cache: dict,
    min_oi_m: float,
    min_vlm_m: float,
) -> list[dict]:
    meta, ctxs = meta_ctx[0], meta_ctx[1]
    now_ms = int(time.time() * 1000)
    rows: list[dict] = []
    for asset, ctx in zip(meta["universe"], ctxs):
        try:
            mark = float(ctx["markPx"])
            oi_usd = float(ctx["openInterest"]) * mark
            day_vlm = float(ctx["dayNtlVlm"])
            current_apr = float(ctx["funding"]) * HOURS_PER_YEAR * 100
            prev_day_px = float(ctx.get("prevDayPx") or 0)
        except (TypeError, ValueError, KeyError):
            continue

        if oi_usd < min_oi_m * 1e6 or day_vlm < min_vlm_m * 1e6:
            continue

        day_chg = (mark - prev_day_px) / prev_day_px * 100 if prev_day_px else 0.0

        coin = asset["name"]
        recs = funding_cache.get(coin, [])
        prices = price_cache.get(coin, [])
        window7d = compute_window(recs, prices, 7, now_ms) if recs else None

        rows.append(
            {
                "coin": coin,
                "mark": mark,
                "oiUsd": oi_usd,
                "dayVlmUsd": day_vlm,
                "currentApr": current_apr,
                "dayChgPct": day_chg,
                "maxLeverage": asset.get("maxLeverage"),
                "window7d": window7d,
            }
        )

    rows.sort(key=lambda r: abs(r["currentApr"]), reverse=True)
    return rows


def build_account(wallet: str, mark_lookup: dict[str, float]) -> dict:
    state = post({"type": "clearinghouseState", "user": wallet})
    ms = state.get("marginSummary", {}) or {}
    out = {
        "wallet": wallet,
        "value": float(ms.get("accountValue", 0) or 0),
        "totalNtlPos": float(ms.get("totalNtlPos", 0) or 0),
        "totalMarginUsed": float(ms.get("totalMarginUsed", 0) or 0),
        "withdrawable": float(state.get("withdrawable", 0) or 0),
        "positions": [],
    }
    for ap_pos in state.get("assetPositions", []) or []:
        p = ap_pos.get("position") or {}
        try:
            szi = float(p.get("szi", 0) or 0)
        except (TypeError, ValueError):
            continue
        if szi == 0:
            continue
        leverage = p.get("leverage") or {}
        cum_funding = p.get("cumFunding") or {}
        liq = p.get("liquidationPx")
        coin = p.get("coin", "")
        try:
            entry = float(p.get("entryPx", 0) or 0)
        except (TypeError, ValueError):
            entry = 0.0
        try:
            position_value = float(p.get("positionValue", 0) or 0)
        except (TypeError, ValueError):
            position_value = 0.0
        try:
            upnl = float(p.get("unrealizedPnl", 0) or 0)
        except (TypeError, ValueError):
            upnl = 0.0
        try:
            roe = float(p.get("returnOnEquity", 0) or 0)
        except (TypeError, ValueError):
            roe = 0.0
        try:
            margin_used = float(p.get("marginUsed", 0) or 0)
        except (TypeError, ValueError):
            margin_used = 0.0
        try:
            lev_value = float(leverage.get("value", 0) or 0)
        except (TypeError, ValueError):
            lev_value = 0.0
        try:
            cum_all = float(cum_funding.get("allTime", 0) or 0)
        except (TypeError, ValueError):
            cum_all = 0.0
        try:
            liq_px = float(liq) if liq not in (None, "") else None
        except (TypeError, ValueError):
            liq_px = None

        out["positions"].append(
            {
                "coin": coin,
                "side": "LONG" if szi > 0 else "SHORT",
                "szi": szi,
                "entry": entry,
                "mark": mark_lookup.get(coin),
                "positionValue": position_value,
                "unrealizedPnl": upnl,
                "roe": roe,
                "leverage": lev_value,
                "leverageType": leverage.get("type"),
                "marginUsed": margin_used,
                "cumFundingAllTime": cum_all,
                "liquidationPx": liq_px,
            }
        )
    out["positions"].sort(key=lambda p: abs(p["positionValue"]), reverse=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--wallet", default=None, help="public wallet address (read-only)")
    ap.add_argument("--min-oi", type=float, default=3.0, help="min OI in $M")
    ap.add_argument("--min-vlm", type=float, default=0.3, help="min 24h vol in $M")
    args = ap.parse_args()

    out: dict = {
        "asOf": int(time.time() * 1000),
        "errors": [],
        "markets": [],
        "account": None,
    }

    funding_cache = load_cache(FUNDING_CACHE)
    price_cache = load_cache(PRICE_CACHE)
    out["cacheCoverage"] = len(funding_cache)
    out["cacheStaleHours"] = cache_stale_hours(funding_cache, out["asOf"])

    try:
        meta_ctx = post({"type": "metaAndAssetCtxs"})
        out["markets"] = build_markets(
            meta_ctx, funding_cache, price_cache, args.min_oi, args.min_vlm
        )
    except Exception as e:  # noqa: BLE001
        out["errors"].append(f"market data: {e}")

    if args.wallet:
        try:
            mark_lookup = {m["coin"]: m["mark"] for m in out["markets"]}
            out["account"] = build_account(args.wallet, mark_lookup)
        except Exception as e:  # noqa: BLE001
            out["errors"].append(f"account: {e}")

    json.dump(out, sys.stdout, default=str)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
