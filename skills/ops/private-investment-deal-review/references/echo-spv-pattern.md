# Echo SPV pattern + Exowatt example

## Echo public product (support.echo.xyz / echo.xyz)
- Group leads share deals; followers invest deal-by-deal on same terms (USDC onchain).
- Participants rolled into **one entity**; that entity invests in the target.
- Founder sees clean cap table (one investor line); Echo handles investor returns at distribution time.
- Platform: ~5% of user profits only; SPV ops costs shared; docs at app.echo.xyz Account → Documents.
- Equity ≠ token delivery: tokens more wallet-direct; equity is vehicle interest.

## Typical BVI vehicle terms (from Exowatt CC Ltd OM, 2025-09)
Use as a **template checklist**, not universal law — always re-read the live memo.

| Item | Exowatt CC Ltd (example) |
|---|---|
| Vehicle | EXOWATT CC LTD (BVI business company) |
| Manager / Director | Gm Echo Manager Ltd (BVI approved manager) |
| Investor security | Non-voting **Participating Shares** (par US$0.01) |
| Control | **Management Shares** (voting) held by Manager; Participating Shares generally non-voting |
| Underlying | Exowatt, Inc. **Preferred Stock** |
| Valuation | $635M post-money FD (per Schedule 1) |
| Total Round Size | $494,770 = Investment Allocation $489,770 + Expense Allotment $5,000 |
| Funding | USDC 1:1 USD (or USD wire) to Vehicle wallet/account |
| Subscription Date | Expected ~2025-08-31 or as Directors determine |
| Term | 5 years + up to 1 year Director extension |
| Carry | Carried Interest Amount **20%**; Residual Distribution Amount 80% |
| Redemption | **Not** at investor option; compulsory redemption by Vehicle only |
| Transfer | Director written consent only; no Competitor; no exchange listing |
| Distributions | Back to **same** wallet/bank as subscription (unless Directors agree otherwise) |
| Share issue gate | Full cleared funds + AML/KYC docs; e-sign may be held in escrow until close |
| Counsel | Carey Olsen (BVI) on vehicle docs; company Definitive Documents **not** expected from Vehicle counsel |

## Doc pack shape
Common Echo zip contents:
1. Confidential Private Placement Memorandum (OM)
2. Subscription Agreement + e-sign page + BVI privacy notice
3. Registry-stamped M&AA (PDF)

Extract path that worked on macOS:
```bash
unzip -o ~/Downloads/<issuer>_offering_documents*.zip -d /tmp/deal-docs
textutil -convert txt "/tmp/deal-docs/"*.docx -outdir /tmp/deal-docs
# then grep Schedule 1, Definitions, Rights of Management Shares, Transfer, Redemption
```

## Dropbox Transfer
- Short links `dropbox.com/t/...` are Transfer packages, not simple shared files.
- Browser download often already sits in `~/Downloads` under the zip name in the Transfer UI — **check Downloads before automating Dropbox**.
- Anonymous `curl ?dl=1` frequently returns the Transfer HTML shell, not the zip.

## Answer template for "when do I get stock?"
1. You get **SPV Participating Shares** at Vehicle close (Subscription Date), after funds + KYC + acceptance.
2. **Company preferred** is issued to the **SPV**, not to your broker.
3. Economic stock exposure yes; street-name shares no.
4. Cash/token/stock-out only via SPV distribution/redemption on exit or end of term.
5. Returns: typically **USDC/USD to original funding rail**; secondary sale of Participating Shares is not a right.

## Post-close funding + portfolio mark (Exowatt, session 2026-07-31)
Public timeline vs Echo vehicle (~Subscription Date expected 2025-08-31, entry **$635M PM** preferred):

| Date | Event |
|---|---|
| 2025-04-22 | Series A ~$70M ($35M equity + $35M debt), Felicis-led |
| ~2025-08-31 | Echo SPV EXOWATT CC LTD / Cooper entry @ $635M PM |
| 2025-11-13 | Series A-II / extension **+$50M** (MVP Ventures, 8090, etc.); cumulative raise cited ~$140M |

- Public sources confirm the **Nov 2025 cash raise** but **do not publish post-money**.
- Cooper portfolio example: **$10k → $22.6k = 2.26×**.
- Naive reverse mark if Echo marks preferred 1:1: `635M × 2.26 ≈ $1.44B` post-money (pre ≈ $1.39B if +$50M was full primary at that price).
- Treat as **inferred mark band (~$1.35–1.5B)**, not a filed valuation. Discounts, carry reserves, or non-1:1 marks move the true round away from that number.
- A pure flat extension at $635M would not produce ~2.3× by itself; large green P&L implies a **higher mark** (round step-up and/or model), still unrealized.
