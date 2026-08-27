# Vessel MCP over Tailscale (fleet notes)

## Identity

- Product: **Vessel** browser MCP (user Chrome profile)
- Default listen: Mac `127.0.0.1:3100`
- HTTP path: **`/mcp`** (streamable HTTP)
- Auth: `Authorization: Bearer <REDACTED>
- Unauthed probe body: `{"error":"Unauthorized — missing or invalid bearer <REDACTED>"}`
- Token file (Mac only): `~/.config/vessel/mcp-auth.json`
  Fields used in practice: `endpoint`, `token`, `pid`

## Fleet wiring that worked in discovery

1. Mac runs Vessel → loopback `:3100`
2. Mac opens reverse tunnel into hub:
   ```bash
   ssh -N -o ExitOnForwardFailure=yes \
     -R 127.0.0.1:3100:127.0.0.1:3100 \
     cm@<REDACTED>
   ```
3. On hub, `ss` shows `127.0.0.1:3100` LISTEN with **no local process PID** (sshd remote-forward)
4. Hermes registers:
   ```bash
   hermes mcp add vessel --url http://127.0.0.1:3100/mcp --auth header
   ```
5. Token provisioning: scp Mac auth JSON →
   `/var/lib/hermes/.hermes/credentials/vessel-mcp-auth.json`
   then load into profile `.env` as `MCP_VESSEL_TOKEN` (or CLI password prompt)

## What failed / avoid

- Direct `curl http://pro:3100` / MBP / Studio while MCP is loopback-only → connection refused
- Hub `ssh coopermaruyama@coopers-mac-*` / `cooper@pro` → **Permission denied (publickey)**
  (hub ed25519 fp `YfDJ…` not authorized on Darwin; same class of failure as `cua-driver` stdio MCP)
- Token not in himitsu store under common names; not in mutagen `git`/`omp` sync roots

## Prior art on this machine

- OMP skills already document Vessel auth path:
  - `~/.omp/agent/managed-skills/argocd-*-sso-cookie-triage/SKILL.md`
- Glean session notes under `~/git/darkmatter/glean/knowledge/notes/sessions/` show successful Vessel tool use **from a Mac-local agent** reading `mcp-auth.json` directly

## Hermes config already present (separate path)

```yaml
mcp_servers:
  cua-driver:
    command: ssh
    args: [..., coopermaruyama@coopers-mac-studio, .../cua-driver, mcp]
```

That is **Studio computer-use / cua**, not Vessel. Treat Vessel HTTP reverse-tunnel as the browser-MCP path when user says `:3100` / Vessel.

## Wire helper

If present: `~/.hermes/scripts/wire-vessel-mcp.sh`
Looks for credentials under `~/.hermes/credentials/vessel-mcp-auth.json` (and a few drop paths), probes initialize, writes `mcp_servers.vessel`.
