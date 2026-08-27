# flue-ref checkout hygiene

Use when working under `~/git/czxtm/flue-ref` or when Cooper asks whether “we just created this repo,” whether `.flue/` should be gitignored, or how to verify a Flue→celld spike.

## What flue-ref is

| Fact | Detail |
| --- | --- |
| Path | `~/git/czxtm/flue-ref` |
| Origin | **Literal clone** of `https://github.com/withastro/flue` |
| Typical tip | Detached HEAD on a release tag (e.g. `v2.0.1` / `902259b`) |
| Not | A greenfield Cooper/czxtm product repo we authored |

**Only local addition from the 2026-08-07 spike:** `examples/celld-spike/`.
Everything else in the tree (including root **`.flue/`**) is **upstream**.

Cooper product Flue apps: `~/git/czxtm/agents-flue`. If the spike graduates past playground status, **copy it out** of `flue-ref` rather than living forever on detached upstream HEAD.

## `.flue/` is source — do not gitignore

Flue source-root priority: **`.flue/` → `src/` → project root**.

| Path | Treat as | Git |
| --- | --- | --- |
| `.flue/` | Authored source root (same class as `src/`) | **Commit** |
| `src/` | Canonical new-app layout; celld spike uses this | **Commit** |
| `.flue-vite/`, `.flue-vite.wrangler.jsonc` | Vite/CF **generated** merge inputs | **gitignore** |
| `dist/`, `.wrangler/`, `celld-out*`, `.celld-state*` | Build + local celld SQLite/replication | **gitignore** |
| `.env`, admit/read body dumps | Secrets / runtime noise | **gitignore** |

**Never gitignore `.flue/` because it is dot-prefixed.** Upstream flue-ref ships real agents there (e.g. `.flue/agents/pr-redirect.ts`).

## Workspace placement

- Put spikes under `flue-ref/examples/*` so `@flue/*` resolves as `workspace:*`.
- A **sibling** package with `file:../flue-ref/packages/*` fails: `@flue/vite` still wants `@flue/runtime@workspace:*`.

## Verify Flue CF / celld spikes correctly

| Layer | Command |
| --- | --- |
| Worker compile | `hermes verify --json --skip-start --phase build` and/or `pnpm run build` |
| celld package | `bash ./scripts/rebuild-deploy.sh` |
| Live durability | celld on free port → ping → POST admit → poll GET for `settlements[].outcome` |

**Why `--skip-start`:** hermes detect maps examples to Vite (`npm run dev` :5173). Real host is **celld**, not vite dev — a failed “start” phase is not a Flue/celld failure.

**Port tip:** Mac `:8788` is often `ask_cooper_server.py` — use **8799** for local celld.

## Dirty-index hygiene on detached HEAD

Working inside upstream will stage runtime junk unless ignored. Spike `.gitignore` must cover at least:

```
node_modules/
dist/
.wrangler/
celld-out/
celld-out-single/
.celld-state*/
.admit.body
.admit.headers
.read.body
.env
.<REDACTED>
*.log
```

If junk hits the index: `git reset HEAD -- examples/celld-spike` then re-add **source only**. Never push playground spike commits to `withastro/flue`.

## Full celld adapter

Proven single-file esbuild path, provider wiring, and live evidence: `references/flue-celld-self-hosted-dos.md`.
