# Flue 2 durable-agent port notes

Condensed migration details from an Eve-to-Flue sibling implementation. Revalidate against the current Flue docs/source before reuse.

## Coherent Flue 2 surface

- Published packages used together: `@flue/runtime`, `@flue/cli`, `@flue/sdk`, and `@flue/vite` at the same version.
- Agents are capitalized exports in a `'use agent'` module.
- Root agents compose behavior with `useModel`, `useInstruction`, `useSkill`, `useTool`, `useSubagent`, and optionally `useSandbox`.
- Routes mount explicitly with `createAgentRouter(Agent)`.
- Node durability uses `sqlite('./data/flue.db')` from `@flue/runtime/node` in `db.ts`.
- Vite builds use the `flue()` plugin from `@flue/vite`; project config comes from `@flue/runtime/config`.

## Important runtime distinctions

- A subagent inherits the parent model unless the `useSubagent` definition supplies `model`. Calling `useModel` inside the delegate render is invalid.
- A harness prompt runs a scratch conversation that shares the root catalog. Stage-specific instructions must be supplied explicitly if the host uses `harness.prompt` instead of model-selected delegation.
- A durable tool should wrap replay-sensitive model stages and external effects in stable `step.do(stageId, ...)` calls.
- Tool handlers receive parsed input as `context.data` in Flue 2. Return structured output as `{ output: ... }`; add an output schema when TypeScript cannot prove a custom interface is JSON-safe.
- **`JsonValue` is strict.** `Record<string, unknown>` and optional `undefined` fields fail `defineTool` typing. Bridge MCP/unknown payloads with `JSON.parse(JSON.stringify(x)) as JsonValue` and prefer `null` over omitted optionals.
- **Native MCP is HTTP/SSE only** (`McpTransport = 'streamable-http' | 'sse'`). Studio `cua-driver mcp` is stdio — hand-roll the client in framework-free `agent/lib` (same constraint as Eve). Do not pretend `defineMcpConnection` covers Studio.
- Keep portable CUA/domain code free of `@flue/*` imports so the same lib serves eve and flue shells.

## Provider migration

Flue 2 uses Pi providers, registered via `setProvider(createProvider(...))`. Do not carry forward older `defineAgent`, `registerProvider`, or AI-SDK `createOpenAI` patterns. Custom OpenAI-compatible endpoints declare complete model metadata and use Pi's OpenAI-completions API adapter. Register at module top level; remember that `flue run` loads the agent module rather than `app.ts`.

## Dispatch transport

Use `createFlueClient` from `@flue/sdk` for remote agent admission. `send()` posts a user message shaped like `{ kind: 'user', body: string }` and returns an admission receipt containing `streamUrl`, `offset`, `submissionId`, `uid`, and optional `deduplicated`. Do not hand-author an obsolete `{ message: ... }` envelope.

Same client works against a **celld**-hosted CF-target Worker (e.g. `http://127.0.0.1:8799/agents/hello/<id>`) once the spike adapter is deployed — see `filesystem-first-agents` → `references/flue-celld-self-hosted-dos.md`.

Inject `fetch` in tests and assert both the exact request body and receipt reduction. Bound/redact error bodies before surfacing remote failures.

## celld host (not a third Flue target)

Flue CF-target agents can run on celld with a **single-file esbuild export** (not stock multi-chunk Vite output). Do not treat celld as Node host. Prefer HTTP providers + `env` from `cloudflare:workers` for keys. Full adapter + gitignore (`.flue/` source vs `.flue-vite*` generated): `filesystem-first-agents` → `references/flue-celld-self-hosted-dos.md`.

## Verification traps

- Registry availability and a local framework checkout can disagree; resolve the package version before scaffolding.
- Builds do not necessarily render every agent/delegate, so add a startup/render probe for hook restrictions.
- Workspace `bun run --filter '*' test` fails when any package's `bun test` finds no tests. Give shared packages a small contract test or remove their test script.
- Parallel workers must not edit shared manifests or run installs concurrently; otherwise a correct version pin can be overwritten and transient Vite/package selection can appear nondeterministic.
