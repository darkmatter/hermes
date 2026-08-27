# Hindsight Cloud (OMP memory bank)

Direct API — not the Hermes `hindsight` memory plugin (`localhost:8888` / bank `hermes`) and not Honcho.

## Endpoint

- Base: `https://api.hindsight.vectorize.io`
- Auth: `Authorization: Bearer <REDACTED> read hindsight-api-key>` (prefix `hsk_`)
- Token lives only in himitsu path `hindsight-api-key` (store `czxtm/secrets`)

Do not print the token. Keep it in-process. Bind `HOME=~ + `HIMITSU_AUTO_PULL=false` before `himitsu read`.

## Banks on this key

| bank_id | Role |
|---|---|
| `omp` | Personal / desktop OMP memory. This is "the omp memory bank." |
| `centaur` | Centaur harness OMP (`bankId: centaur` in `darkmatter/centaur/harness/omp/config.yml`) — kept separate from personal. |
| `hermes` | Hermes Agent bank (plugin default). Distinct from this session's Honcho provider. |
| `voy-centaur` | Voy-Centaur; may be empty. |

"OMP memory bank" means **`omp`**, not `centaur`. Centaur deploy/verify is a different workflow (OMP-owned skill `centaur-hindsight-memory-deploy`).

## Working routes

| Method | Path | Notes |
|---|---|---|
| GET | `/health` | 200 `{"status":"healthy",...}` |
| GET | `/v1/default/banks` | list; includes `fact_count`, `last_write_at` |
| GET | `/v1/default/banks/{id}/stats` | nodes by type, document count |
| GET | `/v1/default/banks/{id}/tags` | `project:*` tags + counts |
| GET | `/v1/default/banks/{id}/memories/list` | `q` substring, `type`, `limit`, `offset`, `tags`. Returns `{items,total}` |
| POST | `/v1/default/banks/{id}/memories/recall` | semantic. Body `query` required; `types` (`world`/`experience`/`observation`), `budget` (`low`/`mid`/`high`), `max_tokens` |
| GET | `/v1/default/banks/{id}/mental-models` | `detail=metadata\|content\|full` |
| GET | `/v1/default/banks/{id}/mental-models/{mid}` | standing distilled instructions |
| GET | `/v1/default/banks/{id}/documents` | **metadata only**; `q` is document-**id** substring, not content |
| GET | `/v1/default/banks/{id}/directives` | `omp` has none |
| POST | `/v1/default/banks/{id}/memories` | retain; body `{"items":[{"content":"..."}]}` |
| GET | `/openapi.json` | schema |

`GET /v1/default/banks/{id}` and `GET .../memories` (no `/list`) return **405**.

Garbage bearer <REDACTED> **401** `Invalid API key format`.

## Mine a bank (read-only)

Use this when the user wants source material, not a connectivity probe.

1. `stats` + `tags` + `mental-models?detail=metadata` — map the bank.
2. Pull high-signal models as markdown: `user-preferences`, `project-conventions-*`, `project-decisions-*`. These are distilled standing asks; they outrank one-off recall hits.
3. Keyword via `memories/list?q=` (paginate `offset`). Useful stems: `cleanup`, `refactor`, `simplify`, `unused`, `prune`, `leftover`, `surgical`, `hygiene`, `AGENTS.md`. Totals are substring-noisy (`stale`, `legacy`, `dedupe` hit infra/idempotency).
4. Semantic via `recall` with `types=["world","experience","observation"]` and `budget=high`. Phrase queries as "The user asked the agent to …" to bias toward prompts, not agent self-reports.
5. Filter: "user requested X" is often a **feature**. Keep only asks that are not "ship a feature / fix a bug" unless the user wanted everything.
6. Dump to `/tmp/omp-mine/` (json + extracted `.md`). Do **not** `retain` back into the bank.

On `omp` (as of 2026-08-17): ~1025 documents, ~23k facts; 69 mental models; `user-preferences` ~45k chars. A packed dump lived at `~/workspace/omp-hindsight-mine-source.zip`.

Compiled non-feature asks from that mine: skill `keep-codebase-maintainable` (`references/instances.md`). That skill is user-owned — do not silently rewrite it.

## No-leak probe

```python
import json, subprocess, urllib.request, urllib.error

token = <REDACTED>
    ["himitsu", "read", "hindsight-api-key"], text=True
).strip()
# requires HOME=~ HIMITSU_AUTO_PULL=false on the process

def req(method, path, body=None):
    data = None if body is None else json.dumps(body).encode()
    r = urllib.request.Request(
        "https://api.hindsight.vectorize.io" + path,
        data=data,
        headers={
            "Authorization": f"Bearer <REDACTED>",
            "Accept": "application/json",
            **({"Content-Type": "application/json"} if body else {}),
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:300]

print("health", req("GET", "/health")[0])
st, banks = req("GET", "/v1/default/banks")
print("banks", st, [b["bank_id"] for b in banks.get("banks", [])])
st, rec = req("POST", "/v1/default/banks/omp/memories/recall",
              {"query": "what is this memory bank for?", "limit": 3})
print("omp recall", st, "n", len(rec.get("results", [])))
```

Report: HTTP codes, bank ids, fact counts, recall hit count / types. Not the token. Not full memory text unless the user asked to read memories.

## Do not (unless asked)

- Switch Hermes `memory.provider` to hindsight (user said keep Honcho)
- `retain` into any bank
- Treat plugin `~/.hermes/hindsight/config.json` (`localhost:8888`, `bank_id: hermes`) as the OMP bank
- Use the Centaur iron-proxy placeholder `HINDSIGHT_API_TOKEN` from this hub — that swap only happens inside claimed sandboxes
