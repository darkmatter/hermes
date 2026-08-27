# Pages/DOCX contract intake and drafting workflow

## Source-variant discovery

When the visible source is an Apple Pages package, search for editable
siblings and prior exports **before** parsing `.iwa` internals:

1. Same basename in `~/Downloads`, `~/Documents`, and Codex work folders.
2. `.docx` and `.pdf` copies — use `mdfind -onlyin ~ '<terms>'`
   or `search_files` with filename globs (`*loan*`, `*contract*`, etc.).
3. Prior render folders containing PDFs or page images (e.g.
   `~/Documents/Codex/<date>/.../loan_packet_render*`).

## Text extraction preference

| Source available | Method | Notes |
|---|---|---|
| `.docx` twin | `textutil -convert txt -output /tmp/doc.txt "path.docx"` | Best — clean, ordered, complete |
| `.pdf` only | `web_extract` or `pdftotext` if installed | Good fallback |
| `.pages` only | `unzip` then `strings` on `.iwa` files; verify against `preview.jpg` | Last resort — loses ordering, truncates text, mixes noise |

## Placeholder inventory

After extraction, list every bracketed field so nothing is missed:

```bash
grep -oE '\[[^]]{1,100}\]' /tmp/extracted_text.txt | sort | uniq -c | sort -rn
```

Group by type: party names, amounts, rates, dates, legal-form identifiers,
and legal-judgment fields (e.g. "secured/unsecured", "governing law",
"prepayment terms"). Separate factual fills from legal/tax judgments.

## Document status classification

Before filling anything, classify the source:

- **Completed agreement needing edits** — proceed with targeted edits.
- **Template with placeholders** — fill placeholders, preserve disclaimers.
- **Educational/reference packet explicitly not for signature** — keep
  "reference only" labels; do not present as executable without counsel
  review. The packet's own disclaimers govern its status.

## Intake-first term collection

Write a structured intake (`01-intake.md`) covering:
- Parties (borrower, lender, corporate forms, jurisdictions)
- Relationship map (ownership %, control, affiliate links) — **critical
  for related-party or cross-border deals**
- Economics (principal, currency, rate, term, payments, maturity,
  prepayment, default grace)
- Commercial terms (use of proceeds, security/collateral, covenants)
- Legal mechanics (governing law, venue, notices, board approvals)

Mark unknowns "TBD." Do NOT collect sensitive identifiers (EINs,
bank-account numbers, personal IDs) in chat.

## Cross-exhibit consistency

Normalize deal terms into one record, then populate every exhibit from
the same values. Cross-check all exhibits for identical:
- Principal, currency, rate, day-count basis
- Payment dates, maturity, prepayment terms
- Default grace periods, governing law, notices

Inconsistency between term sheet, promissory note, and loan agreement is
a common source of recharacterization risk in tax-sensitive deals.

## Legal drafting safeguards

- Preserve "reference only" status until qualified counsel approves
  execution.
- Normalize deal terms in one intake record before populating multiple
  exhibits.
- Keep legal/tax choices as conspicuous TBDs (`[[TBD—COUNSEL]]`,
  `[[TBD—CPA]]`) rather than guesses.
- For related-party cross-border loans, request beneficial ownership,
  attribution, control, treaty-documentation, currency, withholding, and
  debt/equity facts.
- Phrase issue-spotting conditionally; do not state automatic tax
  consequences without verified authority and complete facts.
- Do not encode unverified tax/legal conclusions from a prior session as
  settled reusable rules — route them to the open-issues memo as
  questions for specialist confirmation.

## Open-issues memo structure

Write `00-open-issues.md` alongside drafts. Organize by category:
- Tax-election eligibility
- Arm's-length pricing / transfer-pricing considerations
- Withholding and treaty analysis
- Foreign-ownership / entity-classification reporting
- Debt-vs-equity characterization support
- Foreign-country-side requirements (left to foreign counsel)
- State-law and enforceability
- Currency / FX considerations
- Document consistency checklist

Each issue should state **what to ask counsel**, not what the answer is.
