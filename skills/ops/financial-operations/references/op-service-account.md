# 1Password service account (agents)

## Hard rules
- **Only** `~/.local/bin/op` (wrapper). Injects SA token from `himitsu read op-service-account/token` → **drkmttr.1password.com**.
- **Never** bare brew/nix `op` (`/opt/homebrew/bin/op`, `/etc/profiles/per-user/cm/bin/op`) — missing SA → biometric/GUI prompt.
- **Never** `/run/agenix/op-service-account-token` (personal **my.1password.com**).
- **Never** `op signin` / desktop unlock / biometric.
- **Always** `--vault` on `op item …` (`cm` | `cooper` | `dev`). Wrapper refuses without it.
- Timeout fail-closed: `OP_TIMEOUT` (default 5s); exit 124 = failure, not empty success.

## Catalog (parent agents)
Name-only inventory (no secrets): `~/.hermes/op-sa-catalog.json`

```bash
export PATH="$HOME/.local/bin:$PATH"
for v in cm cooper dev; do
  OP_TIMEOUT=45 op item list --vault "$v" --format=json > "/tmp/op-$v.json"
done
# rebuild catalog JSON with id/category/title only → ~/.hermes/op-sa-catalog.json
```

- **Parent** refreshes the catalog once per session when payment/secret work starts.
- **Children/subagents** read the catalog; do not thrash `op item list`.
- **Missing item:** stop. Ask Cooper to move/copy into `cm`/`cooper`/`dev`. Do not fall back to personal vaults.

## Standing IDs (drkmttr)
| Item | Vault | Id / title |
|---|---|---|
| Amex Platinum (default pay) | cm | `nj33napkeiybo5o4fezookdb4i` |
| Coinbase One (only if user picks) | cm | `p2yhadwwld4fpxilkw6w4hhvwa` |
| Brex card metadata | cm | title `Brex` (PAN still via Brex API when needed) |
| BofA login | cm | title `secure.bankofamerica.com` |
| Vapi private key item | dev | title `vapi` field `credential` |

## Common agent mistakes
- Calling real `op` because PATH put nix/homebrew ahead of `~/.local/bin`.
- `op item list` without `--vault` (wrapper now hard-refuses).
- Documenting/using agenix token as “preferred” (wrong account).
- Subagents each re-listing vaults and timing into interactive auth.
