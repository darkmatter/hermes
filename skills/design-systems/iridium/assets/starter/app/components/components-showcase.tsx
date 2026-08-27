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

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <h2
      className="mb-1 text-xs font-medium tracking-[0.22em] uppercase text-foreground-muted"
      style={{ fontFamily: "var(--font-display)" }}
    >
      {children}
    </h2>
  );
}

export function ComponentsShowcase() {
  const [range, setRange] = useState<"24h" | "7d" | "30d">("24h");

  return (
    <section id="components" className="scroll-mt-20">
      <SectionLabel>Components</SectionLabel>
      <p className="mb-6 max-w-2xl text-sm text-foreground-muted">
        Radix-backed primitives and signature surfaces composed into the kind of
        screens Iridium is built for.
      </p>

      <div className="grid gap-4 lg:grid-cols-3">
        {/* Buttons + badges */}
        <div className="rounded-md border border-border bg-card p-6 lg:col-span-1">
          <p className="mb-4 text-xs tracking-wide text-foreground-muted uppercase">
            Buttons
          </p>
          <div className="flex flex-wrap gap-2">
            <Button size="sm">Primary</Button>
            <Button size="sm" variant="secondary">
              Secondary
            </Button>
            <Button size="sm" variant="outline">
              Outline
            </Button>
            <Button size="sm" variant="ghost">
              Ghost
            </Button>
            <Button size="sm" variant="destructive">
              Delete
            </Button>
          </div>

          <Separator className="my-5" />

          <p className="mb-4 text-xs tracking-wide text-foreground-muted uppercase">
            Badges
          </p>
          <div className="flex flex-wrap gap-2">
            <Badge>Default</Badge>
            <Badge variant="success">Success</Badge>
            <Badge variant="warning">Warning</Badge>
            <Badge variant="destructive">Error</Badge>
            <Badge variant="info">Info</Badge>
            <Badge variant="outline">Outline</Badge>
          </div>

          <Separator className="my-5" />

          <p className="mb-4 text-xs tracking-wide text-foreground-muted uppercase">
            Terminal controls
          </p>
          <div className="flex flex-wrap items-center gap-2">
            <TerminalButton variant="primary" size="sm">
              <Terminal className="size-3" /> Execute
            </TerminalButton>
            <TerminalButton variant="outline" size="sm">
              Cancel
            </TerminalButton>
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

        {/* Form card */}
        <div className="rounded-md border border-border bg-card p-6 lg:col-span-1">
          <p className="mb-4 text-xs tracking-wide text-foreground-muted uppercase">
            New order
          </p>
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
                  <SelectItem value="sol-usdc">SOL / USDC</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="amount">Amount</Label>
              <Input
                id="amount"
                inputMode="decimal"
                placeholder="0.00"
                defaultValue="12.40"
                className="tabular-nums"
              />
            </div>
            <Button
              className="w-full"
              size="sm"
              onClick={() => toast.success("Order submitted", {
                description: "12.40 ETH / USDC — market",
              })}
            >
              <Wallet className="size-3.5" /> Submit order
            </Button>
          </div>
        </div>

        {/* Tabs + dialog */}
        <div className="rounded-md border border-border bg-card p-6 lg:col-span-1">
          <Tabs defaultValue="overview">
            <TabsList className="w-full">
              <TabsTrigger value="overview" className="flex-1">
                Overview
              </TabsTrigger>
              <TabsTrigger value="activity" className="flex-1">
                Activity
              </TabsTrigger>
            </TabsList>
            <TabsContent value="overview" className="pt-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-foreground-muted">
                  Portfolio value
                </span>
                <span className="tabular-nums text-lg font-medium text-n-green">
                  $48,201.55
                </span>
              </div>
              <div className="mt-2 flex items-center gap-2">
                <Pill tone="green">+2.41%</Pill>
                <span className="text-xs text-foreground-muted">
                  vs. yesterday
                </span>
              </div>
            </TabsContent>
            <TabsContent value="activity" className="pt-4">
              <p className="text-sm text-foreground-muted">
                No pending transactions.
              </p>
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
                <DialogDescription>
                  This moves funds to your linked wallet. It cannot be undone.
                </DialogDescription>
              </DialogHeader>
              <DialogFooter>
                <DialogClose asChild>
                  <Button variant="ghost" size="sm">
                    Cancel
                  </Button>
                </DialogClose>
                <DialogClose asChild>
                  <Button size="sm">Confirm</Button>
                </DialogClose>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Positions table + glow KPI */}
      <div className="mt-4 grid gap-4 lg:grid-cols-3">
        <div className="rounded-md border border-border bg-card p-6 lg:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <p className="text-xs tracking-wide text-foreground-muted uppercase">
              Open positions
            </p>
            <Badge variant="outline" className="tabular-nums">
              {POSITIONS.length} active
            </Badge>
          </div>
          <div className="flex flex-col">
            <div className="grid grid-cols-[1.4fr_1fr_1fr_auto] gap-2 border-b border-border-subtle pb-2 text-[11px] tracking-wide text-foreground-muted uppercase">
              <span>Pair</span>
              <span className="text-right">Size</span>
              <span className="text-right">PnL</span>
              <span className="text-right">Health</span>
            </div>
            {POSITIONS.map((p) => (
              <div
                key={p.pair}
                className="grid grid-cols-[1.4fr_1fr_1fr_auto] items-center gap-2 border-b border-border-subtle py-3 text-sm last:border-0"
              >
                <span className="font-medium text-foreground">{p.pair}</span>
                <span className="text-right tabular-nums text-foreground">
                  {p.size}
                </span>
                <span
                  className={`text-right tabular-nums ${
                    p.pnl.startsWith("-") ? "text-n-red" : "text-n-green"
                  }`}
                >
                  {p.pnl}
                </span>
                <span className="flex justify-end">
                  <HealthBadge tier={p.tier} />
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="modern-ui lg:col-span-1">
          <GlowCard className="h-full">
            <p className="text-xs tracking-wide text-foreground-muted uppercase">
              24h volume
            </p>
            <p className="mt-2 tabular-nums text-3xl font-semibold text-foreground">
              $1.284M
            </p>
            <div className="mt-3 flex items-center gap-2">
              <Pill tone="green">+18.6%</Pill>
              <span className="text-xs text-foreground-muted">
                rolling window
              </span>
            </div>
            <Separator className="my-4" />
            <p className="text-sm text-foreground-muted">
              GlowCard is the signature modern surface — a proximity-lit border
              over a translucent panel.
            </p>
          </GlowCard>
        </div>
      </div>
    </section>
  );
}
