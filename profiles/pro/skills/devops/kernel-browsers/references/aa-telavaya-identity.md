# Telavaya / AA passenger identity (booking)

## Correct defaults (unless Cooper overrides)
| Field | Value |
|---|---|
| Name | Telavaya Reynolds |
| DOB | 1991-02-20 |
| Email | **`telvaya@icloud.com`** (not `pelavaya@…`) |
| Phone | **`+1 (206) 954-2027`** / `2069542027` |
| Gender | Female |
| Residence | US / **California** |
| Loyalty | **blank** unless asked |
| AA conf (canceled) | WSZTVR |
| Target flight | LAX→LHR Aug 2 Main ~AA 6935, total once ~$945.50 Main product |

## Do not confuse
| Number | Who |
|---|---|
| **310-989-7067** | **Cooper** — callback / HITL / cardholder verify — **not** passenger phone on Telavaya ticket |
| **206-954-2027** | Telavaya handoff / “text 206” / warm-transfer Levi destination — **use this on AA passenger phone** when booking her |

Prove phone field value after fill (read `input` value === `2069542027`).
Prove State after country (CA select). Never map phone into loyalty.

## Ticket / credit digits
Find-travel-credit needs 13-digit `001…`. Spoken STT `0012342708964` was **wrong** — empty form after clean submit is evidence of bad number, not necessarily $0 credit. Get digits from cancel email/e-ticket; BB ask goes to **206** when Cooper says 206.
