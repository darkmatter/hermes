# Flue + celld: self-hosted Durable Objects

Use when evaluating **celld.dev** (Deno Land self-hosted Workers/DO runtime) as a host for **Flue** Cloudflare-target agents, or when Cooper asks whether Flue “multi-target” means any DO host.

Local Flue tree: `~/git/czxtm/flue-ref` — **upstream checkout of `withastro/flue`** (detached `@v2.0.1`), **not** a greenfield repo we authored.
**Working spike (2026-08-07):** `~/git/czxtm/flue-ref/examples/celld-spike` (only this example is ours).
Cooper Flue apps live separately at `~/git/czxtm/agents-flue`.
celld: https://celld.dev · https://github.com/denoland/celld

## Roles (do not conflate)

| Layer | Owns |
| --- | --- |
| **Flue** | Agent authoring, conversation durability semantics, Node vs CF host adapters |
| **celld** | Self-hosted fleet that runs **Workers + Durable Objects** with per-cell SQLite replicated to **your** S3-compatible bucket |
| **Workers AI / R2 / Worker Loader / CF Containers** | Cloudflare **platform** services — optional Flue features, not the Flue durability core |

**Verdict (updated after live spike):** Strong architectural fit. **Not stock drop-in**, but a thin build adapter makes Flue CF-target agents run on celld with HTTP providers. Proven: ping, 202 admit, completed LiteLLM turn, conversation survival across celld kill/restart, in-flight submission recovery.

## Abstraction boundary (common mistake)

Flue is multi-target at the **authoring** layer:

- `'use agent'`, hooks, tools/skills, conversations/submissions, `app.ts`, `@flue/sdk`

Flue is **not** “one runtime backend, many hosts.” First-class hosts today:

| Target | Process | Persistence | Wake / recovery | Build |
| --- | --- | --- | --- | --- |
| **Node** | `node dist/server.mjs` | `db.ts` (SQLite/Postgres/…) | Node coordinator (`setInterval`, leases) | Vite → server bundle |
| **Cloudflare** | workerd Worker + DOs | **DO SQLite** (`storage.sql`) | **`agents` SDK** + **alarms** / fibers | Vite + `@cloudflare/vite-plugin` + virtual `main` |

**celld is not a third Flue target.** It is a host for **CF-shaped** Worker/DO bundles. The Node target does **not** map onto celld.

```
[ shared agent source ]
        │
   ┌────┴────┐
 Node host   CF host  ← only these two are first-class in Flue
             │
             └── celld runs CF-shaped output via single-file export adapter
```

## Workers AI is only a provider

On the Cloudflare target, Workers AI is **optional** model plumbing:

- Generated entry may install `cloudflareBindingProvider({ binding: env.AI })` when `providers` is omitted or includes `'cloudflare'`.
- Prefer HTTP providers: `providers: []` + `setProvider(createProvider(...))` in the agent module, or `providers: ['anthropic']`.
- LiteLLM works as OpenAI-compatible (`openAICompletionsApi`, `baseUrl: https://litellm.drkmttr.dev/v1`).
- Missing Workers AI on celld is **not** a blocker if you never use the binding.
- Strip `ai` / `r2_buckets` / `worker_loaders` from wrangler so `celld deploy` does not reject unknown keys.

Same class of optional CF platform (avoid on celld profile): R2 skill hydration, Worker Loader / cf-shell, `@cloudflare/sandbox`, Workers Traces, Cron/Queues.

## What has to work on celld

### Hard path (proven on spike)

1. **DO SQLite** — `new_sqlite_classes: ["FlueHelloAgent"]`, binding `FLUE_HELLO_AGENT`.
2. **Alarms + Agents SDK (`agents@0.20`)** — Flue subclasses `Agent`; schedule/fiber path ran through admit → model → settle on celld 0.1.0.
3. **Module Worker + `cloudflare:workers`** — `import { env } from 'cloudflare:workers'` for wrangler `vars` / `CELLD_VAR_*` keys (do **not** rely only on `process.env` inside the Worker).
4. **HTTP model provider** — outbound fetch to LiteLLM succeeded from the cell.

### Packaging (required adapter — not stock Vite tree)

Flue/Vite emits multi-chunk Worker (`dist/flue_*/index.js` + `assets/*`). celld’s `celld deploy` runs its **own** esbuild and fails on:

- split chunks / relative `./assets/…` without a single entry,
- bare Node builtins like `from "path"` (must be `node:path`).

**Working export (see `examples/celld-spike/scripts/rebuild-deploy.sh`):**

```bash
pnpm build   # vite + @cloudflare/vite-plugin → dist/flue_*/index.js

esbuild dist/flue_*/index.js \
  --bundle --format=esm --platform=neutral \
  --conditions=workerd,worker,browser \
  --main-fields=browser,module,main \
  --outfile=celld-out-single/index.js \
  --external:cloudflare:workers --external:cloudflare:* --external:node:* \
  --alias:path=node:path --alias:fs=node:fs --alias:os=node:os \
  # …same for crypto,stream,util,buffer,events,url,string_decoder,tty,async_hooks,diagnostics_channel

# rewrite any remaining bare builtins to node:*
# wrangler.jsonc: name, main, compatibility_date/flags, durable_objects, migrations, vars only
celld deploy ./celld-out-single --bucket s3://… --endpoint … --region …
```

celld accepted wrangler keys used in spike: `name`, `main`, `compatibility_date`, `compatibility_flags`, `durable_objects`, `migrations`, `vars`. Empty `services: []` was fine. Unknown CF keys must be stripped from the **merged** dist wrangler (vite emits many empty arrays).

### Ops gotchas discovered on spike

- **Deploy ≠ live:** “Nodes load a deployment at startup; restart them to serve this version.” Always restart celld after `celld deploy`.
- **Port 8788** on Cooper’s Mac is often `ask_cooper_server.py` — use **8799** (or another free port) for local celld.
- Local object store: MinIO at `:6498`, default `minioadmin`/`minioadmin`; bucket e.g. `s3://celld-flue-spike`.
- Inject keys via wrangler `vars` **and** `CELLD_VAR_LITELLM_API_KEY` / `CELLD_VAR_OPENAI_API_KEY` at node start; agent reads `env` from `cloudflare:workers`.
- Bundle size ~2.9 MiB raw / ~588 KiB gzip for minimal hello — fine for spike, watch cold-start later.
- Put spike **inside** `flue-ref/examples/*` (workspace `workspace:*` deps). A sibling package with `file:../flue-ref/packages/*` fails because `@flue/vite` still resolves `@flue/runtime@workspace:*`.

## Spike evidence (2026-08-07)

| Check | Result |
| --- | --- |
| `GET /api/ping` | `{"pong":true}` |
| `POST /agents/hello/:id` | `202` + `submissionId` |
| Model turn (LiteLLM `flash`) | `settlements[].outcome=completed` — e.g. “Hello, great to see you!” / “ok” / “verified” |
| Kill celld + restart | Prior completed conversation still present |
| In-flight after kill | Recovered and settled on new node |

Reproduce:

```bash
cd ~/git/czxtm/flue-ref/examples/celld-spike
bash ./scripts/rebuild-deploy.sh
# start node on free port (see README.md)
```

## Decision guide

| Goal | Choice |
| --- | --- |
| Flue working soon, zero adapter | Cloudflare Workers or Node (supported) |
| Self-host density + own bucket | Flue **CF-shaped** + `rebuild-deploy.sh`-style adapter → celld |
| “Just run Node Flue on celld” | **No** — wrong substrate |
| Only need cheaper models | Swap providers; stay on CF or Node |

## Layout: `.flue/` vs generated (do not confuse)

| Path | What it is | Git |
| --- | --- | --- |
| **`.flue/`** | Optional **authored source root** (same class as `src/`). Priority: `.flue/` → `src/` → project root. Upstream flue-ref ships real agents here (e.g. `pr-redirect`). | **Commit** |
| **`src/`** | Canonical source root for new apps / our celld spike | **Commit** |
| **`.flue-vite/`**, **`.flue-vite.wrangler.jsonc`** | Vite/CF plugin **generated** merge inputs | **gitignore** |
| **`dist/`**, **`.wrangler/`**, **`celld-out*`**, **`.celld-state*`** | Build + local celld SQLite/replication | **gitignore** |
| **`.env`**, admit/read body dumps | Secrets / runtime noise | **gitignore** |

**Never gitignore `.flue/` just because it is dot-prefixed.** Ignoring it drops real agent source when a project uses the `.flue/` layout.

Spike apps should **not** create a sibling package outside the monorepo with `file:../flue-ref/packages/*` — put examples under `flue-ref/examples/*` so `workspace:*` resolves.

## Client → running celld

celld spike listens **localhost-only** (e.g. `127.0.0.1:8799`; avoid 8788 if `ask_cooper` owns it). Same Flue HTTP surface as CF/Node:

```bash
curl -s http://127.0.0.1:8799/api/ping
curl -s -X POST http://127.0.0.1:8799/agents/hello/my-chat \
  -H 'content-type: application/json' \
  -d '{"kind":"user","body":"Say hi"}'
curl -s http://127.0.0.1:8799/agents/hello/my-chat
```

```ts
import { createFlueClient } from '@flue/sdk';
const client = createFlueClient({
  url: 'http://127.0.0.1:8799/agents/hello/my-chat',
});
// React: useFlueAgent({ url: '…/agents/hello/my-chat', live: 'sse' })
```

No auth on the spike. Not LAN-reachable until rebind + TLS/ingress.

## Related local refs

- Spike app: `~/git/czxtm/flue-ref/examples/celld-spike/README.md`
- `references/flue-portable-durability.md` — one durable owner, many ingresses
- `references/flue-alchemy-cloudflare-infra.md` — Alchemy vs Flue vs CF (CF path, not celld)
- `framework-migrations` → `references/flue-2-port.md` for authoring/surface traps
