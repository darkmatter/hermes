# ID Document Sources for Cooper

Found during USPS Form 1583 fill-out session (July 2026).

## Local Filesystem Locations

| Source | Path | Contents |
|--------|------|----------|
| Tax docs README | `~/Dropbox (Personal)/docs/tax-docs-2025/README.md` | Legal name, property address, AIN, checklist |
| Mortgage statement | `~/Dropbox (Personal)/docs/tax-docs-2025/statement.pdf` | Borrower name, property address, loan number |
| Brokerage statement | `~/Dropbox (Personal)/docs/tax-docs-2025/87f7e1c1-*.pdf` | Legal name, mailing address |
| Auto insurance binder | `~/Dropbox (Personal)/docs/personal/Insurance-Auto-state-farm.pdf` | Named insured, mailing address, vehicle info, agent phone |
| Driver's license (front) | `~/Dropbox (Personal)/docs/tax-docs-2025/drivers-license-front.jpeg` | CA DL — expired Apr 2026 |
| Driver's license (back) | `~/Dropbox (Personal)/docs/tax-docs-2025/drivers-license-back.jpeg` | CA DL back |
| Passport scan | `~/Dropbox (Personal)/docs/personal/15B1F78F-D300-49DC-AD29-A28261F7215C_1_105_c.jpeg` | US Passport — valid until Oct 2032 |

## rclone Remotes

| Remote | Browse command | Notes |
|--------|---------------|-------|
| `darkmatter-personal:` | `rclone lsf darkmatter-personal: --max-depth 2` | Personal docs, agreements |
| `vault-storage:` | `rclone lsf vault-storage: --max-depth 2` | Vault config, scripts |
| `darkmatter-google-drive:` | `rclone lsf darkmatter-google-drive: --max-depth 2` | Google Drive files, appsheet data |
| `dropbox-vault:` | `rclone lsf dropbox-vault: --max-depth 2` | Dropbox vault storage |

## Passport MRZ Parsing (tesseract OCR)

When `vision_analyze` fails on a passport image, use tesseract:

```bash
tesseract /tmp/passport.jpeg /tmp/passport_ocr 2>&1
cat /tmp/passport_ocr.txt
```

The MRZ (Machine Readable Zone) line format:

```
P<USALASTNAME<FIRSTNAME<<<<<<<<<< <<< KKK KKK
PASSPORTNUM9USAYYMMDD SEXYYMMDD...
```

### Cooper's US Passport (from MRZ)

- **Number:** A08507456
- **Nationality:** USA
- **DOB:** 910423 → April 23, 1991
- **Sex:** M
- **Expiration:** 321006 → October 6, 2032
- **Issuing Entity:** US Department of State (standard for US passports)

### Cooper's CA Driver's License (from vision_analyze)

- **Number:** D9368862
- **Address:** 1111 S Grand Ave Apt 715, Los Angeles, CA 90066 (note: different ZIP than mortgage docs)
- **DOB:** 04/23/1991
- **Expiration:** 04/23/2026 (EXPIRED)
- **Issue Date:** 02/17/2021
- **Class:** C
- **Restrictions:** CORR LENS (corrective lenses)

## Address Cross-Reference

| Source | Address | ZIP |
|--------|---------|-----|
| Driver's License | 1111 S Grand Ave Apt 715, Los Angeles, CA | 90066 |
| Mortgage statement | 1111 S Grand Ave #715, Los Angeles, CA | 90015 |
| Auto insurance | 1111 S Grand Ave Apt 715, Los Angeles, CA | 90015-2767 |

The DL address ZIP (90066) differs from the mortgage/insurance address ZIP (90015). The mortgage/insurance address is more likely the current one — DL may have an older ZIP. Ask the user to confirm which address to use on forms.
