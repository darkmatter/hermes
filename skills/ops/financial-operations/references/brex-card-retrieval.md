# Brex corporate card retrieval (fallback payment source)

Brex is Cooper's FALLBACK card source — personal Amex Platinum first (see payment-operations skill). Use only when the primary is unreachable.

## Token

```bash
BREX_TOKEN=<REDACTED>
```

## API host (verified 2026-08-03)

- `https://api.brex.com` — WORKS (HTTP 200).
- `https://platform-api.brex.com` — timeout/unreachable (curl http=000).
- `https://platform.brexapis.com` — old docs host; was unreachable in testing.
Use `api.brex.com` first.

## List cards

```bash
curl -s -m 15 -H "Authorization: Bearer <REDACTED>" "https://api.brex.com/v2/cards"
```

Returns `{"items":[...]}` (41 cards observed). Item fields: `id` (`ncard_…`), `status` (ACTIVE/SHIPPED/TERMINATED), `card_type` (PHYSICAL/VIRTUAL), `last_four`, `expiration_date{month,year}`, `billing_address`, `owner`, plus optionally `card_name`, `budget_id`, `spend_controls`, `mailing_address`.

**The list endpoint NEVER returns full PANs** — there is no `number` field on list items. Don't loop the list looking for one.

## Card selection criteria

Prefer, in order:
1. `status == ACTIVE` and `card_type == VIRTUAL` (PAN retrievable; physical/shipped cards may 404).
2. **No `spend_controls` key** — spend controls can silently decline a charge.
3. Longest remaining expiry.

## Full PAN retrieval

```bash
curl -s -m 10 -H "Authorization: Bearer <REDACTED>" "https://api.brex.com/v2/cards/$CARD/pan"
```

- Returns `{"number", "cvv", "expiration_date", "holder_name", "id"}` (HTTP 200).
- Endpoint guesses that 404: `/number`, `/details`, `/full`. Only `/pan` works.
- Some ACTIVE cards may still 404 on `/pan`; iterate candidates in priority order and take the first 200.

## Secret hygiene

- `umask 077` before saving the PAN response to a temp file; never into chat, logs, tool output, or screenshots.
- Print only masked identifiers: first 6 + last 4 (e.g. `555671…4691`), holder name, expiry.
- Purge the temp file as soon as the card is saved into the merchant form.
- Full PAN/CVV still must NOT be typed through computer use without Cooper's explicit go — retrieval only prepares the handoff.

## Billing address note

Brex `billing_address` is the corporate registered address (e.g. 1603 Capitol Ave, Cheyenne WY — but `state` in the JSON may be wrong, e.g. "CA"; trust the city/ZIP or verify). If a merchant's AVS is strict against a personal cardholder name, flag the mismatch in the confirmation gate before submit.
