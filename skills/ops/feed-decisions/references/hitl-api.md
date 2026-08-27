# HITL + responses API (feed.cm.xyz)

Auth for agents: `Authorization: Bearer <REDACTED> read feed/ingest-token)` plus
`CF-Access-Client-Id/Secret` from himitsu.

## HITL (agent → Cooper)

| Method | Path | Who |
|---|---|---|
| POST | `/api/hitl` | Agent creates |
| GET | `/api/hitl?status=open\|answered\|all` | Both |
| GET | `/api/hitl/:id` | Both |
| POST | `/api/hitl/:id/answer` | Cooper (Access) |
| POST | `/api/hitl/:id/cancel` | Both |

Create body:

```json
{
  "title": "Pay Kernel $30?",
  "body": "Findings…",
  "options": [
    {"id": "pay", "label": "✅ Pay", "recommended": true},
    {"id": "skip", "label": "❌ Don't pay"}
  ],
  "category": "pay",
  "priority": 80,
  "source": "hermes",
  "link": null,
  "external_ref": null,
  "allow_freeform": true
}
```

CLI: `bun ~/git/darkmatter/feed/scripts/hitl.ts ask|list|get|wait|cancel`

## Work progress (feed_responses)

| Method | Path |
|---|---|
| POST | `/api/responses` (UI Send to Hermes) |
| GET | `/api/responses?status=open\|pending\|…&order=desc` |
| GET | `/api/responses/:id` |
| POST | `/api/responses/:id/claim` |
| POST | `/api/responses/:id/progress` `{message, progress_pct}` |
| POST | `/api/responses/:id/done` `{result_summary}` |
| POST | `/api/responses/:id/fail` `{error}` |

CLI: `bun scripts/poll-responses.ts`

Meta: `GET /api/meta` → `open_hitl`, `pending_responses`, `inflight_responses`, `failed_responses`.
