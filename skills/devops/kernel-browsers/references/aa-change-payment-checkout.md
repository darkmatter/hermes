# AA change-flight checkout: durable browser-driving notes

Use this only for authorized ticket changes. It covers read-only navigation through AA’s change flow and the final checkout control shapes; it does **not** authorize a purchase.

## Change flow

1. Retrieve reservation using locator, surname, and any DOB AA requests.
2. `Change trip` → select the affected flight → continue to the fare grid.
3. Treat the fare-grid price as a **difference**, not a ticket total. At trip summary, verify flight, cabin, refundable state, passenger count, prior ticket value, change fee, and final amount due.
4. AA may send the user through optional seat selection before checkout. Do not alter a seat just to advance; wait for checkout/review.

## Targeting implementation details

- AA custom elements often render a wrapper and native button with the same `id` (for example `submitButton`). Use the accessible native button (`getByRole('button', {name: 'Pay now', exact: true})`) instead of an ID locator that can violate strict mode.
- Fare option buttons can be associated to screen-reader descriptions through `aria-labelledby`. When a visible `Select` is ambiguous, locate the fare’s descriptive `span`, read its parent `id`, then target `[aria-labelledby="<that-id>"]`.
- Shell interpolation of API keys can be brittle in automation runners. Prefer secret-backed execution that injects credentials without expanding the secret into the shell command, e.g. `himitsu exec kernel-api-key -- kernel ...`.

## Payment safety

- Before submission, repeat the exact total, passenger, flight, cabin/refundability, and card to the user; obtain an explicit final confirmation.
- A checkout message such as “Please check the security code (CVV)” is a client-side validation failure, **not** a charge attempt or issuer decline. Do not guess or repeatedly retry a stored CVV. Ask the user for the current value or for the credential record to be corrected, and keep the checkout unsubmitted.
- After a genuine submission, stop at the issuer’s MFA/SafeKey challenge and request the user-provided code. Verify the ticket/change confirmation after approval.
