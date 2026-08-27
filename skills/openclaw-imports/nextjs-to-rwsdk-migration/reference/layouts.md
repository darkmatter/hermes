# Layouts (`layout()` from `rwsdk/router`)

The replacement for Next.js's `app/(group)/layout.tsx` convention. RWSDK ships a `layout()` helper in `rwsdk/router` (since 1.2.x) that wraps a group of routes in a shared React component. Layouts can be server components, can nest, and the routing structure makes the chrome decision explicit.

---

## Anti-pattern this replaces

It's tempting to keep a single `<SiteShell>` wrapper inside `Document` that uses a client-side hook to decide which routes get chrome:

```tsx
// DON'T do this
"use client";
import { useEffect, useState } from "react";

function useClientPathname() { /* ...listen to popstate + rwsdk:navigation... */ }

export function SiteShell({ children }) {
  const pathname = useClientPathname();
  const isWikiRoute = /^(\/internal)?\/(wiki|vault)(\/|$)/i.test(pathname ?? "");
  if (isWikiRoute) return <>{children}</>;
  return <><SiteHeader /><div>{children}</div><SiteFooter /></>;
}
```

Three problems:

1. **SSR is wrong on first paint** — server renders the chrome unconditionally; client hides it on `/wiki/*` after hydration, so users see a flash.
2. **The whole subtree becomes client-hydrated** because `SiteShell` is `"use client"`. Server components below it can't stream cleanly.
3. **The "which routes get chrome" decision lives in a regex**, not in routing structure. The next person adding a route has to remember to update both the worker and the regex.

Use `layout()` instead.

---

## Canonical pattern

```tsx
// src/app/layouts/SiteLayout.tsx — server component
import type { LayoutProps } from "rwsdk/router";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";

export function SiteLayout({ children }: LayoutProps) {
  return (
    <>
      <SiteHeader />
      <div className="pt-16">{children}</div>
      <SiteFooter />
    </>
  );
}

// src/app/layouts/WikiLayout.tsx — passthrough (or replace with sidebar shell later)
import type { LayoutProps } from "rwsdk/router";
export function WikiLayout({ children }: LayoutProps) {
  return <>{children}</>;
}
```

```ts
// src/worker.tsx
import { layout, render, route } from "rwsdk/router";

render(Document, [
  // Register wiki/vault FIRST — see "Route order" below.
  layout(WikiLayout, [
    route("/internal/wiki", InternalWikiCatchAll),
    route("/internal/wiki/*", InternalWikiCatchAll),
    route("/internal/vault", InternalVaultCatchAll),
    route("/internal/vault/*", InternalVaultCatchAll),
    route("/wiki/*", WikiCatchAll),
    route("/vault", VaultCatchAll),
    route("/vault/*", VaultCatchAll),
  ]),

  layout(SiteLayout, [
    route("/", Home),
    route("/blog", BlogIndex),
    route("/blog/:slug", BlogDetail),
    route("/products", ProductsIndex),
    route("/internal", InternalIndex),
    route("/internal/:slug", InternalDetail),
  ]),

  // Bare route — no layout. For OG-image shells, raw API responses, etc.
  route("/og-proxy/internal/:slug", OgProxyInternal),

  // Catch-all 404 with chrome.
  layout(SiteLayout, [
    route("/*", ({ params }) => <NotFound path={`/${params.$0 ?? ""}`} />),
  ]),
]);
```

`Document` shrinks to a pure HTML shell:

```tsx
<body>
  <ThemeProvider …>
    <PostHogProvider>{children}</PostHogProvider>
  </ThemeProvider>
  <script>import("/src/client.tsx")</script>
</body>
```

No more `<SiteShell>`, no more `useClientPathname()`.

---

## Route order

**rwsdk matches routes in registration order. Literal paths beat `:param` captures.** If your two layouts both touch `/internal/<...>`, the more specific routes have to come first.

```ts
// WRONG — /internal/wiki returns 404 (matched as InternalDetail with slug="wiki")
render(Document, [
  layout(SiteLayout, [
    route("/internal", InternalIndex),
    route("/internal/:slug", InternalDetail),     // catches /internal/wiki
  ]),
  layout(WikiLayout, [
    route("/internal/wiki", InternalWikiCatchAll), // never reached
    route("/internal/wiki/*", InternalWikiCatchAll),
  ]),
]);

// RIGHT — /internal/wiki and /internal/wiki/foo go to InternalWikiCatchAll
render(Document, [
  layout(WikiLayout, [
    route("/internal/wiki", InternalWikiCatchAll),
    route("/internal/wiki/*", InternalWikiCatchAll),
  ]),
  layout(SiteLayout, [
    route("/internal", InternalIndex),
    route("/internal/:slug", InternalDetail),
  ]),
]);
```

Add a comment at the layout boundary so the next person doesn't "fix" the ordering by alphabetizing:

```ts
// WikiLayout is registered first so the literal /internal/wiki and
// /internal/vault paths win over /internal/:slug in SiteLayout. Without
// this order, /internal/wiki 404s because :slug captures "wiki".
layout(WikiLayout, [...]),
layout(SiteLayout, [...]),
```

---

## What server-only layouts buy you

- **Correct first-paint** — server picks the right chrome based on the URL, not after hydration.
- **No extra hydration cost** — `SiteLayout` and `WikiLayout` are server components; the routing structure dictates which one renders, no client JS needed for layout selection.
- **Page components stay server components** (or stay `"use client"` if they actually need it) without inheriting client-ness from a parent shell.

The original `<SiteShell>` is `"use client"` because it uses `useEffect` to listen to `popstate` and `rwsdk:navigation`. Once layouts own the chrome-selection decision via routing, that polyfill is no longer needed and you can delete the component.

---

## Layout props

```ts
import type { LayoutProps } from "rwsdk/router";

export function SiteLayout({ children, requestInfo }: LayoutProps) {
  // requestInfo is only passed to server-component layouts.
  // Use it for layout-level behavior that depends on the request:
  //   - Read ctx (e.g. ctx.user populated by middleware)
  //   - Inject per-route ARIA landmarks based on URL
  //   - Set per-layout response headers via requestInfo.response.headers
  return …;
}
```

If a layout is `"use client"`, it gets only `{ children }` — `requestInfo` is server-only by construction.

---

## Nesting

`layout()` composes with itself, `prefix()`, and `render()`:

```ts
render(Document, [
  layout(AppLayout, [
    prefix("/admin", [
      layout(AdminLayout, [
        route("/", AdminDashboard),
        route("/users", UserManagement),
      ]),
    ]),
  ]),
]);
```

Outer layouts wrap inner. The above renders `<AppLayout><AdminLayout><AdminDashboard /></AdminLayout></AppLayout>`. Useful for admin/dashboard sections that want both the outer site chrome AND a dashboard-specific sidebar.

For the typical Darkmatter Next migration you probably only need 2–3 top-level layouts (site chrome / wiki frame / dashboard frame). Reserve nesting for cases where you genuinely want both.

---

## Migration checklist

When porting a Next.js app with multiple `layout.tsx` files:

- [ ] `app/layout.tsx` → `src/app/Document.tsx` (the `<html>` shell — already done in Phase 4).
- [ ] `app/(public)/layout.tsx` → `src/app/layouts/PublicLayout.tsx`, wrap routes with `layout(PublicLayout, [...])`.
- [ ] `app/(internal)/layout.tsx` → `src/app/layouts/InternalLayout.tsx`, same.
- [ ] Delete any `<SiteShell>`-style client polyfill in `Document`.
- [ ] Verify route order: literal paths inside the more-specific layout get registered before parametric paths in the more-general layout.
- [ ] Smoke-test that wiki / no-chrome routes don't emit the SiteHeader/SiteFooter HTML (`curl … | grep -c '<footer'` should be 0 on those routes).
