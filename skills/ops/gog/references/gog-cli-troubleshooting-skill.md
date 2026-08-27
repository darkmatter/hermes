---
name: gog-cli-troubleshooting
description: Troubleshooting and setup workflow for the gog CLI application, including Google auth and keyring token decryption issues.
version: 1.0.0
---

# `gog` CLI Troubleshooting
Troubleshooting steps for the Google API CLI wrapper `gog`.

## Keyring and Authentication Issues

### Corrupted Tokens/Decryption Failures
When `gog` fails with errors like:
`read token: read encoded file keyring item: aes.KeyUnwrap(): integrity check failed`
This indicates the local keyring cache for the tokens is corrupted or the encryption password (`GOG_KEYRING_PASSWORD`) has changed.

**Resolution:**
1. Run `gog -a <email> auth doctor` to see keyring health and list the problematic tokens.
2. Ensure OAuth client credentials are stored:
   ```bash
   himitsu read google/oauth-client-secret-darkmatter-drive.json > /tmp/client_secret.json
   gog -a <email> auth credentials set /tmp/client_secret.json
   ```
3. Remove corrupted tokens: `gog auth remove <email> -y`
4. Re-authenticate: see "Re-authenticating gog via live Chrome CDP" below.

### Backend Mismatch — tokens exist but `gog auth list` reports none

`gog auth list` returns `No tokens stored` / `{"accounts":[]}` even though the
user authenticated successfully before. **Before sending the user down a re-auth
path, check whether the tokens are in a different keyring backend** than the one
gog is currently looking at.

gog supports multiple keyring backends. The active one is controlled by
`GOG_KEYRING_BACKEND` (env var or config). Default on macOS = **macOS Keychain**;
`file` = a directory of encrypted JSON files. If a session-injection layer (cron
runner, `~/.hermes/.env`, CI env) sets `GOG_KEYRING_BACKEND=file` but the user
authenticated from an interactive shell where the var was *unset* (→ default
Keychain), the file backend is empty and cron reports zero accounts — even though
valid tokens sit in Keychain. The user then re-auths from the terminal (Keychain
again), cron still can't see them → **recurring re-auth loop**.

**Diagnostic flow** (in order):

```bash
# 1. What backend is active in THIS session?
gog --help 2>&1 | grep -i "keyring backend"
#   → prints: "file (source: env)" or similar

# 2. Is the env var forcing it?
env | grep GOG_KEYRING

# 3. Is the file keyring actually empty?
ls -la ~/Library/Application\ Support/gogcli/keyring/

# 4. Check macOS Keychain for gogcli tokens (gog's default backend)
security dump-keychain 2>/dev/null | grep -i "gogcli" | grep -i "token"
#   → acct entries like "token:default:<email>" mean tokens ARE in Keychain

# 5. Confirm: does gog see tokens when the backend override is removed?
env -u GOG_KEYRING_BACKEND -u GOG_KEYRING_PASSWORD gog auth list
#   → if accounts appear here but not without the -u flags, it's a mismatch
```

### Config-forced file backend (no env var involved)

`~/.config/gogcli/config.json` can set `{"keyring_backend": "file"}` directly,
forcing the file backend with **no env var override**. The env-var diagnostic
flow above won't catch this — `env | grep GOG_KEYRING` returns nothing, yet
`gog --help` still prints `keyring backend: file (source: config)`. When the
file backend is config-forced, tokens are encrypted files in
`~/.local/share/gogcli/keyring/` and need `GOG_KEYRING_PASSWORD` to decrypt.

**The password lives in himitsu** at `gog/keyring-password`. In non-interactive
shells (agents, cron), load it before every gog command:

```bash
export GOG_KEYRING_PASSWORD=<REDACTED>
gog -a <email> auth doctor   # should show status: ok
```

**Fix — three options (in order of preference):**

- **(Quickest) Supply the password from himitsu.** When the file backend is
  intentionally config-forced (e.g., Keychain unavailable headless), just load
  the password. This is the right approach in agent sessions where you can't
  change the config: `export GOG_KEYRING_PASSWORD="$(himitsu read gog/keyring-password 2>/dev/null)"`.
- **(Preferred) Stop forcing the wrong backend.** Remove the
  `GOG_KEYRING_BACKEND` / `GOG_KEYRING_PASSWORD` lines from env-injection layers
  AND/OR remove `"keyring_backend": "file"` from
  `~/.config/gogcli/config.json`. gog then falls back to macOS Keychain (the
  default) where tokens may already live. Back up the config first and verify
  with `gog auth list` afterward.
- **(Alternative) Re-auth into the forced backend.** If you genuinely need the
  file backend (e.g. Keychain unavailable headless), run `gog auth add` from
  *within the same environment* that sets `GOG_KEYRING_BACKEND=file` so the
  tokens are written to the file keyring, not Keychain.

**Pitfall:** Don't assume `{"accounts":[]}` means "never authenticated." Always
check Keychain (`security dump-keychain | grep gogcli`) AND the file keyring
(`ls ~/.local/share/gogcli/keyring/`) before recommending re-auth — the tokens
may be one env-var override or one himitsu password away from working. This is
the #1 cause of "I keep having to re-auth gog" complaints.

## Re-authenticating gog via live Chrome CDP

`gog auth add <email>` requires a browser to complete OAuth. When running headless or via agent, complete the OAuth flow using Cooper's live Chrome session via CDP (full reference in the `financial-operations` skill at `references/live-chrome-cdp.md`):

1. Start `gog auth add <email>` in the background — it starts a local HTTP callback server and prints the OAuth URL:
   ```bash
   # Background process; URL appears in process output
   gog auth add cooper@darkmatter.io &
   ```
2. Extract the OAuth URL from the process output (appears after "visit this URL:").
3. Open it in live Chrome via the CDP helper:
   ```bash
   ~/.hermes/scripts/live-chrome-cdp.js newtab "<OAUTH_URL>"
   ```
4. If Cooper is already logged into Google in Chrome, the consent page appears immediately. The OAuth callback hits the local server and completes the auth flow.
5. Verify: `gog -a <email> auth doctor` should show `status: ok`.

**Pitfall:** The OAuth URL contains a `redirect_uri` with a specific local port. Each `gog auth add` invocation uses a new port and state token. You must open the URL from the *current* invocation — stale URLs from previous attempts will fail silently.

**Fallback when live Chrome CDP is down:** If port 9222 is unreachable, the built-in `browser_navigate` tool works as a fallback for completing the OAuth flow. Start `gog auth add` in the background via `terminal(background=true, notify_on_complete=true)`, poll the process log for the OAuth URL, then navigate to it with `browser_navigate`. The callback still hits the local server and completes auth.

## Re-authenticating gog via two-step remote flow (preferred when user is present)

The `gog login` command (alias for `gog auth add`) supports a `--remote` flag that splits OAuth into two explicit steps. This is the **most reliable agent-driven pattern** when a user is available to complete the browser consent — no CDP, no background process polling, no port-matching race condition.

```bash
# Step 1: Generate the OAuth URL (prints to stdout, does NOT start a local server)
gog login <email> --services=gmail --gmail-scope=full --force-consent --remote --step 1
#   → Outputs an https://accounts.google.com/... URL

# Step 2: User opens the URL, authorizes, then pastes back the redirect URL
#         (the 127.0.0.1 callback URL from the browser address bar).
#         Complete the token exchange:
gog login <email> --services=gmail --gmail-scope=full --force-consent \
  --remote --step 2 --auth-url "<paste-redirect-url-here>"

# Step 3: Verify
gog -a <email> auth doctor
```

**Key flags:**
- `--services=gmail` — restricts auth to Gmail scope (use `--services=gmail,calendar,drive` for multi-service)
- `--gmail-scope=full` — requests `gmail.modify` (read/send/delete) vs `readonly`
- `--force-consent` — forces the Google consent screen (needed when re-authing after token expiry)
- `--remote` — enables the two-step split (no local callback server needed)
- `--step 1` — prints the OAuth URL only
- `--step 2 --auth-url <url>` — completes the exchange with the callback URL

**Account-chooser pitfall:** When the user has multiple Google accounts (e.g., `cooper@darkmatter.io` and `me@cm.xyz`), Google's account picker may default to the wrong one. The user must explicitly select the correct account. The redirect URL will contain an `hd=` parameter matching the authorized account's domain — verify this matches before running step 2. If `hd=` doesn't match, the exchange will fail with `authorized as <wrong-account>, expected <email>`.

**Token expiry:** Refresh tokens can be revoked by Google (after 6 months of inactivity, password change, or security event). When `gog -a <email> auth doctor` fails or `gog gmail list` returns "No auth for gmail", the token is gone and re-auth via either this two-step flow or the CDP method above is required.

## General
- Always use `gog -a <account>` to specify which account context you're operating in.
- Use `--no-input` with `gog auth add` to prevent hanging on prompts in agent-driven flows. The command will print the OAuth URL and exit rather than waiting for browser completion.
- For agent-driven re-auth, use `terminal(background=true)` to start `gog auth add`, poll the process output for the OAuth URL, then open it in the browser. This is more reliable than shell `&` backgrounding.
- `gog auth doctor --check` attempts a full token refresh and reports any failures.

## Multi-account cron verification

When a scheduled email-triage job is meant to cover multiple Gmail accounts, verify and encode account coverage explicitly rather than relying on a generic `gog auth list` check:

1. Run `gog auth doctor --check` for every required account with `-a <account>`.
2. Run the actual read-only Gmail query separately for every account, also with `-a <account>`; a successful global auth listing is not proof that each account is queryable.
3. In the cron prompt, name every required account and provide one concrete command per account. Tell the agent to continue with the healthy account if one fails, and distinguish an empty inbox from an authentication failure.
4. Remove stale scope notes from the prompt after an account is authenticated. Do not leave instructions such as “only configured account” or “account X is not configured” in a job that now has access to X.
5. Confirm the job prompt references the live label taxonomy (`references/gmail-triage-labels.md`) when labeling is in scope — dual-account **and** labeling, not just a dual-account dump into a digest.
6. Trigger a manual cron run after editing the prompt, then verify the job remains enabled and inspect its recorded result/output. A CLI “queued for next tick” response alone is not proof that the run completed.

For a concise account-coverage checklist and example prompt wording, see `references/multi-account-cron-verification.md`.

## Pitfall: gog Keyring in Subprocess (execute_code)

`execute_code` runs Python subprocesses that do NOT inherit `GOG_KEYRING_PASSWORD` from the terminal environment. The keyring file backend requires this env var, and without it gog fails with `aes.KeyUnwrap(): integrity check failed`. Even explicitly passing the env var to subprocess can fail due to AES key unwrapping issues. **Always run gog commands via `terminal()`** (which inherits the shell environment), never via `execute_code`'s `subprocess.run()`.

## References
- `references/email-operations.md` — gog Gmail command reference: list, read, archive, send, MFA code retrieval, and email triage workflow.
- `references/gmail-triage-labels.md` — Cooper's live Gmail label taxonomy (`Triage/*`, `Muted/*`, account-specific helpers), apply/verify commands, and Daily Comms Triage expectations. Prefer this over Superhuman labels.
- `references/multi-account-search.md` — Searching across multiple Gmail accounts, alias-vs-token distinction, and output truncation workarounds (--plain body truncation, --json terminal cap).
- `references/multi-account-cron-verification.md` — Checklist for dual-account cron prompts and verifying a queued manual `hermes cron run`.
- `references/batch-unsubscribe.md` — Multi-platform batch email unsubscribe workflow: extract List-Unsubscribe headers, hit URLs via curl GET/POST per platform (HubSpot, Loops.so, Mailchimp, PostHog, Morningstar), mailto fallback, and categorization strategy.
