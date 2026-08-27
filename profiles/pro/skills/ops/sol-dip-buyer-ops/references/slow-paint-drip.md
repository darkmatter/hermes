# Slow paint-up + padre drip sell

Session learning (MARV / `6xycyGrZ…`, 2026-07-30).

## Why stock “gentle” sell failed

- Armed absorb TP with bag-frac only: `--tp-ladder '0.08:0.04,…'`, `--sell-frac-cap 0.08`, sell ref 120k.
- First fill: **~24M tokens → ~35.3 SOL, impact ~20%**, mcap cratered (~135k → ~90k).
- Root cause: **frac × fat bag ≫ pool**. Absorby style knobs do not limit SOL-out on the sell path unless SOL/impact caps exist.
- Stock TP = **once per rung** (`tp_hits`) → cannot grind inventory; either one hot clip or leftover forever.

## Code knobs (dip_buyer.py)

- `--tp-repeat` — re-fire same gain rung after cooldown (continuous drip).
- `--max-sell-sol` — post-quote scale token raw so out-SOL ≤ N (iterate ~2×).
- `--max-sell-impact` — further shrink / `impact_skip` if still hot.
- Pool soft-cap via existing `--max-pool-frac`.
- Hourly sell SOL-out via `recent[]` + `--max-per-hour`.
- Jupiter impact may be fraction or percent; normalize `>1 → /100` before comparing.

Boot log should show: `tp_repeat=True max_sell_sol=1.0 max_sell_impact=0.02`. Fill notes tag `+solcap=` / `+impcap=`.

## Preferred live profile (this mint)

| Run | Wallet | Role |
|-----|--------|------|
| `buy-paint-marv` | `mrv` `AZYsGo…` | soft paint buy, ref 150k |
| `buy-paint-dip` | `marv-dip-buyer` `PWbrhU…` | soft paint buy, small budget |
| `sell-absorb-padre` | `padre` `GKzKZW…` | drip sell, ref **100k**, SOL-capped |
| `buy-paint-padre` | — | **stopped**; heartbeat `wallet` nulled so sell can own padre |

**Buy response (current preference): `--buy-response freq`** — dips change **cooldown**, not clip size.

| Run | base-clip | FREQ ladder (dd:cd_sec) | hour | budget |
|-----|-----------|-------------------------|------|--------|
| mrv | 1.0 SOL | `0.15:150,0.25:90,0.40:60,0.55:40,0.70:25` | 12 | **500** (whole-wallet) |
| dip | 0.5 SOL | same FREQ | 8 | **500** |

Legacy size ladder `0.20:1 … 0.75:3` only if Cooper wants bigger clips deeper.
Sell: `tp-ladder` all `0.02` fracs · `--tp-repeat` · `--max-sell-sol 1` · `--max-sell-impact 0.02` · `--max-pool-frac 0.01` · hour 5 · CD 180s · **no stop-loss**.

Sell-only-when-strong: keep sell ref **below** intended recovery so crash lows show `gain=0` / `below first TP rung — wait` until bounce.

See also `references/buy-response-freq.md` for flag semantics, budget-500 bind, seller-exploit honesty.

## buy→sell same key checklist

1. `botctl stop --run-id buy-paint-padre` (or whichever buy owned the sell pubkey).
2. Null `wallet` on that run’s `heartbeat.json` (sibling scanner ignores side=stopped **with wallet still set**).
3. Confirm buyers still mark `--sell-wallet` / `--buy-wallet` correctly (annotation ≠ process).
4. Start `sell-absorb-padre` with `--buy-wallet <other buy pubkey>`.

## Monitor

Repo: `scripts/monitor_slow_paint.py`
Hermes wrapper (required for cron): `~/.hermes/scripts/sol_dip_slow_paint_monitor.py` (`runpy` → repo script).
Cron shape: `*/5 * * * *`, `no_agent=true`, `repeat forever`, `workdir` repo, deliver Cooper DM `slack:D0AK02MKFRP`.
Empty stdout = healthy. Alerts on dead/stale, sell impact/clip, drip-hour SOL (skips historic uncapped 35 SOL nuke), dump-while-selling.

## Ops instincts

- If Cooper says sell is “causing too much dip” → **stop sell first**, then tighten caps; don't argue impact math mid-bleed.
- Dual soft paint still buys the hole after a sell nuke — consider pausing buyers while dissecting, or they paint into the aftermath (desired recovery vs amplified spend).
- Budget headroom: Cooper default **`--budget 500`** so chain SOL is the real limit (`min(wallet−fee, budget−spent)`). Low ceilings (99/130/16) leave SOL stranded with `wallet_low`.
- Restart budgets net of spent; wallet swap does not reset spent on a run_id.
- Freq mode + dust wallet: keep `--base-clip` ≤ available or you get `clip rounded to 0`.
- Seller-made dips still drain wallets under sticky deep dd; freq only removes *size amplification*.
