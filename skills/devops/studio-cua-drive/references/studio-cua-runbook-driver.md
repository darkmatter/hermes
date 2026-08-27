# Studio cua-driver runbook

## Serve (from Pro over SSH)

```bash
ssh -o BatchMode=yes coopermaruyama@<REDACTED>
export PATH="$HOME/.local/bin:/opt/homebrew/bin:$PATH"
pkill -f "cua-driver serve" 2>/dev/null || true
sleep 1
nohup env CUA_DRIVER_RS_PERMISSIONS_GATE=0 \
  cua-driver serve --grant existing-profile --no-permissions-gate \
  > /tmp/cua-driver-serve.log 2>&1 &
sleep 2
cua-driver status
printf '%s' '{"session":"aa1","capture_scope":"window"}' | cua-driver call start_session
```

`--grant existing-profile` is required for attaching to the user’s logged-in Chrome.
`browser-approve --strategy existing_profile …` is **interactive only** (not pipeable).
Plain `cua-driver serve --grant existing-profile` may open System Settings (Screen Recording gate) and hang under SSH — use `--no-permissions-gate` + `CUA_DRIVER_RS_PERMISSIONS_GATE=0` after labels are already granted.

## Call JSON via Python (robust from Pro)

Scp a script; avoid nested heredocs through SSH:

```python
import json, subprocess
def call(tool, args):
    p = subprocess.run(
        ["cua-driver", "call", tool],
        input=json.dumps(args), text=True, capture_output=True,
    )
    out = (p.stdout or "").strip()
    return json.loads(out) if out[:1] in "{[" else out
```

Always pass `"session": "<id>"` on browser-scoped tools after `start_session`.

## Chrome form fill (AX)

1. `list_windows` → large Chrome window (title may be **empty**; use bounds height).
2. `start_session` + `bring_to_front`.
3. `get_window_state` → map labels → `element_index`.
4. Text: foreground click → `cmd+a` → `type_text` with index.
5. DOB popups: month open → `down` once Jan→Feb → `return`; re-read values — month clings to Jan often.
6. Re-snapshot; require exact values before submit.
7. Re-resolve Chrome pid/window after every navigation.
8. Airline **Select fare / purchase** buttons stay human-gated.

## Anti-patterns

- Pro `computer_use` on Screen Sharing for Studio
- Multi-line Python injected as a single SSH-quoted string
- Trusting deeplink query params alone for AA search results
- Reporting travel credit $ amount when cancel page only says “Canceled”
