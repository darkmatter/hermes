#!/usr/bin/env python3
"""Map EVERY interactive element on a screenshot in ONE vision call.

Generic — works on forms, fare ladders, modals, carousels, nav. Not form-only.

Output is an agent-browser-style flat list:
    [ref] type  label                         x,y     value/state

Why box_2d: asking Gemini for raw pixels is bimodally wrong (~178px Y error
because it drops the browser chrome strip). Normalized 0-1000
[ymin,xmin,ymax,xmax] is its native convention and is exact.
See ../references/vision-coordinates-box2d.md

Env: OPENROUTER_API_KEY  (from ~/.hermes/.env, NOT himitsu)
     VCOORD_MODEL        (default google/gemini-3.6-flash)

Usage:
  python3 vmap.py shot.png                     # all interactive elements
  python3 vmap.py shot.png --json              # machine readable
  python3 vmap.py shot.png --plan              # grouped by how you must drive it
  python3 vmap.py shot.png --only button,link  # filter by type
  python3 vmap.py shot.png --hint "fare ladder rows"   # focus the sweep
"""
import base64
import json
import os
import re
import sys
import urllib.request

from PIL import Image

MODEL = os.environ.get("VCOORD_MODEL", "google/gemini-3.6-flash")

TYPES = [
    "text", "email", "tel", "number", "password", "textarea",
    "select", "radio", "checkbox", "toggle",
    "button", "link", "tab", "menuitem", "row", "card", "icon",
]

BATCHABLE = {"text", "email", "tel", "number", "password", "textarea"}
SEQUENTIAL = {"select"}
CLICKONLY = {"button", "link", "radio", "checkbox", "toggle",
             "tab", "menuitem", "row", "card", "icon"}

PROMPT_TMPL = """List EVERY element a user could click, type into, or select on this screen.

For each element output:
  "label"    short human name / visible text (snake_case, unique)
  "type"     one of: {types}
  "value"    current visible value, selected option, or price/state text; "" if none
  "state"    one of: enabled, disabled, selected, checked, ""
  "box_2d"   [ymin,xmin,ymax,xmax] normalized 0-1000

Guidance:
- "select" = anything that opens a list of options (chevron/caret), even if it looks like a button.
- "button" = performs an action (Search, Continue, Save, Pay now, Select, Upgrade, Dismiss).
- "link" = navigates or reveals (Details, Change, Edit, breadcrumb, "New search").
- "tab" = date-carousel days, cabin tabs, segment tabs.
- "row" = a selectable result row (a flight row, a passenger card) — label it by its key text.
- Include modal/dialog controls and cookie banners if present; they block clicks.
- Include disabled controls, marked state "disabled".
- Reading order: top-to-bottom, left-to-right.
- Skip global site nav, footer link farms, and pure decoration.
{hint}
Output ONLY a JSON array. No markdown, no prose."""


def sweep(png, hint=""):
    w, h = Image.open(png).size
    b64 = base64.b64encode(open(png, "rb").read()).decode()
    prompt = PROMPT_TMPL.format(
        types=", ".join(TYPES),
        hint=f"- Pay special attention to: {hint}\n" if hint else "",
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
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer <REDACTED>'OPENROUTER_API_KEY']}",
                 "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.loads(r.read().decode())
    txt = d["choices"][0]["message"]["content"]
    txt = re.sub(r"^```(?:json)?|```$", "", txt.strip(), flags=re.M).strip()
    arr = json.loads(re.search(r"\[.*\]", txt, re.S).group(0))

    out = []
    for i, o in enumerate(arr, 1):
        bb = o.get("box_2d") or []
        if len(bb) != 4:
            continue
        ymin, xmin, ymax, xmax = bb            # y FIRST
        out.append({
            "ref": f"e{i}",
            "label": o.get("label", "?"),
            "type": (o.get("type") or "?").lower(),
            "value": o.get("value", "") or "",
            "state": (o.get("state") or "").lower(),
            "x": round(((xmin + xmax) / 2) / 1000 * w),
            "y": round(((ymin + ymax) / 2) / 1000 * h),
        })
    return out


def main():
    png = sys.argv[1]
    args = sys.argv[2:]

    hint = ""
    if "--hint" in args:
        hint = args[args.index("--hint") + 1]
    only = None
    if "--only" in args:
        only = {t.strip() for t in args[args.index("--only") + 1].split(",")}

    els = sweep(png, hint)
    if only:
        els = [e for e in els if e["type"] in only]

    if "--json" in args:
        print(json.dumps(els, indent=2))
        return

    if "--plan" in args:
        def show(title, pred, note):
            group = [e for e in els if pred(e)]
            if not group:
                return
            print(f"\n## {title}  — {note}")
            for e in group:
                v = f"  ={e['value']}" if e["value"] else ""
                s = f"  [{e['state']}]" if e["state"] else ""
                print(f"  {e['ref']:>4}  {e['label']:34s} {e['x']:>5},{e['y']:<5}{v}{s}")
        show("TYPE-ABLE", lambda e: e["type"] in BATCHABLE,
             "safe to chain in ONE `computer batch` call")
        show("SELECTS", lambda e: e["type"] in SEQUENTIAL,
             "one at a time: click -> type value -> Enter -> verify")
        show("CLICK TARGETS", lambda e: e["type"] in CLICKONLY,
             "single clicks; re-map after any navigation")
        return

    print(f"{'ref':>4}  {'type':9s} {'label':34s} {'x':>5} {'y':>5}  value/state")
    print("-" * 86)
    for e in els:
        meta = e["value"] or e["state"]
        print(f"{e['ref']:>4}  {e['type']:9s} {e['label']:34s} "
              f"{e['x']:5d} {e['y']:5d}  {meta[:24]}")


if __name__ == "__main__":
    main()
