# Funding regime guide

How to read the screener output and decide whether to deploy capital. Project-specific sizing tiers and dollar amounts should live in that project's `.agent/context/decisions.md`; this guide is regime-agnostic.

## The four regimes

### Quiet regime

**Signature:** Most names showing exactly 11% APR (the funding cap). Few or no names above 30% APR. No standout opportunities.

**What it means:** Mild positive funding bias across the market. Longs are paying shorts on most names, but at the floor rate, not because of euphoria. No specific name has crowded long positioning yet.

**Action:** Don't deploy harvest book. Sit in cash. Re-check daily.

### Elevated regime

**Signature:** 3-10 names showing 30-60% APR with positive 30d harvest PnL. Stability scores generally above 1.0. No widespread cap-pinning.

**What it means:** Specific names have meaningful crowding. Funding is paying enough to compensate tail risk on a careful selection. Real opportunities exist but require name-by-name diligence.

**Action:** Small-size deployment. Pick the best 2-3 by combined APR × stability × positive 30d PnL. Hard stops at -25%. Use this regime to maintain operational readiness, not as a primary P&L driver.

### Euphoria regime

**Signature:** 5+ names showing 60%+ APR sustained for >7 days. Multiple stability scores above 2.0. Often coincides with bull market mania, post-listing pumps, narrative cycles.

**What it means:** Significant long-side crowding with structural payment to shorts. Market-wide signal that something is overheating.

**Action:** Real-size deployment, up to 4 names. This is also the regime where being too small leaves money on the table; lean into it within your project's risk limits.

**But:** Tail risk is also higher because narrative-driven rallies can squeeze further. Keep stops in place.

### Inverted regime (negative funding side)

**Signature:** Names showing strongly negative APR (-30% or worse) sustained. Shorts paying longs.

**What it means:** Either (a) the asset is dying and shorts are happy to keep paying because they expect more downside, or (b) short-squeeze setup brewing. Both are dangerous.

**Action:** Approach with extreme care. Long-harvest can work but only if:
- The asset has not been in sustained downtrend (>40% drawdown in last 30d disqualifies)
- No identifiable catalyst (delisting, unlock, hack) explaining the negative funding
- 30d historical PnL of the long-harvest position would have been positive

If those gates pass: micro-size only.

## Reading individual rows

For each coin, the screener shows:

- **APR%** — annualized rate. The headline number, but never the only number.
- **cum%** — cumulative funding actually flowed over the window. Tells you what someone holding the position the whole window would have collected.
- **ΔP%** — price change of the underlying. The cost (or benefit) of the directional exposure your harvest position takes on.
- **MDD%** — max drawdown the position experienced. The "worst point" you would have had to sit through.
- **PnL%** — net return of the harvest trade: cum funding ± ΔP.

**The most important field is PnL%, not APR%.**

A 100% APR with -20% PnL means you collected 8% in funding while the underlying ran 28% against you over the window. That's a losing trade despite the eye-popping APR.

A 30% APR with +5% PnL means you collected 2.5% in funding and the underlying drifted slightly your way over the window. That's a winning trade despite the modest APR.

## When the screener and your gut disagree

If a name passes the gates but you have a strong fundamental view on the underlying, defer to the fundamental view. The screener doesn't know about news, unlocks, governance issues, or narrative shifts. It's an evidence-based starting point for analysis, not a buy signal.

Common cases where to override the screener:
- Name is in your existing book or is correlated to it (avoid — adds correlated risk)
- Recent news catalyst (within 7 days) — wait for funding to stabilize post-news
- Sector leader during its narrative cycle (don't short SOL during a Solana season)
- Anything where the founder / major holder / Saylor-figure recently made a bullish public statement

## Position rotation discipline

If running multiple harvest positions, rotate weekly:
- Re-run screener
- Names that no longer pass thresholds → close
- New names that pass → consider opening
- Keep total notional within your project's tier cap

Inertia is the most common failure mode. A position kept past its setup degrading from "harvest" to "directional bet I forgot about."
