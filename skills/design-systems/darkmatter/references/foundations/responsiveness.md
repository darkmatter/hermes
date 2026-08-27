# Responsiveness

darkmatter builds mobile-first with Tailwind v4 utility variants, plus a `useIsMobile()` hook for the handful of JS-driven cases. Source: `hooks/use-mobile.tsx`, `components/ui/sidebar.tsx`.

## Breakpoints

Tailwind v4 defaults (no custom breakpoints are defined in the theme):

| Prefix | Min-width |
| --- | --- |
| `sm` | 40rem (640px) |
| `md` | 48rem (768px) |
| `lg` | 64rem (1024px) |
| `xl` | 80rem (1280px) |
| `2xl` | 96rem (1536px) |

Build mobile-first: base classes target small screens, then layer `sm:` / `md:` / `lg:` overrides.

```tsx
<div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
  {/* cards */}
</div>

<h1 className="text-4xl md:text-6xl lg:text-7xl">…</h1>
```

## `useIsMobile()` hook

For behavior that can't be expressed with CSS variants (conditional rendering, swapping a dialog for a drawer, sidebar collapse), use the hook. It reads a `768px` threshold via `matchMedia`.

```tsx
import { useIsMobile } from "@/hooks/use-mobile"

function Nav() {
  const isMobile = useIsMobile() // true when viewport < 768px
  return isMobile ? <MobileMenu /> : <DesktopMenu />
}
```

The `MOBILE_BREAKPOINT` constant is `768`. The `sidebar` component uses this hook to switch its desktop rail for a `Sheet`-based drawer on mobile.

## Rules

- Prefer CSS responsive variants; reserve `useIsMobile()` for JS-only branches.
- Never hard-code fixed widths or ad-hoc `@media` queries — use the breakpoints above.
- Use the container pattern (`mx-auto max-w-6xl px-4 sm:px-6 lg:px-8`) for page width.
- Verify layouts at both mobile (≈390px) and desktop (≈1440px).
