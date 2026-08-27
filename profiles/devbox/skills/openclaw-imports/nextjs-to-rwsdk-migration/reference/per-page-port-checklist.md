# Per-page port checklist

For each `app/**/page.tsx` you port to `src/app/pages/**/*.tsx`. The codegen script (`scripts/port-page.ts`) handles items 1–7 automatically; items 8–10 are manual.

---

## What `port-page.ts` strips

1. `import type { Metadata } from "next";`
2. `export const metadata = { … }` and `export const metadata: Metadata = { … }` blocks
3. `export async function generateMetadata({...}) { … }` (entire function body, handles nested braces correctly)
4. `export async function generateStaticParams() { … }`
5. Single-line export consts: `dynamic`, `runtime`, `revalidate`, `fetchCache`, `dynamicParams`, `preferredRegion`, `maxDuration`, `contentType`, `alt`, `size`
6. `params: Promise<{…}>` → `params: {…}`
7. `= await params` → `= params`

## What it converts

8. `export default async function PageName(…)` → `export async function NewName(…)` (default-export → named export, name passed as second CLI argument)

## What you still have to do by hand

9. **Catch-all wildcard params.** RWSDK gives you `params.$0: string`. Original Next code expected `params.slug: string[]`. Add this line at the top of catch-all page bodies:

   ```ts
   const slug = params.$0 ? params.$0.split("/").filter(Boolean) : undefined;
   ```

   Then remove the orphan import of `getAllWiki…Slugs` etc. (those were used by the deleted `generateStaticParams`).

10. **Effect-returning function calls.** If the legacy code does `const x = await someEffectFn(...)`, that's broken — Effect isn't always thenable across versions. Replace with:

    ```ts
    import * as Effect from "effect/Effect";
    const x = await Effect.runPromise(someEffectFn(...));
    ```

    Wrap in `try/catch` or `Effect.either` if the failure path matters (it almost always does for auth checks).

11. **`opengraph-image.tsx` files.** These don't have a clean port — `@vercel/og` has Node-only deps that don't survive in Workers. Defer behind a `workers-og`-based handler.

12. **`generateMetadata` was setting page titles** — port to React 19 `<title>` + `<meta>` tags inside the page's returned JSX. React 19 hoists them into `<head>`:

    ```tsx
    export function BlogDetail({ params }: Props) {
      const post = getPostBySlug(params.slug);
      …
      return (
        <>
          <title>{`${post.title} | darkmatter`}</title>
          <meta name="description" content={post.excerpt} />
          <article>…</article>
        </>
      );
    }
    ```

13. **Wire the new component into `src/worker.tsx`.** Import + add a `route()` entry. If you used a `Stub` placeholder during incremental migration, remove the stub line.

---

## Per-page checklist (copy/paste for review)

```
[ ] cp app/foo/page.tsx -> src/app/pages/Foo.tsx
[ ] bun scripts/port-page.ts src/app/pages/Foo.tsx FooPage
[ ] Inspect the result; fix any orphan imports the strip created.
[ ] Catch-all? Convert params.$0 manually.
[ ] Any Effect-returning function awaits? Wrap in Effect.runPromise.
[ ] Add per-page <title>/<meta> if the original had generateMetadata.
[ ] Import + route() in src/worker.tsx.
[ ] bun run check passes.
[ ] Probe the page locally: bun run dev + curl /foo.
```

---

## File-name conventions

Use PascalCase, named exports matching the file:

- `app/foo/page.tsx` → `src/app/pages/Foo.tsx` exporting `Foo`
- `app/foo/[slug]/page.tsx` → `src/app/pages/foo/Detail.tsx` exporting `FooDetail`
- `app/foo/[[...slug]]/page.tsx` → `src/app/pages/foo/CatchAll.tsx` exporting `FooCatchAll`

The directory mirrors the route prefix; the file name describes the route _shape_ (Index, Detail, CatchAll). This lets you grep the route source from a URL pattern instantly.

---

## `app/` is reference-only after porting

Leave the legacy `app/` directory in place during the migration — it's a useful side-by-side comparison and a free safety net. After every route is ported and the prototype is green, delete `app/` in a final cleanup commit.
