# Signature effects

darkmatter's visual identity. These are Framer Motion (`motion`) primitives — use them as-is for hero backgrounds, feature cards, and CTAs. Don't re-implement their motion. Source: `components/ui/`.

Keep effects as accents: one hero background, a few highlighted cards — not on every element. They own their own colors via the decorative `--glow-*` / `--dot-pattern` tokens (see `colors.md`).

## DottedGlowBackground

Animated dotted canvas with drifting glow — the primary hero/section background.

```tsx
import { DottedGlowBackground } from "@/components/ui/dotted-glow-background"

<section className="relative overflow-hidden">
  <DottedGlowBackground className="absolute inset-0" />
  <div className="relative z-10">{/* content */}</div>
</section>
```

Key props (all optional, sensible defaults): `gap`, `radius`, `opacity`, `backgroundOpacity`, `speedMin`, `speedMax`, `speedScale`, and color overrides (`color`, `glowColor`, plus CSS-var forms `colorLightVar` / `glowColorLightVar`, etc.). Prefer the defaults; they're tuned to the dark palette.

## GlowingEffect

Pointer-reactive border glow to wrap a card. Named export `GlowingEffect`.

```tsx
import { GlowingEffect } from "@/components/ui/glowing-effect"

<div className="relative rounded-xl border border-border p-6">
  <GlowingEffect glow spread={40} proximity={64} blur={0} />
  {/* card content */}
</div>
```

Props: `blur`, `inactiveZone`, `proximity`, `spread`, `variant` (`"default" | "white"`), `glow`, `disabled`, `movementDuration`, `borderWidth`, `className`.

## CardSpotlight

Card whose background reveals a radial spotlight following the cursor.

```tsx
import { CardSpotlight } from "@/components/ui/card-spotlight"

<CardSpotlight className="p-6" radius={350}>
  <h3 className="font-mono text-lg text-foreground">Protocols</h3>
  <p className="text-sm text-muted-foreground">On-chain building blocks.</p>
</CardSpotlight>
```

Props: `radius?` (default 350), `color?`, `children`, `className`.

## WobbleCard

Card that subtly tilts/translates toward the pointer.

```tsx
import { WobbleCard } from "@/components/ui/wobble-card"

<WobbleCard containerClassName="bg-card" className="p-8">
  <h3 className="font-mono text-xl">Trading</h3>
</WobbleCard>
```

Props: `children`, `containerClassName?`, `className?`.

## HoverBorderGradient

Button/wrapper with an animated gradient border — the brand CTA treatment. Renders a `button` by default; change with `as`.

```tsx
import { HoverBorderGradient } from "@/components/ui/hover-border-gradient"

<HoverBorderGradient as="a" href="/signup" className="px-6 py-2 font-mono text-sm">
  Launch app
</HoverBorderGradient>
```

Props include `as` (element/component, default `"button"`), `containerClassName`, `className`, `duration`, `clockwise`, plus passthrough props.

## EvervaultCard

Encrypted-text hover card with a hashing animation. Props: `text?`, `className?`.

## BackgroundBeams / BackgroundLines

Full-bleed animated line/beam backdrops for hero sections. `BackgroundBeams` is a memoized absolute-positioned layer; `BackgroundLines` wraps `children` with animated SVG lines (`svgOptions?`).

## FloatingDock

macOS-style magnifying icon dock for compact nav.

```tsx
import { FloatingDock } from "@/components/ui/floating-dock"

<FloatingDock
  items={[{ title: "Home", icon: <Home />, href: "/" }]}
  desktopClassName="…"
  mobileClassName="…"
/>
```

`items`: `{ title: string; icon: React.ReactNode; href: string }[]`.

## TextHoverEffect

Animated stroked-text hover effect for large display words. Props: `text` (required), `duration?`, `automatic?`.

## Common mistakes

- Stacking multiple heavy effects on one screen (perf + noise).
- Re-writing the motion instead of using the component.
- Overriding effect colors with raw values — let them use the `--glow-*` tokens.

## Never invent

Use only the props listed (verified from source). Import names: `DottedGlowBackground`, `GlowingEffect`, `CardSpotlight`, `WobbleCard`, `HoverBorderGradient`, `EvervaultCard`, `BackgroundBeams`, `BackgroundLines`, `FloatingDock`, `TextHoverEffect`.
