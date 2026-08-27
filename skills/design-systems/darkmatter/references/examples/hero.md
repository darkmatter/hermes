# Example — brand hero

A validated hero section: animated dotted-glow backdrop, Monaspace Neon (`font-mono`) display heading, mono eyebrow label, dual CTAs, and a mono meta grid. This is the exact pattern from the starter's homepage and compiles against public component APIs.

## Imports

```tsx
import { ArrowRight, Terminal } from "lucide-react"
import { Button } from "@/components/ui/button"
import { DottedGlowBackground } from "@/components/ui/dotted-glow-background"
```

## Full code

```tsx
"use client"

import { ArrowRight, Terminal } from "lucide-react"
import { Button } from "@/components/ui/button"
import { DottedGlowBackground } from "@/components/ui/dotted-glow-background"

const META = [
  { dt: "surface", dd: "web · app" },
  { dt: "stack", dd: "Radix · Tailwind 4" },
  { dt: "type", dd: "Geist · Monaspace Neon" },
  { dt: "default theme", dd: "dark · oklch(0 0 0)" },
]

export function Hero() {
  return (
    <section className="relative overflow-hidden pt-40 pb-28">
      <DottedGlowBackground
        className="pointer-events-none absolute inset-0 opacity-90"
        opacity={1}
        gap={13}
        radius={1.6}
        backgroundOpacity={0.9}
        speedMin={0.3}
        speedMax={1.6}
      />
      <div className="relative mx-auto max-w-6xl px-6">
        <div className="mb-6 flex items-center gap-2.5 font-mono text-[11px] tracking-[0.04em] text-muted-foreground lowercase">
          <Terminal className="size-3.5" />
          darkmatter · visual + interaction language
        </div>

        <h1 className="max-w-[900px] font-mono text-[clamp(44px,8vw,84px)] font-bold leading-[0.95] tracking-[-0.03em] text-foreground">
          design system
        </h1>

        <p className="mt-6 max-w-[640px] text-lg leading-relaxed text-muted-foreground">
          The dark-first, terminal-inspired system behind darkmatter — a
          bootstrapped app studio building software, protocols, and trading
          infrastructure at the intersection of AI and crypto.
        </p>

        <div className="mt-9 flex flex-wrap items-center gap-3">
          <Button size="lg" className="font-mono">
            Browse components
            <ArrowRight className="size-4" />
          </Button>
          <Button size="lg" variant="outline" className="font-mono">
            View tokens
          </Button>
        </div>

        <dl className="mt-16 grid grid-cols-2 gap-px overflow-hidden rounded-xl border border-border bg-border md:grid-cols-4">
          {META.map((c) => (
            <div key={c.dt} className="bg-background p-6">
              <dt className="font-mono text-[11px] tracking-[0.04em] text-muted-foreground lowercase">
                {c.dt}
              </dt>
              <dd className="mt-2 font-mono text-sm font-medium text-foreground">
                {c.dd}
              </dd>
            </div>
          ))}
        </dl>
      </div>
    </section>
  )
}
```

## Notes

- The `1px` grid trick (`gap-px` + `bg-border` container, `bg-background` cells) draws hairline dividers from the `border` token — no custom borders.
- Heading and labels use `font-mono` (Monaspace Neon) — the brand voice. Body stays `text-muted-foreground`.
- `DottedGlowBackground` is the absolute backdrop; content sits in a `relative` container. Only one hero effect at a time.
