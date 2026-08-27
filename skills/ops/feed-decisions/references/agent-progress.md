# Agent progress on feed decisions

Cooper needs visible proof work is happening — not a silent queue.

## Lifecycle (D1 `feed_responses`)

| Status | pct (typical) | Who sets |
|---|---|---|
| `pending` | 0 | UI Send to Hermes |
| `claimed` | ≥10 | agent `--claim` |
| `running` | mid | agent `--progress` |
| `done` | 100 | agent `--done` + `result_summary` |
| `failed` | 100 | agent `--fail` + `error` |
| `cancelled` | 100 | agent/UI cancel |

## Required agent hygiene

While executing a claimed decision:

1. Claim immediately when picking up work.
2. Progress at least once mid-run with a human-readable message (what portal/email/step).
3. Finish with `--done --summary "…"` including verifiable evidence (receipt id, archive confirm, card comment).
4. On blocker: `--fail --error "…"` — do not leave claimed forever.

## CLI

```bash
bun ~/git/darkmatter/feed/scripts/poll-responses.ts --status open --claim
bun ~/git/darkmatter/feed/scripts/poll-responses.ts --progress 12 --message "Opened official billing (readonly)" --pct 40
bun ~/git/darkmatter/feed/scripts/poll-responses.ts --done 12 --summary "Paid; receipt ch_…"
```

Auth: Bearer <REDACTED> + CF Access service token headers.

## UI

- Inline tracker under the card after Send
- **Agent activity** section polls `/api/responses?status=all&order=desc`
- Open work = `pending|claimed|running`
