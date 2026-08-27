import type { ReactNode } from "react";

import { cn } from "./lib/utils";

export type PillTone = "neutral" | "green" | "amber" | "red" | "sky";

const TONES: Record<PillTone, string> = {
  neutral: "bg-white/8 text-muted-foreground",
  green: "bg-green-500/15 text-green-400",
  amber: "bg-amber-500/15 text-amber-400",
  red: "bg-red-500/15 text-red-400",
  sky: "bg-sky-500/15 text-sky-400",
};

/** Small status pill — modern replacement for the terminal @nixmac Badge. */
export function Pill({
  tone = "neutral",
  className,
  children,
}: {
  tone?: PillTone;
  className?: string;
  children: ReactNode;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-1.5 py-0.5 text-[10px] font-medium leading-none",
        TONES[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}
