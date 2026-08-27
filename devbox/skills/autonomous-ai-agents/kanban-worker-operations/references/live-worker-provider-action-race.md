# Live worker vs operator-side provider action

Use this when a user gives approval in the foreground while the same Kanban card is already `ready`, `running`, or `review`, and either the foreground operator or worker could perform the provider mutation (send, publish, upload, etc.).

## Invariant

A provider action must happen exactly once, while the card reaches a valid terminal outcome without erasing a healthy worker's audit trail.

## Procedure

1. **Read live card/run state immediately before acting.** Inspect card status, latest run, heartbeat, and comments. A card that was blocked during drafting may have been unblocked and auto-claimed seconds later.
2. **Choose one execution owner.** Prefer letting the live worker consume the approval. Do not independently perform the same provider action merely because the foreground also has credentials.
3. **If the operator must act while a worker is live:**
   - perform the provider mutation once;
   - verify the provider's durable result (message ID, upload ID, transaction ID, etc.);
   - immediately add a card comment beginning `DO NOT REPEAT` or `DO NOT RESEND`, including the provider handle, verified state, and prohibited actions not taken.
4. **Do not force-complete a healthy running/review card.** A direct completion can race the worker's claim, lose its structured metadata, or cause a second terminal transition. Let the worker/reviewer reread the provider and finish.
5. **Wait boundedly for a terminal state.** Current heartbeats mean active, not stuck. Accept `done/completed/error=null` or a genuine `blocked/error=null` result.
6. **Reconcile stale display fields after terminal completion.** If the provider labels changed but the task body still shows old tags, use the supported task-update handler to synchronize title/body while preserving `done`; do not reopen merely to fix display text.

## Cross-board diagnostic nuance

A source-board summary may mention a real task ID on another board. Per-board diagnostics cannot resolve foreign-board IDs and may flag `prose_phantom_refs` even though the destination exists.

- Search the destination board by both the referenced task ID and stable key before classifying the reference as hallucinated.
- Treat it as a false-positive diagnostic only after the foreign task and routing invariant are verified.
- Prefer stable keys or board-qualified references in summaries when possible.

## Verification

- [ ] Exactly one provider mutation exists.
- [ ] No retry followed an ambiguous wrapper result before provider lookup.
- [ ] The live worker received explicit no-repeat evidence.
- [ ] Latest run ended terminally with `error=null`.
- [ ] Provider state and card body/status agree.
- [ ] Cross-board references were checked in the destination board before calling them phantom.
