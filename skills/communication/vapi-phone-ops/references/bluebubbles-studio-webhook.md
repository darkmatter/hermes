# BlueBubbles Studio + bb-hook.cm.xyz

## Topology

```
iMessage → Mac Studio BB (:1234, private_api often true)
                │
                │  Cloudflare quick tunnel (EPHEMERAL)
                │  himitsu hermes/bb-studio-url
                ▼
         BB registers webhook ──POST──► https://bb-hook.cm.xyz/bb/webhook?secret=…
                                                │
                     CF named tunnel hermes-pro-webhooks (STABLE DNS)
                                                │
                                                ▼
                              Mac Pro :8790 bb_webhook_server.py
                                                │
                                                ▼
                                    /tmp/bb-inbox + GET /messages
```

## Stable pieces (Pro)

| Item | Path / value |
|---|---|
| DNS | `bb-hook.cm.xyz` (zone cm.xyz, proxied CNAME → tunnel) |
| Tunnel id | `cec4b29a-b3aa-4dd2-abe7-f9c7d3c0fba2` (`hermes-pro-webhooks`) |
| Creds | `~/.cloudflared/cec4b29a-b3aa-4dd2-abe7-f9c7d3c0fba2.json` |
| Config | `~/.cloudflared/hermes-pro-webhooks-config.yml` → `http://127.0.0.1:8790` |
| Server | `~/.hermes/skills/communication/communications/scripts/bb_webhook_server.py` |
| Secret | `~/.hermes/bb/webhook-secret` / `himitsu hermes/bb-hook-secret` |
| Meta | `~/.hermes/bb/config.json` |

## Run after reboot

```bash
export BB_HOOK_SECRET=<REDACTED>
python3 ~/.hermes/skills/communication/communications/scripts/bb_webhook_server.py &
cloudflared tunnel --config ~/.cloudflared/hermes-pro-webhooks-config.yml run &

curl -sS "https://bb-hook.cm.xyz/health?secret=$BB_HOOK_SECRET"
```

## Studio API auth

Password = <REDACTED>

```bash
PASS=$(sqlite3 "$HOME/Library/Application Support/bluebubbles-server/config.db" \
  "SELECT value FROM config WHERE name='password'")
STUDIO=$(himitsu read hermes/bb-studio-url)  # or current trycloudflare URL

curl -sS "$STUDIO/api/v1/server/info?password=$PASS" | python3 -m json.tool
```

Poll receive (works without webhook):

```bash
curl -sS -X POST "$STUDIO/api/v1/message/query?password=$PASS" \
  -H 'Content-Type: application/json' \
  -d '{"limit":20,"sort":"DESC","with":["handle"]}'
```

Send (prefer apple-script if helper_connected false):

```json
{
  "chatGuid": "iMessage;-;+1XXXXXXXXXX",
  "message": "text here",
  "method": "apple-script",
  "tempGuid": "<uuid>"
}
```

POST `$STUDIO/api/v1/message/text?password=…`

## Register / refresh webhook on Studio

`bb-hook.cm.xyz` is stable. Only re-register when Studio loses webhook config or secret rotates:

```bash
SEC=$(cat ~/.hermes/bb/webhook-secret)
curl -sS -X POST "$STUDIO/api/v1/webhook?password=$PASS" \
  -H 'Content-Type: application/json' \
  -d "{\"url\":\"https://bb-hook.cm.xyz/bb/webhook?secret=$SEC\",\"events\":[\"new-message\",\"updated-message\",\"message-send-error\",\"chat-read-status-changed\",\"typing-indicator\"]}"
```

Events may also be `["*"]`. List: `GET …/webhook`. Delete: `DELETE …/webhook/{id}`.

## Inbox for agents

```bash
SEC=$(cat ~/.hermes/bb/webhook-secret)
curl -sS "https://bb-hook.cm.xyz/messages?secret=$SEC&limit=30"
curl -sS "https://bb-hook.cm.xyz/inbox?secret=$SEC&limit=30"
```

## Pitfalls

- Studio **quick tunnel URL** changes when BB/cloudflared restarts — update `himitsu hermes/bb-studio-url` and any live clients; webhook **target** remains bb-hook.cm.xyz.
- Mac Pro local BB `:1234` ≠ Studio; don't assume helper/private-api parity (Tahoe Pro often helper false).
- Webhook requires `events` field or 400.
- Secret goes in query string because BB webhook POST cannot easily set custom headers.
- Tailscale Studio IP `100.111.149.47` is reachable but **:1234 not exposed** directly; use cloudflared URL or enable LAN bind intentionally.
