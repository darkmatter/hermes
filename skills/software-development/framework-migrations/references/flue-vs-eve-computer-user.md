# Flue vs Eve — computer-user port (2026-08-03)

Side-by-side of Studio browser/payment agent:

| Path | Runtime |
|---|---|
| `~/git/czxtm/agents/apps/computer-user` | Eve |
| `~/git/czxtm/agents-flue/apps/computer-user` | Flue 2.0.1 |
| Comparison doc | `agents-flue/COMPARISON-flue-vs-eve.md` |

## Portable core (copy freely)

- `agent/lib/cua.ts` — MCP stdio-over-SSH client, binding, sweep (no framework imports)
- skills + `vmap.py` / `vcoord.py`
- charge-gate policy text

## Authoring boundary only

| Concern | Eve | Flue |
|---|---|---|
| Agent | `defineAgent({ model })` | `'use agent'` + `useModel`/`useTool`/`useSkill` |
| Tools | path slug = name; Zod | explicit `name:`; Valibot; `{ output: JsonValue }` |
| Skills | auto-discover `agent/skills/**` | `import x from "./…/SKILL.md"; useSkill(x)` |
| HTTP | Eve harness | Hono `createAgentRouter` |
| DB | Eve worlds | `sqlite()` in `db.ts` |
| Evals | `defineEval` + Braintrust | vitest pure helpers only (no native eval runner) |
| MCP native | HTTP/SSE | HTTP/SSE — **both need hand-rolled stdio for Studio** |

## Cooper preference for this spike class

- Deliver a **real port** + written comparison, not abstract framework debate.
- Prefer Eve while evals/charge-gate gates are the product surface.
- Prefer Flue for ops-simple Node shell once the loop is proven.
- Keep CUA lib framework-free so re-shell is cheap.

## Flue-specific traps seen in the port

1. Tool `output` must be `JsonValue` — no `Record<string, unknown>`; use `JSON.parse(JSON.stringify(...))` bridge.
2. Optional `undefined` fields break JsonValue unions — return stable shapes with `null`.
3. `v.description` in valibot pipes is optional; keep schemas simple when typing fights.
4. Workspace install after adding `apps/computer-user`; typecheck/test/build per package then root.
5. Live MCP smoke can fail with Studio `browser_wrong_target_refused` (consent) — environmental, not framework.

See also: `filesystem-first-agents` → `references/eve-cua-mcp-ssh-transport.md`.
