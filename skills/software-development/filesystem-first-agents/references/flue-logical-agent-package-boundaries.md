# Flue agent composition in runnable apps

Use this when a Flue monorepo needs multiple durable agents composed into one or more runnable applications.

## Core principle: agents live in apps, not packages

A Flue agent is a **scanner-visible function** in a runnable app's `src/agents/` tree. The canonical shape is direct:

```ts
"use agent";

import { useModel, useSandbox, useSubagent, useTool, useInstruction, type AgentProps } from "@flue/runtime";
import { cloudflareSandbox } from "@flue/runtime/cloudflare";
import { modelSpecifier } from "@repo/lib/models";

import { myPipelineTool } from "./tools/my-pipeline.ts";
import { myReportTool } from "./tools/my-report.ts";
import { scanStage } from "./stages/scan.ts";
import { platformEnvironment, workerModel } from "../../platform-environment.ts";
import { createSandboxKey } from "../../sandbox-key.ts";

export function MyAgent({ id }: AgentProps) {
  const namespace = platformEnvironment.Sandbox;
  if (!namespace) throw new Error("MyAgent requires the Alchemy Sandbox binding");
  const sandboxId = namespace.idFromName(createSandboxKey("my-agent", id));

  useModel(modelSpecifier(workerModel()));
  useSandbox(cloudflareSandbox(namespace.get(sandboxId), { cwd: "/workspace" }));
  useInstruction(ALCHEMY_NO_STATE_STORE_VERSION_OVERRIDE);
  useSubagent(scanStage);
  useTool(myPipelineTool);
  useTool(myReportTool);

  return "You are my-agent. ...";
}

MyAgent.agentName = "my-agent";
```

### What is NOT canonical (rejected host abstraction)

The following patterns were explicitly rejected by the user as making agents "look un-canonical":

- ~~`renderMyAgent(host: MyAgentHost): string`~~ factory functions
- ~~`interface MyAgentHost { model: string; sandbox: ...; adapters?: ... }`~~ host interfaces
- ~~`createMyAgentHost(instanceId): MyAgentHost`~~ host factories in a `hosts/` directory
- ~~`createMyPipelineTool(host.resolveThing)`~~ tool factory functions that take host capabilities
- ~~`MyAgentHostAdapters`~~ adapter contract interfaces

The user's reasoning: the trade-off (reuse across deployment targets) is not worth the indirection cost when each agent has exactly one deployment target. The agents look un-canonical and the abstraction does not save meaningful effort.

### Tools are direct exports, not factories

```ts
// CORRECT — direct export
export const myPipelineTool = defineTool({
  name: "my_pipeline",
  description: "...",
  input: v.object({ ... }),
  harness: true,
  durable: true,
  async run({ data, harness, step }) {
    const result = await runPipeline({
      ...data,
      env: scheduleEnvironment(),  // call platform helpers directly
    });
    return { output: result };
  },
});

// WRONG — factory indirection
export function createMyPipelineTool(resolveThing: ResolveThing) {
  return defineTool({ ... });
}
```

The tool calls `scheduleEnvironment()` or `workerGithubToken()` directly because it lives in the platform app. No injected adapter object that is always `{}` anyway.

## Layout

```text
apps/
  flue-agent-platform/
    src/
      app.ts                        # Hono router mounting all agents
      cloudflare.ts                 # Cloudflare scheduled-event handler
      platform-environment.ts        # env, model, sandbox, schedule helpers
      sandbox-key.ts
      schedules.ts                  # cron classification
      agents/
        conductor/
          agent.ts                  # "use agent" — the canonical agent
          tools/
            ping.ts
            dispatch-specialist.ts
          lib/
            contract.ts
            dispatch.ts             # HTTP dispatch (remote specialists)
            dispatch-local.ts       # in-process dispatch (colocated agents)
            local-dispatch.ts
          skills/
            conductor-dispatch/SKILL.md
        ci-fixer/
          agent.ts
          tools/
            run-ci-fixer.ts
            post-report.ts
          lib/
            config.ts, constants.ts, github.ts, ...
          stages.ts
          schedules/poll.ts
        improvement-scout/
          agent.ts
          tools/
            run-improvement-scout.ts
            post-report.ts
          lib/
            config.ts, constants.ts, run-pipeline.ts, ...
          stages/
            scan.ts, recommend.ts
          schedules/weekly.ts
  computer-user/
    src/
      app.ts
      db.ts
      agents/
        computer-user.ts            # "use agent" — canonical agent
        computer-user/
          tools/                    # cua-click, cua-sweep, cua-vmap, ...
          lib/                      # cua.ts, json.ts
          skills/                   # studio-browser-drive, payment-operations
          skills.ts
```

There is no `packages/agents/` directory. Agent behavior lives directly in the app that deploys it. Framework-neutral pipeline logic (parsing, config resolution, dedup, extraction) has direct tests and lives under `lib/` within the agent's directory.

## Why no `@agents/*` packages

The user tried separating reusable `@agents/*` packages from runnable `apps/*` and found:

1. The host abstraction needed to make packages reusable made agents look un-canonical.
2. Each agent has exactly one deployment target — there is no second consumer to justify the package boundary.
3. The indirection cost (interfaces, factories, adapter contracts, test mock harnesses) exceeds the reuse savings.
4. Tools that call platform helpers directly (`scheduleEnvironment()`, `workerGithubToken()`) are simpler than tools that accept injected host capabilities.

When a second deployment target genuinely appears for an agent, extract the framework-neutral pipeline logic into a package at that point — not preemptively.

## Flue source-root and scanner rules

Flue resolves one source root from the runnable project/config root. The `agents` glob is resolved under that source root:

```ts
// flue.config.ts
export default defineFlueConfig({
  target: "cloudflare",
  app: "./src/app.ts",
  // agents glob is relative to the source root, not the project root
});
```

Registration is scanner-driven, not import-driven:

- The wrapper module carries `"use agent"`;
- The exported capitalized function is the registered root;
- `agentName` must be a literal the scanner can read statically;
- Tools and stages imported by the agent are not themselves scanned as top-level agents.

## Direct dispatch for colocated agents

When two registered agents share an app, use `dispatch(TargetAgent, request)` rather than HTTP:

```ts
import { dispatch } from "@flue/runtime";
import { CiFixer } from "../ci-fixer/agent.ts";

const result = await dispatch(CiFixer, {
  id: conversationId,
  message: { kind: "user", body: JSON.stringify(input) },
});
```

Project the receipt into an explicit plain object before returning it from a tool. Do not return a domain-interface instance and assume it satisfies Flue's `JsonValue` contract.

## Persistence and runtime boundaries

For a Cloudflare app, Flue's per-conversation Durable Object SQLite is the persistence owner; do not add a Node-style `db.ts`.

For a Node-only app such as Computer User, one app-level `db.ts` selects local SQLite. Computer User remains separate when it requires SSH/Tailscale MCP stdio, a logged-in desktop browser, local files, Accessibility permissions, or a distinct trust boundary.

## Premature shared library consolidation

Small repository-internal concerns (instrumentation, models, standing-rules, utils) should start in one `@repo/lib` package with explicit subpath exports rather than each getting its own package boundary:

```json
{
  "exports": {
    "./instrumentation": "./src/instrumentation/index.ts",
    "./models": "./src/models/index.ts",
    "./standing-rules": "./src/standing-rules/index.ts",
    "./utils": "./src/utils/index.ts"
  }
}
```

No root `@repo/lib` export — consumers must name the conceptual section they depend on. A section graduates from `@repo/lib` into its own package only when it gains a concrete independent dependency/version, runtime/security, external-consumer, or ownership boundary.

## Interaction discipline

Once the user has approved architecture decisions—or explicitly says "no more questions, just build"—stop reopening those decisions. Encode assumptions in architecture tests and execute through verification. Ask again only if a genuinely new destructive or external side effect appears.

## Pitfalls

- Using factory functions (`createMyTool(host)`) where a direct `defineTool(...)` export is sufficient.
- Defining `Host` interfaces and `HostAdapters` when the agent has one deployment target.
- Preemptively extracting `@agents/*` packages before a second consumer exists.
- Separating `render*` functions from `agent.ts` — the agent file IS the composition.
- Returning structural domain objects directly where Flue requires explicit JSON-safe tool output.
- Using `@org/agents/name` as if npm allowed a three-segment package name (it parses as package `@org/agents` plus subpath `./name`).
- Expecting imported code to be registered as a top-level agent without an app-local scanned wrapper.
