# Assets: Logos & Icons

## Brand logo
Source: the official Iridium production brand kit. The starter ships the vector masters in `public/`:
- `public/iridium-symbol.svg` — the standalone **`ir` ligature symbol** (signature variant, with the ice-blue accent highlight). Use for compact/square placements: app icon, favicon, avatars, tray, tight nav.
- `public/iridium-wordmark.svg` — the off-white **complete wordmark** ("iridium"). Use in navigation, marketing, and anywhere the name must be legible. Minimum digital width ~120px.
- `public/favicon.svg` — the symbol on the near-black brand square (`#0E0F0F`), wired in `app/layout.tsx` via `metadata.icons`.

The system is **dark-first**, so the header uses the "Signature Dark" lockup — off-white symbol + wordmark on the near-black canvas (see `app/components/site-header.tsx`):

```tsx
import Image from "next/image"
<Image src="/iridium-symbol.svg" alt="" aria-hidden width={22} height={24} className="h-6 w-auto" priority />
<Image src="/iridium-wordmark.svg" alt="Iridium" width={112} height={23} className="h-[18px] w-auto" priority />
```

Rules (from the brand guide):
- Canonical spelling is **Iridium**; domain is **iridium.sh**. Never write "iridum"/"irdum".
- **Never** use the old serif `N` icon — it is deprecated and explicitly disallowed. The mark is the `ir` ligature.
- Use the off-white/white masters on dark surfaces; the black masters on light surfaces. Alternate brand surfaces are magenta (`#E42266`) and amber (`#FFCF6F`) — never combine magenta and amber in one mark.
- Don't shrink the full wordmark into an app/tray icon — use the symbol. Don't stretch, skew, outline, bevel, recolor, or shadow the logo, and keep its clear space.
- Never substitute placeholder/stock imagery for brand marks.

## Icons
The design system does not ship its own icon set. Components use **`lucide-react`** (a dependency), which is the icon system for Iridium apps.

```tsx
import { Wallet, ArrowUpRight, Terminal } from "lucide-react"
<Button size="icon" variant="ghost" aria-label="Wallet"><Wallet /></Button>
```

Rules:
- Use `lucide-react` for all icons; don't introduce another icon library.
- Buttons/badges size icons automatically (`[&_svg]` rules); avoid hard-coding icon sizes unless matching a specific control (e.g. `className="size-3"` inside a small `TerminalButton`).
- Always give icon-only controls an `aria-label`.
