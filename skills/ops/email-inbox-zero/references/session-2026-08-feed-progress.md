# Session learnings — feed progress + agent-first (2026-08)

## Product

- Pay/Don't-pay on feed only; chat ≤5 non-checkbox items
- **Send to Hermes** → D1 (never clipboard Copy for Hermes)
- Agent-first: never ask Cooper what a console showed
- UI: Tabs single-select; Agent activity progress bar Queued→Done

## Agent CLI

```bash
bun ~/git/darkmatter/feed/scripts/poll-responses.ts --status open --claim
bun ~/git/darkmatter/feed/scripts/poll-responses.ts --progress ID --message "…" --pct N
bun ~/git/darkmatter/feed/scripts/poll-responses.ts --done ID --summary "…"
```

## Cross-skills

- Staging/UI/API: `feed-decisions` (`references/agent-progress.md`, `d1-api.md`, `tabs-ui.md`)
- Payment execute: `financial-operations` (charge gate, SA op vault cm)
- Do not leave decisions stuck in `claimed` without progress

## SKILL.md note

email-inbox-zero SKILL.md still mentions “Copy for Hermes” in one place — treat as stale; use this file + `feed-decisions` until SKILL.md can be patched.
