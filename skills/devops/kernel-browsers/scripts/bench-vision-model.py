#!/usr/bin/env python3
"""Benchmark OpenRouter vision models on a real screenshot.

Answers "is the vision model the slow part?" with numbers instead of vibes.
Prints elapsed wall time, reasoning tokens, cost, and the raw coordinate output
so you can eyeball whether the model reports coords in the ORIGINAL pixel space.

Usage:
    set -a; source ~/.hermes/.env; set +a     # OPENROUTER_API_KEY lives here
    python3 bench-vision-model.py /tmp/shot.png
    python3 bench-vision-model.py /tmp/shot.png google/gemini-2.5-flash anthropic/claude-sonnet-4.5

Defaults compare the two Gemini Flash generations, which is the comparison that
mattered on 2026-07-31 (3.5-flash forces reasoning: ~4x slower, ~24x pricier,
and it emitted downscaled coords).

Notes:
- OPENROUTER_API_KEY is NOT in himitsu; it is in ~/.hermes/.env.
- Sourcing that .env may print a harmless Chrome.app path error. Ignore it.
- If the main model has native vision and system.image_input_mode is `auto`,
  Hermes bypasses the aux vision model entirely and the configured aux model
  never runs. Check that before tuning aux config.
"""
from __future__ import annotations

import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

DEFAULT_MODELS = ["google/gemini-2.5-flash", "google/gemini-3.5-flash"]
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# Terse, coordinate-only prompt. Verbose "describe everything" prompts are a
# large part of why the AA drive felt slow -- premium models write paragraphs.
PROMPT_TEMPLATE = (
    "{w}x{h} screenshot. Return ONLY compact JSON mapping each visible interactive "
    "control to its center pixel coordinates in the ORIGINAL {w}x{h} space, e.g. "
    '{{"first_name":[x,y],"continue":[x,y]}}. No prose, no markdown fences.'
)


def image_size(path: str) -> tuple[int, int]:
    """Best-effort PNG dimensions from the IHDR chunk; falls back to 2560x1440."""
    try:
        with open(path, "rb") as fh:
            head = fh.read(24)
        if head[:8] == b"\x89PNG\r\n\x1a\n":
            return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")
    except OSError:
        pass
    return 2560, 1440


def bench(model: str, b64: str, prompt: str) -> None:
    body = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64}"},
                    },
                ],
            }
        ],
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer <REDACTED>'OPENROUTER_API_KEY']}",
            "Content-Type": "application/json",
        },
    )

    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=240) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode()[:200]
        print(f"{model:34s} HTTP {exc.code}  {detail}")
        return
    except Exception as exc:  # noqa: BLE001 - surface anything else plainly
        print(f"{model:34s} ERROR {type(exc).__name__}: {exc}")
        return
    elapsed = time.time() - start

    usage = data.get("usage") or {}
    reasoning = (usage.get("completion_tokens_details") or {}).get("reasoning_tokens")
    cost = usage.get("cost")
    cost_str = f"${cost:.4f}" if isinstance(cost, (int, float)) else "n/a"
    text = (data["choices"][0]["message"]["content"] or "").replace("\n", " ")

    print(f"{model:34s} {elapsed:6.1f}s  reason_tok={reasoning}  cost={cost_str}")
    print(f"    {text[:260]}")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    path = sys.argv[1]
    models = sys.argv[2:] or DEFAULT_MODELS

    if "OPENROUTER_API_KEY" not in os.environ:
        print("OPENROUTER_API_KEY not set. Run: set -a; source ~/.hermes/.env; set +a")
        return 1

    with open(path, "rb") as fh:
        raw = fh.read()
    b64 = base64.b64encode(raw).decode()
    width, height = image_size(path)
    prompt = PROMPT_TEMPLATE.format(w=width, h=height)

    print(f"image   : {path}  ({width}x{height}, {len(raw) // 1024}KB, {len(b64) // 1024}KB b64)")
    print(f"models  : {', '.join(models)}\n")
    for model in models:
        bench(model, b64, prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
