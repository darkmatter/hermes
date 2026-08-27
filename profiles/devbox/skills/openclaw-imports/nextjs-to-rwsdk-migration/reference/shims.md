# `next/*` shims

Seven small modules under `src/shims/` resolved by Vite's `resolve.alias` (see `vite-config.md`). Together they let the existing Next.js component tree compile and run on rwsdk without per-file rewrites. The trade-off: you keep the original `import Link from "next/link"` lines in 200+ components and pay the maintenance cost in one place.

Copy each file verbatim into `src/shims/` of the target repo, then wire the aliases in `vite.config.mts` and `tsconfig.json` (see `vite-config.md`).

---

## `src/shims/next-link.tsx`

```tsx
import type { AnchorHTMLAttributes, ReactNode } from "react";

type LinkProps = Omit<AnchorHTMLAttributes<HTMLAnchorElement>, "href"> & {
  href: string | { pathname?: string };
  prefetch?: boolean;
  replace?: boolean;
  scroll?: boolean;
  shallow?: boolean;
  locale?: string | false;
  children?: ReactNode;
};

const Link = ({
  href,
  prefetch: _prefetch,
  replace: _replace,
  scroll: _scroll,
  shallow: _shallow,
  locale: _locale,
  children,
  ...rest
}: LinkProps) => {
  const url = typeof href === "string" ? href : (href?.pathname ?? "#");
  return (
    <a href={url} {...rest}>
      {children}
    </a>
  );
};

export default Link;
```

RWSDK upgrades plain `<a>` clicks to SPA-style navigation via `initClientNavigation` in `src/client.tsx`. There is no `<Link>` component to mimic — the anchor IS the spa link. `prefetch` etc. are accepted and dropped because rwsdk does prefetching via `<link rel="x-prefetch">` instead.

---

## `src/shims/next-image.tsx`

```tsx
import type { ImgHTMLAttributes, CSSProperties } from "react";

type StaticImageData = { src: string };

type ImageProps = Omit<
  ImgHTMLAttributes<HTMLImageElement>,
  "src" | "width" | "height"
> & {
  src: string | StaticImageData;
  alt: string;
  width?: number | string;
  height?: number | string;
  fill?: boolean;
  priority?: boolean;
  quality?: number;
  unoptimized?: boolean;
  placeholder?: "blur" | "empty";
  blurDataURL?: string;
  loader?: unknown;
  sizes?: string;
};

const Image = ({
  src,
  alt,
  width,
  height,
  fill,
  priority,
  quality: _quality,
  unoptimized: _unoptimized,
  placeholder: _placeholder,
  blurDataURL: _blurDataURL,
  loader: _loader,
  sizes,
  style,
  ...rest
}: ImageProps) => {
  const url = typeof src === "string" ? src : (src as StaticImageData).src;
  const finalStyle: CSSProperties | undefined = fill
    ? {
        position: "absolute",
        inset: 0,
        width: "100%",
        height: "100%",
        ...style,
      }
    : style;

  return (
    <img
      src={url}
      alt={alt}
      width={fill ? undefined : (width as number | undefined)}
      height={fill ? undefined : (height as number | undefined)}
      sizes={sizes}
      style={finalStyle}
      loading={priority ? "eager" : "lazy"}
      decoding="async"
      {...rest}
    />
  );
};

export default Image;
```

Limit: no Next.js image-optimization pipeline. Original assets in `/public` are served as-is by the `ASSETS` binding. If a site relies on Next's automatic image resizing, plan a `@cloudflare/images`-based replacement separately.

---

## `src/shims/next-navigation.ts`

```ts
import { useEffect, useState } from "react";

export function usePathname(): string {
  const [pathname, setPathname] = useState<string>(() =>
    typeof window === "undefined" ? "/" : window.location.pathname,
  );

  useEffect(() => {
    if (typeof window === "undefined") return;
    setPathname(window.location.pathname);
    const onChange = () => setPathname(window.location.pathname);
    window.addEventListener("popstate", onChange);
    window.addEventListener("rwsdk:navigation", onChange as EventListener);
    return () => {
      window.removeEventListener("popstate", onChange);
      window.removeEventListener(
        "rwsdk:navigation",
        onChange as EventListener,
      );
    };
  }, []);

  return pathname;
}

export function useSearchParams(): URLSearchParams | null {
  const [params, setParams] = useState<URLSearchParams | null>(() =>
    typeof window === "undefined"
      ? null
      : new URLSearchParams(window.location.search),
  );

  useEffect(() => {
    if (typeof window === "undefined") return;
    setParams(new URLSearchParams(window.location.search));
    const onChange = () =>
      setParams(new URLSearchParams(window.location.search));
    window.addEventListener("popstate", onChange);
    window.addEventListener("rwsdk:navigation", onChange as EventListener);
    return () => {
      window.removeEventListener("popstate", onChange);
      window.removeEventListener(
        "rwsdk:navigation",
        onChange as EventListener,
      );
    };
  }, []);

  return params;
}

export function useRouter() {
  return {
    push: (href: string) => {
      if (typeof window !== "undefined") window.location.assign(href);
    },
    replace: (href: string) => {
      if (typeof window !== "undefined") window.location.replace(href);
    },
    back: () => {
      if (typeof window !== "undefined") window.history.back();
    },
    refresh: () => {
      if (typeof window !== "undefined") window.location.reload();
    },
    prefetch: () => undefined,
    forward: () => {
      if (typeof window !== "undefined") window.history.forward();
    },
  };
}

export function notFound(): never {
  throw new Response("Not Found", { status: 404 });
}

export function redirect(url: string): never {
  throw new Response(null, { status: 307, headers: { Location: url } });
}

export function permanentRedirect(url: string): never {
  throw new Response(null, { status: 308, headers: { Location: url } });
}
```

The throw-a-Response trick is how rwsdk routes that need to interrupt rendering surface non-200 responses. RWSDK catches a thrown `Response` and returns it. This matches Next.js's `notFound()` semantics without needing a `not-found.tsx` file convention.

`useRouter` is intentionally minimal — for full SPA navigation, use rwsdk's `initClientNavigation` (handled by `src/client.tsx`), not these helpers. The shim exists for components that call `.push()` for genuine programmatic navigation.

---

## `src/shims/next-font-google.ts`

```ts
type FontReturn = {
  className: string;
  variable: string;
  style: { fontFamily: string };
};

const factory =
  (name: string) =>
  (opts: { variable?: string; subsets?: string[]; display?: string } = {}): FontReturn => ({
    className: "",
    variable: opts.variable ?? `--font-${name.toLowerCase()}`,
    style: { fontFamily: name },
  });

export const Inter = factory("inter");
export const Montserrat = factory("montserrat");
export const Source_Code_Pro = factory("source-code-pro");
export const DM_Mono = factory("dm-mono");
export const Roboto = factory("roboto");
export const Lora = factory("lora");
```

Add factories for whatever fonts the target repo uses. The shim returns the shape that consumers depend on (`.variable`, `.className`, `.style.fontFamily`) but does NOT load fonts. Wire actual font loading via `@fontsource-variable/*` packages imported from `globals.css`, a `<link>` to Google Fonts in `Document.tsx`, or `@font-face` declarations for local woff2 files.

---

## `src/shims/next-font-local.ts`

```ts
type LocalFontInput = {
  variable?: string;
  src?: unknown;
};

type FontReturn = {
  className: string;
  variable: string;
  style: { fontFamily: string };
};

const localFont = (opts: LocalFontInput = {}): FontReturn => ({
  className: "",
  variable: opts.variable ?? "--font-local",
  style: { fontFamily: "local" },
});

export default localFont;
```

Same logic as the Google shim. The actual font file is served from `public/fonts/` and referenced via `@font-face` in `globals.css`.

---

## `src/shims/next-server.ts`

```ts
export type NextRequest = Request;

export const NextResponse = {
  next: () => undefined,
  rewrite: (url: URL) => {
    return new Response(null, {
      status: 200,
      headers: { "x-rewrite-to": url.toString() },
    });
  },
  redirect: (url: string | URL, status = 307) =>
    new Response(null, {
      status,
      headers: { Location: typeof url === "string" ? url : url.toString() },
    }),
  json: (body: unknown, init: ResponseInit = {}) =>
    new Response(JSON.stringify(body), {
      ...init,
      headers: {
        ...(init.headers as Record<string, string> | undefined),
        "Content-Type": "application/json",
      },
    }),
};
```

The only Next.js file you should still find using these types after the migration is the legacy `middleware.ts`, which you delete in phase 1. The shim is here so a stray import in a component doesn't break the build. If you find one, refactor it to plain web APIs (`new Response(...)`) rather than threading the shim through new code.

---

## `src/shims/next-og.ts`

```ts
export { ImageResponse } from "@vercel/og";
```

`@vercel/og` is `next/og`'s underlying engine. Re-exporting it lets `opengraph-image.tsx` files compile.

**Caveat:** `@vercel/og` has Node-only dependencies (`fs`, `path`) that don't all work in the Workers runtime. If a target repo has more than one `opengraph-image.tsx` or relies on dynamic OG generation, plan to port to `workers-og` (Cloudflare's port of satori) or write a dedicated worker route that calls satori directly. See [`workers-og`](https://github.com/kvnang/workers-og).

---

## `src/shims/next-headers.ts`

```ts
import { requestInfo } from "rwsdk/worker";

export function headers(): Promise<Headers> {
  return Promise.resolve(requestInfo.request.headers);
}

export function cookies(): Promise<{
  get(name: string): { name: string; value: string } | undefined;
  getAll(): { name: string; value: string }[];
  has(name: string): boolean;
}> {
  const cookieHeader = requestInfo.request.headers.get("cookie") ?? "";
  const parsed = parseCookies(cookieHeader);

  return Promise.resolve({
    get(name) {
      const value = parsed.get(name);
      return value === undefined ? undefined : { name, value };
    },
    getAll() {
      return Array.from(parsed.entries()).map(([name, value]) => ({
        name,
        value,
      }));
    },
    has(name) {
      return parsed.has(name);
    },
  });
}

function parseCookies(header: string): Map<string, string> {
  const map = new Map<string, string>();
  if (!header) return map;
  for (const part of header.split(";")) {
    const idx = part.indexOf("=");
    if (idx === -1) continue;
    const name = part.slice(0, idx).trim();
    const value = part.slice(idx + 1).trim();
    if (name) map.set(name, decodeURIComponent(value));
  }
  return map;
}
```

`requestInfo` comes from `rwsdk/worker` and is populated per-request by the framework. Outside a request lifecycle the access throws — the shim returns a Promise of a Headers object to match the Next.js 15 async-cookies API, but the underlying read is synchronous.

Setting cookies via `cookies().set(...)` is not implemented here — server functions that set cookies should manipulate `requestInfo.response.headers` directly.
