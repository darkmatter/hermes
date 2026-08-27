# Public Hermes dashboard is not this skill

Studio/macOS local Hermes+CuaDriver lives here.

**Public HTTPS dashboard** (`hermes.cm.xyz` via cloudflared on Linux **devbox**,
`hermes-serve` on `:9119`, basic/OAuth auth plugins) is a different class of
work. Load:

- skill **`hermes-dashboard-ops`**
- `references/cf-502-plugin-yaml.md` (2026-08-04 CF 502: Nix package stripped
  all `plugin.yaml` → no auth providers → bind refused → tunnel origin down)

Do not diagnose public 502s as Studio MCP or agenix failures without first
checking `systemctl --user status hermes-serve` on devbox.
