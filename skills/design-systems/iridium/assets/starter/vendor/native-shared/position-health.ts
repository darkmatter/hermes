export type HealthTier = "healthy" | "caution" | "at-risk";

export interface PositionHealthInput {
  currentTick: number | null;
  tickLower: number;
  tickUpper: number;
  isInRange: boolean | null;
  grossAprPct: number | null;
  ilUsd: string | null;
  totalInvestedUsd: string | null;
}

export interface PositionHealthResult {
  score: number;
  tier: HealthTier;
  factors: {
    distance: number;
    apr: number;
    il: number;
    inRange: number;
  };
}

export const HEALTH_WEIGHTS = {
  distance: 0.45,
  apr: 0.25,
  il: 0.2,
  inRange: 0.1,
} as const;

export const HEALTH_THRESHOLDS = {
  healthy: 70,
  caution: 40,
} as const;

export function getHealthTier(score: number): HealthTier {
  if (score >= HEALTH_THRESHOLDS.healthy) return "healthy";
  if (score >= HEALTH_THRESHOLDS.caution) return "caution";
  return "at-risk";
}

function calculateDistanceScore(
  currentTick: number | null,
  tickLower: number,
  tickUpper: number,
  isInRange: boolean | null,
): number {
  if (isInRange === false && currentTick == null) return 0;

  if (currentTick == null) return 50;

  const rangeWidth = tickUpper - tickLower;
  const distFromLower = currentTick - tickLower;
  const distFromUpper = tickUpper - currentTick;
  const minDist = Math.min(distFromLower, distFromUpper);

  if (minDist < 0) {
    const overshoot = Math.abs(minDist) / rangeWidth;
    return Math.max(0, 15 - overshoot * 100);
  }

  const centeredness = minDist / (rangeWidth / 2);
  return 30 + centeredness * 70;
}

function calculateAprScore(grossAprPct: number | null): number {
  if (grossAprPct == null) return 50;
  if (grossAprPct <= 0) return 10;
  if (grossAprPct < 5) return 10 + (grossAprPct / 5) * 40;
  if (grossAprPct < 50) return 50 + ((grossAprPct - 5) / 45) * 40;
  return 90 + Math.min(10, ((grossAprPct - 50) / 50) * 10);
}

function calculateIlScore(
  ilUsd: string | null,
  totalInvestedUsd: string | null,
): number {
  const il = Math.abs(parseFloat(ilUsd ?? "0"));
  const invested = parseFloat(totalInvestedUsd ?? "0");

  if (invested <= 0 || ilUsd == null) return 80;

  const ilRatio = il / invested;

  if (ilRatio <= 0.01) return 100;
  if (ilRatio <= 0.05) return 100 - ((ilRatio - 0.01) / 0.04) * 40;
  if (ilRatio <= 0.15) return 60 - ((ilRatio - 0.05) / 0.1) * 40;
  return Math.max(0, 20 - ((ilRatio - 0.15) / 0.1) * 20);
}

export function calculatePositionHealth(
  input: PositionHealthInput,
): PositionHealthResult | null {
  const {
    currentTick,
    tickLower,
    tickUpper,
    isInRange,
    grossAprPct,
    ilUsd,
    totalInvestedUsd,
  } = input;

  if (tickUpper - tickLower <= 0) return null;

  const distance = calculateDistanceScore(
    currentTick,
    tickLower,
    tickUpper,
    isInRange,
  );
  const apr = calculateAprScore(grossAprPct);
  const il = calculateIlScore(ilUsd, totalInvestedUsd);
  const inRange = isInRange === true ? 100 : 0;

  const composite =
    distance * HEALTH_WEIGHTS.distance +
    apr * HEALTH_WEIGHTS.apr +
    il * HEALTH_WEIGHTS.il +
    inRange * HEALTH_WEIGHTS.inRange;

  const raw = Math.round(Math.max(0, Math.min(100, composite)));
  const score =
    isInRange === false ? Math.min(raw, HEALTH_THRESHOLDS.caution - 1) : raw;

  return {
    score,
    tier: getHealthTier(score),
    factors: { distance, apr, il, inRange },
  };
}
