const SURFACES = [
  { name: "background", cls: "bg-background", var: "--n-bg" },
  { name: "surface", cls: "bg-surface", var: "--n-bg-1" },
  { name: "card", cls: "bg-card", var: "--n-bg-2" },
  { name: "surface-3", cls: "bg-n-bg-3", var: "--n-bg-3" },
  { name: "input", cls: "bg-n-bg-4", var: "--n-bg-4" },
];

const ACCENTS = [
  { name: "primary", cls: "bg-primary", note: "accent / mint" },
  { name: "positive", cls: "bg-n-green", note: "green" },
  { name: "warning", cls: "bg-n-amber", note: "amber" },
  { name: "negative", cls: "bg-n-red", note: "red" },
  { name: "info", cls: "bg-n-blue", note: "blue" },
  { name: "violet", cls: "bg-n-violet", note: "violet" },
];

const RADII = [
  { name: "sm", cls: "rounded-sm", px: "6px" },
  { name: "md", cls: "rounded-md", px: "8px" },
  { name: "lg", cls: "rounded-lg", px: "10px" },
  { name: "xl", cls: "rounded-xl", px: "14px" },
  { name: "2xl", cls: "rounded-2xl", px: "18px" },
];

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <h2
      className="mb-1 text-xs font-medium tracking-[0.22em] uppercase text-foreground-muted"
      style={{ fontFamily: "var(--font-display)" }}
    >
      {children}
    </h2>
  );
}

export function TokensSection() {
  return (
    <section id="tokens" className="scroll-mt-20">
      <SectionLabel>Foundations</SectionLabel>
      <p className="mb-6 max-w-2xl text-sm text-foreground-muted">
        A cool blue-black ramp (OKLCH hue 265) with a mint accent and functional
        status hues. Every surface, border, and status color resolves to the
        native <code className="tabular-nums text-foreground">--n-*</code> ramp.
      </p>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-md border border-border bg-card p-5">
          <p className="mb-3 text-xs tracking-wide text-foreground-muted uppercase">
            Surfaces
          </p>
          <div className="flex flex-wrap gap-3">
            {SURFACES.map((s) => (
              <div key={s.name} className="flex flex-col items-center gap-1.5">
                <div
                  className={`h-12 w-12 rounded-md border border-border-bright ${s.cls}`}
                />
                <span className="text-[11px] text-foreground">{s.name}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-md border border-border bg-card p-5">
          <p className="mb-3 text-xs tracking-wide text-foreground-muted uppercase">
            Accent &amp; status
          </p>
          <div className="flex flex-wrap gap-3">
            {ACCENTS.map((s) => (
              <div key={s.name} className="flex flex-col items-center gap-1.5">
                <div className={`h-12 w-12 rounded-md ${s.cls}`} />
                <span className="text-[11px] text-foreground">{s.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-4 rounded-md border border-border bg-card p-5">
        <p className="mb-4 text-xs tracking-wide text-foreground-muted uppercase">
          Radii
        </p>
        <div className="flex flex-wrap items-end gap-5">
          {RADII.map((r) => (
            <div key={r.name} className="flex flex-col items-center gap-2">
              <div
                className={`h-14 w-14 border border-border-bright bg-n-bg-3 ${r.cls}`}
              />
              <span className="text-[11px] text-foreground">{r.name}</span>
              <span className="tabular-nums text-[10px] text-foreground-muted">
                {r.px}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
