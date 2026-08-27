---
name: bluebubbles-studio
description: Operate Cooper's agent-dedicated BlueBubbles on Mac Studio — stable API (bb-api.cm.xyz), inbound webhooks (bb-hook.cm.xyz), send/receive iMessage, LaunchAgents, and when to avoid Twilio SMS.
version: 1.2.3
---

# BlueBubbles Studio (agent iMessage)


## iMessage identity (critical)

**Always send as Studio** `cooperton42391@gmail.com` via Studio BB (prefer **SSH → Studio localhost:1234**, fallback `https://bb-api.cm.xyz`).

**Never** use Mac Pro local Messages / osascript (`koutaroum@icloud.com`) for Hermes→Cooper pings — that path messages “itself” / self-chat. User correction this session: HITL must not mail from the Pro iMessage account.

### Recipient selection (user correction)
- Default **handoff / “text 206” / ask Telavaya side for ticket digits:** `+12069542027`
- Do **not** default to Cooper cell `+13109897067` unless Cooper asked for 310 or HITL is intentionally on that phone
- Session regret: ticket-number ask first went to 310; Cooper: “you sent that to me - i meant 206”
- When asking for AA **13-digit ticket/credit**: say digits may have been **misheard on the call**, need cancel email / e-ticket `001…` — not “we have no number” if a suspect STT candidate was tried and failed on aa.com

HITL (`ask_cooper_server.py`) must:
1. `GET bb-api …/server/info` and refuse unless `detected_imessage` / `detected_icloud` contains `cooperton42391@gmail.com`
2. Send only BB REST (`message` + `tempGuid`; try `private-api` then `apple-script`; no fake `auto` when invalid)
3. **Never** fall back to osascript on the Pro even if BB send times out

If `helper_connected: false`: private-api errors with helper-not-connected; **apple-script on Studio localhost often still succeeds** (session: HTTP 200 `Message sent!`). Prefer:
```bash
# on Studio via SSH — avoid CF flake for sends when possible
curl -sS -X POST "http://127.0.0.1:1234/api/v1/message/text?password=$PASS" \
  -H 'Content-Type: application/json' \
  -d '{"chatGuid":"any;-;+12069542027","tempGuid":"temp-…","message":"…","method":"apple-script"}'
```
Never fall back to Pro Messages. Prefer Slack HITL if BB fully dead.

### Is SMS a Hermes channel?
**No full SMS agent home.** `platforms.bluebubbles.enabled` is **iMessage/BB transport** for status + HITL replies (bb-hook inbox), not Twilio SMS chat. Green-bubble carrier SMS to the Apple ID is unreliable unless SMS relay is explicitly set up. Twilio outbound for hold pings → **30034** — use BB iMessage instead.

### Inbound for HITL replies
bb-hook inbox (`/messages`) — allowlist `+13109897067` / `+12069542027`. One open ask → any reply text counts; multiple open → include `[req_id]`.

### Shared tunnel hostnames on Pro
Pro named CF tunnel also routes **`ask-cooper.cm.xyz` → `:8788`** (HITL) alongside `bb-hook.cm.xyz` → `:8790`. Prefer multi-host `~/.cloudflared/bb-hook-tunnel.yml` over trycloudflare URLs.

## Endpoints (stable)

| Role | URL |
|---|---|
| Studio BB HTTP API | `https://bb-api.cm.xyz` |
| Inbound webhook (Pro) | `https://bb-hook.cm.xyz/bb/webhook?secret=…` |
| Inbox | `https://bb-hook.cm.xyz/messages?secret=…` |
| Health | `https://bb-hook.cm.xyz/health?secret=…` |

Secrets / meta:

- `~/.hermes/bb/webhook-secret` · himitsu `hermes/bb-hook-secret`
- himitsu `hermes/bb-api-url`, `hermes/bb-hook-url`, `hermes/bb-studio-url`
- `~/.hermes/bb/config.json`

Studio iMessage account: **cooperton42391@gmail.com** (confirm on server info).

## Auth for BB API

Same server password pattern as local BB (often mirrors Pro BB config DB):

```bash
PASS=$(sqlite3 "$HOME/Library/Application Support/bluebubbles-server/config.db" \
  "SELECT value FROM config WHERE name='password'")
curl -sS "https://bb-api.cm.xyz/api/v1/server/info?password=$PASS"
```

Send (private-api preferred; Studio often has helper issues — check `private_api` / `helper_connected` on server info). Prefer BB REST with `tempGuid` for apple-script path when private-api is false.

## Receive

1. **Webhook push (preferred):** Studio registers webhook → `bb-hook.cm.xyz`
   events: `new-message`, `updated-message`, `message-send-error`, `chat-read-status-changed`, `typing-indicator`
2. **Poll:** `POST /api/v1/message/query` on `bb-api.cm.xyz`
3. Pro receiver: `files/hermes/bb/bb_webhook_server.py` · LaunchAgent `dev.hermes.bb-hook` + tunnel `dev.hermes.bb-hook-tunnel`

## Durability (darwin)

- Pro: `programs.bb-hook.enable` → webhook + named CF tunnel `hermes-pro-webhooks` · DNS `bb-hook.cm.xyz`
- Studio: `programs.bb-studio.enable` → keep BB up + named tunnel `hermes-studio-bb` · DNS `bb-api.cm.xyz`
- Tunnel creds live **outside git** under `~/.cloudflared/<tunnel-id>.json`
- Studio may lack brew `cloudflared` — resolve via BB app bundle:
  `/Applications/BlueBubbles.app/.../daemons/cloudflare/arm64/cloudflared`
- **Nix pitfall:** in launchd `ProgramArguments`, quote store paths: `"${cloudflaredBin}"` not bare `${cloudflaredBin}`

## Flake host attrs

`~/.config/darwin/host` and `rebuild.sh` use **hostname**, not host id:

| Machine | Attr |
|---|---|
| Mac Studio | `Coopers-Mac-Studio` |
| Mac Pro | `Coopers-Mac-Pro` |

Not `coopers-mac-studio` / `macpro`.

## When rebuilding fails with GitHub 401

User `darwin-rebuild build` OK but `sudo … switch` 401 on `comin`/github archives:

- Root uses `!include github-token.conf` → `/run/agenix/github_token` (missing until first successful switch).
- Stale `~/.netrc` `login oauth` + `github_pat_*` → GitHub "Deprecated authentication method".
- Fix netrc: `login x-access-token` + working `ghp_` PAT.
- `./rebuild.sh` injects `NIX_CONFIG=access-tokens = github.com=…` under sudo (agenix → user conf → himitsu).

## Do not use for status

- Twilio SMS from Vapi long code → often **30034** (A2P 10DLC). Use BB iMessage for +1206… and Cooper hold updates.
- HITL public hostname: `https://ask-cooper.cm.xyz` (Pro `:8788` behind same style of named tunnel as bb-hook).

## Manual LaunchAgents (no sudo HM)

If Home Manager agents missing, user LaunchAgents work:

- Pro: `dev.hermes.bb-hook`, `dev.hermes.bb-hook-tunnel` (and multi-host tunnel for **ask-cooper.cm.xyz** if YAML has both)
- Studio: `dev.hermes.bb-api-tunnel` (BB app itself often via official `com.bluebubbles.server`)

Logs: `~/Library/Logs/bb-*.{log,err}`

When HM tunnel plist keeps overwriting multi-host YAML, run a **user** KeepAlive agent (`dev.hermes.bb-hook-tunnel-multi` style) pointing at `~/.cloudflared/bb-hook-tunnel.yml` with both `bb-hook` + `ask-cooper` ingress until sudo rebuild lands.

## References

- `references/imessage-vs-twilio.md` — why not Twilio SMS (30034)
- `references/darwin-host-and-rebuild.md` — flake host attrs, sudo 401 / netrc, launchd quoting
