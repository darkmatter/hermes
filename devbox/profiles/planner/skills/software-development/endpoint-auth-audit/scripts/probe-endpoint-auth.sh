#!/usr/bin/env bash
# Non-destructive auth matrix for a public HTTP endpoint.
# Usage: probe-endpoint-auth.sh <url> [optional-json-body-for-realistic-post]
set -euo pipefail

URL="${1:?usage: $0 <url> [json-body]}"
BODY="${2:-{}}"
UA="Hermes-Endpoint-Auth-Audit/1.0"

hdr() { printf '\n=== %s ===\n' "$1"; }

hdr "GET (no auth)"
curl -sS -D - -o /tmp/eaa-body.txt -A "$UA" --max-time 20 -X GET "$URL" || true
echo "--- body ---"; head -c 400 /tmp/eaa-body.txt; echo

hdr "POST empty {} (no auth)"
curl -sS -D - -o /tmp/eaa-body.txt -A "$UA" --max-time 20 -X POST "$URL" \
  -H "Content-Type: application/json" -d '{}' || true
echo "--- body ---"; head -c 400 /tmp/eaa-body.txt; echo

hdr "POST body (no auth)"
curl -sS -D - -o /tmp/eaa-body.txt -A "$UA" --max-time 20 -X POST "$URL" \
  -H "Content-Type: application/json" -d "$BODY" || true
echo "--- body ---"; head -c 400 /tmp/eaa-body.txt; echo

hdr "POST body + Authorization: Bearer <REDACTED>"
curl -sS -D - -o /tmp/eaa-body.txt -A "$UA" --max-time 20 -X POST "$URL" \
  -H "Content-Type: application/json" -H "Authorization: Bearer <REDACTED>" -d "$BODY" || true
echo "--- body ---"; head -c 400 /tmp/eaa-body.txt; echo

hdr "POST body + X-Vapi-Secret: test"
curl -sS -D - -o /tmp/eaa-body.txt -A "$UA" --max-time 20 -X POST "$URL" \
  -H "Content-Type: application/json" -H "X-Vapi-Secret: test" -d "$BODY" || true
echo "--- body ---"; head -c 400 /tmp/eaa-body.txt; echo

echo
echo "Interpret: 2xx + app JSON on no-auth POST => no auth."
echo "401/403 or CF Access redirect on no-auth, success only with real secret => auth ok."
echo "Same 2xx with wrong Bearer <REDACTED> without => secret not enforced."
