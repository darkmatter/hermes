# AA managed-reservation lookup and cabin-change inspection

## Scope
Use this for **read-only** confirmation of AA post-ticketing options. Do not select a fare or confirm a change unless Cooper explicitly authorizes it.

## Reservation retrieval
AA Find Your Trip requires all three fields:
- passenger last name
- six-character record locator (or ticket number)
- date of birth

For the custom DOB `<select>` elements, use option **values** (not expanded labels):
```ts
await page.locator('select[name=dateOfBirthMonth]').selectOption('02');
await page.locator('select[name=dateOfBirthDay]').selectOption('20');
await page.locator('select[name=dateOfBirthYear]').selectOption('1991');
```

AA duplicates generic `id="button"` elements for cookie dismiss and submit. Target the lookup submit with:
```ts
page.getByRole('button', {name: 'Find your trip', exact: true})
```

## Upgrade vs. cabin change
The managed-trip page may show no literal **Upgrade** option. Do not report an upgrade as available merely because it offers `Change seats`, `Same-day flight change`, bags, meals, or `Change trip`.

To inspect a paid cabin move without committing:
1. Open **Change trip**.
2. Check the relevant flight under “Select flights to change.”
3. Continue to **Choose flights**.
4. Read cabin cards for the *same flight/date*.
5. Stop before opening a fare card or selecting a replacement flight.

This is a **ticket reissue / cabin change**, not necessarily an in-place upgrade. AA shows the prior ticket value, $0 change fee if applicable, and a **per-person additional fare difference**. Report those separately.

## Cabin labels
On AA’s change-results grid:
- `Premium Economy` is explicitly labelled.
- Generic visual label `Premium` is backed by accessibility id `cabinType-FlagshipBusiness-*`; report it as **Flagship Business**.
- Include inventory when AA shows it (for example, `1 seat left`).

## Kernel auth
Prefer an injected-secret invocation over shell command substitution when running Kernel from a fresh shell:
```bash
himitsu exec kernel-api-key -- /opt/homebrew/bin/kernel browsers …
```
This avoids exposing the API key and keeps each command independently authenticated.
