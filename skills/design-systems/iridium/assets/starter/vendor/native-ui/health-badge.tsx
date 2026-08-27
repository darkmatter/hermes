import { Badge } from "./badge";
import type { HealthTier } from "@native/shared/position-health";

const TIER_CONFIG: Record<
  HealthTier,
  { variant: "success" | "warning" | "destructive"; label: string }
> = {
  healthy: { variant: "success", label: "HEALTHY" },
  caution: { variant: "warning", label: "CAUTION" },
  "at-risk": { variant: "destructive", label: "AT RISK" },
};

interface HealthBadgeProps {
  tier: HealthTier | null;
}

export function HealthBadge({ tier }: HealthBadgeProps) {
  if (tier == null) return null;

  const config = TIER_CONFIG[tier];

  return <Badge variant={config.variant}>{config.label}</Badge>;
}
