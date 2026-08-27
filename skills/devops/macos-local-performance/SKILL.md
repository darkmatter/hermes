---
name: macos-local-performance
description: "Use when Cooper's Mac is hot, slow, or high CPU/load."
---

# macOS local performance

Diagnose high CPU, load, fans, or "mystery system processes" on Cooper's Mac (M2 Ultra / nix-darwin host). Prefer real process evidence over Activity Monitor vibes.

## Default workflow

1. **Snapshot loaders** (batch):
   ```bash
   ps auxwwr | head -25
   top -l 2 -n 15 -stats pid,command,cpu,mem,time,user | tail -30
   uptime
   memory_pressure 2>/dev/null | head -20
   pmset -g therm 2>/dev/null
   ```
2. **Resolve mystery names** via full path, not the short `COMMAND` column:
   ```bash
   ps -p <PID> -o pid,user,pcpu,pmem,command=
   pgrep -lf <name>
   ls -la "/path/from/command"
   pkgutil --pkgs | rg -i '<vendor>'
   ls /Library/LaunchDaemons /Library/LaunchAgents ~/Library/LaunchAgents | rg -i '<hint>'
   ```
3. **Classify** each top burner:
   - User app (Zed, Chrome, Warp, Cursor) → quit/reload/disable extension
   - Language servers (`tsc`, `tsserver`, `tsgo`) → restart editor or disable the extension
   - Sync daemons (mutagen, dropbox-like) → `mutagen sync list` / pause heavy sessions
   - Vendor always-on helpers (audio, VPN, metrics) → launchd disable if not needed
   - `kernel_task` → **symptom**, not target; fix the cause (thermal, I/O, runaway userland, drivers)
   - `WindowServer` → too many GPU/UI clients; close heavy browsers/editors
4. **Act in safe order**: pause sync → stop unused vendor daemons → rein in editor LSPs → browsers last if still hot.
5. **Verify**: process gone, launchd state, and that the user's real device path still works (e.g. audio output still UA).

## `kernel_task` (do not kill)

- PID 0 / system accounting. High CPU often means thermal/power management, driver work, networking, or memory pressure bookkeeping.
- Check `pmset -g therm`, disk `iostat`, and which userland processes are feeding it.
- Never `kill` it; remove the load sources.

## Name collisions / lookalikes

| Looks like | Often actually | Path / how to tell |
|---|---|---|
| `conmon` / `conmon_cmm` | **Audinate Dante ConMon**, not container runtime conmon | `/Library/Application Support/Audinate/ConMon.bundle/.../conmon_cmm` + `com.audinate.dante.ConMon` |
| `stable` | Warp terminal | `/Applications/Warp.app/...` |
| High `sysmond` | System stats collector under load | Usually secondary to other burners |

See `references/audinate-conmon.md` for Dante/UA specifics on Cooper's machine.

## Permanent disable pattern (launchd system daemons)

Stop now + survive reboot (keep files for reverse):

```bash
sudo launchctl bootout system /Library/LaunchDaemons/<label>.plist 2>/dev/null || true
sudo launchctl disable system/<label>
# verify
sudo launchctl print-disabled system | rg '<label>'
pgrep -lf '<binary>' || echo gone
# bootstrap should refuse while disabled
sudo launchctl bootstrap system /Library/LaunchDaemons/<label>.plist  # expect failure
```

Re-enable:

```bash
sudo launchctl enable system/<label>
sudo launchctl bootstrap system /Library/LaunchDaemons/<label>.plist
```

## Common Cooper hot spots (check these early)

- **Zed + tsgo/tsserver** — editor + TypeScript LSP can dominate multi-core + multi‑GB RSS
- **mutagen** — full `~/git` sync (~hundreds of k files) → `mutagen sync list`; pause with `mutagen sync pause <name>`
- **Chrome + Dia** (+ WindowServer) — multi-browser UI cost
- **Audinate ConMon** — not needed for UA Thunderbolt speakers alone; permanently disable if Dante unused
- **UA stack** — keep `com.uaudio.*` / UA Mixer Engine when using Apollo/Thunderbolt monitors; that is separate from Audinate

## Reporting style

- Lead with a short table: process → CPU → what it is → killable?
- Separate **symptom** (`kernel_task`) from **cause** (named userland)
- Give exact disable/re-enable commands; confirm device still works after stopping audio-adjacent helpers

## Pitfalls

- Do not assume `conmon*` is Podman/Docker — always check path
- `kill` without `launchctl disable` → process returns on reboot (and often immediately via KeepAlive)
- Disabling Audinate ≠ uninstalling UA; don't remove `com.uaudio.*` when only ConMon is the pig
- Memory pressure on large-RAM Macs can still show compressor activity; free-% alone is not the full story — use RSS of top processes
- Don't recommend killing `WindowServer`, `coreaudiod`, or `kernel_task`

## References

- `references/audinate-conmon.md` — Dante ConMon vs UA Thunderbolt, disable state on Cooper's Mac
