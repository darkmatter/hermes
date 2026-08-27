# BlueBubbles hold-status + inbound (Studio)

## Stable endpoints

| Role | URL |
|---|---|
| Studio BB HTTP API | `https://bb-api.cm.xyz` (named CF tunnel `hermes-studio-bb`) |
| Pro webhook receiver | `https://bb-hook.cm.xyz/bb/webhook?secret=…` |
| Inbox | `GET https://bb-hook.cm.xyz/messages?secret=…` |
| himitsu | `hermes/bb-api-url`, `hermes/bb-hook-url`, `hermes/bb-hook-secret`, `hermes/bb-studio-url` |
| Secret file | `~/.hermes/bb/webhook-secret` |
| Meta | `~/.hermes/bb/config.json` |

Password for Studio API: same BB server password as local Pro config DB:

```bash
PASS=$(sqlite3 "$HOME/Library/Application Support/bluebubbles-server/config.db" \
  "SELECT value FROM config WHERE name='password'")
curl -sS "https://bb-api.cm.xyz/api/v1/server/info?password=$PASS"
```

## Why not Twilio SMS

Outbound SMS from the Vapi/Twilio long code to (206) fails **error 30034** (US A2P 10DLC / unregistered). Use **iMessage via Studio BB** for handoff hold updates.

## Send status (prefer API)

```bash
# Prefers Private API when helper up; else apple-script path on Studio
BASE=https://bb-api.cm.xyz
# POST /api/v1/message/text  with address + message (+ tempGuid if required by version)
```

## Inbound

- Poll: `POST $BASE/api/v1/message/query`
- Push: Studio webhook id → `https://bb-hook.cm.xyz/bb/webhook?secret=…`
  events: `new-message`, `updated-message`, `message-send-error`, `chat-read-status-changed`, `typing-indicator`

## Darwin durability

- Modules in `~/darwin`: `programs.bb-hook` (Mac Pro), `programs.bb-studio` (Studio)
- Manual LaunchAgents work without sudo: `dev.hermes.bb-hook`, `dev.hermes.bb-hook-tunnel`, `dev.hermes.bb-api-tunnel`
- Studio cloudflared often from BB app bundle:
  `/Applications/BlueBubbles.app/Contents/Resources/appResources/macos/daemons/cloudflare/arm64/cloudflared`
- Quote store paths in nix `ProgramArguments`: `"${cloudflaredBin}"` not bare `${cloudflaredBin}`

## Flake host attr

`~/.config/darwin/host` and `rebuild.sh` must use **scutil hostname**:

- Pro → `Coopers-Mac-Pro`
- Studio → `Coopers-Mac-Studio`

Not host ids `macpro` / `coopers-mac-studio`.

## GitHub 401 on `darwin-rebuild switch`

If build OK but switch fails downloading `github:nlewo/comin/...` with
`Deprecated authentication method`:

- Studio `~/.netrc` had `login oauth` + `github_pat_*` → GitHub treats as **password**, 401s archive
- Fix: `machine github.com` / `api.github.com` with `login x-access-token` + working `ghp_` (himitsu `github/darkmatter-pat`)
- Also refresh `~/.config/nix/access-tokens.conf`: `access-tokens = github.com=<PAT>`
- Unauthenticated curl of public archives works; **stale netrc is worse than no auth**
