# ~/darwin Zed settings + sops-nix template

Session (2026-07-31): Zed stopped applying `settings.json` edits after sops-nix rendered secrets onto the live path. Cooper asked to undo rendering (placeholders) to validate mutability.

## Layout

| Path | Role |
|------|------|
| `~/darwin/files/config/zed/settings.json.example` | Placeholder template (`__ZED_GITHUB_TOKEN__`, `__ZED_SANITY_TOKEN__`) |
| `~/darwin/files/config/zed/settings.json` | Intended mutable SoT (unison ↔ `~/.config/zed`) |
| `~/darwin/modules/darwin/secrets.nix` | `sops.secrets` for `zed-github-token` / `zed-sanity-token`; optional `sops.templates."zed-settings.json"` |
| `~/darwin/modules~ | unison `dotconfig` pair; may `-ignore Path zed/settings.json` while template owns live path |
| `~/darwin/modules~/zed.nix` | Documents mutable SoT; `mutableUserSettings = true` |
| `~/.config/zed/settings.json` | What Zed loads |

## Failure mode

Template shape (when enabled):

```nix
sops.templates."zed-settings.json" = {
  path = "${user.homeDirectory}/.config/zed/settings.json";
  content = builtins.replaceStrings
    [ "__ZED_GITHUB_TOKEN__" "__ZED_SANITY_TOKEN__" ]
    [ config.sops.placeholder."zed-github-token" config.sops.placeholder."zed-sanity-token" ]
    (builtins.readFile "${gitRoot}/files/config/zed/settings.json.example");
};
```

Observed live state before undo:

- `~/.config/zed/settings.json` → `/run/secrets/rendered/zed-settings.json`
- Repo `files/config/zed/settings.json` was also a **git symlink** (`120000`) to that rendered path
- Unison ignored `zed/settings.json` so secret-filled render never became git SoT

Effect: edit → reload/commit flow broken; UI writes don't land on a normal mutable file.

## Undo applied (no rebuild unless asked)

1. Backup → `~/.config/zed/settings.json.sops-rendered.bak` (gitignored; do not dump).
2. Replaced repo symlink with a **real file**; tokens → placeholders.
3. `ln -sfn ~/darwin/files/config/zed/settings.json ~/.config/zed/settings.json`
4. Disabled `sops.templates."zed-settings.json"` in `modules/darwin/secrets.nix` (comment left in place).
5. Removed unison `-ignore Path zed/settings.json` in `modules~
6. Warned: current generation can re-hijack on activation until rebuild.

## Quick checks

```bash
ls -la ~/.config/zed/settings.json ~/darwin/files/config/zed/settings.json
git -C ~/darwin ls-files -s files/config/zed/settings.json
rg -n 'sops\.templates|zed-settings|ZED_GITHUB|Path zed/settings' \
  ~/darwin/modules/darwin/secrets.nix ~/darwin/modules~
rg -n 'github_personal_access_token|Authorization' \
  ~/darwin/files/config/zed/settings.json   # should show __ZED_* only
```

## Re-enable later

Prefer non-hijacking design: sidecar render, env/MCP secret injection, or app-supported includes — not owning the primary watched `settings.json`. Never commit rendered bodies; never leave repo path as symlink into `/run/secrets`.
