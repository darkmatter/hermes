# Session learnings — payments via feed progress (2026-08)

## Intake

Cooper decides on https://feed.cm.xyz → D1. Poll with progress updates so the UI bar moves.

```bash
bun ~/git/darkmatter/feed/scripts/poll-responses.ts --status open --claim
bun ~/git/darkmatter/feed/scripts/poll-responses.ts --progress ID --message "Opened official billing" --pct 40
# Studio CUA + SA op only; charge gate
bun ~/git/darkmatter/feed/scripts/poll-responses.ts --done ID --summary "Paid; receipt …"
```

## Agent-first

Investigate official portals yourself. Never “what did the console show?”

## 1P

`~/.local/bin/op` + himitsu SA token + `--vault cm|cooper|dev`. Catalog `~/.hermes/op-sa-catalog.json`. Missing item → as-needed move that title into **cm**. Never biometric/agenix personal token.

## Related

`feed-decisions`, `agent-first-billing.md`, `feed-d1-intake.md` (may be slightly stale on progress CLI — prefer this file + feed-decisions agent-progress.md).
