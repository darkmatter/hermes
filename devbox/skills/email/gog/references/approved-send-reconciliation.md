# Approved Gmail send and Kanban reconciliation

Use this for an email tied to a live Kanban card when the user iteratively reviews a draft and then explicitly approves transmission.

## 1. Separate analysis from recipient-facing instructions

- A question such as “does it seem like the broker is already talking to the seller?” asks for **internal inference**. Do not turn it into “Are you talking to the seller?” in the draft unless the user explicitly asks you to ask the recipient.
- Track three buckets while revising: **internal conclusion**, **facts to state**, and **requests/questions to send**. Only the latter two belong in the email.
- Preserve the user's substantive intent across revisions. When one paragraph is corrected, re-check the full draft so a stale version of the same idea does not survive elsewhere.

## 2. Treat preview and send as separate gates

1. “Preview,” “show me the draft,” or a material instruction such as “tell Chris…” means draft/revise only. Display the complete proposed message and state that it is unsent.
2. Require a later explicit instruction such as `send`, `send it`, or `send and close the card` before transmission.
3. Immediately before sending, reread the provider draft/thread and the Kanban card's current status/latest run. Do not assume the card is still blocked merely because it was blocked when drafting began.

## 3. Reuse the existing draft and thread

- Update the existing Gmail draft in place when one exists; do not create a duplicate draft.
- Preserve the original thread via `--thread-id` or `--reply-to-message-id` and verify recipient, subject, thread, and exact body before send.
- For negotiation or financial language, assert every approved term and make sure unapproved alternatives, internal speculation, and earlier draft language are gone.

## 4. Coordinate with a live worker

A user or dashboard action can unblock and auto-dispatch the card while the parent is editing or sending.

- If the card is `running` or `review`, do not force-complete it or race a second send path.
- Prefer allowing the live worker to consume the approval. If the operator must send directly, post an immediate card comment containing: **DO NOT RESEND**, provider thread ID, sent message ID, verified state/tags, and the actions deliberately not performed.
- Wait for the live run to reach a valid terminal outcome. Do not kill a healthy, heartbeating reviewer merely to make the card look done.
- After terminal completion, synchronize any stale card body fields (for example `Email-Tags:`) through the supported task-update handler while preserving `done`.

## 5. Verify Sent without duplicate-send risk

1. Send exactly once.
2. Inspect the returned message ID and the provider thread/Sent mailbox before interpreting any wrapper or comparison error.
3. `--sanitize-content` removes URLs and can normalize MIME formatting. Therefore an exact body comparison against sanitized output may fail even when the send is correct. Verify:
   - message ID and thread ID;
   - `SENT` present and `DRAFT` absent;
   - from/to/subject;
   - all material semantic clauses and approved numeric terms.
4. Never retry solely because sanitized text differs byte-for-byte. Retry only when Sent has no matching message.

## 6. Transition durable state and close work

- Verified reply with the external party owing the next move → `Triage/Waiting`; remove `reply` and other resolved work tags, preserving only still-relevant context tags.
- Read back every message's final state/tag labels.
- Complete the Kanban card only after Sent and provider labels are verified. Record message ID, thread ID, final labels, material commitments, and prohibited actions not taken.

## Verification checklist

- [ ] Internal inference was not leaked into the recipient draft.
- [ ] User previewed the final full message and later gave explicit send approval.
- [ ] Current card/run state was checked immediately before send.
- [ ] Existing draft/thread was reused and verified.
- [ ] Exactly one sent message exists; no retry followed a sanitizer-only mismatch.
- [ ] Gmail state/tags and card body/status agree.
- [ ] Any live worker received no-resend evidence and ended terminally without error.
