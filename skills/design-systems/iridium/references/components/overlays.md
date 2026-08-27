# Overlays

All overlays are Radix-based (except `drawer` = Vaul) and ship their own on-brand transitions. Use them as-is.

## Dialog
`import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogClose } from "@native/ui/dialog"` (also `DialogOverlay`, `DialogPortal`). Modal dialog for focused tasks/confirmations.

```tsx
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@native/ui/dialog"
import { Button } from "@native/ui/button"

<Dialog>
  <DialogTrigger asChild><Button variant="destructive">Close position</Button></DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Close position?</DialogTitle>
      <DialogDescription>This submits a market order to exit.</DialogDescription>
    </DialogHeader>
    <DialogFooter>
      <Button variant="ghost">Cancel</Button>
      <Button variant="destructive">Confirm</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

## ModernModal
`import { ModernModal } from "@native/ui/modern-modal"`. A prebuilt modal wrapper (the "modern"/Glow-styled modal). Use when you want the styled modal shell without composing `Dialog*` parts; read `packages/ui/src/modern-modal.tsx` for its props.

## Sheet
`import { Sheet, SheetTrigger, SheetContent, SheetHeader, SheetTitle, SheetDescription, SheetFooter, SheetClose } from "@native/ui/sheet"`. Edge-anchored panel (side drawer). Use for filters, details, secondary nav.

## Drawer
`import { Drawer, DrawerTrigger, DrawerContent, DrawerHeader, DrawerTitle, DrawerDescription, DrawerFooter, DrawerClose } from "@native/ui/drawer"` (also `DrawerPortal`, `DrawerOverlay`). Vaul-based bottom drawer, good for mobile.

## Popover
`import { Popover, PopoverTrigger, PopoverContent, PopoverAnchor } from "@native/ui/popover"`. Non-modal floating panel for pickers, mini-forms, info.

## DropdownMenu
`import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuGroup, DropdownMenuCheckboxItem, DropdownMenuRadioGroup, DropdownMenuRadioItem, DropdownMenuShortcut, DropdownMenuSub, DropdownMenuSubTrigger, DropdownMenuSubContent, DropdownMenuPortal } from "@native/ui/dropdown-menu"`. Action/context menus.

```tsx
<DropdownMenu>
  <DropdownMenuTrigger asChild><Button size="icon" variant="ghost" aria-label="Menu"><MoreVertical /></Button></DropdownMenuTrigger>
  <DropdownMenuContent align="end">
    <DropdownMenuItem>Edit</DropdownMenuItem>
    <DropdownMenuSeparator />
    <DropdownMenuItem variant="destructive">Delete</DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

## Accordion & Collapsible
- `import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@native/ui/accordion"` — stacked expandable sections (set `type="single"`/`"multiple"`).
- `import { Collapsible, CollapsibleTrigger, CollapsibleContent } from "@native/ui/collapsible"` — a single show/hide region.

## ScrollArea
`import { ScrollArea, ScrollBar } from "@native/ui/scroll-area"`. Styled custom scrollbars — wrap long lists, wide tables, and overlay content so scrollbars stay on-brand.

## Tooltip
See `feedback.md` (wrap in `TooltipProvider`).

## Common mistakes / never invent
- Every `*Content` must have a matching trigger/root; use `asChild` to wrap your own trigger element.
- Prefer `Sheet`/`Drawer` for side/bottom panels over a full `Dialog`.
- Don't override the built-in enter/exit animations.
- Don't guess `ModernModal`/`PaginationControls` props — read their source.
