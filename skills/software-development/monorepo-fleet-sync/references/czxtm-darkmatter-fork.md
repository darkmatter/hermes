# czxtm/agents ↔ darkmatter/agents

`~/git/czxtm/agents` is a **personal fork** of `~/git/darkmatter/agents`. Both
left the old `src/` layout for `agents/` + `apps/` **independently**. Shared
history exists (merge-base is typically the `@repo` rename), but the
restructure commits are parallel — they are not a clean rebase onto each other.

## Paths (do not mix)

| Path | What it is |
| --- | --- |
| `~/git/darkmatter/agents` | Upstream Flue fleet (`darkmatter/agents.git`) |
| `~/git/czxtm/agents` | Personal fork (`czxtm/agents.git`) — keep this on darkmatter/main + unique agents |
| `~/git/agents` | **Historical Eve scaffold** — not the live fleet |

## Do not `git rebase` the restructure

Replaying czxtm’s `refactor(workspace): restructured…` onto darkmatter/main
re-adds the same `agents/*` trees and conflicts for hundreds of files.

Working method:

1. `git stash push -u` on czxtm (keep the WIP).
2. `git branch czxtm/pre-rebase-main` (or similar) as a backup tip.
3. Fetch darkmatter (`git remote add darkmatter …` if missing) and
   `git reset --hard darkmatter/main`.
4. Replay **only unique packages** from the backup:
   `git checkout czxtm/pre-rebase-main -- agents/dip-buyer agents/phone-ops`
5. Re-wire them through the current platform/router surface (see the
   adding-agents checklist in this skill). Do **not** stash-pop the whole
   pared-down `platform.ts` — it fights the full fleet.
6. Overlay additive files only (`packages/sandbox/src/ssh.ts`, desktop
   `useSandbox` host wiring) without deleting darkmatter’s CF sandbox.

Unique czxtm value after a reset: **dip-buyer**, **phone-ops**, and any
additive SSH/desktop overlay. The old pared-down fleet lives on the backup
branch, not on `main`.

## Stale `dist/` after a history rewrite

Workspace packages export types from `dist/*.d.mts`. After `reset --hard` +
`bun install`, `tsc` in `apps/platform` / `agents/router` will lie:

- `Cannot find module '@agents/critic'` — package exists, **dist missing**
- `Record<…>` missing `digest` / extra old specialists — **router dist** still
  has the pre-reset `SPECIALISTS` union

Rebuild before trusting typecheck:

```bash
bunx turbo run build --filter=@repo/lib --filter=@repo/connectors --filter=@agents/router --filter=@agents/dip-buyer --filter=@agents/phone-ops
bunx turbo run typecheck --filter=@repo/platform --filter=@agents/router
```

Do not “fix” source to match a stale `dist` union.

## Adding dip-buyer / phone-ops on a full fleet

Hyphenated identities (`dip-buyer`, `phone-ops`):

- Route / `agentName`: hyphens
- Env / wrangler class: `DIP_BUYER_URL`, `FlueDipBuyerAgent`, `FLUE_DIP_BUYER_AGENT`
- Tests that derive env keys: `specialist.replaceAll("-", "_").toUpperCase() + "_URL"`

Append a **new** wrangler tag (`v6-personal-agents`); never rewrite deployed
`new_sqlite_classes` tags. Update in lockstep:

- `apps/platform/test/alchemy-artifact.test.ts` `validConfig` (new tag + bindings)
- `apps/platform/test/agent-identities.test.ts` pin + length
- `apps/platform/test/dispatch-local.test.ts` `localAgents`

`apps/platform/test/alchemy_bun_test_.ts` is live-only
(`RUN_ALCHEMY_INTEGRATION=1`) and is often already stale vs darkmatter
(coder/digest). Do not treat it as the unit-test gate.
