import { cn } from "./lib/utils";

interface PillToggleProps<T extends string> {
  options: readonly { label: string; value: T }[];
  value: T;
  onChange: (value: T) => void;
  mono?: boolean;
}

export function PillToggle<T extends string>({
  options,
  value,
  onChange,
  mono = false,
}: PillToggleProps<T>) {
  return (
    <div className="flex flex-row gap-0.5">
      {options.map((option) => {
        const isActive = option.value === value;
        return (
          <div
            key={option.value}
            role="button"
            className={cn(
              "cursor-pointer px-2 py-1 rounded border text-[11px] font-medium hover:border-zinc-600",
              isActive
                ? "border-amber-400 text-amber-400"
                : "border-zinc-800 text-zinc-400",
            )}
            style={{
              backgroundColor: isActive
                ? "rgba(212, 168, 83, 0.1)"
                : "transparent",
            }}
            onClick={() => onChange(option.value)}
          >
            <span className={cn(mono ? "font-mono" : undefined)}>
              {option.label}
            </span>
          </div>
        );
      })}
    </div>
  );
}

interface PillFilterProps {
  options: readonly { key: string; label: string }[];
  active: Set<string>;
  onToggle: (key: string) => void;
}

export function PillFilter({ options, active, onToggle }: PillFilterProps) {
  return (
    <div className="flex flex-row flex-wrap gap-1">
      {options.map(({ key, label }) => {
        const isActive = active.has(key);
        return (
          <div
            key={key}
            role="button"
            className={cn(
              "cursor-pointer px-2 py-[3px] rounded border text-[10px] font-medium hover:border-zinc-600",
              isActive
                ? "border-amber-400 text-amber-400"
                : "border-zinc-800 text-zinc-400",
            )}
            style={{
              backgroundColor: isActive
                ? "rgba(212, 168, 83, 0.1)"
                : "transparent",
            }}
            onClick={() => onToggle(key)}
          >
            {label}
          </div>
        );
      })}
    </div>
  );
}
