# Data Display

## Card
`import { Card, CardHeader, CardTitle, CardDescription, CardAction, CardContent, CardFooter } from "@native/ui/card"`. Source: `packages/ui/src/card.tsx`. The standard surface (maps to `--n-bg-2`).

```tsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@native/ui/card"

<Card>
  <CardHeader>
    <CardTitle>Total value</CardTitle>
    <CardDescription>Across all positions</CardDescription>
  </CardHeader>
  <CardContent>
    <p className="text-3xl font-display tabular-nums">$1,284,502</p>
  </CardContent>
</Card>
```
Use `CardAction` for a header-right control (menu, toggle).

## GlowCard
`import { GlowCard } from "@native/ui/glow-card"`. A rounded dark panel with a pointer-tracking glowing border (the signature "Glow" surface). Props: `spread?` (default 40), `proximity?` (default 72), `className?`, `innerClassName?`. Use as chrome for KPI cards, charts, and focal panels — sparingly, not for every card.

```tsx
import { GlowCard } from "@native/ui/glow-card"

<GlowCard innerClassName="p-6">
  <p className="text-xs uppercase font-display text-n-mute">APR (net)</p>
  <p className="text-4xl tabular-nums text-n-green">18.4%</p>
</GlowCard>
```

## Table
`import { Table, TableHeader, TableBody, TableFooter, TableHead, TableRow, TableCell, TableCaption } from "@native/ui/table"`. Use for dense tabular data. Right-align and `tabular-nums` numeric columns; wrap wide tables in `ScrollArea` or `overflow-x-auto`.

```tsx
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@native/ui/table"

<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Pool</TableHead>
      <TableHead className="text-right">Value</TableHead>
      <TableHead className="text-right">APR</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell>USDC / WETH</TableCell>
      <TableCell className="text-right tabular-nums">$412,900</TableCell>
      <TableCell className="text-right tabular-nums text-n-green">21.3%</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

## Avatar
`import { Avatar, AvatarImage, AvatarFallback, AvatarBadge, AvatarGroup, AvatarGroupCount } from "@native/ui/avatar"`. Radix Avatar plus group/badge helpers for stacked avatars and status dots.

## Item
`import { Item, ItemMedia, ItemContent, ItemTitle, ItemDescription, ItemActions, ItemGroup, ItemSeparator, ItemHeader, ItemFooter } from "@native/ui/item"`. A structured list-row primitive (media + content + actions). Use for settings rows, notifications, list entries — instead of hand-building flex rows.

```tsx
import { Item, ItemMedia, ItemContent, ItemTitle, ItemDescription, ItemActions } from "@native/ui/item"

<Item>
  <ItemMedia><Avatar>…</Avatar></ItemMedia>
  <ItemContent>
    <ItemTitle>Rebalance executed</ItemTitle>
    <ItemDescription>Position #4821 · 2m ago</ItemDescription>
  </ItemContent>
  <ItemActions><Button size="sm" variant="ghost">View</Button></ItemActions>
</Item>
```

## Charts
- `import { ... } from "@native/ui/chart"` — shadcn-style Recharts wrapper (`ChartContainer`, `ChartTooltip`, etc.). Series colors come from `--color-chart-1..5` (green, blue, violet, amber, red). See the `charts` skill for Recharts composition; keep colors on the chart tokens.
- `import { ... } from "@native/ui/tick-range-chart"` — domain chart for concentrated-liquidity tick ranges. Use for LP range visualizations.

## Separator
`import { Separator } from "@native/ui/separator"`. Radix separator (`orientation="horizontal" | "vertical"`).

## Terminal & TypingAnimation
- `import { Terminal } from "@native/ui/terminal"` — a console/terminal display block (uses `font-terminal`). For command output, logs, CLI-style panels.
- `import { TypingAnimation } from "@native/ui/typing-animation"` — typewriter text effect (prop `duration` per char). For hero/ambient text; use sparingly.

## Common mistakes / never invent
- Numeric columns/values always use `tabular-nums`, and right-align in tables.
- Don't wrap every card in `GlowCard`; reserve the glow for focal surfaces.
- Keep chart series on the `chart-*` tokens; don't hard-code colors.
