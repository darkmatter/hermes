# Alchemy deploy

How `alchemy.run.ts` should look, why we don't use `Cloudflare.Vite` (yet), and how stages map onto preview URLs.

---

## `alchemy.run.ts`

```ts
import * as Alchemy from "alchemy";
import * as Cloudflare from "alchemy/Cloudflare";
import * as Effect from "effect/Effect";

const PROJECT = "darkmatter";
const SERVICE = "web-rwsdk"; // keep distinct from the legacy SERVICE during cutover

const domainsForStage = (stage: string): string[] | undefined => {
  // dev + every per-PR preview stage gets the auto-assigned *.workers.dev URL.
  // Real domains are reserved for production / staging.
  if (stage === "dev" || stage.startsWith("pr-")) {
    return undefined;
  }

  const raw =
    process.env.CLOUDFLARE_WORKER_DOMAINS ??
    process.env.CLOUDFLARE_WORKER_DOMAIN;

  if (!raw) return undefined;

  const domains = raw
    .split(",")
    .map((d) => d.trim())
    .filter(Boolean);

  return domains.length > 0 ? domains : undefined;
};

const program = Effect.gen(function* () {
  const stage = yield* Alchemy.Stage;

  const website = yield* Cloudflare.Worker("Website", {
    main: "./dist/worker/index.js",
    bundle: false,
    isExternal: true,
    assets: {
      directory: "./dist/client",
      config: {
        notFoundHandling: "none",
        htmlHandling: "auto-trailing-slash",
        runWorkerFirst: false,
      },
    },
    env: {
      CF_TEAM_DOMAIN: process.env.CF_TEAM_DOMAIN ?? "",
      CF_AUD: process.env.CF_AUD ?? "",
      // …other runtime env…
    },
    compatibility: {
      date: "2026-03-17",
      flags: [
        "nodejs_compat",
        "nodejs_compat_populate_process_env",
        "global_fetch_strictly_public",
      ],
    },
    domain: domainsForStage(stage),
  } as Cloudflare.WorkerProps & { isExternal: boolean });

  return {
    url: website.url,
    workerName: website.workerName,
    domains: website.domains,
  };
});

export default Alchemy.Stack(
  `${PROJECT}-${SERVICE}`,
  {
    providers: Cloudflare.providers(),
    state: Cloudflare.state(),
  },
  program,
);
```

Run order:

1. `bun run build` (which is `bun run generate:*-manifest && vite build`) produces `dist/worker/index.js` + `dist/client/`.
2. `bun alchemy deploy ./alchemy.run.ts --stage <stage> --yes` uploads them.

The `as Cloudflare.WorkerProps & { isExternal: boolean }` cast is needed because `isExternal` isn't in the public TypeScript surface yet. It tells alchemy to upload the worker artifact byte-for-byte instead of wrapping it in alchemy's effect bridge — that wrapping breaks rwsdk's RSC entrypoints.

---

## Why not `Cloudflare.Vite`?

`Cloudflare.Vite` is the cleaner API in theory — it builds + uploads in one resource. In practice (alchemy 2.0.0-beta.40, the version available at time of migration):

1. The plugin internally calls `@distilled.cloud/cloudflare-vite-plugin`.
2. Your `vite.config.mts` already has `@cloudflare/vite-plugin` (needed for `bun run dev` to work standalone).
3. Two cloudflare plugins load at the same time when running under alchemy.
4. The duplicate plugin can't figure out which environment owns the worker entry.
5. Build dies with `You must supply options.input to rollup`.

Symptom in CI: `Build failed in 4ms; ERROR: Error: You must supply options.input to rollup`.

The workaround in this skill (build with vite ourselves, upload via `Cloudflare.Worker`) gives the same single-resource alchemy stack and the same `workers.dev` URL shape. Track upstream for an opt-out flag and migrate when it lands.

---

## Pin alchemy exactly

`"alchemy": "^2.0.0-beta.40"` resolves to the `pipeline-v2-test` dist-tag in CI environments where bun does a fresh install. That tag is built against an incompatible `effect.Config` API and every `bun alchemy` invocation crashes with:

```
TypeError: a.asEffect is not a function. (In 'a.asEffect()', 'a.asEffect' is undefined)
```

Pin exactly in `package.json`:

```jsonc
"alchemy": "2.0.0-beta.40"
```

No caret, no tilde. When a new beta is known-good, bump it intentionally.

---

## Stages

- `dev` — local + your laptop. `--stage dev` deploys to `*-dev-*.workers.dev`.
- `staging` — explicit `--stage staging`. Often gets custom domain too.
- `production` — explicit `--stage production`. Gets the apex domain(s).
- `pr-<N>` — provisioned by the CI preview workflow per PR. Gets a deterministic `*-pr-N-*.workers.dev` URL. No custom domain.

`Alchemy.Stage` from inside the `Effect.gen` block reads the active stage. `domainsForStage(stage)` decides whether to claim domains based on that.

---

## Required env in CI

Use the existing repo-level secrets:

- `CLOUDFLARE_API_TOKEN` — secret, set on the GH repo.
- `CLOUDFLARE_ACCOUNT_ID` — secret or variable.
- `CLOUDFLARE_WORKER_DOMAINS` — variable (comma-separated apex list), for production/staging only.
- `CF_TEAM_DOMAIN` / `CF_AUD` — secret or variable, for Cloudflare Access auth on `/internal/*`.

Validate them up-front in the workflow so failures surface fast:

```bash
test -n "$CLOUDFLARE_ACCOUNT_ID" || { echo "Missing CLOUDFLARE_ACCOUNT_ID" >&2; exit 1; }
test -n "$CLOUDFLARE_API_TOKEN" || { echo "Missing CLOUDFLARE_API_TOKEN" >&2; exit 1; }
```

---

## Bootstrap alchemy state once per repo

The first deploy in any repo needs `bun alchemy cloudflare bootstrap` to create the state-storage bucket. Idempotent — safe to run before every deploy. Already in the CI workflow templates.
