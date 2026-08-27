# Cooldown / poll jitter (timing unpredictability)

## Why

Cooper: *“we need some RNG in the timings so it can’t be predicted.”*

Fixed `freq cd=60s` after every fill is a free stopwatch for anyone watching fills (or your own logs). Frequency-vs-depth stays; exact fire-second must not.

## Flags (`dip_buyer.py`)

| Flag | Default | Live preferred | Behavior |
|------|---------|----------------|----------|
| `--cooldown-jitter J` | `0.25` | `0.30` | Each wait samples `U[cd*(1-J), cd*(1+J)]`, floored at `--min-cooldown` in freq mode. **Once per wait** — key = depth/base CD; held until fill then cleared. |
| `--poll-jitter S` | `0.35` | `0.5` | Adds `U[0, min(S, poll)]` into sleep_for while waiting (not every poll re-roll of the whole CD). |

Helpers: `apply_cooldown_jitter(cd, jitter, min_cooldown=…)`. State: `scheduled_cd`, `scheduled_cd_key` in the main loop (buy + sell).

## Sample once, not every poll

Wrong: re-call `random.uniform` every loop → countdown thrash, flappy logs.
Right: if `scheduled_cd is None or key changed` → roll; use that until `last_trade_ts` update clears both schedule fields.

Key shapes:

- buy freq: `freq:{dd_lvl:.4f}:{base_cd:.3f}`
- buy size: `size:{dd_lvl:.4f}:{base_cd:.3f}`
- sell: `sell:{cooldown:.3f}`

Depth change mid-wait re-rolls (correct — new base band).

## Prove live

```text
BUY RESPONSE=freq: … cooldown_jitter=+/-30% poll_jitter=0.50s
cooldown roll base=60.0s -> 70.5s (jitter=+/-30% key=freq:0.4000:60.000)
SIGNAL buy 1.0 SOL … (level=-40% freq cd=70s …)
cooldown roll base=60.0s -> 44.9s …
sell cooldown roll base=180.0s -> …
```

Heartbeat: `cooldown_jitter`, `effective_cooldown_s` (= scheduled if set).

cmdline must show `--cooldown-jitter` / `--poll-jitter` after restart (old PIDs keep pre-jitter binary behavior only if binary unchanged — always restart into new code).

## argparse `%` footgun (hard fail)

Python 3.14 `argparse` expands `%` in `help=`. A bare `+/-25%` causes:

```text
ValueError: badly formed help string
```

at `add_argument(--cooldown-jitter)` → **every** botctl start dies before trading.
Escape: `+/-25%%` in the help string. `py_compile` does **not** catch this — run `dip_buyer.py --help` after editing help text.

## What jitter does / doesn’t buy

| Does | Does not |
|------|----------|
| Break exact T+60s sniping off last fill | Hide that deep dd → faster *band* |
| Decorrelate dual bots’ fire slots slightly (independent RNG) | Stop sticky-dd wallet drain |
| Apply to TP sell rests too | Replace hour caps / SOL sell caps |

Still combine with: small `--base-clip`, hour caps, SOL-capped sells, sell ref below buy ref.

## Unit sanity

```python
from dip_buyer import apply_cooldown_jitter
import random
random.seed(1)
vals = [apply_cooldown_jitter(60, 0.30, min_cooldown=20) for _ in range(200)]
assert min(vals) >= 42 - 1e-6 and max(vals) <= 78 + 1e-6
assert apply_cooldown_jitter(60, 0, min_cooldown=20) == 60
assert apply_cooldown_jitter(10, 0.5, min_cooldown=20) == 20  # floor
```
