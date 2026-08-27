# Component Catalog

51 component modules ship from `@native/ui`, plus `@native/ui/lib/utils` (`cn`) and `@native/ui/hooks/use-mobile` (`useIsMobile`). Import each from its own module path, e.g. `import { Button } from "@native/ui/button"`.

Source of truth: `packages/ui/src/*.tsx` in `darkmatter/iridium` (vendored at `vendor/native-ui/` in the starter).

## Grouped by task area (see the linked file for props, examples, mistakes)

### Buttons & actions → `buttons.md`
`button`, `terminal-button`, `toggle`, `toggle-group`, `copy-button`

### Forms & inputs → `forms.md`
`input`, `label`, `field`, `form`, `select`, `checkbox`, `radio-group`, `input-otp`, `pill-toggle`

### Feedback & status → `feedback.md`
`badge`, `health-badge`, `freshness-indicator`, `pill`, `alert`, `sonner` (Toaster), `tooltip`, `skeleton`

### Data display → `data-display.md`
`card`, `glow-card`, `table`, `avatar`, `item`, `separator`, `chart`, `tick-range-chart`, `terminal`, `typing-animation`

### Navigation → `navigation.md`
`navigation-menu`, `sidebar`, `tabs`, `pagination`, `command`, `breadcrumb`-style via `navigation-menu`

### Overlays → `overlays.md`
`dialog`, `modern-modal`, `sheet`, `drawer`, `popover`, `dropdown-menu`, `tooltip`, `accordion`, `collapsible`, `scroll-area`

### Layout primitives → see `../foundations/spacing-layout.md`
`page-layout` (`PageLayout`, `Row`), `grid` (`Grid`)

### Signature / decorative effects → see `../foundations/motion.md`
`glow-card`, `glowing-effect`, `spotlight-new`, `typing-animation`, `terminal`

## Notes
- Most components are `"use client"`. Use them inside client components in the App Router.
- `chart` wraps Recharts (shadcn-style `ChartContainer`); `carousel` wraps Embla; `command` wraps `cmdk`; `drawer` wraps Vaul; `sonner` wraps Sonner. Overlays/menus are Radix-based.
- `health-badge` and some data types import from `@native/shared/position-health` (aliased in the starter). These are domain-specific to darkmatter's LP/position tooling — use them when modeling position health, otherwise prefer the generic `Badge`/`Pill`.
