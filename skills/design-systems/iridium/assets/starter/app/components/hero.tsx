import { Badge } from "@native/ui/badge";

export function Hero() {
  return (
    <section className="relative overflow-hidden border-b border-border">
      {/* ambient glow */}
      <div
        aria-hidden
        className="pointer-events-none absolute -top-40 left-1/2 h-80 w-[42rem] -translate-x-1/2 rounded-full opacity-30 blur-3xl"
        style={{
          background:
            "radial-gradient(closest-side, var(--color-primary), transparent)",
        }}
      />
      <div className="mx-auto max-w-[1440px] px-4 py-16 sm:px-6 sm:py-20 lg:px-8">
        <div className="flex flex-col items-start gap-5">
          <Badge variant="info" className="tracking-wide">
            Tailwind v4 · React 19 · Radix
          </Badge>
          <h1
            className="max-w-3xl text-balance text-4xl font-semibold leading-tight sm:text-5xl"
            style={{ fontFamily: "var(--font-display)" }}
          >
            The Iridium design system
          </h1>
          <p className="max-w-2xl text-pretty text-base text-foreground-muted sm:text-lg">
            A dark-first, terminal-inspired system for dense financial
            interfaces. Cool blue-black surfaces, a mint accent, tabular
            numerics, and signature glow surfaces — all wired to a single
            OKLCH token ramp.
          </p>
          <div className="flex flex-wrap items-center gap-6 pt-2 text-sm">
            <div className="flex flex-col">
              <span className="tabular-nums text-2xl font-semibold text-foreground">
                51
              </span>
              <span className="text-xs text-foreground-muted">components</span>
            </div>
            <div className="h-8 w-px bg-border" />
            <div className="flex flex-col">
              <span className="tabular-nums text-2xl font-semibold text-foreground">
                5
              </span>
              <span className="text-xs text-foreground-muted">token groups</span>
            </div>
            <div className="h-8 w-px bg-border" />
            <div className="flex flex-col">
              <span className="text-2xl font-semibold text-n-green">●</span>
              <span className="text-xs text-foreground-muted">dark native</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
