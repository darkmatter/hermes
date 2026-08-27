import {
  getDataAge,
  getFreshnessLevel,
  type TierConfig,
} from "./lib/freshness";

interface FreshnessIndicatorProps {
  updatedAt?: number;
  tier: TierConfig;
  compact?: boolean;
}

const TIER_LABELS: Record<string, string> = {
  realtime: "Live",
  live: "Live",
  periodic: "Recent",
  historical: "Cached",
};

export function FreshnessIndicator({
  updatedAt,
  tier,
  compact,
}: FreshnessIndicatorProps) {
  if (!updatedAt) return null;

  const level = getFreshnessLevel(updatedAt, tier);
  const age = getDataAge(updatedAt);

  if (level === "live") {
    return (
      <div className="flex flex-row items-center gap-1">
        <div className="h-1.5 w-1.5 rounded-full bg-green-500" />
        {!compact && (
          <span className="text-muted-foreground text-[10px]">
            {TIER_LABELS[tier.tier]}
          </span>
        )}
      </div>
    );
  }

  const ageSeconds = Math.round(age / 1000);

  return (
    <div className="flex flex-row items-center gap-1">
      <div
        className={`h-1.5 w-1.5 rounded-full ${level === "recent" ? "bg-yellow-500" : "bg-zinc-500"}`}
      />
      {!compact && (
        <span className="text-muted-foreground text-[10px]">
          {ageSeconds}s ago
        </span>
      )}
    </div>
  );
}
