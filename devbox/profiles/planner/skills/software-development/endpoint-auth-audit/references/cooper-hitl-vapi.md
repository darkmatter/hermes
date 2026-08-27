# ask-cooper.cm.xyz `/vapi/tools` (2026-08-15)

## Finding

**No application auth.** Public unauthenticated `POST` is accepted and handled by the HITL server.

## Evidence

| Request | Result |
|---------|--------|
| `GET /vapi/tools` | `404` `{"error":"not found"}` — no `WWW-Authenticate`, no CF Access redirect |
| `POST /vapi/tools` `{}` | `200` `{"results":[]}` |
| `POST` Vapi tool-calls, no creds | `200` `{"results":[{"toolCallId":"x","result":"Unknown tool ping; ignored by HITL server."}]}` |
| Same with wrong `Authorization: Bearer <REDACTED> | still `200` / processed |

Realistic no-auth probe body:

```json
{
  "message": {
    "type": "tool-calls",
    "toolCallList": [
      {"id": "x", "name": "ping", "parameters": {}}
    ]
  }
}
```

## Routing

From `~/machines/modules~/bb-hook.nix` Cloudflare Tunnel ingress:

- `ask-cooper.cm.xyz` → `http://127.0.0.1:8788`
- `decide.cm.xyz` → `http://127.0.0.1:8789` (same tunnel; different local port)
- `bb-hook.cm.xyz` → bb webhook server (has its own secret path)

Launcher notes elsewhere mention `run-ask-cooper-hitl.sh` + himitsu for Slack bot tokens — that is process env for the HITL *bot*, not HTTP auth on `/vapi/tools`.

## Blast radius / fix

- Unknown tool names are ignored (safe for probing).
- Any *registered* Vapi tool on this server would be invokable by anyone who can POST the public URL.
- Hardening: enforce Vapi shared secret (or equivalent header) before handling; and/or Cloudflare Access on the hostname; do not rely on GET 404 obscurity.
