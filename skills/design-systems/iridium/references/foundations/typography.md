# Typography & Fonts

Source: `packages/ui/src/theme.css` (`@theme` font family vars). Font *faces* are loaded per app; the theme only references family names. The starter loads five faces — **Inter, Lora, IBM Plex Mono, Geist Mono, Source Code Pro** — via **`next/font/google`** in `app/layout.tsx`, exposes them as `--font-*` CSS variables on `<html>`, and re-points the theme's named font tokens at those variables in `app/globals.css`.

**Load fonts with `next/font`, never a remote `@import`.** A `@import url("https://fonts.googleapis.com/...")` in a CSS file is render-blocking and will not resolve inside sandboxed preview iframes, leaving the page blank even though the HTML is valid. `next/font` self-hosts the faces, so keep fonts wired the way `layout.tsx`/`globals.css` already do it and add new faces there — don't add a remote font `@import`.

**Global text rendering.** `app/globals.css` sets antialiased smoothing and kerning on `html` for the whole app: `-webkit-font-smoothing: antialiased`, `-moz-osx-font-smoothing: grayscale`, `text-rendering: optimizeLegibility`, `font-kerning: normal`, and `font-feature-settings: "kern" 1`. Keep these — don't disable smoothing/kerning per-component.

## Font families (Tailwind `font-*` utilities)
- `--font-sans` → `font-sans`: **Inter**, ui-sans-serif, system-ui. Default body/UI text.
- `--font-display` → `font-display`: **Inter**, ui-sans-serif, system-ui. Uppercase brand labels, section labels, nav labels.
- `--font-num` → `font-num`: **Source Code Pro** (variable), ui-monospace. Applied to every `.tabular-nums` element — numeric/financial data.
- `--font-mono` → `font-mono`: **IBM Plex Mono**, ui-monospace. Code, IDs, hashes.
- `--font-terminal` / `--font-tech` → `font-terminal` / `font-tech`: **Geist Mono**, ui-monospace. Terminal accents and technical/command-line UI.
- `--font-serif` → `font-serif`: **Lora**. Rarely used.

## Usage patterns
- **Body & UI**: default (`font-sans`). Don't set a family unless deviating.
- **Section labels / nav / wordmark**: `font-display`, usually `uppercase` with `tracking-wide` or `tracking-wider`, often at small sizes (`text-xs`/`text-sm`) in `text-n-mute` or `text-n-fg-3`.
- **Numbers**: always add `tabular-nums` (prices, quantities, P&L, table numeric columns). This switches to `--font-num` and keeps digit columns aligned. This is a signature of the system — never render financial data in a proportional face.
- **Terminal flourishes**: `font-terminal` for command-line style accents, prompts, and the `Terminal` component.

## Scale
Use Tailwind's default type scale (`text-xs` … `text-4xl`). Dense console UIs favor `text-xs`/`text-sm` for data and labels, `text-lg`/`text-xl` for section headings, larger only for hero/marketing. Pair small uppercase `font-display` labels with `text-n-mute` for the terminal feel.

## Rules
- Numeric data → `tabular-nums` (mandatory).
- Labels/headers that should feel like the brand → `font-display uppercase tracking-wide`.
- Don't introduce font families outside the `--font-*` set.
