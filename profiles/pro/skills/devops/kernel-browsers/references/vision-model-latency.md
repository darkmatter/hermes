# Vision latency on computer-use drives — measured

Cooper asked, after a slow-but-successful AA booking drive: *"it was so slow, is it the
vision model that is slow?"* This file is the measured answer. Re-measure before assuming
these numbers still hold.

## Measured 2026-07-31 (live Kernel session, 2560x1440)

### Kernel `computer` ops — NOT the bottleneck
| Op | Wall time |
|---|---|
| `computer screenshot` (full frame, ~110–135KB PNG) | 0.9–1.6s |
| `computer type` | ~0.7s |
| `computer click-mouse` | **~4s** (slowest Kernel call) |

### Vision — the real cost
| Path | Time | Reasoning tokens | Cost | Coord quality |
|---|---|---|---|---|
| **Main model native** (`anthropic/claude-opus-5`, `image_input_mode: auto`) | ~5–15s | n/a | premium | **best** — coords landed first try |
| `google/gemini-3.5-flash` (was configured as aux) | **10.6s** | **1,489** | **$0.0194** | **wrong scale** ❌ |
| `google/gemini-2.5-flash` | **2.8s** | 0 | **$0.0008** | roughly right, not pixel-exact |

## Three findings

### 1. The configured aux vision model never ran
`~/.hermes/config.yaml`:
```yaml
auxiliary:
  vision:
    provider: openrouter
    model: google/gemini-3.5-flash
```
…but `system.image_input_mode: auto` + a **main model with native vision** means Hermes
attaches the PNG straight into the main model's context. `vision_analyze` returns
*"Image loaded into your context — you can see it natively now."* The aux model sat idle.

**So "which vision model is slow" has two answers** — check `image_input_mode` and whether
the main model has native vision *before* blaming the aux config.

### 2. gemini-3.5-flash forces reasoning
```
HTTP 400: "Reasoning is mandatory for this endpoint and cannot be disabled."
```
`{"reasoning":{"enabled":false}}` and `{"reasoning":{"max_tokens":0}}` are both rejected.
It burned 1,489 reasoning tokens to locate form fields: ~4x the latency and ~24x the cost
of 2.5-flash, and it returned coordinates in a **downscaled space**, not the true
2560x1440 grid — which would make blind clicks miss.

For "where is the blue button", reasoning is pure overhead. Prefer **`gemini-2.5-flash`**
for aux vision; avoid 3.5-flash for coordinate work.

### 3. The dominant cost is round-trip COUNT, not any single call
The naive cadence is `screenshot → vision → click → screenshot → vision → …` at roughly
**15–25s per field**. The AA passenger + payment drive was ~30 interactions, so the elapsed
time was mostly **re-visioning a 3.7-megapixel frame after every single field**.

Bigger viewport (2560x1440) buys accuracy and costs latency. Don't undo it — stop paying
for it on every step.

## Speedups (all CLI, none of them require giving up the big viewport)

1. **`computer batch`** — many actions in one round trip:
   ```bash
   kernel browsers computer batch <id> --actions '{"actions":[
     {"type":"click_mouse","x":869,"y":479},
     {"type":"type_text","text":"Telavaya"}
   ]}'
   ```
   **Status: documented from `--help`, NOT yet validated on a real form.** Confirm the
   exact action `type` names with `kernel browsers computer batch --help` before relying
   on it in a checkout flow.

2. **Region screenshots** — crop to the form instead of the whole page:
   ```bash
   kernel browsers computer screenshot <id> --x 650 --y 400 --width 900 --height 700 --to /tmp/form.png
   ```
   Fewer pixels ⇒ faster vision. Add the region origin back when converting to click coords.

3. **Don't vision every step.** Vision once to map a stable form, batch 3–4 fills, then
   **one** verify capture. Re-vision only after navigation, a modal, or an unexpected result.

4. **Terse prompts.** "coords of Continue only, JSON" beats "describe the page and list
   every control" — the descriptive prompts used during the AA drive made a premium model
   write paragraphs per screenshot.

5. **Reuse stable coords.** Once a `<select>` is open, option rows are predictable — click
   without a fresh vision pass.

## Practical split
| Need | Use |
|---|---|
| Coordinate-critical clicking on a checkout | **Main model native vision** (accuracy wins; a missed pay-click costs more than 10s) |
| "What page am I on", banner/error checks, verify shots | **gemini-2.5-flash** (2.8s, ~$0.001) |
| Anything | **not gemini-3.5-flash** for coords — mandatory reasoning, 24x cost, wrong scale |

## Repro
`scripts/bench-vision-model.py` — times any OpenRouter vision model against a saved
screenshot and prints elapsed / reasoning tokens / cost / raw coords.

Note: `OPENROUTER_API_KEY` lives in `~/.hermes/.env`, not in himitsu and not exported into
the agent shell. `set -a; source ~/.hermes/.env; set +a` first (that file may emit a
harmless `Chrome.app/...: No such file or directory` line — ignore it).
