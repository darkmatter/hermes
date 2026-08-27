# Dropbox + rclone + NixOS Recipe

Use this reference when a Hermes skill should be edited through Dropbox on a workstation while Hermes runs on a NixOS server. The pattern generalizes to other rclone remotes, but provider authorization and change polling differ.

## Resulting Topology

```text
Dropbox/Hermes Skills/<skill>/
        ↓ Dropbox API through rclone
<server-home>/Dropbox-Hermes-Skills/<skill>/
        ↓ symlink
$HERMES_HOME/skills/<category>/<skill>
```

Mount only the `Hermes Skills` subtree. The API token may still have wider Dropbox account scope; the narrow mount limits accidental filesystem exposure, not the token's provider-side authority.

## 1. Authorize on a Browser-Capable Workstation

When the server has no usable local browser, run Dropbox OAuth on the workstation:

```bash
umask 077
rclone authorize dropbox > "$HOME/Downloads/hermes-dropbox-token.json"
```

Approve access in the browser, then transfer the token file over a secure one-time channel such as Taildrop, an authenticated SSH copy, or a secret manager. Do not paste the JSON into chat.

Important handling rules:

- Treat the file as a credential even if rclone wraps it in JSON.
- Keep stdout/stderr out of shared logs.
- Remove the workstation copy after confirmed transfer.
- Store the server config with mode `0600`.
- Do not put token contents in a Nix expression: values interpolated into derivations or units can enter the world-readable Nix store.

Some `rclone authorize` versions emit explanatory text around the JSON. Parse the received file and select the JSON object containing `access_token`; do not print the object while validating it. Write a compact JSON value into a protected rclone config section:

```ini
[hermes-dropbox]
type = dropbox
token = <REDACTED>
```

Prefer writing the protected config file directly over passing the token as a command-line argument, which can expose it through process inspection.

Validate authorization without listing private folder names:

```bash
rclone about hermes-dropbox: \
  --config "$HOME/.config/rclone/rclone.conf" --json
```

Done when the command succeeds, only non-sensitive capacity metadata is printed, and the transferred token artifact is gone.

## 2. Seed the Remote Subtree

Choose a human-facing folder such as `Dropbox/Hermes Skills`. Seed the complete skill directory before mounting or changing registration:

```bash
rclone copyto \
  /path/to/current-skill/SKILL.md \
  'hermes-dropbox:Hermes Skills/<skill>/SKILL.md' \
  --config "$HOME/.config/rclone/rclone.conf"
```

Use `rclone copy` for a skill with support directories. Compare a local SHA-256 with `rclone cat ... | sha256sum` before cutover.

Done when every skill file exists remotely and `SKILL.md` hashes match.

## 3. Prove the Mount Interactively

Create the future mountpoint and run a foreground or managed-background proof:

```bash
rclone mount 'hermes-dropbox:Hermes Skills' \
  /path/to/Dropbox-Hermes-Skills \
  --config /path/to/rclone.conf \
  --vfs-cache-mode writes \
  --dir-cache-time 1m \
  --poll-interval 15s
```

Check the actual mountpoint and target file; service state alone is not readiness evidence.

If an unprivileged FUSE mount fails but the same command works as root, use a root system service and add:

```text
--uid <hermes-uid> --gid <hermes-gid> --umask 022 --allow-other
```

Use explicit, verified numeric IDs. Do not assume `1000:100` on an unfamiliar host.

Done when the Hermes runtime identity can read and write the mounted skill.

## 4. Declare the NixOS Service

NixOS manages `/etc`; do not install an imperative unit there. Add a service to the host configuration. This template keeps OAuth mutable and outside the Nix store:

```nix
let
  skillMount = "${user.homeDirectory}/Dropbox-Hermes-Skills";
  rcloneConfig = "${user.homeDirectory}/.config/rclone/rclone.conf";
  # Set these from the host's declared user/group IDs.
  skillUid = "<numeric-uid>";
  skillGid = "<numeric-gid>";
in
{
  systemd.tmpfiles.rules = [
    "d ${skillMount} 0755 ${user.username} users -"
  ];

  systemd.services.hermes-dropbox-skills = {
    description = "Dropbox-backed editable Hermes skills";
    wantedBy = [ "multi-user.target" ];
    wants = [ "network-online.target" ];
    after = [ "network-online.target" ];

    # If Hermes must discover these skills during boot, order the mount first.
    before = [ "hermes-agent.service" ];

    environment.HOME = user.homeDirectory;

    serviceConfig = {
      User = "root";
      Group = "root";
      ExecStart = lib.escapeShellArgs [
        "${pkgs.rclone}/bin/rclone"
        "mount"
        "hermes-dropbox:Hermes Skills"
        skillMount
        "--config" rcloneConfig
        "--cache-dir" "${user.homeDirectory}/.cache/rclone-hermes-dropbox"
        "--vfs-cache-mode" "writes"
        "--dir-cache-time" "1m"
        "--poll-interval" "15s"
        "--uid" skillUid
        "--gid" skillGid
        "--umask" "022"
        "--allow-other"
        "--log-level" "INFO"
      ];
      Restart = "on-failure";
      RestartSec = 5;
      KillSignal = "SIGTERM";
      TimeoutStopSec = 30;
    };
  };
}
```

If the Hermes unit should fail rather than start without the mount, add an explicit dependency appropriate to the host (`requires`/`after`) after testing reboot behavior. Avoid creating a dependency cycle.

### Dirty configuration repositories

A rebuild evaluates working-tree changes. If unrelated edits are present:

1. Commit only the mount-service file.
2. Build from a clean detached worktree or exact committed revision.
3. Run `nixos-rebuild build` before `switch`.
4. Switch from the same clean source.
5. Confirm the unrelated working-tree edits remain untouched.

Done when the build succeeds, the service is enabled and active, and the mountpoint becomes ready after startup.

## 5. Atomically Register the Skill

Create a temporary sibling link and rename it over the runtime registration:

```bash
registration="$HERMES_HOME/skills/<category>/<skill>"
target="/path/to/Dropbox-Hermes-Skills/<skill>"
temporary="$(dirname "$registration")/.<skill>.new"

rm -f "$temporary"
ln -s "$target" "$temporary"
mv -Tf "$temporary" "$registration"
```

Before this step, retain the old source. Afterward, inspect both `readlink "$registration"` and the fully resolved `SKILL.md` path.

Done when the registration resolves to the mounted Dropbox directory.

## 6. Verify Both Directions

Use the bundled verifier from this skill:

```bash
HERMES_HOME=/path/to/hermes-home \
HERMES_SKILL_CATEGORY=email \
HERMES_SKILL_NAME=<skill> \
HERMES_SKILL_MOUNT=/path/to/Dropbox-Hermes-Skills \
HERMES_SKILL_REMOTE='hermes-dropbox:Hermes Skills' \
RCLONE_CONFIG=/path/to/rclone.conf \
HERMES_SKILL_MOUNT_SERVICE=hermes-dropbox-skills.service \
  bash scripts/verify-rclone-skill-source.sh
```

The script checks service/mount readiness, registration, frontmatter, local/remote hash equality, Dropbox → host propagation, host → Dropbox propagation, and probe cleanup. Its result is focused ad-hoc integration evidence, not a repository-wide test-suite result.

Also load the skill with `skill_view` and confirm the expected metadata. Use `/reload-skills` for registration changes and a new session when already-loaded instructions must be refreshed.

Done when the verifier passes, `skill_view` succeeds, and no `.hermes-verify-*` files remain locally or remotely.

## Rollback

If verification fails before deleting the old source:

1. Repoint registration atomically to the old directory.
2. Stop or disable the new mount service if it is causing instability.
3. Preserve the remote copy for diagnosis; do not treat it as live.
4. Resolve transport, ownership, or polling issues before attempting another cutover.

Never delete the only known-good source during rollback.
