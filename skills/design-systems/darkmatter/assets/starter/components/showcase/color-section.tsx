import { SectionHead, PanelLabel } from "@/components/showcase/section-head"

const ZINC = [
  { n: "50", hex: "oklch(98.510% 0.0000 0)", light: true },
  { n: "100", hex: "oklch(96.743% 0.0013 286.37)", light: true },
  { n: "200", hex: "oklch(91.973% 0.0040 286.32)", light: true },
  { n: "300", hex: "oklch(87.111% 0.0055 286.29)", light: true },
  { n: "400", hex: "oklch(71.181% 0.0129 286.07)", light: false },
  { n: "500", hex: "oklch(55.166% 0.0138 285.94)", light: false },
  { n: "600", hex: "oklch(44.186% 0.0146 285.79)", light: false },
  { n: "700", hex: "oklch(37.032% 0.0119 285.81)", light: false },
  { n: "800", hex: "oklch(27.394% 0.0055 286.03)", light: false },
  { n: "900", hex: "oklch(21.033% 0.0059 285.89)", light: false },
  { n: "950", hex: "oklch(14.077% 0.0044 285.82)", light: false },
]

const SEMANTIC = [
  { name: "--background", role: "page canvas — pure black", chip: "oklch(var(--background))" },
  { name: "--foreground", role: "primary text on canvas", chip: "oklch(var(--foreground))" },
  { name: "--card", role: "elevated surface", chip: "oklch(var(--card))" },
  { name: "--primary", role: "primary fill", chip: "oklch(var(--primary))" },
  { name: "--secondary", role: "hairlines & subdued fills", chip: "oklch(var(--secondary))" },
  { name: "--muted-foreground", role: "secondary text (zinc-400)", chip: "oklch(var(--muted-foreground))" },
  { name: "--destructive", role: "destructive actions only", chip: "oklch(var(--destructive))" },
  { name: "--ring", role: "focus ring", chip: "oklch(var(--ring))" },
]

const BLUE_STRIP = ["oklch(93.192% 0.0316 255.59)", "oklch(80.907% 0.0956 251.81)", "oklch(71.374% 0.1434 254.62)", "oklch(62.308% 0.1880 259.81)", "oklch(42.445% 0.1809 265.64)", "oklch(37.906% 0.1378 265.52)", "oklch(28.226% 0.0874 267.94)"]
const EMERALD_STRIP = ["oklch(90.494% 0.0895 164.15)", "oklch(84.519% 0.1299 164.98)", "oklch(77.294% 0.1535 163.22)", "oklch(69.587% 0.1491 162.48)", "oklch(43.180% 0.0865 166.91)", "oklch(37.805% 0.0730 168.94)", "oklch(26.210% 0.0487 172.55)"]

export function ColorSection() {
  return (
    <section id="color" className="border-t border-zinc-900/50 py-24">
      <div className="mx-auto max-w-[1280px] px-6">
        <SectionHead
          index="01"
          eyebrow="color"
          title="Color"
          lede="Pure black is the canvas. Zinc is the structure. Color is reserved for product identity (USDC = blue, Hyperliquid = emerald) and terminal syntax."
        />

        <PanelLabel>surface · zinc</PanelLabel>
        <div className="mb-10 grid grid-cols-6 overflow-hidden rounded-[14px] border border-zinc-900 md:grid-cols-11">
          {ZINC.map((c) => (
            <div
              key={c.n}
              className="flex h-24 flex-col justify-end p-3 font-mono text-[10px]"
              style={{ background: c.hex }}
            >
              <span style={{ color: c.light ? "oklch(0 0 0 / 0.7)" : "oklch(100% 0 0 / 0.85)" }}>{c.n}</span>
            </div>
          ))}
        </div>

        <PanelLabel>semantic tokens · globals.css</PanelLabel>
        <div className="mb-10 grid grid-cols-1 gap-px overflow-hidden rounded-[14px] border border-zinc-900 bg-zinc-900 sm:grid-cols-2 lg:grid-cols-4">
          {SEMANTIC.map((t) => (
            <div key={t.name} className="bg-black p-5">
              <div
                className="mb-4 h-10 w-full rounded-md border border-zinc-800"
                style={{ background: t.chip }}
              />
              <div className="font-mono text-[12px] text-zinc-200">{t.name}</div>
              <div className="mt-1 font-mono text-[11px] leading-relaxed text-zinc-500">{t.role}</div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <div className="rounded-[20px] border border-blue-900/30 bg-blue-950/20 p-8">
            <h4 className="mb-1 font-mono text-lg font-semibold text-white">USDC · Blue</h4>
            <div className="mb-4 font-mono text-[11px] text-zinc-500">stablecoin product identity</div>
            <div className="grid h-12 grid-cols-7 overflow-hidden rounded-md">
              {BLUE_STRIP.map((hex) => (
                <div key={hex} style={{ background: hex }} />
              ))}
            </div>
          </div>
          <div className="rounded-[20px] border border-emerald-900/30 bg-emerald-950/20 p-8">
            <h4 className="mb-1 font-mono text-lg font-semibold text-white">Hyperliquid · Emerald</h4>
            <div className="mb-4 font-mono text-[11px] text-zinc-500">featured vault · live status</div>
            <div className="grid h-12 grid-cols-7 overflow-hidden rounded-md">
              {EMERALD_STRIP.map((hex) => (
                <div key={hex} style={{ background: hex }} />
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
