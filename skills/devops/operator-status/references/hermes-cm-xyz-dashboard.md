# hermes.cm.xyz Dashboard

The Hermes web dashboard served via Cloudflare Tunnel on devbox.

## Connection

| Component | Value |
|---|---|
| URL | `https://hermes.cm.xyz` |
| Tunnel ID | `6a0b0a83-c9d2-4ea7-beac-2fd817f1e154` (name: `devbox`) |
| DNS | CNAME `hermes.cm.xyz` → `6a0b0a83-c9d2-4ea7-beac-2fd817f1e154.cfargotunnel.com` |
| Ingress | `hermes.cm.xyz` → `http://localhost:9119` on devbox |
| Serve command | `hermes dashboard --port 9119 --host 127.0.0.1 --skip-build` |
| Gateway port | 8644 (devbox) — messaging gateway, NOT the web UI |

## NOT `hermes serve`

`hermes serve` is the headless backend (returns 404 / "web UI disabled").
Use `hermes dashboard` for the browser UI.

## systemd persistence (devbox)

Unit: `~/.config/systemd/user/hermes-serve.service` (enabled, `Restart=always`).

```ini
ExecStart=hermes dashboard --no-open --host 127.0.0.1 --port 9119
Environment=HERMES_HOME=~/.hermes
Environment=HERMES_DASHBOARD_BASIC_AUTH_USERNAME=cm
EnvironmentFile=/run/secrets/rendered/hermes-dashboard.env
```

**Critical: bind `127.0.0.1`, not `0.0.0.0`.** Hermes ≥2026.7.30 refuses
public binds (`0.0.0.0`) without a registered auth provider (password or
OAuth). The Cloudflare tunnel connects to `localhost:9119`, so
`127.0.0.1` is sufficient — no auth gate, no public exposure.

### Tunnel `httpHostHeader` must be `localhost` (not `localhost:9119`)

The Hermes auth gate (`should_require_auth`) checks the incoming Host header
against `{"localhost", "127.0.0.1", "::1"}` — **exact match, no port suffix**.
If the tunnel's `httpHostHeader` is `"localhost:9119"`, the gate sees
`localhost:9119` which is NOT in the set → engages auth → returns 401 on
all `/api/*` routes (the SPA HTML still loads but API calls fail).

Fix: set `httpHostHeader: "localhost"` (no port) in the tunnel config:

```bash
curl -X PUT \
  -H "X-Auth-Email: $(himitsu read cloudflare-email)" \
  -H "X-Auth-Key: $(himitsu read cloudflare-global-api-token)" \
  -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/accounts/acb126dc2c4cf93764fa69d9bd55a3cf/cfd_tunnel/6a0b0a83-c9d2-4ea7-beac-2fd817f1e154/configurations" \
  --data '{"config":{"ingress":[{"service":"http://localhost:9119","hostname":"hermes.cm.xyz","originRequest":{"noTLSVerify":false,"httpHostHeader":"localhost","disableChunkedEncoding":true}},{\"service\":\"http_status:404\"}],\"warp-routing\":{\"enabled\":false}}}'
```

### Kanban not available in dashboard web UI

The Hermes web dashboard (`hermes dashboard`) exposes kanban as a built-in
tab, but only when the kanban **plugin** is discoverable. The plugin lives at
`plugins/kanban/dashboard/` and needs a `manifest.json` (plugin manifest with
`name`, `tab`, `entry`, `api` fields) + `dist/` (prebuilt frontend JS/CSS) +
`plugin_api.py` (FastAPI router). Routes mount at `/api/plugins/kanban/*`.

**Hermes 2026.7.30 nix packaging bug:** the nix derivation's `postInstall`
copies `skills/` and `optional-skills/` but **not** `plugins/kanban/dashboard/`
(only `plugin_api.py` ends up in the store — `manifest.json` and `dist/` are
dropped). Without `manifest.json` the plugin discovery scanner skips it →
"Plugin not found" on `/api/plugins/kanban/*`. Hermes 2026.7.20 had the files.

This is a **nix derivation `postInstall` gap** (the build doesn't copy
plugin dashboard assets into the output), not a Hermes code or config issue.
Fix belongs in the Hermes nix derivation's `postInstall` hook or the upstream
`pyproject.toml` `package_data`/`MANIFEST.in`.

Kanban CLI (`hermes kanban stats`, `hermes kanban list`) works independently of
the web dashboard plugin.

### Dashboard auth (basic_auth) in Hermes ≥2026.7.30

The new Hermes version reads `dashboard.basic_auth` from **config.yaml** (not
just env vars). The env vars `HERMES_DASHBOARD_BASIC_AUTH_USERNAME/PASSWORD`
are still honored as overrides but the plugin (`plugins.dashboard_auth.basic`)
must be importable. The systemd unit's `Environment=PYTHONPATH=...` was
overriding the nix wrapper's `site.addsitedir` calls, preventing plugin
discovery. Removing the `PYTHONPATH` line from the systemd unit lets the
nix wrapper handle module resolution correctly.

Config needed (if auth gate does engage, e.g. non-loopback Host):
```yaml
dashboard:
  basic_auth:
    username: cm
    password: <REDACTED>
    secret: <REDACTED>
```

Password hashing uses `hashlib.scrypt` (not sha256). The plugin accepts
plaintext `password:` and hashes it in-memory at load, or pre-computed
`password_hash:` in `scrypt$...` format.

If the unit was generated with `--host 0.0.0.0` (older nix-darwin config),
fix it:

```bash
ssh devbox 'sed -i "s/--host 0.0.0.0/--host 127.0.0.1/" ~/.config/systemd/user/hermes-serve.service && systemctl --user daemon-reload && systemctl --user restart hermes-serve.service'
```

## 502 fix (dashboard not running)

Nothing listening on 9119 on devbox. Check + restart:

```bash
ssh devbox 'systemctl --user status hermes-serve.service'
ssh devbox 'systemctl --user restart hermes-serve.service'
```

If a stale manual process holds the port, kill it first:

```bash
ssh devbox 'pkill -f "hermes dashboard"; sleep 2; systemctl --user restart hermes-serve.service'
```

## 404 from wrong tunnel ingress

If the tunnel was pointed at 8644 (gateway port) instead of 9119, the public
URL returns 404 from the gateway. Revert tunnel ingress to
`http://localhost:9119` via CF API:

```bash
curl -X PUT \
  -H "X-Auth-Email: $(himitsu read cloudflare-email)" \
  -H "X-Auth-Key: $(himitsu read cloudflare-global-api-token)" \
  -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/accounts/acb126dc2c4cf93764fa69d9bd55a3cf/cfd_tunnel/6a0b0a83-c9d2-4ea7-beac-2fd817f1e154/configurations" \
  --data '{"config":{"ingress":[{"service":"http://localhost:9119","hostname":"hermes.cm.xyz","originRequest":{"noTLSVerify":false,"httpHostHeader":"localhost:9119","disableChunkedEncoding":true}},{"service":"http_status:404"}],"warp-routing":{"enabled":false}}}'
```

## Verify

```bash
curl -sS -o /dev/null -w '%{http_code}' https://hermes.cm.xyz/  # expect 200
ssh devbox 'systemctl --user is-active hermes-serve.service'    # expect active
```
