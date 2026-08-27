# Himitsu → 1Password Service-Account Bridge

Use this when the final application credential is stored in 1Password but non-interactive `op` authentication is stored in Himitsu.

## Available service-account tokens

Verified on 2026-08-18:

| Himitsu path | Accessible 1Password vaults |
|---|---|
| `op-service-account/token` | `cm`, `cooper`, `dev` |
| `flue/op-service-account-token` | `centaur` |

Vault access is the decisive constraint. A path copied from a Mac-local personal session, such as `op://Private/...`, may fail even when the service token itself is valid because service accounts cannot see that vault.

## Safe workflow

Bind Himitsu first:

```bash
export PATH="~/.nix-profile/bin:$PATH"
export HOME=~
export HIMITSU_AUTO_PULL=false
```

Load the service token and pass it only as an environment variable to `op`:

```bash
SERVICE_TOKEN=<REDACTED>
OP_SERVICE_ACCOUNT_TOKEN=<REDACTED>
  | jq 'map({id,name})'
```

Discover items by metadata without reading fields:

```bash
OP_SERVICE_ACCOUNT_TOKEN=<REDACTED>
  | jq 'map({id,title,vault:.vault.name})'
```

Retrieve the final credential into a second variable:

```bash
APP_TOKEN=<REDACTED>
  op read 'op://dev/ITEM/FIELD')"
unset SERVICE_TOKEN
```

Service-account `op item get` / `op item list` calls that target a single item **must pass `--vault`** (name or id). Without it the CLI exits 1 with `a vault query must be provided when this command is called by a service account`. `op read op://vault/item/field` already includes the vault and does not need the flag.

Use `APP_TOKEN` in-process, print only a safe authentication outcome, and `unset APP_TOKEN` when done.

## Vapi example

The Vapi API key is available to the service account at:

```text
op://dev/vapi/credential
```

Use:

```bash
SERVICE_TOKEN=<REDACTED>
VAPI_KEY=<REDACTED>
  op read 'op://dev/vapi/credential')"
unset SERVICE_TOKEN
```

Do not fall back to printing item JSON or a full credential object. If the expected path fails:

1. verify the token with `op vault list`;
2. inspect item titles and vault names only;
3. choose an item in an accessible vault;
4. read only the needed field.

## No-leak rules

- Never use `set -x` around secret retrieval.
- Never place the service token or final credential in command text, chat, files, memory, or skills.
- Do not print `op item get ... --format json`; item JSON can include credential fields.
- Metadata-only vault/item listings are safe when filtered to IDs, titles, and vault names.
- A length/prefix probe is acceptable only when authentication cannot otherwise be tested; prefer an authenticated API status probe.
