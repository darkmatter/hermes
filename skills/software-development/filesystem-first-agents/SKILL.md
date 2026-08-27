---
name: filesystem-first-agents
description: >-
  Scaffold, migrate, and run filesystem-first durable agents (including Eve,
  Flue, and Agent Skills-shaped layouts) as a git-backed directory tree.
  Triggers for agent-as-directory setups, portable provider routing, durable
  multi-surface deployment, and cross-framework agent migrations.
---

# Filesystem-first agents (Eve, Flue + portable skills)

Build agents whose **source of truth is the directory tree in git** — markdown for identity/procedures, TypeScript for tools/runtime — not a central registry or cloud console.

Covered frameworks: **[Eve](https://eve.dev)** for workflow-centric durable agents, **Flue** for portable Node/Cloudflare durable agents, and **[Agent Skills](https://agentskills.io)** (`SKILL.md`) for reusable procedures.

## When to use

- User wants eve (or “like eve”) without lock-in
- Repo should fully represent the agent in git
- Scaffold / replace an existing clue-style agent tree
- Direct Anthropic/OpenAI providers instead of Vercel AI Gateway
- OpenAI-compatible gateways (LiteLLM / custom baseURL) e.g. `glm-5.2-fp8`
- Eve eval suites (`eve eval`, mockModel unit vs live LLM tags)
- Self-host vs `eve deploy`
- Studio browser agent (`computer-user`) — host tools + MCP stdio CUA transport
- Flue vs Eve side-by-side ports of the same agent (pair with `framework-migrations`)
- Design one Flue agent reachable from local tooling, Kubernetes, Cloudflare Workers, Slack, cron, or queue workers
- Evaluate **celld** (self-hosted Durable Objects) as a Flue host, or clarify Flue multi-target vs DO runtimes
- Compose Flue multi-agent systems: shared subagents across packages, `useSubagent` / `defineSubagent`, when not to import top-level agents, monorepo layout for `~/git/darkmatter/agents`

For Flue multi-agent topology (subagents vs registered agents vs HTTP specialists), load `references/flue-multi-agent-composition.md` before inventing package layouts or wiring `useSubagent`. It distinguishes logical-agent directories from package/deployment boundaries, covers one Worker with multiple top-level Durable Object agents, direct in-process `dispatch`, and the concrete reasons to split a Node/MCP specialist into a sibling app.

For **Flue agent composition in runnable apps** (canonical agent shape, tool exports, direct dispatch, why not to use host abstractions or `@agents/*` packages, premature shared-library consolidation into `@repo/lib`), load `references/flue-logical-agent-package-boundaries.md`. It covers the canonical direct agent shape (no `render*Host` factories, no `hosts/` directory, tools as direct `defineTool` exports), Flue's strict app-local source root, scanner rules, direct dispatch for colocated agents, persistence boundaries, premature package consolidation criteria, and the pitfalls of factory-indirection and premature extraction.

For Flue deployments, load `references/flue-portable-durability.md` before choosing storage, replication, ingress, or tool checkpoint boundaries. The key model is one durable conversation owner with many ingress surfaces—not independent authoritative copies on every surface.

For **celld.dev** / self-hosted DO fleets as a Flue host, load `references/flue-celld-self-hosted-dos.md` first. Flue multi-target means shared **agent source** with Node vs Cloudflare **host adapters** — not “any Workers runtime.” Workers AI is optional; live spike proved CF-target + single-file esbuild export + HTTP LiteLLM on celld. Also: `.flue/` is authored source (commit); `.flue-vite*` / celld-state are generated (gitignore); `flue-ref` is upstream `withastro/flue`, not a greenfield app.

For Cloudflare infrastructure managed by Alchemy, also load `references/flue-alchemy-cloudflare-infra.md`; keep Flue runtime state, Workflow checkpoints, and Alchemy deployment state as separate authorities. It covers the validated Flue 2.0.3 external-artifact shape, emitted binding/migration assertions, the cross-script Alchemy sandbox DO/container topology, and the rule that source inspection is not a live deployment proof. For the official helper harness, root/app test scripts, runner isolation, version-bound Effect compatibility, and deploy/destroy evidence standard, load `references/alchemy-integration-testing.md`. For isolated cluster execution, load `references/flue-k3s-sandboxes-auth.md`; put Kubernetes behind a trusted sandbox-controller, key durable workspaces by Flue instance id, and keep GitOps manifests generic (`flue-agent-platform`) rather than logical-agent-specific. When deciding whether the Alchemy provider itself needs new resources for private k3s, load `references/alchemy-k3s-resource-gap.md`: inspect the existing reconciler first—Argo/Flux ownership means Git is the interface and direct Alchemy Kubernetes reconciliation is normally out of scope.

## Decision criteria (Cooper preferences)

1. **Filesystem layout first** — the agent must be a readable directory contract in git.
2. **Vendor lock-in optional** — prefer direct AI SDK providers + local sandbox over Gateway/Sandbox/Workflows until explicitly wanted.
3. Eve OSS is fine when layout match matters; OpenClaw/Hermes workspaces are the nearest non-Vercel harness peers.
4. **Stop re-litigating approved boundaries** — after package granularity, deployment boundaries, and namespace are selected—or Cooper says “no more questions, just build”—encode them in tests and implement through verification. Ask again only for a genuinely new destructive or external side effect.

## Eve project layout

```text
my-agent/
├── package.json
├── tsconfig.json
├── .env.example
├── AGENTS.md                 # coding-agent pointers to eve docs
└── agent/                    # THE agent
    ├── agent.ts              # defineAgent({ model, … })
    ├── instructions.md       # always-on system prompt
    ├── tools/*.ts            # defineTool; filename = snake_case tool name
    ├── skills/<name>/SKILL.md  # or skills/<name>.md — progressive disclosure
    ├── channels/eve.ts       # HTTP; optional Slack/Discord/…
    ├── sandbox/sandbox.ts  # optional; defaultBackend() for local
    ├── connections/          # MCP / OpenAPI
    ├── subagents/<id>/
    ├── schedules/
    ├── hooks/
    ├── workspace/            # seeded into sandbox
    └── lib/
```

## Scaffold paths

### A. Official init (empty dir)

```bash
npx eve@latest init my-agent
# or into existing package.json project with no agent/ yet:
npx eve@latest init .
```

Notes:
- Does **not** create a Vercel project.
- Interactive tail often launches `eve dev`; stop with Ctrl+C after scaffold if you only wanted files.
- Target directory must be empty except `.git` / `.DS_Store` / `.gitkeep` / `.hg`.

### B. Manual scaffold (preferred when repo already has history)

Write the layout by hand (template below), then:

```bash
npm install
npx eve build
npx eve info
```

Migrate prior clue-style roots (`AGENTS.md`, `SOUL.md`, `RULES.md`, `agent.yaml`, old `skills/`) into:
- `agent/instructions.md` (identity + rules)
- `agent/skills/**/SKILL.md`
- archive originals under `_legacy-*/` in the same commit

## Models: avoid Vercel when unwanted

```ts
// agent/agent.ts — DIRECT provider (no AI Gateway)
import { anthropic } from "@ai-sdk/anthropic";
import { defineAgent } from "eve";

export default defineAgent({
  model: anthropic("claude-sonnet-4-5"),
});
```

### OpenAI-compatible gateway (LiteLLM / custom baseURL)

Cooper’s default for `czxtm/agents` is LiteLLM, **not** Anthropic direct:

```ts
import { createOpenAI } from "@ai-sdk/openai";
import { defineAgent } from "eve";

const litellm = createOpenAI({
  name: "litellm",
  apiKey: <REDACTED>
  baseURL: process.env.LITELLM_BASE_URL ?? "https://litellm.drkmttr.dev/v1",
});

export default defineAgent({
  // Chat Completions — what LiteLLM exposes at /v1/chat/completions
  model: litellm.chat(process.env.LITELLM_MODEL ?? "glm-5.2-fp8"),
  // REQUIRED for non-gateway / unknown catalog models or build fails:
  // "Cannot compile agent compaction because … does not have known AI Gateway context window metadata."
  modelContextWindowTokens: <REDACTED>
    process.env.LITELLM_CONTEXT_WINDOW_TOKENS ?? 1_000_000,
  ),
});
```

| Mode | Config | Env |
| --- | --- | --- |
| LiteLLM / OAI-compat | `createOpenAI({ baseURL, apiKey }).chat("glm-5.2-fp8")` + `modelContextWindowTokens` | `LITELLM_API_KEY` (or `OPENAI_API_KEY`); optional `LITELLM_BASE_URL`, `LITELLM_MODEL` |
| Direct Anthropic | `anthropic("claude-sonnet-4-5")` from `@ai-sdk/anthropic` | `ANTHROPIC_API_KEY` |
| Direct OpenAI | `openai("…")` / `createOpenAI().chat` | `OPENAI_API_KEY` |
| AI Gateway | string `"anthropic/claude-sonnet-5"` | `AI_GATEWAY_API_KEY` or Vercel OIDC |

Install provider packages as normal deps. Match `@ai-sdk/*` major line to the `ai` version eve pins (eve 0.27 → `ai` ^7). Prefer **`.chat(modelId)`** for LiteLLM (Completions API); default `openai(id)` / responses may not match the gateway.

Verify routing after build/start: `GET /eve/v1/info` → `agent.model.routing.kind` should be `"external"` for direct/custom providers. Manifest should show the model id (e.g. `glm-5.2-fp8`) and provider name (e.g. `litellm`).

Native Anthropic ids use hyphens (`claude-sonnet-4-5`); gateway ids use `provider/model` with dots in versions.

Key location on Cooper’s box for LiteLLM: **verify before trusting any cached path** — as of 2026-08-03 both `~/.secrets/litellm-api-key` and himitsu `litellm-api-key` were rejected (`token_not_found_in_db`); the working key was `himitsu read codex-litellm-key`. Probe any key with one small completion first:

```bash
curl -s https://litellm.drkmttr.dev/v1/chat/completions \
  -H "Authorization: Bearer <REDACTED>" -H 'Content-Type: application/json' \
  -d '{"model":"flash","messages":[{"role":"user","content":"OK"}],"max_tokens":8}'
```

Proxy model aliases include `flash` (= `google/gemini-3.6-flash`), `gemini`, `auto`, `glm-5.2-fp8`. Write the key into project `.env` as `LITELLM_API_KEY=…` via `sed` from the himitsu read (gitignored; never echo it into chat). Eve loads `.env` / `.<REDACTED>` / `.env.development*` in dev/eval automatically.

## HTTP channel + auth

Default HTTP routes exist even without authoring `channels/eve.ts`. When authoring, **`auth` is required**:

```ts
import { eveChannel } from "eve/channels/eve";
import { localDev, placeholderAuth, vercelOidc } from "eve/channels/auth";

export default eveChannel({
  auth: [vercelOidc(), localDev(), placeholderAuth()],
});
```

- `eveChannel()` with no args throws / fails eval (`uploadPolicy` on undefined).
- `localDev()` unlocks localhost for `eve dev`.
- Replace `placeholderAuth()` before production exposure.

Routes: `/eve/v1/health`, `/eve/v1/info`, `/eve/v1/session`, stream, cancel. Self-host must also proxy `/.well-known/workflow/`.

## Sandbox (local-first)

```ts
import { defaultBackend, defineSandbox } from "eve/sandbox";

export default defineSandbox({
  backend: defaultBackend(), // Docker → microsandbox → just-bash; not Vercel
});
```

Do not use `vercel()` sandbox backend unless creating hosted Vercel sandboxes on purpose.

## Skills format

- Plain: `agent/skills/forecast.md` with description frontmatter (or filename slug).
- Packaged: `agent/skills/<name>/SKILL.md` + optional `references/`, `scripts/`, `assets/`.
- Agent Skills Standard ports in as-is; eve exposes `load_skill`.
- Skills are per-agent scoped (root vs subagent); put shared executables in `lib/`.

## Local run / self-host

```bash
# Node >= 24 required by eve
export PATH="/opt/homebrew/opt/node@25/bin:/opt/homebrew/bin:$PATH"  # example on Cooper's Mac

cp .env.example .env   # provider key
npm install
npm run dev            # TUI + HMR
npm run build && npm start
curl -sf localhost:3000/eve/v1/health
```

- Persist `.eve/.workflow-data` across restarts (it IS the durability store for the default local world).
- Optional durable worlds: `experimental.workflow.world` in `agent.ts` (e.g. postgres world package matching eve’s `@workflow/*` line; vendored line is `5.0.0-beta`, incompatible worlds are rejected at init).

**Durability model** (session → turn → step): every turn is a durable workflow checkpointing at each step; crash/redeploy resumes from last completed step (interrupted step re-runs → keep non-idempotent effects approval-gated); parked waits (HITL/OAuth/subagent) hold zero compute. Full model + **Vercel dependency audit table** (what's hosted vs portable: `@vercel/otel` portable, `@vercel/connect` + AI Gateway + `world-vercel` hosted) + **Cloudflare assessment** (Workers can't run the eve runtime — Node ≥24 + filesystem + sandbox; use as edge layer only): `references/eve-durability-and-vercel-deps.md`.

## Dependency pins (eve 0.27 era)

```json
{
  "dependencies": {
    "@ai-sdk/anthropic": "^4.0.21",
    "ai": "^7.0.34",
    "eve": "^0.27.6",
    "zod": "4.4.3",
    "@vercel/connect": "0.4.2"
  },
  "engines": { "node": ">=24" }
}
```

Prefer `engines.node: ">=24"` over `"24.x"` when hosts may run Node 25/26.

## Evals / “unit tests” (`eve eval`)

Eve does **not** use Jest-style unit tests for agent behavior. First-class harness:

```bash
eve eval                       # all evals under evals/
eve eval --tag unit            # offline fixtures
eve eval --tag live            # real model
eve eval --list
eve eval --strict --junit .eve/junit.xml   # CI
```

Layout:

```text
evals/
  evals.config.ts              # required root; defineEvalConfig({}) is enough
  unit-smoke.eval.ts           # tags: ['unit']
  smoke-live.eval.ts           # tags: ['live']
```

- Identity = file path (`evals/weather/foo.eval.ts` → id `weather/foo`).
- **Default-export an array** to fan one file over a dataset: ids become `<file-id>/0000`, `/0001`, … — ideal for model-matrix evals (one row per model).
- **Eval modules are cached outside the source tree** (`.eve/dev-hosts/…/authored-modules/…`) — `import.meta.dirname` / `__dirname` resolve there, NOT in the app. Anchor runtime file paths on `process.cwd()` (eve CLI always runs from the app root), never on import.meta.
- Evals drive **real HTTP sessions** against a booted local (or `--url` remote) agent.
- Artifacts: `.eve/evals/<timestamp>/summary.json` + per-eval streams.
- Exit: `0` pass, `1` fail, `2` config.

### Braintrust reporting + model comparison (native reporter)

eve ships a first-class Braintrust reporter — no raw SDK glue needed. `evals.config.ts`:

```ts
import { Braintrust } from "eve/evals/reporters";
import { defineEvalConfig } from "eve/evals";

const reporters = process.env.BRAINTRUST_API_KEY
  ? [Braintrust({ projectName: "computer-user" })]  // optional: experimentName, baseExperimentName for diffs
  : [];

export default defineEvalConfig({ reporters, judge: { model: litellm.chat("flash") } });
```

- The reporter logs each eval as a row with `scores` (soft assertions by name, gates as `gate:<name>`), `metadata` (tool-call list, status), and `metrics` (toolCallCount, messageCount…). The experiment view IS the model comparison.
- `braintrust` is an optional peer of eve — add it to the app's own `dependencies` (`bun install` from repo root; it lands in the app's node_modules, not hoisted).
- Cross-model comparison pattern: array-exported evals varying one knob (e.g. `VCOORD_MODEL` for the vision sweep, `LITELLM_MODEL` for the driving model) + per-model `model:<id>` tags → run `eve eval --tag 'model:<id>'` per model → one experiment row each. Full worked example: `references/eve-braintrust-evals.md`.

### Offline unit path (`mockModel`)

Swap the agent model when `EVE_MOCK_MODEL=1`:

```ts
import { mockModel } from "eve/evals";
// model: process.env.EVE_MOCK_MODEL === "1" ? mockModel(responder) : liveModel()
```

`mockModel` callback gets `{ lastUserMessage, toolResults, tools, … }` and may return text or `{ toolCalls: [{ name, input }] }` for tool loops.

Recommended npm scripts:

```json
{
  "test": "eve eval",
  "test:unit": "EVE_MOCK_MODEL=1 eve eval --tag unit",
  "test:live": "eve eval --tag live",
  "test:list": "eve eval --list"
}
```

Guard mixed suites: live evals `t.skip` when `EVE_MOCK_MODEL===1`; unit evals `t.skip` when mock is off. Put fixture routing keywords carefully (e.g. don’t put `"ping"` in a smoke prompt if that triggers the mock’s tool branch).

Assertions that matter: `t.succeeded()`, `t.calledTool` / `t.notCalledTool` / `t.usedNoTools()`, `t.check(t.reply, includes(/…/))`.

Note: post-success local runs may log workflow queue `503 socket hang up` during teardown — noise if gates already passed.

## Verification checklist

1. `npx eve info` — Compile ready, 0 errors; skills/tools counts look right
2. `npx eve build` — exits 0, `.output` present
3. `npx eve start` then `curl …/eve/v1/health` → `ok: true`
4. `/eve/v1/info` model routing matches intended provider
5. `npm run test:unit` (offline) and optionally `npm run test:live` (creds)
6. Agent tree + lockfile committed; secrets only in `.env` (gitignored)

## Pitfalls

- **Runtime tool name = file slug, and eval assertions must match it exactly.** eve derives each tool's name from its filename under `agent/tools/` (`cua-sweep.ts` → `cua-sweep`); `defineTool` has no `name` field and identity is path-derived. So instructions/skill prose and `t.calledTool("…")` must use the slug verbatim — a live eval's `calledTool(cua_sweep)` gate failed while observed calls were `[cua-sweep, …]`. After wiring, run `eve info` / a live eval and read the observed tool names back rather than trusting what your docs said.
- **Non-empty in-place init** — `eve init .` refuses dirs with real files; stash/move first or scaffold manually.
- **Empty `eveChannel()`** — always pass `{ auth: […] }`.
- **Gateway vs direct model strings** — string ids hit Gateway and need gateway creds.
- **Custom / LiteLLM models need `modelContextWindowTokens`** — otherwise compaction compile fails with “no known AI Gateway context window metadata”.
- **Use `.chat()` for LiteLLM** — Completions path; don’t assume Responses API.
- **Reasoning models (GLM 5.2, etc.)** — may fill `reasoning_content` and leave `content` empty at tiny `max_tokens`; give room and assert with loose includes (`/pong/i`), not brittle exact equality.
- **vite-plus / vp npm shim** — on Cooper’s machine `~/.vite-plus/bin/npm` can reject `packageManager` fields; use Homebrew Node’s npm (`/opt/homebrew/opt/node@25/bin` ahead of vite-plus) for install/build.
- **`.ts`-extension imports need `allowImportingTsExtensions: true`** in tsconfig when tools import `../lib/x.ts` — sibling apps (ci-fixer, improvement-scout) set it; the bundled scaffold template tsconfig does NOT (→ TS1005). Add it whenever you copy the template.
- **`eve eval` refuses when a dev server is already running** ("A dev server is already running for this eve agent"). Kill the stale `eve dev` process; a `.eve/dev-server-state.v1.json` left behind by a moved/deleted app dir can keep a port squatted — free the port (`lsof -iTCP:<port> -sTCP:LISTEN`, kill) and remove the stale state file.
- **czxtm/agents is bun-based**: `bun install` at repo root auto-links new `apps/*` workspaces (no per-app install needed); run scripts with `bun run <script> -w @czxtm/<app>` or from inside the app dir.
- **Porting Hermes skills into eve** — eve frontmatter is stricter: `description` must be a plain string (required), `metadata` must be string→string only (Hermes' nested `metadata.hermes.tags/category/related_skills` object fails normalization), and `name` is silently ignored (identity is path-derived). `scripts/`, `references/`, `assets/` subdirs port as-is.
- **Don’t commit** `.eve/`, `.output/`, `node_modules/`, `.env`.
- **Preview software** — eve APIs can change; re-read `node_modules/eve/docs/` when versions bump.

## OpenClaw / Hermes peer (when eve is wrong fit)

If the goal is a personal multi-channel assistant workspace rather than a deployable agent app framework:

```text
workspace/
  AGENTS.md SOUL.md IDENTITY.md USER.md TOOLS.md
  skills/**/SKILL.md
```

Still filesystem-first and git-friendly; runtime differs. Hermes skills already follow Agent Skills packaging.

## Support files

- `references/flue-multi-agent-composition.md` — Flue subagents vs top-level agents: registration is scan not import; `defineSubagent` + explicit `useSubagent` mounts; concrete `@repo/subagents` catalog (`structuredSummarizer`, `readOnlyResearcher`, `diffRiskReviewer`) + app-local stage inventory; standing-rules in child frames; when to HTTP-dispatch sibling apps (`~/git/darkmatter/agents`)
- `references/flue-logical-agent-package-boundaries.md` — reusable `@agents/*` libraries versus runnable Flue apps; npm scope/subpath rules; strict app-local `src` scanning; thin wrappers and host contracts; persistence, dispatch receipt, asset-copy, generator, migration, and regression-test patterns
- `references/flue-portable-durability.md` — Flue accepted-work semantics, durable tools/`step.do`, Node versus Durable Object recovery, k3s ownership rules, and the one-owner/many-ingress architecture for local, Slack, workers, and clusters
- `references/flue-celld-self-hosted-dos.md` — Flue + celld: multi-target ≠ multi-host; proven single-file esbuild adapter + LiteLLM via `cloudflare:workers` env; `.flue/`=source (commit) vs `.flue-vite*`/celld-state (gitignore); flue-ref=upstream checkout; `@flue/sdk` client on localhost
- `references/flue-alchemy-cloudflare-infra.md` — division of responsibility between Flue, Alchemy, and Cloudflare; external Worker artifact deployment; Durable Object migration ownership; Workflows/Queue/R2 roles; hybrid Cloudflare/k3s boundary; required integration spike
- `references/alchemy-integration-testing.md` — official `alchemy/Test/Bun` deploy/destroy harness; app/root script forwarding; Bun-vs-Vitest suite isolation; beta.57/Effect compatibility; cross-script DO class shape; live-evidence standard
- `references/flue-k3s-sandboxes-auth.md` — custom `SandboxFactory` over a k3s sandbox-controller, durable Pod/PVC workspace leases, operation recovery/cancellation, identity chain, scoped RBAC, pod hardening, credential brokering, and the Alchemy-versus-GitOps ownership boundary
- `references/eve-direct-provider-scaffold.md` — scaffold notes, LiteLLM/`glm-5.2-fp8`, eval results for `czxtm/agents`
- `references/eve-cua-mcp-ssh-transport.md` — **canonical** Studio transport: MCP stdio over SSH (not one-shot `call`); eve/flue HTTP MCP clients cannot replace this
- `references/eve-cua-ssh-host-tools.md` — **stale** early one-shot SSH draft; prefer mcp-ssh-transport
- `references/eve-braintrust-evals.md` — Braintrust reporter wiring + the two-tier model-comparison eval design (vision-matrix + driving-readonly)
- `references/eve-durability-and-vercel-deps.md` — durability model (sessions/turns/steps, worlds), Vercel dependency audit technique + table, self-host checklist, Cloudflare assessment
- Flue sibling port: `~/git/czxtm/agents-flue/apps/computer-user` + `COMPARISON-flue-vs-eve.md`
- `templates/` — copy-paste starters for agent.ts / channel / sandbox / skill / tool

## Related

- Official docs: https://eve.dev/docs (also `node_modules/eve/docs/`)
- Self-host: `guides/deployment/self-hosting.md` in package docs
