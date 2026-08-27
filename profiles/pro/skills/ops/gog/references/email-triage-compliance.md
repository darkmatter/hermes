# Compliance and regulatory email triage

Use this pattern for notices involving CFTC/SEC/IRS, exchanges, banks, taxes, licensing, or other regulatory deadlines.

## Safe investigation sequence

1. Preserve the original message/thread ID, account, sender, date, deadline, and attachments.
2. Inspect the message body and download/read attachments locally; do not click links from the email during initial review.
3. Check authentication indicators available from Gmail (`DKIM`/`SPF`/`DMARC`) but do not treat them alone as proof that the request applies to the user.
4. Separate facts from claims: identify the exact account/entity, position/activity, statute/program, requested form, code/reference number, deadline, and consequence.
5. Verify through a known official provider/regulator channel (for example, an existing Coinbase login or support/compliance channel), not by replying to the notice or using an unverified session URL.
6. Present no more than five urgent items to the user, with a summary, uncertainty, and proposed action. Do not file, submit MFA, disclose identifying data, or make payments without the appropriate user gate.

## CFTC Form 40 pattern

A Coinbase/CFTC notice may state that a customer must file Form 40, Statement of Reporting Trader, through the CFTC Large Trader Reporting portal. The associated registration instructions can require a 9-digit CFTC code, individual non-shared account, business contact details, phone MFA, email MFA, and up to two business days for account approval.

Before recommending registration or filing, confirm with the provider:

- the Coinbase Futures account/entity involved;
- whether the user actually held or controlled a reportable futures/options position;
- the associated CFTC code number;
- the exact filing deadline and whether an extension is available;
- whether the provider expects the customer or Coinbase to submit any part of the report.

A notice that is DKIM/SPF/DMARC-authenticated can still be misdirected, stale, or applicable to a different account. The correct next step is confirmation through a known official channel, not immediate form submission.

### Where the 9-digit CFTC code actually lives (do not stop at Coinbase)

Cooper's Form 40 mail is multi-message and multi-account. The **Coinbase forward** (`cfm.compliance@coinbase.com`, often on `me@cm.xyz` / delivered-to `me@cooperm.com`) is a broker relay — it typically does **not** include the 9-digit code in the body or the attached generic `CFTC Portal Instructions.pdf`.

Search **all** mail accounts for direct CFTC mail:

```bash
export GOG_KEYRING_PASSWORD=<REDACTED>
for a in me@cm.xyz cooper@darkmatter.io; do
  gog -a "$a" gmail list 'from:(cftc.gov OR portalmail.cftc.gov OR cfm.compliance@coinbase.com) (Form 40 OR "large trader" OR LTR OR "Filing Number")' --max 20 --json
done
```

**Code sources, in priority order:**

1. **Subject of the original CFTC notice** — e.g. `CFTC Form 40 Filing Number: 983967313`.
2. **Named personal PDF** on that notice (e.g. `KOUTAROU MARUYAMA.pdf`) — extract with `pypdf`; the 9-digit code sits near name/deadline even when layout splits "Confidential code number".
3. **Not** the generic portal-instructions PDF alone (only explains that a 9-digit code is required / recovery via `OCRTechSupport@CFTC.gov`).
4. **Not** the Coinbase compliance forward body alone.

Cooper's assigned code from 2026 notices: **`983967313`**. LTR portal registration email: **`cooper@darkmatter.io`**. Portal: `https://portal.cftc.gov`. Org type: **LTR (Large Traders)**.

### Portal OTP vs permanent code

- **Permanent / filing code** = 9-digit CFTC code (LTR signup field "CFTC Code Number").
- **One-time registration/login OTP** from `NOREPLY@portalmail.cftc.gov` (subject like `CFTC Portal One-time Security Code`) — often on **`cooper@darkmatter.io`** even when Form 40 notices landed on personal mail. Body: `CFTC Portal Code for Registration is NNNNNN`. Email codes expire ~8 hours; phone MFA is a separate 6-digit step.

When the user asks "is there a code I just received?", search `newer_than:1d from:portalmail.cftc.gov` on **every** account before saying no.

### Local PDF extract

```bash
gog -a <acct> gmail thread get <threadId> --full --download --out-dir /tmp/cftc --json
python3 - <<'PY'
from pypdf import PdfReader
import re
r = PdfReader("/tmp/cftc/<file>.pdf")
text = "\n".join((p.extract_text() or "") for p in r.pages)
print(re.findall(r"\b\d{9}\b", text))
print(text[:3000])
PY
```

### Closing the loop after registration/filing

When Cooper says the portal is registered / Form 40 is handled:

1. Label related threads `Triage/Done`, remove `Triage/Needs-Action`, archive, mark-read.
2. Use **comma-separated** `--remove` on gog 0.27+ (`--remove "Triage/Needs-Action,INBOX,UNREAD"`), then `gmail archive --thread <ids...>` and `gmail mark-read` — bare repeated `--remove` flags alone have left labels stuck.
3. Verify with `label:"Triage/Needs-Action" (Form 40 OR CFTC)` → count 0.
4. Update durable memory with code + registration state; do not leave "needs 9-digit code" stale.
