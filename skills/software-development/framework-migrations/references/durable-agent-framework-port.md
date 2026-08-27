# Durable Agent Framework Port Checklist

Use this reference when an existing scheduled or tool-driven agent must be recreated on a durable agent framework.

## Suggested Target Layout

```text
app/
├── agent/
│   ├── agent.ts                 # root authoring boundary
│   ├── stages.ts                # scan/claim/fix or equivalent child agents
│   ├── tools/
│   │   ├── run-workflow.ts      # durable orchestration tool
│   │   └── post-report.ts       # optional delivery boundary
│   └── lib/
│       ├── config.ts            # normalization and host gates
│       ├── constants.ts
│       ├── types.ts
│       ├── parse-*.ts           # pessimistic model-output parsers
│       ├── select-targets.ts
│       ├── verify-claim.ts      # external exact-state verification
│       ├── host-http.ts         # token-backed host adapter
│       └── run-pipeline.ts      # framework-independent orchestration
├── src/
│   ├── app.ts                   # framework router
│   └── db.ts                    # persistent adapter
├── tests/
│   └── workflow.test.ts         # offline characterization/safety tests
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Durable Stage Runner Pattern

A model-callable orchestration tool should:

1. declare access to the framework harness;
2. declare durability;
3. assign each stage a deterministic ID such as `scan`, `claim:<target>`, `fix:<target>`;
4. run each model call inside the durable step primitive using that ID;
5. return only JSON-serializable stage responses;
6. pass the stage runner into a framework-independent pipeline.

Keep authorization outside model prose. Before invoking any mutation-capable stage, check that the authenticated host adapter exists. After a model claims external state, independently re-read the canonical API and verify the exact target revision before dispatching the consequential stage.

## Token-Backed Host Adapter

A safe adapter should:

- reject empty tokens at construction;
- add authorization, API-version, accept, and user-agent headers internally;
- apply a bounded timeout;
- expose the smallest read surface needed for verification;
- disable non-GET/HEAD methods unless the host explicitly enables mutations;
- never log the token;
- accept an injected fetch implementation for offline tests.

Test both positive authentication and negative mutation behavior. In Bun projects, type an injected fetch as a small callable interface rather than `typeof globalThis.fetch`; Bun may augment the global function with properties such as `preconnect`, making simple test doubles fail TypeScript assignment.

## Offline Safety Matrix

At minimum, test:

| Area | Required behavior |
|---|---|
| Empty allowlist | No-op before model spend |
| Invalid target | Fails before any stage |
| Dry run | Scan only; no claim, fix, report, comment, reaction, or push |
| Malformed scan | Failed run, not an empty success |
| Claim parser | Literal affirmative only |
| Missing credentials | Mutation-capable stages are not prompted |
| External verification | Exact full revision/SHA, open target, fresh unique marker |
| Stale/ambiguous marker | Refuse and never dispatch fix |
| Attempt cap | Exhausted targets skipped deterministically |
| Fork/push gate | Forks remain propose-only |
| Host mutation adapter | Non-read methods refused by default |
| Durable IDs | Stable and unique per logical stage |

## Verification Commands

Run from the target package first:

```bash
bun run typecheck
bun test
bun run build
```

Then run the workspace equivalents from the repository root. A root failure in another package does not invalidate successful target evidence, but it must be reported exactly. Do not repair the sibling package unless the task includes it.

## Dependency Pins

Resolve exact requested versions before depending on their APIs. If a requested prerelease does not resolve, verify the authoritative registry and reference checkout rather than guessing. Preserve a working lockfile and report any fallback pin as a deviation, not as if the original request was satisfied.
