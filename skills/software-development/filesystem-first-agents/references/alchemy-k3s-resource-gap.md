# Alchemy resource-gap review for Flue + private k3s

Use this when deciding whether a hybrid Flue deployment needs new Alchemy provider resources. Inspect the checked-out Alchemy source rather than inferring coverage from package names or older docs.

## Review method

1. Inventory the desired deployment graph by trust boundary: Cloudflare control plane, authenticated bridge, standing Kubernetes infrastructure, and ephemeral sandbox runtime.
2. Search Alchemy's actual exported resources and provider implementations for each node.
3. Read resource props and reconciler/auth code, not only filenames or JSDoc.
4. Classify each requirement as:
   - existing resource usable as-is;
   - existing primitive needing composition in the application repo;
   - provider gap requiring an Alchemy contribution;
   - runtime object that must not become infrastructure state.
5. Cite the exact source paths/lines that establish constraints.

## Current resource map to verify

Alchemy already has the Cloudflare primitives needed for the control plane:

- Worker and secret/env bindings (`Redacted<string>` becomes `secret_text`);
- Durable Objects and migrations;
- Workflows;
- Queues and consumers;
- R2 buckets and bindings;
- Access Application, Policy, and ServiceToken;
- Tunnel, Tunnel Configuration, and DNS Record.

For Worker-to-private-k3s calls, use a public Access-protected hostname routed through Tunnel ingress. `Tunnel.HostnameRoute` is for WARP/private-network clients; a Worker is not a WARP client. The origin can be a ClusterIP DNS name such as `http://service.namespace.svc.<REDACTED>:80` when cloudflared runs inside the cluster.

Do not invent Flue-specific Worker/Workflow/R2 resources unless repeated application composition justifies them. Flue builds runtime behavior; Alchemy deploys and binds the emitted artifact.

## Decision gate: inspect the existing reconciler first

Before designing provider work, inspect the target cluster's desired-state repository and bootstrap path. If Argo CD, Flux, or another GitOps controller already owns Kubernetes objects, **stop treating direct Alchemy reconciliation as the default**:

- Git commits/manifests are the desired-state interface;
- the existing GitOps controller owns apply, prune, drift correction, and rollout ordering;
- Alchemy must not apply the same Deployment, Service, RBAC, policy, PVC, Tunnel configuration, or DNS record;
- cross-plane outputs should become reviewed/versioned GitOps inputs or use the existing secret/config delivery path—not a hidden `kubectl apply` command.

For an Argo-managed k3s cluster, do **not** build `Kubernetes.KubeconfigCluster`, arbitrary-kind wrappers, or richer Pod types merely to make the deployment look uniform. Build those only for a separate, explicit provider contribution where Alchemy is intended to become the sole Kubernetes reconciler.

## Existing Kubernetes module: important limitation

When evaluating that separate provider contribution, the inspected Alchemy Kubernetes module is useful scaffolding but is coupled to `AWS.EKS.Cluster`:

- object helpers accept the EKS Cluster type;
- object lifecycle is implemented as bindings reconciled by the EKS cluster provider;
- the generic client creates AWS STS `k8s-aws-v1` tokens;
- supported API kinds are hard-coded and limited;
- typed Deployment/Job pod specs expose only a small subset of hardening fields.

Therefore, **only when Alchemy is deliberately becoming the sole reconciler for a non-GitOps cluster**, the provider contribution is not “Kubernetes from scratch”; it is to generalize the current child-object mechanism. The provider work below is conditional and is not part of a normal Argo-managed application deployment.

## Provider work, in order

### P0: provider-neutral cluster target

Introduce a cluster/object-owner interface implemented by both EKS and an external cluster target. Add `Kubernetes.KubeconfigCluster` (or equivalent) that:

- selects an explicit kubeconfig context;
- loads credentials at deployment time;
- does not persist bearer <REDACTED> private keys as ordinary state;
- pins endpoint and CA identity;
- collects and reconciles bound Kubernetes objects;
- preserves the existing server-side-apply and ordered deletion machinery.

Move EKS STS token creation behind an EKS authentication strategy instead of keeping it in the generic client.

### P0: arbitrary-kind support

Replace or extend the closed kind table. Initial safe shape: allow explicit `{ plural, scope, applyRank }` metadata on a raw object and ship built-ins for common kinds. Stronger future shape: Kubernetes API discovery with explicit metadata as fallback. This enables CRDs without a new Alchemy release per kind.

### P1: security and policy kinds

Add built-in support and preferably typed wrappers for:

- Role and RoleBinding;
- NetworkPolicy;
- ResourceQuota and LimitRange;
- PersistentVolumeClaim;
- PodDisruptionBudget.

Expand shared Pod/container types for security contexts, automounted token control, volumes/mounts, probes, affinity/tolerations, RuntimeClass, image-pull secrets, termination grace, and ephemeral-storage limits. Reuse those types in Deployment and Job.

### P1: readiness

Server-side apply is not rollout success. Add a generic `Kubernetes.WaitFor` or workload-specific readiness option with bounded timeout and condition checks. A deploy should fail when the controller or cloudflared cannot become ready.

### P2: secret handling

Only add `Kubernetes.Secret` if Alchemy should own cluster secret delivery. It must accept redacted inputs, omit values from outputs, and avoid ordinary state serialization. When the cluster already uses SOPS/GitOps, retain that owner rather than duplicating it in Alchemy.

## Static infrastructure versus runtime sandboxes

Choose exactly one owner for standing resources:

- **Existing Argo/Flux deployment:** GitOps owns namespaces, controller Deployment/Service, ServiceAccount/RBAC, cloudflared, NetworkPolicies, quotas, LimitRanges, PDBs, storage/runtime policy, and encrypted cluster secrets. Alchemy owns only Cloudflare resources not already declared elsewhere.
- **Explicit Alchemy-owned cluster:** Alchemy may own those standing objects only when no competing reconciler manages them and the provider gap work above has actually been completed.

In either case, the sandbox-controller—not Alchemy or Argo—owns ephemeral Pods, Jobs, per-sandbox PVCs, operation leases, and TTL cleanup. Running an infrastructure deployment per tool command would make deployment state contend with runtime execution and is the wrong ownership model.

## Recommended graph for an Argo-managed cluster

```text
Alchemy stack
  -> Flue Worker + generated DO bindings/migrations
  -> optional Workflow/Queue/R2
  -> Access application/service identity when not already owned

Git repository -> Argo CD
  -> generic flue-agent/sandbox platform
  -> controller + ServiceAccount/RBAC + policy + storage/runtime classes
  -> existing cloudflared route and DNS automation when those are Git-managed

sandbox-controller
  -> dynamic constrained Pod/PVC leases
```

Do not let Alchemy also own a Tunnel configuration or DNS record merely because the resource exists in Alchemy when the GitOps repository already derives those resources from its cloudflared configuration.

## Pitfalls

- Do not call a module “generic Kubernetes” until its auth, cluster type, and object owner are provider-neutral.
- Do not mistake raw-object syntax for arbitrary-kind support when URL construction uses a closed kind registry.
- Do not use private `HostnameRoute` for a Worker that cannot participate in WARP.
- Do not put Access client secrets or Kubernetes credentials in plain stack outputs.
- Do not hide `kubectl apply` inside an Alchemy command merely to claim a single deploy tool.
- Do not report deployment success immediately after apply when workload readiness matters.

Re-inspect source whenever Alchemy versions move; this reference captures the review technique and architectural boundary, not a permanent claim that particular resources remain absent.
