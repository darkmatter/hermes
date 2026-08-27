# Flue multi-agent composition

How to share specialists across Flue apps without confusing **subagents**, **registered top-level agents**, and **HTTP-dispatched sibling apps**. Grounded in Flue v2 docs (`useSubagent` / `defineSubagent`) and the darkmatter monorepo (`~/git/darkmatter/agents`).

## Three different things

| Kind | Addressable? | Own conversation / durable instance? | How the parent reaches it |
| --- | --- | --- | --- |
| **Top-level agent** | Yes (`dispatch` / HTTP route / DO identity) | Yes | Scan registration + `app.route` / client URL |
| **Subagent (delegate)** | No | No — detached child session under parent | Parent mounts with `useSubagent`; model calls built-in `task` |
| **Sibling deployable app** | Yes, on its own process/URL | Yes, on that app | HTTP client / custom dispatch tool (not `useSubagent`) |

Do not collapse these. Importing a function is not the same as registering an agent or mounting a delegate.

## Registration is scan, not import

- Agent modules start with `'use agent'` / `"use agent"`.
- Build scans the **app source root** (override via `agents` glob in `flue.config.ts`).
- Every **exported capitalized** function in a marked module becomes a registered agent (durable identity = function name or `agentName` static).
- Scan **excludes** `node_modules/**` and `dist/**`.
- **Importing** an agent from another package does **not** register it in the importing app.

## Subagents: any agent *function*, not free import-as-child

`useSubagent` takes a **definition**, not a bare agent:

```ts
{
  name: string;           // catalog id for parent's `task` tool
  description: string;    // when the parent model should pick it
  agent: AgentFunction;   // plain function; rendered in a child frame
  model?: string;
  thinkingLevel?: ThinkingLevel;
}
```

- `defineSubagent(...)` is only validate-at-load + freeze for sharing. Not a second agent type.
- You **do** need an explicit mount (name + description + agent). The parent’s roster is intentional, not ambient.
- You **do not** need a special subclass of agent function — but root agents are usually the wrong body to reuse as-is.

### Child-frame restrictions (why bare top-level agents fail as subagents)

In a delegate render, these throw or are disallowed:

- `useModel` — model comes from definition / parent
- `usePersistentState`, `useSandbox` — owned by parent instance; child shares env
- Client-facing hooks (`useDataWriter`, dispatch/event hooks, etc.)

A typical top-level agent calls `useModel` (and often sandbox/state). Mounting that export as `agent:` is the wrong shape. Share an **inner** plain function or a `defineSubagent` module instead.

Delegates inherit parent **environment** (sandbox tools, workspace context, model unless overridden). They inherit **nothing** of the parent conversation (history, instructions, tools, skills, subagents, persistent state).

**Standing rules:** because subagents do not inherit parent instructions, every shared delegate body must call `useStandingRules()` (or equivalent `useInstruction(ALCHEMY_NO_STATE_STORE_VERSION_OVERRIDE)`). The package helper lives at `@repo/subagents/helpers`.

## Package boundaries are not deployment boundaries

Flue’s multi-agent project layout means **one app/source root may register several top-level agents**. Reusable implementation may live in separate workspace packages, but package imports alone are not registration. Keep a thin scanner-visible wrapper under the runnable app’s own source root for every registered top-level agent.

A cosmetic move such as several app-shaped package roots under `src/agents/` still produces independent builds. The reusable-package/shared-runtime form is:

```text
packages/agents/
  conductor/                       # @agents/conductor; behavior, tools, skills
  ci-fixer/                        # @agents/ci-fixer
  improvement-scout/               # @agents/improvement-scout
  computer-user/                   # @agents/computer-user; reusable Node behavior
apps/flue-agent-platform/          # one package, one Vite build, one Worker
  package.json
  flue.config.ts
  vite.config.ts
  src/                             # this app's strict Flue source root
    app.ts
    cloudflare.ts
    hosts/
    agents/
      conductor/agent.ts           # thin registered wrapper
      ci-fixer/agent.ts
      improvement-scout/agent.ts
apps/computer-user/                # separate Node/MCP/security boundary
  src/
    app.ts
    db.ts
    agents/computer-user.ts        # thin registered wrapper
packages/subagents/                # cross-agent defineSubagent catalog
packages/{models,sandbox,utils,...}/
```

With the Cloudflare target, the one Worker still gets a distinct generated Durable Object class and binding per top-level agent. Colocation changes release/runtime boundaries; it does **not** merge durable identities or conversations. See `flue-logical-agent-package-boundaries.md` for package naming, host injection, scanner, asset, and migration details.

### When top-level agents should share one app

Default to one app when agents can share:

- runtime target and compatibility flags;
- deployment/release cadence;
- scaling and security boundary;
- provider/secrets surface;
- observability and routing ownership.

Split to a sibling app only for a concrete boundary: incompatible Node/Worker dependencies, independent scaling/SLA, separate trust or tenant boundary, separate release lifecycle, or an external surface that must fail/deploy independently. A schedule by itself is not sufficient: one Cloudflare Worker can own several cron triggers and route its `scheduled` handler to different top-level agents with `dispatch(...)`.

`computer-user` is a good separate-app example because MCP-over-SSH/CUA is Node-specific and security-sensitive. CI Fixer and Improvement Scout can share a Cloudflare app while retaining separate agent identities. A future coding agent may own a reusable `@agents/*` package plus a thin wrapper under the shared app’s `src/agents/`; promote it to another runnable app only when one of the split criteria applies.

### Direct dispatch inside a shared app

Use Flue’s in-process `dispatch(TargetAgent, request)` rather than HTTP when both registered agents are in one build. This preserves the target agent’s independent durable instance and removes a network hop. Do not call one agent function from another agent body; that is re-entrant rendering, not dispatch.

For Flue 2.0.3, the in-process `DispatchReceipt` is JSON-safe only after projecting these actual fields:

```ts
{
  submissionId: string;
  acceptedAt: string;
  uid: string;
  deduplicated?: true;
}
```

Do not copy HTTP SDK receipt fields such as `streamUrl` or `offset` into an in-process dispatch tool without checking the installed type.

## Recommended monorepo layout

```text
packages/subagents/                 # @repo/subagents — shared defineSubagent catalog
  src/
    structured-summarizer.ts
    read-only-researcher.ts
    diff-risk-reviewer.ts
    helpers.ts                      # useStandingRules / withStandingRules
    index.ts                        # named exports + sharedSubagents (docs/tests only)
apps/flue-agent-platform/src/agents/
  ci-fixer/                         # top-level root + app-local scan/claim/fix delegates
  improvement-scout/                # top-level root + app-local scan/recommend delegates
  conductor/                        # direct dispatch to colocated roots
apps/computer-user/                 # independent Node/MCP app
```

### Concrete package: `@repo/subagents` (as of 2026-08)

| Export | `task` name | When to mount |
| --- | --- | --- |
| `structuredSummarizer` | `structured_summarizer` | Parent has raw evidence; needs compact task result |
| `readOnlyResearcher` | `read_only_researcher` | Parallel sandbox investigation; no mutations |
| `diffRiskReviewer` | `diff_risk_reviewer` | Pre-mutation review of a proposed diff/plan |
| `useStandingRules` / `withStandingRules` | n/a | Inside every shared (and preferred local) delegate body |
| `sharedSubagents` | n/a | Catalog for docs/tests — **do not** mount wholesale |

Paths: `@repo/subagents`, `@repo/subagents/structured-summarizer`, `.../read-only-researcher`, `.../diff-risk-reviewer`, `.../helpers`.

### Inventory decision (what stays app-local)

| Candidate | Location | Why |
| --- | --- | --- |
| structured_summarizer / read_only_researcher / diff_risk_reviewer | **@repo/subagents** | Cross-agent, child-frame-safe |
| ci-fixer scan / claim / fix | **@agents/ci-fixer** when the logical agent has its own reusable package; otherwise app-local until a package boundary is justified | CI ledger, exact SHA, failure/claim/result blocks stay owned with CI Fixer |
| improvement-scout scan / recommend | **@agents/improvement-scout** when package-backed; otherwise app-local | Linear labels + recommendation fence stay owned with Improvement Scout; keep them `defineSubagent`, not extra top-level roots |
| conductor / CI Fixer / Improvement Scout | **behavior packages plus thin top-level wrappers in one Cloudflare app** when runtime/security/release boundaries align | Distinct DO identities with direct durable `dispatch(...)` |
| computer-user and other Node/MCP specialists | **reusable behavior package plus sibling runnable app** | Incompatible runtime and trust boundary; dispatch over HTTP/service binding |

Promote an app-local stage into `@repo/subagents` only on a **second parent** needing the same contract. Promote a top-level agent to a sibling app only for an actual operational boundary, not merely because it has its own name or schedule.

### Policy

1. **Library = menu; mounts = capability set.** Export many delegates from `packages/*`; each parent opts in with explicit `useSubagent(...)` calls. Never auto-mount an entire package into every agent.
2. **Promote on second consumer.** First use: colocate under the app (`agent/stages.ts` or local module). Second parent: move to `packages/subagents`.
3. **Shared packages export definitions or lower-case render functions, not registered roots.** A logical-agent package may export `renderCiFixer(host)`, tools, skills, and `defineSubagent` stages. Keep `"use agent"`, the exported PascalCase root, and literal `agentName` in the app-local scanner wrapper.
4. **Local stages still use `defineSubagent`.** Even app-only stages should be frozen definitions mounted with `useSubagent(ciScan)` rather than inline `{ name, description, agent: Fn }` objects — keeps mounts one-liners and matches Flue’s share pattern.
5. **Per-mount overrides:** `useSubagent({ ...diffRiskReviewer, model: 'litellm/flash' })`.
6. **Optional presets** (still explicit):

   ```ts
   export const supportDelegates = [structuredSummarizer, readOnlyResearcher] as const;
   for (const d of supportDelegates) useSubagent(d);
   ```

7. **Choose the deployment boundary independently.** A top-level agent with its own DO identity may still share one Worker/package. Use a sibling app only for incompatible runtime, security/tenant isolation, independent scaling/SLA, or independent release ownership. Multiple cron schedules can share one Worker and route through its `scheduled` handler.
8. **Keep scan output intentional.** Every exported capitalized function in a scanned `'use agent'` module becomes a registered root. Stage functions such as `ScanAgent` or `RecommendAgent` must instead be plain `defineSubagent` definitions when they are not independently addressable products.

### Mount example

```ts
"use agent";
import { diffRiskReviewer, readOnlyResearcher } from "@repo/subagents";
import { useModel, useSubagent, useTool } from "@flue/runtime";
import { ciScan, ciClaim, ciFix } from "./stages.ts";

export function CiFixer() {
  useModel(`litellm/${config.LITELLM_MODEL}`);
  useSubagent(ciScan);
  useSubagent(ciClaim);
  useSubagent(ciFix);
  useSubagent(readOnlyResearcher); // shared, optional
  useSubagent(diffRiskReviewer);
  useTool(runCiFixerTool);
  return "…";
}
```

Prefer the pipeline tool (`run_ci_fixer` / `run_improvement_scout`) for the main workflow; shared `task` delegates are for ad-hoc parallel work outside that tool.

## darkmatter/agents conventions (Flue v2)

- Bun monorepo: reusable logical agents in `packages/agents/*` as `@agents/*`; broader shared libraries in `packages/*` as `@repo/*`; runnable deployments in `apps/*`. Choose an explicit app such as `apps/flue-agent-platform` for a shared runtime rather than keeping app-shaped packages under `src/agents/*`.
- Thin app entrypoints; domain logic in framework-independent modules with direct tests.
- Agent modules: `"use agent"` + `useModel` / `useInstruction` / `useSkill` / `useTool` / `useSandbox` / `useSubagent`.
- Tools: `defineTool` + Valibot. Skills: `SKILL.md` with YAML `name` + `description`.
- Subagents do **not** inherit root instructions — use `@repo/subagents/helpers` or `@repo/standing-rules` at every authoring boundary.
- Shared delegates: `@repo/subagents`. Colocated top-level agents: direct `dispatch`. Cross-app specialists: HTTP/service-binding dispatch, not `useSubagent`.
- Local Flue ref for docs/source: `~/git/czxtm/flue-ref` (esp. `apps/docs/.../guide/subagents.md`, `packages/vite/src/agent-scan.ts`).
- Package checks: targeted `typecheck`, `test`, and a real Cloudflare `vite build`; inspect the emitted Worker config rather than trusting the authored layout.

## Anti-patterns

- Expecting `import { OtherAppAgent } from '@repo/other'` to register or subagent-mount automatically.
- Mistaking `src/agents/<name>/package.json` for Flue’s multi-agent layout; it is still package-per-agent unless one app/source root scans the agent modules.
- Making every logical agent an independently runnable app or Worker without an independent runtime/scale/security/release reason. A reusable library package per logical agent is compatible with one shared deployment.
- Mounting every shared subagent on every parent “for flexibility” (pollutes `task` roster + context).
- Putting deployable specialists only in a subagents package with no durable address when they need independent identity.
- Calling one agent function from another agent body (re-entrant render throws). Compose via hooks, `useSubagent`, in-process `dispatch`, or HTTP/service bindings.
- Leaving stage helpers as exported capitalized functions in scanned `'use agent'` modules; that silently creates extra registered agents/DO classes.
- Shared package with `"use agent"` + exported roots (scan/registration confusion).
- Forgetting standing rules inside subagent bodies (no inheritance).

## Quick decision

| Need | Put it | Wire with |
| --- | --- | --- |
| Reusable in-process specialist (2+ parents) | `packages/subagents` + `defineSubagent` | Parent `useSubagent(...)` |
| One-parent-only delegate | App-local stage module + `defineSubagent` | `useSubagent` |
| Shared tools / standing rules / skills text | `packages/*` | `useTool` / `useInstruction` / `useSkill` |
| Distinct durable agent, same runtime/security/release boundary | Reusable logical package when desired + same app’s thin `src/agents/<name>` wrapper | `app.route` + direct `dispatch` |
| Incompatible runtime, independent SLA/scale/security/release | Reusable logical package + sibling app workspace | HTTP / service binding / client dispatch tool |
