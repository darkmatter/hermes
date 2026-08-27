# Kanban Dispatcher Crash Diagnosis

When all kanban workers crash (not just one bad card), the problem is
dispatcher/config-level. Checklist for diagnosing from a terminal.

## Crash patterns

Check `task_runs` in the board DB:

```bash
DB=~/.hermes/kanban/boards/<board>/kanban.db
sqlite3 -header -column "$DB" "select id, task_id, outcome, error from task_runs order by rowid desc limit 10;"
```

Worker logs: `~/.hermes/kanban/boards/<board>/logs/<task_id>.log`

| `outcome` | `error` pattern | Root cause | Fix |
|---|---|---|---|
| `crashed` | `protocol violation` (rc=0, no kanban_complete/block) | Worker booted TUI instead of headless chat (`display.interface: tui` or inherited `HERMES_TUI=1`). TUI no-TTY bail-out prints resume banner, exits 0. | Hermes ≥2026.7.20 hardcodes `--cli` + strips `HERMES_TUI` from worker env. **Restart gateway** to load the fix. Older: set `display.interface: cli`. |
| `crashed` | `pid … exited with code 1` | Worker subprocess failed at startup (missing skill, bad profile, PATH drift). | Check `<board>/logs/<task_id>.log`; verify `hermes -p <assignee> doctor`. |
| `crashed` | `spawn_failed` | Couldn't launch the hermes binary. | Check `HERMES_BIN`, PATH in gateway's launchd plist, nix wrapper. |
| `timed_out` | — | Hit `max_runtime_seconds`. | Chunk work or raise limit. |

## Config pitfalls

### `default_assignee` empty → nothing spawns

```bash
hermes config set kanban.default_assignee default
```

### `HERMES_KANBAN_HOME` → remote mount → split DB

If `HERMES_KANBAN_HOME` is set to a macFUSE/SSHFS mount (e.g.
`~/mnt/devbox-hermes`) while the gateway process doesn't inherit it,
the gateway and CLI see **different databases** — the local gateway uses
`~/.hermes/kanban` while the shell uses the remote mount. Two dispatchers
race for the same logical board on different DBs.

`HERMES_KANBAN_HOME` is **not** set by nix-darwin or any config file — it
was inherited from a previous shell session. The launchd plist for the
gateway sets only `HERMES_HOME`, not `HERMES_KANBAN_HOME`.

Resolution: `unset HERMES_KANBAN_HOME` in `~/.<REDACTED>` so new shells
converge on `~/.hermes` (same as the gateway). The macFUSE mount can stay
for file access but kanban won't route through it.

### Two gateways racing (local Mac Pro + devbox)

Both local + devbox gateways with `dispatch_in_gateway: true` race for the
same DB. The local Mac Pro gateway uses `~/.hermes/config.yaml` (which had
`default_assignee: ''` and `display.interface: tui`), while devbox has its own
config with `default_assignee: "default"`. Workers spawned by the local
gateway crash because they inherit the local config's TUI mode and empty
assignee — even though the devbox config is correct.

Resolution: either set `kanban.dispatch_in_gateway: false` on the non-primary
machine, or ensure both configs agree. Cooper's preference: local gateway can
dispatch when work needs to happen on the Mac, but keep configs aligned
(`default_assignee: default` on both).

### Gateway must restart after Hermes upgrade

The kanban worker spawn code (`--cli` hardcode, `HERMES_TUI` strip) lives in
`kanban_db.py`. A running gateway uses old in-memory code until restarted.
After `hermes update`, always `hermes gateway restart`.

## Worker spawn command (reference)

Hermes ≥2026.7.20 builds the worker command as:

```
hermes -p <profile> --cli --accept-hooks [--skills X] [--toolsets T] chat -q <prompt> [-Q for goal mode]
```

Env stripped: `HERMES_TUI` (prevents TUI hijack).
Env set: `HERMES_KANBAN_TASK`, `HERMES_KANBAN_RUN_ID`, `HERMES_KANBAN_DB`,
`HERMES_KANBAN_BOARD`, `HERMES_KANBAN_WORKSPACE`, `TERMINAL_CWD`,
`HERMES_PROFILE`, `HERMES_HOME` (profile-scoped).
