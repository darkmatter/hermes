# Fresh Auth Setup (no pre-existing config)

Steps to auth gog from a clean state when `~/.config/gogcli/config.json` doesn't exist yet.

## 1. Create the config

```bash
mkdir -p ~/.config/gogcli
```

Write `config.json` pointing at the account and the OAuth client from himitsu:

```json
{
  "accounts": {
    "default": "cooper@darkmatter.io"
  },
  "client": {
    "client_id": "<from-himitsu>",
    "client_secret": "<REDACTED>",
    "project_id": "<from-himitsu>",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  },
  "credentials_dir": "~/.local/share/gogcli"
}
```

## 2. Store OAuth client secret

```bash
mkdir -p ~/.local/share/gogcli
himitsu read google/oauth-client-secret-darkmatter-drive.json > ~/.local/share/gogcli/credentials.json

GOG_KEYRING_PASSWORD=<REDACTED>
export GOG_KEYRING_PASSWORD
gog auth credentials ~/.local/share/gogcli/credentials.json
```

The `GOG_KEYRING_PASSWORD` env var is **required** in non-interactive sessions — without it gog's keyring backend prompts for a TTY password and fails.

## 3. Remote OAuth flow

```bash
# Step 1: print auth URL
gog login cooper@darkmatter.io --services=gmail --gmail-scope=full --force-consent --remote --step 1

# User opens the URL, authorizes, and copies the redirect URL

# Step 2: exchange the code
gog login cooper@darkmatter.io --services=gmail --gmail-scope=full --force-consent --remote --step 2 --auth-url "<pasted-redirect-url>"

# Verify
gog auth list -p
```

## 4. Safety flag for agent triage

Always use `--gmail-no-send` when doing read-only triage:
```bash
gog --gmail-no-send gmail list "in:inbox" -j --max 100
```
