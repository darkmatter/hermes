import type { ReactNode } from "react";
import { cn } from "./lib/utils";

interface TerminalButtonProps {
  variant?: "ghost" | "outline" | "primary" | "active" | "destructive";
  size?: "sm" | "md" | "lg";
  fullWidth?: boolean;
  disabled?: boolean;
  className?: string;
  onClick?: (e: React.MouseEvent) => void;
  children?: ReactNode;
}

const variantClasses: Record<
  NonNullable<TerminalButtonProps["variant"]>,
  string
> = {
  ghost:
    "border-transparent bg-transparent hover:border-transparent hover:bg-white/5",
  outline:
    "border-zinc-800 bg-transparent hover:border-zinc-600 hover:bg-white/[0.04]",
  primary:
    "border-amber-400/40 bg-amber-400/[0.08] hover:border-amber-400 hover:bg-amber-400/[0.15]",
  active: "border-amber-400 bg-amber-400/[0.12] hover:bg-amber-400/[0.18]",
  destructive:
    "border-red-500/40 bg-red-500/[0.08] hover:border-red-400 hover:bg-red-500/[0.12]",
};

const sizeClasses: Record<NonNullable<TerminalButtonProps["size"]>, string> = {
  sm: "px-2 py-1 gap-1",
  md: "px-3 py-[7px] gap-1.5",
  lg: "px-5 py-2.5 gap-2",
};

const textSizeClasses: Record<
  NonNullable<TerminalButtonProps["size"]>,
  string
> = {
  sm: "text-xs",
  md: "text-[13px]",
  lg: "text-sm",
};

export function TerminalButton({
  variant = "outline",
  size = "md",
  fullWidth,
  disabled,
  className,
  onClick,
  children,
}: TerminalButtonProps) {
  const isAccent = variant === "active" || variant === "primary";
  const resolvedTextColor = disabled
    ? "text-zinc-400"
    : isAccent
      ? "text-amber-400"
      : "text-zinc-300";

  return (
    <div
      role="button"
      aria-disabled={disabled || undefined}
      onClick={disabled ? undefined : onClick}
      className={cn(
        "inline-flex items-center justify-center rounded border cursor-pointer select-none active:bg-white/[0.06]",
        variantClasses[variant],
        sizeClasses[size],
        fullWidth && "w-full",
        disabled && "opacity-35 cursor-not-allowed pointer-events-none",
        className,
      )}
    >
      <span
        className={cn(
          "flex items-center font-medium tracking-wide",
          textSizeClasses[size],
          resolvedTextColor,
          size === "sm" ? "gap-1" : "gap-1.5",
        )}
      >
        {children}
      </span>
    </div>
  );
}
