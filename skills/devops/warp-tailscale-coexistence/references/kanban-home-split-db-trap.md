# HERMES_KANBAN_HOME split-DB trap

## Symptom

`hermes kanban list` (CLI) and the gateway dispatcher see **different kanban
databases** — tasks shown in the CLI don't match what the gateway dispatches.

## Cause

`HERMES_KANBAN_HOME` was set (inherited from an old shell, not from nix or
any config file) to `~/mnt/devbox-hermes` — a macFUSE mount of
devbox's `~/.hermes`.

- The **gateway** (launchd plist) does NOT set `HERMES_KANBAN_HOME`, so
  `kanban_home()` falls through to `get_default_hermes_root()` → `~/.hermes`
  (local).
- The **CLI** (shell) inherits `HERMES_KANBAN_HOME` → resolves to the
  macFUSE mount of devbox's `~/.hermes`.

Result: two different SQLite databases. The gateway dispatches against the
local DB; the CLI queries the devbox DB. They never agree.

## Fix

`unset HERMES_KANBAN_HOME` in `~/.<REDACTED>` so both paths converge on
`~/.hermes`. The env var was never set by nix, any config file, or the
launchd plist — it was purely inherited from an old shell session.

## Verification

```bash
# Should be empty / unset
echo "${HERMES_KANBAN_HOME:-unset}"

# Gateway and CLI should resolve the same path
python3 -c "from hermes_cli.kanban_db import kanban_home; print(kanban_home())"
```

## Related

- `kanban-worker` skill — TUI crash + default_assignee were also found
  while debugging this; the split-DB masked the real crash diagnosis.
- Cooper decided cross-machine kanban is **not worth it** — run the
  gateway on the machine that owns the DB. No macFUSE mounts for kanban.
