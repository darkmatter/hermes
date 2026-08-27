# D1 feed_responses API

Worker: `cooper-feed` @ https://feed.cm.xyz
Migrations: `0002_feed_responses.sql`, `0003_response_progress.sql`

## Table (summary)

id, created_at, subject, task_id, choice_*, note, prompt, source,
status (`pending|claimed|running|done|failed|cancelled`), claimed_*, done_at, actor_email,
**progress_message, progress_pct, progress_updated_at, error, result_summary**

## Endpoints

| Method | Path | Auth | Role |
|---|---|---|---|
| POST | `/api/responses` | Access session (or Bearer) | UI/agent write — starts Queued 0% |
| GET | `/api/responses?status=open\|all&order=desc` | Bearer <REDACTED> CF Access ST | poll |
| GET | `/api/responses/:id` | Access/Bearer <REDACTED> single row for UI tracker |
| POST | `/api/responses/:id/claim` | Bearer <REDACTED> claimed ≥10% |
| POST | `/api/responses/:id/progress` | Bearer <REDACTED> `{message, progress_pct}` → running |
| POST | `/api/responses/:id/done` | Bearer <REDACTED> `{result_summary}` → 100% |
| POST | `/api/responses/:id/fail` | Bearer <REDACTED> `{error}` |
| POST | `/api/responses/:id/cancel` | Bearer <REDACTED> cancel |
| GET | `/api/meta` | Access/Bearer <REDACTED> `pending_responses`, `inflight_responses`, `failed_responses` |

### POST create body

```json
{
  "subject": "t_… or title",
  "task_id": "t_…",
  "choice_id": "opt-0",
  "choice_label": "✅ Pay",
  "note": "optional",
  "prompt": "full agent instruction",
  "source": "blocked_choice|feed_item|blocked_freeform|agent_smoke"
}
```

## Poll helper (required hygiene)

```bash
bun ~/git/darkmatter/feed/scripts/poll-responses.ts --status open --claim
bun ~/git/darkmatter/feed/scripts/poll-responses.ts --progress 12 --message "Opened billing portal" --pct 40
bun ~/git/darkmatter/feed/scripts/poll-responses.ts --done 12 --summary "Paid; receipt …"
```

Never leave a decision **claimed** without progress/done/fail — UI shows stuck work.

Secrets (himitsu, never print): `feed/ingest-token`, `cf-access-client-id`, `cf-access-client-secret`.

## Deploy

Alchemy `migrationsDir`. After schema: build +
`STAGE=prod bun alchemy deploy ./alchemy.run.ts --stage prod --profile default --yes`
with CF account/token + FEED_INGEST_TOKEN from himitsu.
