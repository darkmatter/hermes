# Transaction-safe shopping and reservation changes

Use this for airline rebooking/upgrades and any browser flow that can change an itinerary or charge a card.

## Split the flow into explicit states

1. **Inspect** — retrieve the reservation and inventory. Do not infer availability from an absent homepage/upgrades widget.
2. **Price** — enter the read-only change/shopping flow when necessary. It can expose a fare-difference card even where no in-place upgrade is offered.
3. **Select** — choose the exact itinerary/cabin only after matching flight number, date, passenger count, availability, and fare type. Selection is not submission, but verify the subsequent summary.
4. **Review** — extract the final total, whether it is an additional charge or total fare, fees, taxes, refundability, and any original-ticket credit applied.
5. **Authorize and submit** — never merge this with selection. Present the exact final charge and scope; submit only after the required user authorization / payment challenge.
6. **Verify** — retrieve the confirmation page and confirm the new cabin/itinerary and ticket status before reporting success.

## Reliable browser inspection pattern

- Prefer screen-driven interaction first. If coordinate scaling or a custom widget makes the visible target unreliable, use a narrow DOM read to discover the real semantic control (`name`, accessible label, or `aria-labelledby`) instead of guessing coordinates.
- For repeated custom fare cards, use the card's accessible description to bind the action to **flight number + route + date + cabin + exact price**. Do not use a global `Select` label or a positional `nth()` selector unless you immediately verify the selected-trip summary.
- Airline check-in/retrieval may require a record locator, last name, and date of birth. Treat that DOB as lookup-only data; never expose it in logs or user updates.
- “Premium”, “Business”, and “First” labels can differ by airline/equipment. Read the card's accessibility text or final fare description before translating it for the user.

## User-facing reporting

Before a charge, state only verified facts: passenger, flight/date, selected cabin, refundability, final additional charge, fees, ticket credit applied, and current seat availability. Do not say “upgraded” until the airline confirmation has been verified.
