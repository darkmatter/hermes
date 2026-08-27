import { SectionHead } from "@/components/showcase/section-head"

const TYPE_SCALE = [
  { meta: "Display · mono · w700", sample: "design_system", cls: "font-mono text-[clamp(40px,7vw,64px)] font-bold leading-none tracking-[-0.025em] text-white" },
  { meta: "H1 · mono · w600", sample: "What we build", cls: "font-mono text-[clamp(34px,5vw,48px)] font-semibold leading-none tracking-[-0.02em] text-white" },
  { meta: "H2 · mono · w600", sample: "Hyperliquid Vault", cls: "font-mono text-[clamp(26px,4vw,36px)] font-semibold leading-none tracking-[-0.01em] text-white" },
  { meta: "H3 · mono · w600", sample: "nixmac", cls: "font-mono text-[28px] font-semibold leading-tight text-white" },
  { meta: "Body · sans · 18/1.55", sample: "Software, protocols, and trading infrastructure at the intersection of AI and crypto.", cls: "font-sans text-lg leading-[1.55] text-zinc-400" },
  { meta: "Body · sans · 16/1.55", sample: "Describe what you want in plain English. nixmac evolves your Nix config, builds it, and applies it.", cls: "font-sans text-base leading-[1.55] text-zinc-400" },
  { meta: "Tagline · mono · 13", sample: "AI-powered macOS configuration", cls: "font-mono text-[13px] text-zinc-500" },
  { meta: "Tag · mono · 11", sample: "macos · nix · ai · rust", cls: "font-mono text-[11px] tracking-[0.04em] text-zinc-400 lowercase" },
]

export function TypeSection() {
  return (
    <section id="type" className="border-t border-zinc-900/50 py-24">
      <div className="mx-auto max-w-[1280px] px-6">
        <SectionHead
          index="02"
          eyebrow="typography"
          title="Type"
          lede="Monaspace Neon carries headings and terminal chrome; Geist handles running text. The scale is tight, monospaced, and lowercase-leaning."
        />
        <div className="overflow-hidden rounded-[14px] border border-zinc-900">
          {TYPE_SCALE.map((row, i) => (
            <div
              key={row.meta}
              className={`grid grid-cols-1 gap-4 p-6 md:grid-cols-[220px_1fr] md:items-baseline ${
                i > 0 ? "border-t border-zinc-900/70" : ""
              }`}
            >
              <div className="font-mono text-[11px] tracking-[0.04em] text-zinc-600 lowercase">{row.meta}</div>
              <div className={row.cls}>{row.sample}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
