# ResponseComposer click pitfall

Cooper reported action options not clickable.

## Cause

Container used `onClick={(e) => e.preventDefault()}`, which cancels label/radio default activation.

## Fix (prod)

- Container: `onClick={(e) => e.stopPropagation()}` only
- Label: `onClick` → `setSelected(value)`
- Radios can be controlled `readOnly` with `pointer-events-none`

Files: `~/git/darkmatter/feed/src/components/dashboard.tsx`
After deploy: hard-refresh feed.cm.xyz (`Cmd+Shift+R`).
