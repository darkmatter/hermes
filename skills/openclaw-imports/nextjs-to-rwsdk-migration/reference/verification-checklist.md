# Verification checklist

Each phase has a gate. Don't claim "done" before the gate is green. Copy this checklist into the migration PR description and check items off as you go.

---

## Phase 1 — Worktree + clean scaffold

- [ ] `git worktree add` created a fresh worktree on `prototype/rwsdk-migration`
- [ ] Reference rwsdk app exists under `/tmp/rwsdk-ref/reference-app/`
- [ ] In the target worktree: `next.config.{js,mjs,ts}`, `next-env.d.ts`, `middleware.ts`, `open-next.config.ts`, `.next/`, `.open-next/`, `Dockerfile`, `fly.toml` are deleted
- [ ] `src/{worker.tsx, client.tsx}` and `src/app/Document.tsx` copied from the reference app

## Phase 2 — Build-system files

- [ ] `vite.config.mts` matches the template in `reference/vite-config.md`
- [ ] `tsconfig.json` has the `paths` shim mirror + node types
- [ ] `wrangler.jsonc` has `main: src/worker.tsx` + nodejs_compat flags
- [ ] `package.json` has `rwsdk`, `@cloudflare/vite-plugin`, `@tailwindcss/vite`, exact-pinned `alchemy`, overrides + resolutions for `@types/react`/csstype
- [ ] `rm -rf node_modules bun.lock && bun install` succeeds with no peer-dep errors
- [ ] `find node_modules -path '*/@types/react/package.json'` returns exactly one path
- [ ] `find node_modules -path '*/csstype/package.json'` returns exactly one path

## Phase 3 — Shims

- [ ] `src/shims/` has all seven files from `reference/shims.md`
- [ ] `bun run check` (tsc) is clean on a representative component file that uses `next/link` + `next/image` + `next/navigation`
- [ ] Sanity check: `grep -rln "from ['\"]next" components lib hooks` returns the expected files (mostly Link/Image — those resolve via aliases, no error)

## Phase 4 — Document + CSS

- [ ] `src/app/Document.tsx` uses `import styles from "./globals.css?url"` + `<link rel="stylesheet" href={styles} />`
- [ ] `src/app/globals.css` imports `@fontsource-variable/*` + the legacy stylesheet + any `@font-face` declarations
- [ ] `bun run build` produces both `dist/worker/index.js` AND `dist/client/assets/globals-*.css`
- [ ] `find dist/client -name '*.css'` is non-empty (this is the gotcha gate)

## Phase 5 — Worker + routing

- [ ] `src/worker.tsx` has the skeleton from `reference/worker-and-routing.md`
- [ ] Home route is wired and `bun run dev` returns 200 on `/`
- [ ] `<link rel="stylesheet">` appears in `curl http://localhost:5173/ | grep link`
- [ ] `feed.xml` and `sitemap.xml` are wired as non-document routes (XML, not HTML)
- [ ] Any redirect routes (`/wiki` → `/internal/wiki`) work

## Phase 6 — Page ports

- [ ] All `app/**/page.tsx` files have a `src/app/pages/**/*.tsx` counterpart
- [ ] `scripts/port-page.ts` was used for the mechanical ports
- [ ] Catch-all routes have explicit `params.$0?.split("/").filter(Boolean)` conversions
- [ ] Any `await effectFn()` calls are now `Effect.runPromise(effectFn())`
- [ ] Every ported page returns 200 in `bun run dev`
- [ ] No console errors in dev for any ported page (open them all, look at devtools)

## Phase 7 — Alchemy deploy

- [ ] `alchemy.run.ts` matches the template in `reference/alchemy-deploy.md` (`Cloudflare.Worker` + `bundle: false` + `isExternal: true`)
- [ ] `domainsForStage` excludes `dev` + `pr-*` from custom domains
- [ ] `bun alchemy deploy --stage dev --yes` produces a working `*-dev-*.workers.dev` URL
- [ ] The deployed URL returns 200 on `/` and serves the CSS correctly
- [ ] `bun alchemy destroy --stage dev --yes` cleans up

## Phase 8 — Preview CI

- [ ] `.github/workflows/preview-deploy.yml` matches `reference/preview-ci.md`
- [ ] `.github/workflows/preview-cleanup.yml` matches `reference/preview-ci.md`
- [ ] Both workflows have `permissions: pull-requests: write`
- [ ] Repo has `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` secrets
- [ ] Opening a draft PR triggers the preview workflow and it ends green
- [ ] The sticky PR comment lands with a clickable preview URL
- [ ] Pushing a new commit to the PR triggers a redeploy (and cancels the in-flight one)
- [ ] Closing the PR triggers the cleanup workflow

---

## Browser verification (recommended before merging)

Drive the deployed preview through Playwright (or any real browser):

- [ ] Every top-level route loads with `bg = rgb(<dark>)` and styled chrome (header, footer, fonts)
- [ ] No console errors
- [ ] Click a `<Link>` → navigation completes without full page reload (verifies SPA mode)
- [ ] Hit a non-existent slug → renders the NotFound page, returns 404 status
- [ ] If the app has auth-gated routes, verify the gated content is NOT visible unauthenticated (this is where Effect-await silent-failures bite)

---

## Final cleanup (after every gate is green)

- [ ] Delete the legacy `app/` directory
- [ ] Delete `next-env.d.ts` if it crept back
- [ ] Delete `patches/` entries for `next-*` packages
- [ ] Update top-level `README.md` to point at rwsdk docs
- [ ] Update `AGENTS.md` / `CLAUDE.md` to reflect the new stack
- [ ] Squash-merge the PR; let the cleanup workflow tear down the preview stage
