# Unison ← Mutagen cutover notes

## Why Mutagen hurt on this tree

- Session `git`: `~/git` ↔ `cm@<REDACTED>:~/git`
- ~180k dirs / ~540k files / ~30 GB; often stuck **Scanning files**
- Continuous two-way-safe + VCS propagate + live writers (IDE git, bots under `sol-dip-buyer/runs`)
- `.git` alone ~21k files / ~16 GB — **keep it** for hop UX; shrink elsewhere

## Unison module gaps (pre-migration)

`programs.unison-sync` today:

- launchd only; hardcodes `-batch -auto -prefer newer`
- Dropbox `__DROPBOX__` resolver
- local roots / argv — **no first-class SSH root/profile/CLI**
- logs under `/tmp/unison-*.log`

Extend before relying on it for `~/git`: SSH roots, `~/.unison/<name>.prf`, `unison-sync` helper, logs under `~/.local/state/unison/`.

## Suggested SSH root form

```text
ssh://cm@<REDACTED>/~/git
```

Validate remote binary for non-interactive SSH:

```bash
ssh cm@<REDACTED> 'unison -version'
# local
unison -version   # expect same 2.x series (was 2.54.x)
```

If PATH missing on remote non-login shell, use absolute `-servercmd` to nix profile unison.

## Ignore starters (Unison syntax; keep .git)

```text
Name node_modules
Name .venv
Name target
Name dist
Name .next
Name __pycache__
Name .direnv
Name .devenv
Name .DS_Store
Name *.tmp
Name *.log
Path */runs
Path */.cache
Path */.turbo
Path */.parcel-cache
Path */coverage
Path */.venv-*
Path */.mutagen
Path */.mutagen-*-staging
Name .pre-commit-config.yaml
Name treefmt.toml
Name process-compose.yaml
Name .test.sh
Path */.tasks/bin
Path */.github/workflows/agenix-rekey.yaml
```

Omp pair extras: `*.db`, `*.db-shm`, `*.db-wal`, `cache`, `logs`, `webcache`, `run`, agent blobs/sessions, auth tokens — mirror mutagen omp ignores on macpro.

Symlinks: macpro mutagen used `--symlink-mode ignore`; set Unison `links` consistently.

## Cutover checklist

1. `mutagen sync pause git` (+ `omp` if present) on every Mac client
2. Clean obvious conflict paths once (runs thrash, dual `.git/index`)
3. First `unison git-devbox` manual (text UI if needed) → build archives
4. Probe file + `git status -sb` both sides
5. Enable launchd pair; terminate mutagen sessions; HM disable mutagen clients + devbox hub
6. `pgrep -lf mutagen` clear; unison idle between intervals

## Never dual-write

Mutagen ensure-sessions (`dev.mutagen.*`) will respawn sessions if HM still enables them. Boot out agents after disable.

## Plan artifact

Full implementation plan:
`~/git/darkmatter/.hermes/plans/2026-08-07_125110-mutagen-to-unison-git-sync.md`

## Dante ConMon (unrelated CPU trap)

```bash
# already done for Cooper — re-enable only if Dante needed
sudo launchctl disable system/com.audinate.dante.ConMon
# re-enable:
# sudo launchctl enable system/com.audinate.dante.ConMon
# sudo launchctl bootstrap system /Library/LaunchDaemons/com.audinate.dante.ConMon.plist
```

`conmon_cmm` ≠ container runtime. Leave `com.uaudio.*` alone for Apollo/UA playback.
