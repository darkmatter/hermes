# Durable BlueBubbles + cm.xyz (darwin)

Repo: `czxtm/machines` (`~/darwin`).

## Modules

| Module | Host | What |
|---|---|---|
| `programs.bb-hook` | Mac Pro (`cm@macpro` / hostname `Coopers-Mac-Pro`) | `bb_webhook_server.py` `:8790` + CF tunnel `hermes-pro-webhooks` → `bb-hook.cm.xyz` |
| `programs.bb-studio` | Studio (`coopermaruyama@coopers-mac-studio`) | Keep BlueBubbles up + tunnel `hermes-studio-bb` → `bb-api.cm.xyz` |

Files: `modules~/bb-{hook,studio}.nix`, script `files/hermes/bb/bb_webhook_server.py`.

## Secrets (not in git)

| Path | Purpose |
|---|---|
| Pro `~/.cloudflared/cec4b29a-….json` | hook tunnel creds |
| Studio `~/.cloudflared/cbb896c0-….json` | api tunnel creds |
| Pro `~/.hermes/bb/webhook-secret` | query secret on webhook URL |
| himitsu `hermes/bb-hook-secret`, `hermes/bb-api-url`, `hermes/bb-hook-url`, `hermes/bb-studio-url` | agent lookup |

## Named tunnels / DNS

- `bb-hook.cm.xyz` → pro webhook receiver
- `bb-api.cm.xyz` → studio BB `:1234`
- Create/edit DNS: CF token `himitsu cloudflare/token-edit-zone` zone `cm.xyz`

## Nix pitfalls

- In launchd `ProgramArguments`, quote script paths: `"${cloudflaredBin}"` not bare `${cloudflaredBin}` (unquoted store path becomes multiple list items → rebuild error near `"tunnel"`).
- Studio may lack brew `cloudflared` — resolve via BlueBubbles.app bundled arm64 binary.
- Flake darwin key is **hostname** (`Coopers-Mac-Pro`, `Coopers-Mac-Studio`), not hostId alone. Set `~/.config/darwin/host` accordingly.
- `darwin-rebuild switch` needs root; user LaunchAgents can keep services up without sudo as interim.

## Interim LaunchAgents (if HM not switched)

Pro: `dev.hermes.bb-hook`, `dev.hermes.bb-hook-tunnel`
Studio: `dev.hermes.bb-api-tunnel` (+ official `com.bluebubbles.server`)

## Webhook register / health

```bash
PASS=$(sqlite3 "$HOME/Library/Application Support/bluebubbles-server/config.db" \
  "SELECT value FROM config WHERE name='password'")
SEC=$(cat ~/.hermes/bb/webhook-secret)
curl -sS "https://bb-api.cm.xyz/api/v1/server/info?password=$PASS"
curl -sS "https://bb-hook.cm.xyz/health?secret=$SEC"
# POST /api/v1/webhook on Studio: url=https://bb-hook.cm.xyz/bb/webhook?secret=$SEC
```

Prefer **bb-api.cm.xyz** over BB-app quick tunnels (ephemeral trycloudflare hostnames).
