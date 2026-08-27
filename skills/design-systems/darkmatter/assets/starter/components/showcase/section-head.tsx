import type { ReactNode } from "react"

export function SectionHead({
  index,
  eyebrow,
  title,
  lede,
}: {
  index: string
  eyebrow: string
  title: string
  lede: ReactNode
}) {
  return (
    <div className="mb-14">
      <div className="mb-3.5 flex items-center gap-2.5 font-mono text-[11px] tracking-[0.04em] text-zinc-500 lowercase">
        <span className="block size-2 rounded-full bg-zinc-700" />
        {index} · {eyebrow}
      </div>
      <h2 className="mb-4 font-mono text-[clamp(32px,5vw,56px)] font-light lowercase leading-none tracking-[-0.02em] text-white">
        {title}
      </h2>
      <p className="max-w-[640px] text-lg leading-[1.55] text-zinc-400">{lede}</p>
    </div>
  )
}

export function PanelLabel({ children }: { children: ReactNode }) {
  return <div className="mb-3 font-mono text-[11px] tracking-[0.04em] text-zinc-500 lowercase">{children}</div>
}
