# Gateway healthy but dashboard says stopped (Nix, 2026-08-04)

## Stack observed on devbox

1. `hermes-gateway.service` **active** for hours.
2. Log after restart: `No adapter available for telegram` (post package that stripped all `plugin.yaml`).
3. After platform overlay: telegram **connected**, webhook on `:8644`, `gateway_state.json` correct.
4. Still: `/api/status` → `gateway_running: false`, `overall: degraded`, `components.platforms.connected: 0`.

## Adapter path (class D1)

- Store: `…/site-packages/plugins/platforms/telegram/{__init__,adapter}.py` present; **no** `plugin.yaml`.
- Discovery scans only directories with `plugin.yaml` (`kind: platform`).
- Overlay: symlink store files + upstream-shaped yaml (`name: telegram-platform`).
- Env on gateway unit: `HERMES_BUNDLED_PLUGINS=~/.hermes/bundled-plugins-fix` (or Nix derivation).
- Success log markers: `✓ telegram connected`, `Gateway running with N platform(s)`, `set_my_commands OK`.

Upstream telegram yaml:
https://raw.githubusercontent.com/NousResearch/hermes-agent/main/plugins/platforms/telegram/plugin.yaml

## Liveness path (class D2)

`_check_gateway_running` → `get_runtime_status_running_pid` → `_record_matches_live_gateway_pid` → `looks_like_gateway_runtime_command_line`.

Live Nix cmdline **before** fix:

```text
python3.14 /nix/store/…/bin/.hermes-wrapped gateway run --replace
```

`_gateway_command_subcommand` requires a token basename in `{hermes, hermes.exe}` (or `hermes_cli.main`). `.hermes-wrapped` → `None` → not a gateway → dashboard false.

PID file `~/.hermes/gateway.pid` may be missing; fallback still fails the cmdline check even when `start_time` matches `/proc/<pid>/stat`.

**Launcher that works:**

```sh
#!/bin/sh
exec -a hermes "$PYTHON" "$WRAPPED" gateway run --replace
```

Resulting cmdline:

```text
hermes /nix/store/…/bin/.hermes-wrapped gateway run --replace
```

Then `/api/status` reports `gateway_running: true`, platforms populated, `overall: ok`.

Unit PATH on NixOS may lack `bash` — use `#!/bin/sh` and absolute paths (status 127 `env: 'bash': No such file` if shebang is `env bash`).

## Darwin durable wiring

`~/darwin/modules~

- `hermesBundledPluginsFix` — dashboard_auth + platforms overlays
- `hermesGatewayRunner` — `writeShellScript` with `exec -a hermes`
- `hermes-gateway` unit: `ExecStart=${hermesGatewayRunner}`, `HERMES_BUNDLED_PLUGINS=…`

Live drop-ins until Home Manager switch:

- `~/.config/systemd/user/hermes-gateway.service.d/bundled-plugins-fix.conf`
- `~/.local/bin/hermes-gateway-run`

## Verify matrix

| Check | Expect |
|---|---|
| `systemctl --user is-active hermes-gateway` | active |
| `tr '\\0' ' ' </proc/$pid/cmdline` | starts with `hermes ` |
| `gateway_state.json` platforms | telegram+webhook `connected` |
| local `/api/status` | `gateway_running: true`, `overall: ok` |
| public `/api/status` (curl + UA) | same |

Do not use bare `urllib` against the public host without a browser UA — Cloudflare may 403.
