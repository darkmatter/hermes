# Buy response: dips change frequency, not size

Session learning (MARV / `6xycyGrZ…`, 2026-07-30 evening).

## Preference

Cooper: *“we need to make dips affect frequency, not size.”*

Implementation shipped in `dip_buyer.py`:

- `--buy-response {size,freq}` (default remains `size` for back-compat).
- `freq` → ladder second field is **cooldown seconds**; SOL clip is **`--base-clip`**.
- `freq_cooldown(base_cd, ladder_val, min_cooldown=…)` floors at `--min-cooldown` (default 15).

## Live trifecta after the change

| Run | Response | Clip | Notes |
|-----|----------|------|-------|
| `buy-paint-marv` | `freq` | 1.0 SOL | `FREQ=0.15:150 … 0.70:25`, hour 12, budget **500** |
| `buy-paint-dip` | `freq` | 0.5 SOL | same FREQ ladder; dust wallet forced clip down from 0.8 → 0.5 |
| `sell-absorb-padre` | n/a sell | ≤1 SOL out | still drip + tp-repeat + impact/sol caps |

At dd ~50% vs 150k buy ref, `effective_cooldown_s` ≈ **60** (−40% rung). Signals look like:

```text
BUY RESPONSE=freq: fixed clip=1.0000 SOL; ladder values are cooldown seconds…
SIGNAL buy 1.0 SOL -> … (level=-40% freq cd=60s impact=0.0178 …)
| level -40% ready (freq clip=1.000 CD=60s), cooldown 53s
```

## Budget 500 = “use whole wallet”

Symptom before: spent 130/130 or 16/16 with **~27 SOL / ~3 SOL still on-chain**, status `wallet_low`, level armed, CD 0.

Formula (`budget-mode wallet`):

```text
remaining = min(wallet_sol - fee_reserve, budget - spent)
```

Fix Cooper preferred: restart with `--budget 500` so remaining ≈ wallet − 0.05 until bag is dry. Top-ups auto-extend without another retune. Spent counter keeps growing historically — that is fine.

## Why size-mode ladder misled

Legacy ladder `0.20:1, 0.30:1.5, 0.45:2 …` used the second field as **SOL**. Deeper crash → bigger clip immediately. That is anti what Cooper wants on thin books / when a seller might lean the market.

Freq mode: same 1.0 SOL paint tick whether −15% or −70%; only the **time between ticks** tightens.

## Seller advantage (honest answer)

Yes, still susceptible if:

1. Buy ref stays now far above spot (permanent deep arm).
2. Dual wallets share the ref.
3. Hour caps + min CD still allow a soft drain over time (fixed clip × N fills).

Better than before (no size amplification into the hole). Still not a private AMM bid. Hard stop when worried: `botctl stop --mint … --run-id buy-paint-*`.

## Verify snippets

```bash
# hb
python3 -c 'import json;h=json.load(open("runs/<m8>/buy-paint-marv/heartbeat.json"));print(h.get("buy_response"),h.get("base_clip_sol"),h.get("effective_cooldown_s"),h.get("level"),h.get("remaining_sol"))'

# cmdline still armed
ps -p $(cat runs/<m8>/buy-paint-marv/bot.pid) -o args= | tr " " "\n" | rg "buy-response|base-clip|budget|ladder"

# unit
.venv/bin/python - <<'PY'
from dip_buyer import freq_cooldown
assert freq_cooldown(180, 10, min_cooldown=20) == 20
assert freq_cooldown(180, 0, min_cooldown=20) == 180
print("ok")
PY
```

## Pitfalls

- **Don't** paste a size ladder into `--buy-response freq`** (e.g. `0.20:1.0` then means CD=1s → floor `min_cooldown` spam). Split ladders by mode.
- **Don't** keep dip `base-clip` above wallet − fee — `clip rounded to 0` forever.
- Hermes verify of multi-MB `bot.log`: full-file substring search, not last-8k only.
- Size mode still available if Cooper reverses; don't delete.
