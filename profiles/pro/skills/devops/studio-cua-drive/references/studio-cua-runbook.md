# Studio cua-driver runbook (Pro → Studio)

## User correction
Never default to Pro Herms `computer_use` on **Screen Sharing**. Cooper asked for SSH + Studio cua.

## Host
- SSH: `coopermaruyama@<REDACTED>` (Tailscale also `100.111.149.47`)
- Binary: `~/.local/bin/cua-driver` → CuaDriver.app (footage versions ~0.14.x observed)

## Start
```bash
ssh -o BatchMode=yes coopermaruyama@<REDACTED> \
  'export PATH=$HOME/.local/bin:/opt/homebrew/bin:$PATH
   cua-driver stop 2>/dev/null || true
   # long-lived — from Pro use background openai terminal tracking
   cua-driver serve --grant existing-profile'
```

## Call shape
Always JSON on stdin to `cua-driver call <tool>`:

| Step | Tool | Notes |
|---|---|---|
| Session | `start_session` | `{"session":"id","capture_scope":"window"}` |
| Windows | `list_windows` | Chrome height >400 |
| Front | `bring_to_front` | `{"pid":…}` |
| Tree | `get_window_state` | max_elements 150–300; re-snap every action |
| Act | `click` / `type_text` / `press_key` / `hotkey` | Prefer `delivery_mode":"foreground"` on forms |

## Form type reliability
- AX values often return `unverifiable` with escalation `recommended: page`.
- Still works if you re-read field values (Last name etc.) after type.
- PopUpButton DOB: click → type `Feb`/`20`/`1991` or down-arrow from Jan → Enter.
- Stale `element_index` after submenu/nav → compulsory new snapshot.

## Scripts
Prefer scp Python to Studio `/tmp/` over giant remote zsh heredocs when quotes break.

## Related
- `references/aa-online-credit-rebook.md`
