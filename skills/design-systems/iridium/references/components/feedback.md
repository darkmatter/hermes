# Feedback & Status

## Badge
`import { Badge, badgeVariants } from "@native/ui/badge"`. Source: `packages/ui/src/badge.tsx`. Supports `asChild`.
- **variant**: `default` (accent), `secondary`, `destructive`, `outline`, `muted`, `info` (amber), `success` (emerald/green), `warning` (amber). Default `default`.

```tsx
<Badge variant="success">FILLED</Badge>
<Badge variant="warning">PENDING</Badge>
<Badge variant="destructive">FAILED</Badge>
<Badge variant="outline">v2</Badge>
```
Use `success`/`warning`/`destructive` for status; keep labels short and often UPPERCASE for the console feel.

## HealthBadge
`import { HealthBadge } from "@native/ui/health-badge"`. Domain component (LP/position health). Prop: `tier: "healthy" | "caution" | "at-risk" | null` (type from `@native/shared/position-health`). Renders a `Badge` with `HEALTHY` / `CAUTION` / `AT RISK`. Returns `null` when `tier` is null.

```tsx
import { HealthBadge } from "@native/ui/health-badge"
<HealthBadge tier="healthy" />
```
Use only for position/health status; for generic status use `Badge`.

## FreshnessIndicator
`import { FreshnessIndicator } from "@native/ui/freshness-indicator"`. Shows data liveness (a green dot + label when live, age otherwise). Props: `updatedAt?: number` (epoch ms), `tier: TierConfig` (from `@native/ui/lib/freshness`), `compact?: boolean`. Returns `null` without `updatedAt`. Use next to live market/data readouts.

## Pill
`import { Pill, type PillTone } from "@native/ui/pill"`. A small rounded status token (lighter than `Badge`). **tone**: `neutral | green | amber | red | sky`. Use for inline tags, deltas, category chips.

```tsx
<Pill tone="green">+2.4%</Pill>
<Pill tone="red">-1.1%</Pill>
<Pill tone="sky">NEW</Pill>
```

## Alert
`import { Alert, AlertTitle, AlertDescription } from "@native/ui/alert"`. Inline callout for warnings/info within a page.

```tsx
import { Alert, AlertTitle, AlertDescription } from "@native/ui/alert"
import { TriangleAlert } from "lucide-react"

<Alert>
  <TriangleAlert />
  <AlertTitle>Low liquidity</AlertTitle>
  <AlertDescription>This pool has thin depth; expect slippage.</AlertDescription>
</Alert>
```

## Toasts (Sonner)
`import { Toaster } from "@native/ui/sonner"` and call `toast()` from the `sonner` package. Mount one `<Toaster />` (already in the starter layout if added; otherwise add once near the root).

```tsx
"use client"
import { toast } from "sonner"
toast.success("Order submitted")
toast.error("Transaction reverted")
```

## Tooltip
`import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "@native/ui/tooltip"`. Wrap the app (or a region) in `TooltipProvider` once.

```tsx
<TooltipProvider>
  <Tooltip>
    <TooltipTrigger asChild><Button size="icon" variant="ghost" aria-label="Info"><Info /></Button></TooltipTrigger>
    <TooltipContent>Annualized, net of fees.</TooltipContent>
  </Tooltip>
</TooltipProvider>
```

## Skeleton
`import { Skeleton } from "@native/ui/skeleton"`. Loading placeholder. Match the size of the content it stands in for.

```tsx
<Skeleton className="h-6 w-24" />
```

## Common mistakes / never invent
- Don't invent badge variants or pill tones beyond those listed.
- `HealthBadge`/`FreshnessIndicator` are domain components — don't repurpose them for generic status.
- Mount `Toaster` once; don't render it per-component.
