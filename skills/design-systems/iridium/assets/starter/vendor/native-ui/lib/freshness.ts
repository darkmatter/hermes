export type FreshnessTier = "realtime" | "live" | "periodic" | "historical";

export interface TierConfig {
  tier: FreshnessTier;
  refetchInterval: number;
  staleTime: number;
}

export function getDataAge(updatedAt: number): number {
  return Date.now() - updatedAt;
}

export function getFreshnessLevel(
  updatedAt: number,
  tier: TierConfig,
): "live" | "recent" | "stale" {
  const age = getDataAge(updatedAt);
  if (age <= tier.refetchInterval) return "live";
  if (age <= tier.refetchInterval * 2) return "recent";
  return "stale";
}
