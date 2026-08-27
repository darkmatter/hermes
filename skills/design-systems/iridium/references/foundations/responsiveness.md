# Responsiveness & Breakpoints

Iridium is built on Tailwind CSS v4, so responsiveness uses Tailwind's standard breakpoint prefixes plus one JS hook. Always design mobile-first (base styles = smallest screen) and layer breakpoint prefixes up.

## Breakpoints
Standard Tailwind v4 breakpoints: `sm` 640px, `md` 768px, `lg` 1024px, `xl` 1280px, `2xl` 1536px. The system's canonical primitives use these:
- `PageLayout` scales padding at `sm` and `lg` and caps content at `max-w-[1440px]`.
- The JS breakpoint is **768px** (`useIsMobile()` in `@native/ui/hooks/use-mobile`), matching `md`.

## How to build responsively
1. **Wrap pages in `PageLayout`** so max-width and gutters are handled.
2. **Multi-column areas**: prefer Tailwind responsive grid utilities for anything that should reflow —
   ```tsx
   <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">…</div>
   ```
   The `Grid` primitive (`@native/ui/grid`) renders a *fixed* column count, so use it for layouts that keep the same columns, or drive its `cols` prop from `useIsMobile()`.
3. **Show/hide or restructure by device** with `useIsMobile()`:
   ```tsx
   "use client";
   import { useIsMobile } from "@native/ui/hooks/use-mobile";
   const isMobile = useIsMobile();
   return isMobile ? <StackedView /> : <TableView />;
   ```
   Use this for genuinely different layouts (e.g. a data table on desktop vs. stacked cards on mobile). `useIsMobile()` returns `false` on the server/first paint until mounted, so it's for client components only.
4. **Sidebar/sheet navigation**: the `Sidebar` component (`@native/ui/sidebar`) and `Sheet` (`@native/ui/sheet`) handle the collapse-to-drawer pattern — use them rather than rebuilding responsive nav.
5. **Dense tables**: wrap wide tables in `ScrollArea` (`@native/ui/scroll-area`) or an `overflow-x-auto` container so they scroll horizontally on narrow screens rather than breaking layout.

## Rules
- Mobile-first: base classes target small screens, add `md:`/`lg:` to expand.
- Never hard-code fixed pixel widths for page structure; let `PageLayout` + responsive utilities handle it.
- Don't use `useIsMobile()` in server components — it needs the client.
