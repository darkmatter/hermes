# Buttons & Actions

## Button
`import { Button, buttonVariants } from "@native/ui/button"`. Source: `packages/ui/src/button.tsx`. Radix `Slot`-backed (supports `asChild`).

- **variant**: `default` (accent/green), `destructive`, `outline`, `secondary`, `ghost`, `link`, `muted`. Default `default`.
- **size**: `default` (tall, `h-14.5`), `sm` (`h-8`, small text), `lg` (`h-16`), `icon` (`size-10`). Default `default`.
- Renders icons via `[&_svg]` sizing; pass a lucide icon as a child.

```tsx
import { Button } from "@native/ui/button"
import { Plus } from "lucide-react"

<Button>Save</Button>
<Button variant="outline" size="sm">Cancel</Button>
<Button variant="destructive">Close position</Button>
<Button size="icon" variant="ghost" aria-label="Add"><Plus /></Button>
// as a link
<Button asChild variant="link"><a href="/docs">Docs</a></Button>
```

Use `default` for the primary action, `outline`/`ghost` for secondary, `destructive` for irreversible actions. The default size is deliberately large — use `sm` in dense toolbars.

## TerminalButton
`import { TerminalButton } from "@native/ui/terminal-button"`. Source: `packages/ui/src/terminal-button.tsx`. The console-styled action for terminal/trading surfaces — bordered, translucent-fill, amber accents.

- **variant**: `ghost` | `outline` | `primary` (amber) | `active` (amber, selected state) | `destructive`. Default per source.
- **size**: `sm` | `md` | `lg`. **fullWidth**: boolean. Plus `disabled`, `onClick`, `className`.

```tsx
import { TerminalButton } from "@native/ui/terminal-button"

<TerminalButton variant="primary" size="md">Execute</TerminalButton>
<TerminalButton variant="active">1H</TerminalButton>
<TerminalButton variant="outline" fullWidth>Connect wallet</TerminalButton>
```

Use `TerminalButton` for command-console/terminal UIs and segmented controls (e.g. timeframe selectors, where `active` marks the selection); use `Button` for standard app chrome.

## Toggle & ToggleGroup
`import { Toggle, toggleVariants } from "@native/ui/toggle"` and `import { ToggleGroup, ToggleGroupItem } from "@native/ui/toggle-group"`. Radix-based two-state / single-or-multi toggles. Use `ToggleGroup` for mutually-exclusive or multi-select option rows (view mode, filters).

```tsx
import { ToggleGroup, ToggleGroupItem } from "@native/ui/toggle-group"

<ToggleGroup type="single" defaultValue="table">
  <ToggleGroupItem value="table">Table</ToggleGroupItem>
  <ToggleGroupItem value="cards">Cards</ToggleGroupItem>
</ToggleGroup>
```

## CopyButton
`import { CopyButton } from "@native/ui/copy-button"`. Props: `text` (string to copy), `className`. Copies to clipboard with built-in copied feedback — use for addresses, hashes, IDs.

```tsx
<CopyButton text="0x1234…abcd" />
```

## Common mistakes / never invent
- Don't add variants/sizes beyond those listed. There is no `xl` size or `success` button variant.
- Don't recolor buttons with raw classes; use the variant that maps to the intent.
- For icon-only buttons use `size="icon"` and always add `aria-label`.
