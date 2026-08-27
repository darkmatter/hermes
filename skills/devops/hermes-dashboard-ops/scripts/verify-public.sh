#!/usr/bin/env bash
# Ad-hoc public + origin + gateway checks for hermes.cm.xyz (no secrets printed).
# Parse JSON with python — do not grep boolean fields.
set -euo pipefail
fail=0
ok() { echo "OK  $1"; }
bad() { echo "FAIL $1"; fail=1; }
check() { local n="$1"; shift; if "$@"; then ok "$n"; else bad "$n"; fi; }

HOST="${HERMES_PUBLIC_HOST:-https://hermes.cm.xyz}"
UA="${HERMES_CURL_UA:-Mozilla/5.0}"

code=$(curl -sS -A "$UA" -o /tmp/hermes-v-body -w '%{http_code}' --max-time 15 "$HOST/" || echo 000)
check "public / is 302" test "$code" = "302"
loc=$(curl -sS -A "$UA" -I --max-time 15 "$HOST/" 2>/dev/null | awk 'tolower($1)=="location:"{print $2}' | tr -d '\r')
check "public / -> login" bash -c "[[ \"$loc\" == *'/login'* ]]"

curl -sS -A "$UA" --max-time 15 "$HOST/api/status" -o /tmp/hermes-v-status || true
check "public status body" test -s /tmp/hermes-v-status
if python3 - <<'PY'
import json
d=json.load(open("/tmp/hermes-v-status"))
assert "version" in d
running = d.get("gateway_running")
state = d.get("gateway_state")
overall = d.get("overall")
plats = d.get("gateway_platforms") or {}
print("version", d.get("version"))
print("gateway_running", running, "state", state, "overall", overall)
print("platforms", {k: (v or {}).get("state") for k,v in plats.items()})
if running is not None:
    assert running is True, running
    assert state == "running", state
    assert overall == "ok", overall
    if "telegram" in plats:
        assert plats["telegram"].get("state") == "connected"
PY
then ok "public /api/status JSON healthy"
else bad "public /api/status JSON healthy"
fi

if command -v ssh >/dev/null && ssh -o BatchMode=yes -o ConnectTimeout=8 devbox true 2>/dev/null; then
  ssh -o BatchMode=yes -o ConnectTimeout=12 devbox '
    set -e
    systemctl --user is-active hermes-serve.service >/dev/null
    systemctl --user is-active hermes-gateway.service >/dev/null
    ss -lnt | grep -q ":9119"
    test "$(curl -sS -o /dev/null -w "%{http_code}" --max-time 5 http://127.0.0.1:9119/api/status)" = "200"
    pid=$(systemctl --user show -p MainPID --value hermes-gateway.service)
    test -n "$pid" && test "$pid" != "0"
    tr "\0" " " < /proc/$pid/cmdline | grep -q "^hermes "
    python3 - <<PY
import json, urllib.request
with urllib.request.urlopen("http://127.0.0.1:9119/api/status", timeout=5) as r:
    d = json.load(r)
assert d.get("gateway_running") is True
assert d.get("overall") == "ok"
print("local_ok")
PY
  ' && ok "devbox origin+gateway argv0" || bad "devbox origin+gateway argv0"
else
  echo "SKIP devbox ssh"
fi

echo "summary fail=$fail"
exit "$fail"
