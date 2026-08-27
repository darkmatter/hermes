# Navigation

Source: `components/ui/{navigation-menu,sidebar,breadcrumb,dropdown-menu,menubar,pagination,context-menu,floating-dock}.tsx`.

## Navigation menu

```tsx
import {
  NavigationMenu, NavigationMenuList, NavigationMenuItem,
  NavigationMenuTrigger, NavigationMenuContent, NavigationMenuLink,
} from "@/components/ui/navigation-menu"
```

Use for the primary top-nav on marketing/product pages. Wordmark + links commonly set in `font-mono`.

## Breadcrumb

```tsx
import {
  Breadcrumb, BreadcrumbList, BreadcrumbItem, BreadcrumbLink,
  BreadcrumbSeparator, BreadcrumbPage,
} from "@/components/ui/breadcrumb"

<Breadcrumb>
  <BreadcrumbList>
    <BreadcrumbItem><BreadcrumbLink href="/">Home</BreadcrumbLink></BreadcrumbItem>
    <BreadcrumbSeparator />
    <BreadcrumbItem><BreadcrumbPage>Trading</BreadcrumbPage></BreadcrumbItem>
  </BreadcrumbList>
</Breadcrumb>
```

## Sidebar

The `sidebar` component is a full system (provider + rail + mobile Sheet). Wrap the app in `SidebarProvider` and use `useSidebar()` for state. It automatically switches to a `Sheet` drawer under 768px via `useIsMobile()`.

```tsx
import {
  SidebarProvider, Sidebar, SidebarContent, SidebarGroup,
  SidebarMenu, SidebarMenuItem, SidebarMenuButton, SidebarTrigger,
} from "@/components/ui/sidebar"

<SidebarProvider>
  <Sidebar>
    <SidebarContent>
      <SidebarGroup>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton>Dashboard</SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarGroup>
    </SidebarContent>
  </Sidebar>
  <main>
    <SidebarTrigger />
    {/* page */}
  </main>
</SidebarProvider>
```

Sidebar has its own token scale (`bg-sidebar`, `text-sidebar-foreground`, `border-sidebar-border`, …) — see `colors.md`.

## Menus

- `dropdown-menu` — action menus / overflow menus (`DropdownMenu`, `DropdownMenuTrigger`, `DropdownMenuContent`, `DropdownMenuItem`, …).
- `context-menu` — right-click menus.
- `menubar` — app-style menu bar.

## Pagination

```tsx
import {
  Pagination, PaginationContent, PaginationItem,
  PaginationLink, PaginationPrevious, PaginationNext,
} from "@/components/ui/pagination"
```

## Floating dock (signature)

`floating-dock` is darkmatter's animated macOS-style dock for a compact icon nav. See `effects.md` for its props.

## Common mistakes

- Building a custom sidebar instead of the `sidebar` system (loses the mobile drawer + tokens).
- Hard-coding sidebar colors instead of the `sidebar-*` tokens.
- Omitting `BreadcrumbPage` for the current page (should not be a link).
