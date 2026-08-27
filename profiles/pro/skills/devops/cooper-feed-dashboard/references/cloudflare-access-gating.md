# Cloudflare Access gating for a Worker hostname (service tokens + IP)

Recipe proven on `feed.cm.xyz` (2026-07-31). Applies to any Worker custom domain you want gated by CF Access while still letting agents/crons hit APIs non-interactively.

## The one rule that bites

**Decision `allow` does NOT admit service tokens or IP-only requests.** A policy with `decision: "allow"` and `include: [{service_token: …}]` still 302s to the Access login page for token-bearing requests. Machine access requires a policy with **`decision: "non_identity"`** (or `bypass`). Identity (email OTP/SSO) → `allow`; machines (service token, IP) → `non_identity`. Layer both on the same app.

## Shape that works

App: `self_hosted`, domain `feed.cm.xyz`, session 24h.

Policies (precedence order):
1. `cooper` — reusable, `allow`: emails + IP `/32` + service tokens (identity path for browsers).
2. `feed-agents-and-ip` — app-specific, `non_identity`: same IP `/32` + service tokens (machine path).

## API access — which credential for which endpoint

| Credential | Use for |
|---|---|
| Wrangler OAuth token (`~/.config/.wrangler/config/default.toml`) | Workers scripts/domains/routes, D1, DNS — **NOT** `/access/*` (error 10000 "Authentication error") |
| Global API key (himitsu `cloudflare-global-api-token` + `cloudflare-email`) as `X-Auth-Email` / `X-Auth-Key` | `/access/*` endpoints |

## Editing gotchas

- Reusable policies (`reusable: true`) cannot be updated via `/access/apps/<app>/policies/<id>` → error **12130**. Edit them at `/access/policies/<id>` (reusable endpoint) or create app-specific policies on the app.
- App-specific policies created via `/access/apps/<app>/policies` get `reusable: false` and are freely editable/deletable there.

## Agent request pattern

```bash
curl https://<host>/api/... \
  -H "CF-Access-Client-Id: $(himitsu read cf-access-client-id)" \
  -H "CF-Access-Client-Secret: $(himitsu read cf-access-client-secret)" \
  -H "Authorization: Bearer <REDACTED>"   # app's own auth, if any
```

Access issues a `CF_Authorization` cookie on success; 302 to `*.cloudflareaccess.com/cdn-cgi/access/login/...` means the request fell through to the identity path (wrong/missing decision `non_identity` match).

## Verify

```bash
# Expect 200 with service token, 302 without (unless IP allowlisted)
curl -sS -o /dev/null -w "%{http_code}\n" https://<host>/api/healthz \
  -H "CF-Access-Client-Id: $ID" -H "CF-Access-Client-Secret: $SECRET"
```

Changing home IP later: PUT the app-specific policy with the new `{"ip": {"ip": "<ip>/32"}}` — reusable policy edit needs the `/access/policies` endpoint.
