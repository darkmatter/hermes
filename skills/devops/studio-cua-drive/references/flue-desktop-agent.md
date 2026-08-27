# Flue `@agents/desktop` (productized Studio CUA)

The Studio MCP-over-SSH loop this skill operates by hand is also packaged as a Flue v2 agent in `~/git/darkmatter/agents`:

| Piece | Path | Role |
|---|---|---|
| Logical agent | `agents/desktop` | `DesktopAgent` (`defineAgent`), identity `desktop` |
| Tools | `agents/desktop/src/tools/cua-*.ts` | `cua_sweep` / `cua_vmap` / `cua_click` / `cua_type` / `cua_navigate` |
| Transport | `agents/desktop/src/lib/cua.ts` | `McpStudioClient`: `ssh … cua-driver mcp` JSON-RPC |
| Node app | `apps/desktop` | Hono `/health` + `/agents/desktop`, `smoke:mcp` |
| Skills | `agents/desktop/src/skills/` | `studio-browser-drive`, `payment-operations` |

“Computer User” is leftover naming (package description, `node-tools.ts`, one platform test). Runtime identity is `desktop`.

## Safety that is still prompt-only

Verify these in code before treating the agent as an unattended payment bot:

- **Charge click:** `cua_click` has no Pay/Subscribe allowlist. The stop lives only in `agent.ts` identity + `payment-operations/SKILL.md`.
- **HTTP auth:** `apps/desktop/src/app.ts` mounts `createAgentRouter` with no `PLATFORM_AUTH_TOKEN` gate (platform has one).
- **PAN in logs:** `slimRefs` returns field `value`s; a post-type sweep can put card numbers into the conversation / Braintrust.
- **Path writes:** `session` and `screenshot_out` are unsanitized (`/tmp/flue-cua-${session}.png`, `binding-${session}.json`).
- **Navigate schemes:** `v.url()` accepts `file://` / `javascript:`.

## Wrong seam: general sandbox

Do **not** inject Flue `local()` (or an unconstrained SSH sandbox) onto `DesktopAgent` so it can run `himitsu` / `op`. That turns a browser agent into a host shell. Secret retrieval belongs in allowlisted tools, not `useSandbox(local({ cwd: process.cwd() }))`.

If adding `@repo/sandbox` `ssh()`: export it as `@repo/sandbox/ssh` (do not re-export from the package root — that pulls `ssh2` into CF-safe imports), set `hostVerifier` (ssh2 defaults to no host-key check), and add the `SANDBOX_MODE` / `SSH_*` keys to `@repo/env` before reading them.

## Review / compare notes

- Source of latest desktop agent: `~/git/darkmatter/agents` (`agents/desktop`, `apps/desktop`).
- Personal fork `~/git/czxtm/agents` has historically matched committed desktop sources; overlay work (sandbox + Postgres) is additive and must typecheck against `@repo/env`.
- Composition tests that only `toContain` strings do not cover charge refusal, auth, or path sanitization.
- Offline unit tests live in `agents/desktop/test/{helpers,cua-act}.test.ts`; live transport is `bun run --filter @repo/desktop-app smoke:mcp`.
