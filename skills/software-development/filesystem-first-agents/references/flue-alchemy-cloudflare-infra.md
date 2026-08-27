# Flue Cloudflare infrastructure through Alchemy

Use this when deploying Flue's Cloudflare target with Alchemy as the infrastructure control plane.

## Ownership boundary

- Flue owns agent definitions, runtime behavior, generated Worker/Durable Object classes, conversation persistence semantics, and SDK protocol.
- Alchemy owns Worker deployment, generated Durable Object bindings/migrations, Workflows, Queue/R2, routes/domains, secrets, stages, and stack outputs **only where those resources have no existing declarative owner**. Existing GitOps-owned cloudflared configuration, DNS automation, and cluster resources stay GitOps-owned; do not duplicate them merely because Alchemy has matching resource types.
- Cloudflare runs those primitives.

Keep Alchemy deployment state separate from Flue Durable Object SQLite and Cloudflare Workflow state. Never treat `Cloudflare.state()` or Darkmatter's `stateStore()` as an application database. Preserve the coordinated-infrastructure guard around `STATE_STORE_VERSION`; do not introduce an app-level override.

## Avoid two deploy authorities

Flue's Cloudflare Vite plugin and Alchemy can both try to own Worker build/deploy configuration. Prefer one build authority and one deploy authority:

```text
Flue + Cloudflare Vite build -> generated dist Worker -> Alchemy Cloudflare.Worker(bundle:false, external artifact) -> deploy
```

This avoids double-loading Cloudflare Vite plugins and avoids a hand-maintained Wrangler deploy path. Inspect the actual build output before setting `main`; do not guess paths or generated class names.

Alchemy should explicitly bind each generated Flue Durable Object class exported by the artifact and remain the sole owner of migration history. Pin Flue agent identities/class names. Intentional renames or moves require data-preserving Durable Object migration declarations, not delete/recreate.

## Validated Flue external-artifact contract (2.0.3)

A real Cloudflare-target build with `@flue/runtime@2.0.3`, `@flue/vite@2.0.3`, Vite 8, and the official Cloudflare Vite plugin established these facts:

- An authored `wrangler.jsonc` containing only worker name, compatibility date, and flags builds successfully with **no authored migration list**.
- The emitted config contains the scanner-generated `durable_objects.bindings` and `migrations: []`. This is the clean input when Alchemy owns migrations.
- The output is a module graph, not necessarily one file: `dist/<sanitized-worker-name>/index.js`, sibling `assets/*.js`, and `wrangler.json`. A worker named `flue-agent-platform` emitted under `dist/flue_agent_platform/` in this build. Always read the emitted config instead of hard-coding the directory transformation.
- `bundle: false` must upload the directory graph around `index.js`; do not extract only the entry module or rebundle it.
- Literal top-level `agentName` statics determine stable generated identities. A shared build containing `ci-fixer`, `conductor`, and `improvement-scout` emitted exactly:

  ```text
  FLUE_CI_FIXER_AGENT         -> FlueCiFixerAgent
  FLUE_CONDUCTOR_AGENT        -> FlueConductorAgent
  FLUE_IMPROVEMENT_SCOUT_AGENT -> FlueImprovementScoutAgent
  ```

- Scan output must be validated before deployment: exact binding/class set, `main === "index.js"`, `no_bundle === true`, and an empty emitted migration list. Fail closed on an extra stage agent or missing root.

For pinned `alchemy@2.0.0-beta.57`, source inspection confirms `Cloudflare.Worker` accepts `main`, `bundle: false`, `env`, and `crons`, and its Durable Object namespace surface includes cross-script `.from(worker)`. Do not copy `isExternal` or Effect APIs from a newer nearby checkout unless the pinned package types expose them. Source inspection is not a deployment proof: still run an Alchemy plan/deploy verification before claiming the cross-script sandbox or migration topology works live.

## Resource map

- `Cloudflare.Worker`: Flue HTTP/Slack ingress and generated agent exports.
- `Cloudflare.DurableObject`: structurally single-owned SQLite-backed Flue conversation runtime.
- `Cloudflare.Workflow`: outer business-process orchestration only—multi-agent stages, approvals, sleeps, cross-service retries.
- `Cloudflare.Queues.Queue`: buffering, fan-out, and load shedding; not canonical conversation state.
- `Cloudflare.R2.Bucket`: large immutable artifacts/logs; store references in Flue.
- Access/Tunnel/service tokens: authenticated bridge from Cloudflare control plane to private execution services.
- Secrets/bindings: provider and channel credentials; never plain stack outputs.

Do not wrap every Flue turn or `step.do()` inside a Workflow. Flue owns durable execution of one accepted submission; Workflow owns the process around submissions. In a Workflow, checkpoint the Flue dispatch receipt separately from reading settlement and use a stable submission idempotency key.

## Cloudflare-target sandbox through Alchemy

Flue's Cloudflare Sandbox is a **target-level integration**, not a Node sandbox adapter. The equivalent deployment must preserve four boundaries:

1. Flue/Vite scans `'use agent'` modules and emits the Worker artifact plus generated `Flue<Name>Agent` class exports.
2. Alchemy deploys that artifact as an external Worker (`bundle: false`; use `isExternal: true` where the pinned API requires it) rather than rebundling it.
3. Alchemy declares the exact generated `FLUE_*_AGENT` bindings and remains the sole migration owner for those SQLite classes; do not also deploy a competing Wrangler migration list.
4. The Linux sandbox is a separate Durable Object/container identity, keyed by the stable Flue agent-instance id and bound into the Flue Worker as a namespace such as `env.Sandbox`.

Alchemy's `Cloudflare.Container` normally binds to an Alchemy Durable Object during that object's outer initialization. Do not replace or subclass a Flue-generated agent Durable Object merely to attach the container. A safe composition is an Alchemy-managed sandbox host Worker/DO/Container with a cross-script Durable Object namespace binding in the prebuilt Flue Worker. The sandbox DO must expose the structural exec/filesystem surface consumed by Flue's `cloudflareSandbox(...)` or by an equivalently tested `SandboxFactory` adapter.

The pinned Alchemy source—not a nearby checkout's package version string—is authoritative for API availability. Verify Container support, cross-script DO bindings, external Worker upload, and migration behavior in the exact installed package. Fail closed if the package cannot represent the binding topology; do not fabricate a Wrangler-shaped object that Alchemy ignores.

Focused verification:

- build the Flue Cloudflare target with `flue()` before the official Cloudflare Vite plugin;
- inspect the finalized artifact/config for every generated class and binding;
- typecheck the sandbox namespace/RPC surface against Flue's structural stub;
- prove repeated lookup by one Flue instance id reaches one sandbox identity;
- deploy/dry-run without a second bundle pass or a second migration owner.

## Hybrid execution boundary

A pure Alchemy/Cloudflare stack is possible when Worker-compatible tools plus Cloudflare Sandbox/Containers are sufficient. If execution must use existing k3s/private `.lan`/`.internal` services, use Alchemy for the Cloudflare control plane and existing k3s GitOps/Nix for the sandbox-controller, RBAC, runner images, network policy, quotas, runtime classes, PVCs, and reaper.

Do not hide `kubectl apply` in an Alchemy command solely to claim one control plane. Preserve the existing cluster GitOps security boundary. The Cloudflare Worker reaches the private controller through an authenticated Tunnel/Access service boundary; it never receives Kubernetes credentials.

## Verification spike

Before committing to the stack shape, prove with the pinned installed Flue and Alchemy versions that:

1. Flue's Cloudflare build emits a deployable external Worker artifact.
2. Alchemy deploys it without a second Cloudflare Vite plugin/bundle pass.
3. Alchemy binds every generated Flue DO class and emits the intended SQLite migration.
4. One agent conversation survives Worker redeploy and DO wake.
5. An Alchemy Workflow service-binding call can dispatch Flue work, persist the receipt, and reconnect/read settlement without duplicate submission.
6. Queue replay and Slack retry reuse stable event/submission idempotency keys.
7. Stage destroy cannot accidentally target production names/state.
8. Runtime secrets never appear in stack outputs or generated committed files.

Re-check installed package source/docs because both Flue's generated class/config surface and Alchemy v2 beta APIs move quickly.
