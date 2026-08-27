# Unison cutover lessons (2026-08 Mac↔devbox)

Session-hardened details for seamless hop continuity. Core rules live in `SKILL.md`.

## Continuity gate

If the user wants “switch machines without feeling it,” **keep `.git`** (branch, index, stash, dirty tree). Do not recommend `ignoreVcs` / drop-`.git` + attach-on-other-side just to shrink the scanner.

## Operating models

| | Mutagen | Unison |
|---|---|---|
| Duty cycle | Always-on watch/scan/stage | Episodic batch → idle ~0 CPU |
| Cost driver | Hot trees (logs, `.git/index`, bots) more than cold bulk | First archive / interval burst |
| Hop UX | Live if healthy | Interval + `unison-sync` before/after hop |

Never dual-write Mutagen and Unison on the same tree.

## Host paths (darwin)

| Piece | Path |
|---|---|
| Unison module | `~/darwin/modules~/unison.nix` |
| Mutagen module | `~/darwin/modules~/mutagen.nix` |
| macpro | `~/darwin/homes/aarch64-darwin/cm@macpro/default.nix` |
| mbp | `~/darwin/homes/aarch64-darwin/cm@mbp/default.nix` |
| devbox | `~/darwin/homes/x86_64-linux/cm@devbox/default.nix` |
| Plan | `~/git/darkmatter/.hermes/plans/2026-08-07_125110-mutagen-to-unison-git-sync.md` |

**macpro status:** Unison `git-devbox` + `omp-devbox` enabled; Mutagen terminated.
**devbox:** `programs.mutagen.enable = false` declared/eval’d — remote activation may lag.
**mbp:** may still be Mutagen — pairwise links are not three-way merge.

## SSH / versions

```text
ssh://cm@<REDACTED>/~/git
```

Double slash before absolute remote path. Prefer full Tailscale name over Host aliases (host-key failures under Unison SSH).

```bash
unison -version
ssh -o BatchMode=yes cm@<REDACTED> 'command -v unison; unison -version'
# same 2.x both sides (observed 2.54.0)
```

Optional: `servercmd = /etc/profiles/per-user/cm/bin/unison`.

## Cross-platform prefs (macOS ↔ Linux)

```text
links = false
perms = 0
owner = false
group = false
rsrc = false
confirmbigdel = false
```

No steady-state `prefer` on source trees. Bootstrap only:

```bash
BOOTSTRAP=1 unison-sync git-devbox
```

## Ignores (keep whole `.git`)

Port Mutagen defaults plus:

```text
Name runs
Path */runs
Name *.log
Path */.cache
Path */.turbo
Name fsmonitor--daemon.ipc
Path */.git/fsmonitor--daemon.ipc
```

Whole-dir ignores like `Name .git` / `Path */.git` are forbidden for hop continuity. Specific files under `.git` (fsmonitor sockets) are OK.

## Noninteractive Unison — Sys_blocked_io

Large conflict dumps into a **pipe** abort with `Sys_blocked_io` before archives write.

```bash
# Good
unison profile -ui text -batch -auto -silent >>"$logfile" 2>&1

# Bad
unison profile 2>&1 | tee "$logfile"
```

- Pre-create `~/.local/state/unison/` (launchd opens log paths before wrapper)
- launchd wrapper must embed silent+file-log, not bare `unison <name>`
- Profiles should exist even when `pair.enable = false` so first manual pass works

## Cutover sequence

1. Match Unison versions + noninteractive SSH path
2. Profiles present; Unison agents disabled
3. Boot out Mutagen **ensure-sessions** first (it **resumes** paused sessions ~every 5m)
4. `mutagen sync pause` all clients
5. Clean inconsistent archives both sides if a prior run died
6. `BOOTSTRAP=1 unison-sync git-devbox`
7. Archives both replicas + probe file round-trip
8. Enable Unison agents; terminate Mutagen sessions + stop daemon
9. HM mutagen off on Mac; declare off on hub
10. Runtime verify ≠ flake eval alone
11. Migrate extra Macs one at a time

### Archive inconsistency

```text
Archive … MISSING on A / should be DELETED on B
```

Delete named archives on **both** sides with bash nullglob on remote:

```bash
ssh host 'bash -lc "shopt -s nullglob; rm -f ~/.unison/arHASH* ~/.unison/fpHASH*"'
```

### Mutagen pause pitfall

`mutagen sync pause` alone fails if ensure-sessions still runs (`sync resume`). Bootout ensure-sessions first.

## Validation layers

| Layer | Means |
|---|---|
| Source | git commit in `~/darwin` |
| Eval | flake `programs.mutagen.enable = false` |
| Built | nix build HM generation |
| Local activate | HM `activate` as user (may skip full sudo darwin-rebuild) |
| Remote activate | separate rebuild on devbox |
| Runtime | pgrep, launchd labels, archives, `-testserver` |

HM launchd labels often: `org.nix-community.home.dev.unison.git-devbox`.

## Hop UX

```bash
unison-sync git-devbox
unison-sync omp-devbox
unison-sync all
unison-sync -i git-devbox
```

Live `.git/index` skips under concurrent edit are expected.

## Session notes (2026-08-07)

- Tree ~541k files / 30 GB; `.git` retained intentionally
- Bootstrap transferred ~526k items; residual failures = live indexes / hot files
- Warm pass shipped probe Mac→devbox
- Mutagen sessions terminated; daemon stopped on macpro
- Full sudo `./rebuild.sh` blocked on password; user HM activate still landed prfs/agents
- Parameterized verifier: `scripts/verify-unison-cutover.sh`

## Related

Audinate `conmon_cmm` ≠ container conmon — skill `macos-local-performance`.
