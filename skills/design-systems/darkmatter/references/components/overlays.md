# Overlays

Source: `components/ui/{dialog,alert-dialog,sheet,drawer,popover,hover-card,command,tooltip}.tsx`. All are Radix-based with the theme's enter/exit animations; keep the `data-[state]` animation classes intact.

## Dialog

```tsx
import {
  Dialog, DialogTrigger, DialogContent, DialogHeader,
  DialogTitle, DialogDescription, DialogFooter,
} from "@/components/ui/dialog"

<Dialog>
  <DialogTrigger asChild><Button>Invite</Button></DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Invite teammate</DialogTitle>
      <DialogDescription>They'll get access to this workspace.</DialogDescription>
    </DialogHeader>
    {/* form */}
    <DialogFooter><Button type="submit">Send invite</Button></DialogFooter>
  </DialogContent>
</Dialog>
```

Always include a `DialogTitle` (accessibility) even if visually hidden with `sr-only`.

## Alert dialog

For destructive confirmations — `AlertDialog`, `AlertDialogTrigger`, `AlertDialogContent`, `AlertDialogAction`, `AlertDialogCancel`. Use `AlertDialogAction` styled as destructive for the confirm.

## Sheet & Drawer

- `sheet` — side panel (Radix Dialog variant). `SheetContent side="right" | "left" | "top" | "bottom"`.
- `drawer` — bottom drawer (Vaul), best for mobile. Pair with `useIsMobile()` to swap a Dialog for a Drawer on small screens.

## Popover & Hover card

```tsx
import { Popover, PopoverTrigger, PopoverContent } from "@/components/ui/popover"
import { HoverCard, HoverCardTrigger, HoverCardContent } from "@/components/ui/hover-card"
```

Popover for click-triggered floating content; hover-card for hover previews.

## Command (⌘K)

```tsx
import {
  Command, CommandInput, CommandList, CommandEmpty,
  CommandGroup, CommandItem,
} from "@/components/ui/command"
```

Use inside a `Dialog` for a command palette. Powered by `cmdk`.

## Common mistakes

- Omitting `DialogTitle` / `SheetTitle` (breaks screen readers).
- Removing the Radix animation classes on `*Content`.
- Using a Dialog on mobile where a Drawer reads better.

## Never invent

Use the exact subcomponent names each file exports; don't assume props that aren't in source.
