# Spacing, layout & radii

Source: `src/app/globals.css` (`@theme` radii), and consumer layouts in `src/app/layouts/`, `src/app/pages/`.

## Radii

Radii derive from a single `--radius: 0.5rem` token:

| Tailwind | Value |
| --- | --- |
| `rounded-sm` | `calc(0.5rem - 4px)` |
| `rounded-md` | `calc(0.5rem - 2px)` |
| `rounded-lg` | `0.5rem` |

Components default to `rounded-md` / `rounded-lg`. Use these tokens; don't hard-code pixel radii. Larger decorative surfaces (cards, effect wrappers) commonly use `rounded-xl` / `rounded-2xl`.

## Spacing

Use Tailwind's default spacing scale (multiples of `0.25rem`). Conventions observed in the site:

- Section vertical rhythm: `py-16` → `py-24` (`md:py-32` for hero/marketing).
- Intra-section stacks: `space-y-4` / `space-y-6`; grids use `gap-4` / `gap-6`.
- Card padding: `p-6` (via `CardHeader`/`CardContent`).

## Container / page width

darkmatter centers content in a max-width container with horizontal padding. Standard pattern:

```tsx
<div className="mx-auto w-full max-w-6xl px-4 sm:px-6 lg:px-8">
  {/* section content */}
</div>
```

- Marketing/content pages: `max-w-6xl` (or `max-w-7xl` for wide hero sections).
- Long-form prose: the `.prose-dark` class self-constrains body to `--blog-line-width: 680px`.

## Layout method

Use flexbox for most one-dimensional layouts (`flex items-center gap-*`) and CSS grid for card galleries / feature grids (`grid gap-6 sm:grid-cols-2 lg:grid-cols-3`). Avoid fixed pixel widths on layout containers — let the container + grid handle sizing.

## Common mistakes

- Hard-coding `rounded-[8px]` instead of `rounded-lg`.
- Fixed-width layout wrappers (`w-[1200px]`) instead of `max-w-6xl mx-auto`.
- Inconsistent section rhythm — keep to the `py-16`/`py-24` cadence.
