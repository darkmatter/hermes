# `worker.tsx` + routing

From [docs.rwsdk.com/core/routing/](https://docs.rwsdk.com/core/routing/). This is the file the Next App Router used to be.

---

## Skeleton

```tsx
// src/worker.tsx
import { defineApp } from "rwsdk/worker";
import { render, route } from "rwsdk/router";

import { Document } from "./app/Document";
import { setCommonHeaders } from "./app/headers";

import { Home } from "./app/pages/Home";
import { BlogIndex } from "./app/pages/blog/Index";
import { BlogDetail } from "./app/pages/blog/Detail";
import { NotFound } from "./app/pages/NotFound";

import { feedHandler } from "./app/routes/feed";
import { sitemapHandler } from "./app/routes/sitemap";

export type AppContext = {
  pathname: string;
};

export default defineApp([
  setCommonHeaders(),

  // Populate ctx for downstream handlers.
  ({ request, ctx }) => {
    ctx.pathname = new URL(request.url).pathname;
  },

  // Non-document responses (RSS, sitemap, redirects) sit ABOVE render(Document, ...)
  route("/feed.xml", feedHandler),
  route("/sitemap.xml", sitemapHandler),
  route(
    "/wiki",
    ({ request }) =>
      new Response(null, {
        status: 307,
        headers: { Location: new URL("/internal/wiki", request.url).toString() },
      }),
  ),

  // All HTML page routes share the Document shell.
  render(Document, [
    route("/", Home),
    route("/blog", BlogIndex),
    route("/blog/:slug", BlogDetail),

    // Wildcard catch-all 404
    route("/*", ({ params }) => <NotFound path={`/${params.$0 ?? ""}`} />),
  ]),
]);
```

`defineApp` returns a Worker-compatible `{ fetch }` handler. Export as default and you're done.

---

## Route patterns

| Pattern | Matches | `params` shape |
| --- | --- | --- |
| `route("/", h)` | exact `/` | `{}` |
| `route("/about", h)` | exact `/about` | `{}` |
| `route("/blog/:slug", h)` | `/blog/foo` (one segment) | `{ slug: string }` |
| `route("/blog/:cat/:slug", h)` | `/blog/news/foo` | `{ cat: string, slug: string }` |
| `route("/files/*", h)` | `/files/anything/multi/segment` | `{ $0: string }` |
| `route("/files/*/preview", h)` | `/files/x/y/preview` | `{ $0: string }` |

Wildcards capture the remaining path as a single string — `params.$0` — not as a `string[]` like Next's `[[...slug]]`. Convert with `params.$0?.split("/").filter(Boolean)` when the page needs the array form.

The bare wildcard `/*` matches everything not matched above it. Put it at the bottom of the `render(Document, [...])` array to act as a 404 fallback.

---

## HTTP method routing

```ts
route("/api/users", {
  get: () => new Response(JSON.stringify(users)),
  post: ({ request }) => new Response("Created", { status: 201 }),
  delete: () => new Response("Deleted", { status: 204 }),
});
```

OPTIONS + 405 are handled automatically. See the [routing docs](https://docs.rwsdk.com/core/routing/) for the full method matrix.

---

## Middleware vs route handlers

Anything inside `defineApp([...])` that ISN'T a `route()` call is middleware. It runs for every request in order, before route matching, and can:

- Mutate `ctx` (most common).
- Return a `Response` to short-circuit (e.g. auth, rewrites).
- Return nothing / undefined to continue.

Example (porting Next.js `middleware.ts` for a crawler rewrite):

```ts
// src/app/middleware/crawler-rewrite.ts
import type { RequestInfo } from "rwsdk/worker";

const CRAWLER_UA = ["slackbot", "twitterbot", "facebookexternalhit", "linkedinbot"];

export async function crawlerRewriteMiddleware({ request }: RequestInfo) {
  const ua = (request.headers.get("user-agent") ?? "").toLowerCase();
  const url = new URL(request.url);

  if (!CRAWLER_UA.some((p) => ua.includes(p))) return;
  if (!url.pathname.startsWith("/internal/")) return;

  const slug = url.pathname.replace(/^\/internal\//, "");
  if (!slug || slug.includes("/")) return;

  // Internal rewrite: fetch the proxy URL and return its response.
  return fetch(new Request(new URL(`/og-proxy/internal/${slug}`, url), request));
}
```

Wire it into `defineApp` as one of the array entries:

```ts
export default defineApp([
  setCommonHeaders(),
  ({ ctx, request }) => { ctx.pathname = new URL(request.url).pathname; },
  crawlerRewriteMiddleware,
  // …routes…
]);
```

---

## `setCommonHeaders`

The Next `next.config.{js,mjs}` `headers` function port. Apply global security headers per response:

```ts
// src/app/headers.ts
import { requestInfo } from "rwsdk/worker";

export function setCommonHeaders() {
  return () => {
    const { response } = requestInfo;
    response.headers.set("X-Content-Type-Options", "nosniff");
    response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
    response.headers.set("X-Frame-Options", "SAMEORIGIN");
  };
}
```

Returned function is itself a middleware. The outer factory exists so you can pass config (e.g. CSP) without making it a global.

---

## Per-page params shapes

```tsx
// app/blog/[slug]/page.tsx  →  src/app/pages/blog/Detail.tsx
type Props = { params: { slug: string } };  // NOT Promise<{...}>

export async function BlogDetail({ params }: Props) {
  const { slug } = params;                  // NOT await params
  …
}

// app/wiki/[[...slug]]/page.tsx  →  src/app/pages/wiki/CatchAll.tsx
type Props = { params: { $0?: string } };

export async function WikiCatchAll({ params }: Props) {
  const slug = params.$0 ? params.$0.split("/").filter(Boolean) : undefined;
  return <WikiPageContent slug={slug} />;
}
```

Next 15+ made `params` a Promise. RWSDK passes it as a plain object. Drop the `Promise<>` wrapper and drop `await params`. The `port-page.ts` codegen does both automatically.

---

## Non-page routes (RSS, sitemaps, API)

For routes that return non-HTML responses, write a function that returns `Response` and register it OUTSIDE `render(Document, [...])`:

```ts
// src/app/routes/feed.ts
export function feedHandler() {
  const items = …;
  const feed = `<?xml version="1.0" …>${items}</rss>`;
  return new Response(feed, {
    headers: { "Content-Type": "application/rss+xml; charset=utf-8" },
  });
}

// src/worker.tsx
route("/feed.xml", feedHandler),
```

If you wrap it in `render(Document, …)` by accident, RWSDK will wrap the XML in `<html>` and break the feed.

---

## `linkFor` for type-safe internal links

```ts
// src/app/shared/links.ts
import { linkFor } from "rwsdk/router";
import type * as Worker from "../../worker";
type App = typeof Worker.default;

export const link = linkFor<App>();
```

```tsx
const href = link("/blog/:slug", { slug: post.slug });
```

Compile-time-checked against the route tree in `worker.tsx`. Use type-only imports so the worker bundle doesn't end up in the client.

See [Generating Links](https://docs.rwsdk.com/core/routing/#generating-links).

---

## `ctx` (`AppContext`)

Mutate `ctx` from middleware, then access it inside route handlers + server components:

```ts
// in middleware
({ request, ctx }) => {
  ctx.pathname = new URL(request.url).pathname;
};

// in a page component
export function Foo({ ctx }: { ctx: AppContext }) {
  return <div>You're on {ctx.pathname}</div>;
}
```

Augment the type via the `DefaultAppContext` interface in `src/types/rw.d.ts` so TypeScript follows along. See `vite-config.md`.
