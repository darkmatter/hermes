import type { ReactNode, CSSProperties } from "react";
import { cn } from "./lib/utils";

const COLS: Record<number, string> = {
  1: "1fr",
  2: "repeat(2, 1fr)",
  3: "repeat(3, 1fr)",
  4: "repeat(4, 1fr)",
  5: "repeat(5, 1fr)",
};

interface GridProps {
  cols?: 1 | 2 | 3 | 4 | 5;
  gap?: number;
  children?: ReactNode;
  className?: string;
  style?: CSSProperties;
}

export function Grid({
  cols = 1,
  gap = 8,
  children,
  className,
  style: styleProp,
}: GridProps) {
  return (
    <div
      className={cn("grid", className)}
      style={{
        gridTemplateColumns: COLS[cols],
        gap,
        ...styleProp,
      }}
    >
      {children}
    </div>
  );
}
