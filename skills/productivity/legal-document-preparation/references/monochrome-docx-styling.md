# Monochrome DOCX styling — condensed reference

House-style recipe for producing "darkmatter-like" .docx files with
python-docx: strictly grayscale palette, editorial serif typography,
hairline rules, and monochrome tables. Session-derived from the
August 2026 cross-border loan packet.

## Palette

| Token            | Hex     | Use                          |
|-------------------|---------|------------------------------|
| Near-black        | `#111111` | Body text, headings, sig labels |
| Gray dark         | `#555555` | Secondary text, disclaimers    |
| Gray medium       | `#666666` | Masthead, footer text          |
| Gray light        | `#888888` | Muted placeholders             |
| Border gray       | `#B8B8B8` | Table cell borders             |
| Alt-row gray      | `#F2F2F2` | Alternating table row fill     |
| White             | `#FFFFFF` | Text on black header row       |

**No blue, red, green, orange, or any non-gray hue anywhere.**

## Typography

- **Primary font:** Source Serif 4 (`~/Library/Fonts/SourceSerif4[opsz,wght].ttf`)
- **Fallback:** Georgia (universally available on macOS)
- Set explicitly on every run via `run.font.name` + XML `w:rFonts`
  (ascii, hAnsi, cs, eastAsia). Do not rely on style inheritance alone.
- Override built-in heading styles (`Heading 1/2/3`) to the same serif
  family — python-docx's default template sets Calibri.

## Layout

- Margins: 1" top/bottom, 1.1" left/right.
- Title: 22pt serif bold, left-aligned, near-black.
- Subtitle: 10pt serif italic, gray-dark, left-aligned.
- Hairlines: 0.75pt black (`w:sz="6"`) bottom-border paragraphs under
  titles, above signature blocks, and around disclaimer boxes.
- Masthead (header): `darkmatter labs` 8pt gray-medium bold left, draft
  banner 8pt gray-medium right (tab-stop right-aligned at 6.3").
- Footer: centered 7.5pt gray-medium deal summary.

## Tables

- No built-in table style (`tbl.style = None`).
- Header row: `#111111` fill, white text, 9pt bold caps.
- Body rows: alternating `#FFFFFF` / `#F2F2F2` fill.
- Borders: thin `#B8B8B8` single lines on cell level.
- Column widths: set explicitly (e.g. 1.7" label / 4.6" value).

## Theme-stripping recipe

python-docx's default Document() template carries the full Office theme
palette (blues `#4F81BD`, reds `#C0504D`, greens `#76923C`, oranges
`#E36C0A`, etc.) in `word/styles.xml` and `word/theme/theme1.xml`.
Run-level font/color overrides are **insufficient** — inherited style
definitions bleed through when Word/Pages renders.

Post-generation, unzip each .docx and strip:

1. **Colors:** In `styles.xml`, `document.xml`, `header*.xml`,
   `footer*.xml` — replace every `w:color`, `w:fill`, and
   `w:srgbClr w:val` whose hex is not in the allowed grayscale set with
   `#111111`.
2. **Fonts:** In the same files + `fontTable.xml` — replace every
   `w:ascii`, `w:hAnsi`, `w:cs`, `w:eastAsia` attribute with the serif
   family name.
3. **Theme:** In `theme/theme1.xml` — replace all `typeface="..."` with
   the serif family and strip non-grayscale `val="..."` color values.
4. Re-zip and verify: zero non-grayscale colors, zero non-serif fonts.

**Fold this into the generator script** so future regenerations stay
clean automatically — do not rely on a separate post-processing step.

## Validation

After stripping, verify via ZIP inspection:

```python
import zipfile, re
z = zipfile.ZipFile("file.docx")
all_xml = z.read("word/styles.xml").decode() + z.read("word/document.xml").decode()
colors = set(re.findall(r'w:color w:val="([0-9A-Fa-f]{6})"', all_xml))
fills = set(re.findall(r'w:fill="([0-9A-Fa-f]{6})"', all_xml))
fonts = set(re.findall(r'w:ascii="([^"]*)"', all_xml))
# Assert: all colors in allowed set, all fonts == serif family
```

Also verify via `textutil -convert html -stdout file.docx` — the
rendered CSS should show only the serif family and grayscale colors.

## Bundled vs embedded fonts

Copying font .ttf files beside a .docx is **bundling**, not **embedding**.
True embedding places font data inside the .docx package as
`/word/fonts/` parts with `embed` relationships in `fontTable.xml`.

- Do not claim fonts are embedded unless the package contains those parts.
- If fonts are merely bundled, say "font files included alongside the
  document."
- Include the applicable license (SIL OFL for Source Serif 4).
- For cross-platform portability, consider actual font embedding via
  Word's "Embed fonts in this file" setting or LibreOffice's equivalent.
