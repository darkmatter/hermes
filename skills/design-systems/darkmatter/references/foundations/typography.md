# Typography

darkmatter's voice is terminal-first: a monospace display face carries the brand, with clean sans for body and a serif reserved for long-form prose. The display mono is **Geist Mono** (variable) — chosen over Monaspace Neon for its tighter kerning at large sizes. Fonts are loaded in `app/globals.css` (`@fontsource-variable/*` imports) and mapped to Tailwind in the `@theme` block. The `body` base enables antialiasing + kerning globally (`-webkit-font-smoothing: antialiased`, `-moz-osx-font-smoothing: grayscale`, `font-kerning: normal`, `text-rendering: optimizeLegibility`) and a slight `letter-spacing: -0.01em` — keep these; they are part of the look. Source: `src/app/globals.css`.

## Font families

| Tailwind class | Family | Use |
| --- | --- | --- |
| `font-mono` | **Geist Mono** (variable, `@fontsource-variable/geist-mono` → `--font-monospace`) | **Brand/display voice** — hero headings, labels, terminal UI, code, stat readouts |
| `font-sans` | **Geist** (variable) | Body default — paragraphs, list text, most UI copy |
| `font-heading` / `.font-sans-secondary` | **Montserrat** (variable) | Section headings (`h1`–`h6` default to this) |
| `font-serif` | **Lora** (variable) | Long-form prose only (blog/wiki body) |

Note the base layer in `globals.css`: `h1`–`h6` already default to `font-heading` (Montserrat) in `text-zinc-200`; `p`/`li` default to `font-sans` (Geist); `body` sits at `zinc-300`, weight 400, antialiased. Monaspace Xenon (`--font-monaspace-xenon`) remains only for `.prose-dark` blog headings.

## Brand voice rule

Reach for `font-mono` (Geist Mono) for the moments that should feel like darkmatter: hero display headings, eyebrow/section labels (often uppercase + tracked), metrics, badges, the nav wordmark, and anything terminal-flavored. Use `font-sans` (Geist) for readable body copy **and for interactive controls** — button labels and nav links render in sans (the `Button` base sets `font-sans`; give nav links `font-sans` too). Don't set body paragraphs, button labels, or nav links in mono; mono there reads as overused.

## Large mono display rule (important)

Mono set large looks wrong with mixed case and heavy weight. For any large `font-mono` display type (roughly `text-4xl`+ / hero + section headings), follow these globally:

- **Single case** — use `lowercase` (preferred, matches the system) or `uppercase`, never mixed case.
- **Lighter weight as size grows** — big display goes `font-light` (300), not `font-bold`/`font-semibold`. The bigger the type, the lighter the weight.
- **Antialiased + kerned** — inherited from the `body` base; don't disable it.

The shared `SectionHead` h2 (`font-mono text-[clamp(32px,5vw,56px)] font-light lowercase`) and the hero h1 (`font-mono text-[clamp(44px,8vw,84px)] font-light lowercase`) already encode this — reuse them rather than re-styling per screen.

```tsx
{/* eyebrow label — brand voice */}
<span className="font-mono text-xs uppercase tracking-[0.2em] text-muted-foreground">
  Systems / Protocols / Trading
</span>

{/* hero display heading — big mono is light + single-case */}
<h1 className="font-mono text-5xl font-light lowercase tracking-tight text-foreground md:text-7xl">
  we build software
</h1>

{/* body */}
<p className="font-sans text-base leading-relaxed text-muted-foreground">
  A bootstrapped studio at the intersection of AI and crypto.
</p>
```

## Type scale

Use Tailwind's default scale. Typical roles:

- Display / hero: `text-5xl`–`text-7xl`, `font-light`, `lowercase`, `tracking-tight`, `font-mono`.
- Section heading: `text-2xl`–`text-4xl`, `font-heading` (default) or `font-mono`.
- Body: `text-base` / `text-sm`, `leading-relaxed`, `font-sans`.
- Eyebrow / label / meta: `text-xs`–`text-sm`, `font-mono`, `uppercase`, `tracking-[0.2em]`, `text-muted-foreground`.
- Long-form prose: wrap in `.prose-dark` (Lora body, Monaspace Xenon headings) — do not hand-style.

## Common mistakes

- Setting body copy in `font-mono`. Mono is for display/brand/terminal, not paragraphs.
- Putting `font-mono` on button labels or nav links — those use `font-sans`.
- Large mono headings set `font-bold`/`font-semibold` or in mixed case — big mono must be `font-light` and single-case (lowercase).
- Using `font-serif` outside long-form prose.
- Hand-styling markdown headings instead of using `.prose-dark`.
