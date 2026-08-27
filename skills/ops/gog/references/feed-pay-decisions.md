# Pay / Don't-pay → feed dashboard

When inbox triage surfaces many pure money decisions (failed charges, renewals, past-due invoices, domain renew), **do not** dump them as a chat wall. Put them on the home feed as simple choices.

## Pattern

1. One blocked `email-triage` Kanban card per vendor/decision:
   ```bash
   hermes kanban --board email-triage create 'Pay decision: <service> <$amount>' \
     --body 'DoD-CLASS: EXECUTE-GATED\nDecision type: PAY / DONT_PAY\n…' \
     --assignee default --priority 180 --initial-status blocked \
     --idempotency-key paydec-<service>-YYYY-MM --json
   ```
2. Wire `~/.hermes/feed/recommendations.json`:
   - `category`: `decision`
   - `why_blocked`: short money reason
   - one `choice` action labeled `Pay or don't pay?` with:
     - `✅ Pay` → prompt authorizing official-portal repair (**charge gate still enforced**)
     - `❌ Don't pay` → cancel/ignore, Done-label threads, complete card
3. Rebuild + push: `python3 ~/.hermes/scripts/build-feed.py` → localhost:8654 + https://feed.cm.xyz
4. Cooper marks cards a few at a time (radio + Copy Hermes prompt), pastes back; agent executes with evidence.

## Grouping

- Prefer **one card per vendor**, not per email.
- Batch SaaS “subscription will renew soon” noise into one multi-service card when helpful.
- Reuse existing cards when present (e.g. Saltbox `t_21988079`, Moniker domains `t_35fbabcc`).

## Chat still owns

Non-checkbox Critical items (≤5): human threads, security handoffs Cooper must do, ambiguous ops. Deadlines list can stay in chat as a dated table.

## Related

- Interactive triage bulk/NA heuristics: `references/interactive-triage-pass.md`
- Feed rebuild/ingest: skill `operator-status` (user-owned — recommend `hermes curator adopt operator-status` if that skill needs the same subsection)
