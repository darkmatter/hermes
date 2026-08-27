"use client"

import { ArrowRight } from "lucide-react"
import { SectionHead } from "@/components/showcase/section-head"
import { CardSpotlight } from "@/components/ui/card-spotlight"
import { WobbleCard } from "@/components/ui/wobble-card"
import { HoverBorderGradient } from "@/components/ui/hover-border-gradient"

export function EffectsSection() {
  return (
    <section id="effects" className="border-t border-zinc-900/50 py-24">
      <div className="mx-auto max-w-[1280px] px-6">
        <SectionHead
          index="04"
          eyebrow="signature effects"
          title="Effects"
          lede="Beyond the primitives, the system ships a small set of motion-driven surfaces — spotlights, wobble cards, and animated gradient borders — for hero moments and product cards."
        />

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <CardSpotlight className="rounded-[20px] border border-zinc-800 p-8">
            <h3 className="relative z-20 font-mono text-[22px] font-semibold text-white">CardSpotlight</h3>
            <p className="relative z-20 mt-2 max-w-sm font-sans text-sm leading-relaxed text-zinc-400">
              A radial spotlight that tracks the cursor across a bordered surface. Move your pointer over this card.
            </p>
            <div className="relative z-20 mt-6 font-mono text-[11px] tracking-[0.04em] text-zinc-500 lowercase">
              components/ui/card-spotlight
            </div>
          </CardSpotlight>

          <WobbleCard containerClassName="rounded-[20px] bg-zinc-900" className="p-8">
            <h3 className="font-mono text-[22px] font-semibold text-white">WobbleCard</h3>
            <p className="mt-2 max-w-sm font-sans text-sm leading-relaxed text-zinc-300">
              A tactile card that subtly tilts and translates toward the cursor — used for featured product surfaces.
            </p>
            <div className="mt-6 font-mono text-[11px] tracking-[0.04em] text-zinc-400 lowercase">
              components/ui/wobble-card
            </div>
          </WobbleCard>
        </div>

        <div className="mt-8 flex flex-wrap items-center justify-center gap-6 rounded-[20px] border border-zinc-900 bg-zinc-950/40 p-12">
          <HoverBorderGradient
            containerClassName="rounded-full"
            className="flex items-center gap-2 bg-black px-6 py-3 font-sans text-sm font-medium text-white"
          >
            <span>Animated border</span>
            <ArrowRight className="size-4" />
          </HoverBorderGradient>
          <p className="max-w-xs text-center font-mono text-[11px] leading-relaxed text-zinc-500 lowercase">
            HoverBorderGradient — a conic border that rotates on hover, reserved for primary CTAs.
          </p>
        </div>
      </div>
    </section>
  )
}
