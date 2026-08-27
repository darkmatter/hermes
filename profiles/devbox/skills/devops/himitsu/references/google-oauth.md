# Google OAuth Client — Darkmatter Drive

**Himitsu path:** `google/oauth-client-secret-darkmatter-drive.json`

**Project:** darkmatter-471021
**OAuth type:** `installed` (desktop/app flow)
**Redirect URI:** `http://localhost`

## Fields

| Field | Description |
|---|---|
| `client_id` | OAuth client identifier |
| `client_secret` | OAuth client secret |
| `project_id` | GCP project (darkmatter-471021) |
| `auth_uri` | `https://accounts.google.com/o/oauth2/auth` |
| `token_uri` | `https://oauth2.googleapis.com/token` |
| `auth_provider_x509_cert_url` | `https://www.googleapis.com/oauth2/v1/certs` |
| `redirect_uris` | `["http://localhost"]` |

## Usage with gog

The `gog` CLI reads this client from the keyring. To re-auth:
```bash
gog login cooper@darkmatter.io --services=gmail,calendar,drive --gmail-scope=full --force-consent
```

## API enablement

The Gmail API must be enabled on the GCP project for Gmail scopes to work. If `unauthorized_client` errors persist after re-auth, check that the Gmail API is enabled in the Google Cloud Console for project `darkmatter-471021`.
