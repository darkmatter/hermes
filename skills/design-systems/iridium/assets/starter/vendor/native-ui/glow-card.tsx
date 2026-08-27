import type { ReactNode } from "react";

import { GlowingEffect } from "./glowing-effect";
import { cn } from "./lib/utils";

/**
 * GlowCard — the core surface of the modernized ("Glow") dashboard.
 *
 * A rounded dark panel with an Aceternity GlowingEffect border that lights up
 * on cursor proximity. Use as the chrome for KPI cards, charts, and tables.
 *
 * Render inside a `.modern-ui` scope so `rounded-*` resolves to real radius
 * (the global terminal theme forces radius 0).
 */
export function GlowCard({
  className,
  innerClassName,
  spread = 40,
  proximity = 72,
  children,
}: {
  className?: string;
  /** Classes for the inner content panel (e.g. padding overrides). */
  innerClassName?: string;
  spread?: number;
  proximity?: number;
  children: ReactNode;
}) {
  return (
    <div
      className={cn(
        "relative rounded-2xl border border-white/10 p-px",
        className,
      )}
    >
      <GlowingEffect
        spread={spread}
        glow
        disabled={false}
        proximity={proximity}
        inactiveZone={0.01}
        borderWidth={2}
      />
      <div
        className={cn(
          "relative h-full rounded-2xl bg-neutral-950/80 p-5 backdrop-blur-sm",
          innerClassName,
        )}
      >
        {children}
      </div>
    </div>
  );
}
