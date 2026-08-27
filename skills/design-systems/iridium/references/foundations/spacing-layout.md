# Spacing, Radii & Layout

## Radii
Source: `packages/ui/src/theme.css` (`--radius-*`) and `native-tokens.css` (`--n-radius`).
- `--n-radius` `6px` → `rounded-n` / `--radius-sm`
- `--n-radius-card` `8px` → `rounded-n-card` / `--radius-md`
- `--radius-lg` `10px`, `--radius-xl` `14px`, `--radius-2xl` `18px`, `--radius-3xl` `22px`, `--radius-4xl` `26px`
- `--radius-full` `9999px` (pills, avatars, status dots)

Use `rounded-md`/`rounded-lg` for cards and controls, `rounded-full` for pills/dots. The old terminal aesthetic pinned radius to 0; the current system does **not** — don't square everything off.

## Spacing
Use Tailwind's default spacing scale. Console UIs are dense: prefer tight gaps (`gap-2`, `gap-3`, `gap-4`), compact padding (`p-3`/`p-4` for cards, `px-3 py-1.5` for controls), and section spacing around `space-y-6`/`space-y-8`.

## Layout primitives
Source: `packages/ui/src/page-layout.tsx`, `packages/ui/src/grid.tsx`.

### PageLayout
`import { PageLayout, Row } from "@native/ui/page-layout"`.
- `PageLayout` wraps a screen in a centered `max-w-[1440px]` container with responsive padding (`px-4 py-5 sm:px-6 sm:py-6 lg:px-8 lg:py-8`). Use it as the outer wrapper for every page instead of ad-hoc `max-w-* mx-auto px-*`.
- `Row` is a horizontal flex row (`flex flex-row items-center`) that also spreads `HTMLAttributes` — use for toolbars, header rows, inline control groups.

### Grid
`import { Grid } from "@native/ui/grid"`. Props: `cols` (1–5, default 1) and `gap` (number of px, default 8).
- Renders a CSS grid with **fixed** equal columns (`repeat(cols, 1fr)`) via inline style — it does **not** change column count across breakpoints on its own.
- For responsive column counts, either switch `cols` with the `useIsMobile()` hook (`@native/ui/hooks/use-mobile`, 768px breakpoint), or use Tailwind responsive grid utilities (`grid grid-cols-1 md:grid-cols-3 gap-4`) directly. See `references/foundations/responsiveness.md`.

## Rules
- Never hard-code fixed pixel page widths. Use `PageLayout`/`Grid` and responsive utilities.
- Keep density high — this is a data/console system, not a spacious marketing layout.
- Radii come from the scale above; don't invent values.
