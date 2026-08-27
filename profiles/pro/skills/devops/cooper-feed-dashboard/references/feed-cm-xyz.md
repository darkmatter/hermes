# feed.cm.xyz — deploy anchors (2026-07-30/31)

## Cloudflare

| Item | Value |
|------|--------|
| Account | darkmatter `acb126dc2c4cf93764fa69d9bd55a3cf` |
| Zone cm.xyz | `9c1b96580b4b16d8ebd0ee4887173887` |
| Worker name | `cooper-feed` |
| D1 database | `cooper-feed` (id at deploy: `03df81f9-4597-4e18-a349-0e10e06814f7`) |
| Custom domain binding | hostname `feed.cm.xyz` → service `cooper-feed` |
| Zone route (fixed 1104) | pattern `feed.cm.xyz/*` → script `cooper-feed` |
| workers.dev subdomain | **`drtkmttr`** → `https://cooper-feed.drtkmttr.workers.dev` |
| Alchemy stack | `cooper-feed` stage `prod` |

## Secrets

| Secret | Location |
|--------|----------|
| Ingest Bearer <REDACTED> `himitsu read feed/ingest-token` / env `FEED_INGEST_TOKEN` |
| Access service token | `himitsu read cf-access-client-id` / `cf-access-client-secret` (token name `cooper`) |
| Access API (global key) | `himitsu read cloudflare-global-api-token` + `cloudflare-email` (`X-Auth-Email`/`X-Auth-Key`) |

## Endpoints

- `GET /api/healthz` — Access-gated health JSON
- `GET /api/meta` — snapshot age + recent ingest log
- `GET /api/feed` — full feed-data payload (Access-gated)
- `POST /api/ingest` — Access headers **and** Bearer <REDACTED> (cron/agent push)

## Access (wired 2026-07-31)

App `feed` id `c048f55f-b168-4b57-ab99-f346dcec337e`, AUD `5479b6bd476cdb2519a525a313d4dc76295056b105e629ca378790e1c7a205c3`, team domain `drkmttr.cloudflareaccess.com` (**drkmttr**, not darkmatter — the worker env `CF_TEAM_DOMAIN` was corrected to match).

Policies:
1. `cooper` — reusable, `allow`: emails (`me@cm.xyz`, `cooper@darkmatter.io`, `me@cooperm.com`) + IP `172.117.206.63/32` + service tokens `cooper`/`openclaw`. Reusable → edit via `/access/policies/<id>` only (app endpoint → error 12130).
2. `feed-agents-and-ip` — app-specific, **`non_identity`**: IP + both service tokens. This is the one that actually admits service-token/IP requests; see `cloudflare-access-gating.md`.

## Recipe that worked

```bash
cd ~/git/darkmatter/feed
# Pins: alchemy 2.0.0-beta.66, effect 4.0.0-beta.102, vite ^8
patch -p1 -d node_modules/alchemy < ~/git/darkmatter/platform/patches/alchemy@2.0.0-beta.66.patch
bun run build
export CLOUDFLARE_ACCOUNT_ID=acb126dc2c4cf93764fa69d9bd55a3cf
export FEED_INGEST_TOKEN=<REDACTED>
STAGE=prod bun alchemy deploy ./alchemy.run.ts --stage prod --profile default --yes
bun scripts/push-feed.ts --from ~/feed/src/feed-data.json --url https://feed.cm.xyz
```

If domain 1104 after Alchemy domain attach: POST zone workers route `feed.cm.xyz/*` → `cooper-feed` (or redeploy with stack `routes`).

## Waku UI notes

- Dashboard is client-fetched from `/api/feed` (`src/components/feed-app.tsx`).
- `dashboard.tsx` must not keep a module-scope `const recs = data.recommendations` after de-staticizing; pass `recommendations` into `TaskCard`.
- Build peer: Vite 8 (Vite 6 + current `@vitejs/plugin-react` → `ERR_PACKAGE_PATH_NOT_EXPORTED` on `vite/internal`).
