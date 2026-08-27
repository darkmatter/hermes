# Motion

Iridium uses three layers of motion. Prefer built-in component animation and utility classes; reach for the `motion` library only for bespoke effects.

## 1. Component-level animation (default)
Radix-based components (`accordion`, `dialog`, `drawer`, `dropdown-menu`, `popover`, `select`, `navigation-menu`, `sheet`, `tooltip`) ship their own enter/exit transitions via **`tw-animate-css`** utilities (imported in `app/globals.css`). Use these components as-is — the motion is already correct and on-brand. Don't reimplement open/close animations.

## 2. Utility animations
- `tw-animate-css` provides `animate-in` / `animate-out` / `fade-*` / `zoom-*` / `slide-*` utilities used throughout the components. Available app-wide.
- A `fade-in` keyframe (opacity + 4px translateY) is defined in `app/globals.css` for subtle content entrances.
- Standard Tailwind `transition-*`, `duration-*`, and `ease-*` utilities for hover/active states.

## 3. Motion library (`motion/react`)
Signature animated components are built on **`motion/react`** (Motion, the successor to Framer Motion):
- `TypingAnimation` (`@native/ui/typing-animation`) — typewriter text, `duration` per character.
- `GlowingEffect` (`@native/ui/glowing-effect`) — animated conic-gradient border glow that tracks the pointer; uses `animate()` with an `ease` of `[0.16, 1, 0.3, 1]`.
- `SpotlightNew` (`@native/ui/spotlight-new`) — ambient spotlight sweep.
- `GlowCard` (`@native/ui/glow-card`) — card with the signature glow treatment.

Use `motion/react` (already a dependency) for new bespoke animation rather than adding another animation library.

## Feel
Motion is subtle and precise — short durations, eased, purposeful (state feedback, focus, ambient glow), never bouncy or playful. The glow/spotlight effects are the system's signature; use them sparingly on hero surfaces and key cards, not everywhere.

## Rules
- Don't add framer-motion/gsap/etc.; use `motion/react` and `tw-animate-css`.
- Respect the components' built-in transitions instead of overriding them.
- Keep durations short and easing smooth; reserve glow/spotlight for focal points.
