#!/usr/bin/env bash
# Query Vapi analytics (POST /analytics) and/or list/get calls.
# Auth: 1Password item `vapi` credential field, or VAPI_API_KEY / ~/.vapi-cli.yaml
#
# Usage:
#   vapi_analytics.sh                  # default dashboard (7d summary)
#   vapi_analytics.sh summary [--days N] [--tz ZONE] [--step day|hour|week]
#   vapi_analytics.sh cost [--days N] [--step day|hour|week]
#   vapi_analytics.sh ends [--days N]
#   vapi_analytics.sh status [--days N]
#   vapi_analytics.sh success [--days N]
#   vapi_analytics.sh query '<json queries array or full body>'
#   vapi_analytics.sh calls [limit]
#   vapi_analytics.sh get <call_id>
#   vapi_analytics.sh raw --file query.json
#   vapi_analytics.sh cli <vapi-cli-args...>
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=vapi_env.sh
source "$SCRIPT_DIR/vapi_env.sh"

usage() {
  sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

json_post_analytics() {
  local body="$1"
  curl -sS -X POST "${VAPI_BASE_URL}/analytics" \
    -H "Authorization: Bearer <REDACTED>" \
    -H "Content-Type: application/json" \
    -d "$body"
}

pretty() {
  python3 -m json.tool
}

iso_days_ago() {
  python3 -c 'import sys; from datetime import datetime,timedelta,timezone; d=int(sys.argv[1]); print((datetime.now(timezone.utc)-timedelta(days=d)).strftime("%Y-%m-%dT%H:%M:%SZ"))' "${1:-7}"
}

iso_now() {
  python3 -c 'from datetime import datetime,timezone; print(datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))'
}

build_summary_body() {
  local days="${1:-7}"
  local tz="${2:-America/Los_Angeles}"
  local step="${3:-day}"
  local start end
  start="$(iso_days_ago "$days")"
  end="$(iso_now)"
  DAYS="$days" TZ_NAME="$tz" STEP="$step" START="$start" END="$end" python3 - <<'PY'
import json, os
start, end, tz, step = os.environ["START"], os.environ["END"], os.environ["TZ_NAME"], os.environ["STEP"]
tr = {"start": start, "end": end, "timezone": tz, "step": step}
queries = [
  {"table":"call","name":"call_counts_by_status","groupBy":["status"],"timeRange":tr,
   "operations":[{"operation":"count","column":"id","alias":"calls"}]},
  {"table":"call","name":"call_ends","groupBy":["endedReason"],"timeRange":tr,
   "operations":[
     {"operation":"count","column":"id","alias":"calls"},
     {"operation":"sum","column":"duration","alias":"sumDuration"},
     {"operation":"sum","column":"cost","alias":"sumCost"}]},
  {"table":"call","name":"cost_and_duration","timeRange":tr,
   "operations":[
     {"operation":"count","column":"id","alias":"calls"},
     {"operation":"sum","column":"duration","alias":"sumDuration"},
     {"operation":"avg","column":"duration","alias":"avgDuration"},
     {"operation":"sum","column":"cost","alias":"sumCost"},
     {"operation":"avg","column":"cost","alias":"avgCost"}]},
  {"table":"call","name":"success_eval","groupBy":["analysis.successEvaluation"],"timeRange":tr,
   "operations":[{"operation":"count","column":"id","alias":"calls"}]},
  {"table":"call","name":"daily_volume","timeRange":{**tr,"step":step},
   "operations":[
     {"operation":"count","column":"id","alias":"calls"},
     {"operation":"sum","column":"cost","alias":"sumCost"},
     {"operation":"sum","column":"duration","alias":"sumDuration"}]},
]
print(json.dumps({"queries": queries}))
PY
}

build_group_body() {
  local name="$1"
  local group_by="$2"
  local days="${3:-7}"
  local tz="${4:-America/Los_Angeles}"
  local step="${5:-}"
  local start end
  start="$(iso_days_ago "$days")"
  end="$(iso_now)"
  NAME="$name" GROUP_BY="$group_by" START="$start" END="$end" TZ_NAME="$tz" STEP="$step" python3 - <<'PY'
import json, os
tr = {"start": os.environ["START"], "end": os.environ["END"], "timezone": os.environ["TZ_NAME"]}
step = os.environ.get("STEP") or ""
if step:
    tr["step"] = step
q = {
    "table": "call",
    "name": os.environ["NAME"],
    "groupBy": [os.environ["GROUP_BY"]],
    "timeRange": tr,
    "operations": [
        {"operation": "count", "column": "id", "alias": "calls"},
        {"operation": "sum", "column": "duration", "alias": "sumDuration"},
        {"operation": "sum", "column": "cost", "alias": "sumCost"},
        {"operation": "avg", "column": "cost", "alias": "avgCost"},
    ],
}
print(json.dumps({"queries": [q]}))
PY
}

build_cost_body() {
  local days="${1:-7}"
  local tz="${2:-America/Los_Angeles}"
  local step="${3:-day}"
  local start end
  start="$(iso_days_ago "$days")"
  end="$(iso_now)"
  START="$start" END="$end" TZ_NAME="$tz" STEP="$step" python3 - <<'PY'
import json, os
tr = {"start": os.environ["START"], "end": os.environ["END"], "timezone": os.environ["TZ_NAME"], "step": os.environ["STEP"]}
q = {
    "table": "call",
    "name": "cost_series",
    "timeRange": tr,
    "operations": [
        {"operation": "count", "column": "id", "alias": "calls"},
        {"operation": "sum", "column": "cost", "alias": "sumCost"},
        {"operation": "avg", "column": "cost", "alias": "avgCost"},
        {"operation": "sum", "column": "duration", "alias": "sumDuration"},
        {"operation": "sum", "column": "costBreakdown.llm", "alias": "sumLlm"},
        {"operation": "sum", "column": "costBreakdown.stt", "alias": "sumStt"},
        {"operation": "sum", "column": "costBreakdown.tts", "alias": "sumTts"},
        {"operation": "sum", "column": "costBreakdown.vapi", "alias": "sumVapi"},
        {"operation": "sum", "column": "costBreakdown.transport", "alias": "sumTransport"},
    ],
}
print(json.dumps({"queries": [q]}))
PY
}

parse_days_tz_step() {
  DAYS=7
  TZ_NAME="America/Los_Angeles"
  STEP=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --days) DAYS="$2"; shift 2 ;;
      --tz) TZ_NAME="$2"; shift 2 ;;
      --step) STEP="$2"; shift 2 ;;
      -h|--help) usage 0 ;;
      *) echo "unknown flag: $1" >&2; usage 1 ;;
    esac
  done
}

cmd="${1:-summary}"
shift || true

case "$cmd" in
  -h|--help|help) usage 0 ;;

  summary|dashboard|default)
    parse_days_tz_step "$@"
    STEP="${STEP:-day}"
    body="$(build_summary_body "$DAYS" "$TZ_NAME" "$STEP")"
    json_post_analytics "$body" | pretty
    ;;

  ends|ended|end-reason|endedReason)
    parse_days_tz_step "$@"
    body="$(build_group_body "call_ends" "endedReason" "$DAYS" "$TZ_NAME" "$STEP")"
    json_post_analytics "$body" | pretty
    ;;

  status)
    parse_days_tz_step "$@"
    body="$(build_group_body "call_status" "status" "$DAYS" "$TZ_NAME" "$STEP")"
    json_post_analytics "$body" | pretty
    ;;

  success|success-eval)
    parse_days_tz_step "$@"
    body="$(build_group_body "success_eval" "analysis.successEvaluation" "$DAYS" "$TZ_NAME" "$STEP")"
    json_post_analytics "$body" | pretty
    ;;

  cost|costs)
    parse_days_tz_step "$@"
    STEP="${STEP:-day}"
    body="$(build_cost_body "$DAYS" "$TZ_NAME" "$STEP")"
    json_post_analytics "$body" | pretty
    ;;

  query)
    raw="${1:-}"
    if [[ -z "$raw" ]]; then
      echo "usage: vapi_analytics.sh query '<json>'" >&2
      exit 1
    fi
    body="$(RAW_JSON="$raw" python3 - <<'PY'
import json, os
obj = json.loads(os.environ["RAW_JSON"])
if isinstance(obj, list):
    obj = {"queries": obj}
elif isinstance(obj, dict) and "queries" not in obj:
    obj = {"queries": [obj]}
print(json.dumps(obj))
PY
)"
    json_post_analytics "$body" | pretty
    ;;

  raw)
    file=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --file|-f) file="$2"; shift 2 ;;
        *) echo "usage: vapi_analytics.sh raw --file query.json" >&2; exit 1 ;;
      esac
    done
    [[ -n "$file" && -f "$file" ]] || { echo "missing --file" >&2; exit 1; }
    json_post_analytics "$(cat "$file")" | pretty
    ;;

  calls|list)
    limit="${1:-20}"
    tmp="$(mktemp)"
    curl -sS -H "Authorization: Bearer <REDACTED>"       "${VAPI_BASE_URL}/call?limit=${limit}" -o "$tmp"
    python3 - "$tmp" <<'PY'
import sys, json
rows = json.load(open(sys.argv[1]))
if not isinstance(rows, list):
    print(json.dumps(rows, indent=2))
    raise SystemExit(0)
print(f"{'id':36}  {'status':12}  {'endedReason':28}  {'cost':8}  {'startedAt':20}  customer")
for d in rows:
    cid = d.get("id", "")
    st = d.get("status", "") or ""
    er = (d.get("endedReason") or "")[:28]
    cost = d.get("cost")
    cost_s = f"${cost:.2f}" if isinstance(cost, (int, float)) else "-"
    started = (d.get("startedAt") or d.get("createdAt") or "")[:19]
    cust = (d.get("customer") or {}).get("number") or ""
    print(f"{cid:36}  {st:12}  {er:28}  {cost_s:8}  {started:20}  {cust}")
print(f"\n{len(rows)} call(s)")
PY
    rm -f "$tmp"
    ;;

  get)
    cid="${1:-}"
    [[ -n "$cid" ]] || { echo "usage: vapi_analytics.sh get <call_id>" >&2; exit 1; }
    tmp="$(mktemp)"
    curl -sS -H "Authorization: Bearer <REDACTED>"       "${VAPI_BASE_URL}/call/${cid}" -o "$tmp"
    python3 - "$tmp" <<'PY'
import sys, json
d = json.load(open(sys.argv[1]))
keep = ["id","status","type","endedReason","startedAt","endedAt","cost",
        "phoneNumberId","assistantId","customer","forwardedPhoneNumber","destination"]
out = {k: d.get(k) for k in keep}
out["customer"] = (d.get("customer") or {}).get("number")
analysis = d.get("analysis") or {}
out["summary"] = analysis.get("summary") or d.get("summary")
out["successEvaluation"] = analysis.get("successEvaluation")
t = d.get("transcript") or ""
out["transcript_preview"] = (t[:2000] + "...") if len(t) > 2000 else (t or None)
out["transcript_len"] = len(t)
print(json.dumps(out, indent=2))
PY
    rm -f "$tmp"
    ;;

  cli)
    if ! command -v vapi >/dev/null 2>&1; then
      echo "vapi CLI not on PATH (expected ~/.vapi/bin or ~/.local/bin)" >&2
      exit 1
    fi
    exec vapi "$@"
    ;;

  *)
    echo "unknown command: $cmd" >&2
    usage 1
    ;;
esac
