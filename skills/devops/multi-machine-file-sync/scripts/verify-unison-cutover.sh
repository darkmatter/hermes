#!/usr/bin/env bash
# Parameterized ad-hoc verifier for Mutagen→Unison hop-sync cutover.
# Not a project test suite. Override defaults via env vars.
#
# Example:
#   LOCAL_GIT="$HOME/git" REMOTE_SSH="cm@<REDACTED>" \
#   REMOTE_GIT="~/git" PROFILE=git-devbox \
#   ./scripts/verify-unison-cutover.sh
set -u
fail=0
pass() { echo "PASS: $1"; }
fail_msg() { echo "FAIL: $1"; fail=$((fail + 1)); }
check() { if eval "$2"; then pass "$1"; else fail_msg "$1"; fi; }

LOCAL_GIT="${LOCAL_GIT:-$HOME/git}"
REMOTE_SSH="${REMOTE_SSH:-cm@<REDACTED>}"
REMOTE_GIT="${REMOTE_GIT:-~/git}"
OMP_LOCAL="${OMP_LOCAL:-$HOME/.omp}"
OMP_REMOTE="${OMP_REMOTE:-~/.omp}"
PROFILE="${PROFILE:-git-devbox}"
OMP_PROFILE="${OMP_PROFILE:-omp-devbox}"
UNISON_DIR="${UNISON_DIR:-$HOME/.unison}"
STATE_DIR="${STATE_DIR:-$HOME/.local/state/unison}"
UID_N="$(id -u)"

echo "=== Unison cutover verify ==="
echo "LOCAL_GIT=$LOCAL_GIT REMOTE=$REMOTE_SSH:$REMOTE_GIT PROFILE=$PROFILE"

echo '--- versions / SSH ---'
check "local unison present" 'command -v unison >/dev/null'
LOCAL_V="$(unison -version 2>/dev/null | head -1 || true)"
REMOTE_V="$(ssh -o BatchMode=yes -o ConnectTimeout=10 "$REMOTE_SSH" 'unison -version 2>/dev/null | head -1' || true)"
echo "   local:  $LOCAL_V"
echo "   remote: $REMOTE_V"
check "remote unison present" 'test -n "$REMOTE_V"'
# Same major.minor when both report "unison version X.Y"
if [[ -n "$LOCAL_V" && -n "$REMOTE_V" ]]; then
  Lmaj="$(sed -n 's/.*version \([0-9]*\.[0-9]*\).*/\1/p' <<<"$LOCAL_V")"
  Rmaj="$(sed -n 's/.*version \([0-9]*\.[0-9]*\).*/\1/p' <<<"$REMOTE_V")"
  check "unison major.minor match ($Lmaj vs $Rmaj)" 'test -n "$Lmaj" && test "$Lmaj" = "$Rmaj"'
fi

echo '--- profiles ---'
check "profile $PROFILE exists" 'test -f "$UNISON_DIR/$PROFILE.prf"'
check "omp profile exists" 'test -f "$UNISON_DIR/$OMP_PROFILE.prf"'
PRF="$UNISON_DIR/$PROFILE.prf"
check "local root in profile" "grep -Fq 'root = $LOCAL_GIT' \"\$PRF\""
check "ssh double-slash remote root" "grep -Eq 'root = ssh://.*//.+' \"\$PRF\""
check "perms=0" "grep -Fqx 'perms = 0' \"\$PRF\""
check "links=false" "grep -Fqx 'links = false' \"\$PRF\""
check "no steady-state prefer" "! grep -Eq '^prefer =' \"\$PRF\""
check "fsmonitor ignored" "grep -q 'fsmonitor--daemon.ipc' \"\$PRF\""
# whole .git must not be ignored
if grep -Eq '^ignore = Name \.git$' "$PRF" \
  || grep -Eq '^ignore = Path \.git$' "$PRF" \
  || grep -Eq '^ignore = Path \*/\.git$' "$PRF"; then
  fail_msg "profile excludes whole .git VCS"
else
  pass "whole .git VCS not excluded"
fi

echo '--- -testserver (no file sync) ---'
check "git -testserver" "unison \"$PROFILE\" -ui text -batch -silent -testserver >/dev/null 2>&1"
check "omp -testserver" "unison \"$OMP_PROFILE\" -ui text -batch -silent -testserver >/dev/null 2>&1"

echo '--- mutagen absent ---'
check "no mutagen daemon" '! pgrep -f "mutagen daemon" >/dev/null 2>&1'
if launchctl print "gui/$UID_N" 2>&1 | grep -qi mutagen; then
  fail_msg "mutagen still in launchd"
else
  pass "no mutagen launchd services"
fi

echo '--- unison agents (label prefix may vary) ---'
LC_OUT="$(launchctl print "gui/$UID_N" 2>&1 || true)"
check "git-devbox agent loaded" 'grep -q "unison.*git-devbox\|git-devbox" <<<"$LC_OUT"'
check "omp-devbox agent loaded" 'grep -q "unison.*omp-devbox\|omp-devbox" <<<"$LC_OUT"'

# Prefer hardened silent wrapper if plists present
for pl in \
  "$HOME/Library/LaunchAgents/org.nix-community.home.dev.unison.git-devbox.plist" \
  "$HOME/Library/LaunchAgents/dev.unison.git-devbox.plist"; do
  if [[ -f "$pl" ]]; then
    arg="$(plutil -extract ProgramArguments.2 raw "$pl" 2>/dev/null || true)"
    wrap="$(sed -n 's#.* exec \(/nix/store/[^ ]*-unison-profile-git-devbox\).*#\1#p' <<<"$arg")"
    if [[ -n "${wrap:-}" && -x "$wrap" ]] && grep -q 'batch -auto -silent' "$wrap"; then
      pass "launchd wrapper uses silent batch ($pl)"
    else
      fail_msg "launchd wrapper missing silent batch ($pl)"
    fi
    break
  fi
done

echo '--- archives both replicas ---'
check "local archives" 'ls "$UNISON_DIR"/ar* >/dev/null 2>&1'
check "remote archives" "ssh -o BatchMode=yes -o ConnectTimeout=10 \"$REMOTE_SSH\" 'ls ~/.unison/ar*' >/dev/null 2>&1"
check "state dir" 'test -d "$STATE_DIR"'

if [[ "${PROBE:-0}" = "1" ]]; then
  echo '--- optional probe round-trip ---'
  name="__unison_probe_$$"
  echo "probe-$(date -u +%Y%m%dT%H%M%SZ)" >"$LOCAL_GIT/$name"
  if unison-sync "$PROFILE" >/dev/null 2>&1 || unison "$PROFILE" -ui text -batch -auto -silent >>"$STATE_DIR/probe.log" 2>&1; then
    if ssh -o BatchMode=yes "$REMOTE_SSH" "test -f $REMOTE_GIT/$name"; then
      pass "probe file appeared on remote"
    else
      fail_msg "probe missing on remote after sync"
    fi
  else
    fail_msg "probe sync command failed"
  fi
  rm -f "$LOCAL_GIT/$name"
  ssh -o BatchMode=yes "$REMOTE_SSH" "rm -f $REMOTE_GIT/$name" 2>/dev/null || true
fi

echo '---'
if [[ "$fail" -eq 0 ]]; then
  echo 'AD-HOC VERIFICATION PASSED'
  exit 0
fi
echo "AD-HOC VERIFICATION FAILED ($fail checks)"
exit 1
