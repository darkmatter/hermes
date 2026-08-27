# Example: Trading / positions panel

A validated composition showing the core Iridium patterns together: `Button`/`Badge`/`TerminalButton`/`PillToggle` controls, a `Select` + `Input` order form with a Sonner toast, `Tabs` + `Dialog`, a positions table with `HealthBadge`, and a signature `GlowCard` KPI. This is a client component (interactive state + toasts).

Key patterns to copy:
- Numeric values use `tabular-nums`; P&L is colored with `text-n-green` / `text-n-red`.
- Surfaces use `bg-card` + `border-border`; muted text uses `text-foreground-muted`.
- `GlowCard` is wrapped in a `.modern-ui` scope so `rounded-*` resolves.
- Section labels use the display font, uppercase, wide tracking.
- Responsive grids use Tailwind utilities (`lg:grid-cols-3`), not fixed widths.

```tsx
"use client";

import { useState } from "react";
import { toast } from "sonner";
import { ArrowUpRight, Terminal, Wallet } from "lucide-react";

import { Button } from "@native/ui/button";
import { Badge } from "@native/ui/badge";
import { Input } from "@native/ui/input";
import { Label } from "@native/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@native/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@native/ui/tabs";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@native/ui/dialog";
import { Separator } from "@native/ui/separator";
import { TerminalButton } from "@native/ui/terminal-button";
import { Pill } from "@native/ui/pill";
import { PillToggle } from "@native/ui/pill-toggle";
import { HealthBadge } from "@native/ui/health-badge";
import { GlowCard } from "@native/ui/glow-card";

const POSITIONS = [
  { pair: "ETH / USDC", size: "12.40", pnl: "+4.82%", tier: "healthy" as const },
  { pair: "WBTC / USDC", size: "0.85", pnl: "+1.19%", tier: "caution" as const },
  { pair: "SOL / USDC", size: "320.0", pnl: "-2.34%", tier: "at-risk" as const },
];

export function TradingPanel() {
  const [range, setRange] = useState<"24h" | "7d" | "30d">("24h");

  return (
    <div className="grid gap-4 lg:grid-cols-3">
      {/* Controls */}
      <div className="rounded-md border border-border bg-card p-6">
        <p className="mb-4 text-xs tracking-wide text-foreground-muted uppercase">Controls</p>
        <div className="flex flex-wrap gap-2">
          <Button size="sm">Primary</Button>
          <Button size="sm" variant="outline">Outline</Button>
          <Button size="sm" variant="destructive">Delete</Button>
        </div>
        <Separator className="my-5" />
        <div className="flex flex-wrap items-center gap-2">
          <TerminalButton variant="primary" size="sm"><Terminal className="size-3" /> Execute</TerminalButton>
          <PillToggle
            value={range}
            onChange={setRange}
            mono
            options={[
              { label: "24H", value: "24h" },
              { label: "7D", value: "7d" },
              { label: "30D", value: "30d" },
            ]}
          />
        </div>
      </div>

      {/* Order form */}
      <div className="rounded-md border border-border bg-card p-6">
        <p className="mb-4 text-xs tracking-wide text-foreground-muted uppercase">New order</p>
        <div className="flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <Label htmlFor="pair">Pair</Label>
            <Select defaultValue="eth-usdc">
              <SelectTrigger id="pair" className="w-full">
                <SelectValue placeholder="Select a pair" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="eth-usdc">ETH / USDC</SelectItem>
                <SelectItem value="wbtc-usdc">WBTC / USDC</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="amount">Amount</Label>
            <Input id="amount" inputMode="decimal" placeholder="0.00" defaultValue="12.40" className="tabular-nums" />
          </div>
          <Button
            className="w-full"
            size="sm"
            onClick={() => toast.success("Order submitted", { description: "12.40 ETH / USDC — market" })}
          >
            <Wallet className="size-3.5" /> Submit order
          </Button>
        </div>
      </div>

      {/* Tabs + dialog */}
      <div className="rounded-md border border-border bg-card p-6">
        <Tabs defaultValue="overview">
          <TabsList className="w-full">
            <TabsTrigger value="overview" className="flex-1">Overview</TabsTrigger>
            <TabsTrigger value="activity" className="flex-1">Activity</TabsTrigger>
          </TabsList>
          <TabsContent value="overview" className="pt-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-foreground-muted">Portfolio value</span>
              <span className="tabular-nums text-lg font-medium text-n-green">$48,201.55</span>
            </div>
            <div className="mt-2 flex items-center gap-2">
              <Pill tone="green">+2.41%</Pill>
              <span className="text-xs text-foreground-muted">vs. yesterday</span>
            </div>
          </TabsContent>
          <TabsContent value="activity" className="pt-4">
            <p className="text-sm text-foreground-muted">No pending transactions.</p>
          </TabsContent>
        </Tabs>
        <Separator className="my-5" />
        <Dialog>
          <DialogTrigger asChild>
            <Button variant="outline" size="sm" className="w-full">
              Open dialog <ArrowUpRight className="size-3.5" />
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Confirm withdrawal</DialogTitle>
              <DialogDescription>This moves funds to your linked wallet. It cannot be undone.</DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <DialogClose asChild><Button variant="ghost" size="sm">Cancel</Button></DialogClose>
              <DialogClose asChild><Button size="sm">Confirm</Button></DialogClose>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Positions table */}
      <div className="rounded-md border border-border bg-card p-6 lg:col-span-2">
        <div className="mb-4 flex items-center justify-between">
          <p className="text-xs tracking-wide text-foreground-muted uppercase">Open positions</p>
          <Badge variant="outline" className="tabular-nums">{POSITIONS.length} active</Badge>
        </div>
        <div className="flex flex-col">
          <div className="grid grid-cols-[1.4fr_1fr_1fr_auto] gap-2 border-b border-border-subtle pb-2 text-[11px] tracking-wide text-foreground-muted uppercase">
            <span>Pair</span>
            <span className="text-right">Size</span>
            <span className="text-right">PnL</span>
            <span className="text-right">Health</span>
          </div>
          {POSITIONS.map((p) => (
            <div key={p.pair} className="grid grid-cols-[1.4fr_1fr_1fr_auto] items-center gap-2 border-b border-border-subtle py-3 text-sm last:border-0">
              <span className="font-medium text-foreground">{p.pair}</span>
              <span className="text-right tabular-nums text-foreground">{p.size}</span>
              <span className={`text-right tabular-nums ${p.pnl.startsWith("-") ? "text-n-red" : "text-n-green"}`}>{p.pnl}</span>
              <span className="flex justify-end"><HealthBadge tier={p.tier} /></span>
            </div>
          ))}
        </div>
      </div>

      {/* Signature GlowCard KPI */}
      <div className="modern-ui">
        <GlowCard className="h-full">
          <p className="text-xs tracking-wide text-foreground-muted uppercase">24h volume</p>
          <p className="mt-2 tabular-nums text-3xl font-semibold text-foreground">$1.284M</p>
          <div className="mt-3 flex items-center gap-2">
            <Pill tone="green">+18.6%</Pill>
            <span className="text-xs text-foreground-muted">rolling window</span>
          </div>
        </GlowCard>
      </div>
    </div>
  );
}
```

Remember to mount `<Toaster />` (from `@native/ui/sonner`) once near the root for the toast to appear.
