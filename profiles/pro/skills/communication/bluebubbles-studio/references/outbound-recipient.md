# Outbound recipient selection

When Cooper says “text …” or “ask via BB”:

1. Use the **number he names** (e.g. **206** → `+12069542027`). Do **not** default to `+13109897067` because HITL allowlist includes both.
2. Still always send **from** Studio `cooperton42391@gmail.com` (apple-script if helper_disconnected; never Pro Messages).
3. Confirm send JSON `to` / handle address before reporting done.
4. Inbound replies on that thread → bb-hook inbox; HITL allowlist still accepts both 310 and 206.

Anti-pattern (this session): sent AA ticket-number request to 310 first; Cooper wanted 206.
