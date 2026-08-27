#!/usr/bin/env bash
# Focused integration verifier for a Hermes skill backed by an rclone mount.
# Required environment:
#   HERMES_HOME
#   HERMES_SKILL_CATEGORY
#   HERMES_SKILL_NAME
#   HERMES_SKILL_MOUNT       Local mount root containing <skill>/SKILL.md
#   HERMES_SKILL_REMOTE      rclone remote root containing <skill>/SKILL.md
#   RCLONE_CONFIG
# Optional:
#   HERMES_SKILL_MOUNT_SERVICE  systemd service name
#   HERMES_VERIFY_ATTEMPTS      one-second polling attempts (default 45)
set -euo pipefail

required=(
  HERMES_HOME
  HERMES_SKILL_CATEGORY
  HERMES_SKILL_NAME
  HERMES_SKILL_MOUNT
  HERMES_SKILL_REMOTE
  RCLONE_CONFIG
)
for variable in "${required[@]}"; do
  [[ -n "${!variable:-}" ]] || {
    printf 'Missing required environment variable: %s\n' "$variable" >&2
    exit 2
  }
done

for command_name in rclone python3; do
  command -v "$command_name" >/dev/null 2>&1 || {
    printf 'Required command not found: %s\n' "$command_name" >&2
    exit 3
  }
done

attempts="${HERMES_VERIFY_ATTEMPTS:-45}"
[[ "$attempts" =~ ^[1-9][0-9]*$ ]] || {
  printf 'HERMES_VERIFY_ATTEMPTS must be a positive integer\n' >&2
  exit 4
}

mount_root="${HERMES_SKILL_MOUNT%/}"
remote_root="${HERMES_SKILL_REMOTE%/}"
skill_dir="$mount_root/$HERMES_SKILL_NAME"
skill_file="$skill_dir/SKILL.md"
registration="$HERMES_HOME/skills/$HERMES_SKILL_CATEGORY/$HERMES_SKILL_NAME"
identifier="$$-$(date +%s)"
cloud_probe=".hermes-verify-cloud-$identifier"
host_probe=".hermes-verify-host-$identifier"

cleanup() {
  python3 -c 'from pathlib import Path; import sys; [Path(p).unlink(missing_ok=True) for p in sys.argv[1:]]' \
    "$mount_root/$cloud_probe" "$mount_root/$host_probe" >/dev/null 2>&1 || true
  rclone deletefile "$remote_root/$cloud_probe" --config "$RCLONE_CONFIG" >/dev/null 2>&1 || true
  rclone deletefile "$remote_root/$host_probe" --config "$RCLONE_CONFIG" >/dev/null 2>&1 || true
}
trap cleanup EXIT

fail() {
  printf 'FAIL: %s\n' "$*" >&2
  exit 1
}

if [[ -n "${HERMES_SKILL_MOUNT_SERVICE:-}" ]]; then
  command -v systemctl >/dev/null 2>&1 || fail 'systemctl unavailable for requested service check'
  systemctl is-enabled --quiet "$HERMES_SKILL_MOUNT_SERVICE" || fail 'mount service is not enabled'
  systemctl is-active --quiet "$HERMES_SKILL_MOUNT_SERVICE" || fail 'mount service is not active'
  printf 'service_ok %s\n' "$HERMES_SKILL_MOUNT_SERVICE"
fi

if command -v mountpoint >/dev/null 2>&1; then
  mountpoint -q "$mount_root" || fail 'local backing path is not a mountpoint'
fi
[[ -d "$skill_dir" ]] || fail 'mounted skill directory is missing'
[[ -r "$skill_file" && -w "$skill_file" ]] || fail 'mounted SKILL.md is not readable and writable'
[[ -L "$registration" ]] || fail 'Hermes registration is not a symlink'

resolved_registration="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$registration")"
resolved_target="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$skill_dir")"
[[ "$resolved_registration" == "$resolved_target" ]] || fail 'Hermes registration resolves to the wrong source'

python3 -c 'from pathlib import Path; import sys; expected=sys.argv[2]; text=Path(sys.argv[1]).read_text(encoding="utf-8"); assert text.startswith("---\n"), "frontmatter must start at byte 0"; assert f"name: {expected}" in text, "skill name missing from frontmatter"' \
  "$skill_file" "$HERMES_SKILL_NAME" || fail 'SKILL.md frontmatter check failed'
printf 'registration_and_frontmatter_ok\n'

hash_file() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | python3 -c 'import sys; print(sys.stdin.read().split()[0])'
  else
    shasum -a 256 "$1" | python3 -c 'import sys; print(sys.stdin.read().split()[0])'
  fi
}

hash_stream() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum | python3 -c 'import sys; print(sys.stdin.read().split()[0])'
  else
    shasum -a 256 | python3 -c 'import sys; print(sys.stdin.read().split()[0])'
  fi
}

local_hash="$(hash_file "$skill_file")"
remote_hash="$(rclone cat "$remote_root/$HERMES_SKILL_NAME/SKILL.md" --config "$RCLONE_CONFIG" | hash_stream)"
[[ "$local_hash" == "$remote_hash" ]] || fail 'local and remote SKILL.md hashes differ'
printf 'skill_hash_ok %s\n' "$local_hash"

rclone touch "$remote_root/$cloud_probe" --config "$RCLONE_CONFIG"
cloud_seen=false
attempt=1
while (( attempt <= attempts )); do
  if [[ -f "$mount_root/$cloud_probe" ]]; then
    cloud_seen=true
    printf 'remote_to_host_ok attempt=%s\n' "$attempt"
    break
  fi
  sleep 1
  attempt=$((attempt + 1))
done
[[ "$cloud_seen" == true ]] || fail 'remote-to-host propagation timed out'

python3 -c 'from pathlib import Path; import sys; Path(sys.argv[1]).write_text("Hermes rclone skill verification probe\n", encoding="utf-8")' \
  "$mount_root/$host_probe"
host_seen=false
attempt=1
while (( attempt <= attempts )); do
  listing="$(rclone lsf "$remote_root" --config "$RCLONE_CONFIG" --files-only --include "$host_probe" 2>/dev/null || true)"
  if [[ "$listing" == "$host_probe" ]]; then
    host_seen=true
    printf 'host_to_remote_ok attempt=%s\n' "$attempt"
    break
  fi
  sleep 1
  attempt=$((attempt + 1))
done
[[ "$host_seen" == true ]] || fail 'host-to-remote propagation timed out'

cleanup
trap - EXIT

remaining="$(rclone lsf "$remote_root" --config "$RCLONE_CONFIG" --files-only \
  --include "$cloud_probe" --include "$host_probe" 2>/dev/null || true)"
[[ -z "$remaining" ]] || fail 'this invocation left remote verification artifacts'
[[ ! -e "$mount_root/$cloud_probe" && ! -e "$mount_root/$host_probe" ]] || fail 'local verification artifacts remain'

printf 'probe_cleanup_ok\n'
printf 'AD_HOC_RCLONE_SKILL_SOURCE_PASS\n'
