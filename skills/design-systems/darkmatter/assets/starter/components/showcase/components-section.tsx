"use client"

import { useState } from "react"
import { ArrowRight, Bell, Check, Rocket } from "lucide-react"
import { SectionHead } from "@/components/showcase/section-head"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Switch } from "@/components/ui/switch"
import { Checkbox } from "@/components/ui/checkbox"
import { Slider } from "@/components/ui/slider"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-[16px] border border-zinc-900 bg-zinc-950/40 p-6">
      <div className="mb-5 font-mono text-[11px] tracking-[0.04em] text-zinc-500 lowercase">{title}</div>
      {children}
    </div>
  )
}

export function ComponentsSection() {
  const [notify, setNotify] = useState(true)
  const [slider, setSlider] = useState([64])

  return (
    <section id="components" className="border-t border-zinc-900/50 py-24">
      <div className="mx-auto max-w-[1280px] px-6">
        <SectionHead
          index="03"
          eyebrow="components"
          title="Components"
          lede="55 Radix-backed primitives share one dark token set. Buttons, inputs, overlays, and data display all inherit the same hairline borders and zinc surfaces."
        />

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <Panel title="buttons">
            <div className="flex flex-wrap gap-3">
              <Button>Default</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="outline">Outline</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="link">Link</Button>
              <Button variant="destructive">Destructive</Button>
            </div>
            <div className="mt-4 flex flex-wrap items-center gap-3">
              <Button size="sm">Small</Button>
              <Button>
                Deploy <Rocket className="size-4" />
              </Button>
              <Button size="lg">Large</Button>
              <Button size="icon" aria-label="Notifications">
                <Bell className="size-4" />
              </Button>
            </div>
          </Panel>

          <Panel title="badges">
            <div className="flex flex-wrap gap-3">
              <Badge>Default</Badge>
              <Badge variant="secondary">Secondary</Badge>
              <Badge variant="outline">Outline</Badge>
              <Badge variant="destructive">Destructive</Badge>
              <Badge className="gap-1.5">
                <span className="size-1.5 animate-pulse rounded-full bg-[oklch(0.91_0.19_141.2)]" /> live
              </Badge>
            </div>
            <Separator className="my-6" />
            <div className="flex items-center gap-4">
              <Avatar>
                <AvatarFallback className="bg-zinc-800 font-mono text-xs text-zinc-300">DM</AvatarFallback>
              </Avatar>
              <div>
                <div className="font-mono text-sm text-zinc-200">darkmatter</div>
                <div className="font-mono text-[11px] text-zinc-500">app studio</div>
              </div>
            </div>
          </Panel>

          <Panel title="form controls">
            <div className="space-y-5">
              <div className="space-y-2">
                <Label htmlFor="email" className="font-mono text-[11px] text-zinc-400">email</Label>
                <Input id="email" type="email" placeholder="you@darkmatter.io" />
              </div>
              <div className="flex items-center justify-between">
                <Label htmlFor="notify" className="font-mono text-[11px] text-zinc-400">deploy notifications</Label>
                <Switch id="notify" checked={notify} onCheckedChange={setNotify} />
              </div>
              <div className="flex items-center gap-2">
                <Checkbox id="terms" defaultChecked />
                <Label htmlFor="terms" className="font-mono text-[11px] text-zinc-400">accept terms</Label>
              </div>
              <div className="space-y-2">
                <Label className="font-mono text-[11px] text-zinc-400">allocation · {slider[0]}%</Label>
                <Slider value={slider} onValueChange={setSlider} max={100} step={1} />
              </div>
            </div>
          </Panel>

          <Panel title="selects & radio">
            <div className="space-y-5">
              <div className="space-y-2">
                <Label className="font-mono text-[11px] text-zinc-400">environment</Label>
                <Select defaultValue="production">
                  <SelectTrigger>
                    <SelectValue placeholder="Select environment" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="development">development</SelectItem>
                    <SelectItem value="staging">staging</SelectItem>
                    <SelectItem value="production">production</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <RadioGroup defaultValue="mono" className="gap-3">
                {[
                  { v: "mono", l: "Monaspace Neon" },
                  { v: "sans", l: "Geist" },
                ].map((o) => (
                  <div key={o.v} className="flex items-center gap-2">
                    <RadioGroupItem value={o.v} id={o.v} />
                    <Label htmlFor={o.v} className="font-mono text-[11px] text-zinc-400">{o.l}</Label>
                  </div>
                ))}
              </RadioGroup>
            </div>
          </Panel>
        </div>

        <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
          <Panel title="tabs">
            <Tabs defaultValue="overview">
              <TabsList>
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="metrics">Metrics</TabsTrigger>
                <TabsTrigger value="logs">Logs</TabsTrigger>
              </TabsList>
              <TabsContent value="overview" className="pt-4 font-mono text-[13px] text-zinc-400">
                A dark-first system tuned for dense, technical surfaces.
              </TabsContent>
              <TabsContent value="metrics" className="pt-4">
                <div className="mb-2 font-mono text-[11px] text-zinc-500">uptime · 99.98%</div>
                <Progress value={82} />
              </TabsContent>
              <TabsContent value="logs" className="pt-4 font-mono text-[12px] text-emerald-400">
                {"> build succeeded in 11.6s"}
              </TabsContent>
            </Tabs>
          </Panel>

          <Panel title="accordion & alert">
            <Alert className="mb-5">
              <Check className="size-4" />
              <AlertTitle className="font-mono">Deployment ready</AlertTitle>
              <AlertDescription className="font-mono text-[12px]">
                Preview promoted to production.
              </AlertDescription>
            </Alert>
            <Accordion type="single" collapsible>
              <AccordionItem value="a">
                <AccordionTrigger className="font-mono text-[13px]">What is darkmatter?</AccordionTrigger>
                <AccordionContent className="font-mono text-[12px] text-zinc-400">
                  A bootstrapped app studio building at the AI/crypto intersection.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="b">
                <AccordionTrigger className="font-mono text-[13px]">Which stack?</AccordionTrigger>
                <AccordionContent className="font-mono text-[12px] text-zinc-400">
                  Radix primitives, Tailwind v4 tokens, Monaspace Neon.
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </Panel>
        </div>

        <div className="mt-6">
          <Card className="border-zinc-800 bg-zinc-950/50">
            <CardHeader>
              <CardTitle className="font-mono">Deploy a new vault</CardTitle>
              <CardDescription className="font-mono text-[12px]">
                Configure allocation and ship to the Hyperliquid perpetuals DEX.
              </CardDescription>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="vault" className="font-mono text-[11px] text-zinc-400">vault name</Label>
                <Input id="vault" placeholder="alpha-market-maker" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="strat" className="font-mono text-[11px] text-zinc-400">strategy</Label>
                <Input id="strat" placeholder="delta-neutral" />
              </div>
              <div className="space-y-2 md:col-span-2">
                <Label htmlFor="notes" className="font-mono text-[11px] text-zinc-400">notes</Label>
                <Textarea id="notes" placeholder="Risk parameters and rebalancing cadence…" />
              </div>
            </CardContent>
            <CardFooter className="justify-end gap-3">
              <Button variant="ghost">Cancel</Button>
              <Button>
                Deploy vault <ArrowRight className="size-4" />
              </Button>
            </CardFooter>
          </Card>
        </div>
      </div>
    </section>
  )
}
