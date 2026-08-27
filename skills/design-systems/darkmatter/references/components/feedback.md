# Feedback

Source: `components/ui/{alert,sonner,toast,toaster,progress,skeleton,tooltip}.tsx`, `hooks/use-toast.ts`.

## Alert

```tsx
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert"
import { Terminal } from "lucide-react"
```

- `variant`: `"default"` | `"destructive"` (default `"default"`).
- An optional leading icon is auto-positioned by the base styles.

```tsx
<Alert>
  <Terminal />
  <AlertTitle>Heads up</AlertTitle>
  <AlertDescription>Deploys run on every push to main.</AlertDescription>
</Alert>

<Alert variant="destructive">
  <AlertTitle>Build failed</AlertTitle>
  <AlertDescription>Check the logs for details.</AlertDescription>
</Alert>
```

## Toasts

Two systems are available; prefer **sonner** for new work.

**Sonner** — mount `<Toaster />` once (already available), then call `toast()`:

```tsx
import { Toaster } from "@/components/ui/sonner"
import { toast } from "sonner"

// in layout: <Toaster />
toast("Deployment queued")
toast.success("Live in production")
toast.error("Something went wrong")
```

**use-toast** (Radix toast) — `useToast()` + `<Toaster />` from `@/components/ui/toaster`:

```tsx
import { useToast } from "@/hooks/use-toast"
const { toast } = useToast()
toast({ title: "Saved", description: "Your changes are live." })
```

Don't mix both in one app; pick one Toaster.

## Progress & Skeleton

```tsx
import { Progress } from "@/components/ui/progress"
import { Skeleton } from "@/components/ui/skeleton"

<Progress value={64} />
<Skeleton className="h-4 w-32" />
```

Skeletons use the `muted` surface — size them with layout classes, not raw colors.

## Tooltip

```tsx
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "@/components/ui/tooltip"

<TooltipProvider>
  <Tooltip>
    <TooltipTrigger asChild><Button variant="ghost" size="icon"><Info /></Button></TooltipTrigger>
    <TooltipContent>Runs the build</TooltipContent>
  </Tooltip>
</TooltipProvider>
```

## Common mistakes

- Rendering two Toasters (sonner + radix) simultaneously.
- Coloring skeletons/progress with raw values instead of the built-in `muted`/`primary` tokens.
- Forgetting `TooltipProvider` around tooltips.

## Never invent

Alert has only `default` and `destructive` variants — no `success`/`warning`.
