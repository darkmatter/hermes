# Getting reliable click coordinates out of a vision model

**TL;DR — never ask a Gemini vision model for raw pixel coordinates. Ask for
`box_2d` normalized 0–1000 and rescale yourself. It goes from ~30% reliable to 100%.**

## The bug this solves
Asking `"return [x,y] pixel coords in the original 2560x1440 space"` produces a
**bimodal** failure: results are either ~2px perfect or ~178px wrong, never in between.

Diagnosis from raw output (same image, same prompt, 6 trials):

```
t0: first_name=[871, 478]   y-scale 1.002   OK
t1: first_name=[871, 348]   y-scale 1.376   BAD
t2: first_name=[870, 480]   y-scale 0.998   OK
t3: first_name=[870, 350]   y-scale 1.369   BAD
```

- **X is always right (±2px). Only Y breaks**, always by ~**1.373×**
- `1440 / 1.373 ≈ 1049` → on bad runs the model reports Y against the **page content
  area only**, silently dropping the ~391px Chrome tab-bar + toolbar strip
- A 178px Y error on a form = **one row off** → you type into the wrong field. This is
  the same class of bug as "last name swallowed the email"

## Things that did NOT fix it
| Attempt | Result |
|---|---|
| Ask model to also report `image_width`/`image_height` it perceives | Always answers `1920x1080` regardless of real size — useless |
| Look for image dims in the API response | **No such metadata.** Response has `usage`, `cost`, `reasoning_details`, `finish_reason`, `image_tokens: 0` — nothing spatial |
| Pre-resize screenshot to 1920x1080 before sending | 3/8 clean — no better |
| Pre-resize to 1280x720 | 0/8 — worse |
| Swap to a "faster" model | 100–630px errors (see `vision-model-benchmark.md`) |

## The fix — use Gemini's native convention
Gemini is trained to emit **`box_2d`, normalized 0–1000**, ordered **`[ymin, xmin, ymax, xmax]`**
(y first!). Asking for pixels forces an internal conversion, and that conversion is what
breaks. Ask in-spec, do the arithmetic locally.

### Prompt
```
Detect the form input controls in this <page description>.
Report these items: first_name, last_name, dob_month, gender, state_province

Output ONLY a JSON array, Gemini box_2d convention, normalized 0-1000:
[{"label":"first_name","box_2d":[ymin,xmin,ymax,xmax]}, ...]
```

### Rescale
```python
def box_to_center(box_2d, real_w, real_h):
    ymin, xmin, ymax, xmax = box_2d          # NOTE: y first
    x = ((xmin + xmax) / 2) / 1000 * real_w
    y = ((ymin + ymax) / 2) / 1000 * real_h
    return round(x), round(y)
```

## Measured results (AA passenger form, 2560x1440, ground truth = coords that clicked)
| Prompt style | Model | Clean runs | Speed |
|---|---|---|---|
| raw pixel coords | gemini-3.6-flash | 3/10 | 7.6s |
| raw pixel coords | gemini-3.5-flash | 1/10 | 12.3s |
| pre-resized 1920x1080 | gemini-3.6-flash | 3/8 | — |
| **box_2d normalized** | **gemini-3.6-flash** | **10/10** | **5.1s** |

Same prompt, across models (8 trials each):
| Model (box_2d) | Accuracy | Speed | Cost |
|---|---|---|---|
| google/gemini-3.6-flash | **9.0/9** | 5.1s | $0.0091 |
| google/gemini-3.5-flash | **9.0/9** | 5.7s | $0.0095 |
| google/gemini-3.1-flash-lite | **9.0/9** | **2.7s** | **$0.0007** |
| google/gemini-2.5-flash | 0/9 | 3.8s | $0.0015 |

**Key insight:** the earlier conclusion "only 3.5-flash can ground pixels, and it's
inherently slow" was **an artifact of the bad prompt format**, not a capability limit.
With box_2d even `flash-lite` is perfect — 2x faster and 13x cheaper.

## Configured choice
`auxiliary.vision.model: google/gemini-3.6-flash` (set 2026-07-31).
Cooper: *"lets set it to 3.6-flash still, who knows what itll do on more complex images"* —
flash-lite ties on this form but 3.6 has more headroom on cluttered pages. If a drive is
latency-bound and the page is simple, flash-lite is a legitimate downgrade.

## Still true regardless of prompt format
- **Verify after clicking.** Screenshot and confirm state; never fire a blind chain of
  clicks off one vision pass.
- Reduce **number** of vision calls (batch fills, region crops) — that's the real latency
  lever, not model choice.
