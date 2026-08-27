# US related-party business loans (domestic)

Condensed guidance from Cooper family/affiliate capital-injection sessions.
Not legal/tax advice — agent drafts are counsel/CPA-ready, never sign-ready.

## 1. Classify the cash first

When someone says “sending money into the business,” force one character before drafting:

| Character | Books (borrower) | Tax (typical) | Payer deduction? |
|-----------|------------------|---------------|------------------|
| Equity / capital contribution | Cash ↑, equity ↑ | Usually not income | No |
| Bona fide loan | Cash ↑, note payable ↑ | Proceeds usually not income; interest may be deductible | Principal no; interest maybe |
| Gift | Usually personal, then contribute | Gift-tax rules on donor | Corporate “gift” usually wrong vehicle |
| Invoice / services revenue | Revenue on P&L | Taxable income | Only if real work at FMV |

**Never paper a capital injection or loan as a consulting invoice** to manufacture a deduction. Related-party fake invoices are audit/fraud risk for both sides.

Arm’s-length test for invoices: would an unrelated buyer pay this amount for the same deliverable with the same proof of work?

## 2. If it is a loan — minimum substance

Debt-vs-equity factors the IRS/courts care about (related-party heat is higher):

- Written note with fixed principal
- Interest (see AFR below)
- Maturity **or** clear demand terms
- Payment schedule that is followed (or formal written amendments)
- Enforceability / default remedies
- Books match the paper (Note Payable / Note Receivable — not revenue, owner draw, or AP-consulting)
- Wire memo matches character: `Loan proceeds – PN dated [date]`
- Corporate authority on **both** sides (board/member written consents)
- Optional but stronger: security, guaranty, intercreditor if other lenders exist

Behavior matters as much as paper. Silent non-collection or later “forgiveness” is a separate tax event — never handshake-only.

## 3. Interest and below-market loans

- Private parties **can** contract for 0% interest.
- Tax law often **imputes** interest on large related-party below-market loans (§7872 and related rules). De minimis caps do not help at seven-figure principal.
- Default recommendation: interest **≥ applicable AFR** for the note’s term bucket (short / mid / long) in the month of signing/funding. CPA picks the exact rate and compounding/day-count.
- Accrued / PIK interest is usually cleaner than pure 0%.
- 0% is also a negative factor in debt-vs-equity analysis when stacked with no maturity, no payments, thin cap, related parties.

Lender’s **company** advancing interest-free cash can raise fiduciary / corporate-waste questions; sometimes cleaner economically is company → owner (with proper tax on that step) → owner loans borrower — still a CPA call.

## 4. Document packet (domestic related-party)

Minimum viable set:

1. **Promissory note** (parties, principal, ≥ AFR interest, payment structure, default, business purpose, governing law)
2. **Borrower written consent** (authorize borrow + signatory)
3. **Lender written consent** (authorize lend; related-party fairness recital when lender is an entity)
4. **Funding / wire authorization** (account details, required memo text, conditions to fund)
5. **Closing checklist** (terms lock → conflicts with existing debt → execute → wire → books → ongoing payments/1099)

Strongly add when facts require: loan agreement (if note is thin), security + UCC, guaranty, intercreditor/subordination (Brex/bank/investor debt), open-issues memo for counsel/CPA.

Payment structure options to offer explicitly (user picks one):

- A — Interest-only + balloon at maturity
- B — Amortizing installments
- C — Demand note with scheduled interest until demand

## 5. CPA vs lawyer (what Cooper actually asked)

| Need | Who |
|------|-----|
| AFR, imputed interest, QBO coding, 1099-INT, entity tax character | **CPA — treat as necessary** |
| Enforceable note language, entity authority, usury/state law, security/guaranty, intercreditor | **Business attorney** |
| “Is a lawyer legally required for the loan to exist?” | **No** — but risk rises with size + related parties |
| Best cost/benefit at ~$2M related-party | CPA sets terms → fill packet → **lawyer light review (1–2 hrs)** → sign → wire |
| CPA only | Defensible only if clean ≥ AFR terms, simple unsecured bilateral entities, full docs + actual payments, user accepts residual legal risk |
| Neither / memo-only wire | Bad at material size |

Do **not** tell the user a lawyer is mandatory in all cases, or that a CPA replaces counsel on enforceability. Split the lanes clearly.

Agent role: draft packet + open issues; do not silently choose governing law, security, guaranty, or below-AFR rates.

## 6. Delivery preferences (this user)

When Cooper asks for a **template / doc packet** (not just conceptual Q&A):

- Produce real `.docx` files, not only a markdown wall in chat.
- Default Dropbox root: `~/Dropbox (Personal)/docs/`
- Folder naming pattern: `Loan Packet - Related Party 2M` (adjust amount/topic).
- Include README + term sheet + numbered exhibits `00_`…`05_`.
- Every draft: header/footer **TEMPLATE / NOT LEGAL ADVICE / attorney+CPA review required**.
- Leave blanks for legal names, rate, dates, governing law — do not invent EINs, account numbers, or SOS names **unless user or source docs already confirmed them**.

Generation path that worked: Node `docx` package (`npm install docx` in `/tmp`) → write into Dropbox folder. Verify with macOS:

```bash
textutil -convert txt -stdout "/path/file.docx" | head
unzip -t "/path/file.docx"
```

`textutil` is the reliable body extract on Cooper’s Mac. Prefer it over assuming pandoc is installed (pandoc may return empty). Headers/footers still need python-docx or visual open if legends must be proven.

Automated cross-exhibit checks: `scripts/verify_docx_packet.py` when a `deal_terms.json` exists.

### AFR lookup (funding-month lock)

- IRS index: https://www.irs.gov/applicable-federal-rates
- PDFs: `https://www.irs.gov/pub/irs-drop/rr-YY-NN.pdf` (e.g. Rev. Rul. 2026-11 = June 2026).
- Use **mid-term** AFR for notes **>3 and ≤9 years**; short-term ≤3; long-term >9.
- Match compounding column (annual/semiannual/quarterly/monthly) to the note’s mechanics — CPA confirms.
- Rate locks to the **month of the loan/funding**, not the month docs are drafted.

### Known entity defaults (confirm each session; may change)

| Side | Typical values (2026 session) |
|------|-------------------------------|
| Borrower | **darkmatter labs, Inc.** — Wyoming S-corp; EIN **33-4385460** (Form 2553; confirm after LLC→Inc); registered addr **1603 Capitol Ave, Ste 415 #671799, Cheyenne, WY 82001** (was LA Grand Ave) |
| Lender (family) | **Susteen, Inc.** — California corp; public HQ **18200 Von Karman Ave, Ste 780, Irvine, CA 92612** (susteen.com); founder/CEO Hiro Maruyama — confirm charter + authorized signers |
| Operating cash | Brex business checking (darkmatter) — common landing account |
| CPA context | Shurek / QBO Essentials; accountant packet under Dropbox `docs/accountant-packet-shurek-2026/` |

Do not invent Susteen EIN or bank details. Confirm SOS legal-name capitalization (`darkmatter labs, Inc.` vs `Darkmatter Labs, Inc.`).

## 7. Intake fields before filling blanks

Batch once (see main skill intake rules):

- Lender legal name, entity type, state of formation
- Borrower legal name, entity type, state of formation
- Ownership / control map (who owns each side)
- Principal, currency (default USD)
- Rate source (CPA AFR month/term)
- Structure A/B/C, payment frequency, first payment, maturity or demand
- Secured? Guaranty? Existing senior debt / Brex-bank consent?
- Use of proceeds (business purpose)
- Target funding date; wire bank identity only at closing

Mark counsel/CPA judgments `[[TBD—COUNSEL]]` / `[[TBD—CPA]]`.

## 8. Books after funding (borrower)

- Dr Cash / Cr Note Payable for principal
- Accrue or pay interest per note
- Principal repayment is not expense
- Do not book loan proceeds as income

Lender: Note Receivable asset; interest income; principal advance not a deductible expense.

## 8b. Post-funding / cash-already-received (critical path)

Cooper often funds **before** paperwork. Do **not** keep drafting a pre-wire packet.

When user says funding already happened (or you find the Brex/bank credit):

1. **Switch mode immediately** — label packet `POST-FUNDING DRAFT`; README opens with “cash already received.”
2. **Intake funding facts** (batch): exact date, exact amount, receiving account (Brex vs other vs personal), any memo/reference, how QBO currently books it.
3. **AFR = funding month**, not draft month. Example: funded 2026-06-10 → June 2026 mid-term AFR (Rev. Rul. 2026-11 annual **4.13%** for a 5-year note), not August’s 4.35%.
4. **Rewrite exhibits for ratification**, not future advance:
   - Note § “Promise to Pay; **Prior Advance**” — acknowledges sum advanced on [date], ratifies as principal as of Effective Date
   - Interest commences on funding/Effective Date
   - Maturity = funding + term (e.g. 2026-06-10 → 2031-06-10 for 5 years)
   - First interest date calendared (e.g. next quarter start) + **catch-up interest** from funding → first payment as CPA issue
   - Both consents: WHEREAS Prior Advance + RESOLVED ratify
   - Funding auth: “ALREADY COMPLETED” + attach Brex PDF ref; no “please wire”
   - Checklist: evidence of credit, QBO reclass, catch-up, sign nunc pro tunc / as-of funding date
5. **CPA open issues to surface explicitly**: debt vs equity of already-received cash; nunc pro tunc vs new note acknowledging prior advance; reverse any income/equity misbooking; 1099-INT; S-corp AAA/basis.
6. **Evidence**: pull Brex transaction PDF/CSV into the Dropbox packet folder; do not claim wire details you did not open.
7. Optional counsel: short ratification / acknowledgment-of-prior-advance language if note body feels thin.

Default commercial structure when user is indifferent (still mark CPA-confirm on rate): **5-year interest-only quarterly + balloon**, unsecured, no personal guaranty — user picked these in 2026 session.

## 9. Pitfalls

- Invoice path used because “payer wants a deduction” while economic deal is capital or loan
- 0% “to keep it simple” on seven-figure related-party debt
- Wire memo saying gift / investment / consulting while docs say loan (or the reverse)
- Missing lender-side corporate approval when father’s **company** is the lender
- Ignoring existing facility covenants (negative pledge, permitted indebtedness)
- Promoting agent templates as sign-ready
- Blocking the whole packet on lawyer-only fields instead of drafting with visible TBDs
- Serial single-question intake instead of one term sheet + draft
- **Drafting a pre-wire packet after cash already hit the account** — always flip to post-funding ratification
- **Using current-month AFR when funding was prior month** — lock AFR to funding month
- Leaving stale rate-basis prose (e.g. “August AFR”) after switching funding month — grep exhibits for month names
- Booking $2M as revenue/owner draw; failing to reclass to Note Payable once character is loan
- Assuming old LA apartment address still correct — confirm Cheyenne registered agent / SOS address

## Related

- Main workflow: parent `legal-document-preparation` SKILL.md
- Cross-border / foreign lender overlays: `references/cross-border-corporate-loans.md`
- Equity/ownership review of completed deals: `private-investment-deal-review` (different class)
- Live packet (2026): `~/Dropbox (Personal)/docs/Loan Packet - Related Party 2M/`
