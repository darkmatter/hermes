# eve durability model + Vercel dependency audit

Findings from auditing vendored eve (0.27 era, `vendor/eve/` in czxtm/agents) on 2026-08-03.

## Durability: session → turn → step

- **session**: the durable conversation/task; lives days/weeks, survives restarts/redeploys.
- **turn**: one user message + all work it triggers. Every turn runs as a **durable workflow** on the open-source Workflow SDK (workflow-sdk.dev).
- **step**: one model call + its tool calls. Eve checkpoints and serializes session state at **every step boundary** (`src/execution/durable-session-store.ts`; versioned `DurableSessionState`/`Snapshot` with migrators under `durable-session-migrations/`).

Crash/timeout/redeploy mid-turn → resumes from last **completed** step. Completed steps never re-run (recorded result replayed); a step interrupted **mid-execution re-runs** → keep non-idempotent side effects (charges, emails) idempotent or approval-gated.

**Parked work**: waiting on human approval / OAuth / subagent suspends the workflow holding **zero compute** until the callback arrives. Continuation token = resume handle for the current hook, NOT a message queue — no durable FIFO of user messages; send one turn at a time and wait for `session.waiting`.

## Workflow worlds (pluggable state store)

Nitro hosts HTTP routes + workflow entrypoints only — **not** state, not sandbox. State comes from a "world" package:

- `@workflow/world-local` (default off-Vercel): persists runs on disk under `.eve/.workflow-data`.
- `@workflow/world-vercel`: hosted Vercel Workflow (deploy-time routing, dashboard metadata).
- Swap via `experimental.workflow.world: "<pkg>"` in root `agent.ts` (docs example: `@workflow/world-postgres`). Package must export default factory / `createWorld()`; read creds from env vars.
- **Protocol version pinning**: vendored `@workflow/*` line is `5.0.0-beta`; the runtime rejects worlds with incompatible protocol versions. Check `pnpm-lock.yaml` for the exact `@workflow/world*` versions your eve release pins.

Sandbox is a separate adapter: `defaultBackend()` off-Vercel (docker/microsandbox), `vercel()` only on purpose.

## Vercel dependency audit (how + results)

Technique: grep every app's `package.json` for `@vercel/*`, check `pnpm-lock.yaml` for `@workflow/world-*`, look for `agent/connections/` (Connect usage) and `channels/*.ts` auth lists, and for `vercel.json`/`.vercel` deploy artifacts.

| Dependency | Hosted Vercel service? | Notes |
|---|---|---|
| `eve` → `nitro` | No | open-source, portable |
| `@vercel/otel` | No | OTel SDK wrapper; works anywhere (we point it at Braintrust) |
| `@vercel/connect` (`connect()` OAuth brokerage) | **Yes** | only where `agent/connections/*.ts` imports `@vercel/connect/eve` (ci-fixer, improvement-scout); conductor has none |
| `vercelOidc()` in channel auth | **Yes, but inert off-Vercel** | fine to leave listed alongside `localDev()`; docs say use Basic/JWT/OIDC when self-hosting |
| String model IDs (`"anthropic/..."`) | **Yes** (AI Gateway) | bypass with direct provider model objects (`createOpenAI({baseURL}).chat(id)`) |
| Vercel Sandbox / Workflow / Cron | **Yes, only on Vercel deploys** | local world + local sandbox are the defaults off-Vercel |

czxtm/agents result (2026-08-03): no `vercel.json`/`.vercel` anywhere → nothing deployed to Vercel; conductor's hard dependency on Vercel-hosted services ≈ zero.

## Self-host checklist (first-class path)

```bash
eve build
PORT=3000 eve start --host 0.0.0.0
curl https://host/eve/v1/health   # then: eve dev https://host
```

1. Workflow state: mount `.eve/.workflow-data` on persistent storage (or a postgres world).
2. Sandbox: docker / microsandbox backend.
3. Auth: replace `vercelOidc()` reliance → Basic/JWT/OIDC/custom verifier.
4. Models: direct providers (no `AI_GATEWAY_API_KEY` needed).
5. Reverse proxy must forward **both** `/eve/` and `/.well-known/workflow/` without path rewriting (missing callback prefix = sessions start but runs stall).
6. Schedules: standard `eve build && eve start` runs Nitro's schedule runner; custom HTTP-only presets must wire scheduled tasks themselves.

## Cloudflare assessment

Workers is the wrong shape for the eve **runtime**: needs Node ≥ 24, a real filesystem (world state), and process/sandbox execution — Workers provide none. A custom Durable Objects workflow world against the beta `@workflow/*` protocol would be required. Cloudflare is fine as an **edge layer** (tunnel, cron triggers hitting the self-hosted service). For durability engines, prefer a self-hosted Node service on a box Cooper controls (Mac Studio, Cilicon runner, NixOS VM).
