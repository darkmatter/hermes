# Colors & tokens

All colors are OKLCH, defined as CSS variables in `app/globals.css` (`:root`) and exposed to Tailwind through the `@theme` block. Source: `src/app/globals.css` in `darkmatter/web`.

**Always** style with the semantic Tailwind classes below. Never hard-code hex/oklch values, and never read the raw `--variable`s directly in component classes.

darkmatter is **dark-only**: `:root` defines a single (dark) palette. There is no `.dark` class or light variant.

## Semantic surface & content tokens

| Token | Tailwind classes | Role |
| --- | --- | --- |
| `background` | `bg-background` | App canvas — near-black (`oklch 10.7% ...`) |
| `foreground` | `text-foreground` | Primary text — pure white |
| `card` / `card-foreground` | `bg-card` / `text-card-foreground` | Card & popover surfaces (slightly lifted black) |
| `popover` / `popover-foreground` | `bg-popover` / `text-popover-foreground` | Floating surfaces |
| `primary` / `primary-foreground` | `bg-primary` / `text-primary-foreground` | Primary actions (dark zinc fill, white text) |
| `secondary` / `secondary-foreground` | `bg-secondary` / `text-secondary-foreground` | Secondary fills (mid zinc) |
| `muted` / `muted-foreground` | `bg-muted` / `text-muted-foreground` | Muted surfaces & secondary text |
| `accent` / `accent-foreground` | `bg-accent` / `text-accent-foreground` | Hover/active accents |
| `destructive` / `destructive-foreground` | `bg-destructive` / `text-destructive-foreground` | Errors, destructive actions (red) |
| `border` | `border-border` | Hairline borders (mid zinc) |
| `input` | `border-input` / `bg-input` | Form field borders |
| `ring` | `ring-ring` | Focus rings (light zinc) |

Sidebar has its own scale: `bg-sidebar`, `text-sidebar-foreground`, `bg-sidebar-primary`, `bg-sidebar-accent`, `border-sidebar-border`, `ring-sidebar-ring`.

## Product accent colors

Per-product identity accents. Defined as raw OKLCH vars in `:root` (`--accent-green`, `--accent-blue`, `--accent-teal`, `--accent-emerald`, `--accent-purple`, `--accent-zinc`, each with a `-light` companion). These are **not** wired into Tailwind `@theme` color utilities — use them via arbitrary values wrapped in `oklch()` when a product needs its signature accent, e.g.:

```tsx
<span className="text-[oklch(var(--accent-emerald))]">emerald</span>
<div className="bg-[oklch(var(--accent-blue))]" />
```

Available: `--accent-green` / `--accent-green-light`, `--accent-blue` / `--accent-blue-light`, `--accent-teal` / `--accent-teal-light`, `--accent-emerald` / `--accent-emerald-light`, `--accent-purple` / `--accent-purple-light`, `--accent-zinc`.

## Decorative / effect colors

Used by the signature effect components (glows, beams, spotlights). Prefer letting the effect components own these; only reference them directly when building a custom effect:

`--glow-cyan`, `--glow-red`, `--glow-sky-blue`, `--glow-sky-glow`, `--glow-violet`, `--glow-highlight-blue`, `--sky-glow`, `--sky-glow-alt`, `--emerald-glow`, `--shadow-slate`, `--shadow-slate-dark`, `--dot-pattern`, `--grid-line`, `--grid-overlay`.

## Prose palette

Long-form markdown (blog/wiki) uses the `.prose-dark` class, which pulls a dedicated `--prose-*` scale (`--prose-body`, `--prose-heading`, `--prose-link-hover`, `--prose-code-text`, `--prose-border`, etc.). Wrap rendered markdown in `<div className="prose-dark">` rather than styling elements individually.

## Common mistakes

- Hard-coding `bg-black` / `text-white` instead of `bg-background` / `text-foreground`.
- Using `text-gray-400` instead of `text-muted-foreground`.
- Trying `bg-accent-emerald` (there is no such utility) — product accents are used via `oklch(var(--accent-emerald))` arbitrary values.
- Adding a light theme. There isn't one.
