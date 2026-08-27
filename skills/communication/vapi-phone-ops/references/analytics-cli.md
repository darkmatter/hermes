# Vapi analytics + CLI reference

## Paths

| Piece | Location |
|---|---|
| CLI binary | `~/.vapi/bin/vapi` → `~/.local/bin/vapi` |
| CLI config | `~/.vapi-cli.yaml` (mode 600), key = private |
| Env helper | `~/.hermes/skills/communication/communications/scripts/vapi_env.sh` |
| Analytics/list helper | `.../communications/scripts/vapi_analytics.sh` |
| Call watcher | `.../communications/scripts/watch_call.sh` |

Resolve key order in `vapi_env.sh`: `VAPI_API_KEY` / `VAPI_KEY` → `op item get vapi --fields credential --reveal` → `~/.vapi-cli.yaml`.

Standing exports: `VAPI_ASSISTANT_ID=86a092df-...`, `VAPI_PHONE_NUMBER_ID=68092f67-...`, `VAPI_BASE_URL=https://api.vapi.ai`.

## Install

```bash
curl -sSL https://vapi.ai/install.sh | bash
# or: npm i -g @vapi-ai/cli
export PATH="$HOME/.vapi/bin:$HOME/.local/bin:$PATH"
# seed config once from 1Password private key:
# api_key: <op item get vapi --fields credential --reveal>  in ~/.vapi-cli.yaml chmod 600
vapi auth status
vapi version   # known good: 0.2.1 (goreleaser darwin/arm64)
```

## CLI commands that work vs don't

| Command | Status (0.2.1) |
|---|---|
| `vapi auth status` / `whoami` | OK |
| `vapi assistant list` / `get` | OK |
| `vapi call get <id>` | OK |
| `vapi call list` | **BROKEN** — `cannot unmarshal string into Go struct field .embed.assistant` |
| `vapi logs list` | OK (when auth valid) |

Workaround for list: `scripts/vapi_analytics.sh calls 20` or raw `GET /call?limit=20`.

## Analytics API

`POST https://api.vapi.ai/analytics`
Header: `Authorization: Bearer <REDACTED> + `Content-Type: application/json`

```json
{
  "queries": [
    {
      "table": "call",
      "name": "call_ends",
      "groupBy": ["endedReason"],
      "timeRange": {
        "start": "ISO-UTC",
        "end": "ISO-UTC",
        "timezone": "America/Los_Angeles",
        "step": "day"
      },
      "operations": [
        {"operation": "count", "column": "id", "alias": "calls"},
        {"operation": "sum", "column": "cost", "alias": "sumCost"},
        {"operation": "sum", "column": "duration", "alias": "sumDuration"},
        {"operation": "avg", "column": "cost", "alias": "avgCost"}
      ]
    }
  ]
}
```

### Constraints proved live

- Top-level **must** be object with `queries` array. Bare `[...]` → 400 `queries must be an array` / `property 0 should not exist`.
- **`groupBy` is always an array of enums.** String form → 400 `groupBy must be an array`.
- Enums: `type`, `assistantId`, `endedReason`, `analysis.successEvaluation`, `status`.
- `table`: `call` | `subscription`.
- Ops: `sum|avg|count|min|max|history`.
- Columns include: `id`, `cost`, `duration`, `costBreakdown.llm|stt|tts|vapi|transport|...`.
- Omitted `timeRange` → last **7 days UTC**.
- Useful `endedReason` example from real traffic: `assistant-forwarded-call`.

### Helper presets

```bash
SCRIPTS=~/.hermes/skills/communication/communications/scripts
$SCRIPTS/vapi_analytics.sh summary --days 14   # status, ends, cost, success, daily
$SCRIPTS/vapi_analytics.sh ends --days 14
$SCRIPTS/vapi_analytics.sh cost --days 14 --step day
$SCRIPTS/vapi_analytics.sh success
$SCRIPTS/vapi_analytics.sh status
$SCRIPTS/vapi_analytics.sh calls 20
$SCRIPTS/vapi_analytics.sh get <call_id>
$SCRIPTS/vapi_analytics.sh query '[{"table":"call","name":"x","operations":[{"operation":"count","column":"id"}]}]'
$SCRIPTS/vapi_analytics.sh cli assistant list
```

## curl | heredoc stdin footgun

```bash
# BAD — heredoc becomes python stdin; pipe from curl is dropped
curl ... | python3 <<'PY'
import sys,json; json.load(sys.stdin)
PY

# GOOD
tmp=$(mktemp)
curl -sS ... -o "$tmp"
python3 - "$tmp" <<'PY'
import sys,json; print(json.load(open(sys.argv[1])))
PY
rm -f "$tmp"
```

`vapi_analytics.sh` `calls` / `get` already use the temp-file pattern.

## Links

- https://docs.vapi.ai/cli
- https://docs.vapi.ai/api-reference/analytics/get
- https://dashboard.vapi.ai/
