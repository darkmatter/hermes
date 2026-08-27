# Flue sandboxes on k3s: broker, durability, and auth

Use this when a Flue agent needs an isolated Linux workspace in k3s. Flue supplies the adapter contract; the application owns sandbox provisioning, reuse, and cleanup.

## Architecture

```text
Flue agent --authenticated HTTPS--> sandbox-controller --narrow RBAC--> Pod + PVC
```

Do not give the model, Flue Worker, or model-facing shell Kubernetes credentials. Put the Kubernetes API behind a trusted controller that enforces fixed profiles for images, resource limits, network access, workspace size, TTL, and external capabilities.

A Flue `SandboxFactory.createSessionEnv({ id })` receives the stable agent instance id. Use it as an idempotent workspace key:

1. `findOrCreate(id, approvedProfile)` returns the existing lease or creates one.
2. Wrap controller file/exec methods as `SandboxApi`.
3. Return `createSandboxSessionEnv(api, "/workspace")`.
4. Keep controller credentials and the sandbox lease token in the adapter closure, never in model-visible env or conversation state.

The profile is selected by trusted agent code (`coding`, `ci`, `read-only`); the model must not choose images, service accounts, namespaces, network policy, or arbitrary resource limits.

## Generic platform manifests, not one workload per logical agent

GitOps should describe a reusable execution/runtime platform, not encode a logical agent such as `nixmac-coder`, `ci-fixer`, or `improvement-scout` into Kubernetes object names and environment variables.

Default shape:

```text
apps/flue-agent-platform.yaml
manifests/flue-agent-platform/
  controller/runtime Service + Deployment
  ServiceAccount/RBAC
  NetworkPolicy, quotas, limits, storage/runtime policy
```

Logical agent identity, prompt, tools, model, and route belong in the Flue application repository. Repository URL and exact source revision are authorized task/lease data. Dynamic workspaces are keyed by conversation/run/lease identity and are created by the controller; do not seed one hard-coded repository in an init container or provision one permanent agent-named PVC.

Use generic approved profiles (`read-only-small`, `coding-standard`, `coding-large`, `ci-build`) for image, resources, network, runtime class, TTL, and credential capabilities. An ApplicationSet that emits one Deployment per agent is an exception for independently scaled, independently released, or hard-isolated products—not the default way to register an agent.

## Durable workspace model

Prefer replaceable compute plus durable workspace:

- constrained Pod for execution;
- PVC for `/workspace` when files must survive pod/runtime restarts;
- stable lookup key derived from Flue instance id;
- lease metadata with `lastUsedAt`, idle TTL, and absolute max lifetime;
- stop/recreate Pod while retaining PVC when idle;
- explicit retention policy for successful, failed, and abandoned workspaces.

Flue has no sandbox teardown callback. A controller/reaper must own cleanup; never rely on agent disposal.

Conversation durability and workspace durability are independent. A recovered Flue submission can reconnect to the same workspace only if the adapter's `findOrCreate(id)` is idempotent and the workspace survived.

## Controller API shape

Typical control surface:

```text
PUT    /v1/sandboxes/by-key/:key       # idempotent find/create
GET    /v1/sandboxes/:id
POST   /v1/sandboxes/:id/exec
GET    /v1/sandboxes/:id/operations/:operationId
DELETE /v1/sandboxes/:id/operations/:operationId
GET/PUT /v1/sandboxes/:id/files/...
POST   /v1/sandboxes/:id/keepalive
DELETE /v1/sandboxes/:id
```

Use an operation id for every exec. On transport loss, query status rather than resubmitting. The runner should execute each command in a process group and support TERM→bounded grace→KILL cancellation. Report infrastructure death as Flue `SandboxDiedError`; use `onOrphanSettled` for late command settlement/reaping.

A transport operation id does not make shell effects exactly-once across an agent crash. Flue intentionally marks unresolved ordinary tools as unknown outcome. Consequential mutations (push, deploy, comments, issue creation) belong in custom durable tools with `step.do()` and external idempotency—not raw Bash.

## Authentication chain

Keep identities separate:

1. **Slack → ingress:** verify Slack HMAC signature and timestamp window; dedupe `event_id`; map the verified actor to application policy only.
2. **Cloudflare Flue Worker → controller:** place the controller behind Cloudflare Tunnel + Access service authentication. Store per-stage Access service-token credentials as Worker secrets; verify the Access JWT at the origin. Map the authenticated service principal to allowed sandbox profiles and quotas.
3. **In-cluster Flue → controller:** use short-lived projected Kubernetes service-account tokens with `audience: sandbox-controller`; validate with TokenReview and expected audience.
4. **Local user → Flue:** normally authenticate to the canonical Flue service and let its workload identity call the controller. For controller development, use Tailscale plus short-lived user OIDC; do not distribute production Worker credentials.
5. **Controller → Kubernetes:** dedicated namespace-scoped service account. Allow only required Pod/PVC/Lease/Service verbs and `pods/exec` if unavoidable. Never grant cluster-admin, RBAC mutation, arbitrary Secret reads, or unrelated namespace access.
6. **Adapter → sandbox:** controller returns a short-lived capability bound to sandbox id, service principal, Flue instance id, stage, allowed verbs, and expiry. Keep it out of shell env, logs, tool inputs, and model context.

Authorization is policy over authenticated principal + stage + agent + profile + repository/tenant + quotas. Never trust a caller-supplied `agentName` as authority.

## Pod hardening

- `automountServiceAccountToken: false`;
- non-root; no privilege escalation; drop all capabilities;
- read-only root filesystem; writable `/workspace` and `/tmp` only;
- `seccompProfile: RuntimeDefault`;
- explicit CPU, memory, ephemeral-storage, and PID limits;
- no host network/PID/IPC, hostPath, privileged mode, or Docker socket;
- default-deny ingress and egress with profile-specific allowlists;
- gVisor/Kata RuntimeClass when available;
- fixed allowlisted runner images and namespace quotas.

## External credentials

Prefer, in order:

1. narrow trusted application tools outside the sandbox;
2. short-lived task-scoped tokens from a credential broker;
3. controller-performed checkout/upload before model access;
4. long-lived credentials inside the sandbox only as a last resort.

For private Git, have the controller obtain a short-lived GitHub App installation token, clone an exact repo/ref, discard the token, and hand the prepared workspace to the agent. Publish via a trusted durable Flue tool after validating the patch/commit. Do not expose general GitHub, Slack, Linear, model-provider, or cluster credentials to Bash.

## Ownership split

For a hybrid Cloudflare/k3s deployment:

- Alchemy manages the Flue Worker, generated Durable Object bindings/migrations, Workflows, optional Queue/R2, Worker secrets, and Cloudflare resources that have no existing owner.
- Existing k3s GitOps/Nix manages the generic platform/controller Deployment, ServiceAccount/RBAC, namespace policy, runner images, NetworkPolicies, quota, RuntimeClass, PVC policy, reaper, and encrypted cluster secrets.
- If the GitOps repository already owns cloudflared configuration and derives DNS records from it, add the route there; do not also declare that Tunnel configuration or DNS record in Alchemy. Alchemy may still own a new Access application/service identity when it does not collide with an existing Access owner.

Do not hide `kubectl apply` inside an Alchemy command merely to claim one control plane; preserve the cluster's existing GitOps security boundary. Inspect the desired-state repository before proposing provider work.

## Verification

- Repeated `findOrCreate` for one Flue id returns one workspace.
- Kill/recreate the Pod and confirm the same PVC reconnects.
- Reject unauthorized principals, profiles, repos, and quota excess.
- Confirm sandbox Pods have no Kubernetes token or secret access.
- Drop the exec response and confirm the adapter reads the existing operation instead of rerunning it.
- Abort a process tree and confirm no grandchildren remain.
- Verify TTL cleanup without any Flue teardown callback.
- Test default-deny network policy and each explicit egress profile.

Reference contract: Flue `SandboxFactory`, `SandboxApi`, and `createSandboxSessionEnv`; re-check installed Flue docs when versions change.
