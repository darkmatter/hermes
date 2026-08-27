#!/usr/bin/env python3
"""
Hyperliquid funding history analyzer.

Builds a local cache of funding rate history + daily price data for all HL perps,
then analyzes each candidate across multiple time windows (7d/30d/60d/90d) to
answer the question that matters:

    If I had held this funding-harvest trade for the window, what would I have
    actually made, net of price movement in the underlying?

Because a 100% APR short where the token 2x'd is a catastrophic loss, not a win.

Modes:
    --sync           Incrementally update cache with latest data (run daily)
    --deep-sync N    Backfill N days of history (run once, then --sync daily)
    --report         (default) Analyze cached data, show top opportunities

Cache:
    /tmp/hl_funding_cache.json  (funding rates)
    /tmp/hl_price_cache.json    (daily closes)

Usage:
    # First run: backfill 90 days
    python funding_history.py --deep-sync 90

    # Daily: update and report
    python funding_history.py --sync

    # Report from cache only (no network)
    python funding_history.py --report

    # Filter to specific windows or min APR
    python funding_history.py --windows 30,60 --min-apr 40
"""

from __future__ import annotations
import argparse
import json
import os
import statistics
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone

API = "https://api.hyperliquid.xyz/info"
HOURS_PER_YEAR = 24 * 365
FUNDING_CACHE = "/tmp/hl_funding_cache.json"
PRICE_CACHE = "/tmp/hl_price_cache.json"
MAX_HISTORY_PER_CALL = 500  # hardcoded HL limit

DEFAULT_EXCLUDE: set[str] = set()  # override per-project with --exclude
DEFAULT_WINDOWS = [7, 30, 60, 90]


def post(payload: dict, retries: int = 6) -> dict | list:
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        API, data=body, headers={"Content-Type": "application/json"}
    )
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                # aggressive backoff on rate limit: 2, 4, 8, 16, 32, 64s
                wait = 2 ** (attempt + 1)
                if attempt == retries - 1:
                    raise
                time.sleep(wait)
                continue
            raise
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(1.0 * (2**attempt))
    raise RuntimeError("unreachable")


def load_cache(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        print(f"cache {path} corrupt ({e}), starting fresh", file=sys.stderr)
        return {}


def save_cache(path: str, data: dict):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f)
    os.replace(tmp, path)


def fetch_funding_chunk(coin: str, start_ms: int, end_ms: int) -> list[dict]:
    return post(
        {
            "type": "fundingHistory",
            "coin": coin,
            "startTime": start_ms,
            "endTime": end_ms,
        }
    )


def fetch_funding_full(coin: str, start_ms: int, end_ms: int) -> list[dict]:
    """Paginate through funding history from start to end, 500 records per call."""
    all_records = []
    cursor = start_ms
    for _ in range(50):  # safety cap: 50 pages = 25000 records ≈ 3 years
        chunk = fetch_funding_chunk(coin, cursor, end_ms)
        if not chunk:
            break
        all_records.extend(chunk)
        if len(chunk) < MAX_HISTORY_PER_CALL:
            break
        # next page starts 1ms after the last record
        cursor = chunk[-1]["time"] + 1
        if cursor >= end_ms:
            break
    return all_records


def fetch_candles(coin: str, interval: str, start_ms: int, end_ms: int) -> list[dict]:
    """Fetch price candles. interval: '1d', '1h', etc."""
    req = {
        "type": "candleSnapshot",
        "req": {
            "coin": coin,
            "interval": interval,
            "startTime": start_ms,
            "endTime": end_ms,
        },
    }
    return post(req)


def sync_funding(coins: list[str], days: int, workers: int = 3) -> dict:
    """
    Pull funding history for all coins, merging with existing cache.
    Only fetches records newer than what's already cached. Checkpoints to
    disk every 20 coins so partial runs aren't lost.
    """
    cache = load_cache(FUNDING_CACHE)
    end_ms = int(time.time() * 1000)
    default_start = end_ms - days * 86400 * 1000

    def _sync_one(coin: str):
        existing = cache.get(coin, [])
        if existing:
            start = max(existing[-1]["t"] + 1, default_start)
        else:
            start = default_start
        if start >= end_ms - 3600_000:  # within last hour, skip
            return coin, existing
        try:
            new = fetch_funding_full(coin, start, end_ms)
        except Exception as e:
            print(f"  ! {coin}: {e}", file=sys.stderr)
            return coin, existing
        # normalize: new records have fundingRate/time; existing have r/t
        new_norm = [{"t": r["time"], "r": float(r["fundingRate"])} for r in new]
        merged = existing + new_norm
        seen = set()
        deduped = []
        for r in sorted(merged, key=lambda x: x["t"]):
            if r["t"] not in seen:
                seen.add(r["t"])
                deduped.append(r)
        cutoff = end_ms - days * 86400 * 1000
        deduped = [r for r in deduped if r["t"] >= cutoff]
        return coin, deduped

    print(
        f"  syncing funding for {len(coins)} coins, {days}d depth "
        f"({workers} workers)...",
        file=sys.stderr,
    )
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(_sync_one, c): c for c in coins}
        for fut in as_completed(futures):
            coin, records = fut.result()
            cache[coin] = records
            done += 1
            if done % 20 == 0:
                save_cache(FUNDING_CACHE, cache)  # checkpoint
                print(f"    {done}/{len(coins)} (checkpointed)", file=sys.stderr)

    save_cache(FUNDING_CACHE, cache)
    return cache


def sync_prices(coins: list[str], days: int, workers: int = 3) -> dict:
    """Pull daily price candles for all coins. Checkpoints every 20 coins."""
    cache = load_cache(PRICE_CACHE)
    end_ms = int(time.time() * 1000)
    start_ms = end_ms - days * 86400 * 1000

    def _sync_one(coin: str):
        try:
            candles = fetch_candles(coin, "1d", start_ms, end_ms)
            return coin, [{"t": c["t"], "c": float(c["c"])} for c in candles]
        except Exception as e:
            print(f"  ! {coin} prices: {e}", file=sys.stderr)
            return coin, cache.get(coin, [])

    print(f"  syncing prices for {len(coins)} coins, {days}d...", file=sys.stderr)
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(_sync_one, c): c for c in coins}
        for fut in as_completed(futures):
            coin, candles = fut.result()
            cache[coin] = candles
            done += 1
            if done % 20 == 0:
                save_cache(PRICE_CACHE, cache)
                print(f"    {done}/{len(coins)} (checkpointed)", file=sys.stderr)

    save_cache(PRICE_CACHE, cache)
    return cache


@dataclass
class WindowStats:
    days: int
    n_intervals: int
    avg_apr: float  # annualized %
    cum_funding_pct: float  # cumulative funding earned by receiver, %
    sign_pct: float  # fraction with favorable sign
    stability: float
    price_change_pct: float  # underlying price Δ over window, %
    max_drawdown_pct: float  # largest drawdown vs starting price
    # Hypothetical P&L for a harvest trade over this window
    # (per $100 notional held continuously)
    short_harvest_pnl: float = 0.0  # shorts: +funding, -price_change
    long_harvest_pnl: float = 0.0  # longs:  +funding, +price_change


def compute_window(
    coin: str, funding: list[dict], prices: list[dict], days: int, now_ms: int
) -> WindowStats | None:
    cutoff = now_ms - days * 86400 * 1000
    f_window = [r for r in funding if r["t"] >= cutoff]
    p_window = [p for p in prices if p["t"] >= cutoff]
    if len(f_window) < 24 or len(p_window) < 2:
        return None

    rates = [r["r"] for r in f_window]
    mean = statistics.mean(rates)
    stdev = statistics.stdev(rates) if len(rates) > 1 else 0.0
    stability = abs(mean) / stdev if stdev > 0 else 0.0
    avg_apr = mean * HOURS_PER_YEAR * 100

    # cumulative funding: sum of hourly rates (this is what a holder actually earns, in %)
    cum_funding_pct = sum(rates) * 100

    # sign consistency — use dominant sign
    pos = sum(1 for r in rates if r > 0)
    neg = sum(1 for r in rates if r < 0)
    sign_pct = max(pos, neg) / len(rates)

    # price analysis
    closes = [p["c"] for p in p_window]
    start_px, end_px = closes[0], closes[-1]
    price_change = (end_px - start_px) / start_px * 100

    # max drawdown as rolling peak
    peak = closes[0]
    max_dd = 0.0
    for c in closes:
        if c > peak:
            peak = c
        dd = (c - peak) / peak * 100
        if dd < max_dd:
            max_dd = dd

    # hypothetical PnL per $100 notional, unleveraged
    # SHORT harvest: +cum_funding (if positive, shorts collect) - price_change
    # LONG harvest: -cum_funding (if negative, longs collect) + price_change
    short_pnl = cum_funding_pct - price_change
    long_pnl = -cum_funding_pct + price_change

    return WindowStats(
        days=days,
        n_intervals=len(rates),
        avg_apr=avg_apr,
        cum_funding_pct=cum_funding_pct,
        sign_pct=sign_pct,
        stability=stability,
        price_change_pct=price_change,
        max_drawdown_pct=max_dd,
        short_harvest_pnl=short_pnl,
        long_harvest_pnl=long_pnl,
    )


@dataclass
class CoinSummary:
    coin: str
    windows: dict[int, WindowStats] = field(default_factory=dict)
    current_apr: float = 0.0
    oi_usd: float = 0.0
    day_vlm: float = 0.0
    mark: float = 0.0
    side: str = ""  # SHORT or LONG
    headline_score: float = 0.0


def score_coin(cs: CoinSummary, primary_window: int) -> float:
    """Rank by actual historical PnL of the harvest trade, not just funding rate."""
    ws = cs.windows.get(primary_window)
    if not ws:
        return -1.0
    if cs.side == "SHORT":
        pnl = ws.short_harvest_pnl
    else:
        pnl = ws.long_harvest_pnl
    # penalize low consistency
    return pnl * ws.sign_pct


def build_report(
    funding_cache: dict,
    price_cache: dict,
    current_ctx: dict,
    windows: list[int],
    exclude: set[str],
    min_apr: float,
    top: int,
) -> tuple[list[CoinSummary], list[CoinSummary]]:
    now_ms = int(time.time() * 1000)

    shorts, longs = [], []
    for coin, records in funding_cache.items():
        if coin in exclude or not records:
            continue
        prices = price_cache.get(coin, [])
        if not prices:
            continue

        # compute stats for each window
        wins = {}
        for w in windows:
            ws = compute_window(coin, records, prices, w, now_ms)
            if ws:
                wins[w] = ws
        if not wins:
            continue

        # use the longest available window's avg APR to decide side
        longest = max(wins.keys())
        primary = wins[longest]

        ctx = current_ctx.get(coin, {})
        cs_base = {
            "coin": coin,
            "windows": wins,
            "current_apr": ctx.get("current_apr", 0.0),
            "oi_usd": ctx.get("oi_usd", 0.0),
            "day_vlm": ctx.get("day_vlm", 0.0),
            "mark": ctx.get("mark", 0.0),
        }

        if primary.avg_apr > 0:
            cs = CoinSummary(side="SHORT", **cs_base)
            cs.headline_score = score_coin(cs, longest)
            shorts.append(cs)
        elif primary.avg_apr < 0:
            cs = CoinSummary(side="LONG", **cs_base)
            cs.headline_score = score_coin(cs, longest)
            longs.append(cs)

    shorts.sort(key=lambda c: c.headline_score, reverse=True)
    longs.sort(key=lambda c: c.headline_score, reverse=True)
    return shorts[:top], longs[:top]


def fetch_current_ctx(exclude: set[str]) -> dict:
    """Get current OI, volume, mark, and instantaneous funding."""
    meta_ctx = post({"type": "metaAndAssetCtxs"})
    meta, ctxs = meta_ctx[0], meta_ctx[1]
    out = {}
    for asset, ctx in zip(meta["universe"], ctxs):
        coin = asset["name"]
        if coin in exclude:
            continue
        mark = float(ctx["markPx"])
        out[coin] = {
            "mark": mark,
            "oi_usd": float(ctx["openInterest"]) * mark,
            "day_vlm": float(ctx["dayNtlVlm"]),
            "current_apr": float(ctx["funding"]) * HOURS_PER_YEAR * 100,
        }
    return out


def fmt_side(rows: list[CoinSummary], windows: list[int], side: str, min_apr: float):
    if not rows:
        print(f"  (no {side} candidates)")
        return

    # header
    header = f"{'coin':<10}{'OI $M':>8}{'mark':>12}{'now APR':>9}"
    for w in windows:
        header += (
            f"  │ {w}d:{' APR%':>7}{' cum%':>7}{' ΔP%':>7}{' MDD%':>7}{' PnL%':>7}"
        )
    print(header)
    print("-" * len(header))

    for cs in rows:
        line = f"{cs.coin:<10}{cs.oi_usd / 1e6:>8.0f}{cs.mark:>12.4f}{cs.current_apr:>9.1f}"
        for w in windows:
            ws = cs.windows.get(w)
            if not ws:
                line += f"  │ {'--':>38}"
                continue
            pnl = ws.short_harvest_pnl if side == "SHORT" else ws.long_harvest_pnl
            line += (
                f"  │{'':<4}"
                f"{ws.avg_apr:>7.0f}"
                f"{ws.cum_funding_pct:>7.1f}"
                f"{ws.price_change_pct:>7.1f}"
                f"{ws.max_drawdown_pct:>7.1f}"
                f"{pnl:>7.1f}"
            )
        print(line)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--sync", action="store_true", help="update cache with latest data")
    ap.add_argument(
        "--deep-sync",
        type=int,
        metavar="DAYS",
        help="backfill DAYS of history (first run)",
    )
    ap.add_argument(
        "--report", action="store_true", help="analyze cache and report (default)"
    )
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument(
        "--windows", type=str, default=",".join(str(w) for w in DEFAULT_WINDOWS)
    )
    ap.add_argument("--min-apr", type=float, default=25.0)
    ap.add_argument("--min-oi", type=float, default=3.0, help="min OI $M (default 3)")
    ap.add_argument("--min-vlm", type=float, default=0.3)
    ap.add_argument("--exclude", type=str, default=",".join(sorted(DEFAULT_EXCLUDE)))
    ap.add_argument(
        "--workers",
        type=int,
        default=3,
        help="parallel API workers (default 3, keep low to avoid 429)",
    )
    args = ap.parse_args()

    if not (args.sync or args.deep_sync or args.report):
        args.report = True

    exclude = {c.strip().upper() for c in args.exclude.split(",") if c.strip()}
    windows = sorted(int(w) for w in args.windows.split(","))

    # Sync modes
    if args.deep_sync:
        ctx = fetch_current_ctx(exclude)
        coins = list(ctx.keys())
        sync_funding(coins, args.deep_sync, workers=args.workers)
        sync_prices(coins, args.deep_sync, workers=args.workers)
        print(
            f"  deep sync complete: {len(coins)} coins × {args.deep_sync}d",
            file=sys.stderr,
        )
    elif args.sync:
        ctx = fetch_current_ctx(exclude)
        coins = list(ctx.keys())
        depth = max(windows)
        sync_funding(coins, depth, workers=args.workers)
        sync_prices(coins, depth, workers=args.workers)
        print(f"  sync complete", file=sys.stderr)

    # Report
    funding_cache = load_cache(FUNDING_CACHE)
    price_cache = load_cache(PRICE_CACHE)
    if not funding_cache:
        print("ERROR: no cache. Run with --deep-sync 90 first.", file=sys.stderr)
        return 1

    current_ctx = fetch_current_ctx(exclude)

    # filter universe: keep coins meeting OI/vlm filters AND that are in cache
    filtered_ctx = {
        c: v
        for c, v in current_ctx.items()
        if v["oi_usd"] >= args.min_oi * 1e6
        and v["day_vlm"] >= args.min_vlm * 1e6
        and c in funding_cache
    }

    # filter caches to the filtered set for reporting
    f_filtered = {c: funding_cache[c] for c in filtered_ctx if c in funding_cache}
    p_filtered = {c: price_cache.get(c, []) for c in filtered_ctx}

    shorts, longs = build_report(
        f_filtered, p_filtered, filtered_ctx, windows, exclude, args.min_apr, args.top
    )

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"\n  Hyperliquid funding history analysis — {now}")
    print(
        f"  Windows: {windows}d   Filters: OI ≥${args.min_oi}M, "
        f"vlm ≥${args.min_vlm}M   Excluding: {sorted(exclude)}"
    )
    print(
        f"  Universe: {len(filtered_ctx)} coins   |   "
        f"Cached funding: {len(funding_cache)} coins\n"
    )

    print("═" * 120)
    print("  SHORT-HARVEST  (short to collect positive funding)")
    print("═" * 120)
    print(
        "  Legend: APR = annualized funding | cum% = cumulative funding collected | "
        "ΔP% = price change\n          MDD% = max drawdown | PnL% = harvest P&L "
        "unleveraged (funding − price change for shorts)\n"
    )
    fmt_side(shorts, windows, "SHORT", args.min_apr)

    print()
    print("═" * 120)
    print("  LONG-HARVEST  (long to collect negative funding)")
    print("═" * 120)
    print("  PnL% = funding collected + price appreciation\n")
    fmt_side(longs, windows, "LONG", args.min_apr)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
