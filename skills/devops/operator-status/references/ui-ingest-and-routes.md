# feed.cm.xyz — session notes (UI + ingest + Access)

## Live routes

| Method | Path | Auth | Role |
|---|---|---|---|
| `GET` | `/` | Access (browser / WARP identity) | Waku UI SPA |
| `GET` | `/api/healthz` | Worker-public; often Access-gated at edge | health |
| `GET` | `/api/meta` | Access / service token | snapshot age + recent ingests |
| `GET` | `/api/feed` | Access / service token | full feed JSON from D1 |
| `POST` | `/api/ingest` | Bearer <REDACTED> + Access service token | upsert D1 snapshot |

No path routes for sections — only in-page IDs (`#section-blocked`, `#section-messages`, …).

## Cron → D1

```
collectors → ~/.hermes/feed/cron-json/*.json
Daily Feed Builder 9acdbe616b8f (30 9 * * * PT)
  → recommendations.json
  → python3 ~/.hermes/scripts/build-feed.py
       writes ~/feed/src/feed-data.json
       bun run build (local ~/feed only)
       push_remote_snapshot() → bun scripts/push-feed.ts → POST /api/ingest
```

Collectors alone never refresh prod. `build-feed.py` must call push **before** `sys.exit` and may resolve token via `himitsu read feed/ingest-token` when env lacks `FEED_INGEST_TOKEN` (dead post-exit push left D1 on 2026-07-30 for days).

Header badge is **data** `generated_at` (D1), not UI deploy time.

## UI contracts (dashboard.tsx)

- `SidebarInset` peer of `Sidebar` so rail **pushes** content (not overlay). Prefer `collapsible="icon"`.
- Action items: single column; `action_needed` → `ResponseComposer` (MC + recommended + freeform note → clipboard).
- Optional item field `response_options: [{id?, label, recommended?, prompt?}]`. Defaults: do hint / draft / snooze / skip.
- Blocked kanban: recommendation `actions` (copy/secret/choice) + note; choice reuses `ResponseComposer`.

## Access WARP

App flag `allow_authenticate_via_warp: true` on feed (and many internals). Org already had `allow_authenticate_via_warp`. Agents still use service tokens + `non_identity`. Dual-tunnel DNS: skill `warp-tailscale-coexistence`.
