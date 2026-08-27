# hermes.cm.xyz CF 502 — plugin.yaml packaging (2026-08-04)

## Observed

- Public: Cloudflare `HTTP/2 502`, body `error code: 502`, cert `*.cm.xyz`.
- `cloudflared` active on devbox; repeated:
  `Unable to reach the origin … dial tcp [::1]:9119: connection refused`
  `originService=http://localhost:9119`
- `hermes-serve` user unit: `activating (auto-restart)`, exit 1, counter 360+.
- Journal:

```text
Refusing to bind dashboard to 0.0.0.0 — the auth gate engages on
non-loopback binds, but no auth providers are registered.
```

- Unit already had:
  - `HERMES_DASHBOARD_BASIC_AUTH_USERNAME=cm`
  - `EnvironmentFile=…/hermes-dashboard.env` (password present, length ~20)
- Manual `register()` of `plugins.dashboard_auth.basic` **with same env** succeeded → env OK, discovery broken.
- Package plugins dir existed; `find … -name plugin.yaml | wc -l` → **0**.

## Hotfix

1. `~/.hermes/bundled-plugins-fix/dashboard_auth/{basic,nous,drain,self_hosted}/`
   - symlink `__init__.py` from store
   - write minimal `plugin.yaml` (`kind: backend`)
2. systemd drop-in:
   `~/.config/systemd/user/hermes-serve.service.d/bundled-plugins-fix.conf`
   → `Environment=HERMES_BUNDLED_PLUGINS=~/.hermes/bundled-plugins-fix`
3. `daemon-reload` + restart → `HERMES_DASHBOARD_READY port=9119`
4. Public: `/` 302 `/login`, `/api/status` 200 (`version` 0.19.1 / release 2026.7.30)

## Durable Nix

`~/darwin/homes/x86_64-linux/cm@devbox/default.nix`:

- `hermesBundledPluginsFix` runCommand overlay
- unit env `HERMES_BUNDLED_PLUGINS=${hermesBundledPluginsFix}`

Apply with Home Manager / rebuild on devbox when convenient. Live drop-in bridges until then.

## Notes

- Hermes listens `0.0.0.0:9119` (IPv4 only); cloudflared prefers `[::1]`. Prefer origin `http://127.0.0.1:9119` long-term.
- Same-day follow-up: gateway looked "stopped" and telegram had no adapter — same stripped-yaml package plus Nix argv0 liveness. See `gateway-nix-liveness.md`; do not dismiss `gateway_running: false` once the dashboard is back.
- Upstream basic plugin yaml shape: https://raw.githubusercontent.com/NousResearch/hermes-agent/main/plugins/dashboard_auth/basic/plugin.yaml
