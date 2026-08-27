# Motion & animation

Source: `src/app/globals.css` (`@theme` animations/keyframes), effect components in `components/ui/`, and `motion` (Framer Motion) for the signature effects.

## Token-driven animation

The theme defines the accordion motion used by Radix collapsibles:

| Token | Value |
| --- | --- |
| `--animate-accordion-down` | `accordion-down 0.2s ease-out` |
| `--animate-accordion-up` | `accordion-up 0.2s ease-out` |

These drive `Accordion` / `Collapsible` open/close and are referenced as `animate-accordion-down` / `animate-accordion-up`. Keyframes animate `height` against Radix's `--radix-accordion-content-height`.

Utility animations from `tailwindcss-animate` (`animate-in`, `animate-out`, `fade-in`, `zoom-in`, `slide-in-from-*`) are used throughout the Radix overlays (dialog, popover, dropdown, tooltip) for enter/exit transitions. Keep the existing `data-[state=open]` / `data-[state=closed]` animation classes when composing overlays.

## Framer Motion effects

The signature effect components (`glowing-effect`, `background-beams`, `wobble-card`, `evervault-card`, `card-spotlight`, `hover-border-gradient`, `text-hover-effect`, `floating-dock`, `background-lines`) use the `motion` package for pointer-driven and looping animation. Use these components as-is rather than re-implementing their motion. See `references/components/effects.md`.

## Rules

- Use the accordion animation tokens for collapsible height transitions; don't hand-roll height animations.
- Preserve Radix enter/exit animation classes when customizing overlays.
- Keep motion subtle and purposeful — glows and beams are accents, not the whole page.
- Respect reduced-motion: the effect components already guard heavy motion; don't force always-on animation on critical content.
