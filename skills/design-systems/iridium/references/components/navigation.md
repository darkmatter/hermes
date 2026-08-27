# Navigation

## Tabs
`import { Tabs, TabsList, TabsTrigger, TabsContent } from "@native/ui/tabs"`. Radix Tabs. Source: `packages/ui/src/tabs.tsx`. Use for switching views within a page.

```tsx
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@native/ui/tabs"

<Tabs defaultValue="positions">
  <TabsList>
    <TabsTrigger value="positions">Positions</TabsTrigger>
    <TabsTrigger value="orders">Orders</TabsTrigger>
    <TabsTrigger value="history">History</TabsTrigger>
  </TabsList>
  <TabsContent value="positions">…</TabsContent>
  <TabsContent value="orders">…</TabsContent>
  <TabsContent value="history">…</TabsContent>
</Tabs>
```

## NavigationMenu
`import { NavigationMenu, NavigationMenuList, NavigationMenuItem, NavigationMenuTrigger, NavigationMenuContent, NavigationMenuLink, NavigationMenuIndicator, NavigationMenuViewport, navigationMenuTriggerStyle } from "@native/ui/navigation-menu"`. Radix NavigationMenu — top-bar navigation with dropdown panels. Use `navigationMenuTriggerStyle()` for plain links so they match trigger styling.

```tsx
<NavigationMenu>
  <NavigationMenuList>
    <NavigationMenuItem>
      <NavigationMenuLink className={navigationMenuTriggerStyle()} href="/dashboard">Dashboard</NavigationMenuLink>
    </NavigationMenuItem>
    <NavigationMenuItem>
      <NavigationMenuTrigger>Markets</NavigationMenuTrigger>
      <NavigationMenuContent>…</NavigationMenuContent>
    </NavigationMenuItem>
  </NavigationMenuList>
</NavigationMenu>
```

## Sidebar
`import { Sidebar, SidebarProvider, SidebarTrigger, SidebarInset, SidebarContent, SidebarHeader, SidebarFooter, SidebarGroup, SidebarGroupLabel, SidebarGroupContent, SidebarMenu, SidebarMenuItem, SidebarMenuButton, SidebarMenuSub, SidebarMenuSubItem, SidebarMenuSubButton, SidebarSeparator, SidebarRail, useSidebar } from "@native/ui/sidebar"` (plus `SidebarInput`, `SidebarMenuAction`, `SidebarMenuBadge`, `SidebarMenuSkeleton`, `SidebarGroupAction`). The full app-shell sidebar (collapsible, responsive to a drawer on mobile).

Wrap the app in `SidebarProvider`, render `<Sidebar>` + `<SidebarInset>` for the main content, and place a `<SidebarTrigger />` in the header. This is the canonical app shell for dashboard-style Iridium apps.

```tsx
import { SidebarProvider, Sidebar, SidebarContent, SidebarMenu, SidebarMenuItem, SidebarMenuButton, SidebarInset, SidebarTrigger } from "@native/ui/sidebar"

<SidebarProvider>
  <Sidebar>
    <SidebarContent>
      <SidebarMenu>
        <SidebarMenuItem><SidebarMenuButton asChild><a href="/">Overview</a></SidebarMenuButton></SidebarMenuItem>
      </SidebarMenu>
    </SidebarContent>
  </Sidebar>
  <SidebarInset>
    <header className="flex items-center gap-2 p-3"><SidebarTrigger /></header>
    <main>…</main>
  </SidebarInset>
</SidebarProvider>
```

## PaginationControls
`import { PaginationControls } from "@native/ui/pagination"`. Prebuilt pagination control (check the source for its exact props — page/count/onChange shape). Use under tables and long lists.

## Command
`import { Command, CommandDialog, CommandInput, CommandList, CommandEmpty, CommandGroup, CommandItem, CommandShortcut, CommandSeparator } from "@native/ui/command"`. `cmdk`-based command palette. Use `CommandDialog` for a ⌘K launcher.

```tsx
<CommandDialog open={open} onOpenChange={setOpen}>
  <CommandInput placeholder="Search…" />
  <CommandList>
    <CommandEmpty>No results.</CommandEmpty>
    <CommandGroup heading="Actions">
      <CommandItem>New order<CommandShortcut>⌘N</CommandShortcut></CommandItem>
    </CommandGroup>
  </CommandList>
</CommandDialog>
```

## Common mistakes / never invent
- Use `Sidebar` for app shells rather than hand-rolling a collapsible nav — it handles the mobile drawer and state via `useSidebar`.
- Wrap `Sidebar` usage in `SidebarProvider`, or `useSidebar` throws.
- Don't guess `PaginationControls` props — read `packages/ui/src/pagination.tsx`.
