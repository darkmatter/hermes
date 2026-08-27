# Component inventory

55 components live in `components/ui/*`, imported via `@/components/ui/<name>`. They are shadcn/ui-style (Radix UI + Tailwind v4 + `cva`), plus darkmatter's signature effect primitives. Source of truth: `components/ui/` in the starter (mirrored from `darkmatter/web`).

Import by path — there is **no** darkmatter npm package:

```tsx
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardContent } from "@/components/ui/card"
```

## Standard shadcn components

`accordion`, `alert`, `alert-dialog`, `aspect-ratio`, `avatar`, `badge`, `breadcrumb`, `button`, `card`, `carousel`, `checkbox`, `collapsible`, `command`, `context-menu`, `dialog`, `drawer`, `dropdown-menu`, `form`, `hover-card`, `input`, `input-otp`, `label`, `menubar`, `navigation-menu`, `pagination`, `popover`, `progress`, `radio-group`, `scroll-area`, `select`, `separator`, `sheet`, `sidebar`, `skeleton`, `slider`, `sonner`, `switch`, `table`, `tabs`, `textarea`, `toast`, `toggle`, `toggle-group`, `tooltip`.

## Signature darkmatter effects

`background-beams`, `background-lines`, `card-spotlight`, `dotted-glow-background`, `evervault-card`, `floating-dock`, `glowing-effect`, `hover-border-gradient`, `text-hover-effect`, `wobble-card`. See `effects.md`.

## Icons & misc

`github-icon` (inline GitHub SVG). Icon libraries available: `lucide-react` and `@tabler/icons-react`.

## Hooks

- `@/hooks/use-mobile` → `useIsMobile()` (768px threshold).
- `@/hooks/use-toast` → `useToast()` / `toast()` (paired with `toast`/`toaster` components; `sonner` is also available).

## Grouped docs

- `buttons.md` — button, toggle, toggle-group.
- `forms.md` — form, input, textarea, select, checkbox, radio-group, switch, slider, label, input-otp.
- `feedback.md` — alert, sonner/toast, progress, skeleton, tooltip.
- `data-display.md` — card, badge, avatar, table, tabs, accordion, separator.
- `navigation.md` — navigation-menu, sidebar, breadcrumb, dropdown-menu, menubar, pagination, floating-dock.
- `overlays.md` — dialog, alert-dialog, sheet, drawer, popover, hover-card, command.
- `effects.md` — all signature effect primitives.
