"use client"

import { ArrowRight, Terminal } from "lucide-react"
import { Button } from "@/components/ui/button"
import { DottedGlowBackground } from "@/components/ui/dotted-glow-background"

const META = [
  { dt: "surface", dd: "web · app" },
  { dt: "stack", dd: "Radix · Tailwind 4" },
  { dt: "type", dd: "Geist · Geist Mono" },
  { dt: "default theme", dd: "dark · oklch(0 0 0)" },
]

export function Hero() {
  return (
    <section id="top" className="relative overflow-hidden pt-40 pb-28">
      <DottedGlowBackground
        className="pointer-events-none absolute inset-0 opacity-90"
        opacity={1}
        gap={13}
        radius={1.6}
        colorDarkVar="--color-neutral-500"
        glowColorDarkVar="--color-sky-800"
        backgroundOpacity={0.9}
        speedMin={0.3}
        speedMax={1.6}
        speedScale={1}
      />
      <div className="relative mx-auto max-w-[1280px] px-6">
        <div className="mb-6 flex items-center gap-2.5 font-mono text-[11px] tracking-[0.04em] text-zinc-500 lowercase">
          <Terminal className="size-3.5" />
          darkmatter · visual + interaction language
        </div>
        <h1 className="max-w-[900px] font-mono text-[clamp(44px,8vw,84px)] font-light lowercase leading-[0.95] tracking-[-0.03em] text-white">
          design system
        </h1>
        <p className="mt-6 max-w-[640px] text-lg leading-[1.55] text-zinc-400">
          The dark-first, terminal-inspired system behind darkmatter — a
          bootstrapped app studio building software, protocols, and trading
          infrastructure at the intersection of AI and crypto.
        </p>
        <div className="mt-9 flex flex-wrap items-center gap-3">
          <Button size="lg">
            Browse components
            <ArrowRight className="size-4" />
          </Button>
          <Button size="lg" variant="outline">
            View tokens
          </Button>
        </div>

        <dl className="mt-16 grid grid-cols-2 gap-px overflow-hidden rounded-[14px] border border-zinc-900 bg-zinc-900 md:grid-cols-4">
          {META.map((c) => (
            <div key={c.dt} className="bg-black p-6">
              <dt className="font-mono text-[11px] tracking-[0.04em] text-zinc-500 lowercase">
                {c.dt}
              </dt>
              <dd className="mt-2 font-mono text-sm font-medium text-zinc-200">
                {c.dd}
              </dd>
            </div>
          ))}
        </dl>
      </div>
    </section>
  )
}
