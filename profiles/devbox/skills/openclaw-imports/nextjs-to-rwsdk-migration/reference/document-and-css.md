# `Document.tsx`, CSS, fonts, theming

The HTML shell, the CSS pipeline, and the gotcha that ate the most time in the first migration.

---

## The load-bearing pattern

From [docs.rwsdk.com/guides/frontend/tailwind/](https://docs.rwsdk.com/guides/frontend/tailwind/):

```tsx
// src/app/Document.tsx
import type React from "react";
import styles from "./globals.css?url";

export const Document: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => (
  <html lang="en" suppressHydrationWarning>
    <head>
      <meta charSet="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Site title</title>
      <link rel="stylesheet" href={styles} />
      <link rel="modulepreload" href="/src/client.tsx" />
    </head>
    <body>
      {children}
      <script>import("/src/client.tsx")</script>
    </body>
  </html>
);
```

The `?url` suffix tells Vite to give you the resolved URL of the CSS file (e.g. `/assets/globals-ozO2FdNR.css`) instead of importing the CSS for its side effects.

## The trap

If you write the more obvious `import "./globals.css"` instead, Vite bundles the CSS into the SSR (`dist/worker/`) output but does NOT emit a copy to `dist/client/`. Page HTML renders, the client hydrates, but no stylesheet is ever requested. The site looks like raw HTML in production while looking fine in dev (where Vite's HMR injects CSS via JS).

Symptom: production deploy serves the page with `bg = rgb(255, 255, 255)` and no Tailwind utilities applied. `<link rel="stylesheet">` is missing from `<head>`.

Fix: the `?url` import + explicit `<link>` shown above. Verify after building with:

```bash
ls dist/client/assets/*.css   # must produce a globals-*.css file
grep -o 'rel="stylesheet"[^>]*' dist/worker/index.js | head
```

---

## Wrapping in providers

Keep your client providers inside `Document`. They have to be `"use client"` (they use `useEffect`):

```tsx
// src/app/Document.tsx
import { ThemeProvider } from "@/components/theme-provider";
import { PostHogProvider } from "@/components/posthog-provider";
import { SiteShell } from "@/components/site-shell";

…
<body>
  <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
    <PostHogProvider>
      <SiteShell>{children}</SiteShell>
    </PostHogProvider>
  </ThemeProvider>
  <script>import("/src/client.tsx")</script>
</body>
```

`next-themes` works without any shim — it's a standalone npm package. PostHog provider needs a small refactor (drop `usePathname`/`useSearchParams`, listen to `popstate` + `rwsdk:navigation` directly).

---

## `src/app/globals.css`

Imports tailwind + fontsource fonts + the existing legacy stylesheet:

```css
@import "@fontsource-variable/inter";
@import "../../app/globals.css"; /* keep the original stylesheet as-is during migration */

@font-face {
  font-family: "Monaspace Neon";
  font-style: normal;
  font-weight: 100 900;
  font-display: swap;
  src: url("/fonts/monaspace-neon-var.woff2") format("woff2-variations");
}

:root {
  --font-monospace: "Monaspace Neon", ui-monospace, SFMono-Regular, Menlo,
    Monaco, Consolas, monospace;
  --font-inter: "Inter Variable", ui-sans-serif, system-ui, -apple-system,
    "Segoe UI", Roboto, sans-serif;
}
```

If the legacy app shipped a local font (via `next/font/local`), copy the woff2/ttf files into `public/fonts/` and reference them via `@font-face`. The `next/font/local` shim returns class-name stubs but doesn't load the file — CSS does.

If the legacy app uses tailwind v3, switch to v4 as part of this migration. RWSDK's docs assume v4 and the `@tailwindcss/vite` plugin only ships v4 support.

---

## `src/client.tsx`

```ts
import { initClient, initClientNavigation } from "rwsdk/client";

const { handleResponse, onHydrated } = initClientNavigation();
initClient({ handleResponse, onHydrated });
```

Don't import CSS from here — that creates a phantom client-only stylesheet path. The Document is the single source of truth for stylesheets.

`initClientNavigation()` is what turns plain `<a href>` clicks into SPA-style transitions. Without it, every nav is a full page load.

---

## Per-page metadata

Document is a static shell. Per-route titles + meta tags are best done by dropping React 19 `<title>` / `<meta>` tags inside the page component's returned JSX. React 19 hoists them into `<head>` automatically:

```tsx
export function BlogDetail({ params }: { params: { slug: string } }) {
  const post = getPostMeta(params.slug);
  if (!post) return <NotFound />;

  return (
    <>
      <title>{`${post.title} | darkmatter`}</title>
      <meta name="description" content={post.excerpt} />
      <meta property="og:title" content={post.title} />
      …
      <article>{/* body */}</article>
    </>
  );
}
```

This replaces Next's `export const metadata` and `generateMetadata`. See [docs.rwsdk.com/guides/frontend/metadata/](https://docs.rwsdk.com/guides/frontend/metadata/).
