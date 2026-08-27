# Feed choice UI: Tabs (one panel)

Cooper rejected stacked multi-input choice rows (radio + label + note repeated).

## Required pattern (prod)

`~/git/darkmatter/feed/src/components/dashboard.tsx` → `ResponseComposer`:

1. **shadcn Tabs** — short tab labels (`optionTabLabel`)
2. **One TabsContent** active: full option label + optional note + **Send to Hermes**
3. Container: `stopPropagation` only — **never** `preventDefault`
4. Submit → `POST /api/responses` → D1 (not clipboard)

Components: `src/components/ui/tabs.tsx`, `radio-group.tsx`.

## Default option tabs (agent-first)

| Tab | id |
|---|---|
| Investigate ★ | investigate_propose |
| Do safe work | execute_safe |
| Snooze | snooze |
| Skip | skip |

See `agent-first-options.md`.
