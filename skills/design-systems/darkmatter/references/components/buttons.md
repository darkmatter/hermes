# Buttons & actions

Source: `components/ui/button.tsx`, `toggle.tsx`, `toggle-group.tsx`.

## Button

```tsx
import { Button } from "@/components/ui/button"
```

Props: standard `<button>` attributes plus `variant`, `size`, and `asChild`.

- `variant`: `"default"` | `"destructive"` | `"outline"` | `"secondary"` | `"ghost"` | `"link"` (default `"default"`)
- `size`: `"default"` | `"sm"` | `"lg"` | `"icon"` (default `"default"`)
- `asChild`: render as the child element (via Radix `Slot`) — use for link buttons.

```tsx
<Button>Get started</Button>
<Button variant="secondary">Docs</Button>
<Button variant="outline" size="sm">Learn more</Button>
<Button variant="ghost" size="icon" aria-label="Settings">
  <Settings />
</Button>

{/* link-as-button */}
<Button asChild>
  <a href="/signup">Sign up</a>
</Button>
```

Shape & type (baked into the base — do not override): darkmatter buttons are **full pills** (`rounded-full`, never `rounded-md`) with `font-sans` labels at `text-xs` / `font-medium`. Heights: `sm` = `h-8`, `default` = `h-9` (36px), `lg` = `h-11` with `text-sm`, `icon` = `h-9 w-9`. Don't re-add `rounded-md`, `text-[12px]`, or `font-sans` per-button — the base already sets them; just pick a `variant` and `size`.

Variant surfaces (baked in):
- `default` — the **glass** primary: translucent near-black fill (`bg-[rgba(9,9,11,0.63)]`), 1px zinc-300/40 border (`border-[rgba(212,212,216,0.42)]`), `shadow-sm`, `text-accent-foreground`. It reads as a subtle raised glass chip on the black canvas, not a solid white button.
- `outline` — **transparent** (`bg-transparent` + `border-input` zinc hairline + `text-foreground`).
- `secondary` — filled zinc surface; `destructive` — red; `ghost`/`link` — no fill.

Don't restyle `default` back to a solid `bg-primary` fill — the glass treatment is the intended primary look.

Font: the base styles set `font-sans` — button labels always render in Geist sans, never mono. Do not add `font-mono` to buttons or nav links; reserve Geist Mono for display headings, eyebrow/meta labels, and terminal/code text (see `foundations/typography.md`).

Icons: pass a `lucide-react` / `@tabler/icons-react` icon as a child. The base styles auto-size any child `svg` to `size-4` and add `gap-2` — do not set icon size manually.

For a brand/marketing CTA with a glowing animated border, wrap content in `HoverBorderGradient` (see `effects.md`) instead of a custom outline.

## Toggle / ToggleGroup

```tsx
import { Toggle } from "@/components/ui/toggle"
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
```

`Toggle` shares `variant` (`"default"` | `"outline"`) and `size` (`"default"` | `"sm"` | `"lg"`). `ToggleGroup` supports `type="single" | "multiple"`.

```tsx
<ToggleGroup type="single" defaultValue="grid">
  <ToggleGroupItem value="grid" aria-label="Grid view"><Grid /></ToggleGroupItem>
  <ToggleGroupItem value="list" aria-label="List view"><List /></ToggleGroupItem>
</ToggleGroup>
```

## Accessibility

- Always give icon-only buttons an `aria-label`.
- Focus ring (`ring-ring`) is built in — never remove `focus-visible` styles.

## Common mistakes

- Setting explicit icon sizes (base styles handle it).
- Hard-coding button colors instead of using `variant`.
- Using `<a>` styled as a button instead of `<Button asChild>`.

## Never invent

Only the six variants and four sizes above exist. There is no `success`/`warning` button variant.
