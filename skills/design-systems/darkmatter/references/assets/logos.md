# Logos & assets

Brand assets live in `public/` in the starter (copied from `darkmatter/web/public`). Use the real logo — never a placeholder or invented mark.

## Logo files

| Path | Use |
| --- | --- |
| `/logo-white.svg` | Full wordmark, **white** — for the dark canvas (default) |
| `/logo-black.svg` | Full wordmark, black — for light surfaces (rare in this dark system) |
| `/img/logo-square-white.svg` | Square glyph/mark, white — favicons, compact nav, avatars |
| `/img/logo-square-black.svg` | Square glyph/mark, black |

Because darkmatter is dark-only, default to the **white** variants.

```tsx
import Image from "next/image"

{/* nav wordmark */}
<Image src="/logo-white.svg" alt="darkmatter" width={132} height={20} priority />

{/* compact / favicon-style mark */}
<Image src="/img/logo-square-white.svg" alt="darkmatter" width={28} height={28} />
```

## Fonts

- `/fonts/monaspace-neon-var.woff2` — the Monaspace Neon variable brand face, loaded via `@font-face` in `app/globals.css`. Other families (Geist, Montserrat, Lora, Monaspace Xenon) load from `@fontsource*` packages.

## Icons

- `lucide-react` and `@tabler/icons-react` are installed — use these for UI icons.
- `@/components/ui/github-icon` provides an inline GitHub mark.

## Rules

- Use white logo variants on the dark canvas.
- Always set meaningful `alt` text ("darkmatter").
- Never substitute placeholder stock or generate a new logo — the assets above are canonical.
- Don't recolor the logo SVGs; use the correct color variant instead.
