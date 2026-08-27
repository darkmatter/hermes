#!/usr/bin/env python3
"""Get EXACT click coordinates from a screenshot via Gemini box_2d.

This is the correct way to turn a browser screenshot into clickable pixels.
Do NOT ask a vision model for raw [x,y] pixels — see
references/vision-coordinates-box2d.md for why (bimodal ~178px Y error).

Measured on the AA passenger form at 2560x1440:
  raw-pixel prompt : 3/10 clean runs
  box_2d (this)    : 10/10 clean runs, ~5s, ~$0.009

Setup
-----
  set -a; source ~/.hermes/.env; set +a     # exports OPENROUTER_API_KEY
  (the key lives in ~/.hermes/.env, NOT in himitsu)

Usage
-----
  python3 scripts/vcoord.py shot.png first_name_input last_name_input save_button
  python3 scripts/vcoord.py shot.png --context "AA payment page" card_number expiry cvv

Output (tab-separated, ready to feed straight into click-mouse):
  first_name_input	870 479
  last_name_input	1656 479

Then:
  kernel browsers computer click-mouse "$SID" --x 870 --y 479

Env
---
  OPENROUTER_API_KEY   required
  VCOORD_MODEL         optional, default google/gemini-3.6-flash
                       (gemini-3.1-flash-lite is also 9/9 and ~13x cheaper
                        if the page is simple and latency matters)
"""
from __future__ import annotations

import base64
import json
import os
import re
import sys
import urllib.request

from PIL import Image

MODEL = os.environ.get("VCOORD_MODEL", "google/gemini-3.6-flash")
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"


def locate(png: str, labels: list[str], context: str = "web page screenshot") -> dict:
    """Return {label: (x, y)} in the image's real pixel space."""
    w, h = Image.open(png).size
    b64 = base64.b64encode(open(png, "rb").read()).decode()

    prompt = (
        f"Detect the UI controls in this {context}.\n"
        f"Report these items: {', '.join(labels)}\n\n"
        "Output ONLY a JSON array, Gemini box_2d convention, normalized 0-1000:\n"
        '[{"label":"<name>","box_2d":[ymin,xmin,ymax,xmax]}, ...]\n'
        "Omit any item that is not visible. No prose, no markdown."
    )

    body = {
        "model": MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url",
                 "image_url": {"url": f"data:image/png;base64,{b64}"}},
            ],
        }],
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer <REDACTED>'OPENROUTER_API_KEY']}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=240) as resp:
        data = json.loads(resp.read().decode())

    txt = data["choices"][0]["message"]["content"]
    txt = re.sub(r"^```(?:json)?|```$", "", txt.strip(), flags=re.M).strip()
    match = re.search(r"\[.*\]", txt, re.S)
    if not match:
        raise SystemExit(f"vcoord: no JSON array in response: {txt[:200]}")

    out: dict[str, tuple[int, int]] = {}
    for obj in json.loads(match.group(0)):
        box = obj.get("box_2d") or []
        if len(box) != 4:
            continue
        ymin, xmin, ymax, xmax = box          # NOTE: y FIRST
        out[obj.get("label")] = (
            round(((xmin + xmax) / 2) / 1000 * w),
            round(((ymin + ymax) / 2) / 1000 * h),
        )
    return out


def main() -> None:
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)

    png = args[0]
    context = "web page screenshot"
    rest = args[1:]
    if "--context" in rest:
        i = rest.index("--context")
        context = rest[i + 1]
        rest = rest[:i] + rest[i + 2:]

    if not rest:
        raise SystemExit("vcoord: give at least one label to locate")

    for label, (x, y) in locate(png, rest, context).items():
        print(f"{label}\t{x} {y}")


if __name__ == "__main__":
    main()
