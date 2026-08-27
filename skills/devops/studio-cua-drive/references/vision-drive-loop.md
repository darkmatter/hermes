---
name: studio-cua-vision-drive
description: >-
  Drive logged-in Studio Chrome with a screenshot→vision→coordinates loop —
  CDP screenshot, gemini-3.6-flash, box_2d 0–1000 scaling, one vmap.py sweep
  per screen. Use for Studio browser forms/checkouts where per-field AX
  ping-pong is too slow. Kernel cloud browsers remain fallback-only.
version: 1.0.0
metadata:
  hermes:
    tags: [cua-driver, mac-studio, vision, box_2d, browser-automation]
    category: devops
    related_skills: [studio-cua-driver, kernel-browsers, payment-operations]
---

# Studio CUA vision drive loop

## Why this exists

Cooper, 2026-08-03, during a slow Google Admin payment-form fill:
*"make absolutely sure you're using the correct model (google 3.6 flash), using the
out of 1000 scaling, sending an initial screenshot to get all text fields at once,
etc. see the kernel skill"* and *"dont use kernel browser, thats a fallback. write a new skill."*

The kernel-browsers drive loop (one `vmap.py` sweep per screen + box_2d coords) is
platform-agnostic. This skill ports it to **Studio-local cua-driver + logged-in
Chrome**. Kernel cloud browsers stay fallback-only.

Hard rules (user-stated, non-negotiable):
- Model: `google/gemini-3.6-flash` (the default of vmap/vcoord scripts — verify, don't substitute).
- Coordinates: Gemini **box_2d, normalized 0–1000, `[ymin,xmin,ymax,xmax]` — y FIRST**. Never ask a vision model for raw pixels (bimodal ~178px Y error, kernel-measured).
- **One initial screenshot per screen maps ALL fields at once** (vmap sweep). Never one-element-at-a-time vision queries.
- If the loop is floundering, **refresh the page and start over** instead of grinding.

## Prerequisites

- `set -a; source ~/.hermes/.env; set +a` → `OPENROUTER_API_KEY` (lives in `~/.hermes/.env` on Pro, not himitsu).
- Pillow on Pro: `python3 -c "import PIL"`.
- Scripts (generic OpenRouter+PIL, reuse as-is): `~/.hermes/skills/devops/kernel-browsers/scripts/vmap.py` and `vcoord.py`.
- Studio daemon + Chrome attach per the `studio-cua-driver` skill (`serve --grant existing-profile --no-permissions-gate`, Chrome pid/window via `list_windows`).

## Key discovery: CDP screenshots bypass broken macOS capture

When Studio loses TCC Screen Recording, every screencapture path dies:
- `get_window_state` → `screenshot_error.code = px_capture_unavailable` ("could not create image from window"), AX tree still fine.
- Bare `screencapture -l<win>` / `screencapture -x` on Studio → "could not create image".

But **`get_browser_state` with `include_screenshot: true` captures the tab viewport
as PNG through CDP** — it never touches macOS screencapture and works regardless of
TCC state. Recovery attempts (`cua-driver permissions grant`, daemon restart) may
still leave `screen_recording: false`; **do not stall on the status** — for browser
tabs the CDP route is available. Verified 2026-08-03 on the payments run.

## The loop

All calls are `printf '%s' '<json>' | cua-driver call <tool>` on Studio over SSH
(see studio-cua-driver for the call shape).

1. **Bind** (fresh daemon / `not a live binding` refusal / after any restart):
```
{"session":"<id>","pid":<chrome_pid>,"window_id":<wid>}  →  get_browser_state
```
Returns new `target_id` + `tabs[]` (each with `tab_id`, `url`, `title`). Tab ids
change across daemon restarts — never reuse old ones.

2. **Screenshot + snapshot** (one call):
```
{"session":"<id>","target_id":"<bt>","tab_id":"<tab>",
 "include_screenshot":true,"snapshot_format":"semantic_v2"}  →  get_browser_state
```
Response carries `screenshot_png_b64` (tab viewport PNG, top-level in CLI JSON)
plus semantic refs.

3. **Decode + ONE vmap sweep** (on Pro):
```
scp <REDACTED>:/tmp/shot_state.json /tmp/
python3 - <<'EOF'
import json,base64
d=json.load(open('/tmp/shot_state.json'))
sc=d.get('structuredContent',d)
open('/tmp/shot.png','wb').write(base64.b64decode(sc['screenshot_png_b64']))
EOF
set -a; source ~/.hermes/.env; set +a
python3 ~/.hermes/skills/devops/kernel-browsers/scripts/vmap.py /tmp/shot.png --plan
```
The sweep returns every control with ref/type/label/x/y/**value**/state. `--plan`
groups them: TYPE-ABLE (batchable), SELECTS (one at a time), CLICK TARGETS.

4. **Act.** Prefer semantic refs when a ref is actionable (`browser_type` with
`mode=insert_text, replace=true` validated on Google payment card fields;
`browser_click` by ref). Fall back to vision-map x/y via `browser_click` when the
ref route refuses (e.g. trusted-input-route refusal on Save buttons).
Semantic snapshot + vmap sweep are complementary: snapshot = refs/values/state,
sweep = pixel-accurate click targets.

5. **Verify by re-sweep.** Re-screenshot + re-run vmap; the `value` column is the
read-back (`card_number = 3767…`, no separate check step). Only then report.

## Session / binding lifecycle pitfalls

- Session ends on idle: `session '<id>' has ended … was rejected` → revive with
  `start_session` on the **same** id (`{"session":"<id>","capture_scope":"window"}`
  → `"revived": true`). Cheap; do it reflexively on that error.
- Daemon restart invalidates every browser binding: refusal `authorization_host_failed`
  / "target bt-… is not a live binding in this session" → re-bind (step 1). The old
  target_id/tab_id are dead forever.
- After `browser_navigate`, refs invalidate; re-snapshot before acting.

## Coordinate-space caveat (check on first use with a new binding)

`browser_click`/`browser_pointer` x/y are **viewport CSS pixels**. The CDP PNG may
be at devicePixelRatio (Retina → 2×). Before the first click, compare PNG pixel
dimensions against the CSS viewport size; if the ratio is >1, divide vmap
coordinates by it. (Kernel's computer-use was raw screen pixels, so this didn't
apply there.) If a first click misses, this is suspect #1.

## Anti-patterns

- One-element-at-a-time vision queries — one vmap sweep per screen.
- Asking vision for raw `[x,y]` pixels — box_2d only.
- Using `vision_analyze` prose to decide click locations — it has no coordinate contract.
- Reusing target_id/tab_id/refs across daemon restarts or navigations.
- Stalling on `screen_recording: false` / `px_capture_unavailable` for browser tabs — CDP screenshots work anyway.
- Grinding a floundering form for many minutes — refresh and start over.
- Reaching for a Kernel cloud browser when Studio Chrome is drivable — fallback only.
