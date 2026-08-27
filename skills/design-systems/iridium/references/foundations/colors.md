# Colors & Tokens

Source: `packages/ui/src/native-tokens.css` (the `--n-*` ramp) and `packages/ui/src/theme.css` (the semantic bridge + Tailwind palette overrides). These are the single source of truth. Never hard-code hex/OKLCH values.

## The native ramp (`--n-*`)

Cool neutrals (hue 265, low chroma) so surfaces read as deep blue-black, not grey. Defined in `:root` and registered as Tailwind utilities via `@theme inline` (so `bg-n-bg-2`, `text-n-mute`, `border-n-hl` all work).

### Surfaces (dark → light)
- `--n-chrome` `oklch(0.03 0.008 265)` — outer chrome, a shade under the body
- `--n-bg` `oklch(0.055 0.01 265)` — main body background
- `--n-bg-1` `oklch(0.105 0.011 265)` — one step lifted
- `--n-bg-2` `oklch(0.14 0.012 265)` — **card**
- `--n-bg-3` `oklch(0.195 0.014 265)` — hover / pressed surface
- `--n-bg-4` `oklch(0.248 0.016 265)` — input background

### Hairlines / borders
- `--n-hl` `oklch(0.75 0.04 265 / 8%)` — default hairline
- `--n-hl-2` `oklch(0.78 0.05 265 / 14%)` — stronger hairline / ring

### Text
- `--n-fg` `oklch(0.985 0.002 265)` — primary
- `--n-fg-2` `oklch(0.885 0.006 265)` — secondary
- `--n-fg-3` `oklch(0.745 0.01 265)` — tertiary
- `--n-mute` `oklch(0.61 0.014 265)` — muted
- `--n-mute-2` `oklch(0.485 0.016 265)` — most muted

### Status / data hues
- Positive (green / accent): `--n-green` `oklch(0.76 0.15 165)`, `--n-green-2`, `--n-green-bg`
- Informational (blue): `--n-blue` `oklch(0.68 0.15 258)`, `--n-blue-2`, `--n-blue-bg`
- Warning (amber): `--n-amber` `oklch(0.82 0.13 85)`
- Negative (red): `--n-red` `oklch(0.7 0.19 18)`
- Violet: `--n-violet` `oklch(0.73 0.15 298)`
- Accent equals green: `--n-accent` = `--n-green`; `--n-on-accent` `oklch(0.055 0.01 265)` (near-black text on accent)

### Translucent lift overlays
`--n-lift` (white), `--n-lift-2/4/5/8` (white at 2/4/5/8% alpha) — for subtle raised surfaces and glows.

## Semantic bridge (use these in app code)

`theme.css` maps standard shadcn semantic tokens onto the ramp, so semantic utilities work and stay on-palette:

- `bg-background` / `text-foreground` — body
- `bg-card` / `text-card-foreground` → `--n-bg-2` / `--n-fg`
- `bg-popover` / `text-popover-foreground` → `--n-bg-2`
- `bg-primary` / `text-primary-foreground` → `--n-accent` (green) / near-black
- `bg-secondary`, `bg-muted`, `bg-accent` → `--n-bg-3`; `text-muted-foreground` → `--n-mute`
- `bg-destructive` → `--n-red`
- `bg-input` → `--n-bg-4`, `ring` → `--n-hl-2`, `border` → `--n-hl`
- Chart series: `--color-chart-1..5` → green, blue, violet, amber, red

## Tailwind palette overrides

`theme.css` re-points ~600 stock-Tailwind call sites onto the ramp: `zinc-*`, `neutral-*`, `gray-*` → surfaces/text; `green-*`/`emerald-*` → green; `red-*` → red; `amber-*`/`yellow-*` → amber; `blue-*`/`sky-*` → blue; `purple-*` → violet. Only shades actually used upstream are mapped. **Prefer the `n-*` utilities or semantic tokens in new code** — the palette overrides exist for legacy migration, not as an invitation to use arbitrary stock shades (unmapped shades will render off-palette).

## Rules
- Never write raw hex or `oklch(...)` in components. Use `n-*` utilities, semantic utilities, or `var(--n-*)`.
- There is no light theme. All values live in `:root` and the app runs with `.dark` on `<html>`.
- For status coloring (P&L, health, alerts) use the status hues, not arbitrary colors.
