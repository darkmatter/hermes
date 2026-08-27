# Dual-stack runbook (WARP + Tailscale)

Session-hardened notes for Cooper’s Mac Pro. Do not thrash clients.

## Bring-up (once)

1. Quit Tailscale app completely (`tailscale status` → stopped).
2. `warp-cli connect` — wait for `Connected` / healthy. **No retry loop.**
3. If Access apps say “authenticate via the warp client”, open browser once:
   `https://drkmttr.cloudflareaccess.com/cdn-cgi/access/refresh-identity`
4. Start Tailscale with DNS off, routes on:
   ```bash
   tailscale up --accept-dns=false --accept-routes
   ```
   If CLI demands full flag set: include current non-defaults or `--reset` carefully.
5. Smoke (≤5 probes total):
   ```bash
   curl -s https://www.cloudflare.com/cdn-cgi/trace | rg warp=
   curl -sI https://feed.cm.xyz/ | head -3
   tailscale ping 100.125.9.116
   dig +time=2 +tries=1 @100.100.100.100 <REDACTED>
   ```

## Tear-down preference

If unstable: disconnect WARP **or** stop Tailscale — not both flapping. TS-only is the stable mesh path.

## Zero Trust IDs (darkmatter account)

| Item | Value |
|---|---|
| Account | `acb126dc2c4cf93764fa69d9bd55a3cf` |
| Team domain | `drkmttr.cloudflareaccess.com` |
| Default device policy | `0198311b-8b9b-759a-903b-a360e6140bbd` |
| Onboarding profile (Cooper emails) | `43916455-ec90-400b-84a7-c493f12c334c` |
| Feed Access app | `c048f55f-b168-4b57-ab99-f346dcec337e` |
| Feed AUD | `5479b6bd476cdb2519a525a313d4dc76295056b105e629ca378790e1c7a205c3` |

Access API auth: himitsu `cloudflare-email` + `cloudflare-global-api-token`.

Custom profile endpoints use **singular** `devices/policy/{id}/fallback_domains` and `…/exclude` (plural `devices/policies/{id}` 404s).

## Name resolution matrix

| Name class | TS DNS on, WARP off | WARP on, TS accept-dns=false |
|---|---|---|
| `100.x` peer IP | yes | yes if TS up |
| `*.<REDACTED>` | MagicDNS / search | need fallback → `100.100.100.100` or dig @ that |
| `*.ts.net` | MagicDNS | same |
| `*.lan` / `*.internal` / `<REDACTED>` | split DNS → `100.105.82.38` (`ca`) | need WARP fallback **with dns_server** `100.105.82.38` |
| search `ca` → `<REDACTED>` | search domain `internal` | **no search domain** unless OS/WARP adds it — use FQDN |

## Panic postmortem (2026-08-02)

- Panic: `userspace watchdog timeout: no successful checkins from configd … in 180 seconds`
- Same window: large `configd-*.ips`, `cua-driver` CPU resource diag
- Trigger pattern: agent repeatedly toggling WARP + Tailscale DNS/routes + profile PUTs
- Lesson: **configd is the shared SCDynamicStore owner** — dual VPN churn can hang it and reboot the Mac even with 200GB RAM free (not a classic jetsam OOM)

## Pending Cooper decision (do not apply unsolicited)

Point WARP Local Domain Fallback:

- `lan`, `internal`, `dm` → `dns_server: ["100.105.82.38"]`
- keep `ts.net` / `<REDACTED>` → `100.100.100.100`

Confirm `ca` (`100.105.82.38`) is reachable over TS before relying on it under WARP.
