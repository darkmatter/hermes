# Cross-border corporate loans — condensed knowledge bank

Session-derived reference for U.S. S-corp / foreign-lender cross-border loans.
**Issue spotting for counsel, not determinations.** Every item below is a
question to raise, not a conclusion to assert.

## S-corp eligibility (ownership-independent)

- A foreign corporation generally cannot be an eligible S-corp shareholder.
  If the lender acquires stock, options, warrants, conversion rights,
  profit-dependent payments, or equity-like benefits, the S election faces
  serious risk. Counsel must confirm the lender owns 0% and has no equity
  rights of any kind.
- §1361(c)(5) "straight debt" safe harbor requires the creditor to be
  eligible to hold S stock — a foreign corporation generally isn't. Counsel
  should evaluate whether the lender qualifies as a regular creditor actively
  engaged in lending; if that path is closed, classification rests on general
  debt-equity case law (fixed maturity, unconditional repayment, adequate
  commercial interest, enforceability, source of repayment).
- Recharacterization risk: soft terms, payment holidays, "pay when able,"
  contingent interest, or optional repayment schedules can cause the IRS to
  treat the advance as equity — which for an S-corp means a prohibited
  second class of stock held by an ineligible shareholder.

## Arm's-length pricing

- IRC §482 reaches "control," not just ownership. "The reality of the
  control is decisive, not its form" — de facto influence counts.
- Rate should be ≥ the Applicable Federal Rate (AFR) for the term at
  signing. Below-market rates create imputed interest — itself subject to
  withholding and 1042-S reporting.
- Archive the AFR table for the month of funding + a written comparable
  rate quote. Counsel should confirm the rate does not trigger §7872
  shareholder-loan rules.

## Withholding and treaty analysis

- Portfolio-interest exemption (IRC §881(c)) requires ALL of:
  - Note issued in registered form;
  - Lender delivers valid Form W-8BEN-E before first interest payment,
  - Interest not contingent on profits, receipts, or dividends,
  - Lender is not a 10%+ shareholder by §318 attribution,
  - Lender is not a CFC receiving interest from a related person,
  - Lender is not a bank lending in ordinary course of business.
- Fallback: U.S.-Japan treaty (Article 11, Interest) may reduce withholding,
  subject to Limitation on Benefits and valid W-8BEN-E.
- If both fail: statutory default is 30%.
- §267(a)(3) accrual deferral applies only to payments to §267(b) "related
  persons" — likely inapplicable without common ownership, but CPA confirms.
- §163(j) business-interest limitation applies regardless of relatedness.
- **Never promise a withholding rate in the contract.** Gross-up language,
  if any, is CPA-driven.

## Foreign-ownership reporting

- Form 5472 / §6088: targets 25%+ foreign-owned U.S. entities. Likely
  inapplicable if a U.S. person owns 100%.
- CFC / Subpart F / §956: applies only if the foreign entity has 10%+
  U.S. shareholders and is majority U.S.-owned. Confirm via lender
  ownership cap table.

## Debt-vs-equity characterization

Document bona fide debt facts:
- Written unconditional obligation to repay a sum certain
- Fixed maturity; fixed commercial rate; fixed payment dates
- Payments actually made on schedule
- Reasonable capitalization / repayment capacity
- Creditor remedies on default
- Nothing contingent on profits, value, or exit
- No oral or side agreements (include in loan agreement)
- Registered form + real enforcement (invoices, payment records, default rights)

## Family-connected (non-ownership) mitigation

When the lender is family-connected but not commonly owned (e.g. father is
an advisor with influence but zero ownership):

- **Procedural mitigation, not structural.** The documents carry the
  arm's-length burden through:
  - Father recused from lender's loan approval (does not vote, sign, or
    serve as sole basis for approval)
  - Lender's board/representative director approves independently
  - Father is not guarantor, finder, or fee payee on the loan
  - No-side-agreements clause in loan agreement
  - Loan not tied to father's other business dealings with lender
  - Written rate rationale and contemporaneous comparable quote
- Use neutral labels ("family-connected, no reported common ownership")
  until counsel classifies the relationship.
- Separate: direct ownership, attributed ownership, formal management
  authority, contractual/economic rights, practical influence, prior
  commercial dealings, and family relationship.

## Japanese-side requirements (for foreign counsel)

- Money Lending Business Act: occasional vs. regulated business analysis.
- FEFCA / Foreign Exchange and Foreign Trade Act post-reporting if loan
  exceeds ¥100M equivalent (~$700K+ USD).
- Japanese transfer-pricing documentation and consumption-tax treatment.
- Lender corporate authority: board/shareholder approvals, signer authority.
- Representative director (代表締締役 for KK) vs. representative member
  (代表締締員 for GK) — do not mix terminology.

## FX / currency

- Default to USD denomination. Foreign-currency principal creates §988
  FX gain/loss exposure for the borrower on repayment.

## Large-loan escalation ($10M+)

At material scale, add closing gates for:
- Repayment-capacity documentation (one-page use-of-proceedes + repayment
  story: revenue, refinance, or equity raise)
- Corporate authority confirmation
- Tax documentation receipt (W-8BEN-E + LOB worksheet)
- Independent lender approval minutes (without family voting/signing)
- Transfer-pricing / market-rate evidence
- Regulatory reporting analysis (FEFCA, 1042/1042-S)
- Actual payment administration (payment calendar, withholding, remittance)
- Never move money while rate, maturity, exact entity names, authority,
  and tax documentation remain unresolved.

## Deliverables shape

Six exhibits + two memos:
1. Cover memo (package summary, locked terms, TBD list, scale flags)
2. Open-issues memo (24-item counsel checklist)
3. Intake form (with confirmed answers baked in)
4. Term sheet (indicative, non-binding)
5. Promissory note (registered form, sum certain, no equity features)
6. Loan agreement (full commercial, covenants, S-corp protection,
   no-side-agreements, father-recusal section if applicable)
7. Borrower written consent (sole shareholder/director)
8. Lender document request (W-8BEN-E, corporate authority, ownership cap)
9. Closing and compliance checklist (payment + tax calendar)

All generated from one `deal_terms.json` via python-docx (terminal Python).
Every file carries "DRAFT FOR COUNSEL REVIEW — NOT SIGN-READY" header.
