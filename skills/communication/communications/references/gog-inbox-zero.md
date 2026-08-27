# Gmail Inbox Zero via gog — operating notes

## Connectivity and the misleading credential warning

`gog auth doctor` may warn that a client-credentials config file is absent and suggest:

```bash
gog auth credentials <credentials.json>
```

Do **not** treat that warning as a need to re-authenticate or replace credentials. First prove the real state:

```bash
gog auth list
gog -a <account> gmail search "newer_than:1d" --max 1 -j
```

If the account token is readable and the query succeeds, Gmail access is working. The warning concerns a client-credentials config path, while OAuth tokens may already be usable through the configured encrypted keyring.

## Safe Inbox Zero workflow

Treat inbox-only actions as `EXECUTE-SAFE`; never delete, send, click financial/fraud email links, alter security settings, or approve OAuth permissions without the appropriate gate.

1. **Create/claim one durable Kanban card** for the inbox-zero run. Add scope, explicit action boundaries, and a Gherkin verification condition.
2. **Enumerate in bounded pages**, never a full `--all` fetch on a large inbox:
   ```bash
   gog -a <account> gmail search "in:inbox" --max 10 -j
   # use returned nextPageToken only after rate-limit headroom is available
   ```
3. **Process one thread/card at a time.** Classify it before changing mailbox state:
   - reversible label/archive/mark-read/filter → `EXECUTE-SAFE`
   - draft needed → `DRAFT` / review
   - send, delete, security change, money/legal impact → `EXECUTE-GATED`
   - identity/2FA/official-account review needed → `HANDOFF` / blocked
4. For security, financial, or fraud-shaped messages, create a blocked handoff card containing the exact source thread IDs and direct Cooper to official account pages/apps. Do not follow message links.
5. For every inbox state change, append the exact verifying Gmail query and the expected/actual result count to the Kanban card. Completion requires an observable read-back, not an assertion.

## Gmail query quota handling

A large `--all` enumeration can hit per-user Gmail query quota (`403 rateLimitExceeded`) or exceed the agent command timeout. No inbox state has changed in that case.

Recovery:

- Stop making requests for the quota window to reset.
- Resume with small `--max 10` requests, with pagination and a measured delay between pages.
- Work from saved pages rather than repeatedly re-querying the same inbox.
- Log the rate-limit event on the active Kanban card; do not claim enumeration completed until the paginated evidence is present.
