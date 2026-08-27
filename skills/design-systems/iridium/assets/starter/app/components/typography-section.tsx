const SCALE = [
  { label: "Display / 4xl", cls: "text-4xl font-semibold", font: "display" },
  { label: "Heading / 2xl", cls: "text-2xl font-semibold", font: "sans" },
  { label: "Title / lg", cls: "text-lg font-medium", font: "sans" },
  { label: "Body / base", cls: "text-base", font: "sans" },
  { label: "Small / sm", cls: "text-sm text-foreground-muted", font: "sans" },
];

const FONTS = [
  { name: "Sans — Inter", varName: "--font-sans", sample: "Aa Bb Cc 0123" },
  {
    name: "Display — Inter",
    varName: "--font-display",
    sample: "IRIDIUM SYSTEM",
  },
  {
    name: "Mono / numeric — Source Code Pro",
    varName: "--font-num",
    sample: "1,234.56  0.00%",
  },
  {
    name: "Terminal — Geist Mono",
    varName: "--font-terminal",
    sample: "> run --status",
  },
];

export function TypographySection() {
  return (
    <section id="type" className="scroll-mt-20">
      <h2
        className="mb-1 text-xs font-medium tracking-[0.22em] uppercase text-foreground-muted"
        style={{ fontFamily: "var(--font-display)" }}
      >
        Typography
      </h2>
      <p className="mb-6 max-w-2xl text-sm text-foreground-muted">
        Inter for UI and display, Geist Mono for terminal and technical
        accents, and a tabular mono for every numeric value.
      </p>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-md border border-border bg-card p-6">
          <div className="flex flex-col gap-4">
            {SCALE.map((s) => (
              <div
                key={s.label}
                className="flex items-baseline justify-between gap-4 border-b border-border-subtle pb-3 last:border-0 last:pb-0"
              >
                <span
                  className={s.cls}
                  style={{ fontFamily: `var(--font-${s.font})` }}
                >
                  The quick brown fox
                </span>
                <span className="shrink-0 text-[11px] text-foreground-muted">
                  {s.label}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-md border border-border bg-card p-6">
          <div className="flex flex-col gap-5">
            {FONTS.map((f) => (
              <div key={f.name}>
                <p className="mb-1 text-[11px] tracking-wide text-foreground-muted uppercase">
                  {f.name}
                </p>
                <p
                  className="text-xl text-foreground"
                  style={{ fontFamily: `var(${f.varName})` }}
                >
                  {f.sample}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
