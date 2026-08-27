---
name: himitsu
description: Age-based secrets manager (github:darkmatter/himitsu). Read, write, search, and exec secrets.
version: 0.1.0
triggers:
  - himitsu
  - secret
  - secrets
  - credential
  - credentials
---

# Himitsu — Secrets Management Skill

## Overview

Himitsu is an age-encrypted secrets store with git-backed sync, project-scoped configs, and 1Password/SOPS import.

**Binary:** `himitsu` (installed via nix profile)
**Store location:** `~/.local/share/himitsu/stores/` (age-encrypted, git-backed)

## Core Commands

### List secrets
```bash
himitsu ls                    # Top-level (24 items per page by default)
himitsu ls --offset 24        # Next page
himitsu ls -R                 # Recursive (all depths)
himitsu ls -d 3               # Depth 3
himitsu ls google/ -R         # List everything under google/
```

### Search secrets
```bash
himitsu search <query>        # Fuzzy search across all stores
himitsu search google         # Find anything matching "google"
himitsu search --tag pci      # Filter by tag
```

### Read a secret
```bash
himitsu get <path>            # Display secret with metadata
himitsu read <path>           # Plaintext only (scripting-friendly)
```

### Write a secret
```bash
himitsu set <path> <value>                    # Set with value
himitsu set <path> <value> --description "..." # With description
himitsu set <path> <value> --tag prod --tag rotate-q1  # With tags
himitsu set <path> <value> --expires-at 30d    # Expiration reminder
himitsu set <path> <value> --env-key API_KEY   # Default env var name
himitsu write <path> <value>                  # No decoration (scripting)
himitsu write <path> <value> --no-push        # Skip git commit+push
echo "secret" | himitsu write <path>          # From stdin
```

### Execute with secrets
```bash
himitsu exec <ref> -- <command>              # Inject matching secrets as env vars
himitsu exec prod/* -- -- python app.py      # Glob: all secrets under prod/
himitsu exec -i prod/* -- -- python app.py   # Clean env (only secrets + baseline)
himitsu exec --tag prod -- -- python app.py  # Filter by tag
```

### Import secrets
```bash
himitsu import --op op://vault/item/field <path>    # Single 1Password field
himitsu import --op op://vault/item <path>           # All fields from 1Password item
himitsu import --op op://vault                       # Entire 1Password vault
himitsu import --sops <file> <path>                   # SOPS-encrypted file
himitsu import --op op://vault --to prod/stripe       # Custom target prefix
himitsu import --op op://vault --dry-run              # Preview without writing
himitsu import --op op://vault --no-push              # Batch import without pushes
```

### Other useful commands
```bash
himitsu tag <path> add <tag>          # Add a tag
himitsu tag <path> rm <tag>           # Remove a tag
himitsu tag <path> list               # List tags on a secret
himitsu sync                          # Pull from remote, rekey drifted secrets
himitsu rekey                         # Re-encrypt for current recipients
himitsu check                         # Verify stores up to date with remotes
himitsu generate                      # Generate SOPS-encrypted output from env defs
himitsu export <glob>                 # Export secrets as SOPS-encrypted file
himitsu context                       # Manage active store context
```

## Known Secret Paths

These are the secrets currently in the store (as of 2025-07). Use `himitsu ls -R` for the full current list.

| Path prefix | Contents |
|---|---|
| `argocd/` | ArgoCD credentials |
| `authentik/` | Authentik SSO |
| `aws-sandbox-*` | AWS sandbox access keys |
| `beads/` | Beads (issue tracking) |
| `composio-api-key` | Composio API key (integrations platform) |
| `composio-api-key` | Composio tool-router API key (ak_* prefix) |
| `cf-*` / `cloudflare*` | Cloudflare tokens and account info |
| `cloudflare/r2-team-drive/*` | Cloudflare R2 "team-drive" bucket (access-key-id, secret-access-key, api-token) |
| `cloudflare/r2-lago/*` | Cloudflare R2 "lago" bucket (access-key-id, secret-access-key, bucket name, endpoint) |
| `cloudflare-account-id` | Cloudflare account ID (needed for R2 endpoint: `https://<id>.r2.cloudflarestorage.com`) |
| `cloudflare-account-id-darkmatter` | Darkmatter-specific Cloudflare account ID |
| `ci-deploy-ssh-*` | CI deploy SSH keypair |
| `common/` | Shared/common secrets |
| `darkmatter-sso/` | Darkmatter SSO |
| `darkmatter-tls/` | TLS certs |
| `dev/` | Dev environment secrets |
| `dune-api-key` | Dune Analytics |
| `elevenlabs-api-key` | ElevenLabs TTS |
| `github/` | GitHub tokens |
| `google/` | Google OAuth and API credentials |
| `hetzner-api-key` | Hetzner cloud |
| `hugging-face-token` | Hugging Face |
| `kimi-api-key` | Kimi AI |
| `linear-api-key` | Linear project management |
| `litellm-api-key` | LiteLLM proxy |
| `macweb/` | MacWeb |
| `neon-api-key` | Neon database |
| `npm-access-token` | npm registry |
| `obsidian-license-key` | Obsidian |
| `personal/` | Personal secrets |
| `planetscale/` | PlanetScale database |
| `pypi-api-token` | PyPI |
| `resend/` | Resend email |
| `slack/` | Slack tokens |
| `spotproxy/` | SpotProxy |
| `tailscale/` | Tailscale |
| `team/` | Team shared secrets |
| `twitter/` | Twitter/X OAuth (client-id, client-secret, access-token, refresh-token) |
| `unsplash/` | Unsplash API |
| `upstash-api-key` | Upstash Redis |
| `vast-ai` | Vast.ai GPU |
| `verda/` | Verda |
| `vsce-personal-access-token` | VS Code Extension marketplace |

### Key secrets for common tasks

- **Google OAuth (Drive):** `google/oauth-client-secret-darkmatter-drive.json`
  - Contains `client_id`, `client_secret`, `project_id` (darkmatter-471021)
  - OAuth type: `installed` (desktop/app), redirect: `http://localhost`
  - See `references/google-oauth.md` for full field reference and setup notes
- **Twitter/X OAuth:** `twitter/oauth-client-id`, `twitter/oauth-client-secret`, `twitter/oauth-access-token`, `twitter/oauth-refresh-token`

## Pitfalls

- `himitsu ls` paginates at 24 items — always check for `--offset` to see more
- `himitsu ls google/` fails with "empty path component" — use `himitsu search google` instead for directory-style queries
- `himitsu ls cloudflare/r2-team-drive/` also fails with empty path component — same workaround: `himitsu search r2-team-drive`
- `himitsu get` shows metadata; `himitsu read` gives plaintext only (prefer `read` for scripting)
- `himitsu set` auto-commits and pushes to git by default; use `--no-push` for batch operations
- `himitsu exec` with `-i` (clean env) is essential when you don't want host env vars leaking into the child process
- Path components use `/` separators (e.g. `prod/API_KEY`)
- Tags are `[A-Za-z0-9_.-]+`, 1-64 chars, case-sensitive

## Related: gog CLI

**gog** — Google workspace CLI for Gmail/Calendar/Drive/etc. Auth'd as `cooper@darkmatter.io`. See the `gog` skill for full usage. The OAuth client secret lives here in himitsu: `google/oauth-client-secret-darkmatter-drive.json`
