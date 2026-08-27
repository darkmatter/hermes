# Flue portable durability and multi-surface deployment

Use this when designing one Flue agent reachable from local tooling, Kubernetes, Cloudflare Workers, Slack, cron, or queue workers.

## Core durability contract

Flue admits every input as a durable **submission before model work begins**. Each accepted submission must settle once as `completed`, `failed`, or `aborted`. Per conversation it stores the canonical append-only stream, accepted submissions/attempt leases, tool results, persistent state, delegated transcripts, and recovery facts.

Execution semantics are **at-least-once execution over exactly-once recording**:

- recorded responses and tool results are reused;
- an interrupted ordinary tool gets an unknown-outcome marker rather than being blindly repeated;
- a `durable: true` tool is re-entered and resumes through recorded `step.do(name, fn)` results;
- every external mutation still needs an application/API idempotency key, ideally derived from `toolCallId`, submission id, or a stable business operation id;
- delegated tasks have their own durable transcripts and are reattached on recovery;
- `usePersistentState()` is conversation-durable, but sandbox files are not.

Agent-level bounds:

```ts
Agent.durability = { maxAttempts: 5, timeoutMs: 7_200_000 };
```

Defaults documented in the 2026-07 Flue reference were ten attempts and one hour per submission; confirm against the installed version before relying on defaults.

## Storage and ownership

### Node local / single host

Use file-backed SQLite in `db.ts`:

```ts
import { sqlite } from '@flue/runtime/node';
export default sqlite(process.env.FLUE_DB_PATH ?? './data/flue.db');
```

This survives process restarts on the same host, not host loss. No `db.ts` means deployed Node uses in-memory state and loses it on restart.

### Kubernetes / k3s

Use Postgres, libSQL, or another external adapter for pod/node-loss recovery. A shared database permits a replacement process to recover work, but **does not make Node active-active**: one conversation must have exactly one live owner. Start with one Flue pod, durable external storage, readiness/liveness probes, graceful termination, and a PodDisruptionBudget. Do not put the same conversation behind naive round-robin replicas. Scale only after adding conversation-affine partitioning/routing.

### Cloudflare Worker

Flue's Cloudflare target maps each conversation to a Durable Object with built-in SQLite, structural single ownership, wake-driven recovery, and no `db.ts`. It is a separate durability domain from Node/Postgres and cannot transparently continue Node conversations. It is best for Fetch-compatible globally addressed agents, not Node-only `local()` filesystem/shell work.

## One durable owner, many ingress surfaces

Prefer one authoritative runtime rather than copies on every surface:

```text
local CLI ───────┐
Slack webhook ───┤
cron/queue worker├──> canonical Flue service ──> durable store
HTTP callers ────┘
```

For Darkmatter-style self-hosting, the default architecture is a Node-target Flue service in k3s with Postgres. Local scripts use `@flue/sdk`; Slack mounts a verified channel; CronJobs and queue workers dispatch idempotent submissions. An ephemeral worker should be a dispatcher or tool executor, not the sole conversation owner, unless another compatible process is guaranteed to restart and reconcile its store.

Persist the SDK dispatch receipt if the calling process may exit. The local `Promise` is not durable; the accepted server-side submission is. A later process can reattach using the receipt.

## Slack pattern

Slack is ingress/presentation, not a durability backend:

1. Verify request signatures.
2. Map `(team, channel, thread)` to a stable conversation id.
3. Dispatch the event and acknowledge Slack quickly.
4. Bind channel/thread/token in trusted code; expose only a narrow reply tool to the model.
5. Claim or deduplicate Slack `event_id` in application-owned durable state before dispatch when duplicate admission matters.
6. Keep short-lived `trigger_id` and `response_url` capabilities out of model context and durable history.

## Workspace caveat

Conversation storage does not persist sandbox files. For coding agents, separately choose a PVC keyed to the conversation, a durable remote sandbox, or Git-backed checkpoints. A durable database and a durable workspace solve different failure modes.

## Target portability boundary

The same agent source can build for local Node, k3s Node, or Cloudflare, but history only follows the backing durability domain. To continue the same production conversation from a local machine, make local tooling an SDK client of the canonical service. Pointing multiple Node runtimes at one external database is valid only when ownership prevents overlap. Moving between Node storage and Durable Objects requires explicit export/import or an application-level handoff.

## Verification checklist

- Durable `db.ts` configured for Node production; Cloudflare has no `db.ts`.
- Every important effect is in a `durable: true` tool and a stable `step.do` boundary.
- External mutations accept stable idempotency keys.
- Conversation ids encode stable domain identity (Slack thread, repo/PR/SHA, schedule window).
- Only one Node owner can process a conversation at a time.
- Sandbox/workspace persistence is designed separately.
- Slack/webhook retries cannot cause duplicate admissions or duplicate effects.
- Recovery is tested by killing the runtime after admission and during each durable step, then starting a replacement and observing terminal settlement.

Authoritative local references used for this note: Flue docs `guide/durability.md`, `guide/database.md`, `guide/node-target.md`, `guide/deploy.md`, and `ecosystem/channels/slack.md` (reviewed 2026-07-21). Re-check installed docs when Flue versions change.
