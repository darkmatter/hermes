# Multi-account cron verification

Use this checklist when a scheduled Gmail triage job is expanded beyond one account.

## Required checks

Run the token refresh check and the real read-only Gmail query separately for each account:

```bash
export GOG_KEYRING_PASSWORD=<REDACTED>

for account in cooper@darkmatter.io me@cm.xyz; do
  gog -a "$account" auth doctor --check
  gog -a "$account" gmail list 'in:inbox newer_than:1d' --max 50 --json
 done
```

`gog auth list` proves that tokens are stored, but it does not by itself prove that every account can execute the Gmail operation the cron needs. Treat an empty `threads` result as a valid empty inbox, not an auth failure. A command error or failed refresh means that account is unavailable.

## Updating the cron prompt

Name every required account and show one explicit `gog -a` command for each. Instruct the agent to:

- combine results across accounts;
- continue if one account fails;
- report the unavailable account clearly;
- never retain stale text saying an authenticated account is unconfigured or that only one account should be checked; and
- when labeling is in scope, apply the live taxonomy in `references/gmail-triage-labels.md` (`Triage/*`, `Muted/*`) rather than digest-only output or Superhuman `AI/*` labels.

## Verifying the edit

After changing the job:

1. Inspect the persisted job definition and confirm its schedule, enabled state, and updated prompt.
2. Trigger a manual run using the Hermes cron command.
3. Remember that the command may only queue the job for the next scheduler tick; inspect the job's subsequent `last_run`/status and output before calling the test successful.

This procedure is intentionally read-only with respect to email: verification must not archive, send, delete, or modify messages.
