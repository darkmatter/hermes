# Feed UI contracts

## HITL panel (primary)

- Component: `src/components/hitl-panel.tsx`
- Sidebar label: **Your decisions** / section `section-hitl`
- Options: shadcn **Tabs** — one active panel (full label + optional note + Submit answer)
- Do **not** rebuild kanban here; snapshot board is legacy context only

## Agent activity

- Component: `src/components/agent-activity.tsx`
- Polls `/api/responses?status=all&order=desc` every few seconds
- Shows Queued → Claimed → Running → Done/Failed with % bar + message

## Click / input pitfalls

- Never `onClick={(e) => e.preventDefault()}` on the choice container — blocks activation
- Use `stopPropagation` only
- Hard-refresh after deploy (`Cmd+Shift+R`)

## Retired

- Clipboard “Copy for Hermes” / “Copy response” as completion path
- Stacked per-option radio + input rows
