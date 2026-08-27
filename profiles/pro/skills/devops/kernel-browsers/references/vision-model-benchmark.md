# Vision model benchmark for UI pixel grounding (2026-07-31)

## Why this exists
Cooper asked "is it the vision model that is slow?" then "can we try like the top 10
models on openrouter for this". Answer turned out to be counter-intuitive and worth
keeping: **the slow model is the only one that actually works.**

## Method
- Image: `/tmp/pax3.png` — real AA passenger form screenshot, **2560x1440**, ~110KB PNG
- Ground truth: the 9 coordinates that **actually landed clicks** during the live
  Aug-3 booking (first/middle/last name, DOB month/day/year, gender, country, state)
- Prompt: "screenshot is EXACTLY 2560x1440 … return ONLY minified JSON mapping keys to
  [x,y] CENTER pixel coordinates in the ORIGINAL 2560x1440 space"
- Scored a "hit" if predicted point is within **60px** (≈ half a field box)
- 4 trials per finalist, run concurrently via OpenRouter

## Results (4 trials each)
| Model | Hit rate | Median err | Avg s | Avg $ |
|---|---|---|---|---|
| **google/gemini-3.5-flash** | **75%** | **4 px** | 13.2 | 0.0223 |
| x-ai/grok-4.3 | 0% | 152 px | 6.8 | 0.0028 |
| openai/gpt-5-mini | 3% | 98 px | 15.3 | 0 |
| openai/gpt-5.1 | 0% | 214 px | 1.8 | 0 |
| google/gemini-2.5-flash | 0% | 603 px | 2.6 | 0.0011 |

Single-trial screen (12 models):
| Model | Median err |
|---|---|
| gemini-3.5-flash | 2 px (9/9 that run) |
| gpt-5-mini | 126 px |
| mistral-medium-3.1 | 122 px |
| glm-4.6v | 346 px |
| gpt-5.1 | 309 px |
| claude-haiku-4.5 / sonnet-4.5 / opus-4.5 | ~495 px |
| gemini-2.5-pro | 531 px |
| qwen3-vl-235b / qwen3-vl-30b | ~629 px |
| llama-4-maverick | 635 px |
| gemini-2.5-flash | 612 px |

Dead / unusable: `x-ai/grok-4.1-fast` (deprecated → 4.3), `google/gemini-3-pro-preview`
(no endpoint), `moonshotai/kimi-k2-thinking` (no image input).

## Conclusions
1. **Keep `auxiliary.vision.model: google/gemini-3.5-flash`.** It is the only model
   tested that resolves coordinates in the true full-resolution space (**4px median**).
2. The ~500–630px cluster (Claude family, Qwen-VL, Llama-4, gemini-2.5-flash) appears to
   reason in a **downscaled** image and never rescales to the original grid. Fast, cheap,
   and useless for clicking.
3. **Do not "optimize" latency by swapping to 2.5-flash / haiku / qwen.** An early guess
   in this session said 2.5-flash was the win because it answered in 2.8s — it was fast
   because it was **guessing** (603px off). Benchmark before believing a speedup.
4. `gemini-3.5-flash` has **mandatory reasoning** (`"Reasoning is mandatory for this
   endpoint and cannot be disabled"` on `reasoning.enabled:false`) — 1.5k–3.9k reasoning
   tokens per call. That IS the 13s. It is the cost of correctness, not waste.
5. **Variance is real:** same model, same image scored 9/9 @2px on one run and 0/9 on
   another. Always screenshot-verify after a click; never fire a blind chain of clicks
   off a single vision pass.

## Practical rule
Vision is expensive **per call**, so reduce **calls**, not quality:
- full-frame vision on **navigation / new page / unexpected state**
- `computer batch` several fills between vision passes
- region screenshots (`--x --y --width --height`) when only one panel matters
- reuse stable coords (open dropdown rows) without re-visioning

## Note on this session specifically
During the actual booking, `image_input_mode: auto` meant screenshots were attached
**natively to the main model (claude-opus-5)** and the configured aux model never ran.
That native path was accurate but also the slow part. Same conclusion applies: cut the
number of vision round-trips.

## Repro
`/tmp/vision_bench.py` (single pass, 12 models) — edit `MODELS`, needs
`OPENROUTER_API_KEY` (from `~/.hermes/.env`, not himitsu).
