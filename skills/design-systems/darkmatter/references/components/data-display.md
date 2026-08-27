# Data display

Source: `components/ui/{card,badge,avatar,table,tabs,accordion,separator}.tsx`.

## Card

```tsx
import {
  Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter,
} from "@/components/ui/card"

<Card>
  <CardHeader>
    <CardTitle>Trading infra</CardTitle>
    <CardDescription>Low-latency execution.</CardDescription>
  </CardHeader>
  <CardContent>…</CardContent>
  <CardFooter><Button size="sm">Open</Button></CardFooter>
</Card>
```

Cards use the `card` surface + `border-border`. For a lifted/glowing card, wrap with `GlowingEffect` or use `CardSpotlight` / `WobbleCard` (see `effects.md`).

## Badge

```tsx
import { Badge } from "@/components/ui/badge"
```

- `variant`: `"default"` | `"secondary"` | `"destructive"` | `"outline"` (default `"default"`).

```tsx
<Badge>New</Badge>
<Badge variant="secondary">Beta</Badge>
<Badge variant="outline" className="font-mono">v0.1.0</Badge>
```

Badges read well in `font-mono` for version/status chips.

## Avatar

```tsx
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar"

<Avatar>
  <AvatarImage src="/img/team/ada.jpg" alt="Ada" />
  <AvatarFallback>AD</AvatarFallback>
</Avatar>
```

## Table

```tsx
import {
  Table, TableHeader, TableBody, TableRow, TableHead, TableCell, TableCaption,
} from "@/components/ui/table"

<Table>
  <TableHeader>
    <TableRow><TableHead>Service</TableHead><TableHead>Status</TableHead></TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell className="font-mono">api-gateway</TableCell>
      <TableCell><Badge variant="secondary">healthy</Badge></TableCell>
    </TableRow>
  </TableBody>
</Table>
```

Monospace (`font-mono`) suits IDs, hashes, and metrics in table cells.

## Tabs

```tsx
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"

<Tabs defaultValue="overview">
  <TabsList>
    <TabsTrigger value="overview">Overview</TabsTrigger>
    <TabsTrigger value="usage">Usage</TabsTrigger>
  </TabsList>
  <TabsContent value="overview">…</TabsContent>
  <TabsContent value="usage">…</TabsContent>
</Tabs>
```

## Accordion

```tsx
import {
  Accordion, AccordionItem, AccordionTrigger, AccordionContent,
} from "@/components/ui/accordion"

<Accordion type="single" collapsible>
  <AccordionItem value="a">
    <AccordionTrigger>What is darkmatter?</AccordionTrigger>
    <AccordionContent>A bootstrapped app studio.</AccordionContent>
  </AccordionItem>
</Accordion>
```

Open/close uses the `accordion-down`/`accordion-up` animation tokens (see `motion.md`).

## Separator

```tsx
import { Separator } from "@/components/ui/separator"
<Separator />
<Separator orientation="vertical" />
```

## Common mistakes

- Skipping `AvatarFallback` (breaks when the image fails).
- Hard-coding card backgrounds instead of the `card` surface.
- Inventing badge variants beyond the four listed.
