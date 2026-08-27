# vite + tsconfig + package.json

The three config files that have to land together. Drift between them is the most common cause of "it compiles in editor but the build dies."

---

## `vite.config.mts`

```ts
import { defineConfig } from "vite";
import { redwood } from "rwsdk/vite";
import { cloudflare } from "@cloudflare/vite-plugin";
import tailwindcss from "@tailwindcss/vite";
import { resolve } from "node:path";

const here = (p: string) => resolve(import.meta.dirname, p);

export default defineConfig({
  // Tailwind v4's vite plugin uses Vite's createResolver() which requires an
  // `ssr` environment to exist. RWSDK only creates a `worker` environment, so
  // we stub `ssr` here. From the rwsdk tailwind docs.
  environments: {
    ssr: {},
  },
  resolve: {
    alias: {
      "@": here("."),

      "next/link": here("./src/shims/next-link.tsx"),
      "next/image": here("./src/shims/next-image.tsx"),
      "next/navigation": here("./src/shims/next-navigation.ts"),
      "next/font/google": here("./src/shims/next-font-google.ts"),
      "next/font/local": here("./src/shims/next-font-local.ts"),
      "next/server": here("./src/shims/next-server.ts"),
      "next/og": here("./src/shims/next-og.ts"),
      "next/headers": here("./src/shims/next-headers.ts"),
    },
  },
  plugins: [
    cloudflare({ viteEnvironment: { name: "worker" } }),
    tailwindcss(),
    redwood({
      forceClientPaths: [
        // lucide-react has a deep transitive "use client" boundary at
        // dist/esm/Icon.mjs that the rwsdk scanner sometimes misses on cold
        // start, causing "No module found for ... Icon.mjs in module lookup"
        // when the Cloudflare vite plugin probes the worker entry before
        // the scan finishes. Pre-registering it forces it into the lookup
        // map before the race window opens. See "Known traps" in SKILL.md.
        "node_modules/lucide-react/dist/esm/Icon.mjs",
        "node_modules/lucide-react/dist/esm/context.mjs",
        "node_modules/lucide-react/dist/esm/DynamicIcon.mjs",
      ],
    }),
  ],
});
```

Plugin order is load-bearing. `cloudflare` first (it defines the worker environment), `tailwindcss` (needs the environments stub to be in place), `redwood` last (it layers RSC environments on top).

Don't add a second cloudflare plugin (e.g. via `Cloudflare.Vite` from alchemy) — they conflict.

## `forceClientPaths` catalog

Add globs for any package that ships a `"use client"` boundary inside `node_modules` AND is reached through enough barrel-re-export hops that the scanner races on cold start. Confirmed examples:

| Package | Files to register |
| --- | --- |
| `lucide-react@^1.16` | `dist/esm/Icon.mjs`, `dist/esm/context.mjs`, `dist/esm/DynamicIcon.mjs` |

If you hit `No module found for '/node_modules/<pkg>/...'` for a different package, grep that package's `dist/` (or `build/`) for `"use client"` and add each matching file path. Cheap to over-register; expensive to under-register.

---

## `tsconfig.json`

```jsonc
{
  "compilerOptions": {
    "target": "es2022",
    "lib": ["DOM", "DOM.Iterable", "ESNext", "ES2022"],
    "jsx": "react-jsx",
    "module": "es2022",
    "moduleResolution": "bundler",
    "types": [
      "node",
      "@cloudflare/workers-types",
      "./worker-configuration.d.ts",
      "./src/types/rw.d.ts",
      "./src/types/vite.d.ts"
    ],
    "paths": {
      "@/*": ["./*"],
      // Mirror the vite aliases so editor IntelliSense follows them.
      "next/link": ["./src/shims/next-link"],
      "next/image": ["./src/shims/next-image"],
      "next/navigation": ["./src/shims/next-navigation"],
      "next/font/google": ["./src/shims/next-font-google"],
      "next/font/local": ["./src/shims/next-font-local"],
      "next/server": ["./src/shims/next-server"],
      "next/og": ["./src/shims/next-og"],
      "next/headers": ["./src/shims/next-headers"]
    },
    "resolveJsonModule": true,
    "noEmit": true,
    "isolatedModules": true,
    "allowSyntheticDefaultImports": true,
    "forceConsistentCasingInFileNames": true,
    "esModuleInterop": true,
    "strict": false,
    "skipLibCheck": true,
    "incremental": true
  },
  "include": [
    "src/**/*.ts",
    "src/**/*.tsx",
    "components/**/*.ts",
    "components/**/*.tsx",
    "lib/**/*.ts",
    "lib/**/*.tsx",
    "hooks/**/*.ts",
    "hooks/**/*.tsx"
  ],
  "exclude": [
    "node_modules",
    ".next",
    ".open-next",
    ".alchemy",
    ".wrangler",
    "app",
    "**/*.test.ts",
    "**/*.test.tsx"
  ]
}
```

- `strict: false` is intentional — the legacy code likely doesn't survive `strict: true` and tightening it is its own follow-up. Keep migration cleanly scoped.
- `app` is excluded because the legacy Next.js `app/` directory is kept around as a reference but isn't part of the build.
- Per-file excludes for known-broken-on-import legacy components (charts, sidebars from shadcn-ui) — add as needed. Better to ship and fix on follow-up than to block the migration on cosmetic type errors that exist on `main` too.
- `worker-configuration.d.ts` is generated by `wrangler types`. Bootstrap it with a stub `interface Env { ASSETS: Fetcher }` so tsc has something to resolve before the first `bun run generate`.

---

## `package.json` deltas

Drop:

- `next`
- `@opennextjs/cloudflare`
- `@flydotio/dockerfile` (if present — we're leaving Fly behind)
- `babel-plugin-react-compiler` (re-add later via `@vitejs/plugin-react`-based setup if needed)
- `next-env.d.ts` reference (delete the file too)
- `@typescript/native-preview` (Next-specific)

Add:

```jsonc
{
  "scripts": {
    "dev": "vite dev",
    "build": "bun run generate:blog-manifest && vite build",
    "preview": "vite preview",
    "release": "rw-scripts ensure-deploy-env && bun run build && wrangler deploy",
    "deploy": "bun run generate:blog-manifest && ALCHEMY_PLAIN=1 alchemy deploy ./alchemy.run.ts",
    "deploy:dev": "bun run generate:blog-manifest && ALCHEMY_PLAIN=1 alchemy deploy ./alchemy.run.ts --stage dev --yes",
    "deploy:staging": "bun run generate:blog-manifest && ALCHEMY_PLAIN=1 alchemy deploy ./alchemy.run.ts --stage staging",
    "deploy:production": "bun run generate:blog-manifest && ALCHEMY_PLAIN=1 alchemy deploy ./alchemy.run.ts --stage production",
    "destroy": "ALCHEMY_PLAIN=1 alchemy destroy ./alchemy.run.ts",
    "generate:blog-manifest": "bun scripts/generate-blog-manifest.ts",
    "generate": "rw-scripts ensure-env && wrangler types --include-runtime false",
    "worker:run": "rw-scripts worker-run",
    "check": "tsc",
    "types": "tsc"
  },
  "dependencies": {
    "rwsdk": "1.2.9",
    "react": "19.2.6",
    "react-dom": "19.2.6",
    "react-server-dom-webpack": "19.2.6",
    "@fontsource-variable/inter": "^5.2.8",
    "effect": "4.0.0-beta.68"
  },
  "devDependencies": {
    "@cloudflare/vite-plugin": "1.33.2",
    "@cloudflare/workers-types": "4.20260426.1",
    "@effect/platform-bun": "4.0.0-beta.68",
    "@effect/platform-node": "4.0.0-beta.68",
    "@tailwindcss/vite": "^4",
    "@vercel/og": "^0.6.5",
    "alchemy": "2.0.0-beta.40",
    "tailwindcss": "^4",
    "typescript": "~5.9.0",
    "vite": "~7.3.2",
    "wrangler": "4.85.0"
  },
  "overrides": {
    "@types/react": "19.2.14",
    "@types/react-dom": "19.2.3",
    "csstype": "^3.1.3"
  },
  "resolutions": {
    "@types/react": "19.2.14",
    "@types/react-dom": "19.2.3",
    "csstype": "^3.1.3"
  }
}
```

The `overrides` + `resolutions` block is non-optional. Radix subdeps ship their own `@types/react` copy with an incompatible `csstype` version, which makes tsc fail with `Type 'React.CSSProperties' is not assignable...`. Forcing single versions through both fields covers npm, yarn, pnpm, and bun.

Pin `alchemy` exactly (no caret) — `^2.0.0-beta.40` resolves to a `pipeline-v2-test` dist-tag in CI that crashes with `a.asEffect is not a function`. See `alchemy-deploy.md` for the writeup.

After modifying overrides, `rm -rf node_modules bun.lock && bun install` — incremental installs don't always deduplicate cleanly.

---

## `src/types/rw.d.ts`

```ts
import "rwsdk/worker";

declare module "rwsdk/worker" {
  interface DefaultAppContext {
    pathname?: string;
    // Add `user`, `session`, etc. as middleware populates them.
  }
}
```

This is how you get type safety on `ctx.pathname` inside route handlers and server components.

## `src/types/vite.d.ts`

```ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_POSTHOG_KEY?: string;
  readonly VITE_POSTHOG_HOST?: string;
  // Add other VITE_ vars the app reads.
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
  readonly dirname: string;
}
```

`import.meta.env.VITE_*` replaces `process.env.NEXT_PUBLIC_*`. Vite only inlines values whose key starts with `VITE_`.
