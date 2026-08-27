# Call digits & outcome discipline (session lessons)

## Failure only after log
- Success may be declared early when hard evidence is already in-hand (live digits, ticketed conf).
- **Never declare failure** (or "no number", "only VM", "call was useless") until `GET /call/<id>` full `messages`/`transcript` for **every relevant call id** in the session — not only the latest.
- DELETE / end-call does **not** wipe transcript value. Example: interactive 206 call still held STT digits after DELETE while a purely-VM follow-up was empty.
- Watcher one-liners and `endedReason` alone are insufficient for failure.

## Spoken 13-digit tickets
- Levi STT of ticket/credit numbers is a **hypothesis**, not ground truth.
- `0012342708964` (WSZTVR thread) looked ticket-shaped but **failed clean aa.com Find travel credit** (form held Reynolds + DOB + digits, submit → silent empty form). User confirmed number wrong.
- Before reuseizing a spoken 001… on payment or rebook: re-verify on aa.com or from cancel/e-ticket email.

## How to ask for the real digit string
- Prefer **Studio BB iMessage from cooperton42391@gmail.com**.
- Ask **the number Cooper specified** (often **+12069542027**, not auto-310). Don't default to 310 HITL phone unless he said so.
- Message tone: brief; "probably misheard on the call"; list cancel email / e-ticket / statement; reply in-thread.

## 206 vs 310 (Telavaya booking)
- **+12069542027** = Telavaya handoff / "text 206" / warm-transfer ================= **and**AA passenger **phone** for Telavaya Reynolds when booking her.
- **+13109897067** = Cooper only (callback / HITL). Never put on Telavaya's ticket contact (Cooper: "thats MY phone number").
